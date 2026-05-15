#!/usr/bin/env bash
# Install Trading Brain foundation skills from GitHub into the Paperclip company library.
# Requires agent-authenticated Paperclip API access (PAPERCLIP_API_KEY).
set -euo pipefail

: "${PAPERCLIP_API_URL:?PAPERCLIP_API_URL is required}"
: "${PAPERCLIP_COMPANY_ID:?PAPERCLIP_COMPANY_ID is required}"
: "${PAPERCLIP_API_KEY:?PAPERCLIP_API_KEY is required}"
: "${PAPERCLIP_RUN_ID:?PAPERCLIP_RUN_ID is required}"

API_BASE="${PAPERCLIP_API_URL%/}"
AUTH_HEADER="Authorization: Bearer ${PAPERCLIP_API_KEY}"
RUN_HEADER="X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}"

# GitHub sources (key-style). Paperclip resolves these to ErsterALLES/ErsterALLES-trading-brain.
readonly SKILL_SOURCES=(
  "ErsterALLES/ErsterALLES-trading-brain/trading-foundation"
  "ErsterALLES/ErsterALLES-trading-brain/market-data"
  "ErsterALLES/ErsterALLES-trading-brain/signal-scoring"
)

import_skill() {
  local source="$1"
  echo "Importing ${source} ..."
  curl -fsSL -X POST "${API_BASE}/api/companies/${PAPERCLIP_COMPANY_ID}/skills/import" \
    -H "${AUTH_HEADER}" \
    -H "${RUN_HEADER}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg source "$source" '{source: $source}')"
}

list_company_skills() {
  curl -fsSL "${API_BASE}/api/companies/${PAPERCLIP_COMPANY_ID}/skills" \
    -H "${AUTH_HEADER}" \
    -H "${RUN_HEADER}"
}

sync_agent_skills() {
  local agent_id="${1:?agent id required}"
  echo "Syncing skills onto agent ${agent_id} ..."
  curl -fsSL -X POST "${API_BASE}/api/agents/${agent_id}/skills/sync" \
    -H "${AUTH_HEADER}" \
    -H "${RUN_HEADER}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
      --arg a "${SKILL_SOURCES[0]##*/}" \
      --arg b "${SKILL_SOURCES[1]##*/}" \
      --arg c "${SKILL_SOURCES[2]##*/}" \
      '{desiredSkills: [$a, $b, $c]}')"
}

main() {
  local imported=0
  for source in "${SKILL_SOURCES[@]}"; do
    import_skill "$source"
    imported=$((imported + 1))
  done
  echo "Imported ${imported} skills."

  echo "Company skill library:"
  list_company_skills | jq -r '.[] | "\(.key) (\(.slug))"' 2>/dev/null || list_company_skills

  if [[ -n "${PAPERCLIP_AGENT_ID:-}" ]]; then
    sync_agent_skills "${PAPERCLIP_AGENT_ID}"
  fi
}

main "$@"
