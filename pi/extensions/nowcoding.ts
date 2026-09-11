import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/**
 * NowCoding 第三方 provider
 * - baseUrl: https://nowcoding.ai/v1 （OpenAI Responses 兼容端点，POST /v1/responses）
 * - api: openai-responses（Codex 同款 Responses 流式格式）
 * - 模型列表来自 GET https://nowcoding.ai/v1/models
 */
export default function (pi: ExtensionAPI) {
  pi.registerProvider("nowcoding", {
    name: "NowCoding",
    baseUrl: "https://nowcoding.ai/v1",
    apiKey: "sk-REPLACE_ME",
    api: "openai-responses",
    models: [
      {
        id: "codex-auto-review",
        name: "Codex Auto Review",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh" },
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.3-codex-spark",
        name: "GPT-5.3 Codex Spark",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh" },
        input: ["text"],
        cost: { input: 1.75, output: 14, cacheRead: 0.175, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.4",
        name: "GPT-5.4",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh" },
        input: ["text", "image"],
        cost: {
          input: 2.5,
          output: 15,
          cacheRead: 0.25,
          cacheWrite: 0,
          tiers: [
            {
              inputTokensAbove: 272000,
              input: 5,
              output: 22.5,
              cacheRead: 0.5,
              cacheWrite: 0,
            },
          ],
        },
        contextWindow: 272000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.4-mini",
        name: "GPT-5.4 mini",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh" },
        input: ["text", "image"],
        cost: { input: 0.75, output: 4.5, cacheRead: 0.075, cacheWrite: 0 },
        contextWindow: 272000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.4-openai-compact",
        name: "GPT-5.4 OpenAI Compact",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh" },
        input: ["text", "image"],
        cost: { input: 2.5, output: 15, cacheRead: 0.25, cacheWrite: 0 },
        contextWindow: 272000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.5",
        name: "GPT-5.5",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh" },
        input: ["text", "image"],
        cost: {
          input: 5,
          output: 30,
          cacheRead: 0.5,
          cacheWrite: 0,
          tiers: [
            {
              inputTokensAbove: 272000,
              input: 10,
              output: 45,
              cacheRead: 1,
              cacheWrite: 0,
            },
          ],
        },
        contextWindow: 272000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.5-openai-compact",
        name: "GPT-5.5 OpenAI Compact",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh" },
        input: ["text", "image"],
        cost: {
          input: 5,
          output: 30,
          cacheRead: 0.5,
          cacheWrite: 0,
          tiers: [
            {
              inputTokensAbove: 272000,
              input: 10,
              output: 45,
              cacheRead: 1,
              cacheWrite: 0,
            },
          ],
        },
        contextWindow: 272000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.6-luna",
        name: "GPT-5.6 Luna",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh", max: "max" },
        input: ["text", "image"],
        cost: {
          input: 0.2,
          output: 1.2,
          cacheRead: 0.02,
          cacheWrite: 0.25,
          tiers: [
            {
              inputTokensAbove: 272000,
              input: 0.4,
              output: 1.8,
              cacheRead: 0.04,
              cacheWrite: 0.5,
            },
          ],
        },
        contextWindow: 272000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.6-sol",
        name: "GPT-5.6 Sol",
        reasoning: true,
        defaultThinking: "xhigh",
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh", max: "max" },
        input: ["text", "image"],
        cost: {
          input: 5,
          output: 30,
          cacheRead: 0.5,
          cacheWrite: 6.25,
          tiers: [
            {
              inputTokensAbove: 272000,
              input: 10,
              output: 45,
              cacheRead: 1,
              cacheWrite: 12.5,
            },
          ],
        },
        contextWindow: 272000,
        maxTokens: 128000,
      },
      {
        id: "gpt-5.6-terra",
        name: "GPT-5.6 Terra",
        reasoning: true,
        thinkingLevelMap: { minimal: "low", xhigh: "xhigh", max: "max" },
        input: ["text", "image"],
        cost: {
          input: 2,
          output: 12,
          cacheRead: 0.2,
          cacheWrite: 2.5,
          tiers: [
            {
              inputTokensAbove: 272000,
              input: 4,
              output: 18,
              cacheRead: 0.4,
              cacheWrite: 5,
            },
          ],
        },
        contextWindow: 272000,
        maxTokens: 128000,
      },
    ],
  });
}
