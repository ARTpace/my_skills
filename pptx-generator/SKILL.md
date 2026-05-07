---
name: pptx-generator
description: "生成、编辑和读取 PowerPoint 演示文稿。使用 PptxGenJS 从零创建（封面、目录、内容、分隔页、总结页），通过 XML 工作流编辑现有 PPTX，或使用 markitdown 提取文本。触发词：PPT、PPTX、PowerPoint、演示文稿、幻灯片、slide、deck。"
version: 1.0.2
license: MIT
metadata:
  version: "1.0"
  category: productivity
  sources:
    - https://gitbrent.github.io/PptxGenJS/
    - https://github.com/microsoft/markitdown
---

# PPTX 演示文稿生成器与编辑器

## 概述

本技能处理所有 PowerPoint 任务：读取/分析现有演示文稿、通过 XML 操作编辑基于模板的文稿、使用 PptxGenJS 从零创建演示文稿。它包含完整的设计系统（调色板、字体、样式配方）和每种幻灯片类型的详细指南。

## 快速参考

| 任务 | 方法 |
|------|------|
| 读取/分析内容 | `python -m markitdown presentation.pptx` |
| 编辑或从模板创建 | 参见 [编辑演示文稿](references/editing.md) |
| 从零创建 | 参见下方的 [从零创建工作流](#从零创建工作流) |

| 项目 | 值 |
|------|------|
| **尺寸** | 10" x 5.625" (LAYOUT_16x9) |
| **颜色** | 6 位十六进制，不带 #（如 `"FF0000"`） |
| **英文字体** | Arial（默认）或经批准的替代字体 |
| **中文字体** | Microsoft YaHei |
| **页码徽章位置** | x: 9.3", y: 5.1" |
| **主题键** | `primary`、`secondary`、`accent`、`light`、`bg` |
| **形状** | RECTANGLE、OVAL、LINE、ROUNDED_RECTANGLE |
| **图表** | BAR、LINE、PIE、DOUGHNUT、SCATTER、BUBBLE、RADAR |

## 参考文件

| 文件 | 内容 |
|------|------|
| [slide-types.md](references/slide-types.md) | 5 种幻灯片页面类型（封面、目录、分隔页、内容、总结）+ 额外布局模式 |
| [design-system.md](references/design-system.md) | 调色板、字体参考、样式配方（Sharp/Soft/Rounded/Pill）、排版与间距 |
| [editing.md](references/editing.md) | 基于模板的编辑工作流、XML 操作、格式规则、常见陷阱 |
| [pitfalls.md](references/pitfalls.md) | QA 流程、常见错误、关键 PptxGenJS 陷阱 |
| [pptxgenjs.md](references/pptxgenjs.md) | 完整的 PptxGenJS API 参考 |

---

## 读取内容

```bash
# 文本提取
python -m markitdown presentation.pptx
```

---

## 从零创建 — 工作流

**在没有模板或参考演示文稿时使用。**

### 步骤 1：研究与需求

搜索了解用户需求 — 主题、受众、目的、基调、内容深度。

### 步骤 2：选择调色板与字体

使用[调色板参考](references/design-system.md#color-palette-reference)选择匹配主题和受众的调色板。使用[字体参考](references/design-system.md#font-reference)选择字体搭配。

### 步骤 3：选择设计风格

使用[样式配方](references/design-system.md#style-recipes)选择匹配演示文稿基调的视觉风格（Sharp、Soft、Rounded 或 Pill）。

### 步骤 4：规划幻灯片大纲

将**每张幻灯片**精确定义为[5 种页面类型](references/slide-types.md)之一。为每张幻灯片规划内容和布局。确保视觉多样性 —— 不要在多张幻灯片上重复相同的布局。

### 步骤 5：生成幻灯片 JS 文件

在 `slides/` 目录中为每张幻灯片创建一个 JS 文件。每个文件必须导出一个同步的 `createSlide(pres, theme)` 函数。遵循[幻灯片输出格式](#幻灯片输出格式)和 [slide-types.md](references/slide-types.md) 中的类型特定指南。如有子智能体可用，同时生成最多 5 张幻灯片。

**告知每个子智能体：**
1. 文件命名：`slides/slide-01.js`、`slides/slide-02.js` 等
2. 图片放在：`slides/imgs/`
3. 最终 PPTX 放在：`slides/output/`
4. 尺寸：10" x 5.625" (LAYOUT_16x9)
5. 字体：中文 = Microsoft YaHei，英文 = Arial（或经批准的替代字体）
6. 颜色：6 位十六进制，不带 #（如 `"FF0000"`）
7. 必须使用主题对象契约（参见[主题对象契约](#主题对象契约)）
8. 必须遵循 [PptxGenJS API 参考](references/pptxgenjs.md)

### 步骤 6：编译为最终 PPTX

创建 `slides/compile.js` 来组合所有幻灯片模块：

```javascript
// slides/compile.js
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

const theme = {
  primary: "22223b",    // 深色，用于背景/文字
  secondary: "4a4e69",  // 次要强调色
  accent: "9a8c98",     // 高亮颜色
  light: "c9ada7",      // 浅色强调
  bg: "f2e9e4"          // 背景颜色
};

for (let i = 1; i <= 12; i++) {  // 根据需要调整数量
  const num = String(i).padStart(2, '0');
  const slideModule = require(`./slide-${num}.js`);
  slideModule.createSlide(pres, theme);
}

pres.writeFile({ fileName: './output/presentation.pptx' });
```

运行：`cd slides && node compile.js`

### 步骤 7：QA（必须）

参见 [QA 流程](references/pitfalls.md#qa-process)。

### 输出结构

```
slides/
├── slide-01.js          # 幻灯片模块
├── slide-02.js
├── ...
├── imgs/                # 幻灯片中使用的图片
└── output/              # 最终产物
    └── presentation.pptx
```

---

## 幻灯片输出格式

每张幻灯片是一个**完整、可运行的 JS 文件**：

```javascript
// slide-01.js
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'cover',
  index: 1,
  title: '演示文稿标题'
};

// 必须是同步函数（不是 async）
function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText(slideConfig.title, {
    x: 0.5, y: 2, w: 9, h: 1.2,
    fontSize: 48, fontFace: "Arial",
    color: theme.primary, bold: true, align: "center"
  });

  return slide;
}

// 独立预览 - 使用幻灯片特定的文件名
if (require.main === module) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  const theme = {
    primary: "22223b",
    secondary: "4a4e69",
    accent: "9a8c98",
    light: "c9ada7",
    bg: "f2e9e4"
  };
  createSlide(pres, theme);
  pres.writeFile({ fileName: "slide-01-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
```

---

## 主题对象契约（强制）

编译脚本传递一个具有以下**确切键**的主题对象：

| 键 | 用途 | 示例 |
|-----|---------|------|
| `theme.primary` | 最深颜色，用于标题 | `"22223b"` |
| `theme.secondary` | 深强调色，用于正文 | `"4a4e69"` |
| `theme.accent` | 中间调强调色 | `"9a8c98"` |
| `theme.light` | 浅色强调 | `"c9ada7"` |
| `theme.bg` | 背景颜色 | `"f2e9e4"` |

**永远不要使用其他键名**，如 `background`、`text`、`muted`、`darkest`、`lightest`。

---

## 页码徽章（必须）

除**封面页**外，所有幻灯片**必须**在右下角包含页码徽章。

- **位置**：x: 9.3", y: 5.1"
- 只显示当前编号（如 `3` 或 `03`），不要显示 "3/12"
- 使用调色板颜色，保持低调

### 圆形徽章（默认）

```javascript
slide.addShape(pres.shapes.OVAL, {
  x: 9.3, y: 5.1, w: 0.4, h: 0.4,
  fill: { color: theme.accent }
});
slide.addText("3", {
  x: 9.3, y: 5.1, w: 0.4, h: 0.4,
  fontSize: 12, fontFace: "Arial",
  color: "FFFFFF", bold: true,
  align: "center", valign: "middle"
});
```

### 药丸徽章

```javascript
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 9.1, y: 5.15, w: 0.6, h: 0.35,
  fill: { color: theme.accent },
  rectRadius: 0.15
});
slide.addText("03", {
  x: 9.1, y: 5.15, w: 0.6, h: 0.35,
  fontSize: 11, fontFace: "Arial",
  color: "FFFFFF", bold: true,
  align: "center", valign: "middle"
});
```

---

## 依赖

- `pip install "markitdown[pptx]"` — 文本提取
- `npm install -g pptxgenjs` — 从零创建
- `npm install -g react-icons react react-dom sharp` — 图标（可选）
