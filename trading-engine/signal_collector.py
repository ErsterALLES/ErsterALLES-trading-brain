import urllib.request
import urllib.error
import json
import time
import os
from datetime import datetime, timezone

# ─── CONFIG ──────────────────────────────────────────────────────
HYPERLIQUID_INFO = "https://api.hyperliquid.xyz/info"

ASSETS = ["BTC", "ETH", "SOL", "XRP", "DOGE"]
TIMEFRAME = "1h"
POLL_INTERVAL = 300

RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
EMA_SHORT = 9
EMA_LONG = 21

DATA_DIR = "/opt/data/projects/trading-brain/data/signals"
os.makedirs(DATA_DIR, exist_ok=True)

# ─── HELPERS ───────────────────────────────────────────────────
def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_ema(closes, period):
    if len(closes) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = sum(closes[:period]) / period
    for price in closes[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calc_atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        trs.append(tr)
    return sum(trs[-period:]) / period

def post_json(url, payload):
    """Synchronous POST with urllib"""
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

# ─── API CALLS ──────────────────────────────────────────────────
def fetch_candles(asset, timeframe=TIMEFRAME, limit=100):
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": asset,
            "interval": timeframe,
            "startTime": int(time.time() * 1000) - (limit * 3600 * 1000),
            "endTime": int(time.time() * 1000)
        }
    }
    return post_json(HYPERLIQUID_INFO, payload)

def fetch_orderbook(asset):
    return post_json(HYPERLIQUID_INFO, {"type": "l2Book", "coin": asset})

def fetch_market_info():
    return post_json(HYPERLIQUID_INFO, {"type": "metaAndAssetCtxs"})

# ─── SIGNAL GENERATION ──────────────────────────────────────────
def generate_signal(asset, candles, orderbook, market_ctx):
    if not candles or len(candles) < EMA_LONG + 5:
        return None
    
    # Hyperliquid candle format: dict with keys o,h,l,c,v
    if isinstance(candles[0], dict):
        closes = [float(c['c']) for c in candles]
        highs = [float(c['h']) for c in candles]
        lows = [float(c['l']) for c in candles]
        volumes = [float(c['v']) for c in candles]
    else:
        closes = [float(c[4]) for c in candles]
        highs = [float(c[2]) for c in candles]
        lows = [float(c[3]) for c in candles]
        volumes = [float(c[5]) for c in candles]
    current_price = closes[-1]
    
    rsi = calc_rsi(closes)
    ema_short = calc_ema(closes, EMA_SHORT)
    ema_long = calc_ema(closes, EMA_LONG)
    atr = calc_atr(highs, lows, closes)
    
    if rsi is None or ema_short is None or ema_long is None or atr is None:
        return None
    
    bid_ask_spread = None
    bid_ask_spread_pct = None
    order_imbalance = None
    
    if orderbook and 'levels' in orderbook:
        bids = orderbook['levels'][0]
        asks = orderbook['levels'][1]
        if bids and asks:
            if isinstance(bids[0], dict):
                best_bid = float(bids[0]['px'])
                best_ask = float(asks[0]['px'])
                bid_vol = sum(float(b['sz']) for b in bids[:5])
                ask_vol = sum(float(a['sz']) for a in asks[:5])
            else:
                best_bid = float(bids[0][0])
                best_ask = float(asks[0][0])
                bid_vol = sum(float(b[1]) for b in bids[:5])
                ask_vol = sum(float(a[1]) for a in asks[:5])
            bid_ask_spread = best_ask - best_bid
            bid_ask_spread_pct = (bid_ask_spread / current_price) * 100
            order_imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol) if (bid_vol + ask_vol) > 0 else 0
    avg_volume = sum(volumes[-10:]) / 10
    volume_surge = volumes[-1] > avg_volume * 1.5 if avg_volume > 0 else False
    
    signal_type = None
    signal_strength = 0
    reasons = []
    
    # EMA Cross detection
    prev_ema_short = calc_ema(closes[:-1], EMA_SHORT)
    prev_ema_long = calc_ema(closes[:-1], EMA_LONG)
    
    if ema_short > ema_long and prev_ema_short and prev_ema_long:
        if prev_ema_short <= prev_ema_long:
            signal_type = "LONG"
            signal_strength += 35
            reasons.append(f"EMA{EMA_SHORT} crossed above EMA{EMA_LONG}")
    elif ema_short < ema_long and prev_ema_short and prev_ema_long:
        if prev_ema_short >= prev_ema_long:
            signal_type = "SHORT"
            signal_strength += 35
            reasons.append(f"EMA{EMA_SHORT} crossed below EMA{EMA_LONG}")
    
    # RSI confirmation
    if signal_type == "LONG" and rsi < 45:
        signal_strength += 20
        reasons.append(f"RSI {rsi:.1f} supports long")
    elif signal_type == "SHORT" and rsi > 55:
        signal_strength += 20
        reasons.append(f"RSI {rsi:.1f} supports short")
    
    # Orderbook confirmation
    if order_imbalance is not None:
        if signal_type == "LONG" and order_imbalance > 0.15:
            signal_strength += 15
            reasons.append(f"Bid imbalance {order_imbalance:.1%}")
        elif signal_type == "SHORT" and order_imbalance < -0.15:
            signal_strength += 15
            reasons.append(f"Ask imbalance {abs(order_imbalance):.1%}")
    
    if volume_surge:
        signal_strength += 10
        reasons.append("Volume surge")
    
    if signal_type and signal_strength < 30:
        signal_type = None
        signal_strength = 0
        reasons = []
    
    # Market context (funding rate + liquidation risk proxy)
    funding = None
    funding_annualized = None
    open_interest = None
    liquidation_risk = "neutral"
    
    if market_ctx and len(market_ctx) >= 2:
        assets = market_ctx[0].get('universe', [])
        ctxs = market_ctx[1]
        for i, a in enumerate(assets):
            if a.get('name') == asset:
                if i < len(ctxs):
                    funding = float(ctxs[i].get('funding', 0))
                    open_interest = float(ctxs[i].get('openInterest', 0))
                    # Annualized funding rate (hourly * 24 * 365)
                    funding_annualized = funding * 24 * 365 if funding else 0
                    # Liquidation risk proxy: extreme funding = crowded trade
                    if funding_annualized > 0.30:  # >30% annualized = extreme longs
                        liquidation_risk = "longs_vulnerable"
                    elif funding_annualized < -0.30:  # < -30% = extreme shorts
                        liquidation_risk = "shorts_vulnerable"
                    elif abs(funding_annualized) > 0.15:
                        liquidation_risk = "elevated"
                break
    
    # Heatmap liquidation zone estimation (based on funding + price + ATR)
    liquidation_zones = {}
    if atr and current_price:
        # If funding is very positive (longs pay shorts), long liquidation clusters below
        if funding_annualized and funding_annualized > 0.20:
            liquidation_zones["long_liquidation_cluster"] = round(current_price - (atr * 3), 2)
        # If funding is very negative (shorts pay longs), short liquidation clusters above
        elif funding_annualized and funding_annualized < -0.20:
            liquidation_zones["short_liquidation_cluster"] = round(current_price + (atr * 3), 2)
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "asset": asset,
        "signal_type": signal_type,
        "signal_strength": signal_strength,
        "reasons": reasons,
        "price": current_price,
        "indicators": {
            "rsi": round(rsi, 2),
            "ema_short": round(ema_short, 2),
            "ema_long": round(ema_long, 2),
            "atr": round(atr, 4),
            "ema_trend": "BULLISH" if ema_short > ema_long else "BEARISH"
        },
        "orderbook": {
            "spread": round(bid_ask_spread, 4) if bid_ask_spread else None,
            "spread_pct": round(bid_ask_spread_pct, 4) if bid_ask_spread_pct else None,
            "imbalance": round(order_imbalance, 4) if order_imbalance is not None else None
        },
        "volume": {
            "current": round(volumes[-1], 2),
            "avg_10": round(avg_volume, 2),
            "surge": volume_surge
        },
        "market_context": {
            "funding_1h": round(funding, 6) if funding else None,
            "funding_annualized_pct": round(funding_annualized * 100, 2) if funding_annualized else None,
            "open_interest": round(open_interest, 2) if open_interest else None,
            "liquidation_risk": liquidation_risk,
            "liquidation_zones": liquidation_zones
        },
        "confidence": min(signal_strength, 100) if signal_type else 0
    }

# ─── MAIN ───────────────────────────────────────────────────────
def run_once():
    """Single collection cycle"""
    timestamp = datetime.now(timezone.utc)
    print(f"\n⏰ {timestamp.strftime('%H:%M:%S UTC')} — Signal collection started")
    
    market_ctx = fetch_market_info()
    all_signals = []
    
    for asset in ASSETS:
        print(f"  📊 {asset}...", end=" ", flush=True)
        
        candles = fetch_candles(asset)
        orderbook = fetch_orderbook(asset)
        
        signal = generate_signal(asset, candles, orderbook, market_ctx)
        
        if signal:
            all_signals.append(signal)
            if signal['signal_type']:
                emoji = "📈" if signal['signal_type'] == "LONG" else "📉"
                print(f"{emoji} {signal['signal_type']} (strength {signal['signal_strength']}, conf {signal['confidence']}%)")
                print(f"     → {', '.join(signal['reasons'])}")
            else:
                print(f"⚪ No signal (RSI {signal['indicators']['rsi']}, trend {signal['indicators']['ema_trend']})")
        else:
            print(f"⚠️ No data")
        
        time.sleep(0.2)
    
    # Save
    if all_signals:
        filename = f"{DATA_DIR}/signals_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({"timestamp": timestamp.isoformat(), "signals": all_signals}, f, indent=2)
        
        with open(f"{DATA_DIR}/latest_signals.json", 'w') as f:
            json.dump({"timestamp": timestamp.isoformat(), "signals": all_signals}, f, indent=2)
        
        print(f"  💾 Saved to {filename}")
    
    active = [s for s in all_signals if s['signal_type']]
    if active:
        print(f"\n  🎯 ACTIVE: {len(active)} signals")
        for s in active:
            dir_emoji = "📈" if s['signal_type'] == "LONG" else "📉"
            print(f"     {dir_emoji} {s['asset']} @ ${s['price']} (conf: {s['confidence']}%)")
    else:
        print(f"\n  ⚪ No actionable signals")
    
    return all_signals

def main_loop():
    print(f"\n🚀 Hyperliquid Signal Collector")
    print(f"   Assets: {', '.join(ASSETS)}")
    print(f"   Interval: {POLL_INTERVAL}s ({POLL_INTERVAL//60}min)")
    print(f"   Output: {DATA_DIR}")
    print(f"   Mode: SHADOW (no live trading)")
    print(f"   Press Ctrl+C to stop\n")
    
    while True:
        cycle_start = time.time()
        try:
            run_once()
        except Exception as e:
            print(f"  ❌ Cycle error: {e}")
        
        elapsed = time.time() - cycle_start
        sleep_time = max(0, POLL_INTERVAL - elapsed)
        if sleep_time > 0:
            print(f"  💤 Sleep {sleep_time:.0f}s...")
            time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\n✅ Stopped")
    except Exception as e:
        print(f"\n\n❌ Fatal: {e}")
        import traceback
        traceback.print_exc()
