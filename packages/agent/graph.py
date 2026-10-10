from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from packages.agent.state import AgentState
from packages.agent.nodes import reasoner_node, tool_node, critic_node

def reasoner_router(state: AgentState) -> str:
    """Routes from Reasoner to either Tools or the Critic."""
    last_message = state["messages"][-1]
    
    # Kill switch
    if state.get("loop_count", 0) >= 5:
        return END
        
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0: #type:ignore 
        return "tools"
        
    # If no tools were called, the Reasoner generated an answer. Send it to the Critic.
    return "critic"

def critic_router(state: AgentState) -> str:
    """Routes from Critic to either END (Approved) or Reasoner (Rejected)."""
    last_message = state["messages"][-1]
    
    # If the last message in the state is a HumanMessage (our REJECT feedback), go back to Reasoner
    if last_message.type == "human" and "QA Review Failed" in last_message.content:
        return "reasoner"
        
    return END

builder = StateGraph(AgentState)
builder.add_node("reasoner", reasoner_node)
builder.add_node("tools", tool_node)
builder.add_node("critic", critic_node)

builder.set_entry_point("reasoner")
builder.add_conditional_edges("reasoner", reasoner_router)
builder.add_edge("tools", "reasoner")
builder.add_conditional_edges("critic", critic_router)

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from packages.config.settings import settings

# Create a connection pool for durable state checkpointing across workers
pool = ConnectionPool(conninfo=settings.database_url, max_size=20, open=True)
checkpointer = PostgresSaver(pool)
checkpointer.setup()  # Ensures the checkpoints tables exist

agent_graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"]
)