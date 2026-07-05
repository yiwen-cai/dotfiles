# Gateway 模型可用性探测脚本

用于在启动 subagent 委托前，快速验证主 agent 和子 agent 的模型是否可用。

## 使用场景

用户指定了模型分配策略（如 nowcoding/gpt-5.5 主 agent + kimi-k2.6 子 agent），在正式委托前运行此脚本确认两端模型均可达。

## 脚本

```bash
#!/bin/bash
# gateway-model-probe.sh
# 探测 gateway 配置的模型可用性

set -e

# 读取 .env 中的 key（如果存在）
NOWCODING_KEY="${NOWCODING_API_KEY:-}"
KIMI_KEY="${KIMI_API_KEY:-}"

# 如果 .env 中有 key，source 它
if [ -f ~/.hermes/.env ]; then
    source ~/.hermes/.env 2>/dev/null || true
fi

# 从 config.yaml 读取 nowcoding key（作为 fallback）
if [ -z "$NOWCODING_KEY" ]; then
    NOWCODING_KEY=$(grep -A5 "nowcoding:" ~/.hermes/config.yaml | grep "api_key:" | head -1 | awk '{print $2}' | tr -d '"')
fi

echo "=== Probing nowcoding/gpt-5.5 ==="
if curl -s -o /dev/null -w "%{http_code}" https://nowcoding.ai/v1/models \
    -H "Authorization: Bearer ${NOWCODING_KEY}" | grep -q "200"; then
    echo "  Endpoint: OK"
    
    # 测试模型列表
    MODELS=$(curl -s https://nowcoding.ai/v1/models \
        -H "Authorization: Bearer ${NOWCODING_KEY}" 2>/dev/null)
    if echo "$MODELS" | grep -q "gpt-5.5"; then
        echo "  Model gpt-5.5: FOUND"
    else
        echo "  Model gpt-5.5: NOT FOUND in model list"
    fi
    
    # 测试实际调用
    RESP=$(curl -s -X POST https://nowcoding.ai/v1/chat/completions \
        -H "Authorization: Bearer ${NOWCODING_KEY}" \
        -H "Content-Type: application/json" \
        -d '{"model":"gpt-5.5","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}' 2>/dev/null)
    if echo "$RESP" | grep -q "choices"; then
        echo "  Chat completion: OK"
        echo "  Response: $(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo 'N/A')"
    else
        echo "  Chat completion: FAILED"
        echo "  Error: $(echo "$RESP" | head -c 200)"
    fi
else
    echo "  Endpoint: FAILED (non-200)"
fi

echo ""
echo "=== Probing kimi-k2.6 ==="
if [ -z "$KIMI_KEY" ]; then
    echo "  No KIMI_API_KEY found in .env or config"
    echo "  Set it with: hermes config set providers.kimi-coding.api_key <key>"
    exit 1
fi

if curl -s -o /dev/null -w "%{http_code}" https://api.kimi.com/coding/v1/models \
    -H "Authorization: Bearer ${KIMI_KEY}" | grep -q "200"; then
    echo "  Endpoint: OK"
    
    RESP=$(curl -s -X POST https://api.kimi.com/coding/v1/chat/completions \
        -H "Authorization: Bearer ${KIMI_KEY}" \
        -H "Content-Type: application/json" \
        -d '{"model":"kimi-k2.6","messages":[{"role":"user","content":"Say OK"}],"max_tokens":5}' 2>/dev/null)
    if echo "$RESP" | grep -q "choices"; then
        echo "  Chat completion: OK"
        echo "  Response: $(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null || echo 'N/A')"
    else
        echo "  Chat completion: FAILED"
        echo "  Error: $(echo "$RESP" | head -c 200)"
    fi
else
    echo "  Endpoint: FAILED (non-200 or auth error)"
fi
```

## 保存位置

```bash
# 保存到 skill 目录
cp gateway-model-probe.sh ~/.hermes/skills/devops/remote-ssh-lab/scripts/
chmod +x ~/.hermes/skills/devops/remote-ssh-lab/scripts/gateway-model-probe.sh
```

## 运行方式

```bash
# 直接运行
bash ~/.hermes/skills/devops/remote-ssh-lab/scripts/gateway-model-probe.sh

# 或在 hermes 中通过 terminal 调用
terminal(command="bash ~/.hermes/skills/devops/remote-ssh-lab/scripts/gateway-model-probe.sh")
```

## 从 session 学到的教训

1. **同一 key 不能跨 provider** — nowcoding 的 key 对 kimi 无效
2. **config.yaml 中的 key 优先于 .env 中的 key** — 当 provider 在 config.yaml 中有 `api_key` 字段时，Hermes 使用它
3. **探测要分三步** — endpoint 可达 → 模型在列表中 → 实际调用成功
4. **任何一步失败都要报告用户** — 不要假设"可能只是暂时的"
