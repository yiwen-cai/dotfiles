---
name: external-coding-agents
description: CLI-based autonomous coding agents — Claude Code, OpenAI Codex, and OpenCode CLI workflows for features, PRs,
  and code review.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# External Coding Agents

Use this skill when delegating coding tasks to CLI-based autonomous coding agents. Covers Claude Code, OpenAI Codex CLI, and OpenCode CLI.

## When to Use

- The user wants to use a CLI coding agent for a feature or PR
- Need to compare or choose between coding agent tools
- Setting up auth, configuration, or workflows for any CLI agent
- Reviewing code produced by an external agent

## Agent Comparison

| Feature | Claude Code | Codex CLI | OpenCode |
|---------|-------------|-----------|----------|
| Provider | Anthropic | OpenAI | Various (OpenRouter, etc.) |
| Model | Claude 3.5/3.7 Sonnet | GPT-4o, o3 | Configurable |
| Auth | `claude login` | `codex login` | `opencode auth login` |
| One-shot | `claude -p "prompt"` | `codex "prompt"` | `opencode run "prompt"` |
| Interactive | `claude` REPL | `codex` REPL | `opencode` REPL |
| PR workflow | Built-in | Built-in | Built-in |
| Cost | Anthropic API | OpenAI API | Varies by provider |

## Claude Code

### Installation
```bash
npm install -g @anthropic-ai/claude-code
```

### Auth
```bash
claude login
# Opens browser for OAuth
```

### One-shot Tasks
```bash
claude -p "Implement a function that sorts a list of objects by a key"
```

### Interactive Session
```bash
claude
# Enters REPL mode for multi-turn coding
```

### PR Workflow
```bash
claude pr create --title "feat: add sorting utility"
claude pr review
```

### Best Practices
- Use `-p` for single tasks, REPL for complex multi-step work
- Always review generated code before committing
- Use `--dry-run` to preview changes
- Set `CLAUDE_CODE_DEBUG=1` for verbose output

## Codex CLI

### Installation
```bash
npm install -g @openai/codex
```

### Auth
```bash
codex login
# Opens browser for OpenAI OAuth
```

### One-shot Tasks
```bash
codex "Refactor this function to use async/await"
```

### Interactive Session
```bash
codex
# Enters REPL mode
```

### PR Workflow
```bash
codex pr create --title "refactor: async patterns"
codex pr review
```

### Best Practices
- Use `codex --model gpt-4o` for complex tasks
- Set `OPENAI_API_KEY` for non-interactive use
- Use `--context` to include additional files
- Review diffs with `codex diff`

## OpenCode

### Installation
```bash
npm install -g @opencode/opencode
# or
pip install opencode
```

### Auth
```bash
opencode auth login
# Supports multiple providers (OpenRouter, etc.)
```

### One-shot Tasks
```bash
opencode run "Add error handling to the API endpoints"
```

### Interactive Session
```bash
opencode
# Enters REPL mode
```

### PR Workflow
```bash
opencode pr create --title "feat: error handling"
opencode pr review
```

### Best Practices
- Configure provider in `~/.opencode/config.yaml`
- Use `--provider openrouter` for model flexibility
- Set `OPENCODE_API_KEY` for non-interactive use
- Review with `opencode review --diff`

## Common Workflows

### Feature Development
1. Start interactive session: `claude` / `codex` / `opencode`
2. Describe the feature with context
3. Review generated code
4. Run tests
5. Commit with conventional commit message

### PR Review
1. Run agent review: `claude pr review` / `codex pr review` / `opencode pr review`
2. Review agent comments
3. Address feedback
4. Merge when CI passes

### Code Exploration
1. Start REPL: `claude` / `codex` / `opencode`
2. Ask about codebase structure
3. Request specific file analysis
4. Get explanations of complex logic

## Security Considerations

- Never paste secrets into agent prompts
- Review all generated code before execution
- Use `--dry-run` for destructive operations
- Enable audit logging when available

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Auth expired | Re-run `login` command |
| Rate limited | Check API dashboard, upgrade tier |
| Model unavailable | Switch provider or model |
| Context too long | Use `--context` to limit files |

## Related Skills

- `kanban-codex-lane` — For Kanban + Codex integration workflows
- `hermes-agent` — For Hermes-specific agent configuration
- `github-pr-workflow` — For PR lifecycle management