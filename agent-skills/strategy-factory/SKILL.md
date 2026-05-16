---
name: strategy-factory
description: "Self-improving strategy discovery, testing, and deployment pipeline"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [trading, strategies, automation, self-improvement, backtest]
    model: opencode/deepseek-v4-flash-free
---

# Strategy Factory

## Purpose
Discovers, backtests, optimizes, and deploys trading strategies automatically. Learns from performance data.

## Pipeline

### Phase 1: Discovery
```
Sources:
- YouTube trading videos (transcribe + extract rules)
- TradingView public strategies
- Academic papers (arXiv)
- Community strategies (Discord, Twitter/X)
```
**Agent**: `claude-code-adapter` (coding)
**Model**: `opencode/deepseek-v4-flash-free` (free for research)

### Phase 2: Implementation
```
Input: Strategy rules (text)
Output: Python strategy file
```
**Agent**: `claude-code-adapter`
**Model**: `claude-sonnet-4` (complex coding) or `gpt-4o` (balanced)

### Phase 3: Backtest
```
Input: Strategy code + historical data
Output: Performance report (win rate, profit factor, max drawdown)
```
**Agent**: `trading-foundation`
**Model**: `opencode/deepseek-v4-flash-free` (free)

### Phase 4: Live Paper Test
```
Input: Strategy + live market data
Duration: 48 hours minimum
```
**Agent**: `paper-trading-engine`
**Model**: `opencode/deepseek-v4-flash-free` (free)

### Phase 5: Deploy or Reject
```
Criteria:
- Win rate > 55%
- Profit factor > 1.3
- Max drawdown < 10%
- Min 10 trades in test period
```
**Agent**: `signal-scoring` (aggregate)
**Model**: `gpt-4o` (decision quality)

## Self-Learning Loop
```
Every 24 hours:
1. Collect performance metrics from all strategies
2. Compare: expected vs actual win rate
3. If strategy underperforms (>10% below expected):
   a. Analyze losing trades
   b. Adjust parameters (e.g., threshold, SL distance)
   c. Re-run paper test for 24h
4. If still underperforming: Archive strategy
5. If new strategy outperforms: Promote to live
```

## Performance Database
```json
{
  "strategies": [
    {
      "name": "vwap_scalper",
      "status": "active",
      "win_rate": 0.62,
      "profit_factor": 1.45,
      "max_dd": 0.08,
      "trades": 150,
      "last_updated": "2026-05-16T09:00:00Z"
    }
  ]
}
```

## Active Strategies Queue
- Max 10 strategies running simultaneously
- New strategies start in "paper" mode
- After 7 days positive performance → "live" mode

## Model Routing
| Task | Agent | Model | Cost |
|------|-------|-------|------|
| Research | Browser | opencode/free | $0 |
| Coding | Claude Code | gpt-4o | ~$0.02/req |
| Backtest | Trading Engine | opencode/free | $0 |
| Decision | CEO | gpt-4o | ~$0.01/req |
| Monitoring | Cronjob | opencode/free | $0 |

## Commands
```bash
# Start strategy factory
curl -X POST https://paperclip-z6c6.srv1357611.hstgr.cloud/api/agents \
  -H "Content-Type: application/json" \
  -d '{"task": "strategy_factory", "skill": "strategy-factory"}'

# Check factory status
curl https://paperclip-z6c6.srv1357611.hstgr.cloud/api/agents/strategy-factory/status
```
