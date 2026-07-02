"""Place -> coordinates via OpenStreetMap Nominatim (free, no key)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from ..models import Citation, DataCard, MapPoint, ToolResult

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "NexusOSINT-MVP/0.1 (https://github.com/nexus-osint)"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def resolve_place(client: httpx.AsyncClient, place: str) -> Optional[dict]:
    """Return the top Nominatim hit for a free-text place, or None."""
    resp = await client.get(
        NOMINATIM_URL,
        params={"q": place, "format": "jsonv2", "limit": 1, "addressdetails": 0},
        headers={"User-Agent": USER_AGENT},
        timeout=15.0,
    )
    resp.raise_for_status()
    hits = resp.json()
    if not hits:
        return None
    hit = hits[0]
    return {
        "lat": float(hit["lat"]),
        "lon": float(hit["lon"]),
        "name": hit.get("display_name", place),
    }


async def geocode(place: str) -> ToolResult:
    async with httpx.AsyncClient() as client:
        hit = await resolve_place(client, place)

    citation = Citation(source="OpenStreetMap Nominatim", url=NOMINATIM_URL, retrieved_at=_now())
    if not hit:
        return ToolResult(
            tool="geocode",
            summary=f'Could not locate "{place}".',
            citations=[citation],
        )

    point = MapPoint(
        id=f"place-{hit['lat']}-{hit['lon']}",
        lat=hit["lat"],
        lon=hit["lon"],
        label=hit["name"],
        kind="place",
    )
    card = DataCard(
        kind="place",
        title=hit["name"].split(",")[0],
        subtitle=hit["name"],
        fields=[
            {"label": "Latitude", "value": f"{hit['lat']:.5f}"},
            {"label": "Longitude", "value": f"{hit['lon']:.5f}"},
        ],
    )
    return ToolResult(
        tool="geocode",
        summary=f"Located {hit['name']} at {hit['lat']:.4f}, {hit['lon']:.4f}.",
        cards=[card],
        points=[point],
        citations=[citation],
        focus={"lat": hit["lat"], "lon": hit["lon"], "zoom": 9},
    )
