---
id: market-data-collector
slug: market-data
key: ErsterALLES/ErsterALLES-trading-brain/market-data
name: Market Data Collector
version: 1.0.0
category: data
tags: [hyperliquid, polymarket, polygon, ohlcv, orderbook, api]
---

# Market Data Collector

Fetch and normalize market data from multiple sources.

## When to use
- Signal generation needs fresh data
- Backtesting needs historical data
- Portfolio tracking needs price updates
- Strategy validation needs market context

## Sources & Endpoints

### Primary: Hyperliquid (Perps)
```python
BASE = "https://api.hyperliquid.xyz"
POST /info {"type": "meta"}  # All perps metadata
POST /info {"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "5m", "startTime": 1234567890000, "endTime": 1234567990000}}
POST /info {"type": "l2Book", "coin": "BTC"}  # Orderbook L2
POST /info {"type": "recentTrades", "coin": "BTC"}
POST /info {"type": "fundingHistory", "coin": "BTC", "startTime": 1234567890000}
```

### Secondary: Polymarket (Signals)
```python
BASE = "https://gamma-api.polymarket.com"
GET /markets?active=true&closed=false&limit=100
GET /markets/{id}/orderbook
GET /markets/{id}/trades
GET /markets/{id}/prices
```

### Backup: Polygon.io
```python
GET /v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}?apiKey={KEY}
```

## Normalization
All sources return unified `MarketData` object with ohlcv, orderbook, funding_rate, open_interest.

## Rate Limits
- Hyperliquid: ~100 req/s
- Polymarket: ~10 req/s
- Polygon: 5 req/s (free tier)

**Rule**: Always backoff on 429. Cache aggressively.
