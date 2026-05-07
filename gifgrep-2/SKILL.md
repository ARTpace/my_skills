---
name: gifgrep
description: "通过 CLI/TUI 搜索 GIF 提供商、下载结果并提取静态帧/缩略图。"
---

# gifgrep

使用 `gifgrep` 搜索 GIF 提供商（Tenor/Giphy）、在 TUI 中浏览、下载结果并提取静态图或图集。

GIF-Grab（gifgrep 工作流程）
- 搜索 > 预览 > 下载 > 提取（静态/图集）用于快速查看和分享。

快速开始
- `gifgrep cats --max 5`
- `gifgrep cats --format url | head -n 5`
- `gifgrep search --json cats | jq '.[0].url'`
- `gifgrep tui "office handshake"`
- `gifgrep cats --download --max 1 --format url`

TUI + 预览
- TUI: `gifgrep tui "query"`
- CLI 静态预览：`--thumbs`（仅 Kitty/Ghostty；静态帧）

下载 + 显示
- `--download` 保存到 `~/Downloads`
- `--reveal` 在 Finder 中显示最后下载的内容

静态图 + 图集
- `gifgrep still ./clip.gif --at 1.5s -o still.png`
- `gifgrep sheet ./clip.gif --frames 9 --cols 3 -o sheet.png`
- 图集 = 采样帧的单个 PNG 网格（非常适合快速查看、文档、PR、聊天）。
- 调整：`--frames`（数量）、`--cols`（网格宽度）、`--padding`（间距）。

提供商
- `--source auto|tenor|giphy`
- `--source giphy` 需要 `GIPHY_API_KEY`
- `TENOR_API_KEY` 可选（如果未设置则使用 Tenor 演示密钥）

输出
- `--json` 打印结果数组（`id`、`title`、`url`、`preview_url`、`tags`、`width`、`height`）
- `--format` 用于管道友好的字段（例如 `url`）

环境调整
- `GIFGREP_SOFTWARE_ANIM=1` 强制软件动画
- `GIFGREP_CELL_ASPECT=0.5` 调整预览几何
