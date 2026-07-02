# Nexus OSINT MVP — Test Report

**Result: 5/5 tests passed** (one bug found mid-test, fixed, and re-verified). App running locally: frontend `http://localhost:3000`, backend `http://localhost:8000`.

## Results

- ✅ **Live flights near London** — "Tracking 40 aircraft within 60 nm of Greater London"; blue heading-rotated markers on the map; flight cards with real Registration/ICAO24/Altitude/Speed; clickable `adsb.lol` citation.
- ✅ **Earthquakes near Tokyo (USGS)** — 18 M3.0+ quakes in last 7 days; map flew to Japan with red markers; seismic cards each with a USGS `source link`.
- ✅ **Natural-language filters** — "M5+ earthquakes in the last 3 days" → "18 earthquakes of M5.0+ worldwide in the last 3 days"; all cards ≥ M5.0. *(Initially failed — "the last 3 days" was misparsed as a place and geocoded to a Teresina airport; fixed the place extractor and re-verified.)*
- ✅ **Weather (Open-Meteo)** — Odesa: partly cloudy, 23.4 °C, humidity 82%, wind 3.5 km/h; violet map marker; Open-Meteo citation.
- ✅ **Geocoding (Nominatim)** — "Locate Port of Rotterdam" → 51.9244, 4.4778; map flew to Rotterdam with green marker.
- ✅ **Help fallback** — "hello" returned the help text with example queries; no tool invoked.

## Evidence

| Live flights near London | Earthquakes near Tokyo |
|---|---|
| ![Flights near London](/home/ubuntu/screenshots/ss_bc69c8c4.png) | ![Earthquakes near Tokyo](/home/ubuntu/screenshots/ss_586b8388.png) |

| 🔴 BUG: "last 3 days" parsed as place | 🟢 FIX: worldwide M5+ filter works |
|---|---|
| ![Bug: misparsed place](/home/ubuntu/screenshots/ss_1d6fbe89.png) | ![Fix verified](/home/ubuntu/screenshots/ss_876add70.png) |

| Weather in Odesa | Geocode Rotterdam |
|---|---|
| ![Weather in Odesa](/home/ubuntu/screenshots/ss_8afbfeb3.png) | ![Locate Rotterdam](/home/ubuntu/screenshots/ss_380311f8.png) |

## Notes
- All 4 data sources are free and require no API key. Optional `OPENAI_API_KEY` enables LLM narrative synthesis.
- Flights queries can take 5–20 s (adsb.lol latency); a "querying live sources…" indicator is shown meanwhile.
