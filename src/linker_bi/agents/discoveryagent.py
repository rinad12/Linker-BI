from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Engine, inspect
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from linker_bi.state import LNKState
from .base import LNKBaseAgent
from linker_bi.prompts.discoveryagent_prompts import _SYSTEM_PROMPT



# ---------------------------------------------------------------------------
# Structured output models
# ---------------------------------------------------------------------------

class _ColumnDescription(BaseModel):
    name: str
    description: str


class _TableDescription(BaseModel):
    name: str
    description: str
    columns: list[_ColumnDescription]


class _SchemaDescriptions(BaseModel):
    tables: list[_TableDescription]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class DiscoveryAgent(LNKBaseAgent):
    """Introspects a database and enriches the schema with LLM descriptions.

    Two-phase execution:
    1. Uses :func:`sqlalchemy.inspect` to extract table names, column types,
       and PK/FK relationships.
    2. Passes the raw schema to the LLM, which returns a natural-language
       description for every table and column.

    The merged result is written into :attr:`~linker_bi.state.LNKState.metadata`
    under the ``"tables"`` key.

    Args:
        llm: Chat model used to generate schema descriptions.
        engine: Bound SQLAlchemy :class:`~sqlalchemy.engine.Engine` pointing
            at the database to introspect.

    Example::

        from sqlalchemy import create_engine
        from langchain_anthropic import ChatAnthropic

        agent = DiscoveryAgent(
            llm=ChatAnthropic(model="claude-sonnet-4-6"),
            engine=create_engine("postgresql://user:pass@localhost/mydb"),
        )
        updated_state = await agent.execute(state)
    """

    def __init__(self, llm: BaseChatModel, engine: Engine) -> None:
        super().__init__(llm)
        self.engine = engine

    # ------------------------------------------------------------------
    # Phase 1 — SQLAlchemy introspection
    # ------------------------------------------------------------------

    def _introspect(self) -> dict[str, Any]:
        """Return raw schema dict extracted via SQLAlchemy inspector."""
        inspector = inspect(self.engine)
        tables: dict[str, Any] = {}

        for table_name in inspector.get_table_names():
            columns = [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": col.get("default"),
                }
                for col in inspector.get_columns(table_name)
            ]

            pk = inspector.get_pk_constraint(table_name)
            primary_key: list[str] = pk.get("constrained_columns", [])

            foreign_keys = [
                {
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
                for fk in inspector.get_foreign_keys(table_name)
            ]

            tables[table_name] = {
                "columns": columns,
                "primary_key": primary_key,
                "foreign_keys": foreign_keys,
            }

        return tables

    # ------------------------------------------------------------------
    # Phase 2 — LLM descriptions
    # ------------------------------------------------------------------

    async def _describe(self, tables: dict[str, Any]) -> _SchemaDescriptions:
        """Ask the LLM to describe every table and column in *tables*."""
        structured_llm = self.llm.with_structured_output(_SchemaDescriptions)
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(tables, indent=2)),
        ]
        return await structured_llm.ainvoke(messages)

    # ------------------------------------------------------------------
    # Merge and execute
    # ------------------------------------------------------------------

    @staticmethod
    def _merge(
        tables: dict[str, Any],
        descriptions: _SchemaDescriptions,
    ) -> dict[str, Any]:
        """Merge LLM descriptions into the raw introspection dict."""
        desc_index: dict[str, _TableDescription] = {
            t.name: t for t in descriptions.tables
        }

        for table_name, table_data in tables.items():
            table_desc = desc_index.get(table_name)
            if table_desc is None:
                continue

            table_data["description"] = table_desc.description

            col_desc_index = {c.name: c.description for c in table_desc.columns}
            for col in table_data["columns"]:
                col["description"] = col_desc_index.get(col["name"], "")

        return tables

    async def execute(self, _state: LNKState) -> dict[str, Any]:
        """Introspect the database, enrich with LLM descriptions, update state.

        Returns:
            Partial state dict with ``metadata`` set to
            ``{"tables": {<table_name>: {...}, ...}}``.
            Each table contains ``description``, ``columns`` (with
            per-column ``description``), ``primary_key``, and
            ``foreign_keys``.
        """
        tables = self._introspect()
        descriptions = await self._describe(tables)
        enriched = self._merge(tables, descriptions)
        return {"metadata": {"tables": enriched}}
