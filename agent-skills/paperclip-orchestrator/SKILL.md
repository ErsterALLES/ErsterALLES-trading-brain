---
name: paperclip-orchestrator
description: "Central orchestrator for Paperclip CEO with intelligent model routing"
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [paperclip, ceo, orchestration, model-routing]
    model: opencode/deepseek-v4-flash-free
---

# Paperclip Orchestrator

## Model Routing Matrix

| Task Type | Agent | Model | Cost | Speed |
|-----------|-------|-------|------|-------|
| **Strategy Research** | Browser/Web | opencode/deepseek-v4-flash-free | $0 | Fast |
| **Complex Coding** | Claude Code | gpt-4o | ~$0.02/req | Medium |
| **Simple Coding** | Claude Code | gpt-4o-mini | ~$0.002/req | Fast |
| **Backtesting** | Trading Engine | opencode/deepseek-v4-flash-free | $0 | Fast |
| **Paper Trading** | Trading Engine | opencode/deepseek-v4-flash-free | $0 | Fast |
| **High-Stakes Decision** | CEO | gpt-4o | ~$0.01/req | Medium |
| **Routine Task** | CEO | opencode/deepseek-v4-flash-free | $0 | Fast |
| **Code Review** | Claude Code | gpt-4o | ~$0.015/req | Medium |
| **Video Transcription** | Terminal | whisper-1 (OpenAI) | ~$0.006/min | Medium |

## Cost Optimization Rules
1. Always use free models (`opencode/*`) for data processing and backtesting
2. Use `gpt-4o` only for coding tasks that require high quality
3. Use `gpt-4o-mini` for simple tasks: summaries, formatting, simple edits
4. Monitor daily token cost - alert if >$5/day

## CEO Task Assignment Protocol

### Task: Strategy Factory
```
CEO receives: "Run strategy factory"
CEO delegates to:
  1. Research Agent (opencode/free) → Find strategies
  2. Coding Agent (gpt-4o) → Implement strategy
  3. Testing Agent (opencode/free) → Backtest + paper trade
  4. Analysis Agent (gpt-4o-mini) → Evaluate results
CEO reports back: Summary + recommendations
```

### Task: Performance Analysis
```
CEO receives: "Analyze today's performance"
CEO delegates to:
  1. Data Agent (opencode/free) → Load performance DB
  2. Analysis Agent (gpt-4o-mini) → Calculate metrics
  3. Report Agent (opencode/free) → Generate summary
CEO reports back: Detailed performance report
```

### Task: Emergency Stop
```
CEO receives: "Emergency - stop all trading"
CEO executes directly: Pause all cronjobs, close positions
Priority: Instant (no delegation)
```

## Agent Configuration

### Claude Code Agent
```yaml
name: claude-code
type: coding
model: gpt-4o
max_tokens: 8000
tools: [Bash, Edit, Read, Grep]
working_dir: /opt/data/projects/trading-brain
```

### Trading Engine Agent
```yaml
name: trading-engine
type: execution
model: opencode/deepseek-v4-flash-free
max_tokens: 4000
tools: [Bash, Python, API]
working_dir: /opt/data/projects/trading-brain/trading-engine
```

### Research Agent
```yaml
name: research
type: discovery
model: opencode/deepseek-v4-flash-free
max_tokens: 4000
tools: [Browser, WebSearch, API]
```

## Self-Improvement Loop
Every 24 hours:
1. Collect performance metrics from all agents
2. Identify bottlenecks (slow models, failed tasks)
3. Adjust model assignments based on success rate
4. If agent fails 3x in a row → switch to more powerful model
5. If agent succeeds 10x in a row → try cheaper model

## Integration with Paperclip CEO
```bash
# Configure CEO adapters
# Currently: opencode_local (68 models, free)
# Next: Add claude_local (Claude Code integration)

# CEO Task
curl -X POST https://paperclip-z6c6.srv1357611.hstgr.cloud/api/ceo/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task": "strategy_factory",
    "agents": ["research", "claude-code", "trading-engine"],
    "model_routing": {
      "research": "opencode/deepseek-v4-flash-free",
      "coding": "gpt-4o",
      "testing": "opencode/deepseek-v4-flash-free"
    }
  }'
```

## Monitoring Dashboard
- Active agents: http://localhost:3000/agents
- Performance metrics: http://localhost:3000/performance
- Cost tracking: http://localhost:3000/costs
