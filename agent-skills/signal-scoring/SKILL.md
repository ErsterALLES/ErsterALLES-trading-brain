---
name: signal-scoring
description: "Multi-strategy signal scoring engine for Hyperliquid futures"
version: 1.1.0
author: Hermes Agent
metadata:
  hermes:
    tags: [trading, signals, scoring, hyperliquid, vwap, mean-reversion]
    model: opencode/deepseek-v4-flash-free
---

# Signal Scoring Engine

## Purpose
Aggregates signals from multiple strategies and assigns confidence scores.

## Supported Strategies

### 1. Valentino Scalper (Momentum)
- **Timeframe**: 5m
- **Trigger**: Funding rate divergence + price momentum
- **Confidence**: 75-90
- **Best for**: Trending markets

### 2. VWAP Scalper (Breakthrough + Mean-Reversion)
- **Timeframe**: 5m
- **Trigger**: VWAP breakthrough OR >1.5% distance from VWAP
- **Confidence**: 65-85
- **Best for**: Trending + ranging markets

### 3. Mean-Reversion Scaler
- **Timeframe**: 15m
- **Trigger**: Bollinger Band touch + RSI divergence
- **Confidence**: 60-80
- **Best for**: Ranging markets

## Scoring Formula
```
final_score = (signal_strength * 0.4) + (trend_alignment * 0.3) + (volume_confirmation * 0.3)
confidence = min(95, max(45, final_score * 100))
```

## Usage
```python
from hyperliquid_valentino_scorer import generate_signals
from vwap_scalper_hyperliquid import run_vwap_scalper

# Get all signals
valentino = generate_signals()
vwap = run_vwap_scalper()

# Aggregate
all_signals = valentino + vwap
best = sorted(all_signals, key=lambda x: x["confidence"], reverse=True)[:5]
```

## Rules
- Only trade signals with confidence >= 55
- Max 3 parallel positions per strategy
- Diversify across at least 5 assets
