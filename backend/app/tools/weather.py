"""Current weather via Open-Meteo (free, no key)."""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from ..models import Citation, DataCard, MapPoint, ToolResult
from .geocode import resolve_place

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
USER_AGENT = "NexusOSINT-MVP/0.1 (https://github.com/nexus-osint)"

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ hail", 99: "Thunderstorm w/ heavy hail",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def weather_at(place: str) -> ToolResult:
    citation = Citation(source="Open-Meteo", url=OPEN_METEO_URL, retrieved_at=_now())
    async with httpx.AsyncClient() as client:
        loc = await resolve_place(client, place)
        if not loc:
            return ToolResult(
                tool="weather_at",
                summary=f'Could not locate "{place}" for a weather report.',
                citations=[citation],
            )
        resp = await client.get(
            OPEN_METEO_URL,
            params={
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code,cloud_cover",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=15.0,
        )
        resp.raise_for_status()
        cur = resp.json().get("current", {})

    condition = WMO_CODES.get(cur.get("weather_code", -1), "Unknown conditions")
    name = loc["name"].split(",")[0]
    card = DataCard(
        kind="weather",
        title=f"Weather — {name}",
        subtitle=condition,
        fields=[
            {"label": "Temperature", "value": f"{cur.get('temperature_2m', '—')} °C"},
            {"label": "Humidity", "value": f"{cur.get('relative_humidity_2m', '—')} %"},
            {"label": "Wind", "value": f"{cur.get('wind_speed_10m', '—')} km/h @ {cur.get('wind_direction_10m', '—')}°"},
            {"label": "Cloud cover", "value": f"{cur.get('cloud_cover', '—')} %"},
        ],
    )
    point = MapPoint(
        id=f"weather-{loc['lat']}-{loc['lon']}",
        lat=loc["lat"],
        lon=loc["lon"],
        label=f"{name}: {condition}, {cur.get('temperature_2m', '?')}°C",
        kind="weather",
    )
    return ToolResult(
        tool="weather_at",
        summary=f"{name}: {condition.lower()}, {cur.get('temperature_2m', '?')}°C, wind {cur.get('wind_speed_10m', '?')} km/h.",
        cards=[card],
        points=[point],
        citations=[citation],
        focus={"lat": loc["lat"], "lon": loc["lon"], "zoom": 8},
    )
