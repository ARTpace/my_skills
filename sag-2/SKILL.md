---
name: sag
description: "基于 ElevenLabs 的文字转语音工具，提供类似 macOS say 命令的使用体验。"
---

# sag

使用 `sag` 进行 ElevenLabs TTS 本地播放。

API 密钥（必需）
- `ELEVENLABS_API_KEY`（首选）
- `SAG_API_KEY` 也被 CLI 支持

快速开始
- `sag "你好"`
- `sag speak -v "Roger" "你好"`
- `sag voices`
- `sag prompting`（模型特定提示）

模型说明
- 默认：`eleven_v3`（富有表现力）
- 稳定：`eleven_multilingual_v2`
- 快速：`eleven_flash_v2_5`

发音 + 表达规则
- 首次修复：重新拼写（例如 "key-note"），添加连字符，调整大小写。
- 数字/单位/URL：`--normalize auto`（或如果损害名称则使用 `off`）。
- 语言偏见：`--lang en|de|fr|...` 引导规范化。
- v3：不支持 SSML `<break>`；使用 `[pause]`、`[short pause]`、`[long pause]`。

v3 音频标签（放在行首）
- `[whispers]`、`[shouts]`、`[sings]`
- `[laughs]`、`[starts laughing]`、`[sighs]`、`[exhales]`
- `[sarcastic]`、`[curious]`、`[excited]`、`[crying]`、`[mischievously]`
- 示例：`sag "[whispers] 保密。 [short pause] 好吗？"`

语音默认值
- `ELEVENLABS_VOICE_ID` 或 `SAG_VOICE_ID`

长输出前确认语音 + 说话人。
