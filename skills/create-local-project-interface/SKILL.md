---
name: create-local-project-interface
description: "为远程服务器项目创建或更新本机元信息接口目录，核实接入路径和环境差异。"
---

# create-local-project-interface

## 接口约定
本机接口只放元信息，代码、数据、模型和结果保留在远程。用 SSH 实际确认路径、环境和项目状态，不依据旧记忆填入“已验证”信息。
按需要生成 README、ACCESS、ENVIRONMENTS、AGENTS，以及适用的 MODELS/DATASETS/RESULTS；简单项目不强制七文件。
多机路径用绝对路径，明确模型位于项目内还是项目外；Python/uv/nvcc 差异和已知踩坑写到对应文件。

## 模板与验证
按需读取 [interface-templates.md](references/interface-templates.md)。更新已有接口时复用原文件，不创建第二个事实源。
核对所有引用路径来自实际查询，环境状态标注采集时间。本机不能混入远程代码、数据或模型副本。
