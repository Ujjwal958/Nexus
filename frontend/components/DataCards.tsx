"use client";

import type { DataCard } from "@/lib/types";

const KIND_BADGE: Record<string, { label: string; cls: string }> = {
  flight: { label: "FLIGHT", cls: "bg-sky-500/15 text-sky-400 border-sky-500/30" },
  earthquake: { label: "SEISMIC", cls: "bg-red-500/15 text-red-400 border-red-500/30" },
  weather: { label: "WEATHER", cls: "bg-violet-500/15 text-violet-400 border-violet-500/30" },
  place: { label: "GEO", cls: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" },
};

function FieldValue({ value }: { value: string }) {
  if (value.startsWith("http")) {
    return (
      <a href={value} target="_blank" rel="noreferrer" className="text-sky-400 underline decoration-dotted">
        source link
      </a>
    );
  }
  return <span>{value}</span>;
}

export default function DataCards({ cards }: { cards: DataCard[] }) {
  if (cards.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-xs text-slate-600">
        Data cards from your queries will appear here.
      </div>
    );
  }
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
      {cards.map((card, i) => {
        const badge = KIND_BADGE[card.kind] ?? KIND_BADGE.place;
        return (
          <div key={i} className="msg-in rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="mb-1 flex items-center justify-between gap-2">
              <span className="truncate font-mono text-sm font-semibold text-slate-100">{card.title}</span>
              <span className={`shrink-0 rounded border px-1.5 py-0.5 text-[10px] font-semibold tracking-wider ${badge.cls}`}>
                {badge.label}
              </span>
            </div>
            {card.subtitle && <div className="mb-2 truncate text-xs text-slate-500">{card.subtitle}</div>}
            <dl className="space-y-1">
              {card.fields.map((f, j) => (
                <div key={j} className="flex justify-between gap-2 font-mono text-xs">
                  <dt className="text-slate-500">{f.label}</dt>
                  <dd className="truncate text-slate-300">
                    <FieldValue value={f.value} />
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        );
      })}
    </div>
  );
}
