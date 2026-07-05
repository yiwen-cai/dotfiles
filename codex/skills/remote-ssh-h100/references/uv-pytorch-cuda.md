# uv + PyTorch CUDA wheels on h100

Use this when a project on h100 uses `uv` and PyTorch, especially when `uv.lock` resolves to CUDA packages that do not match h100's CUDA/driver stack.

## Observed h100 baseline

- System CUDA toolkit symlink: `/usr/local/cuda -> /usr/local/cuda-12.6`
- `nvcc`: CUDA 12.6 (`V12.6.20`)
- NVIDIA driver observed: `570.172.08`
- `nvidia-smi` can report CUDA runtime support as 12.8
- `uv` observed at `/public/home/caiyiwen/.local/bin/uv`, version `0.9.5`
- User-level uv config may exist at `/public/home/caiyiwen/.config/uv/uv.toml`; in one session it used Aliyun PyPI:

```toml
[pip]
index-url = "https://mirrors.aliyun.com/pypi/simple/"
```

## Diagnose current PyTorch/CUDA resolution

```bash
ssh h100 'cd /path/to/project && grep -n "torch\|cu12\|cu13\|cuda\|nvidia" pyproject.toml uv.lock | head -120'
ssh h100 'readlink -f /usr/local/cuda; /usr/local/cuda/bin/nvcc --version; nvidia-smi | sed -n "1,5p"; command -v uv; uv --version'
```

If `uv.lock` contains `nvidia-*-cu13`, `cuda-toolkit 13.x`, or `torch` from PyPI with CUDA 13 dependencies while h100 is CUDA 12.x, prefer resolving against a cu12x PyTorch wheel index.

## Preferred uv configuration for PyTorch cu126

Do not hand-edit `uv.lock`. Edit `pyproject.toml`, then regenerate the lock.

For PyTorch 2.11.0 + cu126 on Linux:

```toml
# in [project].dependencies
"torch==2.11.0+cu126",

[tool.uv.sources]
torch = [
    { index = "pytorch-cu126", marker = "sys_platform == 'linux'" },
]

[[tool.uv.index]]
name = "pytorch-cu126"
url = "https://download.pytorch.org/whl/cu126"
explicit = true
```

Then run:

```bash
uv lock --upgrade-package torch
uv sync
uv run python - <<'PY'
import torch
print("torch:", torch.__version__)
print("torch cuda:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
PY
```

Expected for this configuration:

```text
torch: 2.11.0+cu126
torch cuda: 12.6
cuda available: True
```

## PyTorch index facts discovered

`https://download.pytorch.org/whl/cu126/torch/` contained `torch-2.11.0+cu126` wheels for CPython 3.10, 3.11, 3.12, 3.13, and 3.14 on Linux x86_64/aarch64 and Windows in the checked session. Thus a project with `requires-python = ">=3.12,<3.14"` can use cp312/cp313 wheels.

## Pitfalls

- `nvidia-smi`'s "CUDA Version" is driver runtime support, not the installed toolkit version. Check toolkit with `/usr/local/cuda/bin/nvcc --version` and `readlink -f /usr/local/cuda`.
- PyTorch wheels bundle CUDA runtime libraries; system `/usr/local/cuda` is not the only compatibility factor. The wheel CUDA major version must be supported by the installed driver.
- A domestic PyPI mirror in uv config (e.g. Aliyun) does not replace the PyTorch CUDA wheel index. Keep the explicit PyTorch index for torch.
- Avoid editing `uv.lock` manually; let `uv lock --upgrade-package torch` resolve hashes and transitive NVIDIA packages.
- If the project has academic-integrity instructions (e.g. CS336 `AGENTS.md`) that prohibit repo edits by the agent, provide commands/config snippets for the user rather than modifying the repo directly.
