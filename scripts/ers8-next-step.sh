#!/usr/bin/env bash
# ERS-8 handoff: local verify + optional Paperclip import.
# CEO cloud heartbeats run this when credentialed; otherwise exit 2 with unblock guidance.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

printf '== ERS-8 next step ==\n\n'

printf '1) Local structure preflight\n'
"${ROOT}/scripts/verify-ers8-skills.sh"

if [[ -n "${PAPERCLIP_API_KEY:-}" ]]; then
  printf '\n2) Paperclip company import (API key present)\n'
  "${ROOT}/scripts/install-ers8-paperclip-skills.sh"
  printf '\nDisposition: ERS-8 repo + Paperclip import complete. Mark ERS-8 done.\n'
  exit 0
fi

cat >&2 <<'EOF'

2) Paperclip import skipped (PAPERCLIP_API_KEY not set)

Repo deliverables are ready. Unblock import by injecting PAPERCLIP_API_KEY into the
cloud-agent secret set, or run from an authenticated Paperclip/VPS shell:

  ./scripts/install-ers8-paperclip-skills.sh

See plans/ers8-recovered-next-step.md for success criteria.
EOF

printf '\nDisposition: ERS-8 repo deliverables verified; Paperclip import blocked on API key.\n'
exit 2
