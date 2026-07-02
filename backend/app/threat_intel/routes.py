"""FastAPI routes for the Threat Intelligence module."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from . import blockchain, github_chatter, ransomware
from .models import (
    BlockchainResponse,
    ChatterResponse,
    GroupsResponse,
    RansomwareResponse,
    ThreatSummary,
)

router = APIRouter(prefix="/api/threat", tags=["threat-intel"])

DISCLAIMER = (
    "For authorized defensive security purposes only. All data is sourced from "
    "public indices and read-only APIs."
)


def _worst_severity(victims) -> str:
    order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Safe": 0}
    worst = "Safe"
    for v in victims:
        if order.get(v.risk.severity, 0) > order.get(worst, 0):
            worst = v.risk.severity
    return worst


async def _safe(coro, what: str):
    try:
        return await coro
    except Exception as exc:  # upstream failure
        raise HTTPException(status_code=502, detail=f"{what} source failed: {type(exc).__name__}") from exc


@router.get("/disclaimer")
async def disclaimer() -> dict:
    return {"disclaimer": DISCLAIMER}


@router.get("/summary", response_model=ThreatSummary)
async def summary() -> ThreatSummary:
    victims_resp = await _safe(ransomware.recent_victims(hours=24, limit=200), "Ransomware")
    groups_resp = await _safe(ransomware.active_groups(limit=1000), "Ransomware")
    return ThreatSummary(
        ransomware_24h=len(victims_resp.victims),
        ransomware_severity=_worst_severity(victims_resp.victims),
        active_groups=len(groups_resp.groups),
    )


@router.get("/ransomware/recent", response_model=RansomwareResponse)
async def ransomware_recent(
    hours: int = Query(72, ge=1, le=720),
    country: Optional[str] = None,
    industry: Optional[str] = None,
    group: Optional[str] = None,
    limit: int = Query(60, ge=1, le=200),
) -> RansomwareResponse:
    return await _safe(
        ransomware.recent_victims(hours=hours, country=country, industry=industry, group=group, limit=limit),
        "Ransomware",
    )


@router.get("/ransomware/groups", response_model=GroupsResponse)
async def ransomware_groups(limit: int = Query(60, ge=1, le=400)) -> GroupsResponse:
    return await _safe(ransomware.active_groups(limit=limit), "Ransomware")


@router.get("/chatter/search", response_model=ChatterResponse)
async def chatter_search(
    q: str = Query(..., min_length=2, max_length=80),
    limit: int = Query(15, ge=1, le=50),
) -> ChatterResponse:
    return await _safe(github_chatter.search(q, limit=limit), "GitHub")


@router.get("/blockchain/address", response_model=BlockchainResponse)
async def blockchain_address(
    address: str = Query(..., min_length=10, max_length=100),
    chain: str = Query("bitcoin"),
) -> BlockchainResponse:
    return await _safe(blockchain.lookup(address, chain=chain), "Blockchain")
