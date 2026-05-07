---
name: skill-manager
description: 技能管理工具 - 列出、查看、翻译和管理已安装的 AI 技能。支持批量查看技能描述、生成技能目录、翻译技能文档。Use when user wants to list skills, view skill descriptions, translate skill files, or manage their skill collection.
---

# Skill Manager - 技能管理工具

一个用于管理和翻译 AI 技能的工具技能。

## 功能

1. **列出所有技能** - 显示已安装的所有技能及其描述
2. **查看技能详情** - 读取并显示指定技能的完整内容
3. **翻译技能** - 将技能文档翻译成中文（保留技术术语）
4. **生成技能目录** - 创建所有技能的摘要文档

## 使用方法

### 1. 列出所有技能

```
列出所有技能
显示我的技能列表
有哪些技能可用
```

### 2. 查看特定技能

```
查看 skill-name 技能的详情
读取 add-uint-support 技能的内容
显示 browser-use 技能的用法
```

### 3. 翻译技能

```
翻译 add-uint-support 技能为中文
将 browser-use 技能翻译成中文
翻译 skill-name 技能
```

### 4. 生成技能目录

```
生成技能目录
创建技能清单
列出所有技能及其功能
```

## 翻译规则

翻译技能时遵循以下规则：

1. **保留不翻译的部分：**
   - `name` 字段（技能标识符）
   - 代码示例（C++, Python, JavaScript 等）
   - 技术术语（如 `AT_DISPATCH_V2`, `kUInt16`）
   - 宏名称、类型名称、API 名称

2. **需要翻译的部分：**
   - `description` 字段
   - 说明性文字
   - 使用指南
   - 示例说明

## 工作流程

当用户请求管理技能时：

1. 确定用户的具体需求（列出/查看/翻译/生成目录）
2. 扫描技能目录获取所有 SKILL.md 文件
3. 根据需求执行相应操作
4. 对于翻译任务：
   - 读取原始 SKILL.md
   - 解析 frontmatter 和正文
   - 翻译 description 和说明文字
   - 保留代码和技术术语
   - 生成新的 SKILL.md 文件

## 示例

### 示例 1: 列出所有技能

```
用户: 列出所有技能

助手: 
已安装 85 个技能：

1. **add-uint-support** - 为 PyTorch 算子添加无符号整数类型支持
2. **browser-use** - 通过 browser-use CLI 自动化浏览器操作
3. **canvas-design** - 创建精美的视觉艺术作品（PNG/PDF）
4. **docx** - 全面的 Word 文档处理工具
...
```

### 示例 2: 翻译技能

```
用户: 翻译 browser-use 技能

助手:
正在翻译 browser-use 技能...

翻译完成！主要变更：
- description: "AI-powered browser automation..." → "AI 驱动的浏览器自动化工具..."
- 正文已翻译为中文
- 保留了所有代码示例和技术术语
```

## 注意事项

1. 翻译前建议备份原始文件
2. 某些技能可能已经是中文（如 腾讯会议、小红书 等）
3. 翻译后技能的功能不变，只是文档语言变为中文
4. 建议保留原始英文技能名以便识别

## 技能目录位置

```
c:\Users\ARTpace\.skills-manager\skills\
├── skill-name/
│   └── SKILL.md
├── browser-use/
│   └── SKILL.md
└── ...
```

## 文件格式

SKILL.md 文件结构：

```yaml
---
name: skill-name                    # 不翻译
description: Skill description      # 翻译
---

# Title                              # 翻译

Content...                          # 翻译

```code
# Code examples - 不翻译
```
```
