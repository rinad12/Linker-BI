from langgraph.graph import MessagesState


class LNKState(MessagesState):
    """Central graph state shared across all agents in the Linker BI pipeline.

    Inherits ``messages`` from :class:`~langgraph.graph.MessagesState`, which
    holds the conversation/message history passed between nodes.

    Attributes:
        messages: Inherited list of chat messages (from MessagesState).
        metadata: Arbitrary key-value pairs for pipeline-wide context (e.g.
            user ID, request ID, data-source identifiers).  ``None`` when not
            yet populated.
        plan: A textual execution plan produced by a planning agent.  ``None``
            before the planning step runs.
        semantic_layer: Structured representation of the semantic layer (e.g.
            metric definitions, dimension hierarchies) used by downstream
            agents to build queries.  ``None`` when not yet resolved.
    """

    metadata: dict | None = None
    plan: str | None = None
    semantic_layer: dict | None = None
