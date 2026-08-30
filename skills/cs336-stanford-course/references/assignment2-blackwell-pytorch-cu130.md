# Assignment 2: Blackwell GPU0 and PyTorch CUDA Wheel Migration

Use this when moving CS336 Assignment 2 runs from A800 GPUs (`sm_80`) to GPU0 Blackwell (`sm_120`).

## Key facts from validated session

- `nvidia-smi` on `a800` showed `Driver Version: 580.126.09` and `CUDA Version: 13.0`.
- `nvcc --version` showed CUDA toolkit `12.8`; this is the local compiler/toolkit, not the CUDA runtime bundled in PyTorch wheels.
- The failing env was `torch 2.11.0+cu126`, `torch.version.cuda == 12.6`, and `torch.cuda.get_arch_list()` only included `sm_50 ... sm_90`.
- `CUDA_VISIBLE_DEVICES=0` minimal PyTorch matmul failed with `CUDA error: no kernel image is available for execution on the device`, confirming the wheel lacked Blackwell `sm_120` support.
- PyTorch official wheel indexes contained Linux x86_64 CPython 3.13 wheels for:
  - `torch-2.11.0+cu128-cp313-cp313-manylinux_2_28_x86_64.whl`
  - `torch-2.11.0+cu130-cp313-cp313-manylinux_2_28_x86_64.whl`
  - `torch-2.12.x+cu130-cp313-cp313-manylinux_2_28_x86_64.whl`
- Linux `glibc 2.31` satisfies PyTorch's modern wheel baseline (`glibc >= 2.28`).

## Version interpretation

- `nvidia-smi` CUDA Version = highest CUDA driver API/runtime compatibility exposed by the installed NVIDIA driver.
- `nvcc --version` = local CUDA toolkit compiler version; PyTorch pip wheels do not primarily depend on this for normal tensor execution.
- `torch.version.cuda` = CUDA runtime version bundled with the installed PyTorch wheel.
- For Blackwell, the decisive check is whether `torch.cuda.get_arch_list()` includes `sm_120`, followed by a real GPU0 matmul smoke test.

## uv workspace pitfall

Assignment 2 uses editable `cs336-basics`. If top-level `pyproject.toml` is migrated from `cu126` to `cu130` but `cs336-basics/pyproject.toml` still references `cu126`, `uv lock --upgrade-package torch` fails with conflicting indexes:

```text
Requirements contain conflicting indexes for package `torch`:
- https://download.pytorch.org/whl/cu126
- https://download.pytorch.org/whl/cu130
```

Fix by keeping all workspace/editable package torch dependencies and `tool.uv.sources` entries on the same PyTorch CUDA index. In this session, both `pyproject.toml` and `cs336-basics/pyproject.toml` were set to:

```toml
"torch==2.11.0+cu130"
torch = [{ index = "pytorch-cu130", marker = "sys_platform == 'linux'" }]

[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true
```

Validate without writing the lockfile first:

```bash
uv lock --dry-run --upgrade-package torch
```

## Network/download pitfall

`uv sync` may appear to hang while downloading/unpacking the large `torch` and CUDA 13 dependency wheels. Diagnose before killing:

```bash
ps -eo pid,ppid,stat,etime,pcpu,pmem,args | grep -E '[u]v sync|[u]v lock|[u]v pip'
ss -tpn 2>/dev/null | grep -E 'uv|443|7897'
lsof -p <uv_pid> 2>/dev/null | grep -E '\.cache/uv|\.tmp|torch|cu13'
find ~/.cache/uv -maxdepth 1 -type d -name '.tmp*' -print
```

If `uv sync` fails with `download-r2.pytorch.org ... operation timed out`, prefer direct first because the proxy may be much slower:

```bash
UV_HTTP_TIMEOUT=600 uv sync
```

Fallback with proxy:

```bash
all_proxy=http://127.0.0.1:7897 \
https_proxy=http://127.0.0.1:7897 \
UV_HTTP_TIMEOUT=600 \
uv sync
```

If interrupted, stop leftover `uv` processes and remove unfinished cache temp dirs before retrying:

```bash
pkill -f 'uv sync' || true
find ~/.cache/uv -maxdepth 1 -type d -name '.tmp*' -exec rm -rf {} +
```

## Minimal safe migration steps

Do not run these unless the user accepts a large wheel download.

```bash
cd /storage/caiyiwen/code/cs336/assignment/assignment2-systems
uv lock --dry-run --upgrade-package torch
uv lock --upgrade-package torch
UV_HTTP_TIMEOUT=600 uv sync
CUDA_VISIBLE_DEVICES=0 uv run python - <<'PY'
import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.get_device_name(0))
print(torch.cuda.get_device_capability(0))
print(torch.cuda.get_arch_list())
x = torch.randn(1024, 1024, device="cuda")
y = x @ x
torch.cuda.synchronize()
print("ok", y.shape, y.mean().item())
PY
```

Only migrate benchmarks to GPU0 after the arch list includes `sm_120` and the matmul smoke test passes.

## Validated post-sync smoke tests

After successful sync in this session:

- `.venv/bin/python` reported `torch 2.11.0+cu130`, `torch.version.cuda == 13.0`.
- `torch.cuda.get_arch_list()` returned `['sm_75', 'sm_80', 'sm_86', 'sm_90', 'sm_100', 'sm_120']`.
- `CUDA_VISIBLE_DEVICES=0` on GPU0 Blackwell passed:
  - FP32 matmul
  - BF16 matmul
  - `torch.nn.functional.scaled_dot_product_attention(..., is_causal=True)` forward/backward
  - `cs336_systems/benchmark.py` small forward/backward smoke
- `CUDA_VISIBLE_DEVICES=1` on A800 also passed a matmul smoke test under the same `cu130` env.
