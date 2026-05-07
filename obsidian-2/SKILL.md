---
name: obsidian
description: "管理 Obsidian 知识库（纯 Markdown 笔记），并通过 obsidian-cli 进行自动化操作。"
homepage: https://help.obsidian.md
metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["obsidian-cli"]},"install":[{"id":"brew","kind":"brew","formula":"yakitrak/yakitrak/obsidian-cli","bins":["obsidian-cli"],"label":"Install obsidian-cli (brew)"}]}}
---

# Obsidian

Obsidian 仓库 = 磁盘上的普通文件夹。

仓库结构（典型）
- 笔记：`*.md`（纯文本 Markdown；可用任何编辑器编辑）
- 配置：`.obsidian/`（工作区 + 插件设置；通常不从脚本修改）
- 画布：`*.canvas`（JSON）
- 附件：你在 Obsidian 设置中选择的任何文件夹（图片/PDF等）

## 查找活动仓库

Obsidian 桌面版在此跟踪仓库（真相来源）：
- `~/Library/Application Support/obsidian/obsidian.json`

`obsidian-cli` 从该文件解析仓库；仓库名称通常是**文件夹名称**（路径后缀）。

快速了解"哪个仓库是活动的 / 笔记在哪里？"
- 如果你已设置默认值：`obsidian-cli print-default --path-only`
- 否则，读取 `~/Library/Application Support/obsidian/obsidian.json` 并使用 `"open": true` 的仓库条目。

注意
- 多个仓库很常见（iCloud vs `~/Documents`，工作/个人等）。不要猜测；读取配置。
- 避免在脚本中写入硬编码的仓库路径；优先读取配置或使用 `print-default`。

## obsidian-cli 快速开始

选择默认仓库（一次）：
- `obsidian-cli set-default "<vault-folder-name>"`
- `obsidian-cli print-default` / `obsidian-cli print-default --path-only`

搜索
- `obsidian-cli search "query"`（笔记名称）
- `obsidian-cli search-content "query"`（笔记内部；显示片段 + 行号）

创建
- `obsidian-cli create "Folder/New note" --content "..." --open`
- 需要 Obsidian URI 处理程序（`obsidian://…`）正常工作（Obsidian 已安装）。
- 避免通过 URI 在"隐藏"点文件夹下创建笔记（例如 `.something/...`）；Obsidian 可能拒绝。

移动/重命名（安全重构）
- `obsidian-cli move "old/path/note" "new/path/note"`
- 更新整个仓库中的 `[[wikilinks]]` 和常见 Markdown 链接（这是相对于 `mv` 的主要优势）。

删除
- `obsidian-cli delete "path/note"`

适当时优先直接编辑：打开 `.md` 文件并修改；Obsidian 会检测到更改。
