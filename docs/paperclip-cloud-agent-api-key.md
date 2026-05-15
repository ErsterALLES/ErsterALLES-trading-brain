# Inject `PAPERCLIP_API_KEY` for cloud CEO agents

ERS-8 and other CEO heartbeats need Bearer auth to call Paperclip (`/api/agents/me`, skill import, issue comments).

## Symptom

Cloud agent logs:

```text
Missing env: PAPERCLIP_API_KEY
GET /api/agents/me -> 401
```

`CLOUD_AGENT_INJECTED_SECRET_NAMES` lists identity vars only (no API key).

## Fix (board operator)

1. In Paperclip UI, open the **CEO** agent (see `PAPERCLIP_AGENT_ID` in the agent run env).
2. Copy the agent **API key** (or create one if missing).
3. Add `PAPERCLIP_API_KEY` to the Cursor Cloud adapter **env** / cloud-agent **injected secrets** for this repo.
4. Re-wake the CEO on **ERS-8**, or run on the VPS / any authenticated shell:

```bash
cd ErsterALLES-trading-brain
export PAPERCLIP_API_URL=https://paperclip-z6c6.srv1357611.hstgr.cloud
export PAPERCLIP_COMPANY_ID=<company-uuid>
export PAPERCLIP_AGENT_ID=<ceo-agent-uuid>
export PAPERCLIP_RUN_ID=<any-valid-run-uuid>
./scripts/paperclip-board-ers8.sh <paste-agent-api-key>
```

That runs verify, imports three skills, posts the heartbeat comment, and sets **ERS-8** to `done` or `blocked`.

## Verify

```bash
curl -sS -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  -H "X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID" \
  "$PAPERCLIP_API_URL/api/agents/me"
```

Expect HTTP 200 and agent JSON.
