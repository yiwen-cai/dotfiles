# Skill 精简与部署改造方案

日期：2026-09-06。状态：本机迁移已实施，详见 `docs/skill-migration/RESULTS.md`。以下保留批准时的原始方案。

目标：将本次盘点的 160 个自定义 skill 名称收敛为 16 个全局入口、5 个项目专属入口和按需启用的资料库；保留个人知识及可用工具，撤掉重复、陈旧和通用角色指令。系统和已安装插件的入口另计。

依据：仓库 SKILL-AUDIT-2026-09-06.md、install.sh、scripts/skills-targets.sh、scripts/check-skills.sh、实际全局目录及本机项目目录。

## 一、先固定的决定

1. 本次部署范围是本机 ~/.codex/skills 与 ~/.agents/skills。两者合计只部署 16 个已管理的全局入口。Claude/zcode 的现有部署暂不改变；新脚本不得继续向它们全量同步。它们的适配属于后续明确启用的 profile。
2. 不永久删除独有资源。迁移时保存原始快照；未进入核心的旧入口从自动发现目录移出，有价值的 references/scripts/templates 迁入明确去向。
3. 不新增一个“万能研究助手”把所有内容重新塞在一起。每个入口要有互斥的主要目标、输出约定及有限依赖。
4. 全局保留四个 GPU 入口、周报和科研信息收集。这些任务跨课程、论文、实验和 kernel 项目复用；缩短入口即可，不必强迫用户每次切项目。
5. 普通开发不再要求八段流程、固定数量子代理或提交前考试。课程辅导中的测验保留为主动选择；自动测试、事实核查、必要澄清仍按具体任务执行。
6. 系统/插件维护的功能使用当前版本。撤掉个人副本前先核对差异；本轮不卸载插件、不编辑插件缓存或 .system。
7. 16 是这次明确名单的结果，不是今后禁止增加的配额。执行期间新出现的未登记 skill 保留并报告，不为凑数删除。

## 二、最终 16 个全局入口

| # | 最终名称 | 来源与具体调整 | 触发边界 |
|---|---|---|---|
| 1 | cuda-skill | 保留本地 NVIDIA 文档索引、profiling/排错流程；修复资料访问 | CUDA/PTX、CUDA runtime、GPU profiling |
| 2 | cutlass-skill | 保留 CUTLASS/CuTe 源码、布局与实例索引 | 明确涉及 CUTLASS/CuTe/CuTeDSL |
| 3 | triton-skill | 保留 Triton/Gluon 索引；接收通用测试 skill 中的数值核验模板 | Triton/Gluon 编写、调试与性能 |
| 4 | sglang-skill | 保留 SGLang 源码导航、服务/调度排错 | 明确涉及 SGLang；不因泛称 KV Cache 自动触发 |
| 5 | paper-note-generator | 保留论文笔记模板、生成/校验脚本；移除通用 PDF 教程 | 为一篇或指定几篇论文生成既定格式笔记 |
| 6 | llm-wiki | 保留目录、来源追溯、知识更新规则；禁止普通提问自动扩写大量页面 | 明确请求维护或检索已有知识库 |
| 7 | academic-research-output | 保留科研叙事、答辩与综述经验；接收 powerpoint 学术提示及有用图示模板 | 科研汇报、综述、论文或答辩输出；文档操作交给宿主工具 |
| 8 | weekly-research-report | 保留三段周报格式、路径、量化口径；旧周报放 references | 明确请求导师周报；默认生成文件，不因 skill 自行发送邮件 |
| 9 | course-learning-planner | 保留学习偏好、课程规划、辅导边界；CS336 内容迁出；接收可选测验规则 | 课程安排或辅导；普通问题不强制先规划 |
| 10 | research-content-monitoring | 吸收 automated-daily-briefings 的源表、去重与管线排错 | 科研动态/简报；只有用户要求定时才使用调度工具 |
| 11 | create-local-project-interface | 保留只在本机存元信息的远程项目接口约定 | 建立或修复远程项目的本地入口 |
| 12 | linux-server-environment-migration | 吸收 linux-dev-environment，保留 zsh 等真实踩坑；移除过时固定包版本 | Linux 环境搭建/迁移，不覆盖所有 shell 问题 |
| 13 | huggingface-hub | 保留 CLI 定位、模型/数据操作及路径惯例；详细参数以实际 CLI help 为准 | Hub 资源检索、下载和仓库操作 |
| 14 | youtube-content | 保留字幕提取脚本、语言/时间戳处理 | 视频字幕和课程资料整理 |
| 15 | zhihu | 从全局独有目录完整纳管，保留 CLI 验证/运行脚本；收窄 description | 知乎搜索、本人内容、知识库和额度；不因 API/MCP/RAG 等泛词触发 |
| 16 | github-operations | 吸收 github、gh-address-comments、gh-fix-ci、yeet；保留评论线程与 CI 检查脚本 | GitHub issue/PR/CI 任务；简单本地 git 操作不加载长流程 |

部署位置固定为：上述 1–4 在 ~/.agents/skills；5–16 在 ~/.codex/skills。同一名称只出现在这两个用户级发现目录中的一个。

正文采用“触发条件 → 个人约定 → 资料/脚本入口 → 最小验证”结构。一般入口目标不超过约 100 行；长 GPU 索引放 references，保留导航。行数只作可读性检查，不允许为压缩而丢掉必要约束。

## 三、5 个项目入口

项目入口不再部署到用户级 skills 目录。统一源放 skills-projects/；在项目的 docs/agent-skills/<name>/ 下部署资源包，通过项目 AGENTS.md 的明确条件路由按需阅读。不依赖未经验证的嵌套目录自动发现行为。

| 最终名称 | 吸收内容 | 项目绑定 |
|---|---|---|
| cs336-stanford-course | 现有 CS336 skill + course-learning-planner 中全部 CS336 专属案例/同步规则 | /Users/yiwencai/Documents/code/cs336 |
| bilingual-resume-typst | 现有 skill + resume-review 和 common-issues.md | /Users/yiwencai/Documents/study/CV/basic-resume |
| bupt-thesis-writer | 学校模板规则和校验脚本完整保留 | 待检测到同时含 main.tex 与 BUPTBachelorThesis.sty 的真实根目录后绑定 |
| publish-note | 完整保存全局独有发布规则，修正无差别 git add -A 示例；仅按用户请求发布 | /Users/yiwencai/Documents/code/yiwen-cai.github.io |
| moe-project-access | 合入 sync-moe-project；动态状态改成现场检查 | /Users/yiwencai/Documents/code/moe-kv-cache-experiments |

以上四个已明确绑定的本机目录存在；CV 的 chinese.typ 已核实。论文模板根尚未定位：先保留项目资源包，状态记为 pending，不猜路径、不阻塞其他迁移。

MoE 项目已有 AGENTS.md 和 ACCESS.md；复用并精确增补，不能覆盖。博客也已有 AGENTS.md。MIT 课程不接收 CS336 专属规则。博客里的 resume/chinese.typ 是另一个副本，不因本次整理改动。

## 四、其他原始入口的去向

详细的 160 名称基线见审查报告；实施时把每个名称登记到清单，必须恰有一个主要去向。允许一份旧 skill 的不同资源分配到多个新包，但退役入口只有一个状态。

| 原分组 | 具体处置 |
|---|---|
| 17 个 engineering-* 和其余通用角色 | 从自动发现集合撤下。先检查完整目录；minimal-change 的 Hermes 滚动记录移入 Hermes 可选包，其他独有资产同样先迁出 |
| blindspot-pass、brainstorm、interview、reference、planning、implement、explaination、quiz | 取消八个独立入口。个性化交付偏好精简合入 codex/AGENTS.md；测验规则并入 course-learning-planner/references，需显式选择。旧原件归档 |
| planning-with-files、planning-with-files-zh、software-development-planning | 不进入 16 个核心。恢复脚本与多日任务模板保留为一个 planning-with-files 可选包，仅显式启用 |
| html-artifact、architecture-diagram、sketch、claude-design、markdown-viewer | 不进入 Codex 核心。独有学术模板进 academic-research-output；通用 HTML 需要时使用宿主 visualize。跨宿主所需模板保留一个 html-artifact 可选包 |
| testing-quality-assurance、software-quality-workflows | GPU 数值模板进 triton-skill，具体排错记录进对应项目/可选包；不保留两套通用 QA 入口 |
| imagegen、openai-docs、plugin-creator、skill-creator、skill-installer | 差异提取后撤下 Codex 的手工副本；保留系统维护版；原件归档供其他宿主适配 |
| documents、pdf、presentations、spreadsheets、template-creator 等文档 skill | 同上，使用运行时插件。学术偏好迁入科研输出包。OCR/PDF 编辑等未被覆盖的具体工具能力保存为按需包 |
| computer-use、control-chrome、control-in-app-browser、macos-computer-use | 从 Codex 用户级入口撤下。依赖旧协议的版本只在对应宿主可选包保留，不植入当前 CUA 使用路径 |
| Hermes / Orca / Kanban / 外部代理 | 按宿主保存可选包，默认不部署。kimi-webbridge、native-mcp 同理 |
| Notion、Obsidian、办公、设备、媒体、游戏、模型工具教程 | 保留必要脚本与资料为可选包，默认不部署；按具体任务选择一个，避免一口气启用整类 |
| humanizer | 少量个人写作偏好并入 codex/AGENTS.md；移除入口 |

不将 skills-optional 或 skills-archive 整树软链接到任何 agent 的发现目录。默认将其中的入口文件命名为 SKILL.md.disabled；启用时只在 staging/目标中恢复为 SKILL.md，references/scripts 的相对结构保留。这样即使工具进行广泛文件搜索，也不会误认成一批可用 skill。

## 五、源目录与清单

在现有结构上调整，不引入包管理服务：

```text
dotfiles/
  skills/                         # 12 个跨项目通用入口
  skills-local/                   # 4 个 GPU 入口；不存大型源码副本
  skills-projects/                # 5 个项目资源包
  skills-optional/                # 有效但默认停用的资源包，入口用 .disabled
  skills-archive/                 # 退役原件及来源记录，入口用 .disabled
  skills-manifest.json            # 生命周期、源位置、profile、目标及项目绑定
  scripts/manage-skills.py        # Python 标准库：plan/apply/check/rollback
  scripts/check-skills.sh         # 保留命令入口，调用统一清单校验
  scripts/skills-targets.sh        # 兼容薄层，不再维护另一份全量名单
  tests/test_manage_skills.py     # 仅验证有破坏风险的部署行为
```

skills-manifest.json 的必要信息：

- entries：原始名称、源路径、生命周期（global/project/optional/retired）、合并去向、来源说明。
- profiles：codex-core-12、gpu-shared-4，以及显式启用的可选名称。
- targets：codex 和 agents 启用；claude/zcode 暂时 disabled。
- projects：项目资源名、已核实根目录、绑定状态。机器特定路径放本机配置，不把实验室实时状态写入可移植清单。
- system_provided：只标记系统/插件覆盖关系，不把缓存路径硬编码成部署源。

每次部署的实际管理清单、内容哈希与备份记录保存在 ~/.local/state/dotfiles/skills/；不提交机器运行状态到仓库。

## 六、部署语义

改造重点是取代共享目标根上的 rsync --delete。

1. plan 只计算新增、修改、停用、冲突、未管理条目及系统覆盖项，不写入全局目录。
2. 初次迁移对本次已知的 160 个名称做完整目录比对，不能只比较 SKILL.md。纳管候选、全局独有内容和本地修改全部进入可审查差异。
3. apply 仅更改明确纳管的名称。清单未列出的新 skill、.system 与插件资源保持原样；已有同名未管理目录视为冲突，不覆盖。
4. 目标根如果是符号链接，不遍历其指向执行同步或删除；先报告并处理旧布局。
5. 在受管理单个 skill 的 staging 中校验全部文件后发布。多文件替换要保留完整回滚点；失败时不把整个目标标成成功，错误退出码不得被 `|| true` 吞掉。
6. 内容哈希使用包内相对路径、文件内容和符号链接目标；不以 mtime 判断无修改。包内损坏链接需报告。
7. 停用旧名称时仅移走预期版本：如果部署后用户又改过它，记录冲突而不是删除修改。
8. 第二次 apply 在状态不变时应当无操作。
9. install.sh 只委托统一的部署器。显式 skills 命令可独立运行，避免为精简 skills 连带执行 pi、shell、编辑器配置安装。
10. 可选包通过清单明确启用后部署到一个目标，使用完显式停用；不设后台自动安装/删除。

计划中的命令接口（当前尚不存在）：

```bash
python3 scripts/manage-skills.py plan --targets codex,agents
python3 scripts/manage-skills.py apply --targets codex,agents --plan <plan-file>
python3 scripts/manage-skills.py check --targets codex,agents
python3 scripts/manage-skills.py rollback --snapshot <snapshot-id>
```

apply 应校验 plan 的源与目标哈希；计划生成后若文件变化，重新生成 plan，不应用过期删除列表。具体选项以实施后的 --help 为准。

## 七、执行阶段与交付物

### 阶段 1：盘点与保全

- 记录原始 Git 状态，当前 pi 下三个修改和 skill-creator 的缓存修改均不纳入本次改动。
- 生成 160 名称的迁移映射；新增发现项单列，不默默忽略。
- 完整备份受影响用户级 skill 包到 ~/.local/state/dotfiles/skill-backups/<timestamp>/，保存权限、符号链接和包哈希。
- 将 zhihu、publish-note 等仓库外资产纳管；orca-cli/orchestration/find-skills 的原件也保存后再停用。
- 对系统同名副本做差异清点，将个人修改标出。

验收：每个原始名称可追溯到原件快照与目标；任何独有资源均有保存位置；尚无发现目录删改。

### 阶段 2：实现部署器及清单

- 建立清单，改写部署/校验的共同入口。
- 将 Claude/zcode 设为本次不部署，保证 install.sh 不再对它们执行旧式全量收敛。
- 在临时根测试计划、部署与回滚，不对真实全局目录测试删除。

验收：下节的部署测试全部通过；目标集合与保护项可在 plan 中完整看到。

### 阶段 3：整理内容

- 完成表中合并、重写触发边界和项目资源包。
- 迁移脚本时同步修正相对路径、参考路径和说明中的旧名称；不把“换目录”当作合并完成。
- 修正 Triton .py 文件实为 Markdown 模板的问题：默认转成 templates/triton-kernel-numerical-harness.md；保留其占位性质，不能宣称已变成可执行测试。
- GPU 资料优先从实际存在的源码库解析；不要保留当前 Mac 上损坏的 /public/home/... 链接。使用可配置的 GPU_SKILLS_ROOT；若仅远程有资料，则明确通过 SSH 查询并真实验证一条文档/源码路径，不把远程路径当本地路径。
- 不为修复链接自动下载全部 CUDA/CUTLASS/Triton/SGLang 仓库。需要新建本地资料副本时先确定所需目录和规模；远程可查询即可满足第一版。

验收：16 个入口各有明确边界；已保留资源无损坏引用；四个 GPU 入口至少各能读取到一份对应资料。GPU 单项不可达时保留其原包和诊断，整体验收不能标记全通过。

### 阶段 4：项目绑定与预演

- 对四个已定位项目生成具体 diff，增补 AGENTS 路由、安装项目包。
- 论文项目包保存为 pending；找到真实模板根后补绑定，不写虚构路径。
- 生成真实 codex/agents 部署预演，检查所有停用名称均来自明确迁移清单，未知项没有删除动作。
- 将摘要与完整 diff 留作执行记录；执行授权到位后才进行实际迁移，本次只制定方案。

验收：项目原有说明未被覆盖；普通 dotfiles 任务不会加载 CS336/论文规则；预演无系统资源或未知目录删除。

### 阶段 5：应用与验证

- 仅应用通过检查的 plan，记录快照 ID。
- 启动新任务验证可见入口（本会话目录列表可能不会热更新）。
- 运行部署一致性检查、场景验收；失败则恢复对应包，不继续扩大迁移范围。
- 再运行一次 plan，期望受管理项无差异。

验收：本次管理的 16 个全局名称全部到位、无双根重复；原来项目/可选/退役入口不再全局暴露。未知新项单列，不计为迁移失败也不自动删除。

### 阶段 6：文档与试用

- 更新 README 的全量部署描述、项目绑定、GPU 资料解析方式和回滚命令。
- 更新 check-skills 对主树数量、名称、跨 skill 引用和多来源布局的检查。
- 以接下来约 10 次真实任务记录是否误触发、漏触发或需要恢复可选包；不创建后台监控，也不因为达到某个日期自动删除归档。

验收：新增 skill 时只更新清单，重装不会恢复旧的 150 个入口，也不会清掉独立安装的未知 skill。

## 八、验证矩阵

### 必须自动验证的部署行为

临时目录 fixture 覆盖：

1. 从旧集合迁到新集合，数量和名称正确。
2. 未登记 skill 与 .system 哨兵文件保持逐字节不变。
3. 同名未管理目录、部署后被修改的旧包、失效的 plan 都拒绝覆盖。
4. 不跟随目标根符号链接删除外部内容；包内损坏链接可诊断。
5. 缺失源、文件写入失败与工具失败返回非零，并保留可恢复状态。
6. 第二次部署无变化；rollback 恢复前一状态且不覆盖部署后新编辑。
7. disabled target（Claude/zcode）没有写入；项目部署不覆盖原 AGENTS.md。
8. 归档入口没有 SKILL.md；启用一个可选包不会将其整类目录带入发现集合。

建议运行：`python3 -m unittest discover -s tests -p 'test_manage_skills.py'`，再运行更新后的 `scripts/check-skills.sh --deployed`。这些是本方案要求的未来测试，当前未创建或运行。

### 必须做的场景验收

| 场景 | 期望 |
|---|---|
| Triton tail mask 问题 | 读取 triton-skill 及数值模板；源码/资料路径真实可读 |
| SGLang KV cache 问题 / 普通 KV Cache 原理题 | 前者触发 SGLang；后者不自动加载四个 GPU 包 |
| MIT 第七章学习 | course-learning-planner 不带 CS336 强制同步规则 |
| CS336 作业辅导 | 通过该项目路由加载课程约定，不越过用户的辅导边界 |
| 单篇论文笔记 / 周报 | 分别使用论文笔记与周报格式；不互相抢入口 |
| 博客草稿预览 | 通过博客项目读取 publish-note，正确保留公式约定；不执行未请求的发布 |
| 普通代码小修复 | 不启动八段交付链，也不因 quiz 锁定提交 |
| 知乎 CLI 状态检查 | 完整资源仍在，使用本地无副作用状态检查；不为验收上传文件或发布内容 |
| PDF/表格请求 | 系统/插件功能仍可发现，没有手工同名旧入口竞争 |

GPU 真机编译/benchmark 属于具体任务验收，不为此次目录整理运行完整实验或占用长时间 GPU 资源。

## 九、回滚与完成边界

- 回滚依据快照与部署状态，不使用 git reset --hard、git clean 或整个全局目录覆盖。
- 只撤销本次实际触及且之后未被修改的文件；后续用户编辑作为冲突报告并保留。
- 第一次切换不永久删除快照与退役原件。只有确认新流程稳定且用户要求清理时再回收。
- 完成条件：16 个核心可用、四个已绑定项目规则可读、论文包妥善待绑定、所有旧入口有去向、系统/未知资源保持不变、预演与实际状态一致、验证通过。
- 本轮交付只包括本方案文件。全局写入、跨项目修改、合并和部署均尚未执行。
