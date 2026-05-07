---
name: minimax-docx
description: "使用 OpenXML SDK（.NET）进行专业的 DOCX 文档创建、编辑和格式化。三条流水线：(A) 从零开始创建新文档，(B) 填写/编辑现有文档内容，(C) 应用模板格式并通过 XSD 验证门检查。当用户想要生成、修改或格式化 Word 文档时必须使用此技能——包括用户说"写报告"、"起草提案"、"制作合同"、"填写表格"、"重新格式化以匹配此模板"，或任何最终输出是 .docx 文件的任务。即使用户没有明确提到"docx"，如果任务意味着可打印/正式文档，也应使用此技能。"
version: 1.0.0
license: MIT
metadata:
  version: "1.0.0"
  category: document-processing
  author: MiniMaxAI
  sources:
    - "ECMA-376 Office Open XML File Formats"
    - "GB/T 9704-2012 Layout Standard for Official Documents"
    - "IEEE / ACM / APA / MLA / Chicago / Turabian Style Guides"
    - "Springer LNCS / Nature / HBR Document Templates"
triggers:
  - Word
  - docx
  - document
  - 文档
  - Word文档
  - 报告
  - 合同
  - 公文
  - 排版
  - 套模板
---

# minimax-docx

通过 CLI 工具或基于 OpenXML SDK（.NET）的直接 C# 脚本创建、编辑和格式化 DOCX 文档。

## 设置

**首次使用：** `bash scripts/setup.sh`（Windows 上使用 `powershell scripts/setup.ps1`，加 `--minimal` 可跳过可选依赖）。

**会话中的首次操作：** `scripts/env_check.sh`——如果显示 `NOT READY` 则不要继续。（同一会话中的后续操作可跳过。）

## 快速开始：直接使用 C#

当任务需要结构性文档操作（自定义样式、复杂表格、多节布局、页眉/页脚、目录、图片）时，直接编写 C# 而不是与 CLI 限制搏斗。使用以下脚手架：

```csharp
// 文件：scripts/dotnet/task.csx（或 Console 项目中的新 .cs）
// dotnet run --project scripts/dotnet/MiniMaxAIDocx.Cli -- run-script task.csx
#r "nuget: DocumentFormat.OpenXml, 3.2.0"

using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

using var doc = WordprocessingDocument.Create("output.docx", WordprocessingDocumentType.Document);
var mainPart = doc.AddMainDocumentPart();
mainPart.Document = new Document(new Body());

// --- 在这里编写你的逻辑 ---
// 首先阅读相关的 Samples/*.cs 文件获取已验证的模式
// 参见下面的参考部分中的 Samples/ 表格
```

**编写任何 C# 之前，先阅读相关的 `Samples/*.cs` 文件**——它们包含可编译的、SDK 版本验证过的模式，可以防止常见错误。下面的参考部分中的 Samples 表格将主题映射到文件。

## CLI 简写

所有下面的 CLI 命令使用 `$CLI` 作为以下简写：
```bash
dotnet run --project scripts/dotnet/MiniMaxAIDocx.Cli --
```

## 流水线路由

通过检查用户是否有输入的 .docx 文件来确定路由：

```
用户任务
├─ 无输入文件 → 流水线 A：创建
│   信号词："write"、"create"、"draft"、"generate"、"new"、"make a report/proposal/memo"
│   → 阅读 references/scenario_a_create.md
│
└─ 有输入 .docx
    ├─ 替换/填写/修改内容 → 流水线 B：填写-编辑
    │   信号词："fill in"、"replace"、"update"、"change text"、"add section"、"edit"
    │   → 阅读 references/scenario_b_edit_content.md
    │
    └─ 重新格式化/应用样式/模板 → 流水线 C：格式-应用
        信号词："reformat"、"apply template"、"restyle"、"match this format"、"套模板"、"排版"
        ├─ 模板仅是样式（无内容）→ C-1：覆盖（将样式应用到源文件）
        └─ 模板有结构（封面/目录/示例章节）→ C-2：基址-替换
            （以模板为基，替换示例内容为用户内容）
        → 阅读 references/scenario_c_apply_template.md
```

如果请求跨越多个流水线，按顺序运行（例如先创建后格式化应用）。

## 预处理

如需要，将 `.doc` → `.docx`：`scripts/doc_to_docx.sh input.doc output_dir/`

编辑前预览（避免读取原始 XML）：`scripts/docx_preview.sh document.docx`

分析结构以用于编辑场景：`$CLI analyze --input document.docx`

## 场景 A：创建

首先阅读 `references/scenario_a_create.md`、`references/typography_guide.md` 和 `references/design_principles.md`。从 `Samples/AestheticRecipeSamples.cs` 中选择与文档类型匹配的美学配方——不要自行发明格式值。对于 CJK，还要阅读 `references/cjk_typography.md`。

**选择你的路径：**
- **简单**（纯文本，最小格式）：使用 CLI——`$CLI create --type report --output out.docx --config content.json`
- **结构性**（自定义样式、多节、目录、图片、复杂表格）：直接编写 C#。先阅读相关的 `Samples/*.cs`。

CLI 选项：`--type`（report|letter|memo|academic）、`--title`、`--author`、`--page-size`（letter|a4|legal|a3）、`--margins`（standard|narrow|wide）、`--header`、`--footer`、`--page-numbers`、`--toc`、`--content-json`。

然后运行**验证流水线**（见下方）。

## 场景 B：编辑 / 填写

首先阅读 `references/scenario_b_edit_content.md`。预览 → 分析 → 编辑 → 验证。

**选择你的路径：**
- **简单**（文本替换，占位符填写）：使用 CLI 子命令。
- **结构性**（添加/重新组织节、修改样式、操作表格、插入图片）：直接编写 C#。先阅读 `references/openxml_element_order.md` 和相关的 `Samples/*.cs`。

可用的 CLI 编辑子命令：
- `replace-text --find "X" --replace "Y"`
- `fill-placeholders --data '{"key":"value"}'`
- `fill-table --data table.json`
- `insert-section`、`remove-section`、`update-header-footer`

```bash
$CLI edit replace-text --input in.docx --output out.docx --find "OLD" --replace "NEW"
$CLI edit fill-placeholders --input in.docx --output out.docx --data '{"name":"John"}'
```

然后运行**验证流水线**。还要运行 diff 验证最小更改：
```bash
$CLI diff --before in.docx --after out.docx
```

## 场景 C：应用模板

首先阅读 `references/scenario_c_apply_template.md`。预览并分析源文件和模板。

```bash
$CLI apply-template --input source.docx --template template.docx --output out.docx
```

对于复杂的模板操作（多模板合并、按节的页眉/页脚、样式合并），直接编写 C#——见下面的关键规则获取所需模式。

运行**验证流水线**，然后进行**硬性门检查**：
```bash
$CLI validate --input out.docx --gate-check assets/xsd/business-rules.xsd
```
门检查是**硬性要求**。通过前不要交付。如果失败：诊断、修复、重新运行。

还要 diff 验证内容保留：`$CLI diff --before source.docx --after out.docx`

## 验证流水线

每次写入操作后运行。对于场景 C，完整流水线是**强制性的**；对于 A/B 是**建议性的**（仅当操作非常简单时才可跳过）。

```bash
$CLI merge-runs --input doc.docx                                    # 1. 合并 runs
$CLI validate --input doc.docx --xsd assets/xsd/wml-subset.xsd     # 2. XSD 结构
$CLI validate --input doc.docx --business                           # 3. 业务规则
```

如果 XSD 失败，自动修复并重试：
```bash
$CLI fix-order --input doc.docx
$CLI validate --input doc.docx --xsd assets/xsd/wml-subset.xsd
```

如果 XSD 仍然失败，回退到业务规则 + 预览：
```bash
$CLI validate --input doc.docx --business
scripts/docx_preview.sh doc.docx
# 验证：字体污染=0，表格计数正确，绘图计数正确，sectPr 计数正确
```

最终预览：`scripts/docx_preview.sh doc.docx`

## 关键规则

这些规则可以防止文件损坏——OpenXML 对元素顺序要求严格。

**元素顺序**（属性始终在前）：

| 父元素 | 顺序 |
|--------|-------|
| `w:p`  | `pPr` → runs |
| `w:r`  | `rPr` → `t`/`br`/`tab` |
| `w:tbl`| `tblPr` → `tblGrid` → `tr` |
| `w:tr` | `trPr` → `tc` |
| `w:tc` | `tcPr` → `p`（至少 1 个 `<w:p/>`） |
| `w:body` | 块内容 → `sectPr`（最后一个子元素） |

**直接格式污染：** 从源文档复制内容时，内联 `rPr`（字体、颜色）和 `pPr`（边框、底纹、间距）会覆盖模板样式。始终剥离直接格式——只保留 `pStyle` 引用和 `t` 文本。也要清理表格（包括单元格内的 `pPr/rPr`）。

**修订标记：** `<w:del>` 使用 `<w:delText>`，绝不使用 `<w:t>`。`<w:ins>` 使用 `<w:t>`，绝不使用 `<w:delText>`。

**字体大小：** `w:sz` = 磅值 × 2（12pt → `sz="24"`）。边距/间距使用 DXA（1 英寸 = 1440，1cm ≈ 567）。

**标题样式必须包含 OutlineLevel：** 定义标题样式（Heading1、ThesisH1 等）时，始终在 `StyleParagraphProperties` 中包含 `new OutlineLevel { Val = N }`（H1→0，H2→1，H3→2）。没有这个，Word 会将它们视为纯样式文本——目录和导航窗格将无法工作。

**多模板合并：** 当给定多个模板文件（字体、标题、分节符）时，首先阅读 `references/scenario_c_apply_template.md` 的"多模板合并"部分。关键规则：
- 将所有模板的样式合并为一个 styles.xml。结构（节/分节符）来自分节符模板。
- 每个内容段落必须恰好出现一次——插入分节符时不要重复。
- 绝不要插入空/空白段落作为填充或分节符。输出段落数必须等于输入数。使用分节符属性（`w:sectPr` 在 `w:pPr` 内）和样式间距（`w:spacing` before/after）进行视觉分隔。
- 在每个章节标题前插入奇数页分节符，而不仅仅是第一个。即使章节有双栏内容，也必须从奇数页开始；在标题后使用第二个连续分节符来切换栏。
- 双栏章节需要三个分节符：(1) 前一段落的 pPr 中的 oddPage，(2) 章节标题的 pPr 中的 continuous+cols=2，(3) 最后正文的 pPr 中的 continuous+cols=1 以恢复。
- 为每个节复制分节符模板中的 `titlePg` 设置。摘要和目录节通常需要 `titlePg=true`。

**多节页眉/页脚：** 具有 10+ 节的模板（如中文论文）每个节有不同的页眉/页脚（罗马数字 vs 阿拉伯数字页码，每个区域不同的页眉文本）。规则：
- 使用 C-2 基址-替换：以模板为输出基址，然后替换正文内容。这会自动保留所有节、页眉、页脚和 titlePg 设置。
- 绝不要从头重新创建页眉/页脚——逐字节复制模板页眉/页脚 XML。
- 绝不要添加模板页眉 XML 中不存在的格式（边框、对齐、字体大小）。
- 非封面节必须有页眉/页脚 XML 文件（至少空页眉 + 页码页脚）。
- 参见 `references/scenario_c_apply_template.md` 的"多节页眉/页脚传输"部分。

## 参考资料

按需加载——不要一次加载全部。根据任务选择最相关的文件。

**下面的 C# 示例和设计参考是项目的知识库（"百科全书"）。** 编写 OpenXML 代码时，始终先阅读相关的示例文件——它包含可编译的、SDK 版本验证过的模式，可以防止常见错误。在做出美学决策时，阅读设计原则和配方文件——它们编码了来自权威来源（IEEE、ACM、APA、Nature 等）的经过测试的、和谐的参数集，而不是猜测。

### 场景指南（每个流水线首先阅读）

| 文件 | 时机 |
|------|------|
| `references/scenario_a_create.md` | 流水线 A：从零开始创建 |
| `references/scenario_b_edit_content.md` | 流水线 B：编辑现有内容 |
| `references/scenario_c_apply_template.md` | 流水线 C：应用模板格式 |

### C# 代码示例（可编译，详尽注释——编写代码时阅读）

| 文件 | 主题 |
|------|-------|
| `Samples/DocumentCreationSamples.cs` | 文档生命周期：创建、打开、保存、流、文档默认值、设置、属性、页面设置、多节 |
| `Samples/StyleSystemSamples.cs` | 样式：Normal/Heading 链、字符/表格/列表样式、DocDefaults、latentStyles、CJK 公文、APA 7th、导入、解决继承 |
| `Samples/CharacterFormattingSamples.cs` | RunProperties：字体、大小、粗体/斜体、所有下划线、颜色、高亮、删除线、上标/下标、大写、间距、底纹、边框、强调符号 |
| `Samples/ParagraphFormattingSamples.cs` | ParagraphProperties：对齐、缩进、行/段落间距、keep/widow、outline level、边框、制表符、编号、双向、frame |
| `Samples/TableSamples.cs` | 表格：边框、网格、单元格属性、边距、行高、标题重复、合并（H+V）、嵌套、浮动、三线表、斑马条纹 |
| `Samples/HeaderFooterSamples.cs` | 页眉/页脚：页码、"第 X 页 共 Y 页"、第一/偶/奇、logo 图片、表格布局、公文 "-X-"、按节 |
| `Samples/ImageSamples.cs` | 图片：内联、浮动、文字环绕、边框、alt 文本、在页眉/表格中、替换、SVG 回退、尺寸计算 |
| `Samples/ListAndNumberingSamples.cs` | 编号：项目符号、多级十进制、自定义符号、大纲→标题、法律、中文 一/（一）/1./(1)、重新开始/继续 |
| `Samples/FieldAndTocSamples.cs` | 字段：目录、SimpleField vs 复杂字段、DATE/PAGE/REF/SEQ/MERGEFIELD/IF/STYLEREF、目录样式 |
| `Samples/FootnoteAndCommentSamples.cs` | 脚注、尾注、批注（4 文件系统）、书签、超链接（内部+外部） |
| `Samples/TrackChangesSamples.cs` | 修订：插入（w:t）、删除（w:delText!）、格式更改、全都接受/拒绝、移动跟踪 |
| `Samples/AestheticRecipeSamples.cs` | 来自权威来源的 13 种美学配方：ModernCorporate、AcademicThesis、ExecutiveBrief、ChineseGovernment（GB/T 9704）、MinimalModern、IEEE Conference、ACM sigconf、APA 7th、MLA 9th、Chicago/Turabian、Springer LNCS、Nature、HBR——每个都有来自官方样式指南的精确值 |

注：`Samples/` 路径相对于 `scripts/dotnet/MiniMaxAIDocx.Core/`。

### Markdown 参考（需要规格或设计规则时阅读）

| 文件 | 时机 |
|------|------|
| `references/openxml_element_order.md` | XML 元素排序规则（防止损坏） |
| `references/openxml_units.md` | 单位转换：DXA、EMU、半磅、八分之一磅 |
| `references/openxml_encyclopedia_part1.md` | 详细的 C# 百科全书：文档创建、样式、字符和段落格式 |
| `references/openxml_encyclopedia_part2.md` | 详细的 C# 百科全书：页面设置、表格、页眉/页脚、节、文档属性 |
| `references/openxml_encyclopedia_part3.md` | 详细的 C# 百科全书：目录、脚注、字段、修订标记、批注、图片、数学、编号、保护 |
| `references/typography_guide.md` | 字体搭配、大小、间距、页面布局、表格设计、配色方案 |
| `references/cjk_typography.md` | CJK 字体、字号大小、RunFonts 映射、GB/T 9704 公文标准 |
| `references/cjk_university_template_guide.md` | 中国大学论文模板：数字 styleIds（1/2/3 vs Heading1）、文档区域结构（封面→摘要→目录→正文→参考文献）、字体预期、常见错误 |
| `references/design_principles.md` | **美学基础**：6 个设计原则（留白、对比/比例、接近、对齐、重复、层次）——教授为什么，而不仅仅是是什么 |
| `references/design_good_bad_examples.md` | **好与坏对比**：10 类排版错误，包含 OpenXML 值、ASCII 模拟和修复 |
| `references/track_changes_guide.md` | 修订标记深度研究 |
| `references/troubleshooting.md` | **症状驱动的修复**：13 个常见问题，按你看到的症状索引（标题错误、图片缺失、目录损坏等）——按症状搜索，找到修复方法 |
