# pi agent 配置（脱敏模板）

本目录同步 `~/.pi/agent/` 的配置，作为单一事实源。`install.sh` 负责安装到新机器。

| 文件 | 说明 | 安装方式 |
|------|------|----------|
| `settings.json` | 主配置（skills/theme/provider/packages/enabledModels） | 软链接 |
| `starline.json` | starline 插件显示配置 | 软链接 |
| `auth.json.example` | 认证模板（**含密钥，只提供占位符**） | copy_if_missing |
| `extensions/*.ts` | 自定义 provider 扩展（**apiKey 已替换为 `sk-REPLACE_ME`**） | copy_if_missing |

## 注意事项

- `auth.json`（deepseek api_key + openai-codex OAuth token）与 `extensions/` 里硬编码的
  apiKey 是真实密钥，**绝不提交**；本机文件在 `~/.pi/agent/` 下由 pi 自行维护/刷新。
- 新机器安装后需手动填写：
  1. `~/.pi/agent/auth.json`（用 `auth.json.example` 模板，填真实 key）
  2. `~/.pi/agent/extensions/nowcoding.ts` / `nowcoding-claude.ts` 中的 `apiKey`（用
     `pi/extensions/*.ts` 模板，把 `sk-REPLACE_ME` 换成真实 key）
- `settings.json` 的 `skills` 数组指向 `~/Documents/code/dotfiles/skills`（本仓库），
  新机器需先 clone 到该路径（或安装后手动改）。
- `lastChangelogVersion` 是 pi 回写的字段，升级后仓库文件可能显示修改，属正常现象。
- `models-store.json`、`npm/`、`sessions/` 等是运行时缓存，不同步。
