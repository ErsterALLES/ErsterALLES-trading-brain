import json
import os
from datetime import datetime, timezone
import math

# ─── CONFIG ──────────────────────────────────────────────────────
PORTFOLIO_FILE = "/opt/data/projects/trading-brain/data/trades/shadow_portfolio.json"
REPORT_FILE = "/opt/data/projects/trading-brain/reports/daily_performance.json"
REPORT_MD = "/opt/data/projects/trading-brain/reports/daily_performance.md"

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def calc_sharpe(returns, risk_free=0):
    """Sharpe ratio from daily returns"""
    if len(returns) < 2:
        return 0
    avg = sum(returns) / len(returns)
    variance = sum((r - avg) ** 2 for r in returns) / len(returns)
    std = math.sqrt(variance) if variance > 0 else 0.0001
    if std == 0:
        return 0
    return (avg - risk_free) / std

def calc_max_drawdown(equity_curve):
    """Maximum drawdown percentage"""
    if not equity_curve or len(equity_curve) < 2:
        return 0
    peak = equity_curve[0]
    max_dd = 0
    for val in equity_curve:
        if val > peak:
            peak = val
        dd = (peak - val) / peak if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
    return max_dd * 100

def generate_report():
    portfolio = load_json(PORTFOLIO_FILE)
    if not portfolio:
        print("⚠️ No portfolio data")
        return
    
    closed = portfolio.get("closed_positions", [])
    open_pos = portfolio.get("open_positions", [])
    
    # Basic stats
    total_trades = portfolio.get("total_trades", 0)
    wins = portfolio.get("winning_trades", 0)
    losses = portfolio.get("losing_trades", 0)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    # PnL stats
    total_pnl = sum(t.get("pnl", 0) for t in closed) if closed else 0
    avg_win = sum(t["pnl"] for t in closed if t.get("pnl", 0) > 0) / wins if wins > 0 else 0
    avg_loss = sum(t["pnl"] for t in closed if t.get("pnl", 0) <= 0) / losses if losses > 0 else 0
    profit_factor = abs(sum(t["pnl"] for t in closed if t.get("pnl", 0) > 0) / sum(t["pnl"] for t in closed if t.get("pnl", 0) < 0)) if losses > 0 else float('inf')
    
    # Asset breakdown
    asset_stats = {}
    for t in closed:
        asset = t["asset"]
        if asset not in asset_stats:
            asset_stats[asset] = {"trades": 0, "pnl": 0, "wins": 0}
        asset_stats[asset]["trades"] += 1
        asset_stats[asset]["pnl"] += t.get("pnl", 0)
        if t.get("pnl", 0) > 0:
            asset_stats[asset]["wins"] += 1
    
    # Equity curve approximation (from trades)
    initial = 231.84
    equity_curve = [initial]
    running = initial
    for t in closed:
        running += t.get("pnl", 0)
        equity_curve.append(running)
    
    max_dd = calc_max_drawdown(equity_curve)
    
    # Daily returns (simplified: just daily_pnl / capital)
    daily_returns = [portfolio.get("daily_pnl", 0) / portfolio.get("capital", 231.84)] if portfolio.get("capital") else [0]
    sharpe = calc_sharpe(daily_returns)
    
    # Open positions summary
    open_summary = []
    unrealized_total = 0
    for pos in open_pos:
        unrealized = pos.get("unrealized_pnl", 0)
        unrealized_total += unrealized
        open_summary.append({
            "asset": pos["asset"],
            "direction": pos["direction"],
            "entry": pos["entry_price"],
            "current": pos.get("current_price", pos["entry_price"]),
            "unrealized_pnl": round(unrealized, 2)
        })
    
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "shadow",
        "capital": {
            "initial": 231.84,
            "current": round(portfolio.get("capital", 231.84), 2),
            "total_pnl": round(total_pnl, 2),
            "unrealized": round(unrealized_total, 2)
        },
        "performance": {
            "total_trades": total_trades,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": round(win_rate, 1),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else None,
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2)
        },
        "open_positions": open_summary,
        "asset_breakdown": {k: {
            "trades": v["trades"],
            "win_rate": round(v["wins"] / v["trades"] * 100, 1),
            "pnl": round(v["pnl"], 2)
        } for k, v in asset_stats.items()},
        "equity_curve": [round(e, 2) for e in equity_curve]
    }
    
    save_json(REPORT_FILE, report)
    
    # Markdown report for human reading
    md = f"""# Trading Brain Performance Report
**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | **Mode:** Shadow

## Capital
- **Initial:** $231.84
- **Current:** ${report['capital']['current']}
- **Realized PnL:** ${report['capital']['total_pnl']}
- **Unrealized PnL:** ${report['capital']['unrealized']}

## Performance Metrics
| Metric | Value |
|--------|-------|
| Total Trades | {total_trades} |
| Win Rate | {win_rate:.1f}% |
| Profit Factor | {report['performance']['profit_factor'] or 'N/A'} |
| Sharpe Ratio | {report['performance']['sharpe_ratio']} |
| Max Drawdown | {report['performance']['max_drawdown_pct']}% |
| Avg Win | ${avg_win:.2f} |
| Avg Loss | ${avg_loss:.2f} |

## Open Positions ({len(open_summary)})
"""
    for pos in open_summary:
        emoji = "📈" if pos["direction"] == "LONG" else "📉"
        md += f"- {emoji} **{pos['asset']}** {pos['direction']} | Entry: ${pos['entry']} | Current: ${pos['current']} | Unrealized: ${pos['unrealized_pnl']}\n"
    
    md += f"""
## Asset Breakdown
"""
    for asset, stats in report["asset_breakdown"].items():
        md += f"- **{asset}:** {stats['trades']} trades, {stats['win_rate']}% win, ${stats['pnl']} PnL\n"
    
    with open(REPORT_MD, 'w') as f:
        f.write(md)
    
    print(f"📊 Performance report generated")
    print(f"   JSON: {REPORT_FILE}")
    print(f"   Markdown: {REPORT_MD}")
    print(f"   Capital: ${report['capital']['current']} | Win rate: {win_rate:.1f}% | Trades: {total_trades}")
    
    return report

if __name__ == "__main__":
    try:
        generate_report()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
