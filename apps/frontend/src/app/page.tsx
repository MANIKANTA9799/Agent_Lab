// app/page.tsx
import AgentChat from "@/components/AgentChat";

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-white">
      <h1 className="text-2xl font-bold text-center mb-6">AgentLab Research Platform</h1>
      <AgentChat />
    </main>
  );
}