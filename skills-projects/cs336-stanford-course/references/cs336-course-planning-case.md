# CS336 Course Planning Case

## Context

User wanted to self-study Stanford CS336: Language Modeling from Scratch. They had:
- H100 access / sufficient compute
- Some related ML knowledge
- Limited programming experience
- 4-5 hours available per day

Initial plan over-focused on assignments/environment. User corrected that lecture learning must be considered first.

## Planning Outcome

Recommended duration: 8-10 weeks, not 1 month.

Rationale:
- CS336 is implementation-heavy and officially 5 units.
- Assignment 1 alone requires tokenizer, Transformer, optimizer, and training loop.
- Assignment 2 adds profiling, Triton FlashAttention2, and distributed training.
- Limited programming experience means debugging time dominates even with strong GPU access.

## Workflow Lessons

### Lecture-first correction

For course plans, do not start Day 1 with only setup and assignment repo work. Include lecture/content learning as a first-class block.

Correct Day 1 shape:
1. Lecture 1 / course content: 1.5-2h
2. Environment setup: 1-1.5h
3. Assignment structure / tests: 1h
4. Notes: 0.5h

### Current-topic before next lecture

When the user asked on Day 2 whether to watch Lecture 2, the correct answer was: not formally yet. Finish consolidating Lecture 1 + tokenizer first; optionally preview only PyTorch/einops parts if ahead.

Rule:
- If current assignment depends on Lecture N and the user has not consolidated it, schedule review, tests, and toy examples before moving to Lecture N+1.
- Allow a light preview of the next lecture only when the current day's required work is complete.

## Day 2 Example

Day 2 focus:
- 1.5h PyTorch basics: tensors, autograd, nn.Module, optimizer loop
- 1h reread Lecture 1 tokenizer code
- 1h read Assignment 1 tokenizer tests/adapters
- 1h hand-simulate BPE on a toy corpus
- 0.5h write notes

Avoid:
- Jumping into full tokenizer implementation too early
- Starting Transformer/model sections
- Deep-diving Lecture 2 resource accounting before tokenizer is stable

## Remote Execution Environment Update

Later the user clarified that **all CS336 code runs on the remote lab server**, not on the local machine. Future CS336 planning or coding guidance should assume:

- Code execution host: `lab` (`10.160.4.102`)
- Remote user: `caiyiwen`
- Project root: `/public/home/caiyiwen/code/cs336`
- GPU experiments: 8× H100 on lab
- Local machine/wiki: planning, reading notes, and progress records; not the default execution location
- Long-running training/profile jobs: use tmux on lab

When such an execution-environment correction appears during course planning, update the wiki in all three places rather than creating a tiny standalone page:
1. Main course concept page (`concepts/<course>.md`) — add an “execution environment” section.
2. Master learning plan (`queries/<course>-learning-plan.md`) — add a “runtime/environment principles” section.
3. Current daily plan (`queries/<course>-day<N>-plan.md`) — add concrete commands and warn not to run locally.
4. Update `index.md` timestamp and append to `log.md`; page count stays unchanged if no new page is created.

