# YouTube / Video Ingestion Plan

## Problem

YouTube blockt häufig Agenten, Headless-Zugriffe oder Downloader. Andreas möchte idealerweise nur einen YouTube-Link liefern und der Rest soll automatisch laufen. Alternativ kann er Videos manuell herunterladen und bereitstellen.

## Ziel

Ein robuster, mehrstufiger Ingestion-Prozess für Trading-Videos:

```text
YouTube URL / local video
        ↓
Transcript extraction
        ↓
Audio transcription fallback
        ↓
Frame extraction
        ↓
Vision analysis
        ↓
Transcript-frame alignment
        ↓
Strategy extraction
        ↓
Paperclip Strategy Spec
```

## Stufenmodell

### Stufe 1: Transcript-first

Versuche zuerst:

- YouTube Transcript API
- vorhandene Untertitel
- Sprachfallback: `de,en`

Vorteil:

- schnell
- wenig Daten
- kein Video-Download nötig

Nachteil:

- Viele Videos haben keine Untertitel
- Trading-Erklärung braucht oft visuelle Chartanalyse

### Stufe 2: Metadata + chapter extraction

Zusätzlich sammeln:

- Titel
- Kanal
- Beschreibung
- Kapitel
- Upload-Datum
- Länge
- Tags, falls verfügbar

### Stufe 3: Video/Audio Download, nur wenn zulässig und möglich

Mögliche technische Wege:

- `yt-dlp` mit konservativem Rate Limit
- offizielle/zulässige Quellen, wenn vorhanden
- Cookies nur aus Andreas' eigener Browser-Session und nur für Inhalte, die er selbst legal ansehen darf
- kein aggressives Umgehen von Schutzmechanismen dokumentieren

Wichtig:

- Keine Umgehung von Geoblocking/Paywalls als Projektnorm.
- Wenn YouTube blockt, sauberer Fallback statt endloses Bot-Gefrickel.

### Stufe 4: User-provided file fallback

Wenn Link-Ingestion scheitert:

Andreas legt Datei ab in:

```text
/opt/data/projects/trading-brain/inbox/videos/
```

oder sendet sie über einen vereinbarten Upload-Weg.

Dann läuft die gleiche Pipeline lokal weiter:

- Whisper Transkription
- Frame Extraction
- Vision Analysis
- Strategy Extraction

### Stufe 5: Lokaler Download-Helper auf Andreas' Rechner

Beste praktische Lösung, wenn YouTube serverseitig blockt:

- Andreas installiert lokal einen kleinen Helper
- Er gibt dort nur den YouTube-Link ein
- Helper lädt das Video mit seiner normalen Browser-/Netzwerkumgebung
- Datei wird automatisch zum Projektserver synchronisiert
- Segunda verarbeitet danach alles automatisch

Vorteil:

- weniger Bot-Blocking
- Andreas muss nicht manuell Dateinamen/Uploads verwalten
- Server bleibt sauber

## MVP-Implementierung

1. `inbox/videos/` Dropfolder anlegen
2. `video_manifest.jsonl` für eingehende Videos
3. Ingestion-Script:
   - URL erkennen
   - transcript attempt
   - download attempt falls zulässig
   - local file fallback
4. Whisper-Transkription für lokale Dateien
5. ffmpeg Frame Extraction:
   - alle 10 Sekunden
   - zusätzlich Szenenwechsel
6. Vision-Analyse pro relevantem Frame
7. Strategy Extraction in YAML/JSON

## Output pro Video

```text
videos/<video_id>/
  metadata.json
  transcript.timestamped.json
  transcript.clean.md
  frames/
  frame_analysis.jsonl
  aligned_segments.jsonl
  strategy_spec.yaml
  strategy_report.md
```

## Noch zu entscheiden

- Welches Vision-Modell für Frames?
- Whisper lokal oder OpenAI Whisper API?
- Sollen Videos dauerhaft gespeichert oder nach Frame-/Transkript-Extraktion gelöscht werden?
- Wie groß darf der Video-Speicher werden?
- Wie wird Paperclip angebunden: direkte DB, API oder File-Sync?
