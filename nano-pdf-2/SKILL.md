---
name: nano-pdf
description: "使用 nano-pdf CLI 通过自然语言指令编辑 PDF 文件。"
---

# nano-pdf

使用 `nano-pdf` 通过自然语言指令对 PDF 的特定页面应用编辑。

## 快速开始

```bash
nano-pdf edit deck.pdf 1 "将标题改为'Q3 结果'并修复副标题中的错别字"
```

注意：
- 页码根据工具版本/配置可能是 0 基或 1 基；如果结果看起来差一页，用另一种重试。
- 发送前始终对输出 PDF 进行合理性检查。
