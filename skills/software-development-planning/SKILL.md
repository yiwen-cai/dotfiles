---
name: software-development-planning
description: Plan software development tasks — write markdown plans, file-based planning, and implementation plans with bite-sized
  tasks.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Software Development Planning

Plan software development tasks with structured approaches. Covers plan mode, file-based planning, and implementation plan writing.

## When to Use

- User wants a plan instead of immediate execution
- Complex task requiring 5+ tool calls needs organization
- Breaking down a feature into bite-sized tasks
- Delegating to subagents with clear instructions
- Tracking progress across multiple sessions

## Three Planning Modes

| Mode | Use Case | Output |
|------|----------|--------|
| **Plan Mode** | Quick planning, no execution | `.hermes/plans/YYYY-MM-DD_HHMMSS-{slug}.md` |
| **File-Based Planning** | Complex multi-step projects | `task_plan.md`, `findings.md`, `progress.md` |
| **Implementation Plans** | Detailed task breakdowns | `docs/plans/YYYY-MM-DD-feature-name.md` |

## Plan Mode

For when the user wants a plan instead of execution for a single turn.

### Core Behavior
- Do not implement code
- Do not edit project files except the plan markdown
- Do not run mutating terminal commands
- Deliverable: markdown plan saved under `.hermes/plans/`

### Output Requirements
Include when relevant:
- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan
- Files likely to change
- Tests / validation
- Risks, tradeoffs, open questions

### Save Location
```
.hermes/plans/YYYY-MM-DD_HHMMSS-{slug}.md
```

## File-Based Planning

Manus-style persistent planning files for complex tasks.

### The Core Pattern
```
Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)
→ Anything important gets written to disk
```

### Three Files

| File | Purpose | When to Update |
|------|---------|----------------|
| `task_plan.md` | Phases, progress, decisions | After each phase |
| `findings.md` | Research, discoveries | After ANY discovery |
| `progress.md` | Session log, test results | Throughout session |

### Critical Rules
1. **Create Plan First** — never start complex tasks without `task_plan.md`
2. **The 2-Action Rule** — after every 2 view/browser/search ops, save findings
3. **Read Before Decide** — re-read plan before major decisions
4. **Update After Act** — mark phases complete, log errors
5. **Log ALL Errors** — build knowledge, prevent repetition
6. **Never Repeat Failures** — track attempts, mutate approach

### The 3-Strike Error Protocol
- Attempt 1: Diagnose & Fix
- Attempt 2: Alternative Approach
- Attempt 3: Broader Rethink
- After 3 failures: Escalate to user

## Implementation Plans

Comprehensive plans for feature development with exact file paths and code.

### Bite-Sized Task Granularity
**Each task = 2-5 minutes of focused work**

Every step is one action:
- "Write the failing test"
- "Run it to make sure it fails"
- "Implement minimal code to pass"
- "Run tests to verify pass"
- "Commit"

### Plan Document Structure

#### Header (Required)
```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence]
**Architecture:** [2-3 sentences]
**Tech Stack:** [Key technologies]
```

#### Task Structure
```markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67`
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**
```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test**
Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL

**Step 3: Write minimal implementation**
```python
def function(input):
    return expected
```

**Step 4: Verify pass**
Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**
```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

### Principles
- **DRY** — Don't Repeat Yourself
- **YAGNI** — You Aren't Gonna Need It
- **TDD** — Test-Driven Development (RED-GREEN-REFACTOR)
- **Frequent Commits** — commit after every task

### Writing Process
1. Understand requirements
2. Explore codebase
3. Design approach
4. Write tasks (in order: setup → core → edge cases → integration → cleanup)
5. Add complete details (exact paths, complete code, exact commands)
6. Review the plan
7. Save to `docs/plans/YYYY-MM-DD-feature-name.md`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Vague tasks | "Add authentication" → "Create User model with email field" |
| Incomplete code | Show complete copy-pasteable code |
| Missing verification | Include exact commands with expected output |
| Missing file paths | Use `src/models/user.py`, not "the model file" |
| Tasks too big | Break into 2-5 minute chunks |

## Related Skills

- `subagent-driven-development` — Execute plans via delegate_task
- `test-driven-development` — TDD workflow details
- `requesting-code-review` — Pre-commit review process