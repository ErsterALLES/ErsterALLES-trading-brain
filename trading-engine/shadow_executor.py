import json
import os
import time
from datetime import datetime, timezone

# ─── CONFIG ──────────────────────────────────────────────────────
DATA_DIR = "/opt/data/projects/trading-brain/data"
SIGNALS_FILE = f"{DATA_DIR}/signals/latest_signals.json"
TRADES_FILE = f"{DATA_DIR}/trades/shadow_trades.json"
PORTFOLIO_FILE = f"{DATA_DIR}/trades/shadow_portfolio.json"

# Risk Governor Parameters (from trading-foundation skill)
MAX_RISK_PER_TRADE = 0.02      # 2% of capital
MAX_DAILY_LOSS = 0.05          # 5% daily loss limit
INITIAL_CAPITAL = 231.84       # USDC
MIN_CONFIDENCE = 45            # Minimum signal confidence to act

# Position sizing
LEVERAGE = 1.0                   # No leverage in shadow mode
SL_ATR_MULTIPLIER = 2.0        # Stop loss = 2x ATR
TP_ATR_MULTIPLIER = 3.0        # Take profit = 3x ATR (1.5:1 R/R)

os.makedirs(f"{DATA_DIR}/trades", exist_ok=True)

# ─── PORTFOLIO STATE ─────────────────────────────────────────
def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE) as f:
            return json.load(f)
    return {
        "capital": INITIAL_CAPITAL,
        "daily_pnl": 0,
        "daily_trades": 0,
        "last_trade_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "open_positions": [],
        "closed_positions": [],
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0
    }

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)

def reset_daily_if_needed(portfolio):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if portfolio["last_trade_date"] != today:
        portfolio["daily_pnl"] = 0
        portfolio["daily_trades"] = 0
        portfolio["last_trade_date"] = today
        print(f"  🔄 Daily stats reset for {today}")
    return portfolio

# ─── SIGNAL EVALUATION ─────────────────────────────────────────
def evaluate_signal(signal, portfolio):
    """Evaluate if a signal should become a trade"""
    asset = signal["asset"]
    confidence = signal.get("confidence", 0)
    signal_type = signal.get("signal_type")
    
    # Must have signal
    if not signal_type:
        return None, "No signal direction"
    
    # Confidence check
    if confidence < MIN_CONFIDENCE:
        return None, f"Confidence {confidence}% < minimum {MIN_CONFIDENCE}%"
    
    # Daily loss limit check
    if portfolio["daily_pnl"] <= -INITIAL_CAPITAL * MAX_DAILY_LOSS:
        return None, f"Daily loss limit reached: ${portfolio['daily_pnl']:.2f}"
    
    # Max trades per day check (avoid overtrading)
    if portfolio["daily_trades"] >= 10:
        return None, f"Max daily trades reached: {portfolio['daily_trades']}"
    
    # No duplicate positions (same asset, same direction)
    for pos in portfolio["open_positions"]:
        if pos["asset"] == asset and pos["direction"] == signal_type:
            return None, f"Already have {signal_type} position in {asset}"
    
    # Calculate position size based on risk
    price = signal["price"]
    atr = signal["indicators"].get("atr", price * 0.01)  # Default 1% if no ATR
    
    stop_loss = price + (atr * SL_ATR_MULTIPLIER) if signal_type == "SHORT" else price - (atr * SL_ATR_MULTIPLIER)
    take_profit = price - (atr * TP_ATR_MULTIPLIER) if signal_type == "SHORT" else price + (atr * TP_ATR_MULTIPLIER)
    
    risk_per_unit = abs(price - stop_loss)
    if risk_per_unit == 0:
        return None, "Invalid stop loss (zero risk distance)"
    
    # Position size: risk 2% of capital / risk per unit
    risk_amount = portfolio["capital"] * MAX_RISK_PER_TRADE
    position_size = risk_amount / risk_per_unit
    position_value = position_size * price
    
    # Don't risk more than 20% of capital on one position
    if position_value > portfolio["capital"] * 0.20:
        position_size = (portfolio["capital"] * 0.20) / price
        position_value = portfolio["capital"] * 0.20
        risk_amount = position_size * risk_per_unit
    
    # Minimum position value ($5)
    if position_value < 5:
        return None, f"Position value ${position_value:.2f} < minimum $5"
    
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "asset": asset,
        "direction": signal_type,
        "entry_price": round(price, 4),
        "stop_loss": round(stop_loss, 4),
        "take_profit": round(take_profit, 4),
        "position_size": round(position_size, 6),
        "position_value": round(position_value, 2),
        "risk_amount": round(risk_amount, 2),
        "risk_pct": round((risk_amount / portfolio["capital"]) * 100, 2),
        "confidence": confidence,
        "signal_reasons": signal.get("reasons", []),
        "indicators": signal.get("indicators", {}),
        "orderbook": signal.get("orderbook", {}),
        "status": "open",
        "unrealized_pnl": 0,
        "exit_price": None,
        "exit_time": None,
        "pnl": None,
        "pnl_pct": None,
        "mode": "shadow"
    }
    
    return trade, None

# ─── POSITION MANAGEMENT ─────────────────────────────────────────────
def update_positions(portfolio, current_prices):
    """Update open positions with current market prices"""
    for pos in portfolio["open_positions"]:
        asset = pos["asset"]
        if asset in current_prices:
            current_price = current_prices[asset]
            direction = pos["direction"]
            entry = pos["entry_price"]
            
            # Calculate unrealized PnL
            if direction == "LONG":
                pnl = (current_price - entry) * pos["position_size"]
            else:
                pnl = (entry - current_price) * pos["position_size"]
            
            pos["unrealized_pnl"] = round(pnl, 2)
            pos["current_price"] = current_price
            
            # Check stop loss / take profit
            if direction == "LONG":
                if current_price <= pos["stop_loss"]:
                    portfolio = close_position(portfolio, pos, current_price, "stop_loss")
                    print(f"     🚨 {asset} LONG stopped out @ ${current_price}")
                elif current_price >= pos["take_profit"]:
                    portfolio = close_position(portfolio, pos, current_price, "take_profit")
                    print(f"     🎯 {asset} LONG take profit @ ${current_price}")
            else:  # SHORT
                if current_price >= pos["stop_loss"]:
                    portfolio = close_position(portfolio, pos, current_price, "stop_loss")
                    print(f"     🚨 {asset} SHORT stopped out @ ${current_price}")
                elif current_price <= pos["take_profit"]:
                    portfolio = close_position(portfolio, pos, current_price, "take_profit")
                    print(f"     🎯 {asset} SHORT take profit @ ${current_price}")
    
    return portfolio

def close_position(portfolio, position, exit_price, reason):
    """Close a position and update portfolio"""
    position["status"] = "closed"
    position["exit_price"] = round(exit_price, 4)
    position["exit_time"] = datetime.now(timezone.utc).isoformat()
    position["exit_reason"] = reason
    
    direction = position["direction"]
    entry = position["entry_price"]
    size = position["position_size"]
    
    if direction == "LONG":
        pnl = (exit_price - entry) * size
    else:
        pnl = (entry - exit_price) * size
    
    position["pnl"] = round(pnl, 2)
    position["pnl_pct"] = round((pnl / position["position_value"]) * 100, 2)
    
    # Update portfolio
    portfolio["capital"] += pnl
    portfolio["daily_pnl"] += pnl
    portfolio["total_trades"] += 1
    portfolio["daily_trades"] += 1
    
    if pnl > 0:
        portfolio["winning_trades"] += 1
    else:
        portfolio["losing_trades"] += 1
    
    # Move from open to closed
    portfolio["open_positions"] = [p for p in portfolio["open_positions"] if p["timestamp"] != position["timestamp"]]
    portfolio["closed_positions"].append(position)
    
    return portfolio

# ─── MAIN EXECUTION ───────────────────────────────────────────────────
def execute_shadow_cycle():
    """Main shadow trading cycle"""
    print(f"\n🤖 Shadow Trade Executor | {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
    print(f"   Mode: SHADOW (no real money) | Capital: ${INITIAL_CAPITAL}")
    
    # Load state
    portfolio = load_portfolio()
    portfolio = reset_daily_if_needed(portfolio)
    
    # Load latest signals
    if not os.path.exists(SIGNALS_FILE):
        print(f"   ⚠️ No signals file found")
        save_portfolio(portfolio)
        return portfolio
    
    with open(SIGNALS_FILE) as f:
        signal_data = json.load(f)
    
    signals = signal_data.get("signals", [])
    
    print(f"   Signals received: {len(signals)}")
    print(f"   Open positions: {len(portfolio['open_positions'])}")
    print(f"   Daily P&L: ${portfolio['daily_pnl']:.2f}")
    print(f"   Current capital: ${portfolio['capital']:.2f}")
    
    # Extract current prices for position management
    current_prices = {}
    for s in signals:
        current_prices[s["asset"]] = s["price"]
    
    # Update existing positions first (check SL/TP)
    portfolio = update_positions(portfolio, current_prices)
    
    # Evaluate new signals
    new_trades = 0
    for signal in signals:
        trade, reject_reason = evaluate_signal(signal, portfolio)
        if trade:
            portfolio["open_positions"].append(trade)
            portfolio["daily_trades"] += 1
            new_trades += 1
            print(f"\n   💵 NEW SHADOW TRADE")
            print(f"      Asset: {trade['asset']} {trade['direction']}")
            print(f"      Entry: ${trade['entry_price']} | SL: ${trade['stop_loss']} | TP: ${trade['take_profit']}")
            print(f"      Size: {trade['position_size']} ({trade['position_value']}$)")
            print(f"      Risk: {trade['risk_amount']}$ ({trade['risk_pct']}% of capital)")
            print(f"      Confidence: {trade['confidence']}%")
        else:
            if signal.get("signal_type"):
                print(f"   ❌ {signal['asset']} {signal['signal_type']} rejected: {reject_reason}")
    
    # Summary
    print(f"\n   📊 SUMMARY")
    print(f"      New trades: {new_trades}")
    print(f"      Open positions: {len(portfolio['open_positions'])}")
    print(f"      Daily trades: {portfolio['daily_trades']}")
    print(f"      Daily P&L: ${portfolio['daily_pnl']:.2f}")
    print(f"      Capital: ${portfolio['capital']:.2f}")
    
    if portfolio["open_positions"]:
        unrealized = sum(p.get("unrealized_pnl", 0) for p in portfolio["open_positions"])
        print(f"      Unrealized P&L: ${unrealized:.2f}")
    
    win_rate = (portfolio["winning_trades"] / portfolio["total_trades"] * 100) if portfolio["total_trades"] > 0 else 0
    print(f"      Total trades: {portfolio['total_trades']} | Win rate: {win_rate:.1f}%")
    
    # Save
    save_portfolio(portfolio)
    
    # Also save all trades log
    all_trades = portfolio["open_positions"] + portfolio["closed_positions"]
    with open(TRADES_FILE, 'w') as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "capital": portfolio["capital"],
            "trades": all_trades
        }, f, indent=2)
    
    print(f"   💾 Saved to {TRADES_FILE}")
    
    return portfolio

if __name__ == "__main__":
    try:
        execute_shadow_cycle()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
