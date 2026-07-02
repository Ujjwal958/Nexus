# Nexus MVP — Test Plan

App: local build. Frontend http://localhost:3000 (Next.js), backend http://localhost:8000 (FastAPI). No auth. No PR/CI (local-only per user request).

## Test 1: It should track live flights conversationally with citations
1. Click suggestion chip "Show flights near London".
   - PASS: assistant reply contains "Tracking N aircraft within 60 nm of Greater London" with N > 0.
   - PASS: citation line "[1] adsb.lol (ADS-B network)" appears under the reply and is a link.
   - PASS: map flies to London and shows blue aircraft icons (>5 markers).
   - PASS: data cards show flight callsigns with Registration/ICAO24/Altitude/Ground speed fields (real values, not "—" everywhere).

## Test 2: It should report recent earthquakes near a place (USGS)
1. Type "Recent earthquakes near Tokyo" and send.
   - PASS: reply states "Found N earthquakes of M3.0+ within 800 km of 東京都 in the last 7 days" (N > 0).
   - PASS: map flies to Japan; red circular markers appear.
   - PASS: cards show "M{x} — {place}, Japan" with Magnitude/Depth fields and a USGS "source link".
   - PASS: citation shows "USGS Earthquake Hazards Program".

## Test 3: It should parse query parameters (magnitude/days) from natural language
1. Type "M5+ earthquakes in the last 3 days".
   - PASS: reply says "earthquakes of M5.0+ worldwide in the last 3 days" — proving mag=5 and days=3 were parsed, not defaults (3.0/7).
   - PASS: all cards show Magnitude ≥ 5.0.

## Test 4: It should fetch live weather and geocode places
1. Type "Weather in Odesa".
   - PASS: reply gives condition + temperature °C; violet marker on Odesa; weather card with Temperature/Humidity/Wind/Cloud cover; citation "Open-Meteo".
2. Type "Locate Port of Rotterdam".
   - PASS: reply gives coordinates ~51.9, 4.4; green marker; map flies to Rotterdam; citation "OpenStreetMap Nominatim".

## Test 5: It should show help for unrecognized queries (fallback)
1. Type "hello".
   - PASS: help text listing example queries appears; no tool call, no map change.
