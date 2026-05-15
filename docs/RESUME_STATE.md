# Trading Brain — Resume State
# AUTO-GENERATED: Do not edit manually unless you know what you're doing
# This file survives LLM context-window resets and allows the agent to resume work

## System Status (last updated: 2026-05-15T09:52 UTC)

### Running Components
- **signal_collector.py** ✅ Running (cronjob `trading-cycle`, every 5min)
- **shadow_executor.py** ✅ Running (same cronjob)
- **Chrome headless** ✅ Installed at `/opt/data/bin/google-chrome`
- **Paperclip CEO** 🔄 Assignment ERS-8 "in progress"

### Open Shadow Positions (3)
| Asset | Direction | Entry | SL | TP | Unrealized PnL |
|-------|-----------|-------|-----|-----|----------------|
| BTC | SHORT | $80,463 | $81,299 | $79,209 | +$0.05 |
| DOGE | SHORT | $0.1145 | $0.1173 | $0.1103 | +$0.03 |
| XRP | SHORT | $1.463 | $1.493 | $1.419 | +$0.02 |

### Capital
- Initial: $231.84 USDC
- Current: $231.84 (unrealized +$0.10)
- Mode: SHADOW (no real money)

## In-Progress Tasks (DO NOT restart from scratch)
These tasks were interrupted and must be RESUMED, not restarted:

1. **Live Position Tracker** — Partially built, needs completion
   - File: `trading-engine/position_tracker.py` (NOT YET CREATED)
   - Status: Was about to build when interrupted
   - Resume from: Create file + wire into cronjob

2. **Performance Dashboard** — Not started
   - File: `reports/performance_dashboard.py`
   - Status: Planned but not started
   - Resume from: Read shadow_trades.json + calculate metrics

3. **Telegram Reporter** — Not started
   - File: `trading-engine/telegram_reporter.py`
   - Status: Planned but not started
   - Resume from: Read portfolio state, format Telegram message, send

4. **Heatmap Scraper (real)** — Partially researched
   - APIs tested: CoinGlass (timeout), CoinAnk (404), Binance (401)
   - Working: Funding-rate proxy already in signal_collector
   - Next: Browser-based scraping of CoinGlass/TradingView heatmap pages
   - Resume from: Playwright script to screenshot heatmap pages

5. **Video Analysis Pipeline** — Not started
   - File: `ingestion/video_analyzer.py`
   - Status: Not started
   - Resume from: Install yt-dlp, create pipeline

## Blocked / Waiting
- **Paperclip Skill Import**: CEO working on ERS-8, check before retrying manual import
- **Live Trading Connector**: Blocked until 2+ weeks shadow validation

## Next Action (highest priority)
The agent should pick the highest-priority uncompleted task and resume it.
Current priority (as set by user "machen wir fertig"):
1. Finish Live Position Tracker + Performance Dashboard
2. Build Telegram Reporter
3. Real Heatmap Scraper
4. Video Analysis Pipeline

## How to Resume After Interruption
1. Read this file first
2. Check cronjob status: `cronjob(action='list')`
3. Check latest signals: `cat data/signals/latest_signals.json`
4. Check portfolio: `cat data/trades/shadow_portfolio.json`
5. Pick highest-priority task from queue
6. Continue from last known state (don't restart)
