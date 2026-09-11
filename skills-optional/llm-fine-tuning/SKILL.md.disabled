---
name: llm-fine-tuning
description: Fine-tune large language models with Axolotl, TRL, and Unsloth — LoRA, QLoRA, DPO, GRPO, and full fine-tuning
  workflows.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# LLM Fine-Tuning

Fine-tune large language models using Axolotl, TRL, and Unsloth. Covers LoRA, QLoRA, DPO, GRPO, and full fine-tuning workflows.

## When to Use

- User wants to fine-tune a model on custom data
- Need to choose between fine-tuning frameworks
- Setting up training pipelines for specific methods (SFT, DPO, PPO, GRPO)
- Optimizing training speed and memory usage

## Framework Comparison

| Feature | Axolotl | TRL | Unsloth |
|---------|---------|-----|---------|
| Config style | YAML | Python | Python |
| Speed | Standard | Standard | 2-5x faster |
| Memory | Standard | Standard | 50-80% less |
| Methods | SFT, DPO, ORPO | SFT, DPO, PPO, GRPO | SFT, DPO |
| Ease of use | High (YAML) | Medium | Medium |
| Best for | Quick experiments | Research flexibility | Speed/memory |

## Axolotl

### Quick Start
```bash
# Install
pip install axolotl[flash-attn]

# Train with YAML config
axolotl train config.yaml
```

### YAML Config Structure
```yaml
base_model: meta-llama/Llama-3-8B-Instruct
model_type: LlamaForCausalLM
load_in_4bit: true
adapter: lora
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target_linear: true
lora_fan_in_fan_out: false

# Dataset
datasets:
  - path: user/dataset
    type: alpaca
    split: train

# Training
num_epochs: 3
micro_batch_size: 1
gradient_accumulation_steps: 4
learning_rate: 0.0002
optimizer: adamw_bnb_8bit
lr_scheduler: cosine
warmup_steps: 100

# Output
output_dir: ./outputs
```

### Dataset Formats
- `alpaca`: instruction-input-output
- `sharegpt`: conversation format
- `completion`: raw text completion
- Custom: define `type: custom` with prompt template

## TRL (Transformers Reinforcement Learning)

### Installation
```bash
pip install trl
```

### SFT Training
```python
from trl import SFTTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        output_dir="./outputs",
        num_train_epochs=3,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
    ),
)
trainer.train()
```

### DPO Training
```python
from trl import DPOTrainer

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    beta=0.1,  # DPO temperature
)
trainer.train()
```

### GRPO Training
```python
from trl import GRPOTrainer

trainer = GRPOTrainer(
    model=model,
    reward_funcs=[reward_func],
    args=training_args,
    train_dataset=dataset,
)
trainer.train()
```

## Unsloth

### Installation
```bash
pip install unsloth
```

### Quick Start
```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B",
    max_seq_length=2048,
    dtype=None,  # Auto-detect
    load_in_4bit=True,
)

# Add LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

# Train
trainer = SFTTrainer(...)
trainer.train()
```

### Key Benefits
- **2-5x faster** training via optimized kernels
- **50-80% less VRAM** via optimized gradient checkpointing
- **Automatic RoPE scaling** for longer contexts
- **Native GGUF export** for llama.cpp deployment

## Method Selection Guide

| Goal | Method | Framework |
|------|--------|-----------|
| Instruction following | SFT | Any |
| Preference alignment | DPO | TRL, Axolotl |
| RL with custom rewards | PPO | TRL |
| Group-relative optimization | GRPO | TRL |
| Quick experiments | LoRA | Axolotl, Unsloth |
| Max speed | QLoRA | Unsloth |
| Research flexibility | Custom | TRL |

## Common Pitfalls

1. **OOM errors**: Reduce batch size, enable gradient checkpointing, use QLoRA
2. **Overfitting**: Monitor eval loss, use early stopping, reduce epochs
3. **Learning rate too high**: Start with 2e-4 for LoRA, 1e-5 for full fine-tuning
4. **Dataset format mismatch**: Verify format matches framework expectations
5. **Forgetting base capabilities**: Use higher alpha/r ratio or train longer
6. **Evaluation**: Always evaluate on held-out data, not just training loss

## Memory Requirements

| Model Size | Full FT | LoRA | QLoRA |
|------------|---------|------|-------|
| 7B | 28GB | 14GB | 6GB |
| 13B | 52GB | 26GB | 10GB |
| 30B | 120GB | 60GB | 20GB |
| 70B | 280GB | 140GB | 40GB |

## Related Skills

- `cs336-stanford-course` — For training fundamentals
- `llm-inference-serving` — For deploying fine-tuned models
- `research-paper-writing` — For writing up results