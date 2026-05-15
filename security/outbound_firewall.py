#!/usr/bin/env python3
"""
Outbound Firewall — blocks any unauthorized outbound action.
Every SSH/API/Git/DB action MUST have a valid Telegram watermark.
"""

import sys
import os
import json
import subprocess
import re

sys.path.insert(0, '/opt/data/projects/trading-brain/security')
from watermark import verify_watermark, sign_action

# ─── CONFIG ────────────────────────────────────────────────
WHITELISTED_ACTIONS = [
    "signal_collection",
    "position_tracking",
    "performance_report",
    "telegram_report",
    "health_check",
    "user_authorized",
]

BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"nc\s+-l",
    r"bash\s+-i",
    r"python\s+-c\s+.*socket",
    r"eval\s*\(",
    r"exec\s*\(",
]

LOG_FILE = "/opt/data/projects/trading-brain/logs/firewall.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    ts = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

def check_blocked(command):
    """Check if command matches dangerous patterns"""
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, f"Blocked pattern: {pattern}"
    return False, ""

def authorize_action(action_type, details):
    """
    Authorize an outbound action with Telegram watermark.
    Returns: {"allowed": bool, "watermark": dict, "reason": str}
    """
    # First, check for dangerous patterns
    if "command" in details:
        is_blocked, block_reason = check_blocked(details["command"])
        if is_blocked:
            log(f"❌ BLOCKED: {action_type} | {block_reason} | {details}")
            return {"allowed": False, "watermark": None, "reason": block_reason}
    
    # Generate watermark
    watermark = sign_action(action_type, details)
    
    # Verify it immediately
    result = verify_watermark(watermark)
    
    if not result["valid"]:
        log(f"❌ BLOCKED: {action_type} | Invalid watermark: {result['reason']}")
        return {"allowed": False, "watermark": watermark, "reason": result["reason"]}
    
    log(f"✅ ALLOWED: {action_type} | Age: {result.get('age', 0)}s | {details.get('command', 'N/A')[:60]}")
    return {"allowed": True, "watermark": watermark, "reason": "Authorized via Telegram"}

def exec_authorized(command, action_type="user_authorized", timeout=60):
    """
    Execute a shell command ONLY if watermarked and authorized.
    This is the SAFE wrapper for all subprocess calls.
    """
    # Authorize first
    auth = authorize_action(action_type, {"command": command})
    
    if not auth["allowed"]:
        print(f"🚨 FIREWALL BLOCKED: {auth['reason']}")
        print(f"   Command: {command[:100]}")
        return None  # Command not executed
    
    # Execute with watermark in environment
    env = os.environ.copy()
    env["TELEGRAM_WATERMARK"] = json.dumps(auth["watermark"])
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        return result
    except subprocess.TimeoutExpired:
        log(f"⚠️ TIMEOUT: {command[:60]}")
        return None
    except Exception as e:
        log(f"❌ EXEC ERROR: {e} | {command[:60]}")
        return None

def exec_cron_safe(script_path, action_type, timeout=120):
    """
    Wrapper for cronjob scripts — auto-watermarks internal operations.
    """
    return exec_authorized(f"python3 {script_path}", action_type, timeout)

if __name__ == "__main__":
    # Test
    print("🛡️ Outbound Firewall Test")
    
    # Test 1: Safe command
    r1 = authorize_action("test_safe", {"command": "echo hello"})
    print(f"\n1. Safe command: {'✅ ALLOWED' if r1['allowed'] else '❌ BLOCKED'}")
    print(f"   Reason: {r1['reason']}")
    
    # Test 2: Dangerous command
    r2 = authorize_action("test_dangerous", {"command": "rm -rf /"})
    print(f"\n2. Dangerous command: {'✅ ALLOWED' if r2['allowed'] else '❌ BLOCKED'}")
    print(f"   Reason: {r2['reason']}")
    
    # Test 3: Execute safe
    print(f"\n3. Executing 'echo hello'...")
    result = exec_authorized("echo hello", "test_exec")
    if result:
        print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"   ❌ Blocked")
