---
name: remote-ssh-lab
description: 在远程服务器 lab（10.160.4.102）上通过 SSH 进行编码、跑实验、传输文件等工作流
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Remote Server `lab` — 工作流指南

## 环境概览

| 项目 | 内容 |
|------|------|
| **主机名** | lab（`~/.ssh/config` 中配置）|
| **真实地址** | `10.160.4.102:22` |
| **用户** | `caiyiwen` |
| **认证方式** | SSH Key（`~/.ssh/id_ed25519`）|
| **操作系统** | Ubuntu 20.04.6 LTS (Focal) |
| **内核** | Linux 5.4.0-216-generic x86_64 |
| **Shell** | zsh（`/public/home/caiyiwen/.local/bin/zsh`）|
| **Home** | `/public/home/caiyiwen` |
| **工作目录** | `~/code/`（即 `/public/home/caiyiwen/code/`）|
| **CPU** | 64 核 |
| **内存** | 503 GB |
| **GPU** | 8× NVIDIA H100 PCIe（各 81GB）|
| **Python** | `/usr/bin/python3` → Python 3.8.10（系统自带）|
| **Git** | 2.25.1 |
| **Docker** | 24.0.7 |
| **tmux** | 3.0a |
| **Conda** | 未安装 |

### CUDA 版本

多个版本共存于 `/usr/local/`，默认 symlink 指向 CUDA 12.6：

| 路径 | 版本 |
|------|------|
| `/usr/local/cuda` (默认 symlink) | `→ /usr/local/cuda-12.6/` |
| `/usr/local/cuda-12.6` | **12.6.20**（默认） |
| `/usr/local/cuda-12.3` | 12.3 |
| `/usr/local/cuda-12.2` | 12.2 |
| `/usr/local/cuda-12.1` | 12.1 |
| `/usr/local/cuda-11.8` | 11.8 |

**注意：CUDA 不在 PATH 中，也没有设置 LD_LIBRARY_PATH / CUDA_HOME。** 使用前需要手动添加。

**现有项目（`~/code/`）：**
agent-gpu-skills, BUPTBachelorThesis, Bupt-Thesis-Writer, cc-statusline, cuda, FlashSparse, Fused3S, python, rabbit_order, xllm

## SSH 配置（`~/.ssh/config`）

```text
Host lab
    HostName 10.160.4.102
    Port 22
    User caiyiwen
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
    SetEnv TERM=xterm-256color
    RemoteForward 7897 localhost:7897
```

## 工作流

### 0. 读取远程项目指导文件（强制）

当任务需要 SSH 到 lab 上的某个项目目录工作时，不能假设 Hermes 会自动加载远程目录中的项目指导文件。由于 `ssh lab 'cd <remote-dir> && ...'` 只是远程 shell 命令，当前 Hermes 主会话、`delegate_task` 子 agent、以及普通工具调用都不会自动注入远程目录的 `AGENTS.md` / `AGENT.md` / `CLAUDE.md` / `.cursorrules`。

**必须在执行项目任务前主动读取并遵守这些文件：**

```bash
ssh lab 'cd /path/to/project && for f in AGENTS.md AGENT.md CLAUDE.md .cursorrules; do [ -f "$f" ] && echo "===== $f =====" && sed -n "1,240p" "$f"; done; true'
```

When chaining additional inspection commands after this loop, do not use `&&` immediately after the loop unless the loop is forced to return success. A missing optional guidance file can make the loop's final test return non-zero and skip the rest of the command. Prefer:

```bash
ssh lab 'cd /path/to/project; for f in AGENTS.md AGENT.md CLAUDE.md .cursorrules; do [ -f "$f" ] && echo "===== $f =====" && sed -n "1,240p" "$f"; done; echo "===== next check ====="; find tests -maxdepth 1 -type f | sort'
```

Or add `; true` after the loop before `&& ...` if the rest of the command should only require the `cd` to succeed.

规则：

1. 只要用户要求在 lab 的某个具体项目目录中读代码、改代码、跑测试、写文档或排查问题，就先读取该目录的指导文件。
2. 如果子目录中还有更近层级的指导文件，进入该子目录工作前也要读取；更近层级规则优先。
3. 如果使用 `delegate_task` 派发子 agent，必须把已读取的远程指导文件内容放入子 agent 的 `context`，或明确要求子 agent 首先 SSH 读取这些文件。
4. 若指导文件很长，至少读取与当前任务相关的前 240 行；必要时分页继续读取。
5. 文件可能叫 `AGENTS.md` 或 `AGENT.md`，两者都要检查。

### 1. 初始化 CUDA 环境

CUDA 默认不在环境变量中，使用前需要设置：

```bash
# 一次性设置
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export CUDA_HOME=/usr/local/cuda

# 或写入 .zshrc 永久生效
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.zshrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.zshrc
echo 'export CUDA_HOME=/usr/local/cuda' >> ~/.zshrc

# 切换 CUDA 版本
export PATH=/usr/local/cuda-11.8/bin:$PATH
```

### 1. 快速单次命令（Hermes terminal 模式）

Hermes 可以像执行本地命令一样执行远程命令。适合一次性检查、信息获取：

```bash
# 检查 GPU 状态
ssh lab 'nvidia-smi'

# 查看远程目录结构
ssh lab 'ls ~/code/'

# 查看进程
ssh lab 'ps aux | grep python'

# 检查 CUDA
ssh lab 'export PATH=/usr/local/cuda/bin:$PATH && nvcc --version'
```

**在 Hermes 中：** 直接通过 `terminal(command="ssh lab '...'")` 执行。

### 2. 代码编辑与文件传输

#### 从本地推送代码到 lab
```bash
# 将本地目录复制到远程
scp -r /path/to/local/project lab:~/code/

# 或 rsync（增量同步，推荐日常使用）
rsync -avz --progress /path/to/local/project lab:~/code/
```

#### 从 lab 拉取结果回本地
```bash
rsync -avz --progress lab:~/code/my-project/results/ ./local-results/
```

#### 在 Hermes 中直接编辑远程文件
```bash
# 读取远程文件（ssh + cat）
ssh lab 'cat ~/code/my-project/config.yaml'

# 写入远程文件（使用 heredoc）
ssh lab 'cat > ~/code/my-project/config.yaml << '\''EOF'\''
key: value
EOF'
```

### 3. 长时间运行的实验（tmux 模式）

实验可能跑几小时甚至几天，**必须使用 tmux** 防止 SSH 断开导致进程终止。

```bash
# 1. 创建新 tmux 会话运行实验
ssh lab -t 'tmux new-session -d -s my-exp && tmux send-keys -t my-exp "cd ~/code/my-project && export PATH=/usr/local/cuda/bin:\$PATH && python train.py" Enter'

# 2. 稍后检查进度
ssh lab 'tmux capture-pane -t my-exp -p -S -30'

# 3. 手动 attach 到会话查看（需要交互式终端）
ssh lab -t 'tmux attach -t my-exp'

# 4. 实验完成后杀掉会话
ssh lab 'tmux kill-session -t my-exp'
```

#### tmux 常用操作
| 命令 | 说明 |
|------|------|
| `tmux new-session -d -s <name>` | 创建后台会话 |
| `tmux ls` | 列出所有会话 |
| `tmux attach -t <name>` | 附加到会话 |
| `tmux capture-pane -t <name> -p -S -N` | 捕获最近 N 行输出 |
| `tmux kill-session -t <name>` | 杀掉会话 |
| `tmux send-keys -t <name> "command" Enter` | 向会话发送命令 |

### 4. GPU 实验管理

lab 有 8 块 H100，管理 GPU 分配是关键：

```bash
# 查看 GPU 使用情况
ssh lab 'nvidia-smi'

# 查看当前有哪些进程在用 GPU
ssh lab 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader'

# 在特定 GPU 上跑实验
ssh lab 'export PATH=/usr/local/cuda/bin:$PATH && CUDA_VISIBLE_DEVICES=0,1 python train.py'
```

### 5. Docker 工作流

Docker 24.0.7 可用，适合需要特定环境的实验。Docker 内部自带 CUDA，不需要额外设置。

```bash
# 查看现有镜像/容器
ssh lab 'docker images'
ssh lab 'docker ps -a'

# 拉取镜像
ssh lab 'docker pull pytorch/pytorch:latest'

# 在后台跑容器
ssh lab 'docker run -d --gpus all --name my-exp pytorch/pytorch:latest python train.py'

# 查看日志
ssh lab 'docker logs -f my-exp'

# 复制文件到容器
ssh lab 'docker cp ./data my-exp:/workspace/data'

# 交互式进入容器
ssh lab -t 'docker exec -it my-exp /bin/bash'

# 清理
ssh lab 'docker rm -f my-exp'
```

## 多机互通与文件传输（扩展）

当需要在 lab 与其他服务器（如 a800）之间直接传输文件时，使用以下模式。

### 前置：SSH 密钥互通

默认情况下，lab 和其他服务器可能使用不同的 SSH 密钥，无法直接 SSH。

```bash
# 1. 将 lab 的公钥添加到目标机器的 authorized_keys
ssh lab "cat ~/.ssh/id_ed25519.pub" | ssh a800 "cat >> ~/.ssh/authorized_keys"

# 2. 验证直连
ssh lab "ssh -o StrictHostKeyChecking=no 10.160.4.104 'hostname'"
```

### 方法 A：从 lab 用 rsync 推送到其他服务器（推荐）

在 lab 上执行 rsync，利用内网高速传输：

```bash
# lab → a800 推送
ssh lab "rsync -avz --progress --exclude='.venv' --exclude='__pycache__' \
  ~/source/dir/ 10.160.4.104:~/target/dir/"
```

### 方法 B：通过本地机器中转（当 SSH 直连不可用时）

```bash
# tar pipe：源 → 本机 → 目标
ssh source "cd /path && tar cf - --exclude='.venv' dirname" | \
  ssh target "cd /path && tar xf -"

# scp -3：通过本地路由
scp -3 source:~/source/file target:~/target/file
```

### 方法 C：从 lab 拉取到本地 / 从本地推送到 lab

日常使用 rsync 增量同步：

```bash
# 本地 → lab
rsync -avz --progress --exclude='__pycache__' --exclude='.git' \
  ./project/ lab:~/code/project/

# lab → 本地
rsync -avz --progress lab:~/code/project/results/ ./local-results/
```

### 方法 D：修复迁移后的 .venv 断链

复制 `.venv` 到另一台机器后，Python 和 pip 的 symlink 指向原机器的绝对路径，会断。修复方法：

```bash
# 1. 在目标机器上安装同版本的 Python
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.12.12  # 与原机器相同的版本

# 2. 重新链接 .venv 中的 symlink
VENV=~/path/to/.venv
PYDIR="$HOME/.local/share/uv/python/cpython-3.12.12-linux-x86_64-gnu"
ln -sf "$PYDIR/bin/python3.12" "$VENV/bin/python"
ln -sf "$PYDIR/bin/python3.12" "$VENV/bin/python3"
ln -sf "$PYDIR/bin/pip3" "$VENV/bin/pip" 2>/dev/null || true
```

或者更干净的方式：删除 `.venv` 后重新 `uv sync`（会重新下载依赖包）。

## 在 Hermes Agent 中工作的典型模式

### 模式 A：仅使用 Hermes terminal 执行远程命令（推荐）
Hermes 的 `terminal()` 工具可以通过 `ssh lab '...'` 直接操作远程服务器。适合大部分场景。

```python
# Hermes 中的典型用法
terminal(command="ssh lab 'export PATH=/usr/local/cuda/bin:\$PATH && cd ~/code/my-project && python train.py --epochs 100'", timeout=600)
```

**注意：** 对于长时间运行的任务（>10 分钟），使用 tmux 或 Docker 后台模式，然后定期检查进度。

### 模式 B：tmux + 定时检查
```python
# Step 1: 在 tmux 中启动实验
terminal(command="""ssh lab 'tmux new-session -d -s exp1 \
  "cd ~/code/my-project && export PATH=/usr/local/cuda/bin:\$PATH && CUDA_VISIBLE_DEVICES=0 python train.py"'""")

# Step 2: 一段时间后检查输出
terminal(command="ssh lab 'tmux capture-pane -t exp1 -p -S -20'")

# Step 3: 完成后清理
terminal(command="ssh lab 'tmux kill-session -t exp1'")
```

### 模式 C：本地编写 → scp 上传 → 远程执行
```python
# Step 1: 本地编写代码
write_file(path="/tmp/train.py", content="...")

# Step 2: 上传到 lab
terminal(command="scp /tmp/train.py lab:~/code/my-project/")

# Step 3: 在 lab 上执行（记得加 CUDA 路径）
terminal(command="ssh lab 'export PATH=/usr/local/cuda/bin:\$PATH && cd ~/code/my-project && python train.py'")
```

### 模式 D：使用 rsync 持续同步（适合迭代开发）
```bash
# 在本地项目目录中编写代码，然后增量同步
rsync -avz --exclude='__pycache__' --exclude='.git' --exclude='*.pyc' \
  ./ lab:~/code/my-project/
```

## 注意事项与坑

1. **SSH 超时** — SSH 配置中已设置 `ServerAliveInterval 60` 和 `ServerAliveCountMax 3`，保持长连接
2. **Python 版本低** — 系统 Python 3.8.10 较老。如果需要新版本 Python，建议用 Docker 或自己编译
3. **无 conda** — 没有 conda 环境。可以用 venv：`python3 -m venv ~/venvs/myenv`
4. **CUDA 默认不在 PATH 中** — 必须手动 `export PATH=/usr/local/cuda/bin:$PATH`，或在命令前加、或写入 .zshrc。多个 CUDA 版本共存，通过 `/usr/local/cuda-11.8` 等路径切换
5. **无 nvcc 在 PATH 中**：直接运行 nvcc 会提示找不到。需要用完整路径 `/usr/local/cuda/bin/nvcc` 或先设 PATH
6. **tmux session 持久化** — SSH 断开后 tmux session 不会丢失，这是实验的保障
7. **~/.bashrc 与 ~/.zshrc 有修改** — 远程 shell 配置可能影响环境变量，注意 .bashrc/.zshrc 中可能有的自定义逻辑
8. **RemoteForward 7897** — SSH 配置中将远程 7897 端口转发到本地 localhost:7897，可能与某些服务有关
9. **uv + PyTorch CUDA wheel 选择** — lab 当前系统 CUDA toolkit 默认是 12.6，NVIDIA driver 570.x 的 `nvidia-smi` 可显示 CUDA 12.8；当项目的 `uv.lock` 锁到 PyTorch CUDA 13（如 `nvidia-*-cu13`、`cuda-toolkit 13.x`）时，优先考虑改用 PyTorch cu126/cu128 wheel，而不是手写 `uv.lock`。推荐在项目 `pyproject.toml` 中配置 `tool.uv.sources` + `[[tool.uv.index]]` 指向官方 PyTorch CUDA index，然后运行 `uv lock --upgrade-package torch` 重新生成 lock。详见 `references/uv-pytorch-cuda.md`。
10. **uv 不在远程 PATH 中** — `uv` 安装在 `/public/home/caiyiwen/.local/bin/uv`，但远程 zsh 默认不会加载该路径。通过 SSH 执行命令时必须显式导出 PATH：`export PATH="/public/home/caiyiwen/.local/bin:$PATH" && uv ...`。不要假设 `ssh lab 'uv ...'` 能直接找到 uv。
11. **zsh `source` 多文件陷阱** — 在 zsh 中，`source file1 file2 file3` 不会依次 source 所有文件，只会 source 第一个文件，其余作为参数。需要遍历 source 时，使用 `for f in path/*.zsh; do source "$f"; done`。在远程编写 zsh 脚本时注意此行为差异。

## 参考文件

- **`references/uv-pytorch-cuda.md`** — lab 上使用 uv 管理 PyTorch CUDA wheel 的配置模式、cu126 index 示例、验证命令和常见坑。

- **`references/gateway-model-probe.md`** — 在启动 subagent 委托前，快速验证主 agent 和子 agent 模型可用性的探测脚本和检查清单。当用户指定了模型分配策略（如 nowcoding/gpt-5.5 主 agent + kimi-k2.6 子 agent）时，先运行此探测确认两端模型均可达。

- **`references/a800-server.md`** — 另一台服务器 A800（10.160.4.104）的详细配置、SSH 设置和与 lab 互通的方法。