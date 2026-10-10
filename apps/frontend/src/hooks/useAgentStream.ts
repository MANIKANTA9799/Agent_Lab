import { useState } from "react";

interface AgentState {
    node: string;
    tool: string;
    input: string;
}

export function useAgentStream() {
    const [responseContent, setResponseContent] = useState("");
    const [agentState, setAgentState] = useState<AgentState>({ node: "", tool: "", input: "" });
    const [isProcessing, setIsProcessing] = useState(false);

    // New HITL states
    const [isInterrupted, setIsInterrupted] = useState(false);
    const [pendingNode, setPendingNode] = useState("");

    const processStream = async (response: Response) => {
        if (!response.body) throw new Error("No response body returned from server.");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const dataStr = line.slice(6);
                    if (!dataStr) continue;

                    try {
                        const event = JSON.parse(dataStr);

                        if (event.type === "node_start") {
                            setAgentState((prev) => ({ ...prev, node: event.node }));
                        } else if (event.type === "tool_start") {
                            setAgentState((prev) => ({ ...prev, tool: event.tool, input: event.input }));
                        } else if (event.type === "token") {
                            setResponseContent((prev) => prev + event.content);
                        } else if (event.type === "interrupt") {
                            setIsInterrupted(true);
                            setPendingNode(event.pending_node);
                            setIsProcessing(false); // Pause loading state
                        } else if (event.type === "done") {
                            setIsProcessing(false);
                            setIsInterrupted(false);
                            setAgentState({ node: "", tool: "", input: "" });
                        }
                    } catch (e) {
                        console.warn("JSON parse error on partial SSE chunk", dataStr);
                    }
                }
            }
        }
    };

    const submitQuery = async (query: string, userId: string) => {
        setIsProcessing(true);
        setIsInterrupted(false);
        setResponseContent("");
        setAgentState({ node: "reasoner", tool: "", input: "" });

        try {
            const response = await fetch("http://127.0.0.1:8000/api/v1/agent/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query, user_id: userId }),
            });
            await processStream(response);
        } catch (error) {
            console.error("Stream failed:", error);
            setIsProcessing(false);
        }
    };

    const resumeQuery = async (userId: string, action: "approve" | "reject") => {
        setIsProcessing(true);
        setIsInterrupted(false);

        try {
            const response = await fetch("http://127.0.0.1:8000/api/v1/agent/resume", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, action }),
            });
            await processStream(response);
        } catch (error) {
            console.error("Resume failed:", error);
            setIsProcessing(false);
        }
    };

    return { responseContent, agentState, isProcessing, isInterrupted, pendingNode, submitQuery, resumeQuery };
}