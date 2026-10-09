import uuid
from langchain_core.messages import HumanMessage
from packages.agent.graph import agent_graph

def run_agent_test():
    test_user_id = str(uuid.uuid4())
    
    # Define the initial AgentState payload
    initial_state = {
        "messages": [
            HumanMessage(
                content="Research why solid state batteries are safer than standard lithium-ion batteries."
            )
        ],
        "user_id": test_user_id,
        "context": "",
        "past_queries": [],
        "loop_count": 0,
    }

    print("🚀 Invoking AgentLab Agent Graph...\n")
    
    # Execute the graph
    final_state = agent_graph.invoke(initial_state) # type:ignore 

    print("\n execution complete. Messages trail:")
    for msg in final_state["messages"]:
        role = msg.__class__.__name__
        print(f"\n[{role}]")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"Tool Calls: {msg.tool_calls}")
        else:
            print(f"Content: {msg.content}")

if __name__ == "__main__":
    run_agent_test()