"use client";

import { useEffect, useState } from "react";
import {
  getRecentRansomware,
  getThreatSummary,
  lookupBlockchain,
  searchChatter,
  type BlockchainResponse,
  type ChatterResponse,
  type RansomwareResponse,
  type Severity,
  type ThreatSummary,
} from "@/lib/threat";

const SEV: Record<Severity, { text: string; ring: string; dot: string }> = {
  Critical: { text: "text-red-400", ring: "border-red-500/40 bg-red-500/10", dot: "bg-red-500" },
  High: { text: "text-orange-400", ring: "border-orange-500/40 bg-orange-500/10", dot: "bg-orange-500" },
  Medium: { text: "text-yellow-400", ring: "border-yellow-500/40 bg-yellow-500/10", dot: "bg-yellow-500" },
  Low: { text: "text-blue-400", ring: "border-blue-500/40 bg-blue-500/10", dot: "bg-blue-500" },
  Safe: { text: "text-emerald-400", ring: "border-emerald-500/40 bg-emerald-500/10", dot: "bg-emerald-500" },
};

function SevBadge({ severity }: { severity: Severity }) {
  const s = SEV[severity] ?? SEV.Low;
  return (
    <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-semibold tracking-wider ${s.ring} ${s.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} />
      {severity.toUpperCase()}
    </span>
  );
}

function timeAgo(iso: string): string {
  if (!iso) return "—";
  const d = new Date(iso).getTime();
  if (Number.isNaN(d)) return iso;
  const mins = Math.floor((Date.now() - d) / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 48) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function SectionErr({ msg }: { msg: string }) {
  return <div className="rounded border border-red-500/30 bg-red-500/5 p-3 text-xs text-red-400">{msg}</div>;
}

function Spinner({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 text-xs text-slate-500">
      <span className="h-3 w-3 animate-spin rounded-full border-2 border-slate-600 border-t-sky-400" />
      {label}
    </div>
  );
}

export default function ThreatIntel() {
  const [summary, setSummary] = useState<ThreatSummary | null>(null);

  const [hours, setHours] = useState(72);
  const [rw, setRw] = useState<RansomwareResponse | null>(null);
  const [rwLoading, setRwLoading] = useState(false);
  const [rwErr, setRwErr] = useState("");

  const [chatterQ, setChatterQ] = useState("CVE-2024-3094");
  const [chatter, setChatter] = useState<ChatterResponse | null>(null);
  const [chatterLoading, setChatterLoading] = useState(false);
  const [chatterErr, setChatterErr] = useState("");

  const [addr, setAddr] = useState("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa");
  const [chain, setChain] = useState<BlockchainResponse | null>(null);
  const [chainLoading, setChainLoading] = useState(false);
  const [chainErr, setChainErr] = useState("");

  useEffect(() => {
    getThreatSummary().then(setSummary).catch(() => setSummary(null));
  }, []);

  const loadRansomware = async (h: number) => {
    setRwLoading(true);
    setRwErr("");
    try {
      setRw(await getRecentRansomware(h));
    } catch (e) {
      setRwErr(e instanceof Error ? e.message : "Failed to load ransomware feed.");
    } finally {
      setRwLoading(false);
    }
  };

  useEffect(() => {
    loadRansomware(hours);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hours]);

  const runChatter = async () => {
    if (!chatterQ.trim()) return;
    setChatterLoading(true);
    setChatterErr("");
    try {
      setChatter(await searchChatter(chatterQ.trim()));
    } catch (e) {
      setChatterErr(e instanceof Error ? e.message : "GitHub search failed.");
    } finally {
      setChatterLoading(false);
    }
  };

  const runChain = async () => {
    if (!addr.trim()) return;
    setChainLoading(true);
    setChainErr("");
    try {
      setChain(await lookupBlockchain(addr.trim()));
    } catch (e) {
      setChainErr(e instanceof Error ? e.message : "Blockchain lookup failed.");
    } finally {
      setChainLoading(false);
    }
  };

  useEffect(() => {
    runChatter();
    runChain();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-0 flex-1 overflow-y-auto">
      <div className="mx-auto max-w-6xl space-y-4 p-3 sm:space-y-5 sm:p-5">
        {/* Alert badges */}
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <div className={`rounded-lg border p-3 ${summary ? SEV[summary.ransomware_severity].ring : "border-slate-800 bg-slate-900/60"}`}>
            <div className="text-[10px] uppercase tracking-widest text-slate-400">Ransomware · 24h</div>
            <div className={`mt-1 font-mono text-2xl font-bold ${summary ? SEV[summary.ransomware_severity].text : "text-slate-200"}`}>
              {summary ? summary.ransomware_24h : "…"}
            </div>
            <div className="text-[10px] text-slate-500">new victims posted</div>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="text-[10px] uppercase tracking-widest text-slate-400">Tracked Groups</div>
            <div className="mt-1 font-mono text-2xl font-bold text-slate-200">{summary ? summary.active_groups : "…"}</div>
            <div className="text-[10px] text-slate-500">ransomware operators</div>
          </div>
          <div className="rounded-lg border border-purple-500/30 bg-purple-500/5 p-3">
            <div className="text-[10px] uppercase tracking-widest text-slate-400">Threat Chatter</div>
            <div className="mt-1 font-mono text-2xl font-bold text-purple-300">{chatter ? chatter.results.length : "…"}</div>
            <div className="text-[10px] text-slate-500">public exploit/PoC repos</div>
          </div>
          <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3">
            <div className="text-[10px] uppercase tracking-widest text-slate-400">Blockchain</div>
            <div className="mt-1 font-mono text-2xl font-bold text-amber-300">
              {chain?.result ? `${chain.result.balance_btc.toFixed(2)}` : "…"}
            </div>
            <div className="text-[10px] text-slate-500">BTC on tracked address</div>
          </div>
        </div>

        {/* Ransomware victims */}
        <section className="rounded-lg border border-slate-800 bg-slate-900/40">
          <header className="flex items-center justify-between border-b border-slate-800 px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              <h2 className="font-mono text-sm font-semibold text-slate-100">Ransomware Victims</h2>
            </div>
            <div className="flex gap-1">
              {[24, 48, 72].map((h) => (
                <button
                  key={h}
                  onClick={() => setHours(h)}
                  className={`rounded px-2 py-0.5 font-mono text-xs ${hours === h ? "bg-sky-500/20 text-sky-300" : "text-slate-500 hover:text-slate-300"}`}
                >
                  {h}h
                </button>
              ))}
            </div>
          </header>
          <div className="p-3">
            {rwLoading && <Spinner label="Loading ransomware.live feed…" />}
            {rwErr && <SectionErr msg={rwErr} />}
            {rw && !rwLoading && (
              <>
                <div className="mb-2 text-xs text-slate-500">{rw.summary}</div>
                <div className="grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-3">
                  {rw.victims.slice(0, 12).map((v, i) => (
                    <div key={i} className="msg-in rounded-lg border border-slate-800 bg-slate-950/50 p-3">
                      <div className="mb-1.5 flex items-center justify-between gap-2">
                        <SevBadge severity={v.risk.severity} />
                        <span className="truncate font-mono text-xs text-slate-400">{v.group}</span>
                      </div>
                      <div className="truncate font-mono text-sm font-semibold text-slate-100">{v.victim}</div>
                      <div className="mb-2 truncate text-xs text-slate-500">
                        {[v.country, v.activity].filter(Boolean).join(" · ") || "—"}
                      </div>
                      <dl className="space-y-1 font-mono text-xs">
                        <div className="flex justify-between gap-2">
                          <dt className="text-slate-500">Posted</dt>
                          <dd className="text-slate-300">{timeAgo(v.discovered)}</dd>
                        </div>
                        <div className="flex justify-between gap-2">
                          <dt className="text-slate-500">Data leaked</dt>
                          <dd className={v.data_leaked ? "text-red-400" : "text-slate-400"}>{v.data_leaked ? "Yes" : "Unconfirmed"}</dd>
                        </div>
                        <div className="flex justify-between gap-2">
                          <dt className="text-slate-500">Risk</dt>
                          <dd className="text-slate-300">{v.risk.score}/100</dd>
                        </div>
                      </dl>
                      {v.post_url && (
                        <a href={v.post_url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-xs text-sky-400 underline decoration-dotted">
                          View on ransomware.live
                        </a>
                      )}
                    </div>
                  ))}
                </div>
                <SourceLine source={rw.citation.source} url={rw.citation.url} at={rw.citation.retrieved_at} />
              </>
            )}
          </div>
        </section>

        {/* Threat chatter (GitHub) */}
        <section className="rounded-lg border border-slate-800 bg-slate-900/40">
          <header className="flex items-center gap-2 border-b border-slate-800 px-4 py-2.5">
            <span className="h-2 w-2 rounded-full bg-purple-500" />
            <h2 className="font-mono text-sm font-semibold text-slate-100">Threat Chatter · Exploit / PoC / CVE</h2>
          </header>
          <div className="p-3">
            <div className="mb-3 flex gap-2">
              <input
                value={chatterQ}
                onChange={(e) => setChatterQ(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && runChatter()}
                placeholder="CVE-2024-3094, or a product/keyword"
                className="flex-1 rounded border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 outline-none focus:border-sky-500"
              />
              <button onClick={runChatter} className="rounded bg-sky-500/20 px-3 py-1.5 font-mono text-xs text-sky-300 hover:bg-sky-500/30">
                Search
              </button>
            </div>
            {chatterLoading && <Spinner label="Querying GitHub…" />}
            {chatterErr && <SectionErr msg={chatterErr} />}
            {chatter && !chatterLoading && (
              <>
                <div className="mb-2 text-xs text-slate-500">{chatter.summary}</div>
                <div className="space-y-2">
                  {chatter.results.map((r, i) => (
                    <div key={i} className="msg-in rounded-lg border border-slate-800 bg-slate-950/50 p-3">
                      <div className="mb-1 flex items-center justify-between gap-2">
                        <a href={r.url} target="_blank" rel="noreferrer" className="truncate font-mono text-sm text-sky-400 underline decoration-dotted">
                          {r.full_name}
                        </a>
                        <div className="flex shrink-0 items-center gap-2">
                          {r.poc_flag && <SevBadge severity={r.severity} />}
                          <span className="font-mono text-xs text-slate-500">★ {r.stars}</span>
                        </div>
                      </div>
                      {r.description && <div className="mb-1.5 text-xs text-slate-400">{r.description}</div>}
                      <div className="flex flex-wrap items-center gap-2 font-mono text-[10px] text-slate-500">
                        {r.cve && <span className="rounded border border-red-500/30 bg-red-500/10 px-1.5 py-0.5 text-red-400">{r.cve}</span>}
                        {r.language && <span>{r.language}</span>}
                        <span>updated {timeAgo(r.pushed_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <SourceLine source={chatter.citation.source} url={chatter.citation.url} at={chatter.citation.retrieved_at} />
              </>
            )}
          </div>
        </section>

        {/* Blockchain */}
        <section className="rounded-lg border border-slate-800 bg-slate-900/40">
          <header className="flex items-center gap-2 border-b border-slate-800 px-4 py-2.5">
            <span className="h-2 w-2 rounded-full bg-amber-500" />
            <h2 className="font-mono text-sm font-semibold text-slate-100">Blockchain Tracer · Bitcoin</h2>
          </header>
          <div className="p-3">
            <div className="mb-3 flex gap-2">
              <input
                value={addr}
                onChange={(e) => setAddr(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && runChain()}
                placeholder="Bitcoin address"
                className="flex-1 rounded border border-slate-700 bg-slate-950 px-3 py-1.5 font-mono text-xs text-slate-200 outline-none focus:border-amber-500"
              />
              <button onClick={runChain} className="rounded bg-amber-500/20 px-3 py-1.5 font-mono text-xs text-amber-300 hover:bg-amber-500/30">
                Trace
              </button>
            </div>
            {chainLoading && <Spinner label="Querying blockchain.info…" />}
            {chainErr && <SectionErr msg={chainErr} />}
            {chain && !chainLoading && (
              <>
                <div className="mb-2 text-xs text-slate-500">{chain.summary}</div>
                {chain.result && (
                  <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
                    <Stat label="Balance" value={`${chain.result.balance_btc.toFixed(4)} BTC`} accent="text-amber-300" />
                    <Stat label="Received" value={`${chain.result.total_received_btc.toFixed(4)} BTC`} />
                    <Stat label="Sent" value={`${chain.result.total_sent_btc.toFixed(4)} BTC`} />
                    <Stat label="Transactions" value={String(chain.result.tx_count)} />
                    <Stat label="First seen" value={chain.result.first_seen || "—"} />
                    <Stat label="Last seen" value={chain.result.last_seen || "—"} />
                  </div>
                )}
                {chain.result?.note && <div className="mt-2 text-xs text-amber-400/80">{chain.result.note}</div>}
                <SourceLine source={chain.citation.source} url={chain.citation.url} at={chain.citation.retrieved_at} />
              </>
            )}
          </div>
        </section>

        <footer className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-center text-[11px] text-slate-500">
          For authorized defensive security purposes only. All data is sourced from public indices and read-only APIs.
          Nexus never connects to Tor, illegal markets, or private/invite-only services.
        </footer>
      </div>
    </div>
  );
}

function Stat({ label, value, accent = "text-slate-200" }: { label: string; value: string; accent?: string }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-950/50 p-2.5">
      <div className="text-[10px] uppercase tracking-widest text-slate-500">{label}</div>
      <div className={`mt-0.5 font-mono text-sm font-semibold ${accent}`}>{value}</div>
    </div>
  );
}

function SourceLine({ source, url, at }: { source: string; url: string; at: string }) {
  return (
    <div className="mt-3 flex items-center gap-1.5 border-t border-slate-800 pt-2 text-[10px] text-slate-600">
      <span>Source:</span>
      <a href={url} target="_blank" rel="noreferrer" className="text-sky-500/80 underline decoration-dotted">
        {source}
      </a>
      <span>· retrieved {timeAgo(at)}</span>
    </div>
  );
}
