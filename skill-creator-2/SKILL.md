---
name: skill-creator
description: "技能创建指南。当用户希望创建新技能或更新现有技能，以扩展 CodeBuddy 的专业知识、工作流程或工具集成能力时使用。"
---

# 技能创建器

本技能提供创建有效技能的指导。

## 关于技能

技能是模块化的、自包含的包，通过提供专业工作流程和工具来扩展能力。

### 技能提供什么

1. 专业工作流程 - 特定领域的多步骤程序
2. 工具集成 - 使用特定文件格式或 API 的说明
3. 领域专业知识 - 公司特定的知识、模式、业务逻辑
4. 捆绑资源 - 脚本、参考资料和复杂任务的资源

## 核心原则

### 简洁是关键

上下文窗口是公共资源。只添加模型尚不拥有的上下文。

### 技能的结构

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML 前置元数据 (name + description)
│   └── Markdown 说明
└── 捆绑资源 (可选)
    ├── scripts/       - 可执行代码
    ├── references/    - 上下文文档
    └── assets/        - 输出中使用的文件
```

### 渐进式披露

1. **元数据 (name + description)** - 始终在上下文中
2. **SKILL.md 正文** - 技能触发时
3. **捆绑资源** - 按需

## 技能创建流程

1. 用具体示例理解技能
2. 规划可重用的技能内容（脚本、参考资料、资源）
3. 初始化技能（运行 init_skill.py）
4. 编辑技能（实现资源并编写 SKILL.md）
5. 打包技能（运行 package_skill.py）
6. 根据实际使用迭代

### 第3步：初始化

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

### 第5步：打包

```bash
scripts/package_skill.py <path/to/skill-folder>
```

## 参考资料

- `references/workflows.md` - 顺序工作流程和条件逻辑
- `references/output-patterns.md` - 模板和示例模式
