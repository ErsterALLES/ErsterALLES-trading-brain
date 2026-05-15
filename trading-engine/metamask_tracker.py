#!/usr/bin/env python3
"""
MetaMask Multi-Asset Balance Tracker.
Tracks USDC, ETH, SOL, BTC balances via DeBank API (no API key needed for basic balances).
"""

import urllib.request
import json
import os
from datetime import datetime, timezone

# ─── CONFIG ────────────────────────────────────────────────
DATA_DIR = "/opt/data/projects/trading-brain/data/wallet"
os.makedirs(DATA_DIR, exist_ok=True)

BALANCE_FILE = f"{DATA_DIR}/metamask_balances.json"
HISTORY_FILE = f"{DATA_DIR}/metamask_history.json"

# MetaMask Wallet Address (from screenshot: 0x5491K...v2gth)
WALLET_ADDRESS = "0x5491...v2gth"  # Truncated for privacy — user update needed

def fetch_debank_balance(address):
    """Fetch multi-asset balances from DeBank API (free, no key)"""
    if "..." in address:
        return None, "Wallet address incomplete (truncated in screenshot)"
    
    url = f"https://api.debank.com/user/total_balance?id={address}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0"
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return data, None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)

def fetch_chain_balances(address):
    """Fetch per-chain balances"""
    if "..." in address:
        return None, "Wallet address incomplete"
    
    url = f"https://api.debank.com/user/chain_list?id={address}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return data, None
    except Exception as e:
        return None, str(e)

def format_balance(data):
    """Format balance data nicely"""
    if not data or not isinstance(data, dict):
        return "No data"
    
    total_usd = data.get("data", {}).get("total_usd_value", 0)
    chains = data.get("data", {}).get("chain_list", [])
    
    lines = [f"💰 MetaMask Portfolio"]
    lines.append(f"   Total: ${total_usd:,.2f}")
    lines.append("")
    
    if chains:
        lines.append("   Per Chain:")
        for chain in chains[:5]:
            name = chain.get("name", "Unknown")
            balance = chain.get("usd_value", 0)
            lines.append(f"      {name}: ${balance:,.2f}")
    
    return "\n".join(lines)

def update_balance_history(balance_data):
    """Save balance snapshot to history"""
    if not os.path.exists(HISTORY_FILE):
        history = []
    else:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    
    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "balance": balance_data
    })
    
    # Keep last 1000 entries
    history = history[-1000:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def run_balance_check():
    print("💰 MetaMask Balance Tracker")
    print(f"   Wallet: {WALLET_ADDRESS[:10]}...{WALLET_ADDRESS[-6:]}")
    print("   Source: DeBank API (free)")
    print("")
    
    # Try with truncated address first (will fail, user needs full address)
    result, error = fetch_debank_balance(WALLET_ADDRESS)
    
    if error:
        print(f"   ⚠️ {error}")
        print("   Need full wallet address to track all assets.")
        print("   Current screenshot shows truncated: 0x5491K...v2gth")
        print("")
        print("   💡 USDC typically lives on:")
        print("      - Ethereum mainnet (ERC-20)")
        print("      - Polygon ( bridged)")
        print("      - Arbitrum / Optimism")
        print("")
        print("   Please share full wallet address if you want tracking.")
        return
    
    print(format_balance(result))
    update_balance_history(result)
    
    with open(BALANCE_FILE, 'w') as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run_balance_check()
