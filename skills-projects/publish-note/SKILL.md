---
name: publish-note
description: "在个人 Hugo/Blowfish 博客项目中整理技术笔记、预览和按请求发布。"
---

# publish-note

## 当前约定
先读本项目 AGENTS.md，分类/渲染/部署规则以它为准。笔记位于 `content/notes/<分类>/<slug>/index.md`，英文 slug、中文正文，TOML front matter 手写 summary。
清理 Obsidian 双链、私人本地路径和 PPT 残留；公式正文开头添加 `{{< katex >}}`。当前博客不使用 Mermaid，采用文字图或表格等项目允许的形式。
具体清理和引用例子见 [publishing-details.md](references/publishing-details.md)，其历史状态不作为现状。

## 发布与验证
先构建/预览，核对公式、图表和目录。仅预览请求不触发提交推送；明确发布时遵守项目 Git 约定，只暂存本次文章与相关资源，不用 git add -A。
有引用的数字标明是否自己复现；缺少 arXiv 信息不编造链接。发布后查询对应构建结果。
