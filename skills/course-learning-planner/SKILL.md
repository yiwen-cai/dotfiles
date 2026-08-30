---
name: course-learning-planner
description: 'Use when helping users plan and execute structured learning for courses (online, university, self-study). Covers
  timeline design, daily task breakdown, lecture integration, assignment scheduling, and '
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Course Learning Planner

## CS336 model-side coaching references

When guiding CS336 Assignment 1 model-side work, consult:

- `references/cs336-model-components-tdd-coaching.md` — overall Stage 1-8 TDD map and TA-style boundary.
- `references/cs336-stage1-stage2-shape-pitfalls.md` — session-derived pitfalls for cross entropy target indexing, `get_batch`, `einops` patterns, and Day 6 Stage 2 ordering.

## CS336 Progress Sync Addendum

When the user asks to sync progress or update CS336 notes, update Markdown, the HTML companion, and llm_wiki together; verify timestamps and key headings. See `references/cs336-progress-sync-workflow.md` for the concrete checklist.

A structured approach to planning and executing course learning. This skill ensures that **lecture/content consumption is always the primary focus**, with environment setup, assignments, and implementation work treated as supporting activities.

## CS336 mode-specific guidance

When helping with CS336:

- Treat Stanford CS336 Spring 2026 as the authoritative lecture version unless the user explicitly says otherwise.
- Keep assignment implementation and verification tied to the user's current lab repository and public tests; lecture version and repo state can differ.
- Before writing lecture notes, verify the lecture row and material link from the official course page rather than relying on prior-year memory.
- See `references/cs336-lecture-source-workflow.md` for the concrete source-check workflow and the Lecture 4 pitfall.

## When to Use

- User asks to plan learning for a specific course
- User asks to create a study schedule or timeline
- User is starting a new course and needs day-by-day guidance
- User asks about pacing (how long will this take?)
- User asks for daily/weekly task breakdowns

**Don't use for:**
- One-off questions about a course topic (just answer directly)
- Already-completed courses (use session_search or wiki query instead)
- Pure research without a course structure

## Core Principle: Lecture First

**The most common mistake in learning planning is skipping the lecture/content phase and jumping straight to implementation.**

### Correct Order
1. **Lecture / Content** — Understand concepts, theory, algorithms
2. **Environment / Setup** — Prepare tools, download data, configure environment
3. **Implementation / Assignment** — Apply what was learned

### Why This Matters
- For users with limited programming experience, skipping lectures leads to copying code without understanding
- Lectures provide the mental model needed to debug implementation issues
- Assignments are designed to reinforce lecture content, not replace it

## Planning Workflow

### Step 1: Gather Course Information

Before creating any plan, collect:
- Course name, institution, semester/year
- Official website / syllabus URL
- Lecture schedule (topics, dates, materials)
- Assignment list (descriptions, deadlines)
- Prerequisites
- Recommended workload (hours per week)

**Tools:**
- `browser_navigate` + `browser_snapshot` for course websites
- `curl` for syllabus PDFs or markdown files
- `search_files` if course materials are already local

### Step 2: Assess User Context

| Factor | Why It Matters |
|--------|---------------|
| Daily available time | Determines total duration |
| Programming experience | Affects implementation speed |
| Hardware (GPU/CPU) | Determines what can be run |
| Execution location | Determines whether examples/commands should target local shell, SSH, cloud notebooks, or a cluster |
| Prior knowledge | Determines review needs |
| Deadline pressure | Affects depth vs breadth tradeoff |

**Ask if unclear:** Don't guess about GPU availability, daily time commitment, or where code should run (local vs remote server vs cloud notebook).

### Step 3: Design Timeline

**Rule of thumb:**
- University courses: 1 week of course content ≈ 1-2 weeks of self-study time
- Implementation-heavy courses: multiply by 1.5-2x
- Theory-heavy courses: multiply by 1-1.5x

**Structure:**
- Break into phases aligned with course modules
- Each phase has a clear milestone (e.g., "Complete Assignment 1")
- Include buffer days for debugging and review

### Step 4: Daily Task Design

**Every day must include lecture/content time.**

**Template for a 4-5 hour day:**

| Time | Activity | Purpose |
|------|----------|---------|
| 1.5-2h | Lecture / Reading | Conceptual understanding |
| 1-1.5h | Environment / Setup | Prepare for implementation |
| 1-2h | Implementation / Assignment | Apply concepts |
| 0.5h | Notes / Review | Solidify learning |

**For days with heavy implementation:**
- Still allocate at least 30-60 minutes for reviewing relevant lecture content
- Don't let implementation crowd out conceptual learning

### Phase Transition Workflow

When one assignment/milestone is complete and the next hasn't started, standard "implementation day" structure doesn't fit. Use the **phase transition day** pattern instead:

| Part | Time | Activity | Purpose |
|------|-----:|----------|---------|
| Part 0 | 15min | Environment & state check | Confirm previous phase actually done, stash/clean working tree |
| Part 1 | 30min | **Cleanup** of completed work | ruff format, full regression test, git diff scope check |
| Part 2 | 90min | **Lecture** — foundational topic for next phase | Watch the first lecture of the *next* phase before the directly implementable one (e.g., GPU architecture before Triton) |
| Part 3 | 45min | **Preview** — next assignment scope | Read handout, repo structure, test files — just-in-time, no deep implementation |
| Part 4 | 30min | Notes & next-phase rough schedule | Sync docs, decide next day's direction |

**Why this ordering matters:**
- Cleanup first: prevents unfinished work from leaking into new phase
- Foundational lecture before implementable lecture: builds mental model for new tools (e.g., GPU occupancy/roofline before Triton kernel programming)
- Preview last: enough context to plan Day 2 of new phase, but not enough to start coding prematurely

**Signals that triggered a transition day:**
- All public tests for the current assignment pass
- The user's daily notes say "next milestone reached"
- The next assignment requires different tools, paradigms, or hardware knowledge

### Step 5: Create Deliverables

1. **Master plan document** — Overview, timeline, milestones
2. **Weekly breakdowns** — Specific tasks per week
3. **Day 1 plan** — Detailed step-by-step for the first day
4. **Progress tracking** — Checklists, milestones, review points
5. **Dual-format implementation notes** — When transitioning from planning to implementation, create both:
   - Agent-readable `.md` — structured sections, tables, code blocks for the AI to load as context
   - Human-readable `.html` — dark-themed, well-formatted, self-contained reference the user can browse

## Lecture Integration Checklist

For every assignment or implementation task, verify:

- [ ] Which lecture(s) cover the prerequisite concepts?
- [ ] Has the user watched/read those lectures?
- [ ] Are there lecture code examples to study before implementing?
- [ ] Does the assignment reference specific lecture content?
- [ ] Has the current lecture been consolidated with notes/tests/toy examples before moving to the next lecture?

**If no lecture covers the topic:**
- Note this as a gap
- Suggest supplementary resources
- Adjust timeline to account for self-study

**If the user asks whether to move to the next lecture:**
- First check whether the current lecture's assignment-facing concepts are stable.
- If not stable, schedule review, test reading, and a toy/manual example before advancing.
- If ahead of schedule, allow a light preview of the next lecture, but avoid deep-diving unrelated later material.

**Case references:**
- `references/cs336-course-planning-case.md` captures the CS336 planning correction and daily wiki update pattern.
- `references/cs336-assignment-interface-reading.md` captures a TA-safe workflow for reading CS336 public tests/adapters and summarizing assignment contracts without writing solution code.
- `references/cs336-tokenizer-tdd-coaching.md` captures TA-safe TDD coaching stages, invariants, and common failure patterns for CS336 Assignment 1 tokenizer encode/decode work.
- `references/handout-test-tdd-workflow.md` captures the full workflow from extracting handout PDF rules, aligning them with public tests, designing data structures, and building a stage-by-stage TDD plan before writing any implementation code. Use this when a course assignment provides both a handout and a test suite.
- `references/cs336-ta-safe-tokenizer-guidance.md` captures how to guide CS336 Assignment 1 tokenizer implementation without directly editing core solution code, including the adapter/import boundary and common byte-vs-bytes debugging pitfall.
- `references/cs336-train-bpe-tdd-coaching.md` captures TA-safe TDD coaching for CS336 `train_bpe`: initial vocab, pretoken/pair counters, tie-breaking, single-merge invariants, debug outputs, and common snippet-review pitfalls.
- `references/cs336-model-components-tdd-coaching.md` captures the post-tokenizer Day 5 transition into CS336 Assignment 1 model components: Lecture 2/resource-accounting first, public test/adapter maps, TA-safe boundaries, and a staged TDD order from pure functions/basic layers to attention, Transformer block, and LM forward.
- `references/cs336-tensor-shape-coaching.md` captures CS336 model-side tensor-shape coaching details: `jaxtyping` semantics, broadcasting pitfalls, `einsum`/`einops` usage, stable softmax/cross-entropy shape checks, and `get_batch` dtype/device reminders.
- `references/cs336-model-side-shape-reasoning.md` captures CS336 model-side shape reasoning guidance: jaxtyping annotations, PyTorch broadcasting limits, `einsum`/`einops` usage, and Stage 1 numerical utility invariants for softmax/cross-entropy/get_batch.
- `references/cs336-progress-sync-workflow.md` captures the required CS336 progress-sync workflow: update Markdown, HTML companion, and llm_wiki together whenever the user asks to sync progress or update notes.
- `references/cs336-tokenizer-full-implementation-reference.md` captures the complete tokenizer implementation state from Week 3 (all 27 tests passed): data structures, design decisions, tie-breaking, incremental pair_count optimization, and common pitfalls.

## CS336 model-side coaching

When coaching CS336 Assignment 1 model components, load `references/cs336-model-components-tdd-coaching.md`. It captures the TA-style boundary, staged TDD order, and durable pitfalls discovered while guiding `SwiGLU` and `RoPE` implementations, including the `w1`/`w3` SiLU branch issue and RoPE device/broadcast/interleaving checks.

## Common Pitfalls

1. **Lecture skipped, implementation started immediately**
   - Fix: Always schedule lecture time before implementation time
   - Fix: Ask "Have you watched the lecture for this topic?"

2. **Moving to the next lecture before consolidating the current one**
   - Fix: Before advancing, verify the user can explain the current lecture's core algorithm/concepts in their own words
   - Fix: For implementation-heavy courses, add test-reading and toy/manual examples before the next lecture
   - Fix: Permit only a light preview of the next lecture if required work is already complete

3. **Environment setup treated as Day 1 only**
   - Fix: Environment issues will recur; schedule setup time throughout
   - Fix: Some courses need environment changes per assignment

4. **Execution location assumed incorrectly**
   - Fix: If the user says code runs on a remote server/lab/cloud notebook, update all commands and daily tasks to target that environment
   - Fix: Record environment principles in the course concept page, master plan, and current daily plan if a wiki is being maintained
   - Fix: Distinguish local note/wiki work from remote code execution

5. **Timeline too aggressive**
   - Fix: University courses are designed for full-time students with TAs
   - Fix: Self-study needs 1.5-2x the official duration
   - Fix: Implementation-heavy courses (OS, compilers, ML systems) need even more time

6. **No review/buffer days**
   - Fix: Schedule at least 1 buffer day per week
   - Fix: Debugging always takes longer than expected

7. **Notes not encouraged**
   - Fix: Every day should end with note-taking
   - Fix: Notes should connect lectures to implementations
   - Fix: For implementation-heavy courses, also create dual-format notes (agent `.md` + human `.html`) at the transition from planning to coding

8. **Workspace directory assumed incorrectly**
   - Fix: Always verify the actual workspace directory with the user before creating files
   - Fix: Save the correct path to memory to avoid re-creating files in the wrong location
   - Fix: CS336 example — `~/Documents/code/cs336/`, not `~/code/cs336/`

9. **Coursework academic-integrity rules discovered too late**
   - Fix: Before any assignment coding/debugging on a course repo, read repository guidance files (`AGENTS.md`, `CLAUDE.md`, `README`, handout policy) before editing or running tests.
   - Fix: If repo policy says AI should act as a TA and not implement solutions, switch to Socratic/TDD coaching: explain concepts, ask the user to write code, review snippets, interpret errors, and suggest invariants/tests without editing graded files or providing complete code.
   - Fix: For CS336 specifically, treat tokenizer/model/optimizer/training-loop implementations as core assignment components; provide high-level algorithms, debugging checklists, and code review only.

10. **Skipping foundational lecture when transitioning phases**
    - Fix: When starting a new phase (e.g., implementation → systems), watch the foundational lecture first (e.g., GPU architecture) before the directly implementable one (e.g., Triton kernel programming)
    - Fix: The foundational lecture provides the mental model (roofline, occupancy, memory hierarchy) needed to understand the tools the next assignment uses
    - Fix: Check the course schedule to identify which lecture is foundational vs. implementable for the next phase

## Verification Checklist

- [ ] Plan includes explicit lecture/content time for every phase
- [ ] Timeline accounts for user's daily availability and experience level
- [ ] Assignments are mapped to their prerequisite lectures
- [ ] Buffer time is included (at least 20% of total)
- [ ] Day 1 plan is detailed enough to start immediately
- [ ] Progress tracking mechanism is defined
- [ ] User's hardware constraints are considered
- [ ] User's execution location is explicit, and commands match it

## Example Structure

```
Course: CS336 Language Modeling from Scratch
Duration: 8 weeks
Daily: 4-5 hours

Phase 1 (Week 1-3): Basics
- Week 1: Lecture 1-2, Environment, Start tokenizer
- Week 2: Lecture 3-4, Transformer architecture
- Week 3: Lecture 5, Training loop, Assignment 1 complete

Phase 2 (Week 4-6): Systems
- Week 4: Lecture 6, Triton, GPU profiling
- Week 5: FlashAttention implementation
- Week 6: Distributed training, Assignment 2 complete

[...]
```

## Related

- [[planning-with-files]] — File-based planning for complex projects
- [[writing-plans]] — General implementation planning
- [[course-study-planning]] — Legacy course study planning (archived, content merged here)