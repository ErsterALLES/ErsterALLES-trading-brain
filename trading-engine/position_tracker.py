import json
import os
import time
from datetime import datetime, timezone

# ─── CONFIG ──────────────────────────────────────────────────────
PORTFOLIO_FILE = "/opt/data/projects/trading-brain/data/trades/shadow_portfolio.json"
SIGNALS_FILE = "/opt/data/projects/trading-brain/data/signals/latest_signals.json"
POSITIONS_FILE = "/opt/data/projects/trading-brain/data/positions/live_positions.json"
LOG_FILE = "/opt/data/projects/trading-brain/logs/position_tracker.log"

os.makedirs(os.path.dirname(POSITIONS_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ─── LOGGING ─────────────────────────────────────────────────────
def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

# ─── LOAD / SAVE ────────────────────────────────────────────────
def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ─── POSITION TRACKER ───────────────────────────────────────────
def track_positions():
    """Update all open positions with current market prices and check SL/TP"""
    log("")
    log("📊 Position Tracker started")
    
    portfolio = load_json(PORTFOLIO_FILE, {
        "capital": 231.84,
        "open_positions": [],
        "closed_positions": [],
        "daily_pnl": 0,
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0
    })
    
    signals_data = load_json(SIGNALS_FILE, {"signals": []})
    current_prices = {s["asset"]: s["price"] for s in signals_data.get("signals", [])}
    
    open_positions = portfolio.get("open_positions", [])
    closed_positions = portfolio.get("closed_positions", [])
    actions_taken = []
    
    new_open = []
    for pos in open_positions:
        asset = pos["asset"]
        direction = pos["direction"]
        entry = pos["entry_price"]
        
        if asset not in current_prices:
            log(f"  ⚠️ No price for {asset}, keeping position open")
            new_open.append(pos)
            continue
        
        current_price = current_prices[asset]
        pos["current_price"] = current_price
        
        # Calculate unrealized PnL
        if direction == "LONG":
            unrealized = (current_price - entry) * pos["position_size"]
        else:
            unrealized = (entry - current_price) * pos["position_size"]
        pos["unrealized_pnl"] = round(unrealized, 2)
        
        # Check SL / TP
        sl = pos["stop_loss"]
        tp = pos["take_profit"]
        
        hit_sl = False
        hit_tp = False
        
        if direction == "LONG":
            if current_price <= sl:
                hit_sl = True
            elif current_price >= tp:
                hit_tp = True
        else:  # SHORT
            if current_price >= sl:
                hit_sl = True
            elif current_price <= tp:
                hit_tp = True
        
        if hit_sl:
            # Close at stop loss
            pos["status"] = "closed"
            pos["exit_price"] = round(current_price, 4)
            pos["exit_time"] = datetime.now(timezone.utc).isoformat()
            pos["exit_reason"] = "stop_loss"
            pos["pnl"] = pos["unrealized_pnl"]
            pos["pnl_pct"] = round((pos["pnl"] / pos["position_value"]) * 100, 2)
            
            portfolio["capital"] += pos["pnl"]
            portfolio["daily_pnl"] += pos["pnl"]
            portfolio["total_trades"] += 1
            if pos["pnl"] > 0:
                portfolio["winning_trades"] += 1
            else:
                portfolio["losing_trades"] += 1
            
            closed_positions.append(pos)
            actions_taken.append(f"🚨 {asset} {direction} STOPPED @ ${current_price} | PnL: ${pos['pnl']:.2f}")
            log(f"  🚨 {asset} {direction} hit SL @ ${current_price} | PnL: ${pos['pnl']:.2f}")
            
        elif hit_tp:
            # Close at take profit
            pos["status"] = "closed"
            pos["exit_price"] = round(current_price, 4)
            pos["exit_time"] = datetime.now(timezone.utc).isoformat()
            pos["exit_reason"] = "take_profit"
            pos["pnl"] = pos["unrealized_pnl"]
            pos["pnl_pct"] = round((pos["pnl"] / pos["position_value"]) * 100, 2)
            
            portfolio["capital"] += pos["pnl"]
            portfolio["daily_pnl"] += pos["pnl"]
            portfolio["total_trades"] += 1
            if pos["pnl"] > 0:
                portfolio["winning_trades"] += 1
            else:
                portfolio["losing_trades"] += 1
            
            closed_positions.append(pos)
            actions_taken.append(f"🎯 {asset} {direction} TAKE PROFIT @ ${current_price} | PnL: ${pos['pnl']:.2f}")
            log(f"  🎯 {asset} {direction} hit TP @ ${current_price} | PnL: ${pos['pnl']:.2f}")
            
        else:
            # Still open
            new_open.append(pos)
            log(f"  ✅ {asset} {direction} open @ ${current_price} | Unrealized: ${pos['unrealized_pnl']:.2f}")
    
    portfolio["open_positions"] = new_open
    portfolio["closed_positions"] = closed_positions
    
    # Save updated portfolio
    save_json(PORTFOLIO_FILE, portfolio)
    
    # Save live positions snapshot
    live_snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "open_count": len(new_open),
        "closed_count": len(closed_positions),
        "actions": actions_taken,
        "open_positions": new_open,
        "capital": portfolio["capital"],
        "daily_pnl": portfolio["daily_pnl"],
        "total_trades": portfolio["total_trades"],
        "win_rate": (portfolio["winning_trades"] / portfolio["total_trades"] * 100) if portfolio["total_trades"] > 0 else 0
    }
    save_json(POSITIONS_FILE, live_snapshot)
    
    log(f"")
    log(f"  📊 SUMMARY")
    log(f"     Open positions: {len(new_open)}")
    log(f"     Closed today: {len(actions_taken)}")
    log(f"     Capital: ${portfolio['capital']:.2f}")
    log(f"     Daily PnL: ${portfolio['daily_pnl']:.2f}")
    log(f"     Total trades: {portfolio['total_trades']}")
    win_rate = (portfolio["winning_trades"] / portfolio["total_trades"] * 100) if portfolio["total_trades"] > 0 else 0
    log(f"     Win rate: {win_rate:.1f}%")
    
    if new_open:
        total_unrealized = sum(p.get("unrealized_pnl", 0) for p in new_open)
        log(f"     Unrealized PnL: ${total_unrealized:.2f}")
    
    log(f"  💾 Saved to {POSITIONS_FILE}")
    
    return live_snapshot

if __name__ == "__main__":
    try:
        track_positions()
    except Exception as e:
        log(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
