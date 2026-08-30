# Session Example: H100 → A800 Shell + CUDA Migration

## Server Layout

| Role | SSH Alias | Hostname/IP | User | Home Directory |
|------|-----------|-------------|------|----------------|
| Source (H100) | `lab` | 10.160.4.102 | caiyiwen | `/public/home/caiyiwen` |
| Target (A800) | `a800` | 10.160.4.104 | caiyiwen | `/storage/caiyiwen` |

Both use the same SSH key (`~/.ssh/id_ed25519`).

## Source Inventory

- Shell: zsh + oh-my-zsh + powerlevel10k
- Plugins: git, jsontools, z, zsh-autosuggestions, fast-syntax-highlighting
- Custom config: `~/.config/zsh/custom/` with aliases.zsh, env.zsh, script.zsh
  - aliases: `ls=lsd`, `reload="source ~/.zshrc"`
  - env: CUDA_HOME, UV_INDEX_URL, TAVILY_API_KEY, EXA_API_KEY
  - script: `eval "$(fzf --zsh)"`
- Miniconda: `/public/home/caiyiwen/apps/miniconda3`
- Local tools: lsd (~/.local/bin), fzf (~/.fzf), nvim, helix, wezterm
- CUDA: nvcc at `/usr/bin/nvcc`, `/usr/local/cuda` symlink
- Additional apps in `~/apps/`: chafa, helix, miniconda3, nvim, wezterm

## Target After Migration

- Home: `/storage/caiyiwen`
- Same zsh/oh-my-zsh/powerlevel10k setup
- Miniconda 26.3.2 at `~/apps/miniconda3`
- lsd 1.1.5 at `~/.local/bin/lsd`
- fzf 0.73.1 at `~/.fzf/bin/fzf`
- CUDA 12.8 at `/usr/local/cuda-12.8` (symlink via `/usr/local/cuda`)
- 2× NVIDIA A800 80GB PCIe, Driver 580.126.09

## Key Commands Used

```bash
# Check source .zshrc
ssh lab "cat ~/.zshrc"

# Check target environment
ssh a800 "echo \$HOME; which conda; ls -la /usr/local/cuda*"

# Transfer custom config
scp lab:~/.config/zsh/custom/aliases.zsh a800:~/.config/zsh/custom/
scp lab:~/.config/zsh/custom/env.zsh a800:~/.config/zsh/custom/
scp lab:~/.config/zsh/custom/script.zsh a800:~/.config/zsh/custom/
scp lab:~/.p10k.zsh a800:~/.p10k.zsh

# Install local tools (no sudo)
ssh a800 "curl -sL https://github.com/lsd-rs/lsd/releases/download/v1.1.5/lsd-v1.1.5-x86_64-unknown-linux-musl.tar.gz | tar xz -C /tmp/ && cp /tmp/lsd-*/lsd ~/.local/bin/ && chmod +x ~/.local/bin/lsd"
ssh a800 "git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install --no-bash --no-fish --key-bindings --completion --no-update-rc"

# Test full config
ssh a800 'zsh -c "export WEZTERM_EXECUTING=; source ~/.zshrc; which lsd && which fzf && which conda"'

# Test interactive aliases
ssh -t a800 'zsh -i -c "cuversion; gpu"'
```

## Bug Fix Record

**Bug**: `source $HOME/.config/zsh/custom/*.zsh` in .zshrc only sourced the first file (aliases.zsh). env.zsh and script.zsh were silently skipped.
**Fix**: Replace with `for f in $HOME/.config/zsh/custom/*.zsh; do source "$f"; done`
**Root cause**: In zsh (and bash), `source file1 file2` sources file1 with file2 as $1 — it does NOT source all files.
