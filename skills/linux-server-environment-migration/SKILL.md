---
name: linux-server-environment-migration
description: "在 Linux 服务器之间迁移或搭建用户开发环境，保留本人的路径适配与 shell 排错经验。"
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# linux-server-environment-migration

## 迁移顺序
先检查 SSH、源/目标 home、权限、现有工具、shell 配置与 CUDA 环境。只迁移任务要求的配置，包版本以目标环境和项目锁定版本为准。
用户级安装优先；不假定有 sudo，不在未需要时安装整套工具或 conda。涉及密钥保留在机器外置配置，不写入仓库。
迁移前保留原配置，适配 home/PATH/venv/nvcc 位置，再在非交互与交互 shell 中分别验证。

## 已验证陷阱
- zsh `source *.zsh` 只 source 第一个文件；应循环逐个 source。详见 [zsh-source-glob-gotcha.md](references/zsh-source-glob-gotcha.md)。
- sed 去注释块时不能损坏 conda 初始化标记。
- 源机器的绝对路径必须逐项适配；通过 SSH 写大块配置时使用引用安全的文件传输或 heredoc。
验证需要的工具定位、插件加载、环境解释器和 CUDA 版本；不用输出密钥值证明环境设置成功。
