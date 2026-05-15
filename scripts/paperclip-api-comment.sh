#!/usr/bin/env bash
# Post a CEO heartbeat comment to a Paperclip issue when PAPERCLIP_API_KEY is set.
# Usage: paperclip-api-comment.sh <issueId> <markdown-body-file>
set -euo pipefail

issue_id="${1:?issue id required}"
body_file="${2:?body file required}"

for v in PAPERCLIP_API_URL PAPERCLIP_API_KEY PAPERCLIP_RUN_ID; do
  if [[ -z "${!v:-}" ]]; then
    printf 'Missing %s — cannot post issue comment\n' "$v" >&2
    exit 2
  fi
done

API="${PAPERCLIP_API_URL%/}"
body="$(cat "$body_file")"

curl -fsSL -X POST "${API}/api/issues/${issue_id}/comments" \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" \
  -H "X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --arg body "$body" '{body: $body}')"

printf '\nPosted comment to issue %s\n' "$issue_id"
