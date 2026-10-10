import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, ToolMessage

from packages.agent.graph import agent_graph

router = APIRouter(prefix="/agent", tags=["Agent"])

class AgentRequest(BaseModel):
    query: str
    user_id: str

class ResumeRequest(BaseModel):
    user_id: str
    action: str  # "approve" or "reject"

async def event_generator(query: str, user_id: str) -> AsyncGenerator[str, None]:
    state_update = {
        "messages": [HumanMessage(content=query)],
        "user_id": user_id,
    }
    config = {"configurable": {"thread_id": user_id}}

    try:
        async for event in agent_graph.astream_events(
            state_update, #type:ignore
            config=config, #type:ignore
            version="v2"
        ): #type:ignore
            event_type = event.get("event")

            if event_type == "on_chain_start" and event.get("name") in ["reasoner", "tools", "critic"]:
                payload = {"type": "node_start", "node": event.get("name")}
                yield f"data: {json.dumps(payload)}\n\n"

            elif event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    payload = {"type": "token", "content": chunk.content}
                    yield f"data: {json.dumps(payload)}\n\n"

            elif event_type == "on_tool_start":
                payload = {
                    "type": "tool_start",
                    "tool": event.get("name"),
                    "input": event.get("data", {}).get("input"),
                }
                yield f"data: {json.dumps(payload)}\n\n"

            await asyncio.sleep(0.01)

        # Inspect the persisted graph state after the execution loop finishes
        current_state = agent_graph.get_state(config) #type:ignore
        
        # If 'next' contains a node (e.g., 'tools'), we hit a HITL breakpoint
        if current_state.next:
            payload = {"type": "interrupt", "pending_node": current_state.next[0]}
            yield f"data: {json.dumps(payload)}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

async def resume_generator(user_id: str, action: str) -> AsyncGenerator[str, None]:
    config = {"configurable": {"thread_id": user_id}}

    if action == "reject":
        state = agent_graph.get_state(config) #type:ignore
        last_message = state.values["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            rejection_msg = ToolMessage(
                content="Action REJECTED by human supervisor. You must use an alternative strategy or ask the user for clarification.",
                tool_call_id=last_message.tool_calls[0]["id"],
                name=last_message.tool_calls[0]["name"]
            )
            agent_graph.update_state(config, {"messages": [rejection_msg]}, as_node="tools") #type:ignore

    try:
        # Passing None tells LangGraph to continue execution
        async for event in agent_graph.astream_events(None, config=config, version="v2"): #type:ignore
            event_type = event.get("event")

            if event_type == "on_chain_start" and event.get("name") in ["reasoner", "tools", "critic"]:
                payload = {"type": "node_start", "node": event.get("name")}
                yield f"data: {json.dumps(payload)}\n\n"

            elif event_type == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    payload = {"type": "token", "content": chunk.content}
                    yield f"data: {json.dumps(payload)}\n\n"

            elif event_type == "on_tool_start":
                payload = {
                    "type": "tool_start",
                    "tool": event.get("name"),
                    "input": event.get("data", {}).get("input"),
                }
                yield f"data: {json.dumps(payload)}\n\n"

            await asyncio.sleep(0.01)

        final_state = agent_graph.get_state(config) #type:ignore
        if final_state.next:
            yield f"data: {json.dumps({'type': 'interrupt', 'pending_node': final_state.next[0]})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.post("/stream")
async def stream_agent_execution(request: AgentRequest):
    return StreamingResponse(
        event_generator(query=request.query, user_id=request.user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )

@router.post("/resume")
async def resume_agent_execution(request: ResumeRequest):
    return StreamingResponse(
        resume_generator(user_id=request.user_id, action=request.action),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )