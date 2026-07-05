# Content Localization for Daily Briefings

Translation conventions and patterns used when the collection script fetches English content (GitHub, Tavily, Exa) and the user needs Chinese output.

## What to translate

| Content type | Examples | Translate? |
|---|---|---|
| Release version subtitles | "The Patch Release", "The Velocity Release", "The Surface Release", "The Foundation Release", "The Curator release" | Yes → "补丁版本", "速度版本", "界面版本", "基础版本", "策展人版本" |
| Commit messages | "fix(web): profiles page modal (#43858)" | Yes → "修复(web): profiles 页面弹窗 (#43858)" |
| Release notes | "Bug Fixes", "Contributors", "Highlights", "Release Date", "Full Changelog" | Yes → "Bug 修复", "贡献者", "亮点", "发布日期", "完整更新日志" |
| Source names | "GitHub Releases", "GitHub Commits", "Tavily", "Exa" | Yes → "GitHub 发布", "GitHub 提交" (Tavily/Exa stay as brand names) |
| Item descriptions/summaries | English paragraphs from search results | Yes |
| Card titles (h2) | English title of release/commit/article | Yes |
| UI framework text | "Untitled", "Unknown source", "No summary" | Already localized in template — verify at render time |

## What to preserve (DO NOT translate)

- **Technical names**: Hermes Agent, GitHub, NousResearch, HERMES_HOME, .env, MCP, Codex CLI
- **Version identifiers**: v0.x.x, v2026.5.29.2, #43858
- **Hashes/SHAs**: 9dd9ef0, d1383a6
- **URLs**: all hrefs and plain-text URLs
- **HTML/CSS tags and structure**: `<article>`, `<h2>`, `<a href="...">`, class names
- **MEDIA: markers**: `MEDIA:/absolute/path/to/file` — this is a delivery directive
- **Numbers and dates**: 1,302 commits, 2026-05-29T13:37:26+00:00
- **Already-Chinese content**: e.g. "每日动态", "重点条目", "本次采集到", "来源"

## Version name mapping table

| English original | Chinese translation |
|---|---|
| The Patch Release | 补丁版本 |
| The Velocity Release | 速度版本 |
| The Surface Release | 界面版本 |
| The Foundation Release | 基础版本 |
| The Curator release | 策展人版本 |

## Source name mapping

| English original | Chinese translation |
|---|---|
| GitHub Releases | GitHub 发布 |
| GitHub Commits | GitHub 提交 |
| GitHub Repository | GitHub 仓库 |
| Tavily | Tavily (keep) |
| Exa | Exa (keep) |

## Commit message pattern

```
fix(area): description (#PR_number) → 修复(area): description (#PR_number)
feat(area): description → 功能(area): description
docs: description → 文档: description
refactor: description → 重构: description
```

Keep the parenthesized "area" term (e.g. (web), (skills)) in English — these are codebase module references.

## Release note section mappings

| English | Chinese |
|---|---|
| Release Date | 发布日期 |
| Bug Fixes | Bug 修复 |
| Contributors | 贡献者 |
| Highlights | 亮点 |
| Full Changelog | 完整更新日志 |
| Since vX.Y.Z | 自 vX.Y.Z 以来 |
| commits | 次提交 |
| merged PRs | 个合并 PR |
| files changed | 个文件变更 |
| insertions | 行新增 |
| deletions | 行删除 |
| issues closed | 关闭 issue |
| community contributors | 位社区贡献者 |
