export interface Citation {
  source: string;
  url: string;
  retrieved_at: string;
}

export type PointKind = "flight" | "earthquake" | "weather" | "place";

export interface MapPoint {
  id: string;
  lat: number;
  lon: number;
  label: string;
  kind: PointKind;
  heading?: number | null;
  meta: Record<string, unknown>;
}

export interface DataCard {
  kind: PointKind;
  title: string;
  subtitle: string;
  fields: { label: string; value: string }[];
}

export interface Focus {
  lat: number;
  lon: number;
  zoom: number;
}

export interface ChatResponse {
  reply: string;
  intent: string;
  tool_used: string | null;
  llm_used: boolean;
  cards: DataCard[];
  points: MapPoint[];
  citations: Citation[];
  focus: Focus | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  toolUsed?: string | null;
}
