---
name: apple-notes
description: "通过 macOS 上的 `memo` CLI 管理 Apple 备忘录（创建、查看、编辑、删除、搜索、移动和导出笔记）。当用户要求 CodeBuddy Code 添加笔记、列出笔记、搜索笔记或管理笔记文件夹时使用。"
---

# Apple Notes CLI

使用 `memo notes` 直接从终端管理 Apple 备忘录。创建、查看、编辑、删除、搜索笔记，在文件夹间移动笔记，并导出为 HTML/Markdown。

设置
- 安装（Homebrew）：`brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- 手动（pip）：`pip install .`（克隆仓库后）
- 仅限 macOS；如果提示，授予 Notes.app 自动化访问权限。

查看笔记
- 列出所有笔记：`memo notes`
- 按文件夹筛选：`memo notes -f "文件夹名称"`
- 搜索笔记（模糊）：`memo notes -s "查询"`

创建笔记
- 添加新笔记：`memo notes -a`
  - 打开交互式编辑器撰写笔记。
- 快速添加标题：`memo notes -a "笔记标题"`

编辑笔记
- 编辑现有笔记：`memo notes -e`
  - 交互式选择要编辑的笔记。

删除笔记
- 删除笔记：`memo notes -d`
  - 交互式选择要删除的笔记。

移动笔记
- 移动笔记到文件夹：`memo notes -m`
  - 交互式选择笔记和目标文件夹。

导出笔记
- 导出为 HTML/Markdown：`memo notes -ex`
  - 导出选定笔记；使用 Mistune 进行 markdown 处理。

限制
- 无法编辑包含图片或附件的笔记。
- 交互式提示可能需要终端访问。

注意
- 仅限 macOS。
- 需要 Apple Notes.app 可访问。
- 用于自动化，在系统设置 > 隐私与安全性 > 自动化中授予权限。
