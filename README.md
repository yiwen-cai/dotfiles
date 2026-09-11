# dotfiles

个人终端开发环境配置仓库，同步 Claude Code、Codex、Cursor 与 Helix 的配置及 skills。

## 仓库结构

```
.
├── skills/                      # 13 个核心入口（按清单部署）
├── skills-local/                # 4 个 GPU 资料入口
├── skills-projects/             # 项目专属流程
├── skills-optional/             # 默认停用的可选包
├── skills-archive/              # 迁移前原件（本机快照，.gitignore 排除）
├── skills-manifest.json         # 生命周期与目标清单
├── scripts/
│   ├── check-skills.sh          # skills 结构与部署一致性校验
│   └── skills-targets.sh        # 部署目标定义（install.sh 共用）
├── claude/                      # Claude Code 配置 (~/.claude)
│   ├── CLAUDE.md                # 全局指令
│   ├── hermes-rules.md          # Hermes 规则
│   ├── settings.json.example    # 设置模板 (含密钥占位符)
│   ├── config.json.example      # API key 模板
│   └── skills → ../skills       # 兼容软链接（勿放入真实目录）
├── codex/                       # Codex 配置 (~/.codex)
│   ├── AGENTS.md
│   ├── config.toml              # Codex 主配置 (无密钥)
│   ├── auth.json.example        # 认证模板 (含密钥占位符)
│   ├── .env.example             # 环境变量模板
│   ├── rules/
│   │   └── default.rules
│   └── skills → ../skills       # 兼容软链接（勿放入真实目录）
├── cursor/                      # Cursor 配置
│   ├── settings.json            # 编辑器设置 (-> Application Support/.../User)
│   ├── keybindings.json         # 快捷键
│   ├── snippets/                # 代码片段
│   ├── hooks.json               # Agent hooks (-> ~/.cursor)
│   ├── cli-config.json          # Cursor CLI 配置
│   ├── mcp.json.example         # MCP 模板 (含密钥占位符)
│   └── extensions.txt           # 扩展 ID 列表
├── helix/                       # Helix 配置 (~/.config/helix)
│   ├── config.toml              # 编辑器行为、诊断与快捷键
│   ├── languages.toml           # 可移植 clangd 与独立 CUDA 语言
│   ├── bin/clangd-helix         # macOS/Linux clangd 自动选择器
│   └── runtime/queries/cuda/    # CUDA 复用 C++ tree-sitter queries
├── pi/                          # pi agent 配置 (~/.pi/agent)
│   ├── settings.json            # 主配置（软链接）
│   ├── starline.json            # starline 插件配置（软链接）
│   ├── auth.json.example        # 认证模板（含密钥，只放占位符）
│   ├── extensions/              # 自定义 provider 扩展（apiKey 已脱敏）
│   └── README.md
├── dot_zshrc                    # zsh 配置
├── secrets.zsh.example          # 本机密钥模板（实际文件放在仓库外）
├── install.sh                   # 一键安装脚本
└── .gitignore
```

## 技能组织（显式清单）

`skills-manifest.json` 是唯一的生命周期与部署清单：

| 来源 | 用途 | 默认部署 |
|---|---|---|
| `skills/` | 13 个科研/学习/环境/平台入口 | `~/.codex/skills`、`~/.claude/skills`（同一 profile 镜像） |
| `skills-local/` | 4 个 GPU 资料入口 | `~/.agents/skills` |
| `skills-projects/` | 5 个项目专属包 | 已绑定项目的 `docs/agent-skills/`，由 AGENTS.md 按需路由 |
| `skills-optional/` | 68 个按需包，入口为 `SKILL.md.disabled` | 默认不部署 |
| `skills-archive/` | 全部 160 个迁移前原件，入口停用；**本机快照，不入库**（见 `.gitignore`） | 不部署 |

71 个原始名称已退役，个人资料/脚本按清单合并或保存在原件中；退役条目亦可从 git 历史取回。系统 `.system` 与插件缓存由宿主管理。
Claude Code 的 target 已启用，与 codex 共用 `codex-core` profile，两处内容逐字节一致；zcode 仍为 disabled。
安装脚本只同步清单登记的名称，不会再向宿主同步整棵技能树。
`claude/skills` 与 `codex/skills` 仍是仓库内的兼容链接，不代表这些宿主的实际部署集合。

target 的 `discovery_group` 表示"由同一个 agent 扫描的目录集合"：同组内一个技能名只能出现在一处
（`codex` 与 `agents` 同组，互斥），跨组可以镜像同名技能（`claude` 自成一组，镜像 codex 的 13 个入口）。
未声明该字段的 target 归入同一个默认组并保持互斥，镜像必须显式声明。

部署器只操作**已登记的名称**，不再对共享目录执行 `rsync --delete`。未知 skill 和 `.system` 原样保留；同名未知目录、用户后续编辑或过期计划会报冲突。

```bash
# 只检查源包
bash scripts/check-skills.sh

# 生成完整预演（不改全局目录）
python3 scripts/manage-skills.py plan --targets codex,agents,claude,projects --out /tmp/skills-plan.json

# 应用已核对且仍有效的预演
python3 scripts/manage-skills.py apply --plan /tmp/skills-plan.json

# 检查实际部署；再部署应无变化
bash scripts/check-skills.sh --deployed

# 回滚某次部署（路径由 apply 返回；后续编辑会受到保护）
python3 scripts/manage-skills.py rollback --snapshot /absolute/path/to/snapshot
```

首次迁移已有目录需要显式的路径→内容哈希 `--adopt` 清单；不要为绕过冲突直接强行覆盖。
部署状态、项目绑定和每次快照保存在 `~/.local/state/dotfiles/skills/`。
项目绑定文件为该目录下的 `projects.json`（skill 名→已核实项目绝对路径）；未绑定的论文包保持 pending。

启用可选包：在相应 target 的 `optional` 数组中加入一个清单中的可选名称，生成 plan 后 apply。
部署器只将该包的 `SKILL.md.disabled` 在目标中恢复为 `SKILL.md`，不会启用整个目录。
停用时从数组移除，再 plan/apply；已修改的部署包会报冲突并保留。

### GPU 资料

四个入口各带 `scripts/resolve-gpu-source.py`。本地资料库可用时设置 `GPU_SKILLS_ROOT`；否则经 SSH 读取 H100 上的资料。
远程位置可用 `GPU_SKILLS_HOST` 与 `GPU_SKILLS_REMOTE_ROOT` 覆盖，不把远程路径做成本机符号链接。
解析器读取一份实际文档/源码并返回哈希；沙箱不允许 SSH 时，应使用宿主提供的授权机制，不能误判为资料不存在。
不自动下载大型源码仓库，也不启动 GPU 实验。

迁移依据见 [审查](SKILL-AUDIT-2026-09-06.md)、[方案](.hermes/plans/2026-09-06-skill-consolidation.md) 和 [执行记录](docs/skill-migration/RESULTS.md)。

## 在新机器上安装

```bash
git clone https://github.com/yiwen-cai/dotfiles.git ~/Documents/code/dotfiles
cd ~/Documents/code/dotfiles
./install.sh
```

脚本会把配置软链接到 `~/.claude`、`~/.codex`、`~/.cursor`、`~/.config/helix` 以及
`~/Library/Application Support/Cursor/User/`（macOS）。

> 已存在的文件会 skip，不会覆盖本机现有配置。

### 安装 Cursor 扩展（可选）

```bash
xargs -n1 cursor --install-extension < cursor/extensions.txt
```

### Helix 与 C/C++/CUDA LSP

Apple Silicon macOS 使用 Homebrew 的 Helix 和 LLVM 22：

```bash
brew install helix llvm
hx --health cpp
hx --health cuda
```

`languages.toml` 通过仓库内的 `clangd-helix` 启动器自动选择 Homebrew LLVM、
Linux `clangd-22` 或系统 clangd；也可以用 `HELIX_CLANGD` 覆盖。CUDA 在 macOS
上仅提供编辑器语义能力，具体项目仍需通过 `.clangd`、`compile_flags.txt` 或
`compile_commands.json` 提供 vendored CUDA headers 与真实编译参数；不能在
macOS 本机编译或运行 CUDA kernel。完整说明见 [`helix/README.md`](helix/README.md)。

### 本机路径说明

- `cursor/settings.json` 中的 `vim.neovimPath` 默认为 `/opt/homebrew/bin/nvim`（Apple Silicon Homebrew）。
  Intel Mac 或 Linux 请按本机路径自行调整。
- `cursor/mcp.json.example` 里 shrimp-task-manager 使用 `$HOME/Documents/code/mcp/...`，
  请按本机实际 MCP 安装路径修改。

## ⚠️ 密钥文件需手动填写

`install.sh` 不会自动创建含密钥的文件。请用 `.example` 模板手动创建并填入真实值：

```bash
cp claude/settings.json.example ~/.claude/settings.json   # 填 ANTHROPIC_AUTH_TOKEN
cp claude/config.json.example    ~/.claude/config.json     # 填 primaryApiKey
cp codex/auth.json.example       ~/.codex/auth.json        # 填 OPENAI_API_KEY
cp codex/.env.example            ~/.codex/.env             # 填代理地址
cp cursor/mcp.json.example       ~/.cursor/mcp.json        # 填 TAVILY_API_KEY 等
cp secrets.zsh.example           ~/.config/dotfiles/secrets.zsh
chmod 600 ~/.config/dotfiles/secrets.zsh
```

`dot_zshrc` 只会加载仓库外的 `~/.config/dotfiles/secrets.zsh`，不会保存明文
API key。请在该本机文件中填写需要导出的环境变量，例如 `OPENAI_API_KEY`。

> 真实密钥文件已在 `.gitignore` 中排除；提交前仍应执行 secret scan。已经提交过的
> 密钥必须先轮换，之后再单独评估是否需要重写 Git 历史。

## 安全说明

- **绝不上传**：Claude 的 `settings.json` / `config.json`、Codex 的 `auth.json` / `.env`、
  Cursor 的 `mcp.json`、`~/.config/dotfiles/secrets.zsh`，以及 `*.sqlite`、`*.pem`、
  `id_ed25519` 等
- 含密钥的配置只提供 `.example` 脱敏模板
- Cursor 的 `settings.json` / `keybindings.json` / `hooks.json` 不含密钥，正常同步
- 提交前运行 `gitleaks dir .` 扫描当前文件，运行 `gitleaks git .` 扫描完整历史

## 更新配置

大部分配置（`~/.claude/CLAUDE.md` 等）用软链接安装，直接编辑本仓库文件即生效；
修改 skill 源后，先生成部署预演，再使用 `scripts/manage-skills.py apply` 部署。更新后：

```bash
cd ~/Documents/code/dotfiles
git add -A && git commit -m "update config" && git push
```
