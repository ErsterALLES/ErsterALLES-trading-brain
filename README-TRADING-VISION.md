# Trading Brain / Paperclip Strategy Lab

**Owner:** Andreas Kaufmann  
**Agent:** Segunda / Hermes Agent  
**Created:** 2026-05-14  
**Purpose:** Dauerhafte Projektakte für das Trading-Brain-System, damit der Kontext nicht wieder aus Telegram-Backups rekonstruiert werden muss.

## Zielbild

Paperclip soll zur zentralen Datenbank, Gedächtnis- und Auswertungsschicht aller Trading-Bots werden:

- Signale sammeln, bewerten, speichern und querverweisen
- Marktdaten, News, Videos, Social, On-chain, Makro, Sport, Earnings und weitere Quellen integrieren
- Strategien aus Daten, Videos und Trade-Outcomes ableiten und versionieren
- Polymarket und Hyperliquid im aktuellen Fokus analysieren
- MetaTrader/MT5 als konventionellen Trading-Arm für Nasdaq, Gold, Forex, Rohstoffe usw. anbinden
- Später weitere Märkte: Agrar, Gold, Öl, Nasdaq, Futures, Spot, Gridbots, Sportwetten-Daten, Social Sentiment usw.

## Sicherheits- und Rechtsnotizen

- **Keine Private Keys in diesem Projektordner speichern.** Wenn Wallets erwähnt werden, nur Adressen oder redaktierte IDs.
- Polymarket kann in Deutschland rechtlich/geografisch problematisch sein. Diese Projektakte behandelt Polymarket zunächst als Analyse-/Signalquelle. Aktives Trading muss rechtlich sauber geprüft werden.
- Automatisiertes Trading startet nicht direkt mit vollem Echtgeld-Autopilot, sondern über Analyse → Shadow Mode → kleine kontrollierte Live-Trades → Skalierung.

## Projektstruktur

- `conversation-notes/` — dauerhafte Gesprächs- und Entscheidungsnotizen
- `architecture/` — Systemarchitektur und Komponenten
- `ingestion/` — Datenquellen, YouTube-/Video-Pipeline, News, APIs
- `schemas/` — Datenmodelle für Paperclip/Trading-Brain
- `plans/` — konkrete Baupläne und nächste Schritte
- `secrets-redacted/` — Platzhalter/Referenzen ohne Klartext-Keys

## Aktueller Fokus

1. Paperclip als Trading-Brain strukturieren
2. Strategy Distillation Agent: YouTube/Video → Transkript + Frames → Strategie-Regeln → Bot-fähige Specs
3. Polymarket + Hyperliquid als erste Markt-/Signalmodule
4. MT5/MetaTrader Bridge als konventioneller Trading-Arm
5. Alles versioniert, auditierbar und in Paperclip nachvollziehbar speichern

## Wiederaufnahme-Prompt

Wenn der Kontext verloren geht, sag einfach:

> Weiter am Trading-Brain-Projekt. Lies `/opt/data/projects/trading-brain/README.md` und die neuesten Dateien unter `conversation-notes/` und `plans/`.
