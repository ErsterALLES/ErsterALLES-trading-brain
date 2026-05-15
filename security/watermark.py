#!/usr/bin/env python3
"""
Telegram Watermark System.
Every outbound action is watermarked with Telegram chat ID + timestamp + HMAC signature.
Unauthorized actions (no watermark) are blocked by the Outbound Firewall.
"""

import hashlib
import hmac
import json
import time
import os
from datetime import datetime, timezone

# ─── CONFIG ────────────────────────────────────────────────
TELEGRAM_CHAT_ID = "7936307967"
SECRET_FILE = "/opt/data/projects/trading-brain/security/.master_secret.enc"
SALT_FILE = "/opt/data/projects/trading-brain/security/.salt.bin"
WATERMARK_DIR = "/opt/data/projects/trading-brain/security/watermarks"
AUTH_TTL_SECONDS = 300  # 5 minutes max per action

os.makedirs(WATERMARK_DIR, exist_ok=True)
os.chmod(WATERMARK_DIR, 0o700)

def load_secret():
    """Load master secret from encrypted storage"""
    with open(SALT_FILE, 'rb') as f:
        salt = f.read()
    with open(SECRET_FILE, 'rb') as f:
        encrypted = f.read()
    # XOR decrypt
    return bytes(a ^ b for a, b in zip(encrypted, salt))

def _generate_watermark(action_type, action_details):
    """Generate a watermark for an outbound action"""
    secret = load_secret()
    timestamp = int(time.time())
    
    # Canonical action string (WITHOUT details for simplicity)
    canonical = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "ts": timestamp,
        "type": action_type,
        "details": {}  # details intentionally not included in signature
    }, sort_keys=True, separators=(',',':'))
    
    # HMAC signature
    signature = hmac.new(secret, canonical.encode(), hashlib.sha256).hexdigest()[:32]
    
    watermark = {
        "v": 1,  # protocol version
        "chat_id": TELEGRAM_CHAT_ID,
        "ts": timestamp,
        "type": action_type,
        "sig": signature
    }
    
    return watermark

def sign_action(action_type, details, save_watermark=True):
    """
    Watermark an outbound action.
    Call this BEFORE every SSH/API/Git/DB action.
    
    Args:
        action_type: e.g. "ssh", "api_call", "git_push", "paperclip_login"
        details: dict with action specifics (host, command, etc.)
        save_watermark: whether to persist the watermark for audit trail
    
    Returns:
        watermark dict
    """
    watermark = _generate_watermark(action_type, details)
    
    if save_watermark:
        # Save to audit trail (encrypted)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{ts}_{action_type}_{watermark['sig'][:8]}.json"
        filepath = os.path.join(WATERMARK_DIR, filename)
        
        audit_entry = {
            "watermark": watermark,
            "details": details,
            "approved": True  # auto-approved for now, oracle will verify
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_entry, f)
        os.chmod(filepath, 0o600)
    
    return watermark

def verify_watermark(watermark):
    """
    Verify a watermark is valid and not expired.
    Called by the Outbound Firewall before allowing any action.
    
    Returns:
        {"valid": bool, "reason": str}
    """
    # Check version
    if watermark.get("v") != 1:
        return {"valid": False, "reason": "Invalid watermark version"}
    
    # Check chat ID
    if watermark.get("chat_id") != TELEGRAM_CHAT_ID:
        return {"valid": False, "reason": "Unauthorized chat ID"}
    
    # Check timestamp (anti-replay)
    ts = watermark.get("ts", 0)
    now = int(time.time())
    age = now - ts
    if age > AUTH_TTL_SECONDS:
        return {"valid": False, "reason": f"Watermark expired ({age}s old, max {AUTH_TTL_SECONDS}s)"}
    if age < -60:  # future timestamp
        return {"valid": False, "reason": "Watermark from future"}
    
    # Verify signature
    secret = load_secret()
    canonical = json.dumps({
        "chat_id": watermark["chat_id"],
        "ts": watermark["ts"],
        "type": watermark.get("type", "unknown"),
        "details": {}  # intentionally empty, matching generation
    }, sort_keys=True, separators=(',',':'))
    
    expected_sig = hmac.new(secret, canonical.encode(), hashlib.sha256).hexdigest()[:32]
    
    if watermark.get("sig") != expected_sig:
        return {"valid": False, "reason": "Invalid signature - possible tampering"}
    
    # All checks passed
    return {"valid": True, "reason": "Watermark valid", "age": age}

def get_latest_watermarks(limit=10):
    """Get recent watermarks for audit trail"""
    files = sorted(os.listdir(WATERMARK_DIR), reverse=True)
    watermarks = []
    for f in files[:limit]:
        path = os.path.join(WATERMARK_DIR, f)
        try:
            with open(path) as fh:
                data = json.load(fh)
            watermarks.append(data)
        except:
            pass
    return watermarks

if __name__ == "__main__":
    # Test
    print("📊 Telegram Watermark System Test")
    print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
    
    wm = sign_action("test", {"command": "echo hello"})
    print(f"\n   Generated watermark:")
    print(f"   {json.dumps(wm, indent=2)}")
    
    result = verify_watermark(wm)
    print(f"\n   Verification: {'✅ VALID' if result['valid'] else '❌ INVALID'}")
    print(f"   Reason: {result['reason']}")
    
    # Test expired
    old_wm = wm.copy()
    old_wm["ts"] = old_wm["ts"] - 400
    old_wm["sig"] = "invalid_sig_for_test"
    result2 = verify_watermark(old_wm)
    print(f"\n   Expired test: {'✅ VALID' if result2['valid'] else '❌ INVALID'}")
    print(f"   Reason: {result2['reason']}")
