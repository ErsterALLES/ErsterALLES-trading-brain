# ERS-8 recovered next step

**Recovered:** 2026-05-15 (ERS-9)  
**Issue:** ERS-8 — install three Trading Brain foundation skills into Paperclip

## What ERS-8 already delivered (repo)

| Artifact | Purpose |
|----------|---------|
| `agent-skills/trading-foundation/SKILL.md` | Risk / portfolio governor |
| `agent-skills/market-data/SKILL.md` | Polymarket + Hyperliquid collectors |
| `agent-skills/signal-scoring/SKILL.md` | Signal ensemble scoring |
| `skills/*` | Symlinks so project skill scans find the same files |
| `scripts/verify-ers8-skills.sh` | Local preflight (structure + `slug`/`key` frontmatter) |
| `scripts/install-ers8-paperclip-skills.sh` | Company library import + optional CEO agent sync |

Local preflight passes when run from repo root:

```bash
./scripts/verify-ers8-skills.sh
```

## Recovered missing next step (operational)

ERS-8 closed after repo prep but **without executing the Paperclip import**. The missing step is:

1. Run `./scripts/ers8-next-step.sh` from a Paperclip agent runtime (or VPS shell) where these env vars are set:
   - `PAPERCLIP_API_URL`
   - `PAPERCLIP_API_KEY`
   - `PAPERCLIP_COMPANY_ID`
   - `PAPERCLIP_RUN_ID`
   - Optional: `PAPERCLIP_AGENT_ID` (CEO) to sync skills onto the agent after import
   - Optional: `PAPERCLIP_ISSUE_IDENTIFIER=ERS-8` (default) for disposition script
2. Confirm the company library lists all three skills (installer prints matching keys).
3. Disposition script posts a comment and sets **ERS-8** to `done` (or `blocked` if import fails).

Import sources (GitHub paths on `main`):

- `ErsterALLES/ErsterALLES-trading-brain/trading-foundation`
- `ErsterALLES/ErsterALLES-trading-brain/market-data`
- `ErsterALLES/ErsterALLES-trading-brain/signal-scoring`

## Success criteria

- `./scripts/verify-ers8-skills.sh` exits 0
- `./scripts/install-ers8-paperclip-skills.sh` completes without curl/jq errors
- Company skills API shows the three `ErsterALLES/ErsterALLES-trading-brain/*` keys
- CEO agent (if synced) can invoke the skills on the next trading task

## Blocker note (cloud agent heartbeat)

Cursor Cloud runs for this repo inject `PAPERCLIP_*` identity vars but **not** `PAPERCLIP_API_KEY` (verified 2026-05-15 CEO rotation heartbeat). `GET /api/agents/me` returns 401 without Bearer auth; `./scripts/ers8-next-step.sh` exits 2 after local verify passes.

**Unblock owner:** board operator / Paperclip host admin.  
**Unblock action:** add `PAPERCLIP_API_KEY` to `CLOUD_AGENT_INJECTED_SECRET_NAMES`, then re-wake CEO or run `./scripts/install-ers8-paperclip-skills.sh` on the VPS with the same env vars.

## After import (out of ERS-8 scope)

Per `plans/paperclip-foundation-readiness-report.md`, next foundation skills to stage: `signal-ingestion`, `strategy-distillation-video`, `strategy-spec-authoring`, `risk-manager`, `execution-safety`.
