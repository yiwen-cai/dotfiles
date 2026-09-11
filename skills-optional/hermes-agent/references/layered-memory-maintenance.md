# Layered Memory Maintenance

## Purpose

Use this reference when cleaning, adding, or reviewing persistent memory for this user. The goal is to keep memory as an index and durable fact store, while keeping workflows in skills and session history in `session_search`.

## Layer Model

### Top Layer: Global Index

Store only broad routing information:

- Global response preferences.
- Stable long-term user context.
- Domain entry points.
- References to skills that hold procedures.

Example shape:

```text
CS336 index: default a800; assignment workflows live in cs336-stanford-course skill.
```

### Lower Layer: Local Stable Facts

Store compact, durable facts within a domain:

- Stable paths.
- Stable naming conventions.
- Long-lived environment conventions.
- User-specific presentation constraints.

Example shape:

```text
Weekly report index: save under ~/study/weekpaper; public wording for lab is "实验室 H100".
```

### Skill Layer: Procedures

Put these in skills, not memory:

- Multi-step workflows.
- Command templates.
- Debugging paths.
- Verification checklists.
- Reusable report/document templates.
- Tool-specific pitfalls and fixes.

### Session Search Layer: History

Use `session_search` for:

- What happened in a past task.
- Previous run outputs.
- PR numbers, issue numbers, commits, temporary branch names.
- One-off progress notes and transient decisions.

## Save Rules

Before adding a memory entry, classify it:

| Candidate | Destination |
|---|---|
| Durable user preference | `user` memory |
| Stable environment fact | `memory` memory |
| Workflow with 2+ steps | skill or skill reference file |
| Temporary task progress | session transcript only |
| Command sequence or checklist | skill |
| One-off run output | session transcript or task artifact |

## Rewrite Rules

When memory is near capacity or has duplicates:

1. Merge duplicate preferences into one top-level index entry.
2. Replace procedural detail with a pointer to the relevant skill.
3. Keep stable paths only if future routing depends on them.
4. Remove stale task progress and one-off results.
5. Avoid imperative phrasing that reads like a new instruction unless it truly is a persistent preference.

## Good Entry Shapes

```text
Global output index: Chinese output; translate external materials; LLM answers should be layered and rigorous.
```

```text
CS336 index: default a800; path /storage/.../assignment; workflows in cs336-stanford-course skill.
```

```text
Hermes WebUI index: no auto-scroll; implementation/debug workflows in hermes-agent references.
```

## Bad Entry Shapes

```text
Ran nsys profile today and generated min_train_ctx128.nsys-rep.
```

This belongs in session history or a task artifact.

```text
Always run this exact 12-line command before every CS336 task.
```

This belongs in a skill reference, not memory.

```text
Tool X does not work.
```

If durable, capture the fix or setup requirement in a troubleshooting skill instead.

## User-Specific Policy

The user explicitly wants this mechanism followed both for manual memory edits and for automatic cleanup. Treat memory as an index from global to local; treat skills as the home for concrete workflows.
