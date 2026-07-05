# Common Resume Issues Checklist

Review each `.typ` file against this list.

## Data Consistency (multi-version)
- [ ] GPA matches across Chinese/English versions
- [ ] Grade (均分) matches across versions
- [ ] Rank (排名) matches — both numerator and denominator
- [ ] Same projects/awards appear in both versions
- [ ] Same skills appear in both versions
- [ ] No extra data in one version not in the other (e.g., "Grade with optional course")

## Typo / Format
- [ ] GitHub URL: `github.com` not `github,com`
- [ ] Email consistent between versions (or intentionally different)
- [ ] No trailing comma at end of bullet lists
- [ ] Chinese punctuation: `，` not `,` in Chinese text; `。` at end of complete sentences
- [ ] No stray spaces after Chinese commas: `一等奖， 最高` → `一等奖，最高`
- [ ] Space between Chinese and English: `AI Agent 的平台` not `AI Agent的平台`
- [ ] Colon consistency: `*label*: value` (English colon) throughout

## Section Completeness
- [ ] Skills section not truncated — full content present
- [ ] All projects have `dates` parameter
- [ ] No duplicate award entries (same competition split across two items)
- [ ] Section headings consistent (all Chinese or all English, not mixed)

## Content Quality
- [ ] Project descriptions have quantifiable results (speedup, grade, rank), not just feature lists
- [ ] Bullet points consistent: no stray trailing periods when others don't have them
- [ ] "研究方向" vs "技术" — research directions describe what you study, not what tools you can use
- [ ] English text in Chinese resume: avoid phrases like "1st of course"; use "第 1 名"

## Typst-Specific
- [ ] `#super[st]` / `#super[nd]` rendered correctly (superscript doesn't break in plain-text review)
- [ ] `dates-helper()` used for ranges; bare `dates:` for single months
- [ ] `#work()` only for items with company/organization context
- [ ] `#project()` used correctly with `name:`, `role:`, `dates:` parameters
