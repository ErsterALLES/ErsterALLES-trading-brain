#!/usr/bin/env python3
import subprocess
import sys
import time

steps = [
    ("Signal Collector + Shadow Executor", "/opt/data/projects/trading-brain/trading-engine/run_collector_once.py"),
    ("Position Tracker", "/opt/data/projects/trading-brain/trading-engine/position_tracker.py"),
    ("Performance Dashboard", "/opt/data/projects/trading-brain/reports/performance_dashboard.py"),
    ("Telegram Reporter", "/opt/data/projects/trading-brain/trading-engine/telegram_reporter.py"),
]

for name, script in steps:
    print(f"\n{'='*50}")
    print(f"STEP: {name}")
    print(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, timeout=120
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR in {name}: {result.stderr}")
    time.sleep(1)

print(f"\n{'='*50}")
print("ALL STEPS COMPLETE")
print(f"{'='*50}")
