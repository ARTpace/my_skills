---
name: oracle
description: "使用 @steipete/oracle CLI 将提示词和相关文件打包，获取第二个模型的审查（通过 API 或浏览器），用于调试、重构、设计检查或交叉验证。"
---

# Oracle (CLI)

Oracle 将你的提示词 + 选定文件打包到一个"一次性"请求中，以便另一个模型可以用真实的仓库上下文回答（API 或浏览器自动化）。将输出视为建议：根据代码库 + 测试进行验证。

## 主要用例（浏览器）

默认工作流程：`--engine browser` 与 ChatGPT 中的 GPT。

## 黄金路径

1. 选择精简的文件集（仍然包含真相的最少文件）。
2. 预览你即将发送的内容（`--dry-run` + `--files-report`）。
3. 在浏览器模式下运行以使用通常的 ChatGPT 工作流程；仅在你明确需要时使用 API。
4. 如果运行分离/超时：重新附加到存储的会话（不要重新运行）。

## 命令（首选）

- 显示帮助：`npx -y @steipete/oracle --help`
- 预览（无 token）：`npx -y @steipete/oracle --dry-run summary -p "<task>" --file "src/**" --file "!**/*.test.*"`
- Token/成本检查：`npx -y @steipete/oracle --dry-run summary --files-report -p "<task>" --file "src/**"`
- 浏览器运行：`npx -y @steipete/oracle --engine browser -p "<task>" --file "src/**"`
- 手动粘贴回退：`npx -y @steipete/oracle --render --copy -p "<task>" --file "src/**"`

## 附加文件 (`--file`)

- 包含：`--file "src/**"`、`--file src/index.ts`
- 排除：`--file "!src/**/*.test.ts"`
- 默认忽略的目录：`node_modules`、`dist`、`coverage`、`.git` 等。
- 硬限制：拒绝大于 1 MB 的文件。

## 预算 + 可观察性

- 目标：保持总输入低于约 196k token。
- 使用 `--files-report` 在花费之前发现 token 大户。

## 会话

- 存储在 `~/.oracle/sessions` 下。
- 列表：`oracle status --hours 72`
- 附加：`oracle session <id> --render`
- 使用 `--slug "<3-5 words>"` 获得可读的会话 ID。

## 安全

- 默认不要附加机密。
- 优先选择"刚好足够的上下文"：更少的文件 + 更好的提示胜过整个仓库转储。
