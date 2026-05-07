---
name: skill-finder
description: "全功能智能体技能管理：搜索 35+ 技能、本地安装、收藏 favorites、从源更新。在查找技能、安装新技能或管理技能集合时使用。"
license: CC BY-NC-SA 4.0
metadata:
  author: yamapan (https://github.com/aktsmm)
---

# 技能查找器

全功能智能体技能管理工具。

## 何时使用

- **查找技能**、**搜索技能**、**安装技能**、**スキル検索**
- 查找特定任务或领域的技能
- 在本地查找和安装技能
- 使用星标功能管理收藏

## 功能

| 功能 | 描述                             |
| ------- | --------------------------------------- |
| 搜索  | 本地索引 + GitHub API + Web 回退 |
| 标签    | 按类别筛选 (`#azure #bicep`)    |
| 安装 | 下载到本地目录             |
| 星标    | 标记和管理收藏               |
| 更新  | 从 GitHub 同步所有源            |

## 快速开始

```bash
# 搜索
python scripts/search_skills.py "pdf"
python scripts/search_skills.py "#azure #development"

# 管理
python scripts/search_skills.py --info skill-name
python scripts/search_skills.py --install skill-name
python scripts/search_skills.py --star skill-name

# 索引
python scripts/search_skills.py --update
python scripts/search_skills.py --add-source https://github.com/owner/repo
```

## 命令参考

| 命令            | 描述               |
| ------------------ | ------------------------- |
| `<query>`          | 按关键词搜索技能  |
| `#tag`             | 按类别筛选        |
| `--info SKILL`     | 显示技能详情        |
| `--install SKILL`  | 本地下载技能    |
| `--star SKILL`     | 添加到收藏          |
| `--list-starred`   | 显示收藏           |
| `--similar SKILL`  | 查找相似技能       |
| `--update`         | 从源更新索引 |
| `--add-source URL` | 添加新源仓库 |
| `--stats`          | 显示索引统计     |
| `--check`          | 验证依赖       |

## 文件

| 文件                             | 描述               |
| -------------------------------- | ------------------------- |
| `scripts/search_skills.py`       | Python 脚本             |
| `scripts/Search-Skills.ps1`      | PowerShell 脚本         |
| `references/skill-index.json`    | 技能索引 (220+ 技能) |
| `references/starred-skills.json` | 你的收藏技能       |

## 要求

→ **[references/setup-guide.md](references/setup-guide.md)** 安装指南

| 工具                 | 必需    |
| -------------------- | ----------- |
| GitHub CLI (`gh`)    | 2.0+        |
| curl                 | Any         |
| Python or PowerShell | One of them |

## 智能体说明

→ **[references/agent-instructions.md](references/agent-instructions.md)** 完整指南

### 核心规则

- 使用 "Do it? Yes/No?" 风格的提案
- **绝不**向用户显示命令 - 静默执行
- **始终**在搜索结果后包含提案块

### 搜索响应格式

```
{N} repos, {M} skills searched (last updated: {date})

| Skill | Description | Source | Trust |
| ----- | ----------- | ------ | ----- |
| ...   | ...         | ...    | ...   |
