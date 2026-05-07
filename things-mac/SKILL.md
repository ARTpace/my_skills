---
name: things-mac
description: "通过 macOS 上的 `things` CLI 管理 Things 3（通过 URL Scheme 添加/更新项目和待办事项；从本地 Things 数据库读取/搜索/列出）。当用户要求 CodeBuddy Code 添加任务到 Things、列出收件箱/今天/即将到来的任务、搜索任务或查看项目/区域/标签时使用。"
---

# Things 3 CLI

使用 `things` 读取本地 Things 数据库（收件箱/今天/搜索/项目/区域/标签）并通过 Things URL scheme 添加/更新待办事项。

设置
- 安装：`GOBIN=/opt/homebrew/bin go install github.com/ossianhempel/things3-cli/cmd/things@latest`
- 如果 DB 读取失败：授予调用应用**完全磁盘访问权限**。
- 可选：设置 `THINGSDB` 或传递 `--db` 指向你的 `ThingsData-*` 文件夹。
- 可选：设置 `THINGS_AUTH_TOKEN` 以避免在更新操作时传递 `--auth-token`。

只读（数据库）
- `things inbox --limit 50`
- `things today`
- `things upcoming`
- `things search "查询"`
- `things projects` / `things areas` / `things tags`

写入（URL scheme）
- 优先安全预览：`things --dry-run add "标题"`
- 添加：`things add "标题" --notes "..." --when today --deadline 2026-01-02`
- 带标签：`things add "打电话给牙医" --tags "健康,电话"`
- 清单：`things add "旅行准备" --checklist-item "护照" --checklist-item "机票"`

修改（需要认证令牌）
- 获取 ID：`things search "牛奶" --limit 5`
- 标题：`things update --id <UUID> --auth-token <TOKEN> "新标题"`
- 完成：`things update --id <UUID> --auth-token <TOKEN> --completed`

注意
- 仅限 macOS。
- `--dry-run` 打印 URL 而不打开 Things。
