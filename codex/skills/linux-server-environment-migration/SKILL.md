---
name: linux-server-environment-migration
description: Migrate a Linux development environment (shell config, dev tools, conda, CUDA) between servers via SSH — inventory,
  transfer, adapt paths, test.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Linux Server Environment Migration

Migrate shell config, development tools, conda, and CUDA between Linux servers via SSH.

## Workflow

### 1. SSH Connectivity Check

```bash
# Confirm SSH config
cat ~/.ssh/config | grep -A 5 '^Host source'
cat ~/.ssh/config | grep -A 5 '^Host target'

# Test reachability
ssh source "hostname; uname -a"
ssh target "hostname; uname -a"
```

### 2. Source Server Inventory

Before copying anything, inspect the source server:

```bash
ssh source "
  echo '=== HOME ==='; echo \$HOME
  echo '=== SHELL ==='; echo \$SHELL; ls -la ~/.zshrc
  echo '=== ZSH ==='; ls ~/.oh-my-zsh/custom/themes/; ls ~/.oh-my-zsh/custom/plugins/ 2>/dev/null
  echo '=== CUSTOM CONFIG ==='; ls ~/.config/zsh/custom/ 2>/dev/null
  echo '=== CONDA ==='; which conda 2>/dev/null || echo 'no conda'
  echo '=== TOOLS ==='; which lsd fzf nvim 2>/dev/null
  echo '=== CUDA ==='; which nvcc 2>/dev/null; ls /usr/local/cuda-* 2>/dev/null
  echo '=== APPS ==='; ls ~/apps/ 2>/dev/null
"
```

Extract the full `.zshrc` content for analysis:

```bash
ssh source "cat ~/.zshrc"
```

### 3. Target Server Inventory

```bash
ssh target "
  echo '=== HOME ==='; echo \$HOME
  echo '=== SHELL ==='; echo \$SHELL
  echo '=== CONDA ==='; which conda 2>/dev/null || echo 'no conda'
  echo '=== CUDA ==='; which nvcc 2>/dev/null || echo 'no nvcc'
  echo '=== TOOLS ==='; which lsd fzf 2>/dev/null
"
```

### 4. Path Difference Analysis

**Compare home directories** — this is the most critical adaptation. All hardcoded paths in `.zshrc` and custom configs need adjustment.

Examples of paths that typically differ:
- `export PATH="$HOME/bin:..."`
- conda/mamba initialization paths
- CUDA paths (`/usr/local/cuda`, `/usr/local/cuda-N`)
- Custom script/config paths

**TLDP** (Tilde vs Literal Dir Pattern): prefer `$HOME` or `~` over hardcoded absolute paths in the target `.zshrc` to minimize adaptation work.

### 5. Install Prerequisites on Target

```bash
# zsh + oh-my-zsh
ssh target "sudo apt update && sudo apt install -y zsh"
ssh target 'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
ssh target "chsh -s \$(which zsh)"   # optional, requires re-login
```

### 6. Clone zsh Plugins & Theme

```bash
ssh target "
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k
  git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
  git clone --depth=1 https://github.com/zdharma-continuum/fast-syntax-highlighting ~/.oh-my-zsh/custom/plugins/fast-syntax-highlighting
"
```

### 7. Install Local Tools (no sudo)

For `~/.local/bin` tools when sudo is unavailable:

```bash
# fzf
ssh target "git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install --no-bash --no-fish --key-bindings --completion --no-update-rc"

# lsd (prebuilt musl binary)
ssh target "
  curl -sL https://github.com/lsd-rs/lsd/releases/download/v1.1.5/lsd-v1.1.5-x86_64-unknown-linux-musl.tar.gz | tar xz -C /tmp/
  cp /tmp/lsd-v1.1.5-x86_64-unknown-linux-musl/lsd ~/.local/bin/
  chmod +x ~/.local/bin/lsd
"
```

### 8. Transfer Custom Config Files via SCP

```bash
# Custom zsh config
scp source:~/.config/zsh/custom/aliases.zsh target:~/.config/zsh/custom/
scp source:~/.config/zsh/custom/env.zsh target:~/.config/zsh/custom/
scp source:~/.config/zsh/custom/script.zsh target:~/.config/zsh/custom/

# p10k theme config
scp source:~/.p10k.zsh target:~/.p10k.zsh
```

### 9. Write Adapted .zshrc

Key adaptations:
- Replace hardcoded home paths with `$HOME`
- Comment out conda/mamba blocks if conda not yet installed
- Comment out source-specific aliases (claude, etc.)
- Use the **`for` loop pattern** for sourcing custom files

**CRITICAL — zsh source pitfall**: In zsh, `source file1 file2 file3` only sources **file1**, treating the rest as positional args. **Never use `source ~/.config/*.zsh`** with a glob expanding to multiple files. Always use:

```zsh
for f in $HOME/.config/zsh/custom/*.zsh; do source "$f"; done
```

(This is different from bash, where `source file1 file2` would source file1 and pass file2 as $1 — zsh is the same as bash in that respect, but both differ from the naive expectation that `source` with multiple file args sources all of them)

### 10. Install Miniconda

```bash
ssh target "mkdir -p ~/apps && cd /tmp && \
  curl -sL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh && \
  bash miniconda.sh -b -p ~/apps/miniconda3 && \
  rm miniconda.sh"
```

After install, uncomment the conda/mamba init blocks in `.zshrc`.

### 11. Verify CUDA Environment

```bash
ssh target "
  echo '=== nvcc ==='; nvcc --version | grep release
  echo '=== CUDA_HOME ==='; echo \$CUDA_HOME
  echo '=== tools ==='; which ncu cuobjdump compute-sanitizer 2>&1
  echo '=== GPU ==='; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
"
```

Default CUDA aliases to add:
```zsh
alias gpu="nvidia-smi"
alias gpulog="nvidia-smi -l 1"
alias gpuselect="nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv"
alias nvccv="nvcc --version | tail -1"
alias cuversion="nvcc --version | grep release"
```

### 12. Integration Test

After everything is configured, run a comprehensive test in a sub-shell:

```bash
ssh target 'zsh -c "
export WEZTERM_EXECUTING=
source ~/.zshrc 2>&1 >/dev/null
echo \"=== Tools ===\"
which lsd && lsd --version
which fzf && fzf --version
echo \"=== Conda ===\"
which conda && conda --version
echo \"=== Plugins ===\"
echo \"plugins=\${plugins}\"
echo \"=== Theme ===\"
echo \"ZSH_THEME=\$ZSH_THEME\"
echo \"=== CUDA ===\"
nvcc --version | grep release
"'
```

## Pitfalls

1. **zsh multi-file source** (see step 9) — `source $HOME/custom/*.zsh` only sources the first file. Always use a `for` loop.
2. **Non-interactive alias testing** — zsh does NOT expand aliases in `zsh -c` or `zsh -f` (non-interactive mode). Test aliases in `zsh -i` or use `alias name` to check definition.
3. **`which` vs `type` in zsh** — `which` is a builtin in zsh and may behave differently from the external binary. `type -a` is more reliable.
4. **WezTerm guard** — if `.zshrc` starts with `if [[ -n "$WEZTERM_EXECUTING" ]]; then return; fi`, sourcing it in a test sub-shell with `WEZTERM_EXECUTING=` (empty string) triggers the guard. Set `export WEZTERM_EXECUTING=` explicitly in tests.
5. **sed uncommenting** — when uncommenting conda/mamba blocks with `sed '/^# >>> conda/,/^# <<< conda/s/^# //'`, the `# >>> ... >>>` and `# <<< ... <<<` marker lines lose their `#` prefix and become syntax errors. Fix them back with separate sed commands.
6. **oh-my-zsh CWD** — oh-my-zsh.sh does `cd $ZSH` to check git revision. Ensure oh-my-zsh is a real git clone (not a tarball extraction) or this step silently fails.
7. **SSH key passphrase** — repeated SSH calls time out if the key requires a passphrase. Prefer keys without passphrase for automated migration.

## Verification

Run a full end-to-end check after each major step (tools, config, shell init, conda, CUDA). Use `zsh -c "export WEZTERM_EXECUTING=; source ~/.zshrc; ..."` as the standard test harness.