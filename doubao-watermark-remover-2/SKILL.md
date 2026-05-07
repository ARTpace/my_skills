---
name: doubao-watermark-remover
description: 从图片中移除可见的豆包（Doubao）AI 水印。当用户要求移除豆包水印、清理豆包生成的图片，或处理带有"豆包AI生成"水印的图片时使用。
---

# 豆包水印移除器

## 依赖

- Python 3.9+
- Pillow（使用 `pip install -r requirements.txt` 安装）

## 快速开始

1) 在 scripts 文件夹中安装依赖：
   - `cd doubao-watermark-remover/scripts && pip install -r requirements.txt`

2) 运行 CLI：
   - `python remove_watermark.py <输入图片> <输出图片>`

## CLI 用法

- 参数：
  - `input-image`：带豆包水印的图片路径
  - `output-image`：清理后图片的路径（格式从扩展名推断）

示例：

```
python remove_watermark.py ./in.png ./out.png
```

## 此技能提供什么

- `scripts/remove_watermark.py`：CLI 入口点和核心算法。
- `scripts/capture_alpha_map.py`：捕获豆包水印 alpha 贴图的工具。
- `references/algorithm.md`：数学、检测规则和使用指南。

## 工作流程

1) 首次使用：使用 `capture_alpha_map.py` 生成 alpha 贴图
2) 使用 `remove_watermark.py` 进行批处理。

## 捕获 Alpha 贴图（首次使用必需）

由于豆包水印图案可能有所不同，你需要先捕获 alpha 贴图：

1. 生成纯黑色图片 (0,0,0) 并让豆包添加水印
2. 运行捕获工具：
   ```
   python capture_alpha_map.py <带水印的黑色图片.png> <宽度> <高度>
   ```
   尺寸选项：140x35（小图）或 180x40（大图）

3. 工具会将 alpha 贴图保存到 `assets/` 文件夹

## 注意

- 豆包水印"豆包AI生成"出现在**右下角**
- 脚本使用 Pillow 进行图片 IO 和逐像素编辑
- 输出格式从输出文件扩展名推断
