"""Shared data models for Nexus tool results and API payloads."""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Provenance for a piece of intelligence."""

    source: str
    url: str
    retrieved_at: str


class MapPoint(BaseModel):
    """A geo point rendered on the live map."""

    id: str
    lat: float
    lon: float
    label: str
    kind: Literal["flight", "earthquake", "weather", "place"]
    heading: Optional[float] = None
    meta: dict[str, Any] = Field(default_factory=dict)


class DataCard(BaseModel):
    """A rich preview card shown in the dashboard."""

    kind: Literal["flight", "earthquake", "weather", "place"]
    title: str
    subtitle: str = ""
    fields: list[dict[str, str]] = Field(default_factory=list)


class ToolResult(BaseModel):
    """Normalized output of every OSINT tool."""

    tool: str
    summary: str
    cards: list[DataCard] = Field(default_factory=list)
    points: list[MapPoint] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    focus: Optional[dict[str, float]] = None  # {lat, lon, zoom} for map flyTo


class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    intent: str
    tool_used: Optional[str] = None
    llm_used: bool = False
    cards: list[DataCard] = Field(default_factory=list)
    points: list[MapPoint] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    focus: Optional[dict[str, float]] = None
