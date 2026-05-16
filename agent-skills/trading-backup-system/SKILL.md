---
name: trading-backup-system
description: "Automated backup system for trading strategies, configs, and trade data"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [backup, safety, data-persistence, automation]
    model: opencode/deepseek-v4-flash-free
---

# Trading Backup System

## Safety First
All backups stored in:
- **Local**: `/opt/data/backups/trading-brain-YYYYMMDD-HHMMSS/`
- **GitHub**: `ErsterALLES/ErsterALLES-trading-brain/`
- **Paperclip Assets**: Skills + Configs

## What Gets Backed Up
```
📦 trading-brain/
  ├── trading-engine/         # All Python strategies
  ├── agent-skills/           # Paperclip skills (market-data, signal-scoring, etc.)
  ├── data/                   # Trade history, performance DB
  ├── logs/                   # Execution logs
  ├── .env                    # API keys (encrypted)
  └── config.yaml             # System config
```

## Backup Schedule
- **Hourly**: Trade data (automated via cron)
- **Daily**: Full system backup
- **On-demand**: Before major changes

## Quick Restore
```bash
# From local backup
cd /opt/data/backups/trading-brain-20260516-091005
cp -r * /opt/data/projects/trading-brain/

# From GitHub
git clone https://github.com/ErsterALLES/ErsterALLES-trading-brain.git
cd ErsterALLES-trading-brain
```

## Commands
```bash
# Manual backup
./scripts/backup.sh

# Restore last backup
./scripts/restore.sh latest
```

## Last Backup
- Date: 2026-05-16 09:10:05
- Location: `/opt/data/backups/trading-brain-20260516-091005`
- Size: Pending
- Status: ✅ Complete
