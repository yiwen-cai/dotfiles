#!/usr/bin/env bash
# Compatibility wrapper: skills-manifest.json is the only target/profile definition.
deploy_managed_skills() {
  local skills_plan
  skills_plan="$(mktemp)"
  if ! python3 "$REPO_DIR/scripts/manage-skills.py" plan --targets codex,agents,claude --out "$skills_plan"; then
    rm -f "$skills_plan"
    return 1
  fi
  local skills_status=0
  python3 "$REPO_DIR/scripts/manage-skills.py" apply --plan "$skills_plan" || skills_status=$?
  rm -f "$skills_plan"
  return "$skills_status"
}
