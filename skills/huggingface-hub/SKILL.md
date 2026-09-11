---
name: huggingface-hub
description: "通过 Hugging Face CLI 查找和操作模型、数据集及 Hub 仓库，处理实际下载路径和版本。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# huggingface-hub

## 使用方式
先定位 `hf` 并读取所用子命令 `--help`，沿用现有认证；不输出 token。下载前确认 repo ID、revision、所需文件和目标目录。
只下载任务所需权重/数据子集；用户指定的模型位置是事实源，不为方便再创建一份大型模型副本。下载后核对文件完整性、revision 与后续加载路径。
发布或更新 Hub 内容仅在用户要求时执行，核对目标仓库与文件范围。

## 常见入口
`hf download`、`hf repo`、`hf auth` 的具体选项以本机帮助为准。需要额外 Python API 时使用当前库文档，不依赖旧版本参数。
命令成功后验证磁盘文件或远端结果，并报告实际保存位置。
