---
name: github-operations
description: "处理 GitHub issue、PR 评论和 Actions CI，使用实际可用的连接器或 gh 并保留线程级上下文。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# github-operations

## 路由与授权
先从当前 git remote/branch 或用户链接确定仓库与 PR。有连接器且覆盖任务时使用连接器；线程状态、CI 日志或缺少覆盖时用 `gh`，不假定宿主装有特定插件。
普通本地 git 不需要此工作流。用户已要求修复的范围直接完成；不因旧模板重复要求“批准修复”。发评论、提交、推送和创建 PR 按用户实际授权执行。

## 具体工具
- 评论线程：`python scripts/fetch_comments.py`；先读帮助/实现确认上下文，保留 resolved 状态和行级评论，不把扁平 comments 当完整 review。
- Actions：`python scripts/inspect_pr_checks.py --repo <repo> --pr <PR>`；需要时读失败 job 日志，非 Actions 的 CI 链接单独报告。
- 提交/PR：检查当前 diff 和已有修改，仅暂存本任务文件。正文写问题、最终行为、验证及限制；多行正文用结构化字段或 `--body-file`。

## 验证
检查实际 PR/评论/CI 状态，区分读取、修改、发布结果。缺认证时报告具体需要的登录步骤，不输出 token。
