import type { Citation } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type Severity = "Critical" | "High" | "Medium" | "Low" | "Safe";

export interface RiskScore {
  score: number;
  severity: Severity;
  factors: string[];
}

export interface RansomwareVictim {
  victim: string;
  group: string;
  country: string;
  activity: string;
  attack_date: string;
  discovered: string;
  domain: string;
  claim_url: string;
  post_url: string;
  description: string;
  data_leaked: boolean;
  risk: RiskScore;
}

export interface ChatterHit {
  name: string;
  full_name: string;
  description: string;
  url: string;
  stars: number;
  language: string;
  pushed_at: string;
  topics: string[];
  cve: string;
  poc_flag: boolean;
  severity: Severity;
}

export interface BlockchainAddress {
  address: string;
  chain: string;
  balance_btc: number;
  total_received_btc: number;
  total_sent_btc: number;
  tx_count: number;
  first_seen: string;
  last_seen: string;
  note: string;
}

export interface ThreatSummary {
  ransomware_24h: number;
  ransomware_severity: Severity;
  active_groups: number;
}

export interface RansomwareResponse {
  summary: string;
  victims: RansomwareVictim[];
  citation: Citation;
}

export interface ChatterResponse {
  summary: string;
  query: string;
  results: ChatterHit[];
  citation: Citation;
}

export interface BlockchainResponse {
  summary: string;
  result: BlockchainAddress | null;
  citation: Citation;
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    let detail = `API error ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const getThreatSummary = () => getJSON<ThreatSummary>("/api/threat/summary");

export const getRecentRansomware = (hours: number, opts: { country?: string; industry?: string; group?: string } = {}) => {
  const p = new URLSearchParams({ hours: String(hours), limit: "60" });
  if (opts.country) p.set("country", opts.country);
  if (opts.industry) p.set("industry", opts.industry);
  if (opts.group) p.set("group", opts.group);
  return getJSON<RansomwareResponse>(`/api/threat/ransomware/recent?${p.toString()}`);
};

export const searchChatter = (q: string) =>
  getJSON<ChatterResponse>(`/api/threat/chatter/search?q=${encodeURIComponent(q)}&limit=15`);

export const lookupBlockchain = (address: string) =>
  getJSON<BlockchainResponse>(`/api/threat/blockchain/address?address=${encodeURIComponent(address)}`);
