import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/**
 * NowCoding Claude 第三方 provider（Claude Code / Anthropic Messages 格式）
 * - baseUrl: https://nowcoding.ai （SDK 自动追加 /v1/messages）
 * - api: anthropic-messages
 * - 模型列表来自 GET https://nowcoding.ai/v1/models（claude token 分组）
 */
export default function (pi: ExtensionAPI) {
  pi.registerProvider("nowcoding-claude", {
    name: "NowCoding Claude",
    baseUrl: "https://nowcoding.ai",
    apiKey: "sk-REPLACE_ME",
    api: "anthropic-messages",
    models: [
      {
        id: "claude-haiku-4-5-20251001",
        name: "Claude Haiku 4.5",
        reasoning: true,
        input: ["text", "image"],
        cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
        contextWindow: 200000,
        maxTokens: 64000,
        compat: { supportsStrictTools: true },
      },
      {
        id: "claude-opus-4-6",
        name: "Claude Opus 4.6",
        reasoning: true,
        thinkingLevelMap: { max: "max" },
        input: ["text", "image"],
        cost: { input: 5, output: 25, cacheRead: 0.5, cacheWrite: 6.25 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: { forceAdaptiveThinking: true, supportsStrictTools: true },
      },
      {
        id: "claude-opus-4-7",
        name: "Claude Opus 4.7",
        reasoning: true,
        thinkingLevelMap: { xhigh: "xhigh", max: "max" },
        input: ["text", "image"],
        cost: { input: 5, output: 25, cacheRead: 0.5, cacheWrite: 6.25 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          forceAdaptiveThinking: true,
          supportsTemperature: false,
          supportsStrictTools: true,
        },
      },
      {
        id: "claude-opus-4-8",
        name: "Claude Opus 4.8",
        reasoning: true,
        thinkingLevelMap: { xhigh: "xhigh", max: "max" },
        input: ["text", "image"],
        cost: { input: 5, output: 25, cacheRead: 0.5, cacheWrite: 6.25 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          forceAdaptiveThinking: true,
          supportsTemperature: false,
          supportsStrictTools: true,
        },
      },
      {
        id: "claude-opus-5",
        name: "Claude Opus 5",
        reasoning: true,
        defaultThinking: "xhigh",
        thinkingLevelMap: { xhigh: "xhigh", max: "max" },
        input: ["text", "image"],
        cost: { input: 5, output: 25, cacheRead: 0.5, cacheWrite: 6.25 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: {
          forceAdaptiveThinking: true,
          supportsTemperature: false,
          supportsStrictTools: true,
        },
      },
      {
        id: "claude-sonnet-4-6",
        name: "Claude Sonnet 4.6",
        reasoning: true,
        thinkingLevelMap: { max: "max" },
        input: ["text", "image"],
        cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: { forceAdaptiveThinking: true, supportsStrictTools: true },
      },
      {
        id: "claude-sonnet-5",
        name: "Claude Sonnet 5",
        reasoning: true,
        thinkingLevelMap: { xhigh: "xhigh", max: "max" },
        input: ["text", "image"],
        cost: { input: 2, output: 10, cacheRead: 0.2, cacheWrite: 2.5 },
        contextWindow: 1000000,
        maxTokens: 128000,
        compat: { forceAdaptiveThinking: true, supportsStrictTools: true },
      },
    ],
  });
}
