#!/usr/bin/env bash
# ERS-8 handoff: local verify + optional Paperclip import.
# ERS-9 uses this script as the durable "next step" after successful repo work.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

printf '== ERS-8 next step ==\n\n'

printf '1) Local structure preflight\n'
"${ROOT}/scripts/verify-ers8-skills.sh"

if [[ -n "${PAPERCLIP_API_KEY:-}" ]]; then
  printf '\n2) Paperclip company import (API key present)\n'
  "${ROOT}/scripts/install-ers8-paperclip-skills.sh"
  printf '\nDisposition: ERS-8 repo + Paperclip import complete. Mark ERS-8 and ERS-9 done.\n'
else
  printf '\n2) Paperclip import skipped (PAPERCLIP_API_KEY not set)\n'
  printf '   Run in an authenticated Paperclip shell:\n'
  printf '     ./scripts/install-ers8-paperclip-skills.sh\n'
  printf '\nDisposition: ERS-8 repo deliverables done (verify passed).\n'
  printf '             Delegate Paperclip import verification if import was not run in prod.\n'
fi
