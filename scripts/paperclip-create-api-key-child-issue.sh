#!/usr/bin/env bash
# Create a child issue to track cloud-agent PAPERCLIP_API_KEY injection (requires API auth).
set -euo pipefail

for v in PAPERCLIP_API_URL PAPERCLIP_API_KEY PAPERCLIP_COMPANY_ID PAPERCLIP_RUN_ID; do
  [[ -n "${!v:-}" ]] || { printf 'Missing %s\n' "$v" >&2; exit 2; }
done

API="${PAPERCLIP_API_URL%/}"
PARENT="${PAPERCLIP_PARENT_ISSUE_IDENTIFIER:-ERS-8}"
TITLE="Inject PAPERCLIP_API_KEY for cloud CEO runs"
BODY="$(cat <<'EOF'
Cloud CEO heartbeats cannot call Paperclip APIs (`GET /api/agents/me` → 401) because `PAPERCLIP_API_KEY` is not in injected secrets. The agent-home path is listed in secrets but not mounted in the cloud workspace.

**Unblock ERS-8:** add `PAPERCLIP_API_KEY` to cloud-agent injected secrets, then run `./scripts/paperclip-board-ers8.sh <agent-api-key>` on `main`.

See `docs/paperclip-cloud-agent-api-key.md`.
EOF
)"

auth=(-H "Authorization: Bearer ${PAPERCLIP_API_KEY}" -H "X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}" -H "Content-Type: application/json")

parent_id="$(curl -fsSL "${auth[@]}" "${API}/api/companies/${PAPERCLIP_COMPANY_ID}/issues" | jq -r --arg p "$PARENT" '
  (if type == "array" then . elif .issues then .issues else [] end)
  | map(select((.identifier // .key // "") == $p)) | .[0].id // empty
')"

payload="$(jq -nc \
  --arg title "$TITLE" \
  --arg body "$BODY" \
  --arg parent "${parent_id:-}" \
  '{
    title: $title,
    description: $body,
    status: "todo",
    priority: "high"
  } + (if $parent != "" then {parentIssueId: $parent} else {} end)')"

resp="$(curl -fsSL -X POST "${auth[@]}" "${API}/api/companies/${PAPERCLIP_COMPANY_ID}/issues" -d "$payload")"
printf '%s\n' "$resp" | jq -r '"Created \(.identifier // .key // .id) id=\(.id)"'
