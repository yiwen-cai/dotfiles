---
name: github-operations
description: 'GitHub operations umbrella: authentication, repository management, issues, PR lifecycle, code review, CI, releases,
  and API fallbacks via gh/git/curl.'
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# GitHub Operations

Use this class-level umbrella for GitHub work: authentication, repository lifecycle, issues, pull requests, code review, CI checks, branch protection, secrets, releases, and API fallback workflows. Load this instead of separate narrow GitHub skills.

## Core operating pattern

1. Detect auth/tooling once.
2. Extract `owner/repo` from the remote if inside a repo.
3. Prefer `gh` when authenticated; otherwise use `git` plus GitHub REST/GraphQL with `GITHUB_TOKEN`.
4. Use file tools for code edits and `git` for repository state/history.
5. Verify side effects by reading back GitHub state (`gh pr view`, API response, checks, issue state, release listing).

```bash
git --version
gh --version 2>/dev/null || echo "gh not installed"
gh auth status 2>/dev/null || echo "gh not authenticated"

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  AUTH=gh
else
  AUTH=curl
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q '^GITHUB_TOKEN=' ~/.hermes/.env; then
      export GITHUB_TOKEN=$(grep '^GITHUB_TOKEN=' ~/.hermes/.env | head -1 | cut -d= -f2- | tr -d '\r\n')
    elif grep -q 'github.com' ~/.git-credentials 2>/dev/null; then
      export GITHUB_TOKEN=$(grep 'github.com' ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

if git remote get-url origin >/dev/null 2>&1; then
  REMOTE_URL=$(git remote get-url origin)
  OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
  OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
  REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
fi
```

## Authentication

Use `gh auth status` first. If unavailable, use PAT/SSH.

- PAT scopes commonly needed: `repo`, `workflow`, `read:org` for org repos.
- `gh auth login` is simplest on desktops; `echo "$TOKEN" | gh auth login --with-token && gh auth setup-git` is best headless.
- Git-only fallback: `git config --global credential.helper store`, then use the PAT as the HTTPS password.
- SSH fallback: generate ed25519 key, add public key to GitHub, test `ssh -T git@github.com`.

Troubleshooting: password auth is disabled; stale cached credentials need `git credential reject`; Copilot tokens are not GitHub API tokens.

## Repository management

Common tasks:

```bash
# clone
gh repo clone owner/repo || git clone https://github.com/owner/repo.git

# create repo with gh
gh repo create my-project --private --source . --push

# create repo with REST
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user/repos \
  -d '{"name":"my-project","private":true}'

# fork and sync
gh repo fork owner/repo --clone
git fetch upstream && git checkout main && git merge upstream/main && git push origin main

# inspect/edit
gh repo view owner/repo
gh repo edit --enable-issues=true --enable-auto-merge
```

Branch protection, Actions secrets, releases, workflow runs, and gists are all repository-management work. Prefer `gh secret set` for secrets because REST requires public-key encryption.

## Issues and triage

Use for creating, searching, labeling, assigning, closing, and commenting on issues.

```bash
gh issue list --state open --label bug
gh issue view 42
gh issue create --title "Login redirect ignores ?next=" --body-file issue.md --label bug

gh issue edit 42 --add-label "priority:high" --add-assignee @me
gh issue comment 42 --body "Investigated; root cause is auth middleware."
gh issue close 42 --reason completed
```

REST fallback endpoints: `GET/POST /repos/{owner}/{repo}/issues`, `POST /issues/{n}/labels`, `POST /issues/{n}/assignees`, `POST /issues/{n}/comments`, `PATCH /issues/{n}`.

Triage loop: list untriaged → read details → categorize → label/priority → assign → comment with decision.

## PR lifecycle

```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b feat/short-description
# edit files
git add <files>
git commit -m "feat: concise summary"
git push -u origin HEAD

gh pr create --title "feat: concise summary" --body-file pr.md
gh pr checks --watch
gh pr merge --squash --delete-branch
```

REST fallback: `POST /pulls` to create, `GET /commits/{sha}/status` and `GET /commits/{sha}/check-runs` for checks, `PUT /pulls/{n}/merge` to merge, GraphQL for auto-merge.

CI auto-fix loop: check status → read failed logs (`gh run view --log-failed` or logs ZIP) → understand → patch/write files → commit/push → wait and re-check. Stop after bounded attempts if still failing.

## Code review

Use for local pre-push review or reviewing a PR.

Local pre-push:

```bash
git diff main...HEAD --stat
git diff main...HEAD --name-only
git diff main...HEAD
```

Review checklist: correctness, security, code quality, testing, performance, documentation. Read full changed files when diff context is insufficient.

PR review flow:

```bash
gh pr view 123
gh pr diff 123 --name-only
gh pr checks 123
gh pr checkout 123
# run tests/lints where practical
gh pr review 123 --comment --body "..."
# or --approve / --request-changes
```

Structured output:

```markdown
## Code Review Summary
### Critical
### Warnings
### Suggestions
### Looks Good
```

Inline REST reviews use `POST /repos/{owner}/{repo}/pulls/{n}/reviews` with `commit_id`, `event`, `body`, and `comments`.

## Templates and references

This umbrella carries migrated support files from the former narrow GitHub skills:

- `scripts/gh-env.sh` — auth/repo environment bootstrap.
- `references/review-output-template.md` — formal review summary template.
- `references/ci-troubleshooting.md` — CI failure diagnosis patterns.
- `references/conventional-commits.md` — commit message guidance.
- `references/github-api-cheatsheet.md` — REST endpoint crib sheet.
- `templates/bug-report.md`, `templates/feature-request.md`, `templates/pr-body-bugfix.md`, `templates/pr-body-feature.md` — starter issue/PR bodies.