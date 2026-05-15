#!/usr/bin/env bash
# Print curl commands for board to mark ERS-8 blocked + comment when cloud CEO cannot auth.
# Usage: PAPERCLIP_API_KEY=... ./scripts/paperclip-ers8-board-mark-blocked.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "${ROOT}/scripts/paperclip-resolve-api-key.sh"
paperclip_resolve_api_key "$ROOT" || true

for v in PAPERCLIP_API_URL PAPERCLIP_API_KEY PAPERCLIP_COMPANY_ID PAPERCLIP_RUN_ID; do
  [[ -n "${!v:-}" ]] || { printf 'Set %s (agent API key) first\n' "$v" >&2; exit 2; }
done

API="${PAPERCLIP_API_URL%/}"
API="${API/http:\/\//https:\/\/}"
IDENT="${PAPERCLIP_ISSUE_IDENTIFIER:-ERS-8}"
BODY_FILE="${1:-${ROOT}/docs/ers8-heartbeat-comment.md}"
BODY="$(jq -Rs . <"$BODY_FILE")"

auth=(-H "Authorization: Bearer ${PAPERCLIP_API_KEY}" -H "X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}" -H "Content-Type: application/json")

issue_id="$(curl -fsSL "${auth[@]}" "${API}/api/companies/${PAPERCLIP_COMPANY_ID}/issues" | jq -r --arg id "$IDENT" '
  (if type == "array" then . elif .issues then .issues else [] end)
  | map(select((.identifier // .key // "") == $id)) | .[0].id // empty')"

if [[ -z "$issue_id" ]]; then
  printf 'Issue %s not found\n' "$IDENT" >&2
  exit 4
fi

printf 'Issue %s id=%s\n' "$IDENT" "$issue_id"
printf 'Run these commands (or pipe to bash):\n\n'

cat <<EOF
curl -fsSL -X POST '${API}/api/issues/${issue_id}/comments' \\
  -H 'Authorization: Bearer ${PAPERCLIP_API_KEY}' \\
  -H 'X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}' \\
  -H 'Content-Type: application/json' \\
  -d '{"body":${BODY}}'

curl -fsSL -X PATCH '${API}/api/issues/${issue_id}' \\
  -H 'Authorization: Bearer ${PAPERCLIP_API_KEY}' \\
  -H 'X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}' \\
  -H 'Content-Type: application/json' \\
  -d '{"status":"blocked"}'
EOF

if [[ "${EXECUTE:-}" == "1" ]]; then
  printf '\nExecuting (-- EXECUTE=1)...\n'
  curl -fsSL -X POST "${auth[@]}" "${API}/api/issues/${issue_id}/comments" \
    -d "{\"body\":${BODY}}"
  curl -fsSL -X PATCH "${auth[@]}" "${API}/api/issues/${issue_id}" \
    -d '{"status":"blocked"}'
  printf '\nDone: ERS-8 marked blocked with comment.\n'
fi
