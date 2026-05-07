---
name: gws-gmail-send
version: 1.0.0
description: "Gmail：发送邮件。"
metadata:
  openclaw:
    category: "productivity"
    requires:
      bins: ["gws"]
    cliHelp: "gws gmail +send --help"
---

# gmail +send

> **前置条件：** 阅读 `../gws-shared/SKILL.md` 了解认证、全局标志和安全规则。如果缺失，运行 `gws generate-skills` 创建。

发送邮件

## 用法

```bash
gws gmail +send --to <EMAIL> --subject <SUBJECT> --body <TEXT>
```

## 标志

| 标志 | 必需 | 默认值 | 描述 |
|------|----------|---------|-------------|
| `--to` | ✓ | — | 收件人邮箱地址 |
| `--subject` | ✓ | — | 邮件主题 |
| `--body` | ✓ | — | 邮件正文（纯文本） |
| `--dry-run` | — | — | 显示将要发送的请求而不实际执行 |

## 示例

```bash
gws gmail +send --to alice@example.com --subject 'Hello' --body 'Hi Alice!'
```

## 提示

- 自动处理 RFC 2822 格式化和 base64 编码。
- 如需 HTML 正文、附件或 CC/BCC，请使用原始 API：
- gws gmail users messages send --json '...'

> [!CAUTION]
> 这是**写入**命令 — 执行前请与用户确认。

## 参见

- [gws-shared](../gws-shared/SKILL.md) — 全局标志和认证
- [gws-gmail](../gws-gmail/SKILL.md) — 所有发送、阅读和管理邮件命令
