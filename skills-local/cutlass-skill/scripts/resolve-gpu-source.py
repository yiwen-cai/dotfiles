#!/usr/bin/env python3
"""Resolve a readable GPU documentation checkout locally or over SSH."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

NAME = Path(__file__).resolve().parents[1].name
SAMPLES = {
    'cuda-skill': 'cuda_skill/references/nsys-docs/INDEX.md',
    'cutlass-skill': 'cutlass_skill/repos/cutlass/include/cute/layout.hpp',
    'triton-skill': 'triton_skill/repos/triton/python/tutorials/01-vector-add.py',
    'sglang-skill': 'sglang_skill/repos/sglang/README.md',
}
PROBE = '''import pathlib,sys,json,hashlib
root=pathlib.Path(sys.argv[1]); sample=root/sys.argv[2]
text=sample.read_bytes()
print(json.dumps({'root':str(root),'sample':str(sample),'sha256':hashlib.sha256(text).hexdigest(),'first_line':text.decode('utf-8',errors='replace').splitlines()[0] if text else ''}))'''


def main():
    if NAME not in SAMPLES:
        raise ValueError('Resolver must be installed in one of the four named GPU skill packages')
    override = os.environ.get('GPU_SKILLS_ROOT')
    local = Path(override).expanduser() if override else Path.home() / 'Documents/code/agent-gpu-skills'
    if override or (local / SAMPLES[NAME]).is_file():
        raw = subprocess.check_output([sys.executable, '-c', PROBE, str(local), SAMPLES[NAME]], text=True, timeout=10)
        result = {'transport': 'local', **json.loads(raw)}
    else:
        host = os.environ.get('GPU_SKILLS_HOST', 'h100')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.@-]*', host):
            raise ValueError('Invalid GPU_SKILLS_HOST')
        remote = os.environ.get('GPU_SKILLS_REMOTE_ROOT', '/public/home/caiyiwen/code/agent-gpu-skills')
        command = shlex.join(['python3', '-c', PROBE, remote, SAMPLES[NAME]])
        raw = subprocess.check_output(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', host, command], text=True, timeout=20)
        result = {'transport': 'ssh', 'host': host, **json.loads(raw)}
    result['skill'] = NAME
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'GPU source unavailable: {exc}', file=sys.stderr)
        sys.exit(1)
