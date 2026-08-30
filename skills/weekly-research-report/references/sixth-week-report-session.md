# 第六周周报会话参考

## 场景

用户准备撰写本周周报，主题为：推进 CS336 Assignment 2，以及调研 KV Cache 相关文献并准备第一次汇报。

## 本次确认的本地材料位置

- 周报目录：`/Users/yiwencai/Documents/study/weekpaper`
- 本周输出文件：`/Users/yiwencai/Documents/study/weekpaper/第六周周报.md`
- KV Cache 汇报材料目录：`/Users/yiwencai/Documents/study/第一次汇报分享`

## KV Cache 汇报材料结构

`/Users/yiwencai/Documents/study/第一次汇报分享` 中包含：

- `kv_cache_optimization_outline_and_reading_list.md`：完整汇报定位、45 分钟大纲、详细分节内容和阅读列表。
- `kv_cache_complete_ppt_description.md`：约 31 页 PPT 的页面标题、布局、正文要点、图示要求、代表论文和演讲者备注。
- `part1_explanation.md` 至 `part6_explanation.md`：6 个部分的讲稿/解释稿。
- `part1_ppt.md` 至 `part6_ppt.md`：6 个部分的 PPT 页面稿。
- `paper_notes/`：KV Cache 相关论文或技术报告笔记索引，本次统计到 28 篇代表性工作。
- 已生成 PPT：`长上下文 LLM 推理中的 KV Cache 优化综述：系统管理、缓存压缩与架构协同.pptx`。

汇报主线可概括为：

```text
KV Cache 是长上下文推理的核心瓶颈
    ↓
PagedAttention / vLLM 解决动态显存管理问题
    ↓
Eviction / Quantization / Semantic Compression 减少 cache 成本
    ↓
MQA / GQA / MLA 从架构层减少 KV Cache
    ↓
2025-2026 新趋势：reasoning-aware、multi-tier、serving-aware、verification-based cache
```

## CS336 Assignment 2 远端状态采集

远端路径：

```text
/storage/caiyiwen/code/cs336/assignment/assignment2-systems
```

推荐状态检查命令：

```bash
ssh a800 "export PATH='/storage/caiyiwen/.local/bin:\$PATH' && cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && pwd && git status --short && (uv run pytest -q || true)"
```

本次采集到的状态：

- 修改/新增文件包括：`cs336-basics/cs336_basics/model.py`、`cs336-basics/pyproject.toml`、`pyproject.toml`、`uv.lock`、`cs336_assignment2_systems_translate.pdf`、`cs336_systems/benchmark.py`。
- `cs336_systems/benchmark.py` 为 127 行，支持 forward/backward/train microbenchmark。
- 全量测试结果：`14 failed in 70.76s`。
- 失败项集中在 FlashAttention、DistributedDataParallel、FullyShardedDataParallel、Sharded Optimizer。
- 失败原因定位到 `tests/adapters.py` 中对应接口仍为 `NotImplementedError`，不要写成数值错误或实现已完成。

## Benchmark sanity check

推荐最小验证命令：

```bash
ssh a800 "export PATH='/storage/caiyiwen/.local/bin:\$PATH' && cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems && uv run python cs336_systems/benchmark.py --batch-size 1 --context-length 16 --num-layers 1 --d-model 64 --num-heads 4 --d-ff 128 --warmup-steps 1 --measure-steps 2 --mode train"
```

本次输出：

```text
forward mean: 0.004592599987518042s, std: 0.00022035700385458767s
backward mean: 0.005381451497669332s, std: 0.0006113645067671314s
optim mean: 0.004196567984763533s, std: 0.00024287300766445696s
```

## 重要命令转义注意点

通过本地 shell 调用 `ssh a800 "... $PATH ..."` 时，远端 `$PATH` 容易被本地 shell 提前展开，导致远端 `uv` 找不到。应在命令字符串中写成 `\$PATH`，例如：

```bash
ssh a800 "export PATH='/storage/caiyiwen/.local/bin:\$PATH' && cd /path/to/project && uv run pytest -q"
```

这是可复用的远端状态采集模式；不要把一次性的 `uv: command not found` 记录成长期环境故障。

## 写作处理方式

- 将 CS336 写成“Assignment 2 启动与 profiling/benchmark 框架搭建”，不要夸大为系统模块完成。
- 将 `14 failed` 写入“当前问题/后续验收目标”，而非完成项。
- KV Cache 部分可作为本周主要成果，突出“文献体系梳理 + 汇报结构 + PPT/讲稿材料准备”。
- 用户说“遇到问题略”时仍可基于真实测试状态和材料复杂度写技术风险，但不要虚构阻塞性问题。
