from .state import AgentState
from langchain_ollama import ChatOllama
from packages.agent.tools import search_research_knowledgebase
from langchain_core.messages import ToolMessage,HumanMessage
llm = ChatOllama(model="llama3.1:latest", temperature=0).bind_tools([search_research_knowledgebase])

tools_by_name = {
    search_research_knowledgebase.name: search_research_knowledgebase
}
async def reasoner_node(state: AgentState) -> dict:
    """Invokes the LLM asynchronously to allow token streaming."""
    
    # Change invoke() to await ainvoke()
    response = await llm.ainvoke(state["messages"])
    
    current_loops = state.get("loop_count", 0) + 1
    return {"messages": [response], "loop_count": current_loops}
def tool_node(state: AgentState) -> dict:
    """Executes tool calls requested by the reasoner and returns ToolMessages."""
    last_message = state["messages"][-1]
    tool_messages = []

    # Extract all tool calls requested by the last AIMessage
    tool_calls = getattr(last_message, "tool_calls", [])

    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Forcefully inject user_id from AgentState for security (prevent IDOR)
        if "user_id" in state:
            tool_args["user_id"] = state["user_id"]

        # Look up tool in registry and execute
        tool = tools_by_name.get(tool_name)
        if tool:
            output = tool.invoke(tool_args)
        else:
            output = f"Error: Tool '{tool_name}' not found."

        # Construct a ToolMessage linked back to the tool_call_id
        tool_messages.append(
            ToolMessage(
                content=str(output),
                tool_call_id=tool_call["id"],
                name=tool_name,
            )
        )

    return {"messages": tool_messages}


from langchain_core.messages import SystemMessage, AIMessage

async def critic_node(state: AgentState) -> dict:
    """Evaluates the Reasoner's response and decides whether to approve or reject."""
    print("Entering critic...")
    
    # Extract the original user query and the Reasoner's latest answer
    original_query = state["messages"][0].content
    latest_answer = state["messages"][-1].content
    
    # System prompt forcing the Critic into a strict evaluation role
    eval_prompt = f"""You are a strict QA Critic. 
User Query: {original_query}
Agent Answer: {latest_answer}

If the Agent Answer relies on general knowledge, is unhelpful, or fails to answer the query, respond ONLY with "REJECT: <reason>".
If the Agent Answer is specific, grounded, and answers the query, respond ONLY with "APPROVE".
"""
    
    # Use a fresh, fast LLM call (temperature=0 for deterministic evaluation)
    critic_llm = ChatOllama(model="llama3.1:latest", temperature=0)
    evaluation = await critic_llm.ainvoke([SystemMessage(content=eval_prompt)])
    
    # If rejected, append the rejection as a HumanMessage to force the Reasoner to fix it
    if "REJECT" in evaluation.content.upper(): #type:ignore 
        return {"messages": [HumanMessage(content=f"QA Review Failed. You must improve your answer based on this feedback: {evaluation.content}")]}
    
    # If approved, we don't need to add anything to the state.
    return {}