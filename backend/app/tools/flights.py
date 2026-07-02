"""Live aircraft near a location via the adsb.lol ADS-B API (free, no key)."""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from ..models import Citation, DataCard, MapPoint, ToolResult
from .geocode import resolve_place

ADSB_URL = "https://api.adsb.lol/v2/lat/{lat}/lon/{lon}/dist/{nm}"
USER_AGENT = "NexusOSINT-MVP/0.1 (https://github.com/nexus-osint)"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def flights_near(place: str, radius_nm: int = 60, limit: int = 40) -> ToolResult:
    citation = Citation(source="adsb.lol (ADS-B network)", url="https://api.adsb.lol", retrieved_at=_now())
    async with httpx.AsyncClient() as client:
        loc = await resolve_place(client, place)
        if not loc:
            return ToolResult(
                tool="flights_near",
                summary=f'Could not locate "{place}" to search for flights.',
                citations=[citation],
            )
        resp = await client.get(
            ADSB_URL.format(lat=loc["lat"], lon=loc["lon"], nm=radius_nm),
            headers={"User-Agent": USER_AGENT},
            timeout=20.0,
        )
        resp.raise_for_status()
        aircraft = resp.json().get("ac") or []

    points: list[MapPoint] = []
    cards: list[DataCard] = []
    for ac in aircraft[:limit]:
        lat, lon = ac.get("lat"), ac.get("lon")
        if lat is None or lon is None:
            continue
        callsign = (ac.get("flight") or "").strip()
        hexcode = ac.get("hex", "")
        name = callsign or ac.get("r") or hexcode
        alt = ac.get("alt_geom") or ac.get("alt_baro")
        gs = ac.get("gs")
        track = ac.get("track")
        points.append(
            MapPoint(
                id=f"flight-{hexcode}",
                lat=lat,
                lon=lon,
                label=name,
                kind="flight",
                heading=track,
                meta={"type": ac.get("t"), "reg": ac.get("r")},
            )
        )
        if len(cards) < 8:
            cards.append(
                DataCard(
                    kind="flight",
                    title=name,
                    subtitle=ac.get("t") or "Unknown type",
                    fields=[
                        {"label": "Registration", "value": ac.get("r") or "—"},
                        {"label": "ICAO24", "value": hexcode},
                        {"label": "Altitude", "value": f"{alt} ft" if isinstance(alt, (int, float)) else str(alt or "—")},
                        {"label": "Ground speed", "value": f"{gs:.0f} kt" if gs else "—"},
                        {"label": "Track", "value": f"{track:.0f}°" if track is not None else "—"},
                        {"label": "Squawk", "value": ac.get("squawk") or "—"},
                    ],
                )
            )

    n = len(points)
    name_short = loc["name"].split(",")[0]
    summary = (
        f"No aircraft currently broadcasting within {radius_nm} nm of {name_short}."
        if n == 0
        else f"Tracking {n} aircraft within {radius_nm} nm of {name_short} right now."
    )
    return ToolResult(
        tool="flights_near",
        summary=summary,
        cards=cards,
        points=points,
        citations=[citation],
        focus={"lat": loc["lat"], "lon": loc["lon"], "zoom": 8},
    )
