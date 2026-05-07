---
name: nano-banana-pro
description: "使用 Nano Banana Pro（Gemini 3 Pro Image）生成/编辑图片。支持图片创建和修改请求。支持文本生图和图片编辑；1K/2K/4K 分辨率；使用 --input-image 进行图片编辑。"
---

# Nano Banana Pro 图片生成与编辑

使用 Google 的 Nano Banana Pro API（Gemini 3 Pro Image）生成新图片或编辑现有图片。

## 用法

使用绝对路径运行脚本（不要先 cd 到技能目录）：

**生成新图片：**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "你的图片描述" --filename "output-name.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**编辑现有图片：**
```bash
uv run {baseDir}/scripts/generate_image.py --prompt "编辑指令" --filename "output-name.png" --input-image "path/to/input.png" [--resolution 1K|2K|4K] [--api-key KEY]
```

**重要：** 始终从用户当前工作目录运行，以便图片保存在用户工作的地方。

## 默认工作流（草稿 > 迭代 > 最终）

- 草稿（1K）：快速反馈循环
- 迭代：小幅调整提示词；每次运行使用新文件名
- 最终（4K）：仅在提示词锁定后使用

## 分辨率选项

- **1K**（默认）- 约 1024px 分辨率
- **2K** - 约 2048px 分辨率
- **4K** - 约 4096px 分辨率

## API 密钥

1. `--api-key` 参数
2. `GEMINI_API_KEY` 环境变量

## 图片编辑

使用 `--input-image` 参数指定图片路径。提示词应包含编辑指令。

## 提示词处理

**生成：** 将用户的图片描述原样传递给 `--prompt`。
**编辑：** 在 `--prompt` 中传递编辑指令。

## 输出

- 将 PNG 保存到当前目录
- 脚本输出生成图片的完整路径
- **不要读回图片** - 只需告知用户保存路径
