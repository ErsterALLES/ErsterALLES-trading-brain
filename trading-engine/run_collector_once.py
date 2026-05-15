#!/usr/bin/env python3
import sys, os
sys.path.insert(0, '/opt/data/projects/trading-brain/trading-engine')
from signal_collector import run_once
try:
    run_once()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
