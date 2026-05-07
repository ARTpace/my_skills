---
name: newsletter-curation
description: "新闻通讯策划，包含内容来源、编辑结构和订阅者增长策略。涵盖期刊格式、链接汇总、评论风格和发送节奏。用于：电子邮件新闻通讯、链接汇总、每周摘要、策划内容、创作者新闻通讯。触发词：newsletter、email newsletter、newsletter curation、weekly digest、link roundup、curated newsletter、newsletter writing、newsletter format、subscriber growth、newsletter strategy、content curation、newsletter template"
allowed-tools: Bash(infsh *)
---

# 新闻通讯策划

通过 [inference.sh](https://inference.sh) CLI 创建和策划高质量新闻通讯。

## 快速开始

> 需要 inference.sh CLI (`infsh`)。获取安装说明：`npx skills add inference-sh/skills@agent-tools`

```bash
infsh login

# 查找要策划的内容
infsh app run tavily/search-assistant --input '{
  "query": "2024年本周最重要的 AI 发展"
}'

# 生成新闻通讯头部
infsh app run infsh/html-to-image --input '{
  "html": "<div style=\"width:600px;height:200px;background:linear-gradient(135deg,#1e293b,#334155);display:flex;align-items:center;padding:40px;font-family:system-ui;color:white\"><div><h1 style=\"font-size:32px;margin:0;font-weight:800\">每周信号</h1><p style=\"font-size:16px;opacity:0.7;margin-top:8px\">第47期 — 2025年1月15日</p></div></div>"
}'
```


## 新闻通讯格式

### 1. 链接汇总

5-15个策划链接，每个链接附带1-3句评论。

```markdown
## 本周精选

### [文章标题](url)
一到三句话解释为什么这很重要以及读者
会从中获得什么。添加你的观点 — 不要只是描述。

### [文章标题](url)
你的评论在这里。价值在于你的策划和视角，
不仅仅是链接。
```

### 2. 深度分析 + 链接

一篇深度分析（300-500字）+ 5-8个策划链接。

```markdown
## 大事件

[本周最重要主题的300-500字分析]

## 也值得一读

- **[标题](url)** — 一句话评论
- **[标题](url)** — 一句话评论
...
```

### 3. 原创散文

一篇重点突出的文章（500-1,000字），有明确的论点。

```markdown
## [散文标题]

[你的原创分析、观点或见解]

## 我在读什么

- [标题](url) — 简短说明
- [标题](url) — 简短说明
```

### 4. 问答/访谈

与专家或从业者的对话特写。

### 5. 数据/趋势

数字、图表和你所在领域的趋势分析。

## 期刊结构

### 模板

```markdown
# [新闻通讯名称] — 第#[N]期

## 👋 你好

[2-3句个人介绍 — 你在想什么，
本期涵盖什么，为什么现在很重要]

## 🔥 大事件
