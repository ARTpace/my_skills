---
name: find-skills
description: "帮助用户发现和安装智能体技能。当用户提出「如何做 X」、「查找某个技能」、「有没有能做……的技能」等问题，或表示希望扩展功能时使用。当用户正在寻找可能作为可安装技能存在的功能时，应使用此技能。"
---

# 查找技能

此技能帮助你从开放的智能体技能生态系统中发现和安装技能。

## 何时使用此技能

当用户执行以下操作时使用此技能：

- 问"如何做 X"，其中 X 可能是具有现有技能的常见任务
- 说"为 X 查找技能"或"是否有 X 的技能"
- 问"你能做 X 吗"，其中 X 是专业功能
- 表达扩展智能体功能的兴趣
- 想要搜索工具、模板或工作流程
- 提到他们希望在特定领域（设计、测试、部署等）获得帮助

## 什么是 Skills CLI？

Skills CLI (`npx skills`) 是开放智能体技能生态系统的包管理器。技能是扩展智能体功能的模块化包，具有专业知识、工作流程和工具。

**关键命令：**

- `npx skills find [query]` - 交互式或按关键词搜索技能
- `npx skills add <package>` - 从 GitHub 或其他来源安装技能
- `npx skills check` - 检查技能更新
- `npx skills update` - 更新所有已安装的技能

**浏览技能：** https://skills.sh/

## 如何帮助用户查找技能

### 第 1 步：了解他们需要什么

当用户请求帮助时，识别：

1. 领域（例如，React、测试、设计、部署）
2. 特定任务（例如，编写测试、创建动画、审查 PR）
3. 这是否是足够常见的任务，可能存在技能

### 第 2 步：搜索技能

使用相关查询运行查找命令：

```bash
npx skills find [query]
```

例如：

- 用户问"如何使我的 React 应用更快？" → `npx skills find react performance`
- 用户问"你能帮我审查 PR 吗？" → `npx skills find pr review`
- 用户问"我需要创建变更日志" → `npx skills find changelog`

该命令将返回如下结果：

```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

如果未找到相关结果，尝试 ClawHub 作为回退（参见下面的"ClawHub 回退"部分）。

### 第 3 步：向用户展示选项

找到相关技能时，向用户展示：

1. 技能名称及其功能
2. 他们可以运行的安装命令
3. 在 skills.sh 上了解更多信息的链接

示例响应：

```
我找到了可能有帮助的技能！"vercel-react-best-practices" 技能提供
来自 Vercel Engineering 的 React 和 Next.js 性能优化指南。

安装：
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

了解更多：https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 第 4 步：检测当前客户端

安装前，通过检查 `__CFBundleIdentifier` 环境变量检测正在运行的客户端：

```bash
echo $__CFBundleIdentifier
```

根据结果确定目标技能目录：

| `__CFBundleIdentifier` 包含 | 客户端    | 目标技能目录        |
| ------------------------------- | --------- | ------------------------ |
