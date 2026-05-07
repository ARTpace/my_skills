---
name: wacli
description: "通过 wacli CLI 向他人发送 WhatsApp 消息或搜索/同步 WhatsApp 历史记录（非日常聊天用途）。"
---

# wacli

仅当用户明确要求你在 WhatsApp 上给某人发消息或同步/搜索 WhatsApp 历史记录时使用 `wacli`。

安全
- 需要明确的收件人 + 消息文本。
- 发送前确认收件人 + 消息。

认证 + 同步
- `wacli auth`（二维码登录 + 初始同步）
- `wacli sync --follow`（持续同步）
- `wacli doctor`

查找聊天 + 消息
- `wacli chats list --limit 20 --query "名称或号码"`
- `wacli messages search "查询" --limit 20 --chat <jid>`

发送
- 文本：`wacli send text --to "+14155551212" --message "你好！"`
- 文件：`wacli send file --to "+14155551212" --file /path/agenda.pdf --caption "议程"`

注意
- 存储目录：`~/.wacli`（用 `--store` 覆盖）。
- 使用 `--json` 获得机器可读输出。
