---
name: openai-whisper-api
description: "通过 OpenAI 音频转录 API（Whisper）将音频转录为文字。"
---

# OpenAI Whisper API (curl)

通过 OpenAI 的 `/v1/audio/transcriptions` 端点转录音频文件。

## 快速开始

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

默认值：
- 模型：`whisper-1`
- 输出：`<input>.txt`

## 常用标志

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model whisper-1 --out /tmp/transcript.txt
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language en
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "Speaker names: Peter, Daniel"
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

## API 密钥

设置 `OPENAI_API_KEY` 环境变量。
