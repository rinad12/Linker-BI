import operator
from typing import Annotated, Any

from langgraph.graph import MessagesState


class LNKState(MessagesState):  # type: ignore[misc]
    """Central graph state shared across all agents in the Linker BI pipeline.

    Inherits ``messages`` from :class:`~langgraph.graph.MessagesState`, which
    holds the conversation/message history passed between nodes.

    Attributes:
        messages: Inherited list of chat messages (from MessagesState).
        plan: Ordered list of steps representing the execution strategy
            produced by a planning agent. Accumulated across nodes via
            ``operator.add``.
        metadata: Key-value pairs containing database schema results (e.g.
            table names, column definitions, data-source identifiers).
            ``None`` when not yet populated.
        semantic_layer: Dictionary representing the generated semantic layer
            content. ``None`` before the semantic layer generation step runs.
        errors: List of error/feedback strings collected during the Critic
            loop. Accumulated across nodes via ``operator.add``.
    """

    plan: Annotated[list[str], operator.add] = []
    metadata: dict[str, Any] | None = None
    semantic_layer: dict[str, Any] | None = None
    errors: Annotated[list[str], operator.add] = []
