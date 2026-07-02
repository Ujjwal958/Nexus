"""Risk scoring engine for threat intelligence findings."""
from __future__ import annotations

from .models import RiskScore

CRITICAL_SECTORS = {
    "healthcare",
    "health care",
    "hospital",
    "energy",
    "utilities",
    "water",
    "transportation",
    "government",
    "public administration",
    "financial",
    "finance",
    "banking",
}


def _severity(score: int) -> str:
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def ransomware_risk(*, data_leaked: bool, industry: str) -> RiskScore:
    """Ransomware victims are inherently high risk; leaked data and critical
    infrastructure sectors push the score toward Critical."""
    score = 50
    factors = ["Active ransomware victim"]

    if data_leaked:
        score += 30
        factors.append("Data confirmed leaked")

    if (industry or "").strip().lower() in CRITICAL_SECTORS:
        score += 20
        factors.append("Critical infrastructure sector")

    score = min(score, 100)
    return RiskScore(score=score, severity=_severity(score), factors=factors)
