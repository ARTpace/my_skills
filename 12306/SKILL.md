---
name: "12306"
description: 查询中国铁路 12306 的列车时刻、余票和站点信息。当用户询问国内火车票/高铁票/火车票、时刻表或余票时使用。
version: 1.0.2
allowed-tools: Bash,Read
metadata:
  openclaw:
    emoji: "🚄"
    requires:
      bins:
        - node
---

# 12306 火车票查询

查询中国铁路 12306 的列车时刻和余票。

## 查询车票

```bash
node {baseDir}/scripts/query.mjs <出发> <到达> [选项]
```

- HTML 模式（默认）：写入文件，将路径输出到 stdout
- Markdown 模式（`-f md`）：将表格输出到 stdout

### 示例

```bash
# 北京到上海的所有列车（默认查询今天）
node {baseDir}/scripts/query.mjs 北京 上海

# Markdown 表格输出（到 stdout，适合聊天）
node {baseDir}/scripts/query.mjs 北京 上海 -t G -f md

# 上午出发、最多2小时、二等座有余票
node {baseDir}/scripts/query.mjs 上海 杭州 -t G --depart 06:00-12:00 --max-duration 1h --seat ze

# 只显示下午6点前到达且可预订的车次
node {baseDir}/scripts/query.mjs 深圳 长沙 --available --arrive -18:00

# 自定义输出路径
node {baseDir}/scripts/query.mjs 广州 武汉 -o /tmp/tickets.html

# JSON 输出（到 stdout）
node {baseDir}/scripts/query.mjs 广州 武汉 --json
```

### 选项

- `-d, --date <YYYY-MM-DD>`：出行日期（默认：今天）
- `-t, --type <G|D|Z|T|K>`：筛选车次类型（可组合，如 `GD`）
- `--depart <HH:MM-HH:MM>`：出发时间范围（如 `08:00-12:00`，`18:00-`）
- `--arrive <HH:MM-HH:MM>`：到达时间范围（如 `-18:00`，`14:00-20:00`）
- `--max-duration <duration>`：最长行程时间（如 `2h`、`90m`、`1h30m`）
- `--available`：只显示可预订的车次
- `--seat <types>`：只显示有指定座位余票的车次（逗号分隔：`swz,zy,ze,rw,dw,yw,yz,wz`）
- `-f, --format <html|md>`：输出格式 — `html`（默认，保存文件）或 `md`（markdown 表格到 stdout）
- `-o, --output <path>`：输出文件路径，仅 html 模式（默认：`{baseDir}/data/<出发>-<到达>-<日期>.html`）
- `--json`：将原始 JSON 输出到 stdout

### 输出列

| 列 | 含义 |
|------|------|
| 商务/特等 | 商务座/特等座 (swz) |
| 一等座 | 一等座 (zy) |
| 二等座 | 二等座 (ze) |
| 软卧/动卧 | 软卧/动卧 (rw/dw) |
| 硬卧 | 硬卧 (yw) |
| 硬座 | 硬座 (yz) |
| 无座 | 无座 (wz) |

数值 = 余票数量，`有` = 有票（数量未知），`—` = 不适用

## 站点查询

```bash
node {baseDir}/scripts/stations.mjs 杭州
node {baseDir}/scripts/stations.mjs 香港西九龙
```

## 注意事项

- 数据直接来自 12306 官方 API（无需密钥）
- 站点数据缓存在 `{baseDir}/data/stations.json`，有效期 7 天
- 支持城市名（解析为主站）或精确站名
- 支持所有车次类型：G（高铁）、D（动车）、Z（直达）、T（特快）、K（快速）
