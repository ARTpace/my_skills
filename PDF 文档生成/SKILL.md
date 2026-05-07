---
name: minimax-pdf
description: "当 PDF 的视觉质量和设计标识很重要时使用此技能。创建（从零生成）："制作 PDF"、"生成报告"、"写提案"、"创建简历"、"漂亮的 PDF"、"专业文档"、"封面"、"精美的 PDF"、"可交付客户的文档"。填写（填写表单字段）："填写表格"、"填写此 PDF"、"填写表单字段"、"将值写入 PDF"、"此 PDF 有哪些字段"。重新格式化（将设计应用到现有文档）："重新格式化此文档"、"应用我们的样式"、"将 Markdown/文本转换为 PDF"、"让这份文档看起来更好"、"重新样式化此 PDF"。此技能使用基于 Token 的设计系统：颜色、排版和间距源自文档类型，并贯穿每一页。输出可直接打印。当外观重要时优先使用此技能，而不仅仅是在需要任何 PDF 输出时。"
version: 1.0.0
license: MIT
metadata:
  version: "1.0"
  category: document-generation
---

# minimax-pdf

三个任务，一个技能。

## 在执行任何 CREATE 或 REFORMAT 工作之前阅读 `design/design.md`。

---

## 路由表

| 用户意图 | 路由 | 使用的脚本 |
|---|---|---|
| 从零开始生成新的 PDF | **CREATE** | `palette.py` → `cover.py` → `render_cover.js` → `render_body.py` → `merge.py` |
| 填写/填写现有 PDF 中的表单字段 | **FILL** | `fill_inspect.py` → `fill_write.py` |
| 重新格式化/重新样式化现有文档 | **REFORMAT** | `reformat_parse.py` → 然后执行完整的 CREATE 流水线 |

**规则：** 当在 CREATE 和 REFORMAT 之间犹豫时，问用户是否有现有文档可以开始。如果有 → REFORMAT。如果没有 → CREATE。

---

## 路由 A：创建

完整流水线——内容 → 设计 Token → 封面 → 正文 → 合并的 PDF。

```bash
bash scripts/make.sh run \
  --title "Q3 Strategy Review" --type proposal \
  --author "Strategy Team" --date "October 2025" \
  --accent "#2D5F8A" \
  --content content.json --out report.pdf
```

**文档类型：** `report` · `proposal` · `resume` · `portfolio` · `academic` · `general` · `minimal` · `stripe` · `diagonal` · `frame` · `editorial` · `magazine` · `darkroom` · `terminal` · `poster`

| 类型 | 封面模式 | 视觉标识 |
|---|---|---|
| `report` | `fullbleed` | 深色背景、点阵网格、Playfair Display |
| `proposal` | `split` | 左侧面板 + 右侧几何图形、Syne |
| `resume` | `typographic` | 超大首字母、DM Serif Display |
| `portfolio` | `atmospheric` | 近黑色、径向发光、Fraunces |
| `academic` | `typographic` | 浅色背景、古典衬线、EB Garamond |
| `general` | `fullbleed` | 深石板色、Outfit |
| `minimal` | `minimal` | 白色 + 单个 8px 强调条、Cormorant Garamond |
| `stripe` | `stripe` | 3 条粗水平色带、Barlow Condensed |
| `diagonal` | `diagonal` | SVG 斜切、深浅两半、Montserrat |
| `frame` | `frame` | 内嵌边框、角落装饰、Cormorant |
| `editorial` | `editorial` | 幽灵字母、全大写标题、Bebas Neue |
| `magazine` | `magazine` | 暖奶油色背景、居中堆叠、Hero 图片、Playfair Display |
| `darkroom` | `darkroom` | 海军蓝背景、居中堆叠、灰度图片、Playfair Display |
| `terminal` | `terminal` | 近黑色、网格线、等宽字体、霓虹绿 |
| `poster` | `poster` | 白色背景、粗侧边栏、超大标题、Barlow Condensed |

封面额外内容（通过 `--abstract`、`--cover-image` 注入 Token）：
- `--abstract "text"` — 封面上的摘要文本块（magazine/darkroom）
- `--cover-image "url"` — Hero 图片 URL/路径（magazine、darkroom、poster）

**颜色覆盖——始终根据文档内容选择：**
- `--accent "#HEX"` — 覆盖强调颜色；`accent_lt` 通过向白色变淡自动派生
- `--cover-bg "#HEX"` — 覆盖封面背景颜色

**强调颜色选择指南：**

你对强调颜色有创意决定权。从文档的语义上下文——标题、行业、目的、受众——中选择，而不是从通用的"安全"选择中选择。强调颜色出现在分节规则、标注条、表格标题和封面上：它承载着文档的视觉标识。

| 上下文 | 建议的强调颜色范围 |
|---|---|
| 法律/合规/金融 | 深海军蓝 `#1C3A5E`、炭灰色 `#2E3440`、石板色 `#3D4C5E` |
| 医疗/健康 | 青绿色 `#2A6B5A`、冷绿色 `#3A7D6A` |
| 技术/工程 | 钢蓝色 `#2D5F8A`、靛蓝色 `#3D4F8A` |
| 环境/可持续 | 森林绿 `#2E5E3A`、橄榄色 `#4A5E2A` |
| 创意/艺术/文化 | 勃艮第红 `#6B2A35`、李子紫 `#5A2A6B`、赤陶色 `#8A3A2A` |
| 学术/研究 | 深青色 `#2A5A6B`、图书馆蓝 `#2A4A6B` |
| 企业/中性 | 石板色 `#3D4A5A`、石墨色 `#444C56` |
| 奢侈/高端 | 暖黑色 `#1A1208`、深青铜色 `#4A3820` |

**规则：** 选择一个有思想的设计师会为这份特定文档选择的颜色——而不是类型的默认值。柔和、低饱和度的色调效果最好；避免鲜艳的原色。当犹豫时，选择更深和更中性的颜色。

**content.json 块类型：**

| 块 | 用途 | 关键字段 |
|---|---|---|
| `h1` | 章节标题 + 强调规则 | `text` |
| `h2` | 子章节标题 | `text` |
| `h3` | 子子章节（粗体） | `text` |
| `body` | 两端对齐段落；支持 `<b>` `<i>` 标记 | `text` |
| `bullet` | 无序列表项（• 前缀） | `text` |
| `numbered` | 有序列表项——计数器在非编号块上自动重置 | `text` |
| `callout` | 带强调色左边栏的高亮洞察框 | `text` |
| `table` | 数据表——强调色标题、交错行底纹 | `headers`、`rows`、`col_widths`?、`caption`? |
| `image` | 嵌入图片，缩放到列宽 | `path`/`src`、`caption`? |
| `figure` | 带自动编号"Figure N:"标题的图片 | `path`/`src`、`caption`? |
| `code` | 带强调色左边框的等宽代码块 | `text`、`language`? |
| `math` | 显示数学——通过 matplotlib mathtext 的 LaTeX 语法 | `text`、`label`?、`caption`? |
| `chart` | 通过 matplotlib 渲染的柱状/折线/饼图 | `chart_type`、`labels`、`datasets`、`title`?、`x_label`?、`y_label`?、`caption`?、`figure`? |
| `flowchart` | 通过 matplotlib 的带节点+边的流程图 | `nodes`、`edges`、`caption`?、`figure`? |
| `bibliography` | 带悬挂缩进的编号参考文献列表 | `items` [{id, text}]、`title`? |
| `divider` | 强调色全宽规则 | — |
| `caption` | 小型弱化标签 | `text` |
| `pagebreak` | 强制新页面 | — |
| `spacer` | 垂直空白 | `pt`（默认 12） |

**chart / flowchart 模式：**
```json
{"type":"chart","chart_type":"bar","labels":["Q1","Q2","Q3","Q4"],
 "datasets":[{"label":"Revenue","values":[120,145,132,178]}],"caption":"Q results"}

{"type":"flowchart",
 "nodes":[{"id":"s","label":"Start","shape":"oval"},
          {"id":"p","label":"Process","shape":"rect"},
          {"id":"d","label":"Valid?","shape":"diamond"},
          {"id":"e","label":"End","shape":"oval"}],
 "edges":[{"from":"s","to":"p"},{"from":"p","to":"d"},
          {"from":"d","to":"e","label":"Yes"},{"from":"d","to":"p","label":"No"}]}

{"type":"bibliography","items":[
  {"id":"1","text":"Author (Year). Title. Publisher."}]}
```

---

## 路由 B：填写

在不改变布局或设计的情况下填写现有 PDF 中的表单字段。

```bash
# 步骤 1：检查
python3 scripts/fill_inspect.py --input form.pdf

# 步骤 2：填写
python3 scripts/fill_write.py --input form.pdf --out filled.pdf \
  --values '{"FirstName": "Jane", "Agree": "true", "Country": "US"}'
```

| 字段类型 | 值格式 |
|---|---|
| `text` | 任何字符串 |
| `checkbox` | `"true"` 或 `"false"` |
| `dropdown` | 必须与检查输出中的选择值匹配 |
| `radio` | 必须与单选值匹配（通常以 `/` 开头） |

始终首先运行 `fill_inspect.py` 获取确切的字段名称。

---

## 路由 C：重新格式化

解析现有文档 → content.json → CREATE 流水线。

```bash
bash scripts/make.sh reformat \
  --input source.md --title "My Report" --type report --out output.pdf
```

**支持的输入格式：** `.md` `.txt` `.pdf` `.json`

---

## 环境

```bash
bash scripts/make.sh check   # 验证所有依赖
bash scripts/make.sh fix     # 自动安装缺失的依赖
bash scripts/make.sh demo    # 构建一个示例 PDF
```

| 工具 | 用于 | 安装 |
|---|---|---|
| Python 3.9+ | 所有 `.py` 脚本 | 系统 |
| `reportlab` | `render_body.py` | `pip install reportlab` |
| `pypdf` | 填写、合并、重新格式化 | `pip install pypdf` |
| Node.js 18+ | `render_cover.js` | 系统 |
| `playwright` + Chromium | `render_cover.js` | `npm install -g playwright && npx playwright install chromium` |
