import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, ToolMessage
from langsmith import traceable

from packages.agent.graph import agent_graph
from apps.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/agent", tags=["Agent"])

class AgentRequest(BaseModel):
    query: str
    job_id: str  # Use job_id instead of user_id for thread_id to prevent collision

class ResumeRequest(BaseModel):
    job_id: str
    action: str  # "approve" or "reject"

@traceable(name="agentlab-stream")
async def event_generator(query: str, job_id: str, user_id: str) -> AsyncGenerator[str, None]:
    state_update = {
        "messages": [HumanMessage(content=query)],
        "user_id": user_id,  # Securely injected from token
    }
    config = {"configurable": {"thread_id": job_id}}

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

        current_state = agent_graph.get_state(config) #type:ignore
        
        if current_state.next:
            payload = {"type": "interrupt", "pending_node": current_state.next[0]}
            yield f"data: {json.dumps(payload)}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@traceable(name="agentlab-resume")
async def resume_generator(job_id: str, action: str, user_id: str) -> AsyncGenerator[str, None]:
    config = {"configurable": {"thread_id": job_id}}
    state = agent_graph.get_state(config) #type:ignore
    
    if not state or not state.next:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Job is not in an interrupted state'})}\n\n"
        return

    # Security check: Ensure the user owns this job state
    # (Since we are using MemorySaver, state might not strictly enforce this without DB. We check state dict.)
    if state.values.get("user_id") != user_id:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Unauthorized job access'})}\n\n"
        return

    if action == "reject":
        last_message = state.values["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            rejection_msg = ToolMessage(
                content="Action REJECTED by human supervisor. You must use an alternative strategy or ask the user for clarification.",
                tool_call_id=last_message.tool_calls[0]["id"],
                name=last_message.tool_calls[0]["name"]
            )
            agent_graph.update_state(config, {"messages": [rejection_msg]}, as_node="tools") #type:ignore

    try:
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
async def stream_agent_execution(
    request: AgentRequest,
    current_user: dict = Depends(get_current_user)
):
    return StreamingResponse(
        event_generator(query=request.query, job_id=request.job_id, user_id=current_user["id"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )

@router.post("/resume")
async def resume_agent_execution(
    request: ResumeRequest,
    current_user: dict = Depends(get_current_user)
):
    return StreamingResponse(
        resume_generator(job_id=request.job_id, action=request.action, user_id=current_user["id"]),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )