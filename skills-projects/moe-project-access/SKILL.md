---
name: moe-project-access
description: "在 MoE KV Cache 本机接口项目中读取接入信息、核查远程实验状态。"
---

# moe-project-access

## 接入事实源
这是元信息接口，真实代码/数据/模型在远程。本项目 README、ACCESS、ENVIRONMENTS、MODELS、DATASETS、RESULTS 是首要导航；先读这些文件，易变状态用 SSH 确认并注明时间。
遵守项目 TA 风格和实验执行约定；接入或查状态不授权启动训练/推理。

## 状态报告
按 [status-checks.md](references/status-checks.md) 选择所需检查，不强制读取全部历史日志。记录机器、项目路径、解释器、模型位置、结果证据和未确定项。跨机对比验证输入一致性，不能沿用历史 md5 结论。
变更接入事实时精确更新原有接口文件，不另造第二份环境状态。
