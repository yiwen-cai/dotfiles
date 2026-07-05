# 技术模型调研报告模板

## 用途

当用户要求对某个 AI 模型（如 LLM、多模态模型、编码模型）进行技术调研并生成报告时使用。本模板补充了 `paper-note-generator` 的论文笔记能力，覆盖**无独立技术论文的模型**（如 Kimi K2.6、K2.7 Code）的调研场景。

## 适用场景

- 模型只有官方博客/发布页，没有 arXiv 论文
- 模型有 Hugging Face Model Card 但缺乏训练细节
- 需要整合第三方独立分析（如 Kili Technology、Artificial Analysis）
- 需要生成图文并茂的 HTML/PDF 调研报告

## 调研流程

### Phase 1 — 信息收集

1. **官方渠道**：
   - 官方博客/发布页（kimi.com/blog, openai.com/blog 等）
   - Hugging Face Model Card
   - API 文档

2. **学术渠道**：
   - arXiv 基础论文（如 K2 系列的基础报告 arXiv: 2507.20534）
   - Google Scholar 引用分析

3. **第三方分析**：
   - 独立评测机构（Artificial Analysis, Kili Technology）
   - 技术社区深度解读（Reddit, Hacker News, 知乎）
   - 云服务商部署指南（Cloudflare, Fireworks, Baseten）

### Phase 2 — 数据整理

建立结构化数据档案（JSON/Python dict）：

```python
model_data = {
    "model_info": {
        "name": "模型名称",
        "developer": "开发公司",
        "release_date": "发布日期",
        "model_type": "开源/闭源/开源权重",
        "positioning": "模型定位"
    },
    "architecture": {
        "type": "架构类型",
        "total_params": "总参数量",
        "active_params_per_token": "激活参数",
        "layers": 层数,
        "hidden_dim": 隐藏维度,
        "context_window": "上下文长度"
    },
    "training": {
        "pretraining_data": "预训练数据量",
        "data_mix": ["数据构成"],
        "batch_size": "batch size",
        "lr_schedule": "学习率",
        "post_training": ["后训练步骤"]
    },
    "benchmarks": {
        "coding": {"benchmark_name": {"model_a": score, "model_b": score}},
        "reasoning": {},
        "agentic": {}
    },
    "deployment": {
        "providers": ["部署平台"],
        "pricing": {"input": "价格", "output": "价格"}
    }
}
```

### Phase 3 — 图表生成

使用 matplotlib 生成专业图表：

1. **基准对比柱状图**：多模型在编码/推理/Agentic 基准上的对比
2. **雷达图**：多维度能力评估
3. **架构示意图**：MoE 结构、注意力机制等
4. **训练流程图**：预训练 → SFT → RL 的 pipeline
5. **部署架构图**：多平台部署拓扑

图表规范：
- 300 DPI 高分辨率
- 专业配色（深蓝 #1a365d、橙色 #ed8936、灰色系）
- 中文字体支持（霞鹜文楷 LXGW WenKai 或 Heiti SC）
- 适合嵌入 HTML 的尺寸

### Phase 4 — 报告生成

#### HTML 报告结构

```
1. 封面（渐变背景、标题、副标题、作者信息）
2. 目录（可点击锚点导航）
3. 执行摘要（核心结论、关键数据卡片）
4. 模型概览（定位、发布信息、访问渠道）
5. 架构设计（参数表、架构图、设计特点）
6. 训练方法（预训练配置、后训练创新、流程图）
7. 基准测试（编码/推理/Agentic 三大维度，含图表）
8. 核心特性（长程编码、Agent Swarm、主动代理等）
9. 部署与生态（平台、定价、集成）
10. 竞品对比（多维度对比表、优势劣势）
11. 局限与风险（技术局限、信息风险、部署考量）
12. 结论与建议（适用场景、技术建议、未来展望）
13. 参考来源（所有引用链接）
```

#### CSS 设计规范

- 主色：#1a365d（深蓝）
- 强调色：#ed8936（橙色）
- 成功色：#38a169（绿色）
- 背景：#f7fafc（浅灰）
- 卡片阴影：0 2px 8px rgba(0,0,0,0.06)
- 圆角：12px
- 字体：系统字体栈（-apple-system, BlinkMacSystemFont, Segoe UI, Roboto）

#### 交互功能

- 平滑滚动导航
- 章节高亮（滚动时自动高亮当前章节）
- 响应式布局（支持移动端）
- 进度条可视化

### Phase 5 — 验证

1. 浏览器打开验证所有图表加载
2. 检查导航锚点是否正确
3. 验证响应式布局
4. 确认无内容重复或遗漏

## 关键注意事项

### 信息来源标注

- **官方数据**：标注来源（官方博客、Model Card）
- **第三方数据**：标注独立评测机构名称
- **推测内容**：明确标注为"基于第三方分析推测"或"尚未经独立验证"
- **缺失信息**：明确标注"官方未公开"或"论文中未找到该数据"

### 无独立技术论文的处理

当模型没有独立技术论文时：

1. 明确说明"该模型没有独立技术报告"
2. 列出所有可用信息来源（官方博客、Model Card、第三方分析）
3. 标注哪些信息是官方公开的，哪些是第三方推测的
4. 对于缺失的关键细节（训练数据构成、计算量等），明确标注缺失

### 基准对比注意事项

1. **评估环境差异**：不同模型可能使用不同的评估工具（如 K2.6 使用 Kimi Code CLI，GPT-5.4 使用 Codex），需标注
2. **统计显著性**：小幅度领先（如 +0.9）可能受噪声影响，需说明
3. **多次运行**：优先引用多次独立运行的平均值
4. **工具增强**：区分"无工具"和"有工具"的基准结果

## 文件结构

```
k2_6_report/                    # 报告目录
├── index.html                  # 主报告
├── charts/                     # 图表目录
│   ├── chart1_benchmark_comparison.png
│   ├── chart2_reasoning_radar.png
│   ├── chart3_agentic_comparison.png
│   ├── chart4_hallucination.png
│   ├── chart5_moe_architecture.png
│   ├── chart6_training_pipeline.png
│   └── chart7_deployment_architecture.png
└── generate_charts.py          # 图表生成脚本（可复用）
```

## 示例

参见本次会话生成的 Kimi K2.6 技术调研报告：
- 报告路径：`/Users/yiwencai/wiki/k2_6_report/index.html`
- 图表路径：`/Users/yiwencai/wiki/k2_6_report/charts/`
- 数据整理：基于官方博客、K2 基础论文 (arXiv: 2507.20534)、Hugging Face Model Card、Kili Technology 独立分析
