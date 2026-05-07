---
name: himalaya
description: "通过 IMAP/SMTP 管理邮件的命令行工具。使用 `himalaya` 在终端中列出、阅读、撰写、回复、转发、搜索和整理邮件。支持多账户和 MML（MIME 元语言）格式撰写邮件。"
---

# Himalaya Email CLI

Himalaya 是一个 CLI 邮件客户端，允许你从终端使用 IMAP、SMTP、Notmuch 或 Sendmail 后端管理邮件。

## 参考

- `references/configuration.md`（配置文件设置 + IMAP/SMTP 认证）
- `references/message-composition.md`（撰写邮件的 MML 语法）

## 先决条件

1. 安装 Himalaya CLI（用 `himalaya --version` 验证）
2. 配置文件位于 `~/.config/himalaya/config.toml`
3. 配置 IMAP/SMTP 凭证（密码安全存储）

## 配置设置

运行交互式向导设置账户：
```bash
himalaya account configure
```

或手动创建 `~/.config/himalaya/config.toml`：
```toml
[accounts.personal]
email = "you@example.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@example.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show email/imap"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show email/smtp"
```

## 常用操作

### 列出文件夹
```bash
himalaya folder list
```

### 列出邮件
```bash
himalaya envelope list
himalaya envelope list --folder "Sent"
himalaya envelope list --page 1 --page-size 20
```

### 搜索邮件
```bash
himalaya envelope list from john@example.com subject meeting
```

### 阅读邮件
```bash
himalaya message read 42
himalaya message export 42 --full
```

### 回复/转发
```bash
himalaya message reply 42
himalaya message reply 42 --all
himalaya message forward 42
```

### 撰写新邮件
```bash
himalaya message write
himalaya message write -H "To:recipient@example.com" -H "Subject:Test" "Message body here"
```

### 移动/复制/删除
```bash
himalaya message move 42 "Archive"
himalaya message copy 42 "Important"
himalaya message delete 42
```

### 标记
```bash
himalaya flag add 42 --flag seen
himalaya flag remove 42 --flag seen
```
