---
name: debugging-with-inspect
description: Debug Python and Node.js applications using inspect protocols — pdb, debugpy, and node-inspect for breakpoints,
  stepping, and remote debugging.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Debugging with Inspect Protocols

Debug Python and Node.js applications using built-in and remote debugging tools.

## When to Use

- A test fails and the traceback doesn't reveal why
- Need to step through code and watch values
- A long-running process misbehaves and can't be restarted
- Post-mortem analysis of a crash
- Debugging subprocesses or child processes

## Python Debugging

### Tools

| Tool | When | Best For |
|------|------|----------|
| `breakpoint()` | Local, interactive | Quick debugging, no setup |
| `python -m pdb` | Launch under debugger | No source edits needed |
| `debugpy` | Remote/headless | Long-lived processes, attach to running |
| `remote-pdb` | Terminal-friendly | Agent-friendly remote debugging |

### pdb Quick Reference

Inside `(Pdb)` prompt:

| Command | Action |
|---------|--------|
| `n` | Next line (step over) |
| `s` | Step into |
| `r` | Return from function |
| `c` | Continue |
| `l` | List source |
| `w` | Stack trace |
| `p expr` | Print expression |
| `pp expr` | Pretty-print |
| `interact` | Full Python REPL |
| `q` | Quit |

### Local Breakpoint
```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()  # Drops into pdb
    return result + y
```

### Remote with debugpy
```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()
```

Attach with VS Code `launch.json`:
```json
{
  "name": "Attach to Python",
  "type": "debugpy",
  "request": "attach",
  "connect": { "host": "127.0.0.1", "port": 5678 }
}
```

### remote-pdb (Agent-Friendly)
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
```

Connect: `nc 127.0.0.1 4444`

### pytest Debugging
```bash
# Drop to pdb on failure
pytest test.py --pdb -p no:xdist

# Trace from start
pytest test.py --trace -p no:xdist
```

### Common Pitfalls
1. **xdist conflict** — pdb doesn't work with pytest-xdist; use `-p no:xdist`
2. **CI hangs** — `breakpoint()` in non-TTY hangs; never commit it
3. **PYTHONBREAKPOINT=0** — check env if breakpoints don't hit
4. **Threads** — pdb only debugs current thread; use debugpy for multi-threaded

## Node.js Debugging

### Tools

| Tool | When | Best For |
|------|------|----------|
| `node inspect` | Built-in, zero install | Quick poking |
| `ndb` / CDP | Scriptable | Automation, non-interactive |
| `--inspect-brk` | Start with inspector | Debug from first line |
| `SIGUSR1` | Attach to running | Already-running processes |

### node inspect REPL

Launch:
```bash
node inspect script.js
node --inspect-brk script.js
```

Commands:

| Command | Action |
|---------|--------|
| `c` | Continue |
| `n` | Next |
| `s` | Step in |
| `o` | Step out |
| `sb('file.js', 42)` | Set breakpoint |
| `bt` | Backtrace |
| `repl` | JS REPL in current scope |
| `.exit` | Quit |

### Attach to Running Process
```bash
# Enable inspector on existing process
kill -SIGUSR1 <pid>

# Attach debugger
node inspect -p <pid>
```

### TypeScript with tsx
```bash
node --inspect-brk --import tsx script.ts
```

### CDP Scripting
```javascript
const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9229 });
  const { Debugger, Runtime } = client;
  
  Debugger.paused(async ({ callFrames }) => {
    const top = callFrames[0];
    console.log(`Paused at ${top.url}:${top.location.lineNumber}`);
    
    // Get local variables
    for (const scope of top.scopeChain) {
      if (scope.type === 'local') {
        const { result } = await Runtime.getProperties({
          objectId: scope.object.objectId
        });
        for (const p of result) {
          console.log(`  ${p.name} =`, p.value?.value);
        }
      }
    }
    
    await Debugger.resume();
  });
  
  await Runtime.enable();
  await Debugger.enable();
  await Debugger.setBreakpointByUrl({
    urlRegex: '.*app\\.tsx$',
    lineNumber: 119
  });
})();
```

### Common Pitfalls
1. **Wrong line numbers** — breakpoints hit emitted JS, not TS source
2. **Port collisions** — default 9229; use `--inspect=0` for random port
3. **Child processes** — `--inspect` on parent doesn't inspect children
4. **Background kills** — Ctrl+C out of debugger leaves target paused

## Cross-Language Tips

### Choosing the Right Tool

| Scenario | Python | Node.js |
|----------|--------|---------|
| Quick local debug | `breakpoint()` | `node inspect` |
| Long-lived process | `debugpy` / `remote-pdb` | `SIGUSR1` + attach |
| IDE integration | `debugpy` | `--inspect` + Chrome DevTools |
| Terminal/agent | `remote-pdb` | `node inspect` |
| Post-mortem | `pdb.post_mortem()` | `--inspect-brk` + `p`ause |

### Verification Checklist
- [ ] Debugger connects successfully
- [ ] First breakpoint hits
- [ ] Stack trace shows expected frames
- [ ] Variables are inspectable
- [ ] Can step through code
- [ ] No stray breakpoints left in committed code

## Related Skills

- `systematic-debugging` — 4-phase root cause debugging
- `python-debugpy` — Python-specific debugging (archived)
- `node-inspect-debugger` — Node.js-specific debugging (archived)
- `engineering-code-reviewer` — Code review for catching bugs early