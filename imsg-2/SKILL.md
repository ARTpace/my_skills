---
name: imsg
description: "iMessage/短信命令行工具，支持列出聊天、查看历史记录、监听和发送消息。"
---

# imsg

使用 `imsg` 在 macOS 上读取和发送 Messages.app iMessage/SMS。

要求
- Messages.app 已登录
- 终端具有完全磁盘访问权限
- 控制 Messages.app 的自动化权限（用于发送）

常用命令
- 列出聊天：`imsg chats --limit 10 --json`
- 历史记录：`imsg history --chat-id 1 --limit 20 --attachments --json`
- 监听：`imsg watch --chat-id 1 --attachments`
- 发送：`imsg send --to "+14155551212" --text "hi" --file /path/pic.jpg`

注意
- `--service imessage|sms|auto` 控制投递方式。
- 发送前确认收件人 + 消息。
