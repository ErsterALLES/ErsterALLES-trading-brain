---
id: trading-foundation
slug: trading-foundation
key: ErsterALLES/ErsterALLES-trading-brain/trading-foundation
name: Trading Foundation
version: 1.0.0
category: trading
author: ErsterALLES
tags: [risk, position-sizing, portfolio, trading-modes]
---

# Trading Foundation

Core risk and portfolio management rules for the Trading Brain.

## When to use
- Any trading action before order execution
- Portfolio health checks
- New strategy onboarding
- Mode transitions (shadow → paper → live)

## Execution

### 1. Trading Mode Check
Read `/config/trading-params.yaml` and verify current mode:
- `shadow`: Log only, no real orders, validate signals
- `paper`: Simulate execution with slippage, track P&L
- `live`: Real capital at risk, all governors active

**Rule**: Default to `shadow` if config missing or ambiguous.

### 2. Risk Governor (Pre-Trade)
Before any position opening, verify:
1. **Portfolio Heat**: Σ(open position risk) < max_portfolio_heat% (default: 5%)
2. **Position Size**: size < max_position_size% of equity (default: 2.5%)
3. **Daily Loss Limit**: today's realized + unrealized loss < daily_loss_limit% (default: 3%)
4. **Max Drawdown**: current drawdown from peak < max_drawdown% (default: 10%)

**Action**: If any check fails → BLOCK trade, log reason, alert operator.

### 3. Position Sizing Formula
```
size = min(
  (equity * max_position_size / 100),
  (risk_budget / stop_distance)
)
```
Where:
- `risk_budget` = equity * (max_portfolio_heat / 100) * 0.5
- `stop_distance` = ATR(14) * 2 or fixed % from entry

### 4. Stop Loss / Take Profit
- **Default SL**: 2% from entry (or ATR-based)
- **Default TP**: 5% from entry (2.5:1 R/R minimum)
- **Trailing Stop**: Activate at +3% profit, trail at 1.5x ATR

### 5. Mode Escalation Rules
| From | To | Condition |
|------|-----|-----------|
| shadow | paper | 50+ validated signals, 60%+ hit rate, 7 days shadow |
| paper | live | 30+ paper trades, positive Sharpe, max DD < 5% |
| any | shadow | DD limit breached, 3 consecutive losses, API error |

## Output
Always return a `TradeDecision` object:
```json
{
  "decision": "ALLOWED | BLOCKED",
  "reason": "string",
  "mode": "shadow | paper | live",
  "position_size_usd": 0.0,
  "stop_loss": 0.0,
  "take_profit": 0.0,
  "risk_metrics": {
    "portfolio_heat_after": 0.0,
    "daily_loss_pct": 0.0,
    "max_drawdown_pct": 0.0
  }
}
```
