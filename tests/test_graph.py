import asyncio
import os
import os
from dotenv import load_dotenv

load_dotenv()

print("=== LANGSMITH DEBUG ===")
print("TRACING:", os.getenv("LANGSMITH_TRACING"))
print("PROJECT:", os.getenv("LANGSMITH_PROJECT"))
print("API KEY:", bool(os.getenv("LANGSMITH_API_KEY")))
print("=======================")

from langsmith import traceable

@traceable(name="graph-file-test")
def test_trace():
    return "hello"

print("TRACE TEST:", test_trace())

from packages.agent.graph import agent_graph
from langchain_core.messages import HumanMessage
from langsmith import traceable

from packages.agent.graph import agent_graph


@traceable(name="agentlab-graph-test")
async def run_graph():
    state = {
        "messages": [
            HumanMessage(content="What is LangGraph?")
        ],
        "user_id": "test-user",
        "context": "",
        "past_queries": [],
        "loop_count": 0,
    }

    config = {
        "configurable": {
            "thread_id": "langsmith-test-123"
        }
    }

    async for event in agent_graph.astream_events(
        state,
        config=config,
        version="v2",
    ):
        print(event["event"])


asyncio.run(run_graph())