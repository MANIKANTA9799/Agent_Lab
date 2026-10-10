'use client';

import { useState } from "react";
import { useAgentStream } from "@/hooks/useAgentStream";

export default function AgentChat() {
    const [input, setInput] = useState("");
    const {
        responseContent,
        agentState,
        isProcessing,
        isInterrupted,
        pendingNode,
        submitQuery,
        resumeQuery
    } = useAgentStream();

    const handleSend = () => {
        if (!input.trim()) return;
        submitQuery(input, "test-user-123");
        setInput("");
    };

    return (
        <div className="max-w-2xl mx-auto p-6 flex flex-col gap-4">
            <div className="bg-slate-50 p-6 rounded-lg min-h-[400px] border flex flex-col">

                {/* Agent Telemetry / Thought Process */}
                {isProcessing && (
                    <div className="mb-4 text-sm font-mono text-blue-600 bg-blue-50 p-2 rounded">
                        {agentState.node === "tools"
                            ? `[⚡ Executing Tool: ${agentState.tool}] searching for: "${agentState.input}"`
                            : `[🧠 Node: ${agentState.node}] Analyzing...`}
                    </div>
                )}

                {/* Human-in-the-Loop Approval Banner */}
                {isInterrupted && (
                    <div className="mb-4 p-4 bg-amber-100 border-l-4 border-amber-500 rounded flex flex-col gap-3">
                        <div>
                            <h3 className="font-bold text-amber-900">Action Required: Approval Needed</h3>
                            <p className="text-sm text-amber-800">
                                The agent is requesting permission to execute node: <strong>{pendingNode}</strong>
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => resumeQuery("test-user-123", "approve")}
                                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-semibold transition"
                            >
                                Approve Execution
                            </button>
                            <button
                                onClick={() => resumeQuery("test-user-123", "reject")}
                                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-semibold transition"
                            >
                                Reject Action
                            </button>
                        </div>
                    </div>
                )}

                {/* Final Synthesized Stream */}
                <div className="prose whitespace-pre-wrap flex-1">
                    {responseContent}
                </div>

            </div>

            <div className="flex gap-2">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && !isProcessing && !isInterrupted && handleSend()}
                    disabled={isProcessing || isInterrupted}
                    className="flex-1 border p-2 rounded disabled:bg-gray-100"
                    placeholder="Ask AgentLab to research something..."
                />
                <button
                    onClick={handleSend}
                    disabled={isProcessing || isInterrupted}
                    className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
                >
                    Research
                </button>
            </div>
        </div>
    );
}