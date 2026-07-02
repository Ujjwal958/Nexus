"""Conversation engine: intent parsing -> tool routing -> synthesis.

Works fully without any API key (regex intent parser + deterministic
synthesis). If OPENAI_API_KEY is set, the final answer is rewritten by an
LLM for richer investigative narrative — the data and citations are
identical either way.
"""
from __future__ import annotations

import os
import re
from typing import Optional

from .models import ChatResponse, ToolResult
from .tools import flights_near, geocode, recent_earthquakes, weather_at

FLIGHT_RE = re.compile(r"\b(flight|flights|aircraft|plane|planes|jet|jets|air traffic)\b", re.I)
QUAKE_RE = re.compile(r"\b(earthquake|earthquakes|quake|quakes|seismic|tremor)\b", re.I)
WEATHER_RE = re.compile(r"\b(weather|temperature|wind|rain|forecast|storm)\b", re.I)
LOCATE_RE = re.compile(r"\b(locate|where is|find|geocode|show me|map)\b", re.I)

PLACE_RE = re.compile(
    r"(?:near|around|in|at|over|for|of)\s+(?P<place>[A-Za-z][A-Za-z .,'\-]{1,60}?)(?:\s+(?:right now|now|today|currently|please|in the last.*|last.*))?[?.!]?$",
    re.I,
)
MAG_RE = re.compile(r"(?:magnitude|mag|m)\s*(?:>=?|above|over)?\s*(\d+(?:\.\d+)?)", re.I)
DAYS_RE = re.compile(r"last\s+(\d+)\s+day", re.I)

HELP_TEXT = (
    "I'm Nexus, a real-time OSINT co-pilot. Try:\n"
    "- \"Show flights near London\" (live ADS-B via adsb.lol)\n"
    "- \"Recent earthquakes near Tokyo\" or \"M5+ earthquakes in the last 3 days\" (USGS)\n"
    "- \"Weather in Odesa\" (Open-Meteo)\n"
    "- \"Locate Port of Rotterdam\" (OpenStreetMap)\n"
    "Every answer carries source citations."
)


def extract_place(message: str) -> Optional[str]:
    m = PLACE_RE.search(message.strip())
    if not m:
        return None
    place = m.group("place").strip(" .,!?")
    if place.lower() in {"the", "the last", "last", "now", "me", "the world", "worldwide"}:
        return None
    return place


def classify(message: str) -> str:
    if QUAKE_RE.search(message):
        return "earthquakes"
    if FLIGHT_RE.search(message):
        return "flights"
    if WEATHER_RE.search(message):
        return "weather"
    if LOCATE_RE.search(message):
        return "locate"
    return "help"


async def run_tool(intent: str, message: str) -> Optional[ToolResult]:
    place = extract_place(message)
    if intent == "flights":
        return await flights_near(place or "London")
    if intent == "earthquakes":
        mag = MAG_RE.search(message)
        days = DAYS_RE.search(message)
        return await recent_earthquakes(
            place=place,
            days=int(days.group(1)) if days else 7,
            min_magnitude=float(mag.group(1)) if mag else 3.0,
        )
    if intent == "weather":
        return await weather_at(place or "London")
    if intent == "locate":
        return await geocode(place or message)
    return None


async def synthesize_llm(message: str, result: ToolResult) -> Optional[str]:
    """Rewrite the deterministic summary with an LLM, if configured."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)
        cards_text = "\n".join(
            f"- {c.title} ({c.subtitle}): " + ", ".join(f"{f['label']}={f['value']}" for f in c.fields)
            for c in result.cards
        )
        completion = await client.chat.completions.create(
            model=os.environ.get("NEXUS_LLM_MODEL", "gpt-4o-mini"),
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Nexus, an OSINT analyst co-pilot. Write a concise, factual "
                        "intelligence brief (3-5 sentences) from the tool data. Never invent "
                        "data not present in the input. Mention the data source."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Query: {message}\nTool: {result.tool}\nSummary: {result.summary}\nData:\n{cards_text}\nSource: {result.citations[0].source if result.citations else 'n/a'}",
                },
            ],
        )
        return completion.choices[0].message.content
    except Exception:
        return None


async def handle_message(message: str) -> ChatResponse:
    intent = classify(message)
    if intent == "help":
        return ChatResponse(reply=HELP_TEXT, intent="help")

    try:
        result = await run_tool(intent, message)
    except Exception as exc:  # upstream API failure
        return ChatResponse(
            reply=f"The upstream data source failed ({type(exc).__name__}). Try again shortly.",
            intent=intent,
        )
    if result is None:
        return ChatResponse(reply=HELP_TEXT, intent="help")

    llm_reply = await synthesize_llm(message, result)
    return ChatResponse(
        reply=llm_reply or result.summary,
        intent=intent,
        tool_used=result.tool,
        llm_used=llm_reply is not None,
        cards=result.cards,
        points=result.points,
        citations=result.citations,
        focus=result.focus,
    )
