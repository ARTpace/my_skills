---
name: weather
description: "获取当前天气和天气预报（无需 API 密钥）。"
---

# 天气

两个免费服务，无需 API 密钥。

## wttr.in（主要）

```bash
curl -s "wttr.in/London?format=3"
curl -s "wttr.in/London?format=%l:+%c+%t+%h+%w"
curl -s "wttr.in/London?T"
```

格式代码：`%c` 天气状况，`%t` 温度，`%h` 湿度，`%w` 风速，`%l` 位置

提示：
- URL 编码空格：`wttr.in/New+York`
- 机场代码：`wttr.in/JFK`
- 单位：`?m`（公制）`?u`（美制）
- 仅今天：`?1`，仅当前：`?0`

## Open-Meteo（备用，JSON）

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.12&current_weather=true"
```
