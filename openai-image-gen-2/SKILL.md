---
name: openai-image-gen
description: "通过 OpenAI Images API 批量生成图片。支持随机提示词采样和 `index.html` 图库展示。"
---

# OpenAI 图片生成

生成一些"随机但有结构"的提示词，并通过 OpenAI Images API 渲染它们。

## 设置

- 需要环境变量: `OPENAI_API_KEY`

## 运行

```bash
python3 {baseDir}/scripts/gen.py
```

有用的标志:
```bash
python3 {baseDir}/scripts/gen.py --count 16 --model gpt-image-1.5
python3 {baseDir}/scripts/gen.py --prompt "超详细的龙虾宇航员工作室照片" --count 4
python3 {baseDir}/scripts/gen.py --size 1536x1024 --quality high --out-dir ./out/images
```

## 输出

- `*.png` 图片
- `prompts.json` (提示词 > 文件映射)
- `index.html` (缩略图画廊)
