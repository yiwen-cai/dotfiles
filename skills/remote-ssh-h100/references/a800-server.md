---
related_servers: [h100]
---

# A800 服务器（a800）

| 项目 | 内容 |
|------|------|
| **SSH 别名** | `a800` |
| **真实地址** | `10.160.4.104:22` |
| **用户** | `caiyiwen` |
| **认证方式** | SSH Key（与 h100 相同，`~/.ssh/id_ed25519`） |
| **操作系统** | Ubuntu |
| **Home** | `/storage/caiyiwen` |
| **Shell** | zsh（oh-my-zsh + powerlevel10k） |
| **GPU** | 2× NVIDIA A800 80GB PCIe |
| **CUDA** | 12.8（`/usr/local/cuda` → cuda-12.8） |
| **Driver** | 580.126.09（CUDA 13.0 compat） |

## 软件工具

| 工具 | 版本 | 安装位置 |
|------|------|----------|
| conda | 26.3.2 | `~/apps/miniconda3` |
| uv | 0.11.21 | `~/.local/bin/uv` |
| nvm / node | 0.40.4 / v24.16.0 LTS | `~/.nvm` |
| lsd | 1.1.5 | `~/.local/bin/lsd` |
| fzf | 0.73.1 | `~/.fzf` |
| ncu | (CUDA 12.8) | `/usr/local/cuda/bin/ncu` |
| nsight-sys | (CUDA 12.8) | `/usr/local/cuda/bin/nsight-sys` |

## SSH 配置

```text
Host a800
    HostName 10.160.4.104
    Port 22
    User caiyiwen
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
```

## 与 h100 互通

- 本机（macOS）通过 SSH 别名 `h100` 和 `a800` 分别访问
- h100 到 a800 直连已配好 SSH key（10.160.4.104）
- 内网延迟：~0.3ms

## 网络注意事项

外部下载速度慢（~200 B/s 到 PyTorch 源），建议：
- 使用清华镜像：`https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu126/`
- 或从 h100 通过内网 rsync/SCP 传输已下载的包
