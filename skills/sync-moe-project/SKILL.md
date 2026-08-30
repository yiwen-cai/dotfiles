---
name: sync-moe-project
description: 同步 A800 服务器上 MoE KV Cache 实验项目（moe_kv_cache_experiments）的进展状态。当用户提到"同步 MoE 项目"、"同步 moe 实验"、"moe 进展"、"a800 实验状态"或类似关键词时触发。用于获取远程实验的最新状态、结果文件、日志和模型下载进度。
---

# Sync MoE Project

## Overview

该 skill 用于自动同步 A800 服务器上 `/home/caiyiwen/moe_kv_cache_experiments` 项目的实验进展。通过 SSH 连接远程服务器，收集项目状态、实验结果、日志和模型下载进度，并生成结构化报告。

## Workflow

### Step 1: 收集项目元信息

通过 SSH 执行以下命令收集基础信息：

```bash
ssh a800 "cd /home/caiyiwen/moe_kv_cache_experiments && git status && git log --oneline -5"
ssh a800 "ls -la /home/caiyiwen/moe_kv_cache_experiments/"
ssh a800 "cat /home/caiyiwen/moe_kv_cache_experiments/progress.md"
ssh a800 "cat /home/caiyiwen/moe_kv_cache_experiments/task_plan.md"
ssh a800 "cat /home/caiyiwen/moe_kv_cache_experiments/findings.md"
```

### Step 2: 检查实验结果目录

```bash
ssh a800 "ls -la /home/caiyiwen/moe_kv_cache_experiments/results/"
ssh a800 "ls -la /home/caiyiwen/moe_kv_cache_experiments/models/"
```

对每个实验结果子目录，检查内容：
```bash
ssh a800 "ls -la /home/caiyiwen/moe_kv_cache_experiments/results/<exp_dir>/ | head -20"
ssh a800 "cat /home/caiyiwen/moe_kv_cache_experiments/results/<exp_dir>_run.log | tail -30"
```

### Step 3: 检查模型下载状态

```bash
ssh a800 "cat /home/caiyiwen/moe_kv_cache_experiments/download_qwen3_8b.log | tail -20"
```

### Step 4: 生成结构化报告

将收集到的信息整理为以下结构的报告：

1. **项目状态总览**：路径、git 状态、最近提交
2. **已完成工作**：按阶段列出已完成任务
3. **实验结果表格**：每个实验的状态、说明、问题
4. **当前问题**：列出阻塞或失败的问题
5. **模型/资源状态**：模型下载进度、可用模型列表
6. **下一步建议**：基于当前状态给出行动建议

## 关键文件路径

| 文件 | 路径 |
|------|------|
| 项目根目录 | `/home/caiyiwen/moe_kv_cache_experiments` |
| 进展记录 | `/home/caiyiwen/moe_kv_cache_experiments/progress.md` |
| 任务计划 | `/home/caiyiwen/moe_kv_cache_experiments/task_plan.md` |
| 发现记录 | `/home/caiyiwen/moe_kv_cache_experiments/findings.md` |
| 实验结果 | `/home/caiyiwen/moe_kv_cache_experiments/results/` |
| 模型目录 | `/home/caiyiwen/moe_kv_cache_experiments/models/` |
| 下载日志 | `/home/caiyiwen/moe_kv_cache_experiments/download_qwen3_8b.log` |

## 常见问题与处理

### 1. matplotlib 兼容性问题
如果可视化阶段报错 `boxplot() got an unexpected keyword argument 'labels'`，说明 matplotlib 版本较新，参数名已改为 `tick_labels`。需要修复 `src/viz.py` 中的对应调用。

### 2. CUDA OOM
如果 2048 长度实验出现 OOM，检查：
- 是否使用了 `torch.no_grad()`
- 是否可以使用 `device_map="auto"` 做模型并行
- 是否需要清空缓存 `torch.cuda.empty_cache()`
- 是否需要切换到更小的模型（如 Qwen3-8B）

### 3. 模型下载进度
Qwen3-8B 下载进度可通过 `download_qwen3_8b.log` 查看。下载完成后可用于替代 30B 模型进行 pilot 实验。

## 参考信息

- 服务器：A800（通过 `ssh a800` 连接）
- GPU：NVIDIA RTX PRO 6000 Blackwell (97GB) + 2× NVIDIA A800 80GB
- 主要模型：Qwen3-30B-A3B（已就绪）、Qwen3-8B（下载中）
- 数据集：LongBench（已下载解压到 `data/raw/longbench/`）
