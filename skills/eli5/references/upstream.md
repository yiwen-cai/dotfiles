# 来源与许可

本包在 2026-09-13 从两个 MIT 上游合并并本地化：

| 上游 | 取用内容 | 获取方式 |
|---|---|---|
| [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community/tree/main/eli5)（MIT，作者 Thariq Shihipar） | `/eli5 <主题>` 入口语义、「图多字少」的 HTML 图解交付形态 | `gh api repos/anthropics/claude-plugins-community/contents/eli5/...` |
| [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5)（MIT） | 年龄、学段、职业、亲属四类受众分级与语言校准原则 | `gh api repos/DreambigOu/ELI5/contents/skills/eli5/SKILL.md` |

两份原文均为英文单文件；本地化后的差异：

- 描述改为本仓库统一的中文三段式（用途、触发词、验收标准）。
- 受众分级表移入 [audience-levels.md](audience-levels.md)，入口只保留判定与交付规则，按需加载。
- 交付默认改为对话内文字解释；HTML 图解仅在用户要求图解或可分享页面时产出（上游社区插件默认直接产出 artifact）。
- 补充本仓库的通用边界：先读实际材料再解释、材料缺失时说明缺口、解释请求不顺带改代码或发消息、简化处需显式标注。

上游许可为 MIT，保留其版权声明即可再分发；本地化文本随本仓库维护。
