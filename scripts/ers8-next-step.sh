#!/usr/bin/env bash
# Recovered ERS-8 next step: verify repo layout, then import skills into Paperclip when credentialed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

printf 'ERS-8 recovered next step — phase 1: local verify\n'
"${ROOT}/scripts/verify-ers8-skills.sh"

if [[ -z "${PAPERCLIP_API_KEY:-}" ]]; then
  cat >&2 <<'EOF'

ERS-8 recovered next step — phase 2: Paperclip import (skipped)

PAPERCLIP_API_KEY is not set in this environment. The repo is ready; run this script again
from a Paperclip runtime or host shell with:

  export PAPERCLIP_API_URL=...
  export PAPERCLIP_API_KEY=...
  export PAPERCLIP_COMPANY_ID=...
  export PAPERCLIP_RUN_ID=...

Optional: export PAPERCLIP_AGENT_ID to sync skills onto the CEO agent after import.

See plans/ers8-recovered-next-step.md for success criteria.
EOF
  exit 2
fi

printf '\nERS-8 recovered next step — phase 2: Paperclip import\n'
exec "${ROOT}/scripts/install-ers8-paperclip-skills.sh"
