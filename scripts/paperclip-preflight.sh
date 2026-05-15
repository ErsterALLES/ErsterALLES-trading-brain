#!/usr/bin/env bash
# Paperclip agent auth + ERS-8 readiness preflight for cloud CEO runs.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

missing=()
for v in PAPERCLIP_API_URL PAPERCLIP_API_KEY PAPERCLIP_COMPANY_ID PAPERCLIP_RUN_ID; do
  if [[ -z "${!v:-}" ]]; then
    missing+=("$v")
  fi
done

if ((${#missing[@]} > 0)); then
  printf 'Missing env: %s\n' "${missing[*]}" >&2
  if [[ -n "${CLOUD_AGENT_INJECTED_SECRET_NAMES:-}" ]]; then
    printf 'Injected secrets: %s\n' "$CLOUD_AGENT_INJECTED_SECRET_NAMES" >&2
  fi
  printf 'ERS-8: run ./scripts/ers8-next-step.sh after PAPERCLIP_API_KEY is injected (see plans/ers8-recovered-next-step.md)\n' >&2
  exit 2
fi

API="${PAPERCLIP_API_URL%/}"
code="$(curl -sSL -o /tmp/pc_me.json -w '%{http_code}' \
  -H "Authorization: Bearer ${PAPERCLIP_API_KEY}" \
  -H "X-Paperclip-Run-Id: ${PAPERCLIP_RUN_ID}" \
  "${API}/api/agents/me")"
printf 'GET /api/agents/me -> %s\n' "$code"
if [[ "$code" != "200" ]]; then
  head -c 200 /tmp/pc_me.json >&2 || true
  printf '\n' >&2
  exit 3
fi

bash scripts/verify-ers8-skills.sh
printf 'Preflight OK — run scripts/install-ers8-paperclip-skills.sh\n'
