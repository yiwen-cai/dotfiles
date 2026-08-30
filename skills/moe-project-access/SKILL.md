---
name: moe-project-access
description: 接入 MoE KV Cache 实验项目的快速指引。当用户提到"接入项目"、"连接项目"、"项目环境"、"a800/h100 项目信息"、"如何连到服务器"、"项目在哪台机器"、"ssh 到实验服务器"或需要了解 MoE KV Cache 实验项目在 A800 / H100 上的部署情况时触发。提供两台服务器的 SSH 配置、项目路径、环境、模型位置、数据位置等关键接入信息。
---

# MoE Project Access

## Overview

MoE KV Cache 实验项目部署在两台实验室服务器上。本 skill 提供**快速接入指引**：SSH 配置、项目路径、Python 环境、模型/数据位置、GPU 配置，以及两台机器的差异和当前分工。

## 服务器总览

| 服务器 | SSH 别名 | IP | 用途 | GPU |
|--------|---------|-----|------|-----|
| **A800** | `a800` | 10.160.4.104 | 历史实验主战场（阶段 0–7 已完成） | Blackwell 97GB + 2× A800 80GB |
| **H100** | `h100` | 10.160.4.102 | 新工作环境（复现 + vLLM 开发） | 8× H100 PCIe 81GB |

两台都用同一个 SSH key（`~/.ssh/id_ed25519`），用户名 `caiyiwen`。

## 接入命令

```bash
# 连接 A800
ssh a800

# 连接 H100
ssh h100

# 无交互快速执行命令（脚本/探针用）
ssh -o ConnectTimeout=10 -o BatchMode=yes a800 "命令"
ssh -o ConnectTimeout=10 -o BatchMode=yes h100 "命令"
```

⚠️ **H100 连接偶尔不稳定**（会话掉线、连接重置）。若需要长时间运行任务，务必用 `tmux`：
```bash
ssh h100
tmux new -s mywork 'bash long_running_script.sh'
# 重连后恢复
ssh h100 -t 'tmux attach -t mywork'
```

## A800 服务器

### 项目路径
- **项目根**：`/home/caiyiwen/moe_kv_cache_experiments`
- **模型目录**：`models/`（项目内）
  - `models/Qwen3-30B-A3B/`（MoE，57G）
  - `models/Qwen3-8B/`（Dense，16G）
  - `models/Qwen1.5-MoE-A2.7B-Chat/`（早期模型）
- **数据**：`data/raw/longbench/`（LongBench 真实长上下文）
- **规划文件**：`task_plan.md` / `progress.md` / `findings.md`（阶段 0–7 完整历史）

### 环境
- **Python venv**：`.venv`（Python 3.13，uv 管理）
- **关键依赖**：torch / transformers / bitsandbytes / accelerate / scipy / seaborn
- **vLLM**：`/home/caiyiwen/vllm/.venv`（vllm 0.1.dev1，Python-only build）
  - ⚠️ A800 上 vLLM 的 torch 误装成 cu130（应为 cu128），若用 vLLM 推理需先修正

### GPU
- GPU0: **NVIDIA RTX PRO 6000 Blackwell**（compute 12.0, 97GB）— 实验主力
- GPU1/2: **A800 80GB PCIe** — 常被其他用户（furongtian）占用
- CUDA 12.8，编译用 `/usr/local/cuda-12.8/bin/nvcc`（不要用 `/usr/bin/nvcc` 有 bug）

### 常用命令
```bash
# 跑实验（示例）
cd /home/caiyiwen/moe_kv_cache_experiments
CUDA_VISIBLE_DEVICES=0 .venv/bin/python src/run_experiment.py --model models/Qwen3-8B ...

# 查进度
tail -f results/<exp>_run.log
```

## H100 服务器

### 项目路径
- **项目根**：`/public/home/caiyiwen/code/moe-test`（注意：不是 `moe_kv_cache_experiments`，与 A800 不同名）
- **模型目录**：`/public/home/caiyiwen/models/`（项目**外**，项目内 `models/` 为空）
  - `Qwen3-30B-A3B/`（57G，✅ 校验完整）
  - `Qwen3-8B/`（16G，✅ 校验完整）
- **数据**：`data/`（LongBench，与 A800 md5 一致）
- **规划文件**：`task_plan_h100.md` / `progress_h100.md` / `findings_h100.md`（H100 专属，2026-07-04 起新工作）
  - 历史（阶段 0–7）看 A800 的无后缀文件

### 环境
- **Python venv**：`.venv-h100`（Python 3.12，uv 管理）
  - ⚠️ 是 uv 管理环境，`pip list` 不工作，要用 `uv pip list --python .venv-h100/bin/python`
- **uv 路径**：`/public/home/caiyiwen/.local/bin/uv`
- **关键依赖**：torch 2.10.0+cu126 / transformers 4.57.6 / bitsandbytes 0.49.2（全齐）
- **vLLM**：`/public/home/caiyiwen/code/vllm/.venv`（vllm 0.23.1rc1，源码 editable 安装，torch cu126 ✅ 正确）

### GPU
- 8 卡 H100 PCIe，每卡 81GB
- **GPU 0-3 通常空闲**，GPU 4-7 常被其他用户占用
- 选卡：`CUDA_VISIBLE_DEVICES=0/1/2/3`

### 常用命令
```bash
# 跑实验（H100 专属脚本）
cd /public/home/caiyiwen/code/moe-test
bash tools/h100/h100_run_concentration_dense.sh    # Dense concentration
bash tools/h100/h100_run_concentration_moe.sh      # MoE concentration
bash tools/h100/h100_run_routing.sh                # Routing-attention 全系列

# 查包
/public/home/caiyiwen/.local/bin/uv pip list --python .venv-h100/bin/python
```

## 两台机器的关键差异（重要）

| 项 | A800 | H100 |
|----|------|------|
| 项目目录 | `/home/caiyiwen/moe_kv_cache_experiments` | `/public/home/caiyiwen/code/moe-test` |
| home 根 | `/home/caiyiwen/` | `/public/home/caiyiwen/`（NFS） |
| 模型位置 | 项目内 `models/` | 项目外 `/public/home/caiyiwen/models/` |
| Python | 3.13（`.venv`） | 3.12（`.venv-h100`） |
| uv 路径 | `/storage/caiyiwen/.local/bin/uv` | `/public/home/caiyiwen/.local/bin/uv` |
| vLLM torch | cu130 ⚠️ 待修 | cu126 ✅ |
| 实验状态 | 历史已完成 | 复现 + 新工作（2026-07-04 起） |
| 规划文件 | `*.md`（无前缀） | `*_h100.md` |

## 实验框架（两台通用）

项目用 HuggingFace Transformers 框架（不用 vLLM 做 attention 分析，因为要拿 attention weights）：

- `src/run_experiment.py` — Attention Concentration 主入口（`--source longbench --layerwise`）
- `src/run_routing_attention_analysis.py` — Routing-Attention 联合分析（MoE only）
- `src/load_model.py` — INT4 NF4 量化 + eager attention（必须 eager，否则拿不到 weights）
- `src/attention_hook.py` — 3 种 attention 采集模式（output/hook/layerwise）
- `src/concentration.py` — 指标计算（Gini / power-law α / entropy / top-K / effective KV）
- `src/data.py` — LongBench 数据加载（`PROJECT_DIR` 已改为自适应，兼容两台机器）

### 跨机对比实验注意
- **输入一致性已验证**：manifest / raw jsonl / tokenizer / data.py 两边 md5 全部一致
- Qwen3-8B 和 Qwen3-30B-A3B 用**同一套 tokenizer**，Dense vs MoE 天然输入对齐
- 跨机数值差异只来自硬件（H100 vs A800/Blackwell）和量化噪声，可视为可复现

## 排错速查

| 问题 | 解决 |
|------|------|
| H100 连接超时/重置 | 用 tmux 跑长任务；或设探针循环重连 |
| `pip list` 在 H100 venv 报空 | 用 `uv pip list --python .venv-h100/bin/python` |
| A800 GPU0 被占 | 换 GPU1/2，或等其他用户释放（furongtian 常占 1/2） |
| H100 GPU 4-7 被占 | 用 GPU 0-3 |
| A800 找不到模型 | 路径是项目内 `models/`，不是 `/storage/caiyiwen/models/` |
| H100 data.py 报 manifest not found | 已修复（PROJECT_DIR 自适应），若仍报错设 `MOE_PROJECT_DIR` 环境变量 |
| nvcc 报 `invalid option` | 用 `/usr/local/cuda-12.8/bin/nvcc` 全路径，不要用 `/usr/bin/nvcc` |
