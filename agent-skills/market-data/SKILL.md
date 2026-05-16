---
name: market-data
description: "Real-time market data collection for crypto assets via Hyperliquid API"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [trading, market-data, hyperliquid, crypto]
    model: opencode/deepseek-v4-flash-free
---

# Market Data Collector

## Purpose
Fetches OHLCV candles, funding rates, open interest, and order book data from Hyperliquid for signal generation.

## API Endpoint
```
POST https://api.hyperliquid.xyz/info
Content-Type: application/json
```

## Methods

### Get Candles
```json
{"type": "candleSnapshot", "req": {"coin": "BTC", "startTime": 1700000000000, "endTime": 1700003600000, "interval": "5m"}}
```

### Get All Mids
```json
{"type": "allMids"}
```

### Get Meta
```json
{"type": "meta"}
```

## Usage
```bash
python3 -c "
import requests, json
url = 'https://api.hyperliquid.xyz/info'
res = requests.post(url, json={'type': 'candleSnapshot', 'req': {'coin': 'BTC', 'interval': '5m', 'startTime': 0, 'endTime': 9999999999999}})
print(json.dumps(res.json()[-5:], indent=2))
"
```

## Output Format
```json
[
  {"T": 1700000000000, "c": "42000.5", "h": "42100.0", "l": "41950.0", "o": "42050.0", "v": "15.3"},
  ...
]
```

## Performance Notes
- No API key required for public data
- Rate limit: ~20 req/sec
- Cache results for 30s to avoid unnecessary calls
