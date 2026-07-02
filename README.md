# Nexus Intelligence Platform — MVP

A real-time, conversational OSINT co-pilot. Ask natural-language questions and get
live data with full source provenance, rendered on an interactive dark-mode map
with rich data cards.

## Live data sources (free, no API key required)

| Domain | Source |
|--------|--------|
| Aviation (live ADS-B) | adsb.lol |
| Seismic | USGS Earthquake Hazards Program |
| Weather | Open-Meteo |
| Geocoding | OpenStreetMap Nominatim |

## Architecture

- `backend/` — Python 3.10+, FastAPI. Conversation engine: intent classifier →
  tool router → OSINT tool adapters → synthesis. Every response carries citations.
  Optional LLM narrative synthesis via OpenAI (set `OPENAI_API_KEY`); works fully
  without it via deterministic summaries.
- `frontend/` — Next.js 14 + TypeScript + Tailwind. Command Center layout:
  chat panel (left) + MapLibre GL live map and data cards (right).

## Run

```bash
# Backend (port 8000)
cd backend
uv venv && uv pip install -e '.[llm]'
.venv/bin/uvicorn app.main:app --port 8000

# Frontend (port 3000)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and try:
- "Show flights near London"
- "Recent earthquakes near Tokyo"
- "M5+ earthquakes in the last 3 days"
- "Weather in Odesa"
- "Locate Port of Rotterdam"

## Optional LLM synthesis

```bash
export OPENAI_API_KEY=sk-...
export NEXUS_LLM_MODEL=gpt-4o-mini   # default
```
