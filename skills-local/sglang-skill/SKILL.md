---
name: sglang-skill
description: "定位 SGLang 源码与实例，处理明确涉及 SGLang 的推理引擎问题。"
---

# sglang-skill

## 定位资料
先运行 `python3 scripts/resolve-gpu-source.py`（脚本路径相对于本包）。优先使用 `GPU_SKILLS_ROOT` 指向的实际资料库；未配置本地可用库时，使用 `GPU_SKILLS_HOST`（默认 h100）及 `GPU_SKILLS_REMOTE_ROOT` 查询远程。
输出明确标记 local/ssh、版本 checkout 路径和已验证样例。SSH 路径不是本地文件，使用 SSH 读取；不创建指向远程绝对路径的本地符号链接。

## 按任务阅读
定位后按 [source-index.md](references/source-index.md) 的目录/符号索引查所需文档。索引中的版本和旧路径仅供定位，当前源码与 CLI 输出优先。
只读资料不要求运行训练或 benchmark。执行编译/性能实验时使用任务授权范围，核实设备型号、依赖版本与输入条件。
