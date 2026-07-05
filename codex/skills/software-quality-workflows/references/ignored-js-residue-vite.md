# Ignored JavaScript Residue Blocking TypeScript Builds

Use this reference when a Vue/Vite/TypeScript project build reports missing exports from a `.js` module even though the corresponding `.ts` source clearly exports the symbol.

## Symptom

Vite/Rolldown may fail with an error like:

```text
[MISSING_EXPORT] "SOME_SYMBOL" is not exported by "packages/client/src/stores/foo.js".
```

But `packages/client/src/stores/foo.ts` contains `export const SOME_SYMBOL = ...`.

## Diagnosis

Check for ignored or generated `.js` siblings under source directories. They can be invisible in normal `git status` if `.gitignore` excludes them, but module resolution can still pick them before `.ts` sources.

```bash
git ls-files 'packages/client/src/**/*.js'
git ls-files --others --exclude-standard 'packages/client/src/**/*.js'
git ls-files --others -i --exclude-standard 'packages/client/src/**/*.js' | sed -n '1,120p'
git check-ignore -v packages/client/src/stores/foo.js
```

Interpretation:

- `git ls-files` returns paths: tracked source files; do not delete blindly.
- `--others --exclude-standard` returns paths: untracked visible files; inspect before deleting.
- `--others -i --exclude-standard` returns paths: ignored residue; likely safe to clean when they mirror `.ts`/`.vue` sources.

## Fix Pattern

Only clean ignored JavaScript residue in the affected source subtree, then rebuild.

```bash
git clean -fX 'packages/client/src/**/*.js'
NO_COLOR=1 npm run build
```

If the repo uses generated JavaScript source intentionally, narrow the glob to the failing subtree or exact file first.

## Why This Matters

This failure is easy to misread as an upstream export regression. The durable lesson is to inspect ignored files, not to patch exports that already exist in TypeScript.
