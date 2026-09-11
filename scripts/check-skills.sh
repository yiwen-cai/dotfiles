#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$REPO_DIR/scripts/manage-skills.py" validate
if [ "${1:-}" = "--deployed" ]; then
  check_plan="$(mktemp)"
  trap 'rm -f "$check_plan"' EXIT
  python3 "$REPO_DIR/scripts/manage-skills.py" check --targets codex,agents,claude,projects --out "$check_plan"
  echo 'ok: managed skills and bound project routes match the manifest'
elif [ -n "${1:-}" ]; then
  echo 'Usage: scripts/check-skills.sh [--deployed]' >&2
  exit 2
fi
