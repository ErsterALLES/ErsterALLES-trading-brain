#!/usr/bin/env python3
"""
Generate master secret for Telegram Watermark Gateway.
Secret = HMAC-SHA256(Telegram Chat ID + Salt, Host Fingerprint)
Stored encrypted at rest.
"""

import os
import hashlib
import hmac
import json
import base64
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────
TELEGRAM_CHAT_ID = "7936307967"
SALT_FILE = "/opt/data/projects/trading-brain/security/.salt.bin"
SECRET_FILE = "/opt/data/projects/trading-brain/security/.master_secret.enc"
PUBKEY_FILE = "/opt/data/projects/trading-brain/security/public_key.pem"

# ─── SALT GENERATION ───────────────────────────────────────
def generate_salt():
    """Generate 256-bit random salt"""
    salt = os.urandom(32)
    with open(SALT_FILE, 'wb') as f:
        f.write(salt)
    os.chmod(SALT_FILE, 0o600)
    return salt

def load_salt():
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, 'rb') as f:
            return f.read()
    return generate_salt()

# ─── HOST FINGERPRINT ──────────────────────────────────────
def get_host_fingerprint():
    """Unique host identifier (persistent across reboots)"""
    # Try machine-id first
    if os.path.exists("/etc/machine-id"):
        with open("/etc/machine-id") as f:
            return f.read().strip()
    # Fallback to hostname + CPU info hash
    hostname = os.uname().nodename
    try:
        with open("/proc/cpuinfo") as f:
            cpu_info = f.read()
        cpu_hash = hashlib.sha256(cpu_info.encode()).hexdigest()[:16]
    except:
        cpu_hash = "unknown"
    return hashlib.sha256(f"{hostname}:{cpu_hash}".encode()).hexdigest()[:32]

# ─── MASTER SECRET ─────────────────────────────────────────
def generate_master_secret():
    """Generate secret from Telegram Chat ID + Salt + Host Fingerprint"""
    salt = load_salt()
    host_fp = get_host_fingerprint()
    
    # Secret = HMAC(Telegram Chat ID, Salt || Host Fingerprint)
    message = f"{TELEGRAM_CHAT_ID}:{host_fp}".encode()
    secret = hmac.new(salt, message, hashlib.sha256).digest()
    
    # Store encrypted at rest (simple XOR with salt for now - production uses proper crypto)
    # In production: Use libsodium or Fernet
    encrypted = bytes(a ^ b for a, b in zip(secret, salt))
    
    with open(SECRET_FILE, 'wb') as f:
        f.write(encrypted)
    os.chmod(SECRET_FILE, 0o600)
    
    # Generate public key for verification (no secret leakage)
    pubkey = hashlib.sha256(secret).hexdigest()[:64]
    with open(PUBKEY_FILE, 'w') as f:
        f.write(f"-----BEGIN TELEGRAM GATEWAY PUBLIC KEY-----\n")
        f.write(pubkey)
        f.write(f"\n-----END TELEGRAM GATEWAY PUBLIC KEY-----\n")
    
    print("🔐 Master Secret generated")
    print(f"   Salt: {salt.hex()[:16]}...{salt.hex()[-16:]}")
    print(f"   Host Fingerprint: {host_fp[:16]}...")
    print(f"   Public Verification Key: {pubkey[:16]}...")
    print(f"   Stored in: {SECRET_FILE}")
    return secret

def load_master_secret():
    """Load secret from encrypted storage"""
    if not os.path.exists(SECRET_FILE):
        print("⚠️ No secret found. Generating new one...")
        return generate_master_secret()
    
    salt = load_salt()
    with open(SECRET_FILE, 'rb') as f:
        encrypted = f.read()
    
    # Decrypt (XOR with salt)
    secret = bytes(a ^ b for a, b in zip(encrypted, salt))
    return secret

if __name__ == "__main__":
    if os.path.exists(SECRET_FILE):
        print("🔐 Master Secret already exists. Regenerating...")
    generate_master_secret()
    print("\n✅ Done. Run this again only if server is compromised.")
