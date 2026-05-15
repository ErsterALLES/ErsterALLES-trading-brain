#!/usr/bin/env bash
# Run ERS-8 import + issue disposition from a shell that has a Paperclip agent API key.
# Usage: PAPERCLIP_API_KEY=... ./scripts/paperclip-board-ers8.sh
#    or: ./scripts/paperclip-board-ers8.sh <api-key>
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Board operator: complete ERS-8 Paperclip import and close the issue.

Required env (from Paperclip CEO agent settings or company agent API key):
  PAPERCLIP_API_URL
  PAPERCLIP_API_KEY
  PAPERCLIP_COMPANY_ID
  PAPERCLIP_RUN_ID      (any valid run id, or current CEO run)
  PAPERCLIP_AGENT_ID    (CEO agent uuid)

Optional:
  PAPERCLIP_ISSUE_IDENTIFIER=ERS-8

Example:
  export PAPERCLIP_API_URL=https://paperclip-z6c6.srv1357611.hstgr.cloud
  export PAPERCLIP_COMPANY_ID=<company-uuid>
  export PAPERCLIP_AGENT_ID=<ceo-agent-uuid>
  export PAPERCLIP_RUN_ID=<any-run-uuid>
  ./scripts/paperclip-board-ers8.sh <agent-api-key>
EOF
  exit 0
fi

if [[ -n "${1:-}" ]]; then
  export PAPERCLIP_API_KEY="$1"
fi

for v in PAPERCLIP_API_URL PAPERCLIP_API_KEY PAPERCLIP_COMPANY_ID PAPERCLIP_RUN_ID PAPERCLIP_AGENT_ID; do
  if [[ -z "${!v:-}" ]]; then
    printf 'Missing %s\n' "$v" >&2
    exit 2
  fi
done

exec "${ROOT}/scripts/paperclip-ers8-disposition.sh" "${ROOT}/docs/ers8-heartbeat-comment.md"
