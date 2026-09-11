# Node Version Symlink Workflow

## Problem

Hermes bundles Node v22 at `~/.hermes/node/bin/node`, but the user wants Hermes to use a newer nvm-managed Node (e.g., v23). Hermes also creates `~/.local/bin/node -> ~/.hermes/node/bin/node`, which often appears earlier in PATH than nvm's bin directory.

## Solution: Symlink Hermes Internal Node to nvm

Instead of replacing the entire `~/.hermes/node` directory (risky, breaks on Hermes updates), symlink individual binaries inside Hermes's node bin directory to nvm equivalents.

### Steps

```bash
cd ~/.hermes/node/bin

# Backup bundled binaries
mv node node-v22
mv npm npm-v22
mv npx npx-v22

# Create symlinks to nvm
ln -s ~/.nvm/versions/node/v23.11.1/bin/node node
ln -s ~/.nvm/versions/node/v23.11.1/bin/npm npm
ln -s ~/.nvm/versions/node/v23.11.1/bin/npx npx
```

### Verification

```bash
~/.hermes/node/bin/node -v   # v23.11.1
~/.hermes/node/bin/npm -v    # 10.9.2
which -a node                # ~/.local/bin/node, ~/.nvm/.../node
```

### Reversal

```bash
cd ~/.hermes/node/bin
rm node npm npx
mv node-v22 node
mv npm-v22 npm
mv npx-v22 npx
```

## Why Not Replace the Entire Directory?

- Hermes may verify or reinstall its bundled Node on update
- Downloading a full Node tarball can fail (large file, slow mirror)
- Symlinks preserve Hermes's directory structure while delegating execution

## PATH Priority Note

The `~/.local/bin/node` symlink is created by Hermes installer. If `~/.local/bin` precedes nvm in PATH, even nvm's `node` command may resolve to the Hermes bundled version. The symlink fix above resolves this regardless of PATH order because Hermes internally calls `~/.hermes/node/bin/node`.
