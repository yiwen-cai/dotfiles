---
name: zhihu
description: "使用知乎 CLI 搜索知乎、读取本人创作/收藏、检索知识库或查询额度；用于明确的知乎开放平台任务。"
---

# zhihu

## 会话初始化
每次会话第一次使用，运行本包 `scripts/run.sh status`，使用返回的绝对 binary_path，不盲用 PATH 中的同名 CLI。
首次使用与认证、命令边界完整见 [workflow.md](references/workflow.md)。调用前读取其中适用部分；当前任务已有安装/初始化授权时不要重复索要。

## 任务边界
搜索用 `search zhihu` / `search global`，本人信息用 `me`，知识库用 `knowledge`，额度用 `quota`。不因为普通 API、MCP、RAG 提问自动调用知乎。
创作接口摘要不当完整正文；CLI 本身不作为文章发布工具。文件上传只处理用户明确指定且要求上传的文件。
验证所需的最小结果，分页只取完成任务所需范围。
