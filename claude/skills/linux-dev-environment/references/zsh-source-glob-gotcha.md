# zsh `source` with glob: Only first file is sourced

## The Bug

```zsh
# ❌ This does NOT source all files
source ~/custom/*.zsh
```

In zsh, `source file1 arg1 arg2` follows POSIX semantics: it sources file1, and arg1/arg2 become positional parameters (`$1`, `$2`) inside file1. Multiple filenames from glob expansion are NOT each sourced — only the first one is.

## The Fix

```zsh
# ✅ Loop to source each file
for f in ~/custom/*.zsh; do
  source "$f"
done
```

## Reproduction

Create test files to see the bug:

```bash
mkdir -p /tmp/zsh-test
cat > /tmp/zsh-test/a.zsh << 'EOF'
A_VAR="sourced_from_a"
EOF

cat > /tmp/zsh-test/b.zsh << 'EOF'
B_VAR="sourced_from_b"
EOF

# Bug demonstration
zsh -c 'source /tmp/zsh-test/*.zsh; echo "A_VAR=${A_VAR:-unset}"; echo "B_VAR=${B_VAR:-unset}"; echo "\$1=${1:-unset}"'

# Output:
# A_VAR=sourced_from_a
# B_VAR=unset      <-- b.zsh was NOT sourced
# $1=/tmp/zsh-test/b.zsh  <-- it became $1 inside a.zsh!

# Fix demonstration
zsh -c 'for f in /tmp/zsh-test/*.zsh; do source "$f"; done; echo "A_VAR=${A_VAR:-unset}"; echo "B_VAR=${B_VAR:-unset}"'

# Output:
# A_VAR=sourced_from_a
# B_VAR=sourced_from_b   <-- correctly sourced
```

## Why This Matters

This bug is silent — no error message is produced. The first file (alphabetically) loads correctly, but all subsequent files in the glob are silently ignored. You only notice when features from later files don't work (fzf, extra PATH entries, additional aliases, etc.).

## How bash differs

In **bash**, `source file1 file2 file3` only sources file1 too (same POSIX behavior). But in bash, `source *.sh` with a single-match glob works fine. The key difference is that zsh's `source` builtin behaves identically to bash here — the real issue is that zsh users are more likely to use glob patterns with `source` due to zsh's more sophisticated glob support.

## Verification

After applying the fix, verify with:
```bash
# Check that all custom files were loaded
grep -c "sourced" ~/.config/zsh/custom/*.zsh
# Or check that expected side effects exist
echo $PATH | tr ':' '\n' | grep -E "fzf|local"
```
