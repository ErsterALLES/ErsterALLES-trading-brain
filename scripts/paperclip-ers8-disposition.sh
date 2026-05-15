#!/usr/bin/env bash
# CEO heartbeat for ERS-8: verify repo, import skills, post comment, set issue status.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

IDENTIFIER="${PAPERCLIP_ISSUE_IDENTIFIER:-ERS-8}"
COMMENT_FILE="${1:-}"

api() {
  local method="$1" path="$2"
  shift 2
  curl -fsSL -X "$method" "${API}${path}" \
    -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" \
    -H "X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}" \
    -H "Content-Type: application/json" \
    "$@"
}

find_issue_id() {
  local list
  list="$(api GET "/api/companies/${PAPERCLIP_COMPANY_ID}/issues?assigneeAgentId=${PAPERCLIP_AGENT_ID}")"
  jq -r --arg id "$IDENTIFIER" '
    (if type == "array" then . elif .issues then .issues else [] end)
    | map(select((.identifier // .key // "") == $id))
    | .[0].id // empty
  ' <<<"$list"
}

post_comment() {
  local issue_id="$1" body="$2"
  api POST "/api/issues/${issue_id}/comments" \
    -d "$(jq -nc --arg body "$body" '{body: $body}')"
}

set_status() {
  local issue_id="$1" status="$2"
  api PATCH "/api/issues/${issue_id}" \
    -d "$(jq -nc --arg status "$status" '{status: $status}')"
}

printf '== ERS-8 disposition (CEO) ==\n\n'

if ! "${ROOT}/scripts/verify-ers8-skills.sh"; then
  printf 'Local verify failed — fix repo before Paperclip import.\n' >&2
  exit 1
fi

if [[ -z "${PAPERCLIP_API_KEY:-}" ]]; then
  "${ROOT}/scripts/ers8-next-step.sh" || true
  printf '\nCannot update Paperclip issue without PAPERCLIP_API_KEY.\n' >&2
  printf 'Unblock: inject PAPERCLIP_API_KEY into cloud-agent secrets; re-run %s\n' "$0" >&2
  exit 2
fi

for v in PAPERCLIP_API_URL PAPERCLIP_COMPANY_ID PAPERCLIP_RUN_ID PAPERCLIP_AGENT_ID; do
  if [[ -z "${!v:-}" ]]; then
    printf 'Missing %s\n' "$v" >&2
    exit 2
  fi
done

API="${PAPERCLIP_API_URL%/}"
code="$(curl -sSL -o /tmp/pc_me.json -w '%{http_code}' \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" \
  -H "X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}" \
  "${API}/api/agents/me")"
if [[ "$code" != "200" ]]; then
  printf 'Auth failed GET /api/agents/me -> %s\n' "$code" >&2
  head -c 200 /tmp/pc_me.json >&2 || true
  exit 3
fi
printf 'Paperclip auth OK\n'

issue_id="$(find_issue_id || true)"
if [[ -z "$issue_id" ]]; then
  printf 'Issue %s not found for assignee — listing company issues\n' "$IDENTIFIER" >&2
  api GET "/api/companies/${PAPERCLIP_COMPANY_ID}/issues" | jq -r '
    (if type == "array" then . elif .issues then .issues else [] end)
    | .[:20][] | "\(.identifier // .key // "?") \(.id) \(.status)"
  ' >&2 || true
  exit 4
fi
printf 'Issue %s id=%s\n' "$IDENTIFIER" "$issue_id"

import_ok=0
if "${ROOT}/scripts/install-ers8-paperclip-skills.sh"; then
  import_ok=1
fi

if [[ -n "$COMMENT_FILE" && -f "$COMMENT_FILE" ]]; then
  body="$(cat "$COMMENT_FILE")"
else
  body="$(cat <<EOF
## CEO heartbeat — ERS-8

- Local verify: passed
- Paperclip import: $([[ "$import_ok" == 1 ]] && echo 'completed' || echo 'failed — see run logs')
- Branch: \`main\` includes \`scripts/ers8-next-step.sh\` and runbook

$([[ "$import_ok" == 1 ]] && echo '**Disposition:** repo + company library import complete.' || echo '**Disposition:** import failed; issue remains blocked until skills appear in company library.')
EOF
)"
fi

post_comment "$issue_id" "$body"
printf 'Posted comment\n'

if [[ "$import_ok" == 1 ]]; then
  set_status "$issue_id" "done"
  printf 'Set status done\n'
else
  set_status "$issue_id" "blocked"
  printf 'Set status blocked (import failed)\n'
  exit 5
fi
