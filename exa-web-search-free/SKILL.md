---
id: D.Va/exa-web-search-free
owner_id: D.Va
name: exa-web-search-free
description: "通过 Exa MCP 进行免费 AI 搜索。网页搜索新闻/信息，代码搜索 GitHub/StackOverflow 文档/示例，公司研究获取商业情报。无需 API 密钥。"
version: 1.0.0
icon: "🔍"
author: D.Va
metadata:
  clawdbot:
    emoji: "🔍"
    requires:
      bins:
        - mcporter
---

# Exa Web Search（免费）

用于网页、代码和公司研究的神经搜索。无需 API 密钥。

## 设置

验证 mcporter 已配置：
```bash
mcporter list exa
```

如果未列出：
```bash
mcporter config add exa https://mcp.exa.ai/mcp
```

## 核心工具

### web_search_exa
搜索网页获取最新信息、新闻或事实。

```bash
mcporter call 'exa.web_search_exa(query: "latest AI news 2026", numResults: 5)'
```

**参数：**
- `query` - 搜索查询
- `numResults`（可选，默认：8）
- `type`（可选）- `"auto"`、`"fast"` 或 `"deep"`

### get_code_context_exa
从 GitHub、Stack Overflow 查找代码示例和文档。

```bash
mcporter call 'exa.get_code_context_exa(query: "React hooks examples", tokensNum: 3000)'
```

**参数：**
- `query` - 代码/API 搜索查询
- `tokensNum`（可选，默认：5000）- 范围：1000-50000

### company_research_exa
研究公司获取商业信息和新闻。

```bash
mcporter call 'exa.company_research_exa(companyName: "Anthropic", numResults: 3)'
```

**参数：**
- `companyName` - 公司名称
- `numResults`（可选，默认：5）

## 高级工具（可选）

通过更新配置 URL 可获取六个额外工具：
- `web_search_advanced_exa` - 域名/日期筛选
- `deep_search_exa` - 查询扩展
- `crawling_exa` - 完整页面提取
- `people_search_exa` - 专业个人资料
- `deep_researcher_start/check` - AI 研究代理

**启用所有工具：**
```bash
mcporter config add exa-full "https://mcp.exa.ai/mcp?tools=web_search_exa,web_search_advanced_exa,get_code_context_exa,deep_search_exa,crawling_exa,company_research_exa,people_search_exa,deep_researcher_start,deep_researcher_check"

# 然后使用：
mcporter call 'exa-full.deep_search_exa(query: "AI safety research")'
```

## 提示

- 网页：使用 `type: "fast"` 快速查找，`"deep"` 深入搜索
- 代码：较低的 `tokensNum`（1000-2000）用于聚焦，较高（5000+）用于全面
- 更多模式参见 [examples.md](references/examples.md)

## 资源

- [GitHub](https://github.com/exa-labs/exa-mcp-server)
- [npm](https://www.npmjs.com/package/exa-mcp-server)
- [文档](https://exa.ai/docs)
