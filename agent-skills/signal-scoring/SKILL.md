---
id: signal-scoring
slug: signal-scoring
key: ErsterALLES/ErsterALLES-trading-brain/signal-scoring
name: Signal Scoring & Aggregation
version: 1.0.0
category: strategy
tags: [signals, ensemble, scoring, confirmation, weights]
---

# Signal Scoring & Aggregation

Turn raw signals into actionable trade decisions.

## When to use
- Multiple detectors fire simultaneously
- Need confidence score before risk manager
- Strategy validation against historical signals

## Signal Sources
1. Technical Indicators (RSI, MACD, EMA cross, Volume profile)
2. Market Microstructure (orderbook imbalance, trade flow, funding divergence)
3. YouTube Strategy Distillation (pattern rules from video analysis)
4. Polymarket Sentiment (prediction market directional bias)

## Scoring Pipeline

### Step 1: Raw Signal -> Strength (0-1)
Each detector emits direction, strength, symbol, timeframe, metadata.

### Step 2: Source Weighting
weights:
  technical_indicators: 0.30
  market_microstructure: 0.35
  youtube_strategy: 0.20
  polymarket_sentiment: 0.15

### Step 3: Ensemble Score
ensemble_score = sum(source_strength * source_weight)
normalized_score = ensemble_score / sum(abs(weights of active sources))

### Step 4: Confirmation Rules
- Minimum score: 0.60
- Direction agreement: >=60% of active sources must agree
- Timeframe alignment: Signal valid if confirmed on 2+ timeframes
- Anti-churn: Wait 4h between same-direction signals on same symbol

## Output: TradeSignal
Returns JSON with symbol, direction, confidence, sources, entry_zone, stop_loss, take_profit, risk_reward, valid_until.

## Execution Rules
- Score < 0.60: Log only (shadow)
- Score 0.60-0.75: Paper trade with 50% size
- Score > 0.75: Full size (respecting risk governor)
- Expired: Discard if valid_until passed without fill
