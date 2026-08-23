# nowcoding.ai — 自定义 OpenAI 兼容 Provider 示例

## 端点信息

- **base_url:** `https://nowcoding.ai/v1`
- **API 格式:** OpenAI Chat Completions（标准）
- **认证:** Bearer Token

## 可用模型

| Model ID | 说明 |
|----------|------|
| gpt-5.5 | 旗舰模型 |
| gpt-5.5-openai-compact | 精简版 |
| gpt-5.4 | 前代旗舰 |
| gpt-5.4-mini | 轻量版 |
| gpt-5.4-openai-compact | 精简版 |
| gpt-5.3-codex | 代码专精 |
| gpt-5.3-codex-openai-compact | 代码精简版 |
| gpt-5.3-codex-spark | 代码快速版 |
| gpt-5.2 | 旧版 |
| gpt-5.2-codex-openai-compact | 旧版代码精简 |
| gpt-5.2-openai-compact | 旧版精简 |

## Config.yaml 配置

```yaml
providers:
  nowcoding:
    base_url: https://nowcoding.ai/v1
    api_key: "<your-nowcoding-api-key>"
    models:
      - gpt-5.5
      - gpt-5.5-openai-compact
      - gpt-5.4
      - gpt-5.4-mini
      - gpt-5.3-codex
      - gpt-5.2
```

## 使用方法

```bash
# 切换到此 provider
hermes --provider nowcoding --model gpt-5.5

# 或在会话中输入 /model，选择 nowcoding → gpt-5.5
```

## 验证命令

```bash
# 列出模型
curl -s https://nowcoding.ai/v1/models \
  -H "Authorization: Bearer $API_KEY" | python3 -m json.tool

# 测试对话
curl -s https://nowcoding.ai/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5","messages":[{"role":"user","content":"ping"}]}'
```
