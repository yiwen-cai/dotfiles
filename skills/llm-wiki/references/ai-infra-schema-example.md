# AI/ML Infra Schema Example

Example SCHEMA.md for a user working on LLM inference optimization, GPU kernel development, CUDA/Triton.

Use this when the user's existing wiki has a generic SCHEMA (e.g., "knowledge management survey") but their actual work is in AI/ML infrastructure.

## Domain

AI/ML 研究 — 聚焦 LLM 推理加速、GPU 算子优化、CUDA/Triton 技术栈，兼顾模型架构与训练方法

## Tag Taxonomy

### Core Research Areas
- `inference` — 推理优化（vLLM, TensorRT-LLM, speculative decoding, continuous batching）
- `kernel-optimization` — 算子层优化（GEMM, fused kernel, custom op, operator fusion）
- `cuda` — CUDA 编程与优化（PTX, SASS, shared memory, warp shuffle, cooperative groups）
- `triton` — Triton DSL 与编译器（tile scheduling, memory coalescing, autotune）
- `sparse-computation` — 稀疏计算（sparse attention, sparse matrix, structured sparsity）

### Model Architecture & Training
- `moe` — Mixture of Experts 架构与优化（routing, load balancing, expert parallelism）
- `attention-optimization` — 注意力优化（FlashAttention, PagedAttention, linear attention, MQA, GQA）
- `quantization` — 量化技术（INT8, FP8, AWQ, GPTQ, SmoothQuant, KV cache quantization）
- `memory-optimization` — 内存优化（KV cache management, activation checkpointing, offloading, paging）
- `distributed-training` — 分布式训练（TP, PP, DP, EP, FSDP, 3D parallelism）
- `distributed-inference` — 分布式推理（tensor parallelism, pipeline parallelism, expert parallelism）

### System & Graph
- `graph-optimization` — 计算图优化（torch.compile, ONNX, graph capture, CUDA graphs）
- `compiler` — 编译器技术（XLA, TVM, MLIR, Triton compiler passes）
- `scheduling` — 调度优化（prefill-decode disaggregation, chunked prefill, dynamic batching）

### Domain & Meta
- `llm` — 大语言模型（architecture, training, pretraining, post-training）
- `ai` — 人工智能通用
- `optimization` — 优化方法论（mathematical optimization, auto-tuning, profiling）
- `benchmark` — 评测与基准（throughput, latency, TPS, roofline analysis）
- `paper` — 论文笔记（arXiv, conference, key results, reproduction notes）
- `tool` — 工具与框架（vLLM, SGLang, TensorRT-LLM, DeepSpeed, Megatron-LM）
- `person` — 研究者与工程师
- `company` — 公司与实验室（OpenAI, Anthropic, DeepSeek, Meta AI, NVIDIA, 华为）
- `comparison` — 对比分析
- `timeline` — 技术演进时间线
- `study-plan` — 学习计划与课程（CS336, CUDA mode, Triton tutorial）
- `project` — 个人项目记录（competition, internship work）

## Page Thresholds

- **Create a `paper/` page** for every paper you read — even if only one source, central enough
- **Create a `tool/` page** for every framework/library you use in depth
- **Create a `project/` page** for your own projects and competition work
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Split a page** when it exceeds ~200 lines
