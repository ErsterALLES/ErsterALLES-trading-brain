#!/usr/bin/env bash
# Resolve PAPERCLIP_API_KEY from env or a mounted key file (not committed).
paperclip_resolve_api_key() {
  local root="${1:-.}"
  if [[ -n "${PAPERCLIP_API_KEY:-}" ]]; then
    return 0
  fi
  local f="${PAPERCLIP_API_KEY_FILE:-}"
  if [[ -z "$f" ]]; then
    for candidate in "${root}/.paperclip-api-key" "${root}/.secrets/paperclip-api-key"; do
      if [[ -f "$candidate" ]]; then
        f="$candidate"
        break
      fi
    done
  fi
  if [[ -n "$f" && -f "$f" && -r "$f" ]]; then
    PAPERCLIP_API_KEY="$(tr -d '[:space:]' <"$f")"
    export PAPERCLIP_API_KEY
    printf 'Resolved PAPERCLIP_API_KEY from file (len=%s)\n' "${#PAPERCLIP_API_KEY}" >&2
    return 0
  fi
  return 1
}
