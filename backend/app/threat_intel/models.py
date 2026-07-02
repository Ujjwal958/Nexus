"""Pydantic models for the Threat Intelligence module."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..models import Citation

Severity = str  # "Critical" | "High" | "Medium" | "Low" | "Safe"


class RiskScore(BaseModel):
    score: int
    severity: Severity
    factors: list[str] = Field(default_factory=list)


class RansomwareVictim(BaseModel):
    victim: str
    group: str
    country: str = ""
    activity: str = ""  # industry / sector
    attack_date: str = ""
    discovered: str = ""
    domain: str = ""
    claim_url: str = ""
    post_url: str = ""
    description: str = ""
    data_leaked: bool = False
    risk: RiskScore


class RansomwareGroup(BaseModel):
    name: str
    added_date: str = ""
    description: str = ""
    locations: int = 0  # number of known leak-site mirrors
    url: str = ""


class ChatterHit(BaseModel):
    """A public GitHub repo surfaced for exploit/PoC/CVE threat chatter."""

    name: str
    full_name: str
    description: str = ""
    url: str
    stars: int = 0
    language: str = ""
    pushed_at: str = ""
    topics: list[str] = Field(default_factory=list)
    cve: str = ""
    poc_flag: bool = False
    severity: Severity = "Low"


class BlockchainAddress(BaseModel):
    address: str
    chain: str = "bitcoin"
    balance_btc: float = 0.0
    total_received_btc: float = 0.0
    total_sent_btc: float = 0.0
    tx_count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    note: str = ""


class ThreatSummary(BaseModel):
    ransomware_24h: int = 0
    ransomware_severity: Severity = "Safe"
    active_groups: int = 0


class RansomwareResponse(BaseModel):
    summary: str
    victims: list[RansomwareVictim] = Field(default_factory=list)
    citation: Citation


class GroupsResponse(BaseModel):
    summary: str
    groups: list[RansomwareGroup] = Field(default_factory=list)
    citation: Citation


class ChatterResponse(BaseModel):
    summary: str
    query: str
    results: list[ChatterHit] = Field(default_factory=list)
    citation: Citation


class BlockchainResponse(BaseModel):
    summary: str
    result: Optional[BlockchainAddress] = None
    citation: Citation
