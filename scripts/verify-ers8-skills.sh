#!/usr/bin/env bash
# Local preflight for ERS-8: three GitHub-importable trading skills in-repo.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

required=(
  agent-skills/trading-foundation/SKILL.md
  agent-skills/market-data/SKILL.md
  agent-skills/signal-scoring/SKILL.md
  skills/trading-foundation
  skills/market-data
  skills/signal-scoring
  scripts/install-ers8-paperclip-skills.sh
  scripts/ers8-next-step.sh
  plans/ers8-recovered-next-step.md
)

for path in "${required[@]}"; do
  if [[ ! -e "$path" ]]; then
    printf 'Missing: %s\n' "$path" >&2
    exit 1
  fi
done

for skill in trading-foundation market-data signal-scoring; do
  file="agent-skills/${skill}/SKILL.md"
  for field in slug key; do
    if ! grep -q "^${field}:" "$file"; then
      printf 'Missing frontmatter %s in %s\n' "$field" "$file" >&2
      exit 1
    fi
  done
done

printf 'ERS-8 local structure OK (%d skills, install script present)\n' 3
