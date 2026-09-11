# Skill 精简执行记录

执行日期：2026-09-06。已完成本机 Codex/agents 迁移；未提交或推送 Git 改动。

## 最终结果

| 项目 | 结果 |
|---|---|
| Codex 用户级入口 | 12 个，位于 `~/.codex/skills` |
| 共享 GPU 入口 | 4 个，位于 `~/.agents/skills`，与 Codex 目录无同名重复 |
| 项目资源包 | 5 个源包，其中 4 个已绑定并部署 |
| 可选包 | 68 个，默认停用 |
| 退役名称 | 71 个，不再自动发现 |
| 迁移前原件 | 160 个全部保存于 `skills-archive/`，入口为 `SKILL.md.disabled` |
| 初次部署 | 168 个文件/包动作：144 个旧全局入口停用、18 个替换、6 个新增 |
| 收尾部署 | 1 个项目包更新，明确 CS336 wiki 路径 |

最终启用名单与合并来源以 `skills-manifest.json` 为准。初始审查中的五类数量是建议阶段统计，经过合并及源包分配后形成以上生命周期数量。

## 已绑定项目

- CS336：`/Users/yiwencai/Documents/code/cs336`
- 简历：`/Users/yiwencai/Documents/study/CV/basic-resume`
- 博客：`/Users/yiwencai/Documents/code/yiwen-cai.github.io`
- MoE 本机接口：`/Users/yiwencai/Documents/code/moe-kv-cache-experiments`

包放在各项目 `docs/agent-skills/<name>/`，通过该项目 AGENTS.md 的条件路由读取。既有项目规则保留，博客旧发布流程路径已修正。
论文模板实际位于 H100 的 `$HOME/code/BUPTBachelorThesis`；已只读核实 main.tex 和 BUPTBachelorThesis.sty。本次没有扩展到远程部署，论文包在 `skills-projects/bupt-thesis-writer` 保留，项目绑定状态为 pending。

## 内容整理

- 取消默认八段交付链及提交前考试，保留主动选择的课程测验。
- 通用课程入口不含 CS336 专属同步规则；CS336 的作业优先、TA 边界及 wiki 路径在项目包中保存。
- GitHub 入口保留评论线程提取与 CI 日志脚本，清除旧插件固定路由。
- 科研简报合并源表、管线资料；只有明确请求才创建调度任务。
- 学术输出接收论文综述提示与图示模板，文档文件操作由系统/插件承担。
- Triton 数值验证内容从伪装成 .py 的 Markdown 转为明确的可适配模板。
- 所有 160 个原件的文件内容/权限及链接文本与备份逐项核对，无保存差异。
- 原主树与全局完整包的唯一差异为 skill-creator（包括原有缓存差异）；两份均保存在本机初始快照，仓库中的原有已修改缓存文件仍保持原位。
- 系统/插件同名入口的原文差异另保存在本目录 `*.diff`；这些是审计材料，不作为运行指令。

## 验证证据

- 部署器 14 项自动测试通过：未知包及 .system 保护、初次迁移、同名冲突、后续编辑保护、过期计划、目标符号链接、缺源/坏链接、失败恢复、回滚、幂等、停用 target、单项可选启用和项目路由。
- 21 个 global/project 包通过系统 skill-creator 的 quick_validate。
- 保留的活跃 Python 脚本经 AST 语法检查；论文提取与 GitHub CI 脚本的 --help 正常。
- 四个 GPU 解析器均真实通过 SSH 读取到 H100 上对应文档/源码并返回 SHA-256。没有下载大型仓库或启动 GPU 实验。
- 知乎 run.sh status 在具备系统凭据访问权限的环境中返回 `ready`、`auth.configured=true`、`compatible=true`。未修改凭据或发布/上传内容。普通沙箱会将 Keychain 读取失败表现为未配置，不能据此重置认证。
- `.system`、`~/.claude/skills` 和 `~/.zcode/skills` 在迁移前后哈希一致。
- 项目包、全局包与清单一致；再次生成 plan 为零变更。
- 入口及引用进行了静态场景复核：普通 KV Cache 问题不作为 SGLang 触发条件，MIT 不继承 CS336 规则，论文笔记/周报分别路由，博客预览不自动发布。
- 三个看似缺失的 Markdown 链接位于示例模板中（ACCESS.md、diagram.svg、示例“链接”），不是包的运行依赖；实际入口引用均可解析。

未声称已端到端执行真实论文写作、视频转录、GPU benchmark 或部署博客。当前任务的技能目录由会话开始时提供，不能在本会话证明 UI 目录已刷新；新任务应读取新的全局集合。不为刷新目录额外创建用户任务。

## 备份和回滚

初始完整备份（含原全局目录、源目录和项目 AGENTS.md）：

`/Users/yiwencai/.local/state/dotfiles/skill-backups/20260906-093700`

原来的五个用户级源目录符号链接在迁移前先冻结为原始内容副本；因此部署回滚可恢复可读的旧包，不依赖已经整理过的源路径。初始完整备份同时保留原链接布局。

本次产生两个部署快照。恢复这次全局/项目部署时按逆序执行：

```bash
python3 scripts/manage-skills.py rollback --snapshot /Users/yiwencai/.local/state/dotfiles/skills/snapshots/5e9dcfb77ea149adbb1c4830a7b45257
python3 scripts/manage-skills.py rollback --snapshot /Users/yiwencai/.local/state/dotfiles/skills/snapshots/fd7d7f0942e6494c81d30db6da9c0869
```

回滚保护后续编辑，遇冲突会停止。部署回滚只恢复全局/项目部署；仓库的清单、源目录重组与 codex/AGENTS.md 需要根据初始备份和本次 diff 单独恢复，不能运行整个仓库的 reset/clean 来覆盖原有工作。
本次未覆盖原有 pi 文件修改。初始备份与归档不自动清理。

## 后续维护

新增或启用 skill 使用显式清单，先 plan 再 apply。其他宿主本轮不部署，不假定它们具备 Codex 的运行时能力。
可选包只保存其功能资产，尚未逐一验证外部服务/依赖；启用具体包时再验证对应环境。
接下来正常使用时记录误触发或缺失即可；没有创建后台监控或自动删除任务。
