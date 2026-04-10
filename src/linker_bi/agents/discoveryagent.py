from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import Engine, inspect
from langchain_core.language_models import BaseChatModel

from linker_bi.state import LNKState
from .base import LNKBaseAgent


class DiscoveryAgent(LNKBaseAgent):
    """Introspects a SQLAlchemy-connected database and populates state metadata.

    Uses :func:`sqlalchemy.inspect` to extract table names, column definitions,
    primary-key constraints, and foreign-key relationships, then writes the
    structured result into :attr:`~linker_bi.state.LNKState.metadata`.

    LLM-based description of the schema is handled by a separate agent
    downstream in the pipeline.

    Args:
        llm: Chat model instance required by the base class interface.
        engine: A bound SQLAlchemy :class:`~sqlalchemy.engine.Engine` pointing
            at the database to introspect.
    """

    def __init__(self, llm: BaseChatModel, engine: Engine) -> None:
        super().__init__(llm)
        self.engine = engine

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

    async def execute(self, _state: LNKState | None) -> dict[str, Any]:
        """Introspect the database and return updated state with schema metadata.

        Returns:
            Partial state dict with ``metadata`` set to
            ``{"tables": {<table_name>: {...}, ...}}``.
            Each table contains ``columns`` (with ``name``, ``type``,
            ``nullable``, ``default``), ``primary_key``, and ``foreign_keys``.
        """
        tables = await asyncio.to_thread(self._introspect)
        return {"metadata": {"tables": tables}}
