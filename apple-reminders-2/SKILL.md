---
name: apple-reminders
description: "通过 macOS 上的 `remindctl` CLI 管理 Apple 提醒事项（列出、添加、编辑、完成、删除）。支持列表、日期过滤和 JSON/纯文本输出。"
---

# Apple Reminders CLI (remindctl)

使用 `remindctl` 直接从终端管理 Apple 提醒事项。支持列表筛选、基于日期的视图和脚本输出。

设置
- 安装（Homebrew）：`brew install steipete/tap/remindctl`
- 从源码：`pnpm install && pnpm build`（二进制文件在 `./bin/remindctl`）
- 仅限 macOS；提示时授予提醒事项权限。

权限
- 检查状态：`remindctl status`
- 请求访问：`remindctl authorize`

查看提醒事项
- 默认（今天）：`remindctl`
- 今天：`remindctl today`
- 明天：`remindctl tomorrow`
- 本周：`remindctl week`
- 逾期：`remindctl overdue`
- 即将到来：`remindctl upcoming`
- 已完成：`remindctl completed`
- 全部：`remindctl all`
- 特定日期：`remindctl 2026-01-04`

管理列表
- 列出所有列表：`remindctl list`
- 显示列表：`remindctl list 工作`
- 创建列表：`remindctl list 项目 --create`
- 重命名列表：`remindctl list 工作 --rename 办公室`
- 删除列表：`remindctl list 工作 --delete`

创建提醒事项
- 快速添加：`remindctl add "买牛奶"`
- 带列表 + 到期日：`remindctl add --title "给妈妈打电话" --list 个人 --due 明天`

编辑提醒事项
- 编辑标题/到期日：`remindctl edit 1 --title "新标题" --due 2026-01-04`

完成提醒事项
- 按 id 完成：`remindctl complete 1 2 3`

删除提醒事项
- 按 id 删除：`remindctl delete 4A83 --force`

输出格式
- JSON（脚本）：`remindctl today --json`
- 纯文本 TSV：`remindctl today --plain`
- 仅计数：`remindctl today --quiet`

日期格式
`--due` 和日期筛选器接受：
- `today`、`tomorrow`、`yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

注意
- 仅限 macOS。
- 如果访问被拒绝，在系统设置 > 隐私与安全性 > 提醒事项中启用 Terminal/remindctl。
- 如果通过 SSH 运行，在运行命令的 Mac 上授予访问权限。
