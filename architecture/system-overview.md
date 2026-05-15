# Trading Brain System Overview

## Ziel

Ein modularer Trading-Intelligence-Stack mit Paperclip als zentraler Datenbank, Wissensgraph, Strategiearchiv und Agenten-Orchestrator.

## Hochlevel-Architektur

```text
Data Sources
  ├─ Market APIs: Polymarket, Hyperliquid, MT5, CEX/DEX, On-chain
  ├─ News/Event APIs: RSS, News, X/Twitter, Reddit, Earnings, Macro Calendars
  ├─ Video Sources: YouTube, local video files, courses, screen recordings
  └─ Alternative Data: weather, shipping, sports injuries, social sentiment
        ↓
Collectors / Ingestion Agents
        ↓
Paperclip Trading Brain
  ├─ signals
  ├─ sources
  ├─ events
  ├─ strategy_components
  ├─ strategies
  ├─ trade_ideas
  ├─ positions
  ├─ trade_outcomes
  └─ evidence graph
        ↓
Analysis + Strategy Engine
  ├─ signal scoring
  ├─ correlation engine
  ├─ strategy fusion
  ├─ thesis engine
  └─ backtest/shadow simulator
        ↓
Risk Manager / Portfolio Governor
        ↓
Execution Services
  ├─ Hyperliquid Executor
  ├─ Polymarket Executor/Monitor, subject to legal feasibility
  ├─ MT5 Bridge / MetaTrader Executor
  └─ Future connectors
        ↓
Trade Results zurück nach Paperclip
```

## Paperclip-Rolle

Paperclip ist:

- zentrale Datenbank
- Signal- und Event-Gedächtnis
- Strategiearchiv
- Trade-Journal
- Agenten-Koordination
- Analyseoberfläche
- Wissensgraph

Paperclip ist **nicht** primär:

- Hot Wallet
- low-latency execution engine
- alleiniger Risk Manager

## Execution-Prinzip

Die Order-Ausführung läuft über separate Services:

- robust
- testbar
- key-isoliert
- mit Limits
- mit Audit-Logs
- im Zweifel zuerst Shadow Mode

## Agentenrollen

### Market Data Agents
- Preise, Orderbooks, Funding, Volumen, Open Interest, Liquidationen

### News/Event Agents
- Nachrichten, Makro, Sport, Earnings, Geo-Ereignisse

### Strategy Distillation Agent
- Videos/Kurse/Transkripte → strukturierte Strategien

### Signal Scoring Agent
- bewertet Relevanz, Zuverlässigkeit, Geschwindigkeit, Tradebarkeit

### Strategy Agents
- Polymarket Mispricing
- Hyperliquid Momentum/Funding
- Event Macro
- MT5 Nasdaq/Gold/Forex
- Sports/Event Edge

### Risk Manager
- Positionsgröße
- Portfolio-Exposure
- Drawdown-Limits
- Korrelationen
- Trade-Freigabe

### Execution Agent
- baut Orders
- sendet Orders
- überwacht Fills
- meldet alles an Paperclip zurück

## Betriebsmodi

1. **Analysis Mode:** Nur Daten sammeln und Ideen erzeugen
2. **Shadow Mode:** System simuliert Trades ohne echte Ausführung
3. **Approval Mode:** System schlägt Trades vor, Andreas/Segunda gibt frei
4. **Controlled Live:** kleine Live-Trades mit Limits
5. **Scaled Live:** nur nach nachweisbarer Performance
