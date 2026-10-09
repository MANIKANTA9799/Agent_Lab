from .state import AgentState
from langchain_ollama import ChatOllama
from packages.agent.tools import search_research_knowledgebase
from langchain_core.messages import ToolMessage
llm = ChatOllama(model="llama3.1:latest", temperature=0).bind_tools([search_research_knowledgebase])

tools_by_name = {
    search_research_knowledgebase.name: search_research_knowledgebase
}
def reasoner_node(state: AgentState) -> dict:
   response = llm.invoke(state["messages"])
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

        # If user_id is missing from tool_args, inject it from AgentState for security
        if "user_id" not in tool_args and "user_id" in state:
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


