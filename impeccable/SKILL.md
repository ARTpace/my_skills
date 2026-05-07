---
name: impeccable
description: 当用户想要设计、重新设计、塑造、评审、审计、打磨、澄清、提炼、加固、优化、适配、动画化、着色、提取或以其他方式改进前端界面时使用。涵盖网站、落地页、仪表盘、产品 UI、应用外壳、组件、表单、设置、引导流程和空状态。处理 UX 评审、视觉层次、信息架构、认知负荷、无障碍、性能、响应式行为、主题化、反模式、排版、字体、间距、布局、对齐、颜色、动效、微交互、UX 文案、错误状态、边缘情况、国际化以及可复用的设计系统或令牌。也适用于需要更大胆或更令人愉悦的平淡设计、需要更安静的花哨设计、浏览器中 UI 元素的实时迭代，或应该感觉技术上非凡的雄心勃勃的视觉效果。不适用于纯后端或非 UI 任务。
version: 3.0.5
user-invocable: true
argument-hint: "[craft|shape · audit|critique · animate|bolder|colorize|delight|layout|overdrive|quieter|typeset · adapt|clarify|distill · harden|onboard|optimize|polish · teach|document|extract|live] [target]"
license: Apache 2.0. Based on Anthropic's frontend-design skill. See NOTICE.md for attribution.
---

设计和迭代生产级前端界面。真实可运行的代码，坚定的设计选择，卓越的工艺。

## 设置（必须执行）

在进行任何设计工作或文件编辑之前，必须通过这些关卡。跳过它们会产生忽略项目的通用输出。

| 关卡 | 必需检查 | 失败时 |
|---|---|---|
| 上下文 | 通过 `node .trae-cn/skills/impeccable/scripts/load-context.mjs` 获取 PRODUCT.md / DESIGN.md 加载结果。 | 继续前先运行加载器。 |
| 产品 | PRODUCT.md 存在且非空或占位符（`[TODO]` 标记，<200 字符）。 | 运行 `/impeccable teach`，刷新上下文，然后继续。永远不要仅从用户的原始提示词合成 PRODUCT.md。 |
| 命令 | 使用子命令时已加载匹配的命令参考。 | 继续前先加载参考。 |
| 工艺 | `/impeccable craft` 有用户确认的 shape 简报用于此任务。`teach` / PRODUCT.md 永远不算 shape。 | 运行 `/impeccable shape` 并等待明确的简报确认。 |
| 图像 | 所需的视觉探测/模型已生成或有理由跳过。 | 在编码前解决 `shape.md` 或 `craft.md` 中的图像生成关卡。 |
| 变更 | 以上所有活跃关卡均通过。 | 暂不编辑项目文件。 |

Codex 风格的智能体在编辑文件前必须声明：

```text
IMPECCABLE_PREFLIGHT: context=pass product=pass command_reference=pass shape=pass|not_required image_gate=pass|skipped:<reason> mutation=open
```

对于 `/impeccable craft`，`shape=pass` 仅在用户单独回复批准 shape 设计简报后有效，或用户在请求中提供了已确认的简报。不要在编写 PRODUCT.md、总结假设或自行起草未确认的简报后将 `shape=pass` 标记为通过。

其他框架在能暴露此状态时应遵循相同的检查清单。

### 1. 上下文收集

项目根目录下的两个文件，不区分大小写：

- **PRODUCT.md** — 必需。用户、品牌、调性、反面参考、战略原则。
- **DESIGN.md** — 可选，强烈推荐。颜色、排版、层级、组件。

一次调用加载两者：

```bash
node .trae-cn/skills/impeccable/scripts/load-context.mjs
```

消费完整的 JSON 输出。永远不要通过 `head`、`tail`、`grep` 或 `jq` 管道处理。

如果输出已在本会话的对话历史中，不要重新运行。需要重新加载的例外情况：你刚运行了 `/impeccable teach` 或 `/impeccable document`（它们会重写文件），或用户手动编辑了其中一个。

`/impeccable live` 已通过 `live.mjs` 预热上下文 —— 如果你已在本会话中运行了 `live.mjs`，不要再运行 `load-context.mjs`。

如果 PRODUCT.md 缺失、为空或是占位符（`[TODO]` 标记，<200 字符）：运行 `/impeccable teach`，然后用新上下文恢复用户的原始任务。如果原始任务是 `/impeccable craft`，在任何实现工作之前恢复到 `/impeccable shape`。

如果 DESIGN.md 缺失：每会话提醒一次（*"运行 `/impeccable document` 以获得更符合品牌的输出"*），然后继续。

### 2. 注册

每个设计任务要么是**品牌**（营销、落地页、活动、长内容、作品集 —— 设计就是产品）要么是**产品**（应用 UI、管理后台、仪表盘、工具 —— 设计服务于产品）。

在设计前识别。优先级：(1) 任务本身的线索（"落地页" vs "仪表盘"）；(2) 聚焦的表面（正在处理的页面、文件或路由）；(3) PRODUCT.md 中的 `register` 字段。第一个匹配生效。

如果 PRODUCT.md 缺少 `register` 字段（旧版），从其"用户"和"产品目的"部分推断一次，然后在本会话中缓存推断值。建议用户运行 `/impeccable teach` 显式添加该字段。

加载匹配的参考：[reference/brand.md](reference/brand.md) 或 [reference/product.md](reference/product.md)。以下共享设计法则适用于两者。

## 共享设计法则

适用于每个设计，两种注册类型均适用。将实现复杂度与美学愿景匹配 —— 极繁主义需要精心设计的代码，极简主义需要精准。创造性解读。在不同项目间变化；永远不要收敛于相同的选择。模型有能力做出非凡的工作 —— 不要保留。

### 颜色

- 使用 OKLCH。当亮度接近 0 或 100 时降低色度 —— 极端值下的高色度看起来刺眼。
- 永远不要使用 `#000` 或 `#fff`。将每种中性色调向品牌色相（色度 0.005–0.01 就足够）。
- 在选择颜色之前先选择**颜色策略**。承诺轴上的四个步骤：
  - **克制** — 着色中性色 + 一个强调色 ≤10%。产品默认；品牌极简主义。
  - **投入** — 一种饱和色承载 30–60% 的表面。身份驱动页面的品牌默认。
  - **全调色板** — 3–4 个命名角色，每个都有意使用。品牌活动；产品数据可视化。
  - **沉浸** — 表面就是颜色。品牌英雄页、活动页面。
- "一个强调色 ≤10%"规则仅适用于克制策略。投入/全调色板/沉浸有意超出。不要条件反射地将每个设计都压缩为克制策略。

### 主题

深色 vs. 浅色永远不是默认。不是因为"工具看起来酷所以深色"。不是因为"为了安全所以浅色"。

在选择之前，写一句物理场景：谁在使用，在哪里，在什么环境光下，在什么情绪中。如果这句话不能强制答案，说明不够具体 —— 添加细节直到能强制答案。

"可观测性仪表盘"不能强制答案。"SRE 在凌晨 2 点昏暗房间里 27 英寸显示器上查看事件严重性"可以。运行场景，而不是类别。

### 排版

- 正文行长度限制在 65–75ch。
- 通过比例 + 粗细对比建立层次（步骤间 ≥1.25 比例）。避免扁平比例。

### 布局

- 变化间距以创造节奏。处处相同的内边距是单调的。
- 卡片是懒惰的答案。只在它们真正是最佳交互方式时使用。嵌套卡片永远是错的。
- 不要把一切都包在容器里。大多数东西不需要容器。

### 动效

- 不要动画化 CSS 布局属性。
- 使用指数曲线缓出（ease-out-quart / quint / expo）。不要弹跳，不要弹性。

### 绝对禁止

匹配并拒绝。如果你即将写出以下任何内容，用不同的结构重写该元素。

- **侧边条纹边框。** `border-left` 或 `border-right` 大于 1px 作为卡片、列表项、标注或警告上的彩色强调。永远不是有意的。用完整边框、背景着色、前置数字/图标或什么都不用来重写。
- **渐变文字。** `background-clip: text` 结合渐变背景。装饰性的，永远没有意义。使用单一纯色。通过粗细或大小强调。
- **玻璃态作为默认。** 模糊和玻璃卡片用于装饰。罕见且有目的，否则不用。
- **英雄指标模板。** 大数字、小标签、支持统计、渐变强调。SaaS 陈词滥调。
- **相同卡片网格。** 相同大小的卡片，图标 + 标题 + 文字，无休止重复。
- **模态框作为第一想法。** 模态框通常是懒惰。先穷尽内联/渐进式替代方案。

### 文案

- 每个词都要有价值。不要重述标题，不要重复标题的引言。
- **不要破折号。** 使用逗号、冒号、分号、句号或括号。也不要用 `--`。

### AI 味道测试

如果有人看到这个界面能毫无疑问地说"AI 做的"，那就失败了。跨注册类型的失败是上述绝对禁止。注册类型特定的失败在各参考中。

**类别反射检查。** 如果有人能从类别名称猜出主题和调色板 —— "可观测性 → 深蓝"，"医疗 → 白+青"，"金融 → 深蓝+金"，"加密货币 → 黑底霓虹" —— 这是训练数据反射。重新构思场景句子和颜色策略，直到答案不再从领域显而易见。

## 命令

| 命令 | 类别 | 描述 | 参考 |
|---|---|---|---|
| `craft [feature]` | 构建 | 塑造，然后端到端构建功能 | [reference/craft.md](reference/craft.md) |
| `shape [feature]` | 构建 | 在编码前规划 UX/UI | [reference/shape.md](reference/shape.md) |
| `teach` | 构建 | 设置 PRODUCT.md 和 DESIGN.md 上下文 | [reference/teach.md](reference/teach.md) |
| `document` | 构建 | 从现有项目代码生成 DESIGN.md | [reference/document.md](reference/document.md) |
| `extract [target]` | 构建 | 提取可复用令牌和组件到设计系统 | [reference/extract.md](reference/extract.md) |
| `critique [target]` | 评估 | 带启发式评分的 UX 设计评审 | [reference/critique.md](reference/critique.md) |
| `audit [target]` | 评估 | 技术质量检查（无障碍、性能、响应式） | [reference/audit.md](reference/audit.md) |
| `polish [target]` | 精炼 | 发布前的最终质量检查 | [reference/polish.md](reference/polish.md) |
| `bolder [target]` | 精炼 | 放大安全或平淡的设计 | [reference/bolder.md](reference/bolder.md) |
| `quieter [target]` | 精炼 | 调低激进或过度刺激的设计 | [reference/quieter.md](reference/quieter.md) |
| `distill [target]` | 精炼 | 剥离至本质，移除复杂性 | [reference/distill.md](reference/distill.md) |
| `harden [target]` | 精炼 | 生产就绪：错误、国际化、边缘情况 | [reference/harden.md](reference/harden.md) |
| `onboard [target]` | 精炼 | 设计首次运行流程、空状态、激活 | [reference/onboard.md](reference/onboard.md) |
| `animate [target]` | 增强 | 添加有目的的动画和动效 | [reference/animate.md](reference/animate.md) |
| `colorize [target]` | 增强 | 为单色 UI 添加战略性颜色 | [reference/colorize.md](reference/colorize.md) |
| `typeset [target]` | 增强 | 改进排版层次和字体 | [reference/typeset.md](reference/typeset.md) |
| `layout [target]` | 增强 | 修复间距、节奏和视觉层次 | [reference/layout.md](reference/layout.md) |
| `delight [target]` | 增强 | 添加个性和令人难忘的细节 | [reference/delight.md](reference/delight.md) |
| `overdrive [target]` | 增强 | 突破常规极限 | [reference/overdrive.md](reference/overdrive.md) |
| `clarify [target]` | 修复 | 改进 UX 文案、标签和错误消息 | [reference/clarify.md](reference/clarify.md) |
| `adapt [target]` | 修复 | 适配不同设备和屏幕尺寸 | [reference/adapt.md](reference/adapt.md) |
| `optimize [target]` | 修复 | 诊断和修复 UI 性能 | [reference/optimize.md](reference/optimize.md) |
| `live` | 迭代 | 视觉变体模式：在浏览器中选择元素，生成替代方案 | [reference/live.md](reference/live.md) |

外加两个管理命令 —— `pin <command>` 和 `unpin <command>`，详见下文。

### 路由规则

1. **无参数** — 将上表渲染为面向用户的命令菜单，按类别分组。询问他们想做什么。
2. **第一个词匹配命令** — 加载其参考文件并遵循其指示。命令名之后的所有内容都是目标。
3. **第一个词不匹配** — 通用设计调用。应用设置步骤、共享设计法则和已加载的注册参考，使用完整参数作为上下文。

设置（上下文收集、注册）此时已加载；子命令不会重新调用 `/impeccable`。

如果第一个词是 `craft`，设置仍然先运行，但 [reference/craft.md](reference/craft.md) 拥有流程的其余部分。如果设置调用 `teach` 作为阻塞项，完成 teach，刷新上下文，然后恢复原始命令和目标。

## Pin / Unpin

**Pin** 创建独立快捷方式，使 `/<command>` 直接调用 `/impeccable <command>`。**Unpin** 移除它。脚本写入项目中存在的每个框架目录。

```bash
node .trae-cn/skills/impeccable/scripts/pin.mjs <pin|unpin> <command>
```

有效的 `<command>` 是上表中的任何命令。简洁地报告脚本结果 —— 成功时确认新快捷方式，错误时将 stderr 逐字转发。
