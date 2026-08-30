# dotfiles

个人终端开发环境配置仓库，同步 Claude Code、Codex、Cursor 与 Helix 的配置及 skills。

## 仓库结构

```
.
├── skills/                      # 技能单一事实源（全量，部署到所有工具）
├── skills-local/                # 本机专属技能（按工具白名单部署）
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
├── dot_zshrc                    # zsh 配置
├── secrets.zsh.example          # 本机密钥模板（实际文件放在仓库外）
├── install.sh                   # 一键安装脚本
└── .gitignore
```

## 技能组织（单一事实源）

所有技能只维护一份，放在 `skills/`；`claude/skills` 与 `codex/skills` 只是兼容软链接。
`install.sh` 把 `skills/`（全量）+ `skills-local/`（按白名单）rsync 部署到：

| 目标 | 目录 | 部署主树 | 本地技能白名单 |
|------|------|----------|----------------|
| Claude | `~/.claude/skills` | 是 | bupt-thesis-writer, cuda-skill, cutlass-skill, sglang-skill, triton-skill |
| Codex | `~/.codex/skills` | 是 | bupt-thesis-writer |
| zcode | `~/.zcode/skills` | 是 | — |
| agents | `~/.agents/skills` | 否（仅本地） | cuda-skill, cutlass-skill, sglang-skill, triton-skill |

- 部署用 `rsync -aO --delete` 全权收敛，目标目录以仓库为准；`--exclude='.system'` 保护 Codex 内置技能目录。
- 白名单内的本地技能以**符号链接**形式部署（指向 `skills-local/`），不复制内容；改动仓库后重新运行 install.sh 即生效。
- 本地 GPU 技能（cuda/cutlass/sglang/triton-skill）内部的 `references`/`repos` 符号链接指向 `~/code/agent-gpu-skills`（github.com/slowlyC/agent-gpu-skills），新机器需先 clone 该仓库。
- 技能间交叉引用一律按技能名（如「先执行 blindspot-pass」），禁止写 `~/.claude/skills/<x>/SKILL.md` 这类路径——那是当初 claude/codex 双树分叉的根源。
- 改完技能后先运行 `scripts/check-skills.sh --deployed` 校验，再运行 `./install.sh` 部署。

交付流程链路（同一套技能，各工具通用）：

`blindspot-pass → brainstorm → interview → reference → planning → implement → explaination → quiz`

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
skills 目录不是软链接，修改 `skills/` 或 `skills-local/` 后需重新运行 `./install.sh` 部署。更新后：

```bash
cd ~/Documents/code/dotfiles
git add -A && git commit -m "update config" && git push
```
