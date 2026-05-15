# Cursor Pro / Cursor Cloud Integration for Paperclip

**Date:** 2026-05-14  
**Status:** Cursor API key validated; Paperclip adapter configuration pending.

## Summary

Andreas has a Cursor Pro subscription and created a Cursor API key intended for Paperclip.

The key format is:

```text
crsr_...<redacted>
```

Do **not** store the full key in project docs. It was provided in chat and validated via Cursor API.

## Validation Results

Tested against Cursor API:

- `https://api.cursor.com/v1/me` → success
- API key name: `paperclip`
- User email: `kaufi3@gmx.de`
- `https://api.cursor.com/v1/models` → success, models are listed
- `https://api.cursor.com/v1/agents` → success, currently empty

Conclusion: **Cursor API key is valid and usable.**

## Cursor API Authentication Notes

Cursor docs say APIs use Basic Auth:

```bash
curl https://api.cursor.com/... -u YOUR_API_KEY:
```

Practical test also showed Bearer auth works for `/v1/me`, `/v1/models`, and `/v1/agents`.

Paperclip may use either:

- Basic auth internally
- Bearer auth internally
- env var passed to its Cursor adapter

## Paperclip Frontend Findings

Paperclip frontend bundle includes these adapter types:

```text
acpx_local
claude_local
codex_local
cursor_cloud
gemini_local
opencode_local
pi_local
cursor
openclaw_gateway
```

Cursor-related adapters:

- `cursor_cloud` — label: **Cursor Cloud**, description: Managed remote Cursor agent
- `cursor` — label: **Cursor**, description: Local Cursor agent

Important: Paperclip supports `cursor_cloud` natively in the UI/adapter system. This likely means no large download is needed for Cursor Cloud. A local Cursor agent may require a CLI/package, but Cursor Cloud should use the API key.

## Likely Configuration

Paperclip agent adapter type:

```json
{
  "adapterType": "cursor_cloud",
  "adapterConfig": {
    "model": "default",
    "env": {
      "CURSOR_API_KEY": {
        "type": "plain",
        "value": "crsr_..."
      }
    }
  }
}
```

Alternative possible env names to test:

- `CURSOR_API_KEY`
- `CURSOR_TOKEN`
- `API_KEY`

The frontend generic adapter config builder supports:

- `instructionsFilePath`
- `promptTemplate`
- `bootstrapPromptTemplate`
- `model`
- `env`
- adapter schema values

## What Still Needs Paperclip Access

To activate this inside Paperclip we need one of:

1. Authenticated Paperclip UI browser session
2. Paperclip board/session API auth
3. Direct Docker/DB access on the VPS
4. Paperclip admin route/API for agents/adapters/secrets

Current blocker:

- Hermes container has no browser installed
- Hermes container has no sudo/root
- Docker socket unavailable
- SSH password to Hostinger VPS was rejected during latest test

## Next Setup Steps

### Step 1: Get Paperclip Admin Access

Options:

- Use browser UI manually once and configure `cursor_cloud` adapter
- Fix SSH/root access to VPS
- Provide updated root password or SSH key access
- Install browser/CDP sidecar so Hermes can operate the UI

### Step 2: Create Cursor Secret in Paperclip

Preferred:

- Store Cursor key as Paperclip Secret, not as plaintext adapter config
- Use secret reference in adapter env binding

### Step 3: Configure Cursor Cloud Agent

Create or update an agent with:

- Adapter type: `cursor_cloud`
- Model: `default` or `composer-2` / latest model from `/v1/models`
- Env: Cursor API key secret
- Instructions: Trading-Brain/Paperclip agent role
- Workspace: Trading-Brain project or Paperclip workspace

### Step 4: Test Adapter Environment

Use Paperclip's adapter test endpoint if authenticated:

```text
POST /companies/{companyId}/adapters/cursor_cloud/test-environment
```

The frontend shows Paperclip has this endpoint.

### Step 5: Test Real Cursor Agent Run

Create a small Paperclip issue:

> Read the Trading Brain project README and summarize next setup steps.

Verify Cursor Cloud agent runs and reports back.

## Does Anything Need Downloading?

Likely answer:

- **Cursor Cloud:** no major download; needs API key configured in Paperclip.
- **Local Cursor adapter:** may require Cursor/Cursor Agent CLI. This is optional and probably not needed if Cursor Cloud works.
- **Browser automation:** still separate. Cursor does not replace Chromium for Paperclip UI automation.

## Security

- Do not store full `crsr_` key in project docs.
- Prefer Paperclip secret store or environment secret.
- Rotate the key if it was exposed broadly.

## Immediate Recommendation

Use Cursor Cloud inside Paperclip as a managed coding agent once Paperclip admin access is available. Keep Ollama/OpenRouter as fallback providers and Cursor as the Pro subscription-backed coding runner.
