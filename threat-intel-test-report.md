# Nexus Threat Intel Module — Test Report

Date: 2026-07-02 · Servers: frontend :3000, backend :8000 · Lint/typecheck: clean (0 errors)

## Result: 3/3 tests passed

### Test 1 — Ransomware Victims (ransomware.live) ✔
Filtered feed to last 24h: 17 victims shown, matching the "Ransomware · 24h" alert badge. Severity badges (CRITICAL, red), risk scores (80–100/100), data-leaked flags, time-ago timestamps, and clickable ransomware.live citations all render.

![Ransomware 24h feed](/home/ubuntu/screenshots/ss_c19beb83.png)

### Test 2 — Threat Chatter (GitHub exploit/PoC/CVE search) ✔
Searched "log4shell": 15 public repos returned, 3 flagged as exploit/PoC with HIGH severity badges; CVE tags (CVE-2021-44228), star counts, language and freshness metadata shown, plus GitHub source citation.

![log4shell chatter results](/home/ubuntu/screenshots/ss_e940e3a4.png)

### Test 3 — Blockchain Tracer (blockchain.info) ✔
Traced the Bitcoin genesis address `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`: balance 107.2323 BTC, received 107.2323, sent 0.0000, 63,406 transactions, last seen 2026-07-02. First-seen correctly omitted with an accuracy note for high-volume addresses.

![Blockchain trace + legal disclaimer](/home/ubuntu/screenshots/ss_de09c144.png)

## Notes
- Dark-web source (Ahmia) was swapped for GitHub threat chatter per user decision (Ahmia blocks automated queries from this VM).
- Legal disclaimer footer present: defensive use only, public read-only sources, no Tor/illegal markets.
