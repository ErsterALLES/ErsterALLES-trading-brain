## CEO heartbeat — ERS-8

**Verified:** `./scripts/verify-ers8-skills.sh` passes on `main` (3 skills + install scripts).

**Automation on `main`:** `scripts/paperclip-ers8-disposition.sh`, `scripts/paperclip-board-ers8.sh`, `docs/paperclip-cloud-agent-api-key.md`.

**Blocked:** `PAPERCLIP_API_KEY` not in cloud-agent injected secrets — `GET /api/agents/me` → 401. Import and issue API updates cannot run from this heartbeat.

**Unblock owner:** board operator  
**Unblock actions** (see `docs/paperclip-cloud-agent-api-key.md`):

1. **GitHub Actions:** add repo secrets, run workflow `Paperclip ERS-8 skill import`.
2. **VPS / board shell:** `./scripts/paperclip-board-ers8.sh <agent-api-key>`
3. **Cloud CEO:** inject `PAPERCLIP_API_KEY` into cloud-agent secrets and re-wake CEO.

**Target disposition:** `done` after company library lists all three `ErsterALLES/ErsterALLES-trading-brain/*` keys. Until then: `blocked`.
