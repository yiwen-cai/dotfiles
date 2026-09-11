# Skill 审查建议（2026-09-06）

结论：保留个人流程、真实工具接入和可核验资料，移除通用专家角色与重复入口。低频能力移出自动发现目录，并不等于永久删除。此报告记录迁移前的审查建议；后续已按批准方案实施，执行结果见 docs/skill-migration/RESULTS.md。表中链接指向保存的原件，原始分类不等于最终部署分类。

## 范围与证据边界

- 仓库 skills/：150 个；skills-local/：5 个。
- ~/.codex/skills：152 个顶层 skill（150 个主树副本、bupt-thesis-writer 和全局独有 zhihu）；这些仓库对应项的 SKILL.md 内容一致，不是两套独立设计。
- ~/.agents/skills：8 个（4 个 GPU skill 链接，以及 find-skills、orca-cli、orchestration、publish-note）。
- 合计 160 个自定义名称；另发现 .system 下 6 个目录，系统维护内容不计入删减。运行时/插件自带 skill 由对应系统管理，不与个人文件混删。
- 全量检查了目录、SKILL.md 元数据/结构、脚本与引用清单，对个人主线、重复入口和风险项重点读正文；未逐一执行工具，也未穷尽全部 references。分类属于有证据的架构判断，不是每个 skill 的功能验收。
- 参考近期 25 条任务的标题/摘要及项目资料：GPU/推理性能、FlashAttention、KV Cache、Flow Matching/Diffusion 学习、H100 环境、博客/知乎。由此推断职业主线偏 AI 研究及系统工程；没有据此断言具体职位或当前学历，也没有把缺少近期任务当作从不使用。

## 决策原则

价值 ≈ 使用频率 × 对正确率/效率的实际增量 − 触发歧义、过时状态和流程负担。

1. 删除后若只损失“你是资深专家”“认真测试”“翻译准确”等通用要求，优先移除。
2. 删除后若会损失私人路径、特定格式、已验证踩坑、脚本、源码索引，保留这些资产。
3. 特定项目才成立的规则放到项目；全局只保留跨项目且常用的入口。
4. 工具自带且持续更新的操作说明由工具维护；个人 skill 保存差异，避免复制整个旧版本。
5. 不把知识/推理能力等同于外部能力：媒体生成、OCR、数据库、GPU 实测与排版验证仍需要真实工具。
6. 目录中的所有正文不一定每轮全部加载；精简的主要收益是降低入口竞争、错误路由与陈旧指令，不能把总文件大小当作每轮 token 节省。

## 优先处理的实际问题

1. 四个 GPU skill 共五个资料链接指向 $HOME/code/agent-gpu-skills/...，当前 Mac 不存在；包括 Triton quick-reference。保留优先级很高，但必须修复路径或明确通过远程访问。README 却描述 ~/code/agent-gpu-skills，文档也需校正。
2. scripts/skills-targets.sh 对 Codex 主树使用全量部署，install/check 流程含 rsync --delete，仅保护 .system。zhihu 不在仓库期望树，按当前机制重新部署存在删除它的风险；先纳管或设明确排除规则。README 列出 agents 目标，实际 SKILL_TARGETS 没有该项。
3. 不应直接删全局副本后运行 install.sh，它会重建；真正精简需要修改源目录布局及每个宿主的部署清单。归档区必须位于自动发现与部署树之外。
4. quiz 把 3–7 题逐题答对作为提交/合并门禁，brainstorm 等还有硬前置依赖；对学习任务有选择价值，对一般交付负担过大。建议取消默认链路，保留显式学习模式。
5. subagent-driven-development 绑定 delegate_task 与 kimi-k2.6；旧浏览器 skill 绑定 browser-client/Node REPL；macos-computer-use 假定 computer_use。与本会话当前工具协议不同，不应全局强制触发。
6. testing-quality-assurance/scripts/triton_kernel_numerical_harness.py 实际是含 Markdown 代码围栏与 NotImplementedError 的适配模板，并非可直接运行的验证器；不能因为有 scripts 目录就高估成熟度。
7. 系统/运行时与仓库的同名文件并非字节一致。去重前须迁出个人修改，尤其是 powerpoint 的文献综述提示、resume-review 的问题清单、工程类里的真实 Hermes 踩坑。

## 建议规模

不要定一个必须凑齐的数量。可先以约 15–25 个全局自定义入口为试运行范围：下表“保留”的 9 个，加上合并后的少量入口，以及确实跨项目高频的 GPU/科研短路由。系统自带能力另计，项目 skill 按项目加载。

“合并”表示保留有效内容后移除冗余入口；“移除”默认指从自定义自动加载集合移除，保留版本历史。不是要求立即永久删除整目录。

## 分类数量

- 保留：9 个原始入口。
- 移到项目：10 个原始入口。
- 合并：40 个原始入口。
- 归档：64 个原始入口。
- 移除：37 个原始入口。

## 保留

| Skill | 判断理由 / 去向 |
|---|---|
| [academic-research-output](/Users/yiwencai/Documents/code/dotfiles/skills-archive/academic-research-output/SKILL.md.disabled) | 科研输出规范、既有知识库结构或论文笔记模板是个人资产；缩短入口，详细知识放 references。 |
| [course-learning-planner](/Users/yiwencai/Documents/code/dotfiles/skills-archive/course-learning-planner/SKILL.md.disabled) | 保留个人学习边界、讲课与作业顺序；CS336 专属进度和案例迁回课程 skill，避免影响 MIT 等课程。 |
| [create-local-project-interface](/Users/yiwencai/Documents/code/dotfiles/skills-archive/create-local-project-interface/SKILL.md.disabled) | Mac 与远程 Linux 工作流中的接口目录约定、迁移经验有复用价值；易变环境信息现场读取。 |
| [huggingface-hub](/Users/yiwencai/Documents/code/dotfiles/skills-archive/huggingface-hub/SKILL.md.disabled) | 与模型下载、课程学习有关的工具入口；前者主要是命令参考，后者另有字幕提取脚本，价值不是通用总结能力。 |
| [linux-server-environment-migration](/Users/yiwencai/Documents/code/dotfiles/skills-archive/linux-server-environment-migration/SKILL.md.disabled) | Mac 与远程 Linux 工作流中的接口目录约定、迁移经验有复用价值；易变环境信息现场读取。 |
| [llm-wiki](/Users/yiwencai/Documents/code/dotfiles/skills-archive/llm-wiki/SKILL.md.disabled) | 科研输出规范、既有知识库结构或论文笔记模板是个人资产；缩短入口，详细知识放 references。 |
| [paper-note-generator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/paper-note-generator/SKILL.md.disabled) | 科研输出规范、既有知识库结构或论文笔记模板是个人资产；缩短入口，详细知识放 references。 |
| [youtube-content](/Users/yiwencai/Documents/code/dotfiles/skills-archive/youtube-content/SKILL.md.disabled) | 与模型下载、课程学习有关的工具入口；前者主要是命令参考，后者另有字幕提取脚本，价值不是通用总结能力。 |
| [zhihu](/Users/yiwencai/Documents/code/dotfiles/skills-archive/zhihu/SKILL.md.disabled) | 近期明确安装且与知乎内容工作相关；独有 CLI 接入。收窄 API/MCP 等泛化触发词；不把它误当作文章发布工具。 |

## 移到项目

| Skill | 判断理由 / 去向 |
|---|---|
| [bilingual-resume-typst](/Users/yiwencai/Documents/code/dotfiles/skills-archive/bilingual-resume-typst/SKILL.md.disabled) | 保留真实简历路径、中文事实源和只报告问题的偏好，放 CV 项目。 |
| [bupt-thesis-writer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/bupt-thesis-writer/SKILL.md.disabled) | 校级 LaTeX 模板和检查脚本不可由通用写作替代；论文项目保留，阶段结束后归档。 |
| [cs336-stanford-course](/Users/yiwencai/Documents/code/dotfiles/skills-archive/cs336-stanford-course/SKILL.md.disabled) | 保留具体课程约定、辅导边界、实验踩坑与资料；课程项目按需加载。 |
| [cuda-skill](/Users/yiwencai/Documents/code/dotfiles/skills-archive/cuda-skill/SKILL.md.disabled) | 核心 GPU/推理资料索引，强烈保留；优先在 GPU 项目暴露，频繁跨项目使用可留全局短入口。当前 Mac 的资料链接失效，需修复。 |
| [cutlass-skill](/Users/yiwencai/Documents/code/dotfiles/skills-archive/cutlass-skill/SKILL.md.disabled) | 核心 GPU/推理资料索引，强烈保留；优先在 GPU 项目暴露，频繁跨项目使用可留全局短入口。当前 Mac 的资料链接失效，需修复。 |
| [moe-project-access](/Users/yiwencai/Documents/code/dotfiles/skills-archive/moe-project-access/SKILL.md.disabled) | 保留接入知识，迁入项目 ACCESS/ENVIRONMENTS 与 AGENTS；GPU 占用、依赖版本、实验状态不应当作长期事实。 |
| [publish-note](/Users/yiwencai/Documents/code/dotfiles/skills-archive/publish-note/SKILL.md.disabled) | 保留个人 Hugo/Blowfish 分类、KaTeX 开关、清理规则与部署流程，放博客项目；移除示例中无差别 git add -A 的做法。 |
| [sglang-skill](/Users/yiwencai/Documents/code/dotfiles/skills-archive/sglang-skill/SKILL.md.disabled) | 核心 GPU/推理资料索引，强烈保留；优先在 GPU 项目暴露，频繁跨项目使用可留全局短入口。当前 Mac 的资料链接失效，需修复。 |
| [triton-skill](/Users/yiwencai/Documents/code/dotfiles/skills-archive/triton-skill/SKILL.md.disabled) | 核心 GPU/推理资料索引，强烈保留；优先在 GPU 项目暴露，频繁跨项目使用可留全局短入口。当前 Mac 的资料链接失效，需修复。 |
| [weekly-research-report](/Users/yiwencai/Documents/code/dotfiles/skills-archive/weekly-research-report/SKILL.md.disabled) | 保留导师周报的固定路径、格式与历史经验，放科研/周报工作区；跨项目经常调用时可留短路由。 |

## 合并

| Skill | 判断理由 / 去向 |
|---|---|
| [architecture-diagram](/Users/yiwencai/Documents/code/dotfiles/skills-archive/architecture-diagram/SKILL.md.disabled) | 跨宿主需要时保留一个 HTML/图示入口及独有模板；Codex 内优先现有 visualize。不要对普通解释强制生成 HTML。 |
| [automated-daily-briefings](/Users/yiwencai/Documents/code/dotfiles/skills-archive/automated-daily-briefings/SKILL.md.disabled) | 合成一个科研信息收集入口；保留源列表、去重/质量规则与既有管线排错，调度交给当前宿主。 |
| [blindspot-pass](/Users/yiwencai/Documents/code/dotfiles/skills-archive/blindspot-pass/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [brainstorm](/Users/yiwencai/Documents/code/dotfiles/skills-archive/brainstorm/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [documents](/Users/yiwencai/Documents/code/dotfiles/skills-archive/documents/SKILL.md.disabled) | Codex 使用当前运行时插件版，源仓库副本不再重复部署；先核对自定义差异、模板及其他宿主需求。此结论不是说模型天生会可靠处理 Office 文件。 |
| [explaination](/Users/yiwencai/Documents/code/dotfiles/skills-archive/explaination/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [gh-address-comments](/Users/yiwencai/Documents/code/dotfiles/skills-archive/gh-address-comments/SKILL.md.disabled) | 保留一个轻量 GitHub 入口及评论/CI 脚本，去掉相互冲突的 connector 优先与 gh 优先路由；常规 git/PR 操作无需五个入口。 |
| [gh-fix-ci](/Users/yiwencai/Documents/code/dotfiles/skills-archive/gh-fix-ci/SKILL.md.disabled) | 保留一个轻量 GitHub 入口及评论/CI 脚本，去掉相互冲突的 connector 优先与 gh 优先路由；常规 git/PR 操作无需五个入口。 |
| [github](/Users/yiwencai/Documents/code/dotfiles/skills-archive/github/SKILL.md.disabled) | 保留一个轻量 GitHub 入口及评论/CI 脚本，去掉相互冲突的 connector 优先与 gh 优先路由；常规 git/PR 操作无需五个入口。 |
| [github-operations](/Users/yiwencai/Documents/code/dotfiles/skills-archive/github-operations/SKILL.md.disabled) | 保留一个轻量 GitHub 入口及评论/CI 脚本，去掉相互冲突的 connector 优先与 gh 优先路由；常规 git/PR 操作无需五个入口。 |
| [html-artifact](/Users/yiwencai/Documents/code/dotfiles/skills-archive/html-artifact/SKILL.md.disabled) | 跨宿主需要时保留一个 HTML/图示入口及独有模板；Codex 内优先现有 visualize。不要对普通解释强制生成 HTML。 |
| [humanizer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/humanizer/SKILL.md.disabled) | 抽取符合个人口味的少量写作约束到写作偏好；无需单独的通用润色入口。 |
| [imagegen](/Users/yiwencai/Documents/code/dotfiles/skills-archive/imagegen/SKILL.md.disabled) | Codex 部署排除手工副本，使用 .system 维护版；文件内容并非完全相同，先迁移独有修改。其他宿主需要的版本仍可在源仓库保留。 |
| [implement](/Users/yiwencai/Documents/code/dotfiles/skills-archive/implement/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [interview](/Users/yiwencai/Documents/code/dotfiles/skills-archive/interview/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [linux-dev-environment](/Users/yiwencai/Documents/code/dotfiles/skills-archive/linux-dev-environment/SKILL.md.disabled) | 并入 linux-server-environment-migration；保留 zsh source glob 等实战记录。 |
| [nano-pdf](/Users/yiwencai/Documents/code/dotfiles/skills-archive/nano-pdf/SKILL.md.disabled) | 文档入口收敛；保留 powerpoint 学术文献综述提示和必要编辑脚本。OCR/特殊 PDF 编辑仍是按需工具能力，不应丢失。 |
| [ocr-and-documents](/Users/yiwencai/Documents/code/dotfiles/skills-archive/ocr-and-documents/SKILL.md.disabled) | 文档入口收敛；保留 powerpoint 学术文献综述提示和必要编辑脚本。OCR/特殊 PDF 编辑仍是按需工具能力，不应丢失。 |
| [openai-docs](/Users/yiwencai/Documents/code/dotfiles/skills-archive/openai-docs/SKILL.md.disabled) | Codex 部署排除手工副本，使用 .system 维护版；文件内容并非完全相同，先迁移独有修改。其他宿主需要的版本仍可在源仓库保留。 |
| [pdf](/Users/yiwencai/Documents/code/dotfiles/skills-archive/pdf/SKILL.md.disabled) | Codex 使用当前运行时插件版，源仓库副本不再重复部署；先核对自定义差异、模板及其他宿主需求。此结论不是说模型天生会可靠处理 Office 文件。 |
| [planning](/Users/yiwencai/Documents/code/dotfiles/skills-archive/planning/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [planning-with-files](/Users/yiwencai/Documents/code/dotfiles/skills-archive/planning-with-files/SKILL.md.disabled) | 长任务确需文件持久化时只保留一个入口和恢复脚本；不以超过 5 次工具调用强制创建三文件。 |
| [planning-with-files-zh](/Users/yiwencai/Documents/code/dotfiles/skills-archive/planning-with-files-zh/SKILL.md.disabled) | 长任务确需文件持久化时只保留一个入口和恢复脚本；不以超过 5 次工具调用强制创建三文件。 |
| [plugin-creator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/plugin-creator/SKILL.md.disabled) | Codex 部署排除手工副本，使用 .system 维护版；文件内容并非完全相同，先迁移独有修改。其他宿主需要的版本仍可在源仓库保留。 |
| [powerpoint](/Users/yiwencai/Documents/code/dotfiles/skills-archive/powerpoint/SKILL.md.disabled) | 文档入口收敛；保留 powerpoint 学术文献综述提示和必要编辑脚本。OCR/特殊 PDF 编辑仍是按需工具能力，不应丢失。 |
| [presentations](/Users/yiwencai/Documents/code/dotfiles/skills-archive/presentations/SKILL.md.disabled) | Codex 使用当前运行时插件版，源仓库副本不再重复部署；先核对自定义差异、模板及其他宿主需求。此结论不是说模型天生会可靠处理 Office 文件。 |
| [quiz](/Users/yiwencai/Documents/code/dotfiles/skills-archive/quiz/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [reference](/Users/yiwencai/Documents/code/dotfiles/skills-archive/reference/SKILL.md.disabled) | 取消通用任务的八段前置依赖；必要提炼到简短交付约定。保留主动触发的设计探索/学习测验，quiz 不作为一般提交门禁。 |
| [research-content-monitoring](/Users/yiwencai/Documents/code/dotfiles/skills-archive/research-content-monitoring/SKILL.md.disabled) | 合成一个科研信息收集入口；保留源列表、去重/质量规则与既有管线排错，调度交给当前宿主。 |
| [resume-review](/Users/yiwencai/Documents/code/dotfiles/skills-archive/resume-review/SKILL.md.disabled) | 合入 bilingual-resume-typst，保留 references/common-issues.md 后移除第二入口。 |
| [skill-creator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/skill-creator/SKILL.md.disabled) | Codex 部署排除手工副本，使用 .system 维护版；文件内容并非完全相同，先迁移独有修改。其他宿主需要的版本仍可在源仓库保留。 |
| [skill-installer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/skill-installer/SKILL.md.disabled) | Codex 部署排除手工副本，使用 .system 维护版；文件内容并非完全相同，先迁移独有修改。其他宿主需要的版本仍可在源仓库保留。 |
| [software-development-planning](/Users/yiwencai/Documents/code/dotfiles/skills-archive/software-development-planning/SKILL.md.disabled) | 长任务确需文件持久化时只保留一个入口和恢复脚本；不以超过 5 次工具调用强制创建三文件。 |
| [software-quality-workflows](/Users/yiwencai/Documents/code/dotfiles/skills-archive/software-quality-workflows/SKILL.md.disabled) | 保留数值核验、快照排错与历史案例到 GPU 或相关项目；通用测试口号删去。所谓 Triton .py 脚本实际包含 Markdown 围栏与占位符，应作为模板管理。 |
| [specialized-document-generator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/specialized-document-generator/SKILL.md.disabled) | 文档入口收敛；保留 powerpoint 学术文献综述提示和必要编辑脚本。OCR/特殊 PDF 编辑仍是按需工具能力，不应丢失。 |
| [spreadsheets](/Users/yiwencai/Documents/code/dotfiles/skills-archive/spreadsheets/SKILL.md.disabled) | Codex 使用当前运行时插件版，源仓库副本不再重复部署；先核对自定义差异、模板及其他宿主需求。此结论不是说模型天生会可靠处理 Office 文件。 |
| [sync-moe-project](/Users/yiwencai/Documents/code/dotfiles/skills-archive/sync-moe-project/SKILL.md.disabled) | 合入 MoE 项目接入/状态检查流程；与 access 对 Qwen3-8B 下载状态的描述已冲突。 |
| [template-creator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/template-creator/SKILL.md.disabled) | Codex 使用当前运行时插件版，源仓库副本不再重复部署；先核对自定义差异、模板及其他宿主需求。此结论不是说模型天生会可靠处理 Office 文件。 |
| [testing-quality-assurance](/Users/yiwencai/Documents/code/dotfiles/skills-archive/testing-quality-assurance/SKILL.md.disabled) | 保留数值核验、快照排错与历史案例到 GPU 或相关项目；通用测试口号删去。所谓 Triton .py 脚本实际包含 Markdown 围栏与占位符，应作为模板管理。 |
| [yeet](/Users/yiwencai/Documents/code/dotfiles/skills-archive/yeet/SKILL.md.disabled) | 保留一个轻量 GitHub 入口及评论/CI 脚本，去掉相互冲突的 connector 优先与 gh 优先路由；常规 git/PR 操作无需五个入口。 |

## 归档

| Skill | 判断理由 / 去向 |
|---|---|
| [airtable](/Users/yiwencai/Documents/code/dotfiles/skills-archive/airtable/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [apikey-image-gen](/Users/yiwencai/Documents/code/dotfiles/skills-archive/apikey-image-gen/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [apple-ecosystem-automation](/Users/yiwencai/Documents/code/dotfiles/skills-archive/apple-ecosystem-automation/SKILL.md.disabled) | 真实工具接入，不能用通用能力替代；有知识同步或办公任务时按需启用，已有插件覆盖的功能只保留个人差异。 |
| [ascii-art](/Users/yiwencai/Documents/code/dotfiles/skills-archive/ascii-art/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [ascii-video](/Users/yiwencai/Documents/code/dotfiles/skills-archive/ascii-video/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [audiocraft](/Users/yiwencai/Documents/code/dotfiles/skills-archive/audiocraft/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [baoyu-visual-content](/Users/yiwencai/Documents/code/dotfiles/skills-archive/baoyu-visual-content/SKILL.md.disabled) | 保留图示/数学动画/设计的格式知识和模板，按输出类型启用；主线是学习与技术表达，无需所有绘图入口常驻。 |
| [comfyui](/Users/yiwencai/Documents/code/dotfiles/skills-archive/comfyui/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [debugging-hermes-tui-commands](/Users/yiwencai/Documents/code/dotfiles/skills-archive/debugging-hermes-tui-commands/SKILL.md.disabled) | 保留 Hermes 源码/环境知识，维护 Hermes 时启用或移入其项目；最近任务样本未显示它仍是主线，不据此永久删除。 |
| [debugging-with-inspect](/Users/yiwencai/Documents/code/dotfiles/skills-archive/debugging-with-inspect/SKILL.md.disabled) | 相关技术参考，但目前多为通用教程/工具速查；具体项目用到该栈再加载。评测协议、已验证配置和真实排错沉淀后可升级为核心。 |
| [design-md](/Users/yiwencai/Documents/code/dotfiles/skills-archive/design-md/SKILL.md.disabled) | 保留图示/数学动画/设计的格式知识和模板，按输出类型启用；主线是学习与技术表达，无需所有绘图入口常驻。 |
| [dspy](/Users/yiwencai/Documents/code/dotfiles/skills-archive/dspy/SKILL.md.disabled) | 相关技术参考，但目前多为通用教程/工具速查；具体项目用到该栈再加载。评测协议、已验证配置和真实排错沉淀后可升级为核心。 |
| [excalidraw](/Users/yiwencai/Documents/code/dotfiles/skills-archive/excalidraw/SKILL.md.disabled) | 保留图示/数学动画/设计的格式知识和模板，按输出类型启用；主线是学习与技术表达，无需所有绘图入口常驻。 |
| [external-coding-agents](/Users/yiwencai/Documents/code/dotfiles/skills-archive/external-coding-agents/SKILL.md.disabled) | 宿主专用的代理编排协议，按 Hermes/Orca/外部 CLI 场景启用；不应全局覆盖 Codex 原生工具和模型选择。 |
| [feishu](/Users/yiwencai/Documents/code/dotfiles/skills-archive/feishu/SKILL.md.disabled) | 真实工具接入，不能用通用能力替代；有知识同步或办公任务时按需启用，已有插件覆盖的功能只保留个人差异。 |
| [gif-search](/Users/yiwencai/Documents/code/dotfiles/skills-archive/gif-search/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [godmode](/Users/yiwencai/Documents/code/dotfiles/skills-archive/godmode/SKILL.md.disabled) | 当前主线之外的游戏/工具/红队场景；从日常全局集移出，有明确项目再启用。 |
| [google-workspace](/Users/yiwencai/Documents/code/dotfiles/skills-archive/google-workspace/SKILL.md.disabled) | 真实工具接入，不能用通用能力替代；有知识同步或办公任务时按需启用，已有插件覆盖的功能只保留个人差异。 |
| [grok-image-to-video](/Users/yiwencai/Documents/code/dotfiles/skills-archive/grok-image-to-video/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [heartmula](/Users/yiwencai/Documents/code/dotfiles/skills-archive/heartmula/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [hermes-agent](/Users/yiwencai/Documents/code/dotfiles/skills-archive/hermes-agent/SKILL.md.disabled) | 保留 Hermes 源码/环境知识，维护 Hermes 时启用或移入其项目；最近任务样本未显示它仍是主线，不据此永久删除。 |
| [hermes-agent-skill-authoring](/Users/yiwencai/Documents/code/dotfiles/skills-archive/hermes-agent-skill-authoring/SKILL.md.disabled) | 保留 Hermes 源码/环境知识，维护 Hermes 时启用或移入其项目；最近任务样本未显示它仍是主线，不据此永久删除。 |
| [hermes-desktop-environment](/Users/yiwencai/Documents/code/dotfiles/skills-archive/hermes-desktop-environment/SKILL.md.disabled) | 保留 Hermes 源码/环境知识，维护 Hermes 时启用或移入其项目；最近任务样本未显示它仍是主线，不据此永久删除。 |
| [hermes-memory-providers](/Users/yiwencai/Documents/code/dotfiles/skills-archive/hermes-memory-providers/SKILL.md.disabled) | 保留 Hermes 源码/环境知识，维护 Hermes 时启用或移入其项目；最近任务样本未显示它仍是主线，不据此永久删除。 |
| [hermes-s6-container-supervision](/Users/yiwencai/Documents/code/dotfiles/skills-archive/hermes-s6-container-supervision/SKILL.md.disabled) | 保留 Hermes 源码/环境知识，维护 Hermes 时启用或移入其项目；最近任务样本未显示它仍是主线，不据此永久删除。 |
| [himalaya](/Users/yiwencai/Documents/code/dotfiles/skills-archive/himalaya/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [hyperframes](/Users/yiwencai/Documents/code/dotfiles/skills-archive/hyperframes/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [jupyter-live-kernel](/Users/yiwencai/Documents/code/dotfiles/skills-archive/jupyter-live-kernel/SKILL.md.disabled) | 相关技术参考，但目前多为通用教程/工具速查；具体项目用到该栈再加载。评测协议、已验证配置和真实排错沉淀后可升级为核心。 |
| [kanban-codex-lane](/Users/yiwencai/Documents/code/dotfiles/skills-archive/kanban-codex-lane/SKILL.md.disabled) | 宿主专用的代理编排协议，按 Hermes/Orca/外部 CLI 场景启用；不应全局覆盖 Codex 原生工具和模型选择。 |
| [kanban-orchestrator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/kanban-orchestrator/SKILL.md.disabled) | 宿主专用的代理编排协议，按 Hermes/Orca/外部 CLI 场景启用；不应全局覆盖 Codex 原生工具和模型选择。 |
| [kanban-worker](/Users/yiwencai/Documents/code/dotfiles/skills-archive/kanban-worker/SKILL.md.disabled) | 宿主专用的代理编排协议，按 Hermes/Orca/外部 CLI 场景启用；不应全局覆盖 Codex 原生工具和模型选择。 |
| [kimi-webbridge](/Users/yiwencai/Documents/code/dotfiles/skills-archive/kimi-webbridge/SKILL.md.disabled) | 用于额外 MCP/浏览器桥接的专门入口；当前已有原生连接与浏览器工具，仅在特定宿主接入任务中启用。 |
| [linear](/Users/yiwencai/Documents/code/dotfiles/skills-archive/linear/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [llm-fine-tuning](/Users/yiwencai/Documents/code/dotfiles/skills-archive/llm-fine-tuning/SKILL.md.disabled) | 相关技术参考，但目前多为通用教程/工具速查；具体项目用到该栈再加载。评测协议、已验证配置和真实排错沉淀后可升级为核心。 |
| [llm-inference-serving](/Users/yiwencai/Documents/code/dotfiles/skills-archive/llm-inference-serving/SKILL.md.disabled) | 相关技术参考，但目前多为通用教程/工具速查；具体项目用到该栈再加载。评测协议、已验证配置和真实排错沉淀后可升级为核心。 |
| [lm-evaluation-harness](/Users/yiwencai/Documents/code/dotfiles/skills-archive/lm-evaluation-harness/SKILL.md.disabled) | 相关技术参考，但目前多为通用教程/工具速查；具体项目用到该栈再加载。评测协议、已验证配置和真实排错沉淀后可升级为核心。 |
| [manim-video](/Users/yiwencai/Documents/code/dotfiles/skills-archive/manim-video/SKILL.md.disabled) | 保留图示/数学动画/设计的格式知识和模板，按输出类型启用；主线是学习与技术表达，无需所有绘图入口常驻。 |
| [maps](/Users/yiwencai/Documents/code/dotfiles/skills-archive/maps/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [minecraft-modpack-server](/Users/yiwencai/Documents/code/dotfiles/skills-archive/minecraft-modpack-server/SKILL.md.disabled) | 当前主线之外的游戏/工具/红队场景；从日常全局集移出，有明确项目再启用。 |
| [native-mcp](/Users/yiwencai/Documents/code/dotfiles/skills-archive/native-mcp/SKILL.md.disabled) | 用于额外 MCP/浏览器桥接的专门入口；当前已有原生连接与浏览器工具，仅在特定宿主接入任务中启用。 |
| [notion](/Users/yiwencai/Documents/code/dotfiles/skills-archive/notion/SKILL.md.disabled) | 真实工具接入，不能用通用能力替代；有知识同步或办公任务时按需启用，已有插件覆盖的功能只保留个人差异。 |
| [obsidian](/Users/yiwencai/Documents/code/dotfiles/skills-archive/obsidian/SKILL.md.disabled) | 真实工具接入，不能用通用能力替代；有知识同步或办公任务时按需启用，已有插件覆盖的功能只保留个人差异。 |
| [openhue](/Users/yiwencai/Documents/code/dotfiles/skills-archive/openhue/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [orca-cli](/Users/yiwencai/Documents/code/dotfiles/skills-archive/orca-cli/SKILL.md.disabled) | 宿主专用的代理编排协议，按 Hermes/Orca/外部 CLI 场景启用；不应全局覆盖 Codex 原生工具和模型选择。 |
| [orchestration](/Users/yiwencai/Documents/code/dotfiles/skills-archive/orchestration/SKILL.md.disabled) | 宿主专用的代理编排协议，按 Hermes/Orca/外部 CLI 场景启用；不应全局覆盖 Codex 原生工具和模型选择。 |
| [p5js](/Users/yiwencai/Documents/code/dotfiles/skills-archive/p5js/SKILL.md.disabled) | 保留图示/数学动画/设计的格式知识和模板，按输出类型启用；主线是学习与技术表达，无需所有绘图入口常驻。 |
| [pixel-art](/Users/yiwencai/Documents/code/dotfiles/skills-archive/pixel-art/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [pokemon-player](/Users/yiwencai/Documents/code/dotfiles/skills-archive/pokemon-player/SKILL.md.disabled) | 当前主线之外的游戏/工具/红队场景；从日常全局集移出，有明确项目再启用。 |
| [polymarket](/Users/yiwencai/Documents/code/dotfiles/skills-archive/polymarket/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [popular-web-designs](/Users/yiwencai/Documents/code/dotfiles/skills-archive/popular-web-designs/SKILL.md.disabled) | 保留图示/数学动画/设计的格式知识和模板，按输出类型启用；主线是学习与技术表达，无需所有绘图入口常驻。 |
| [pretext](/Users/yiwencai/Documents/code/dotfiles/skills-archive/pretext/SKILL.md.disabled) | 保留图示/数学动画/设计的格式知识和模板，按输出类型启用；主线是学习与技术表达，无需所有绘图入口常驻。 |
| [remotion](/Users/yiwencai/Documents/code/dotfiles/skills-archive/remotion/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [segment-anything](/Users/yiwencai/Documents/code/dotfiles/skills-archive/segment-anything/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [songsee](/Users/yiwencai/Documents/code/dotfiles/skills-archive/songsee/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [songwriting-and-ai-music](/Users/yiwencai/Documents/code/dotfiles/skills-archive/songwriting-and-ai-music/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [spotify](/Users/yiwencai/Documents/code/dotfiles/skills-archive/spotify/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [subagent-driven-development](/Users/yiwencai/Documents/code/dotfiles/skills-archive/subagent-driven-development/SKILL.md.disabled) | 宿主专用的代理编排协议，按 Hermes/Orca/外部 CLI 场景启用；不应全局覆盖 Codex 原生工具和模型选择。 |
| [teams-meeting-pipeline](/Users/yiwencai/Documents/code/dotfiles/skills-archive/teams-meeting-pipeline/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [touchdesigner-mcp](/Users/yiwencai/Documents/code/dotfiles/skills-archive/touchdesigner-mcp/SKILL.md.disabled) | 具有专门的媒体工具或素材价值；无近期高频证据，按兴趣项目启用，不误判为模型已有媒体生成能力。 |
| [warp-agentic-development](/Users/yiwencai/Documents/code/dotfiles/skills-archive/warp-agentic-development/SKILL.md.disabled) | 当前主线之外的游戏/工具/红队场景；从日常全局集移出，有明确项目再启用。 |
| [webhook-subscriptions](/Users/yiwencai/Documents/code/dotfiles/skills-archive/webhook-subscriptions/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [weights-and-biases](/Users/yiwencai/Documents/code/dotfiles/skills-archive/weights-and-biases/SKILL.md.disabled) | 相关技术参考，但目前多为通用教程/工具速查；具体项目用到该栈再加载。评测协议、已验证配置和真实排错沉淀后可升级为核心。 |
| [xurl](/Users/yiwencai/Documents/code/dotfiles/skills-archive/xurl/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |
| [yuanbao](/Users/yiwencai/Documents/code/dotfiles/skills-archive/yuanbao/SKILL.md.disabled) | 独有服务/设备接口，但近期样本没有高频证据；仅在实际使用对应服务时部署。 |

## 移除

| Skill | 判断理由 / 去向 |
|---|---|
| [academic-study-planner](/Users/yiwencai/Documents/code/dotfiles/skills-archive/academic-study-planner/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [claude-design](/Users/yiwencai/Documents/code/dotfiles/skills-archive/claude-design/SKILL.md.disabled) | 已有 HTML/可视化入口覆盖主要目标，独有风格可作为模板；markdown-viewer 主要再要求安装另一套技能。 |
| [codebase-inspection](/Users/yiwencai/Documents/code/dotfiles/skills-archive/codebase-inspection/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [computer-use](/Users/yiwencai/Documents/code/dotfiles/skills-archive/computer-use/SKILL.md.disabled) | 从当前 Codex 全局部署移除旧宿主操作说明；本会话已有 cua API。旧副本假设 browser-client 或 computer_use 工具，不能凭文本创造工具；其他宿主单独验证。 |
| [control-chrome](/Users/yiwencai/Documents/code/dotfiles/skills-archive/control-chrome/SKILL.md.disabled) | 从当前 Codex 全局部署移除旧宿主操作说明；本会话已有 cua API。旧副本假设 browser-client 或 computer_use 工具，不能凭文本创造工具；其他宿主单独验证。 |
| [control-in-app-browser](/Users/yiwencai/Documents/code/dotfiles/skills-archive/control-in-app-browser/SKILL.md.disabled) | 从当前 Codex 全局部署移除旧宿主操作说明；本会话已有 cua API。旧副本假设 browser-client 或 computer_use 工具，不能凭文本创造工具；其他宿主单独验证。 |
| [creative-ideation](/Users/yiwencai/Documents/code/dotfiles/skills-archive/creative-ideation/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [data-consolidation-agent](/Users/yiwencai/Documents/code/dotfiles/skills-archive/data-consolidation-agent/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [engineering-ai-data-remediation-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-ai-data-remediation-engineer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-ai-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-ai-engineer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-autonomous-optimization-architect](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-autonomous-optimization-architect/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-backend-architect](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-backend-architect/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-code-reviewer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-code-reviewer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-codebase-onboarding-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-codebase-onboarding-engineer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-data-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-data-engineer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-database-optimizer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-database-optimizer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-devops-automator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-devops-automator/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-git-workflow-master](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-git-workflow-master/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-incident-response-commander](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-incident-response-commander/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-minimal-change-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-minimal-change-engineer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-security-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-security-engineer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-senior-developer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-senior-developer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-software-architect](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-software-architect/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-sre](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-sre/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [engineering-technical-writer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/engineering-technical-writer/SKILL.md.disabled) | 通用专家角色、示例和任意成功指标不构成新增能力；删除入口前迁出实际项目踩坑。minimal-change 内的 Hermes 滚动案例应保留。 |
| [find-skills](/Users/yiwencai/Documents/code/dotfiles/skills-archive/find-skills/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [language-translator](/Users/yiwencai/Documents/code/dotfiles/skills-archive/language-translator/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [lsp-index-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/lsp-index-engineer/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [macos-computer-use](/Users/yiwencai/Documents/code/dotfiles/skills-archive/macos-computer-use/SKILL.md.disabled) | 从当前 Codex 全局部署移除旧宿主操作说明；本会话已有 cua API。旧副本假设 browser-client 或 computer_use 工具，不能凭文本创造工具；其他宿主单独验证。 |
| [markdown-viewer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/markdown-viewer/SKILL.md.disabled) | 已有 HTML/可视化入口覆盖主要目标，独有风格可作为模板；markdown-viewer 主要再要求安装另一套技能。 |
| [project-management-experiment-tracker](/Users/yiwencai/Documents/code/dotfiles/skills-archive/project-management-experiment-tracker/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [prompt-engineer](/Users/yiwencai/Documents/code/dotfiles/skills-archive/prompt-engineer/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [sketch](/Users/yiwencai/Documents/code/dotfiles/skills-archive/sketch/SKILL.md.disabled) | 已有 HTML/可视化入口覆盖主要目标，独有风格可作为模板；markdown-viewer 主要再要求安装另一套技能。 |
| [specialized-mcp-builder](/Users/yiwencai/Documents/code/dotfiles/skills-archive/specialized-mcp-builder/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [specialized-model-qa](/Users/yiwencai/Documents/code/dotfiles/skills-archive/specialized-model-qa/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [specialized-workflow-architect](/Users/yiwencai/Documents/code/dotfiles/skills-archive/specialized-workflow-architect/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |
| [technical-translator-agent](/Users/yiwencai/Documents/code/dotfiles/skills-archive/technical-translator-agent/SKILL.md.disabled) | 主要是通用方法、角色设定或与当前主线不匹配的业务模板；缺少足够个人增量。需用时直接描述任务、查当前文档即可。 |

## 插件与系统部分

保留 .system 的维护机制，以及当前运行时提供的文档/表格/演示/PDF、可视化、浏览器和图像生成能力。此处不建议手工删除缓存内的 SKILL.md。

Canva、Sites、Notion、深度研究等已安装插件应按真实使用频率决定是否启用；没有逐项深审它们的全部资源，本报告不建议仅凭名称卸载。用户提供的 recommended_plugins 是未安装推荐列表，不计为冗余已安装 skill。

## 后续落地顺序（尚未执行）

1. 保存现有 Git 状态与清单，先保护全局独有 zhihu、publish-note 等资产。
2. 修复核心 GPU 资料访问和部署源说明。
3. 先撤掉通用角色入口、旧宿主入口及 Codex 同名副本；迁出实战 references。
4. 合并科研、GitHub、文档、规划入口；把项目状态/阶段规则移回项目。
5. 把低频项移到非发现的归档区，按宿主设置部署白名单；再 dry-run 查看所有删除项。
6. 用一次 GPU 问题、课程辅导、论文笔记、博客预览和周报任务验证路由，再据实际误触发与缺失调整集合。
