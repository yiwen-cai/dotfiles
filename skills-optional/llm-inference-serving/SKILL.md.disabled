---
name: llm-inference-serving
description: Deploy and serve LLMs — local GGUF inference, high-throughput vLLM serving, structured generation with Outlines,
  and model abliteration.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# LLM Inference and Serving

Deploy and serve large language models. Covers local GGUF inference, high-throughput serving, structured generation, and model abliteration.

## When to Use

- User wants to run a model locally
- Need to serve models in production
- Want structured/typed outputs from LLMs
- Need to remove refusal behaviors from models
- Comparing inference frameworks

## Framework Comparison

| Framework | Use Case | Key Feature |
|-----------|----------|-------------|
| **llama.cpp** | Local/edge inference | GGUF quantization, CPU/GPU |
| **vLLM** | Production serving | PagedAttention, high throughput |
| **Outlines** | Structured generation | JSON/regex/Pydantic constraints |
| **OBLITERATUS** | Model surgery | Refusal removal, weight projection |

## llama.cpp — Local GGUF Inference

### Installation
```bash
# macOS
brew install llama.cpp

# From source
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build && cmake --build build --config Release
```

### Run from Hugging Face Hub
```bash
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

### Python Bindings
```python
from llama_cpp import Llama

llm = Llama(
    model_path="./model-q4_k_m.gguf",
    n_ctx=4096,
    n_gpu_layers=35,
    chat_format="llama-3",
)

out = llm("What is machine learning?", max_tokens=256)
```

### Quant Selection
- **Q4_K_M**: General chat (default)
- **Q5_K_M**: Code/technical work
- **Q6_K**: High quality if memory allows
- **Q3_K_M**: Tight RAM budgets
- **IQ variants**: Extreme compression

## vLLM — High-Throughput Serving

### Installation
```bash
pip install vllm
```

### Basic Server
```bash
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192
```

### OpenAI-Compatible API
```python
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8000/v1', api_key='EMPTY')

response = client.chat.completions.create(
    model='meta-llama/Llama-3-8B-Instruct',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
```

### Production Deployment
```bash
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics \
  --metrics-port 9090
```

### Key Metrics
- TTFT (time to first token) < 500ms
- Throughput > 100 req/sec
- GPU utilization > 80%

## Outlines — Structured Generation

### Installation
```bash
pip install outlines
```

### JSON with Pydantic
```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, User)
user = generator("Extract: John Doe, 30, john@example.com")
```

### Choice Generation
```python
generator = outlines.generate.choice(model, ["positive", "negative", "neutral"])
sentiment = generator("Review: This is great!")
```

### Regex Generation
```python
generator = outlines.generate.regex(model, r"[0-9]{3}-[0-9]{3}-[0-9]{4}")
phone = generator("Generate phone number:")
```

### Backends
- Transformers (Hugging Face)
- llama.cpp (GGUF)
- vLLM (high-throughput)
- OpenAI (limited support)

## OBLITERATUS — Model Abliteration

### Installation
```bash
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS && pip install -e .
```

### Basic Usage
```bash
# Default method (advanced)
obliteratus obliterate meta-llama/Llama-3-8B-Instruct \
  --method advanced \
  --output-dir ./abliterated-models
```

### Method Selection
| Method | Use Case |
|--------|----------|
| `basic` | Quick test, prototyping |
| `advanced` | Default, most models |
| `aggressive` | Stubborn refusals |
| `surgical` | Reasoning models (R1) |
| `nuclear` | MoE models (DeepSeek) |

### Verification
After abliteration, check:
- Refusal rate < 5%
- Perplexity change < 10%
- KL divergence < 0.1

### License Warning
OBLITERATUS is AGPL-3.0. Always invoke via CLI, never import as a library.

## Hardware Requirements

| Use Case | VRAM | Example |
|----------|------|---------|
| Small models (7B-13B) | 24GB | 1x A10 |
| Medium models (30B-40B) | 80GB | 2x A100 |
| Large models (70B+) | 160GB | 4x A100 |
| Quantized (70B AWQ) | 40GB | 1x A100 |

## When to Choose What

| Scenario | Solution |
|----------|----------|
| Local chat, single user | llama.cpp |
| Production API, 100+ req/sec | vLLM |
| Need typed JSON outputs | Outlines |
| Remove model refusals | OBLITERATUS |
| Edge/CPU only | llama.cpp Q4 |
| Maximum throughput | vLLM + tensor parallelism |

## Common Pitfalls

1. **OOM during loading**: Reduce `--gpu-memory-utilization` or use quantization
2. **Slow TTFT**: Enable prefix caching or chunked prefill
3. **Invalid JSON**: Use Outlines for guaranteed valid structure
4. **Refusals persist**: Try `aggressive` method or increase `--n-directions`
5. **Model not found**: Use `--trust-remote-code` for custom models

## Related Skills

- `llm-fine-tuning` — For training models before serving
- `cs336-stanford-course` — For model fundamentals
- `research-paper-writing` — For documenting deployments