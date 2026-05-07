---
name: openai-whisper
description: "使用 Whisper CLI 进行本地语音转文字（无需 API 密钥）。"
---

# Whisper (CLI)

使用 `whisper` 在本地转录音频。

快速开始
- `whisper /path/audio.mp3 --model medium --output_format txt --output_dir .`
- `whisper /path/audio.m4a --task translate --output_format srt`

注意
- 模型在首次运行时下载到 `~/.cache/whisper`。
- 此安装的 `--model` 默认为 `turbo`。
- 使用较小模型以获得速度，较大模型以获得准确性。
