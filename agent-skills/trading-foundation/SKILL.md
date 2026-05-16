---
name: trading-foundation
description: "Risk management, paper trading engine, and position sizing"
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [trading, risk, paper-trading, hyperliquid]
    model: opencode/deepseek-v4-flash-free
---

# Trading Foundation

## Purpose
Handles position sizing, risk limits, paper trading simulation, and trade execution logging.

## Risk Limits
- Max risk per trade: 2.0% of balance
- Max risk per session: 5.0% of balance
- Leverage: 20x (futures mode)
- Stop Loss: Always set (max 2% from entry)
- Take Profit: 1.5:1 RRR minimum

## Position Sizing
```python
def calculate_position_size(balance, risk_pct, entry, stop_loss, leverage=20):
    risk_amount = balance * (risk_pct / 100)
    price_distance = abs(entry - stop_loss) / entry
    position_size = (risk_amount / price_distance) * leverage
    return min(position_size, balance * 0.5)  # Max 50% of balance
```

## Paper Trading Engine
```python
# Simulates trades without real money
# Logs: entry, exit, pnl, fees, slippage
# Tracks: win rate, profit factor, max drawdown
```

## Live Trading Bridge (Future)
```python
# Will use Hyperliquid SDK:
# from hyperliquid.exchange import Exchange
# exchange = Exchange(wallet, base_url="https://api.hyperliquid.xyz")
# exchange.order("BTC", True, 0.01, 42000, {"limit": {"tif": "Gtc"}})
```

## Performance Tracking
- Daily P&L tracking
- Win rate per strategy
- Sharpe ratio calculation
- Max drawdown alerts

## Usage
```bash
cd /opt/data/projects/trading-brain/trading-engine
python3 paper_trading_engine.py
```

## Backup
All trades saved to: `/opt/data/projects/trading-brain/data/trades/`
