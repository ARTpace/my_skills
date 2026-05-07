---
name: openai-image-gen
description: "通过 OpenAI Images API 批量生成图片。支持随机提示词采样和 `index.html` 图库展示。"
---

# OpenAI Image Gen

Generate a handful of "random but structured" prompts and render them via OpenAI Images API.

## Setup

- Needs env: `OPENAI_API_KEY`

## Run

```bash
python3 {baseDir}/scripts/gen.py
```

Useful flags:
```bash
python3 {baseDir}/scripts/gen.py --count 16 --model gpt-image-1.5
python3 {baseDir}/scripts/gen.py --prompt "ultra-detailed studio photo of a lobster astronaut" --count 4
python3 {baseDir}/scripts/gen.py --size 1536x1024 --quality high --out-dir ./out/images
```

## Output

- `*.png` images
- `prompts.json` (prompt > file mapping)
- `index.html` (thumbnail gallery)
