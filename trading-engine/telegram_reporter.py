import json
import os
from datetime import datetime, timezone

# ─── CONFIG ──────────────────────────────────────────────────────
POSITIONS_FILE = "/opt/data/projects/trading-brain/data/positions/live_positions.json"
SIGNALS_FILE = "/opt/data/projects/trading-brain/data/signals/latest_signals.json"
PORTFOLIO_FILE = "/opt/data/projects/trading-brain/data/trades/shadow_portfolio.json"
REPORT_FILE = "/opt/data/projects/trading-brain/reports/daily_performance.json"

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def build_telegram_message():
    """Build concise Telegram status message"""
    
    positions = load_json(POSITIONS_FILE)
    signals = load_json(SIGNALS_FILE)
    portfolio = load_json(PORTFOLIO_FILE)
    report = load_json(REPORT_FILE)
    
    if not positions or not portfolio:
        return None
    
    ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
    
    # Header
    msg = f"🤖 *Trading Brain Update* — {ts}\n"
    msg += f"💰 Capital: `${portfolio.get('capital', 231.84):.2f}` | Daily PnL: `${portfolio.get('daily_pnl', 0):.2f}`\n\n"
    
    # Active signals
    active_signals = [s for s in signals.get("signals", []) if s.get("signal_type")]
    if active_signals:
        msg += "*🎯 Active Signals*\n"
        for s in active_signals[:5]:
            emoji = "📈" if s["signal_type"] == "LONG" else "📉"
            msg += f"{emoji} {s['asset']} {s['signal_type']} | Conf: {s['confidence']}% | ${s['price']}\n"
        msg += "\n"
    
    # Open positions
    open_pos = portfolio.get("open_positions", [])
    if open_pos:
        msg += "*📌 Open Positions*\n"
        total_unrealized = 0
        for pos in open_pos:
            unrealized = pos.get("unrealized_pnl", 0)
            total_unrealized += unrealized
            emoji = "📈" if pos["direction"] == "LONG" else "📉"
            msg += f"{emoji} {pos['asset']} {pos['direction']} | Entry: ${pos['entry_price']} | Unreal: ${unrealized:.2f}\n"
        msg += f"_Total Unrealized: ${total_unrealized:.2f}_\n\n"
    
    # Daily summary
    total_trades = portfolio.get("total_trades", 0)
    if total_trades > 0:
        wins = portfolio.get("winning_trades", 0)
        losses = portfolio.get("losing_trades", 0)
        win_rate = (wins / total_trades * 100)
        msg += f"*📊 Today* | Trades: {total_trades} | Wins: {wins} | Losses: {losses} | WR: {win_rate:.0f}%\n"
    
    # Recent actions
    actions = positions.get("actions", [])
    if actions:
        msg += "\n*⚡ Recent*\n"
        for a in actions[-3:]:
            msg += f"• {a}\n"
    
    msg += f"\n_Mode: SHADOW (paper trading)_"
    
    return msg

def send_report():
    """Generate and return the message (caller sends via Telegram)"""
    msg = build_telegram_message()
    if msg:
        print("📤 Telegram message prepared")
        print(msg)
        return msg
    else:
        print("⚠️ No data for report")
        return None

if __name__ == "__main__":
    try:
        send_report()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
