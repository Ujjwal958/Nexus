"""Blockchain address lookup via blockchain.info (free, no key).

Read-only Bitcoin address intelligence: balance, totals, transaction count,
first/last activity. Useful for tracing ransomware / abuse wallet activity
from public reports.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

import httpx

from ..models import Citation
from .models import BlockchainAddress, BlockchainResponse

RAWADDR = "https://blockchain.info/rawaddr/{address}"
USER_AGENT = "NexusOSINT-MVP/0.1 (defensive threat intel)"
SATOSHI = 100_000_000

# Loose validation for legacy / p2sh / bech32 BTC addresses.
_BTC_RE = re.compile(r"^(bc1[a-z0-9]{8,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,39})$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fmt_ts(unix: int) -> str:
    if not unix:
        return ""
    return datetime.fromtimestamp(unix, tz=timezone.utc).strftime("%Y-%m-%d")


async def lookup(address: str, chain: str = "bitcoin") -> BlockchainResponse:
    address = address.strip()
    citation = Citation(
        source="blockchain.info",
        url=f"https://www.blockchain.com/explorer/addresses/btc/{address}",
        retrieved_at=_now(),
    )
    if not _BTC_RE.match(address):
        return BlockchainResponse(
            summary=f'"{address}" does not look like a valid Bitcoin address.',
            result=None,
            citation=citation,
        )

    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        resp = await client.get(RAWADDR.format(address=address), params={"limit": 50}, timeout=25.0)
        resp.raise_for_status()
        data = resp.json()

    txs = data.get("txs") or []
    times = [t.get("time") for t in txs if t.get("time")]
    n_tx = data.get("n_tx") or 0
    # blockchain.info returns newest transactions first, so max(times) is the
    # true last-seen. first-seen is only accurate if the full history fit in
    # this single page (n_tx <= fetched); otherwise we don't claim it.
    last_seen = _fmt_ts(max(times)) if times else ""
    first_seen = _fmt_ts(min(times)) if times and n_tx <= len(txs) else ""
    balance = (data.get("final_balance") or 0) / SATOSHI
    received = (data.get("total_received") or 0) / SATOSHI
    sent = (data.get("total_sent") or 0) / SATOSHI

    notes = []
    if n_tx == 0:
        notes.append("No transactions found for this address.")
    else:
        if balance == 0:
            notes.append("Address has been fully swept (zero balance).")
        if not first_seen:
            notes.append(f"High-volume address ({n_tx} tx); first-seen omitted, last-seen is exact.")
    note = " ".join(notes)

    result = BlockchainAddress(
        address=address,
        chain=chain,
        balance_btc=round(balance, 8),
        total_received_btc=round(received, 8),
        total_sent_btc=round(sent, 8),
        tx_count=n_tx,
        first_seen=first_seen,
        last_seen=last_seen,
        note=note,
    )
    summary = (
        f"BTC {address[:10]}… holds {balance:.4f} BTC across {n_tx} transactions "
        f"(received {received:.4f}, sent {sent:.4f}); active {first_seen or '?'} → {last_seen or '?'}."
    )
    return BlockchainResponse(summary=summary, result=result, citation=citation)
