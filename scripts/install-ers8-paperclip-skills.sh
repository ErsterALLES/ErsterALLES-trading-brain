#!/usr/bin/env bash
# Install the three Trading Brain foundation skills into the Paperclip company library.
# Sources: ErsterALLES/ErsterALLES-trading-brain (agent-skills/* on main).
#
# Requires: PAPERCLIP_API_URL, PAPERCLIP_API_KEY, PAPERCLIP_COMPANY_ID, PAPERCLIP_RUN_ID
# Optional: PAPERCLIP_AGENT_ID (CEO) to sync skills onto that agent after import

set -euo pipefail

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    printf 'Missing required env var: %s\n' "$name" >&2
    exit 1
  fi
}

require_env PAPERCLIP_API_URL
require_env PAPERCLIP_API_KEY
require_env PAPERCLIP_COMPANY_ID
require_env PAPERCLIP_RUN_ID

API="${PAPERCLIP_API_URL%/}"
COMPANY="${PAPERCLIP_COMPANY_ID}"
RUN="${PAPERCLIP_RUN_ID}"

auth_headers=(
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}"
  -H "X-Paperclip-Run-Id: ${RUN}"
  -H "Content-Type: application/json"
)

SKILL_SOURCES=(
  "ErsterALLES/ErsterALLES-trading-brain/trading-foundation"
  "ErsterALLES/ErsterALLES-trading-brain/market-data"
  "ErsterALLES/ErsterALLES-trading-brain/signal-scoring"
)

import_one() {
  local source="$1"
  printf 'Importing %s...\n' "$source"
  curl -sS -X POST "${API}/api/companies/${COMPANY}/skills/import" \
    "${auth_headers[@]}" \
    -d "$(jq -nc --arg source "$source" '{source: $source}')"
  printf '\n'
}

printf 'ERS-8: importing %d trading skills into company %s\n' "${#SKILL_SOURCES[@]}" "$COMPANY"

for source in "${SKILL_SOURCES[@]}"; do
  import_one "$source"
done

printf '\nInstalled company skills:\n'
curl -sS "${API}/api/companies/${COMPANY}/skills" \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" \
  | jq -r '.skills[]? | select(.key | test("ErsterALLES|trading-foundation|market-data|signal-scoring")) | "- \(.name) (\(.key))"' 2>/dev/null \
  || curl -sS "${API}/api/companies/${COMPANY}/skills" \
    -H "Authorization: Bearer ${PAPERCLIP_API_KEY}"

if [[ -n "${PAPERCLIP_AGENT_ID:-}" ]]; then
  printf '\nSyncing skills to agent %s...\n' "${PAPERCLIP_AGENT_ID}"
  curl -sS -X POST "${API}/api/agents/${PAPERCLIP_AGENT_ID}/skills/sync" \
    "${auth_headers[@]}" \
    -d "$(jq -nc '{
      desiredSkills: [
        "ErsterALLES/ErsterALLES-trading-brain/trading-foundation",
        "ErsterALLES/ErsterALLES-trading-brain/market-data",
        "ErsterALLES/ErsterALLES-trading-brain/signal-scoring"
      ]
    }')"
  printf '\n'
fi

printf 'Done.\n'
