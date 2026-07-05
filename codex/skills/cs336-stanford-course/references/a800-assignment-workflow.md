# CS336 A800 Assignment Workflow

Use this reference when helping the user advance CS336 assignments on the remote `a800` host.

## Principle

The workflow is assignment-first. Start from the current assignment section, tests, handout requirements, and the user's implementation state. Only bring in lecture content when it is necessary for the current step.

## Remote Paths

- Local notes/repo root: `/Users/yiwencai/Documents/code/cs336`
- Remote assignment root: `/storage/caiyiwen/code/cs336/assignment`
- Assignment 1: `/storage/caiyiwen/code/cs336/assignment/assignment1-basics`
- Assignment 2: `/storage/caiyiwen/code/cs336/assignment/assignment2-systems`
- Remote host: `a800`
- Remote `uv`: `/storage/caiyiwen/.local/bin/uv`

## Command Pattern

Prefer commands of this form:

```bash
ssh a800 'export PATH=/storage/caiyiwen/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH; cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && uv run pytest -q'
```

When using local double quotes around an SSH command, escape remote `$PATH` as `\$PATH` so the local shell does not expand it prematurely.

## Current Assignment 2 Flow

For the profiling section, use this progression:

1. Verify the student's existing `cs336_systems/benchmark.py` with a small smoke run.
2. Query `nvidia-smi -L` and pin CS336 benchmarks to an A800 with `CUDA_VISIBLE_DEVICES`; do not assume GPU 0 is an A800, because newer Blackwell GPUs may appear first and the assignment PyTorch build may not support `sm_120`.
3. Ensure the benchmark supports the current required modes and reports real measured output.
4. Use `nsys` only after the benchmark works.
5. Generate a minimal trace first, then expand to `forward`, `backward`, and `train` mode comparisons.
6. Let trace observations decide what GPU/kernel lecture material to study next.

If CUDA init errors occur, first separate environment/driver state from code bugs: run a minimal PyTorch allocation probe under explicit `CUDA_VISIBLE_DEVICES`, compare with `nvidia-smi`, and inspect current `dmesg` only as time-sensitive evidence. Re-check after reboot or driver changes before presenting a root cause.

## A800 GitHub Setup

The user configured GitHub SSH access on `a800` using their GitHub account. HTTPS GitHub URLs are globally rewritten to SSH form, so normal `git fetch`, `git pull`, and `git push` should work without switching remotes manually.

## Reporting Wording

When writing advisor-facing weekly reports, describe the remote machine as `实验室 H100 服务器` unless the user explicitly asks to mention internal hostnames.