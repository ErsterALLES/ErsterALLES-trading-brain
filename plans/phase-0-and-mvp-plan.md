# Phase 0 + MVP Plan — Trading Brain / Strategy Lab

## Goal

Paperclip als dauerhaftes Trading-Brain vorbereiten und als erstes MVP den Strategy Distillation Agent für YouTube/lokale Trading-Videos bauen.

## Phase 0: Projekt- und Systemaudit

Dauer: 45–90 Minuten

Tasks:

1. Projektordner prüfen und Kontextdateien lesen
2. Paperclip-Instanz prüfen:
   - API/API-Routen
   - DB-Typ
   - Möglichkeit für eigene Objekte/Skills/Routines
3. Bestehende Trading-Projekte inventarisieren:
   - copy-trader-v2
   - ai-coin-factory
   - polymarket-ki-trader
   - solana-bot
   - paperclip-trading-core, falls vorhanden
4. Wallet-/Key-Risiko prüfen, ohne Private Keys neu in Dokumente zu schreiben
5. Entscheiden:
   - Paperclip-native Datenhaltung
   - separate Trading-DB neben Paperclip
   - hybride File/API-Sync-Lösung

## MVP 1: Strategy Distillation Agent

Dauer: 1–2 Tage für brauchbaren Prototyp

### Inputs

- YouTube URL
- lokale Videodatei
- optional: Markt/Strategietyp vom User

### Outputs

- `metadata.json`
- `transcript.timestamped.json`
- `frames/`
- `frame_analysis.jsonl`
- `strategy_spec.yaml`
- `strategy_report.md`
- Paperclip-Eintrag / Skill / Task mit Evidenzlinks

### Pipeline

1. URL/File Intake
2. Transcript attempt
3. Download/local fallback
4. Whisper transcription if needed
5. Frame extraction via ffmpeg
6. Vision analysis of key frames
7. Alignment transcript ↔ frames
8. Strategy extraction
9. Human-readable report
10. Bot-ready YAML strategy spec

## MVP 2: Polymarket + Hyperliquid Collectors

Dauer: 1–3 Tage

- Polymarket Gamma API Collector
- Polymarket CLOB price/orderbook collector
- Hyperliquid market/funding/position collector
- Signals in Paperclip speichern
- Daily/Hourly Summary

## MVP 3: MT5 Bridge

Dauer: 2–4 Tage

- MT5 Demo Account anbinden
- Kursdaten abrufen
- Paper Trading / Demo Execution
- Strategie-Spec aus MVP 1 in MT5-kompatible Regeln übersetzen

## Risk Policy

Start nur mit:

1. Analysis Mode
2. Shadow Mode
3. Approval Mode
4. kleine Live-Trades
5. Skalierung nach Performance

## Nächster konkreter Schritt

Wenn Andreas „go“ sagt:

1. Paperclip und bestehende Trading-Projekte auditieren
2. Ingestion-Prototyp für ein erstes YouTube-Video oder lokale Videodatei bauen
3. Testvideo verarbeiten
4. Strategy Spec erzeugen
5. Ergebnis in Projektordner speichern
