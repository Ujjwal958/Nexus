"use client";

import { useEffect, useRef, useState } from "react";
import type { ChatMessage } from "@/lib/types";

const SUGGESTIONS = [
  "Show flights near London",
  "Recent earthquakes near Tokyo",
  "M5+ earthquakes in the last 3 days",
  "Weather in Odesa",
  "Locate Port of Rotterdam",
];

export default function Chat({
  messages,
  loading,
  onSend,
}: {
  messages: ChatMessage[];
  loading: boolean;
  onSend: (text: string) => void;
}) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const submit = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setInput("");
    onSend(trimmed);
  };

  return (
    <div className="flex h-full flex-col">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="mt-8 space-y-3 text-center">
            <div className="font-mono text-sm text-slate-500">
              Ask about live flights, earthquakes, weather, or locations.
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => submit(s)}
                  className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-400 transition hover:border-sky-600 hover:text-sky-400"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg-in flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                m.role === "user"
                  ? "bg-sky-600/20 text-sky-100"
                  : "border border-slate-800 bg-slate-900/80 text-slate-200"
              }`}
            >
              {m.content}
              {m.role === "assistant" && m.citations && m.citations.length > 0 && (
                <div className="mt-2 border-t border-slate-800 pt-1.5">
                  {m.citations.map((c, j) => (
                    <a
                      key={j}
                      href={c.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block font-mono text-[10px] text-slate-500 hover:text-sky-400"
                    >
                      [{j + 1}] {c.source} · {new Date(c.retrieved_at).toLocaleTimeString()} UTC
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="msg-in flex justify-start">
            <div className="rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-2 font-mono text-xs text-slate-500">
              querying live sources<span className="live-dot">…</span>
            </div>
          </div>
        )}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit(input);
        }}
        className="border-t border-slate-800 p-3"
      >
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Nexus…  e.g. “Show flights near Dubai”"
            className="flex-1 rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-sky-600"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="rounded-md bg-sky-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-500 disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
