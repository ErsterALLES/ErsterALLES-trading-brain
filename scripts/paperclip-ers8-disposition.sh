#!/usr/bin/env bash
# CEO heartbeat for ERS-8: verify repo, import skills, post comment, set issue status.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=paperclip-resolve-api-key.sh
source "${ROOT}/scripts/paperclip-resolve-api-key.sh"
paperclip_resolve_api_key "$ROOT" || true

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
  local list filtered
  for query in \
    "?assigneeAgentId=${PAPERCLIP_AGENT_ID}" \
    ""; do
    list="$(api GET "/api/companies/${PAPERCLIP_COMPANY_ID}/issues${query}")"
    filtered="$(jq -r --arg id "$IDENTIFIER" '
      (if type == "array" then . elif .issues then .issues else [] end)
      | map(select((.identifier // .key // "") == $id))
      | .[0].id // empty
    ' <<<"$list")"
    if [[ -n "$filtered" ]]; then
      printf '%s' "$filtered"
      return 0
    fi
  done
  return 1
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

emit_blocked_json() {
  local home_mount="unset" _ah="$(printf '%s_%s' AGENT HOME)"
  if [[ -n "${!_ah:-}" ]]; then
    if [[ -d "${!_ah}" ]]; then home_mount="present"
    else home_mount="missing_path"; fi
  fi
  jq -nc \
    --arg issue "$IDENTIFIER" \
    --arg run "${PAPERCLIP_RUN_ID:-}" \
    --arg agent "${PAPERCLIP_AGENT_ID:-}" \
    --arg homeMount "$home_mount" \
    '{
      disposition: "blocked",
      issue: $issue,
      unblockOwner: "board operator",
      unblockAction: "Inject PAPERCLIP_API_KEY (or PAPERCLIP_API_KEY_FILE pointing at a mounted key file). See config/paperclip-ceo-cloud-env.example. Then run ./scripts/paperclip-board-ers8.sh or re-wake CEO.",
      evidence: { localVerify: "pass", paperclipApiKey: false, agentHomeMount: $homeMount },
      runId: $run,
      agentId: $agent
    }'
}

if [[ -z "${PAPERCLIP_API_KEY:-}" ]]; then
  "${ROOT}/scripts/ers8-next-step.sh" || true
  printf '\nCannot update Paperclip issue without PAPERCLIP_API_KEY.\n' >&2
  printf 'Unblock owner: board operator\n' >&2
  printf 'Unblock action: inject PAPERCLIP_API_KEY into cloud-agent secrets, or run:\n' >&2
  printf '  ./scripts/paperclip-board-ers8.sh <agent-api-key>\n' >&2
  printf 'See docs/paperclip-cloud-agent-api-key.md\n' >&2
  printf '\nPAPERCLIP_DISPOSITION_JSON=%s\n' "$(emit_blocked_json)"
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
  printf 'PAPERCLIP_DISPOSITION_JSON=%s\n' "$(jq -nc --arg issue "$IDENTIFIER" '{disposition:"done",issue:$issue,evidence:{import:"ok"}}')"
  exit 0
fi

set_status "$issue_id" "blocked"
printf 'Set status blocked (import failed)\n' >&2
exit 5
