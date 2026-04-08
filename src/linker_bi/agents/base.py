from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel

from linker_bi.state import LNKState


class LNKBaseAgent(ABC):
    """Base class for all LangGraph agents in the Linker BI pipeline.

    Every concrete agent must subclass :class:`LNKBaseAgent` and implement
    :meth:`execute`.  The class enforces a consistent interface so that agents
    can be composed into LangGraph graphs without boilerplate.

    Args:
        llm: A LangChain chat model instance (e.g. ``ChatAnthropic``,
            ``ChatOpenAI``) used by the agent to generate responses or
            structured outputs.

    Attributes:
        llm: The chat model passed at construction time.

    Example::

        class MyAgent(LNKBaseAgent):
            async def execute(self, state: LNKState) -> dict:
                response = await self.llm.ainvoke(state["messages"])
                return {"messages": [response]}
    """

    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm

    @abstractmethod
    async def execute(self, state: LNKState) -> dict[str, Any]:
        """Run agent logic against the current graph state and return updated state.

        Args:
            state: The current :class:`~linker_bi.state.LNKState` snapshot
                passed in by the LangGraph runtime.

        Returns:
            A partial dict containing only the state fields modified by
            this agent's logic, which LangGraph merges into the graph state.
        """
