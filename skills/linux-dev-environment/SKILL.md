---
name: linux-dev-environment
description: Linux 开发环境搭建与配置迁移 — shell 配置、工具安装、conda 环境、跨服务器配置适配
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Linux 开发环境搭建

## 适用场景

- 在新 Linux 机器上从零搭建开发环境
- 在服务器之间迁移 Shell 配置（zsh / oh-my-zsh / powerlevel10k / 插件 / alias）
- 用户本地安装开发工具（无 sudo 权限）
- 安装配置 miniconda
- 适配跨服务器的路径差异和环境变量

## 迁移工作流

### 第一步：对比两机差异

迁移前必须确认以下差异点，否则直接拷配置会报错：

| 检查项 | 说明 |
|--------|------|
| 家目录路径 | `echo $HOME` — 两机可能不同（如 `/public/home/user` vs `/storage/user`） |
| 已装的工具 | `which <tool>` 逐项检查 |
| conda 位置 | `which conda` 或 `ls ~/apps/miniconda3` |
| sudo 权限 | `sudo -n true 2>/dev/null && echo has_sudo || echo no_sudo` |
| 特殊依赖路径 | CUDA 路径、NVM、自定义脚本位置 |

### 第二步：Shell 配置迁移

```bash
# 1. 目标机装 zsh + oh-my-zsh（需要 sudo）
sudo apt install -y zsh
chsh -s $(which zsh)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# 2. 安装 powerlevel10k
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
  ~/.oh-my-zsh/custom/themes/powerlevel10k

# 3. 安装插件
git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions \
  ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
git clone --depth=1 https://github.com/zdharma-continuum/fast-syntax-highlighting \
  ~/.oh-my-zsh/custom/plugins/fast-syntax-highlighting

# 4. SCP 同步自定义配置（保留 API key 等敏感信息）
scp source:~/.config/zsh/custom/*.zsh target:~/.config/zsh/custom/
scp source:~/.p10k.zsh target:~/.p10k.zsh

# 5. 适配 .zshrc（处理路径差异，注释不存在的引用）
```

### 第三步：工具安装（无 sudo）

当没有 `sudo apt install` 权限时使用用户本地安装：

```bash
mkdir -p ~/.local/bin

# fzf
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
~/.fzf/install --no-bash --no-fish --key-bindings --completion --no-update-rc
# 注意：需要在 .zshrc 中手动添加 PATH
export PATH="$HOME/.fzf/bin:$PATH"
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# lsd (Rust ls 替代)
# 下载 musl 静态链接 release
curl -sL https://github.com/lsd-rs/lsd/releases/download/v1.1.5/lsd-v1.1.5-x86_64-unknown-linux-musl.tar.gz \
  | tar xz -C /tmp/
cp /tmp/lsd-*/lsd ~/.local/bin/
chmod +x ~/.local/bin/lsd
```

### 第四步：Miniconda 安装

```bash
mkdir -p ~/apps
curl -sL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  -o /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p ~/apps/miniconda3
rm /tmp/miniconda.sh
~/apps/miniconda3/bin/conda --version
```

### 第五步：启用 conda/mamba shell hook

在 `.zshrc` 中添加或解注释 conda 初始化块，**注意修正路径为 `$HOME` 或目标机实际路径**。

## 参考文件

- `references/zsh-source-glob-gotcha.md` — 完整复现步骤和详解 zsh 中 `source *.zsh` 只加载第一个文件的陷阱

## 关键陷阱

### ⚠️ zsh 的 `source` 不支持多文件 glob

这是最容易被忽略的问题。在 zsh 中：

```zsh
# ❌ 错误：只会 source 第一个文件，其余作为位置参数传入
source ~/.config/zsh/custom/*.zsh

# ✅ 正确：使用 for 循环依次 source 每个文件
for f in ~/.config/zsh/custom/*.zsh; do source "$f"; done
```

**原因**：zsh 的 `source`（以及 `.` 命令）符合 POSIX 语义——`source file1 arg1 arg2` 会 source file1，然后把 arg1/arg2 设为 `$1`/`$2`。多个文件名不会被分别 source。

**如何发现**：配置看起来加载了（无报错），但第二个文件及之后的内容（fzf、额外 PATH 追加等）实际上从未执行。

### ⚠️ sed 取消注释多行块时标记行被破坏

当使用 sed 的 range 地址取消注释代码块时：

```bash
# 假设有以下注释块
# >>> conda initialize >>>
# real_code_line
# <<< conda initialize <<<

# ❌ 危险：sed 也会去掉标记行的 # 前缀
sed -i '/^# >>>/,/^# <</s/^# //' file
# 结果：>>> conda initialize >>> (语法错误！)

# ✅ 正确：额外修复标记行
sed -i 's/^>>> conda initialize >>>/# >>> conda initialize >>>/'
sed -i 's/^<<< conda initialize <</# <<< conda initialize <</'
```

### ⚠️ .zshrc 中的硬编码路径

从一台机器迁移到另一台时，`.zshrc` 中可能包含：
- `export PATH="/specific/path/bin:$PATH"`（如 `/public/home/user/...`）
- `source /specific/path/custom/*.zsh`
- `alias claude="/specific/path/..."`

应统一使用 `$HOME` 替代，或迁移时注释掉不存在的引用并逐一确认。

### ⚠️ 远程文件编辑

通过 SSH 修改远程机器的 `.zshrc` 时小心引号嵌套。建议：
- 短修改用 `sed`
- 大段重写用 `cat > file << 'EOF'`（单引号 EOF 阻止变量展开）

## 验证清单

- [ ] `which lsd` 且 `ls` 别名生效
- [ ] `which fzf` 且 Ctrl+R/Ctrl+T 快捷键可用
- [ ] `which conda` 且 `conda --version` 正常
- [ ] conda 环境已初始化（`echo $CONDA_DEFAULT_ENV` 显示 `base`）
- [ ] 自定义 alias 生效（`alias reload`、`alias ls` 等）
- [ ] 环境变量已设置（`echo $CUDA_HOME`、`echo $UV_INDEX_URL` 等）
- [ ] oh-my-zsh 插件已加载（`echo ${plugins}` 包含预期列表）
- [ ] powerlevel10k 主题生效（`echo $ZSH_THEME` 显示 `powerlevel10k/powerlevel10k`）