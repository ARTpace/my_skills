---
name: gws-gmail
version: 1.0.0
description: "Gmail：发送、阅读和管理邮件。"
metadata:
  openclaw:
    category: "productivity"
    requires:
      bins: ["gws"]
    cliHelp: "gws gmail --help"
---

# gmail (v1)

> **前置条件：** 阅读 `../gws-shared/SKILL.md` 了解认证、全局标志和安全规则。如果缺失，运行 `gws generate-skills` 创建。

```bash
gws gmail <resource> <method> [flags]
```

## 辅助命令

| 命令 | 描述 |
|---------|-------------|
| [`+send`](../gws-gmail-send/SKILL.md) | 发送邮件 |
| [`+triage`](../gws-gmail-triage/SKILL.md) | 显示未读收件箱摘要（发件人、主题、日期） |
| [`+reply`](../gws-gmail-reply/SKILL.md) | 回复消息（自动处理线程） |
| [`+reply-all`](../gws-gmail-reply-all/SKILL.md) | 回复全部（自动处理线程） |
| [`+forward`](../gws-gmail-forward/SKILL.md) | 转发消息给新收件人 |
| [`+watch`](../gws-gmail-watch/SKILL.md) | 监听新邮件并以 NDJSON 流式输出 |

## API 资源

### users

  - `getProfile` — 获取当前用户的 Gmail 个人资料。
  - `stop` — 停止接收指定用户邮箱的推送通知。
  - `watch` — 设置或更新指定用户邮箱的推送通知监听。
  - `drafts` — 草稿资源操作
  - `history` — 历史记录资源操作
  - `labels` — 标签资源操作
  - `messages` — 消息资源操作
  - `settings` — 设置资源操作
  - `threads` — 线程资源操作

## 发现命令

调用任何 API 方法前，先检查：

```bash
# 浏览资源和方法
gws gmail --help

# 检查方法的必需参数、类型和默认值
gws schema gmail.<resource>.<method>
```

使用 `gws schema` 输出来构建 `--params` 和 `--json` 标志。
