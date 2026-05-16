---
name: claude-code-adapter
description: "Claude Code CLI integration for autonomous coding tasks"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [coding, claude-code, agent, automation]
    model: opencode/deepseek-v4-flash-free
---

# Claude Code Adapter

## Purpose
Enables Claude Code CLI (`claude`) to execute coding tasks autonomously within Paperclip agents.

## Prerequisites
```bash
# Installed globally
claude --version  # 2.1.142
```

## Configuration
```bash
# Set working directory
export CLAUDE_CODE_WORKING_DIR=/opt/data/projects/trading-brain

# Optional: Set model (uses Anthropic API)
export ANTHROPIC_API_KEY=...
```

## Usage

### Direct Command
```bash
cd /opt/data/projects/trading-brain
claude -p "Implement a new strategy: Bollinger Band Breakout with RSI confirmation" \
       --allowedTools "Bash,Edit,Read" \
       --verbose
```

### As Agent Task
```bash
# Non-interactive mode for automation
claude -p "Code review: Check vwap_scalper_hyperliquid.py for bugs" \
       --output-format "stream-json" \
       --verbose
```

## Allowed Tools
- `Bash`: Execute shell commands
- `Edit`: Modify files
- `Read`: Read files
- `Grep`: Search codebase
- `LSP`: Language server protocol

## Safety
- Always runs in project directory
- No internet access without explicit permission
- Changes must be committed before exiting

## Cost
- Uses Anthropic API (paid) or local models
- Alternative: `opencode_local` (free) for simple tasks

## Model Recommendation
- **Complex coding**: `claude-sonnet-4` (Anthropic API)
- **Simple tasks**: `opencode/deepseek-v4-flash-free` (free)
- **Fast iteration**: `gpt-4o-mini` (cheap, fast)
