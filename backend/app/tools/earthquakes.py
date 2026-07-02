"""Recent earthquakes via USGS FDSN event API (free, no key)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

from ..models import Citation, DataCard, MapPoint, ToolResult
from .geocode import resolve_place

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
USER_AGENT = "NexusOSINT-MVP/0.1 (https://github.com/nexus-osint)"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def recent_earthquakes(
    place: Optional[str] = None,
    days: int = 7,
    min_magnitude: float = 3.0,
    limit: int = 30,
) -> ToolResult:
    citation = Citation(source="USGS Earthquake Hazards Program", url=USGS_URL, retrieved_at=_now())
    params: dict = {
        "format": "geojson",
        "starttime": (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d"),
        "minmagnitude": min_magnitude,
        "limit": limit,
        "orderby": "time",
    }
    focus = None
    where = "worldwide"
    async with httpx.AsyncClient() as client:
        if place:
            loc = await resolve_place(client, place)
            if loc:
                params.update({"latitude": loc["lat"], "longitude": loc["lon"], "maxradiuskm": 800})
                focus = {"lat": loc["lat"], "lon": loc["lon"], "zoom": 5}
                where = f"within 800 km of {loc['name'].split(',')[0]}"
        resp = await client.get(USGS_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=20.0)
        resp.raise_for_status()
        data = resp.json()

    points: list[MapPoint] = []
    cards: list[DataCard] = []
    for feat in data.get("features", []):
        props = feat["properties"]
        lon, lat, depth = feat["geometry"]["coordinates"]
        mag = props.get("mag")
        when = datetime.fromtimestamp(props["time"] / 1000, tz=timezone.utc)
        points.append(
            MapPoint(
                id=f"quake-{feat['id']}",
                lat=lat,
                lon=lon,
                label=f"M{mag} {props.get('place', '')}",
                kind="earthquake",
                meta={"mag": mag, "depth_km": depth},
            )
        )
        if len(cards) < 8:
            cards.append(
                DataCard(
                    kind="earthquake",
                    title=f"M{mag} — {props.get('place', 'Unknown location')}",
                    subtitle=when.strftime("%Y-%m-%d %H:%M UTC"),
                    fields=[
                        {"label": "Magnitude", "value": str(mag)},
                        {"label": "Depth", "value": f"{depth:.0f} km"},
                        {"label": "Details", "value": props.get("url", "")},
                    ],
                )
            )

    n = len(points)
    summary = (
        f"No M{min_magnitude}+ earthquakes {where} in the last {days} days."
        if n == 0
        else f"Found {n} earthquakes of M{min_magnitude}+ {where} in the last {days} days."
    )
    return ToolResult(
        tool="recent_earthquakes",
        summary=summary,
        cards=cards,
        points=points,
        citations=[citation],
        focus=focus,
    )
