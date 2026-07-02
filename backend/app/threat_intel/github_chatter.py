"""Threat-actor chatter via public GitHub (free, no key).

Monitors publicly available GitHub repositories for exploit / proof-of-concept
(PoC) code and CVE references — a defensive early-warning signal for security
teams. Read-only use of the public GitHub Search API. If GITHUB_TOKEN is set,
it is used to raise the rate limit; otherwise unauthenticated search is used.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone

import httpx

from ..models import Citation
from .models import ChatterHit, ChatterResponse

SEARCH_URL = "https://api.github.com/search/repositories"
USER_AGENT = "NexusOSINT-MVP/0.1 (defensive threat intel)"

_CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.I)
_POC_RE = re.compile(r"\b(poc|proof.of.concept|exploit|0day|zero.day|rce|lpe|payload)\b", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _days_since(iso: str) -> float | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0


def _severity(*, poc: bool, days: float | None, stars: int) -> str:
    """Fresh, PoC-flagged, and widely-starred repos warrant more attention."""
    if not poc:
        return "Low"
    recent = days is not None and days <= 30
    if recent and stars >= 25:
        return "Critical"
    if recent or stars >= 50:
        return "High"
    return "Medium"


async def search(query: str, *, limit: int = 15) -> ChatterResponse:
    q = query.strip()
    # Bias the query toward security-relevant repos.
    gh_query = q if _CVE_RE.search(q) else f"{q} exploit OR poc OR vulnerability"
    citation = Citation(
        source="GitHub (public repositories)",
        url=f"https://github.com/search?q={q.replace(' ', '+')}&type=repositories",
        retrieved_at=_now(),
    )
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(
            SEARCH_URL,
            params={"q": gh_query, "sort": "updated", "order": "desc", "per_page": limit},
            timeout=25.0,
        )
        resp.raise_for_status()
        items = resp.json().get("items") or []

    results: list[ChatterHit] = []
    for it in items:
        desc = it.get("description") or ""
        blob = f"{it.get('full_name','')} {desc} {' '.join(it.get('topics') or [])}"
        cve = ""
        cve_m = _CVE_RE.search(blob) or _CVE_RE.search(q)
        if cve_m:
            cve = cve_m.group(0).upper()
        poc = bool(_POC_RE.search(blob))
        pushed = it.get("pushed_at") or ""
        stars = it.get("stargazers_count") or 0
        results.append(
            ChatterHit(
                name=it.get("name") or "",
                full_name=it.get("full_name") or "",
                description=desc[:240],
                url=it.get("html_url") or "",
                stars=stars,
                language=it.get("language") or "",
                pushed_at=pushed,
                topics=(it.get("topics") or [])[:6],
                cve=cve,
                poc_flag=poc,
                severity=_severity(poc=poc, days=_days_since(pushed), stars=stars),
            )
        )

    flagged = sum(1 for r in results if r.poc_flag)
    if not results:
        summary = f'No public GitHub repositories matched "{q}".'
    else:
        summary = f'{len(results)} public GitHub repo(s) matching "{q}"'
        summary += f" — {flagged} flagged as exploit/PoC." if flagged else "."
    return ChatterResponse(summary=summary, query=q, results=results, citation=citation)
