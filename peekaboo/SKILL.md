---
name: peekaboo
description: "使用 Peekaboo CLI 截取和自动化 macOS 界面操作。"
---

# Peekaboo

Peekaboo 是一个完整的 macOS UI 自动化 CLI：捕获/检查屏幕、定位 UI 元素、驱动输入、管理应用/窗口/菜单。

## 功能

核心：`bridge`、`capture`、`clean`、`config`、`image`、`learn`、`list`、`permissions`、`run`、`sleep`、`tools`
交互：`click`、`drag`、`hotkey`、`move`、`paste`、`press`、`scroll`、`swipe`、`type`
系统：`app`、`clipboard`、`dialog`、`dock`、`menu`、`menubar`、`open`、`space`、`window`
视觉：`see`

## 快速开始
```bash
peekaboo permissions
peekaboo list apps --json
peekaboo see --annotate --path /tmp/peekaboo-see.png
peekaboo click --on B1
peekaboo type "Hello" --return
```

## 定位参数
- 应用/窗口：`--app`、`--pid`、`--window-title`、`--window-id`、`--window-index`
- 快照：`--snapshot`（来自 `see` 的 ID）
- 元素/坐标：`--on`/`--id`、`--coords x,y`

## 示例
```bash
peekaboo see --app Safari --annotate --path /tmp/see.png
peekaboo click --on B3 --app Safari
peekaboo type "user@example.com" --app Safari
peekaboo image --mode screen --screen-index 0 --retina --path /tmp/screen.png
peekaboo app launch "Safari" --open https://example.com
peekaboo menu click --app Safari --item "New Window"
peekaboo hotkey --keys "cmd,shift,t"
```

注意
- 需要屏幕录制 + 辅助功能权限。
- 点击前使用 `peekaboo see --annotate` 识别目标。
