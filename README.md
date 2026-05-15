# ErsterALLES-trading-brain

Trading Brain / Paperclip Strategy Lab foundation repo. Vision and architecture: [README-TRADING-VISION.md](README-TRADING-VISION.md).

## Foundation skills (ERS-8)

Three Paperclip-importable skills live under `agent-skills/` (mirrored in `skills/`):

| Skill | Path |
|-------|------|
| Trading Foundation | `agent-skills/trading-foundation/` |
| Market Data Collector | `agent-skills/market-data/` |
| Signal Scoring | `agent-skills/signal-scoring/` |

### Recovered next step

After ERS-8 repo work, the operational step is to **import these skills into the Paperclip company library**:

```bash
./scripts/ers8-next-step.sh
```

- Without `PAPERCLIP_API_KEY`, the script runs local verify only and exits `2` with instructions.
- With credentials, it runs `scripts/install-ers8-paperclip-skills.sh` (import + optional agent sync).

Details: [plans/ers8-recovered-next-step.md](plans/ers8-recovered-next-step.md).

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/verify-ers8-skills.sh` | Local structure + frontmatter preflight |
| `scripts/install-ers8-paperclip-skills.sh` | POST import to Paperclip company + list/sync |
| `scripts/ers8-next-step.sh` | Verify then import (recovered ERS-8 next step) |
