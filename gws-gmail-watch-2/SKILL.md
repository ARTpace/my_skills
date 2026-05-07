---
name: gws-gmail-watch
version: 1.0.0
description: "Gmail：监听新邮件并以 NDJSON 流式输出。"
metadata:
  openclaw:
    category: "productivity"
    requires:
      bins: ["gws"]
    cliHelp: "gws gmail +watch --help"
---

# gmail +watch

> **前置条件：** 阅读 `../gws-shared/SKILL.md` 了解认证、全局标志和安全规则。如果缺失，运行 `gws generate-skills` 创建。

监听新邮件并以 NDJSON 流式输出

## 用法

```bash
gws gmail +watch
```

## 标志

| 标志 | 必需 | 默认值 | 描述 |
|------|----------|---------|-------------|
| `--project` | — | — | Pub/Sub 资源的 GCP 项目 ID |
| `--subscription` | — | — | 已有的 Pub/Sub 订阅名称（跳过设置） |
| `--topic` | — | — | 已授予 Gmail 推送权限的已有 Pub/Sub 主题 |
| `--label-ids` | — | — | 逗号分隔的 Gmail 标签 ID 筛选（如 INBOX,UNREAD） |
| `--max-messages` | — | 10 | 每次拉取的最大消息数 |
| `--poll-interval` | — | 5 | 拉取间隔秒数 |
| `--msg-format` | — | full | Gmail 消息格式：full, metadata, minimal, raw |
| `--once` | — | — | 拉取一次后退出 |
| `--cleanup` | — | — | 退出时删除创建的 Pub/Sub 资源 |
| `--output-dir` | — | — | 将每条消息写入此目录中的单独 JSON 文件 |

## 示例

```bash
gws gmail +watch --project my-gcp-project
gws gmail +watch --project my-project --label-ids INBOX --once
gws gmail +watch --subscription projects/p/subscriptions/my-sub
gws gmail +watch --project my-project --cleanup --output-dir ./emails
```

## 提示

- Gmail watch 7 天后过期 — 重新运行以续期。
- 不使用 --cleanup 时，Pub/Sub 资源会保留以便重连。
- 按 Ctrl-C 优雅停止。

## 参见

- [gws-shared](../gws-shared/SKILL.md) — 全局标志和认证
- [gws-gmail](../gws-gmail/SKILL.md) — 所有发送、阅读和管理邮件命令
