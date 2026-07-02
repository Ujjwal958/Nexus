"""Ransomware intelligence via ransomware.live (free, no key).

Public, read-only aggregation of ransomware group leak-site posts.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from ..models import Citation
from .models import (
    GroupsResponse,
    RansomwareGroup,
    RansomwareResponse,
    RansomwareVictim,
)
from .scoring import ransomware_risk

BASE = "https://api.ransomware.live/v2"
USER_AGENT = "NexusOSINT-MVP/0.1 (defensive threat intel)"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _citation(path: str) -> Citation:
    return Citation(source="ransomware.live", url=f"{BASE}{path}", retrieved_at=_now())


def _parse_dt(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _hours_since(value: str) -> Optional[float]:
    dt = _parse_dt(value)
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0


async def recent_victims(
    *,
    hours: int = 72,
    country: Optional[str] = None,
    industry: Optional[str] = None,
    group: Optional[str] = None,
    limit: int = 60,
) -> RansomwareResponse:
    citation = _citation("/recentvictims")
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        resp = await client.get(f"{BASE}/recentvictims", timeout=25.0)
        resp.raise_for_status()
        raw = resp.json() or []

    victims: list[RansomwareVictim] = []
    for v in raw:
        posted = v.get("discovered") or v.get("attackdate") or ""
        age = _hours_since(posted)
        if age is not None and age > hours:
            continue
        activity = v.get("activity") or ""
        vc = (v.get("country") or "").strip()
        if country and country.strip().upper() not in {vc.upper(), _country_name(vc).upper()}:
            continue
        if industry and industry.strip().lower() not in activity.lower():
            continue
        gname = v.get("group") or ""
        if group and group.strip().lower() != gname.lower():
            continue
        data_leaked = bool(v.get("screenshot")) or bool(v.get("data_size"))
        victims.append(
            RansomwareVictim(
                victim=v.get("victim") or v.get("domain") or "(unknown)",
                group=gname,
                country=vc,
                activity=activity,
                attack_date=v.get("attackdate") or "",
                discovered=posted,
                domain=v.get("domain") or "",
                claim_url=v.get("claim_url") or "",
                post_url=v.get("url") or "",
                description=(v.get("description") or "")[:280],
                data_leaked=data_leaked,
                risk=ransomware_risk(data_leaked=data_leaked, industry=activity),
            )
        )
        if len(victims) >= limit:
            break

    victims.sort(key=lambda x: x.risk.score, reverse=True)
    filt = []
    if group:
        filt.append(f"group {group}")
    if country:
        filt.append(f"country {country}")
    if industry:
        filt.append(f"industry {industry}")
    scope = (" matching " + ", ".join(filt)) if filt else ""
    summary = (
        f"{len(victims)} ransomware victim(s) posted in the last {hours}h{scope}."
        if victims
        else f"No ransomware victims posted in the last {hours}h{scope}."
    )
    return RansomwareResponse(summary=summary, victims=victims, citation=citation)


async def active_groups(limit: int = 60) -> GroupsResponse:
    citation = _citation("/groups")
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        resp = await client.get(f"{BASE}/groups", timeout=25.0)
        resp.raise_for_status()
        raw = resp.json() or []

    groups: list[RansomwareGroup] = []
    for g in raw:
        locations = g.get("locations")
        groups.append(
            RansomwareGroup(
                name=g.get("name") or "(unknown)",
                added_date=g.get("added_date") or "",
                description=(g.get("description") or "")[:280],
                locations=len(locations) if isinstance(locations, list) else 0,
                url=f"https://www.ransomware.live/group/{g.get('name')}" if g.get("name") else "",
            )
        )
    groups.sort(key=lambda x: x.added_date, reverse=True)
    groups = groups[:limit]
    summary = f"{len(groups)} tracked ransomware groups (most recently added first)."
    return GroupsResponse(summary=summary, groups=groups, citation=citation)


_COUNTRY_NAMES = {
    "US": "USA",
    "GB": "UK",
    "DE": "Germany",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "BR": "Brazil",
    "CA": "Canada",
    "AU": "Australia",
    "IN": "India",
    "JP": "Japan",
    "NL": "Netherlands",
}


def _country_name(code: str) -> str:
    return _COUNTRY_NAMES.get(code.upper(), code)
