from langgraph.graph import END ,StateGraph
from packages.agent.state import AgentState
from packages.agent.nodes import reasoner_node,tool_node


def router(state:AgentState)->str :
    last_message= state["messages"][-1]
    if state.get("loop_count",0)>=5 :
        return END
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0: # type:ignore 
        return "tools"
    return END

builder = StateGraph(AgentState)
builder.add_node("reasoner", reasoner_node)

builder.add_node("tools", tool_node)
builder.set_entry_point("reasoner")
builder.add_conditional_edges("reasoner", router)
builder.add_edge("tools", "reasoner")
agent_graph = builder.compile()