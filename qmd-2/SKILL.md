---
name: qmd
description: "本地混合搜索 Markdown 笔记和文档。用于搜索笔记、查找相关内容或从已索引的集合中检索文档。"
---

# qmd - 快速 Markdown 搜索

Markdown 笔记、文档和知识库的本地搜索引擎。索引一次，快速搜索。

## 何时使用（触发短语）

- "搜索我的笔记 / 文档 / 知识库"
- "查找相关笔记"
- "从我的集合中检索 markdown 文档"
- "搜索本地 markdown 文件"

## 默认行为（重要）

- 优先 `qmd search`（BM25）。它通常是即时的，应该是默认选择。
- 仅当关键词搜索失败且需要语义相似性时才使用 `qmd vsearch`（冷启动时可能非常慢）。
- 除非用户明确要求最高质量的混合结果并能容忍长运行时间/超时，否则避免使用 `qmd query`。

## 先决条件

- Bun >= 1.0.0
- macOS: `brew install sqlite`（SQLite 扩展）
- 确保 PATH 包含：`$HOME/.bun/bin`

安装 Bun (macOS)：`brew install oven-sh/bun/bun`

## 安装

`bun install -g https://github.com/tobi/qmd`

## 设置

```bash
qmd collection add /path/to/notes --name notes --mask "**/*.md"
qmd context add qmd://notes "此集合的描述"  # 可选
qmd embed  # 一次性启用向量 + 混合搜索
```

## 索引内容

- 用于 Markdown 集合（通常是 `**/*.md`）。
- 在我们的测试中，"混乱"的 Markdown 没问题：分块是基于内容的（大约每个块几百个 token），不是严格的标题/结构基础。
- 不能替代代码搜索；对仓库/源代码树使用代码搜索工具。

## 搜索模式

- `qmd search`（默认）：快速关键词匹配（BM25）
- `qmd vsearch`（最后手段）：语义相似性（向量）。由于本地 LLM 工作在向量查找之前，通常很慢。
- `qmd query`（通常跳过）：混合搜索 + LLM 重新排序。通常比 `vsearch` 慢，可能超时。

## 性能说明

- `qmd search` 通常是即时的。
- `qmd vsearch` 在某些机器上可能需要约 1 分钟，因为查询扩展可能会将本地模型（例如 Qwen3-1.7B）加载到内存中；向量查找本身通常很快。
- `qmd query` 在 `vsearch` 之上添加 LLM 重新排序，因此它可能更慢，对交互式使用不太可靠。
- 如果需要重复进行语义搜索，考虑保持进程/模型热（例如，如果你的设置中可用，使用长期运行的 qmd/MCP 服务器模式），而不是每次调用冷启动 LLM。

## 常用命令

```bash
qmd search "query"             # 默认
qmd vsearch "query"
qmd query "query"
qmd search "query" -c notes     # 搜索特定集合
qmd search "query" -n 10        # 更多结果
qmd search "query" --json       # JSON 输出
qmd search "query" --all --files --min-score 0.3
```

## 有用选项

- `-n <num>`：结果数量
- `-c, --collection <name>`：限制到集合
- `--all --min-score <num>`：返回高于阈值的所有匹配
- `--json` / `--files`：代理友好的输出格式
- `--full`：返回完整文档内容

## 检索

```bash
qmd get "path/to/file.md"       # 完整文档
qmd get "#docid"                # 按搜索结果中的 ID
qmd multi-get "journals/2025-05*.md"
qmd multi-get "doc1.md, doc2.md, #abc123" --json
```

## 维护

```bash
qmd status                      # 索引健康
qmd update                      # 重新索引更改的文件
qmd embed                       # 更新嵌入
```

## 保持索引新鲜
