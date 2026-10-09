
print("🔥 STATE.PY LOADED")
from typing import TypedDict,Annotated,Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    context: str
    past_queries: list[str]
    loop_count: int