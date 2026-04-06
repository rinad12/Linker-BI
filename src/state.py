from langgraph.graph import MessagesState 

class LNKState(MessagesState):
    metadata: dict | None = None
    plan: str | None = None
    semantic_layer: dict | None = None