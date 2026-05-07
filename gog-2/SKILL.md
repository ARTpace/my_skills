---
name: gog
description: "Google Workspace 命令行工具，支持 Gmail、日历、云端硬盘、通讯录、表格和文档。"
---

# gog

使用 `gog` 操作 Gmail/日历/云端硬盘/通讯录/表格/文档。需要 OAuth 设置。

设置（一次性）
- `gog auth credentials /path/to/client_secret.json`
- `gog auth add you@gmail.com --services gmail,calendar,drive,contacts,sheets,docs`
- `gog auth list`

常用命令
- Gmail 搜索：`gog gmail search 'newer_than:7d' --max 10`
- Gmail 发送：`gog gmail send --to a@b.com --subject "Hi" --body "Hello"`
- 日历：`gog calendar events <calendarId> --from <iso> --to <iso>`
- 云端硬盘搜索：`gog drive search "query" --max 10`
- 通讯录：`gog contacts list --max 20`
- 表格获取：`gog sheets get <sheetId> "Tab!A1:D10" --json`
- 表格更新：`gog sheets update <sheetId> "Tab!A1:B2" --values-json '[["A","B"],["1","2"]]' --input USER_ENTERED`
- 表格追加：`gog sheets append <sheetId> "Tab!A:C" --values-json '[["x","y","z"]]' --insert INSERT_ROWS`
- 表格清除：`gog sheets clear <sheetId> "Tab!A2:Z"`
- 表格元数据：`gog sheets metadata <sheetId> --json`
- 文档导出：`gog docs export <docId> --format txt --out /tmp/doc.txt`
- 文档查看：`gog docs cat <docId>`

注意
- 设置 `GOG_ACCOUNT=you@gmail.com` 避免重复 `--account`。
- 脚本编写时优先使用 `--json` 加 `--no-input`。
- 表格值可通过 `--values-json`（推荐）或内联行传递。
- 文档支持导出/查看/复制。就地编辑需要 Docs API 客户端（不在 gog 中）。
- 发送邮件或创建事件前请确认。
