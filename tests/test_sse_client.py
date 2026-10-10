import asyncio
import httpx
import json

async def test_agent_stream():
    url = "http://127.0.0.1:8000/api/v1/agent/stream"
    payload = {
        "query": "Research why solid state batteries are safer than standard lithium-ion batteries.",
        "user_id": "test-user-123"
    }

    print("🚀 Connecting to AgentLab SSE Stream...\n")

    # Connect to the streaming endpoint
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=payload, timeout=60.0) as response:
            # Iterate through the raw bytes line-by-line
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                
                # Strip the "data: " SSE prefix
                data_str = line[6:]
                if not data_str:
                    continue
                    
                try:
                    event = json.loads(data_str)
                    
                    # Route UI updates based on event type
                    if event["type"] == "node_start":
                        print(f"\n\n[🔄 Transitioning to Node: {event['node']}]")
                    elif event["type"] == "tool_start":
                        print(f"\n\n[🛠️ Tool Call: {event['tool']}] -> Input: {event['input']}")
                    elif event["type"] == "token":
                        # Print LLM tokens seamlessly on the same line
                        print(event["content"], end="", flush=True)
                    elif event["type"] == "done":
                        print("\n\n✅ Stream Complete.")
                    elif event["type"] == "error":
                        print(f"\n\n❌ Error: {event['message']}")
                        
                except json.JSONDecodeError:
                    print(f"\nFailed to parse JSON: {data_str}")

if __name__ == "__main__":
    asyncio.run(test_agent_stream())