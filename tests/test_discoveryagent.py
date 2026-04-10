from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, create_engine
from sqlalchemy.pool import StaticPool

from linker_bi.agents.discoveryagent import DiscoveryAgent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    e = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    meta = MetaData()
    Table(
        "users",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("email", String, nullable=True),
    )
    Table(
        "orders",
        meta,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
        Column("amount", Integer, nullable=True),
    )
    meta.create_all(e)
    return e


@pytest.fixture
def agent(engine):
    return DiscoveryAgent(llm=MagicMock(), engine=engine)


# ---------------------------------------------------------------------------
# _introspect
# ---------------------------------------------------------------------------


def test_introspect_returns_both_tables(agent):
    result = agent._introspect()
    assert set(result.keys()) == {"users", "orders"}


def test_introspect_column_names(agent):
    cols = {c["name"] for c in agent._introspect()["users"]["columns"]}
    assert cols == {"id", "name", "email"}


def test_introspect_column_type(agent):
    cols = {c["name"]: c["type"] for c in agent._introspect()["users"]["columns"]}
    assert "INTEGER" in cols["id"].upper()


def test_introspect_primary_key(agent):
    assert agent._introspect()["users"]["primary_key"] == ["id"]


def test_introspect_foreign_key(agent):
    fks = agent._introspect()["orders"]["foreign_keys"]
    assert len(fks) == 1
    assert fks[0]["referred_table"] == "users"
    assert fks[0]["constrained_columns"] == ["user_id"]
    assert fks[0]["referred_columns"] == ["id"]


def test_introspect_no_foreign_keys_on_users(agent):
    assert agent._introspect()["users"]["foreign_keys"] == []


# ---------------------------------------------------------------------------
# execute
# ---------------------------------------------------------------------------


async def test_execute_returns_metadata_key(agent):
    result = await agent.execute(None)
    assert "metadata" in result


async def test_execute_metadata_contains_tables(agent):
    result = await agent.execute(None)
    assert "tables" in result["metadata"]
    assert set(result["metadata"]["tables"].keys()) == {"users", "orders"}


async def test_execute_does_not_call_llm(agent):
    await agent.execute(None)
    agent.llm.assert_not_called()
