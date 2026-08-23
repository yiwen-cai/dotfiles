# Helix configuration

This directory is a reusable Helix configuration for C, C++, and CUDA editing.

## Install

Run the repository installer:

```bash
./install.sh
```

It links:

- `config.toml` and `languages.toml` into `~/.config/helix/`;
- the CUDA tree-sitter queries into `~/.config/helix/runtime/queries/cuda/`;
- `bin/clangd-helix` into `~/.local/bin/`.

Ensure `~/.local/bin` is in `PATH`. The wrapper resolves clangd in this order:

1. `HELIX_CLANGD`, when explicitly set;
2. Homebrew LLVM on Apple Silicon or Intel macOS;
3. `clangd-22` in standard Linux locations;
4. the system `clangd`.

Examples:

```bash
brew install helix llvm                  # macOS
export HELIX_CLANGD=/custom/bin/clangd  # optional override
```

## CUDA project contract

The shared configuration registers `.cu` and `.cuh` as an independent `cuda`
language and reuses the C++ parser. It deliberately does not embed a CUDA
Toolkit path: each CUDA project must provide one of the following:

- `compile_commands.json` with its real build flags; or
- `.clangd` plus `compile_flags.txt` with vendored CUDA headers and LSP stubs.

This keeps the dotfiles portable and avoids committing NVIDIA's proprietary
headers. On macOS, CUDA support is for completion, diagnostics, and navigation
only; it does not provide `nvcc`, a GPU runtime, or local kernel execution.

## Verify

```bash
clangd-helix --version
hx --health cpp
hx --health cuda
```
