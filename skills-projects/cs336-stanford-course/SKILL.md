---
name: cs336-stanford-course
description: "在 CS336 项目中按用户作业优先、TA 辅导和远程实验约定学习与核验。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# cs336-stanford-course

## 本项目约定
当前作业优先，所需讲义即时补充，不默认按 lecture 顺序安排。沿用仓库既有 TA 边界；先读当前作业与测试；需要知识记录时，从 `$WIKI_PATH`（未设置则 `~/wiki`）读取 `concepts/cs336-language-modeling.md` 和相关 `queries/`，不要把它们误当作课程仓库内路径。
本机项目为 `~/Documents/code/cs336`。服务器路径、SSH 执行、profiling 与写作规则按 [a800-assignment-workflow.md](references/a800-assignment-workflow.md) 和当前项目环境确认；展示给用户的命令按已在对应服务器 shell 中书写，实际本机执行使用 SSH。

## 按需资料
- 作业阶段/混合精度/Nsight：[assignment-guide.md](references/assignment-guide.md)，具体 profiling 读 `assignment2-nsys-profiling.md`。
- 模型组件辅导：`cs336-model-components-tdd-coaching.md`、`cs336-stage1-stage2-shape-pitfalls.md`。
- 用户要求同步进度时：`cs336-progress-sync-workflow.md`，同步已有 Markdown、HTML 和 wiki，不另造重复记录。
- GPU 数值或性能问题使用实际 Triton/CUDA 资料；选卡先检查设备型号，不把 a800 的 GPU0 默认为 A800。
自动测试和学习测验分开；无默认提交考试门禁。
