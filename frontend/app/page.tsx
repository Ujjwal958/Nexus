"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import Chat from "@/components/Chat";
import DataCards from "@/components/DataCards";
import ThreatIntel from "@/components/ThreatIntel";
import { sendChat } from "@/lib/api";
import type { ChatMessage, DataCard, Focus, MapPoint } from "@/lib/types";

const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

type Tab = "command" | "threat";

export default function CommandCenter() {
  const [tab, setTab] = useState<Tab>("command");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [points, setPoints] = useState<MapPoint[]>([]);
  const [cards, setCards] = useState<DataCard[]>([]);
  const [focus, setFocus] = useState<Focus | null>(null);

  const handleSend = async (text: string) => {
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    try {
      const res = await sendChat(text);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.reply, citations: res.citations, toolUsed: res.tool_used },
      ]);
      if (res.points.length > 0) setPoints(res.points);
      if (res.cards.length > 0) setCards(res.cards);
      if (res.focus) setFocus({ ...res.focus });
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Backend unreachable. Is the Nexus API running on port 8000?" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ id, label }: { id: Tab; label: string }) => (
    <button
      onClick={() => setTab(id)}
      className={`rounded px-3 py-1 font-mono text-xs tracking-wide transition-colors ${
        tab === id ? "bg-sky-500/20 text-sky-300" : "text-slate-500 hover:text-slate-300"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b border-slate-800 bg-[#0c1118] px-4 py-2.5">
        <div className="flex items-center gap-4">
          <span className="font-mono text-lg font-bold tracking-widest text-sky-400">NEXUS</span>
          <nav className="flex items-center gap-1">
            <TabButton id="command" label="COMMAND CENTER" />
            <TabButton id="threat" label="THREAT INTEL" />
          </nav>
        </div>
        <div className="flex items-center gap-4 font-mono text-xs">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="live-dot h-2 w-2 rounded-full bg-emerald-400" /> LIVE
          </span>
          <span className="hidden text-slate-500 sm:block">
            {tab === "command" ? "4 OSINT sources" : "defensive threat intel"}
          </span>
        </div>
      </header>

      {tab === "command" ? (
        <main className="flex min-h-0 flex-1">
          <section className="flex w-[38%] min-w-[340px] flex-col border-r border-slate-800">
            <Chat messages={messages} loading={loading} onSend={handleSend} />
          </section>
          <section className="flex min-w-0 flex-1 flex-col">
            <div className="h-[58%] min-h-[300px] border-b border-slate-800">
              <MapView points={points} focus={focus} />
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto p-3">
              <DataCards cards={cards} />
            </div>
          </section>
        </main>
      ) : (
        <main className="flex min-h-0 flex-1 flex-col">
          <ThreatIntel />
        </main>
      )}
    </div>
  );
}
