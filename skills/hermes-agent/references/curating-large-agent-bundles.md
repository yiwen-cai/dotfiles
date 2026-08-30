# Curating large external agent/skill bundles

When a repository ships hundreds of AI-tool agents/skills, installing everything is often counterproductive. Prefer a small allowlist matched to the user's actual work profile.

Session pattern that worked:

1. Inspect available agent names by category from source directories.
2. Build a stable allowlist of production-relevant agent basenames.
3. Add a shell helper such as `is_recommended_agent()` near the top-level constants.
4. In every per-tool installer loop, filter on the artifact basename before copying:
   - Markdown agents: `is_recommended_agent "$(basename "$f" .md)" || continue`
   - Cursor rules: `is_recommended_agent "$(basename "$f" .mdc)" || continue`
   - Codex TOML agents: `is_recommended_agent "$(basename "$f" .toml)" || continue`
   - JSON agent configs: `is_recommended_agent "$(basename "$f" .json)" || continue`
   - Skill directories: derive `name="$(basename "$d")"` or `skillname="$(basename "$skilldir")"`, then filter before `mkdir`/`cp`.
5. Leave single-file convention installers alone if they do not copy agents one-by-one, unless the user explicitly wants to disable them.
6. Update help text so users know the script is allowlist-filtered by default.
7. Verify with:
   - `bash -n scripts/install.sh`
   - a small script that parses the allowlist and checks each item exists in source directories.

Example recommended allowlist for a user focused on LLM/deep learning, Python experiments, C++/systems, remote GPU work, model serving, and agent engineering:

```text
engineering-ai-engineer
engineering-ai-data-remediation-engineer
engineering-autonomous-optimization-architect
engineering-backend-architect
engineering-code-reviewer
engineering-codebase-onboarding-engineer
engineering-data-engineer
engineering-database-optimizer
engineering-devops-automator
engineering-git-workflow-master
engineering-incident-response-commander
engineering-minimal-change-engineer
engineering-security-engineer
engineering-senior-developer
engineering-software-architect
engineering-sre
engineering-technical-writer
testing-api-tester
testing-performance-benchmarker
testing-reality-checker
testing-test-results-analyzer
specialized-model-qa
specialized-mcp-builder
specialized-workflow-architect
specialized-document-generator
lsp-index-engineer
prompt-engineer
technical-translator-agent
language-translator
academic-study-planner
data-consolidation-agent
project-management-experiment-tracker
```

Pitfalls:

- Different integrations use different file extensions and layouts; a filter added only to `.md` loops will miss `.mdc`, `.toml`, `.json`, and directory-based `SKILL.md` formats.
- Avoid filtering after `mkdir` to prevent creating empty directories for excluded agents.
- `--category` filters may still install too much when categories are broad, so use an agent-level allowlist for production pruning.
- Verify allowlist items exist in source, not only in generated `integrations/`, because integrations may be stale or missing before conversion.
