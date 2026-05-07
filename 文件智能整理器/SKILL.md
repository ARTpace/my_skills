---
id: custom/file-organizer
owner_id: kal
name: 文件智能整理器
description: 按类型、日期、大小自动整理文件的PowerShell工具
version: 1.0.0
icon: "📁"
author: 卡尔
metadata:
  clawdbot:
    emoji: "📁"
    requires:
      bins:
        - powershell
    os:
      - win32
---

# 文件智能整理器

自动将文件按规则分类到文件夹。

## 功能概述
- 按文件类型整理（如文档、图片、视频）
- 按修改日期整理（年/月）
- 按文件大小整理
- 统计文件夹内容
- 撤销上次整理（安全机制）

## 快速开始

```powershell
# 导入模块
Import-Module .\src\FileOrganizer.psm1

# 按类型整理下载文件夹
Sort-FilesByType -Path "C:\Users\Administrator\Downloads"

# 按日期整理
Sort-FilesByDate -Path "C:\Users\Administrator\Documents"

# 查看统计
Get-FileStats -Path "C:\Users\Administrator\Downloads"
```

## 函数列表

### Sort-FilesByType
按文件扩展名整理到子文件夹。

参数:
- `-Path` : 要整理的文件夹路径
- `-WhatIf` : 仅预览，不实际移动
- `-LogPath` : 记录操作日志

### Sort-FilesByDate
按修改年份/月份整理。

参数:
- `-Path` : 文件夹路径
- `-GroupBy` : 'Year' 或 'Month'
- `-WhatIf` : 预览模式

### Sort-FilesBySize
按文件大小整理。

参数:
- `-Path` : 文件夹路径
- `-Thresholds` : 自定义阈值 (默认: 1MB, 100MB, 1GB)
- `-WhatIf` : 预览模式

### Get-FileStats
统计文件夹内容。

参数:
- `-Path` : 文件夹路径
- `-Recurse` : 包含子文件夹

### Undo-LastSort
撤销上次整理操作。

参数:
- `-Path` : 要恢复的文件夹

## 依赖
- PowerShell 5.1+
- Windows操作系统

## 安装
```bash
claw skill install custom/file-organizer
```
