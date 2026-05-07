---
name: unity-plugin
version: 1.6.1
description: "通过 OpenClaw Unity 插件控制 Unity 编辑器。用于 Unity 游戏开发任务，包括场景管理、GameObject/组件操作、调试、输入模拟和播放模式控制。触发于 Unity 相关请求，如检查场景、创建对象、截图、测试游戏或控制编辑器。"
homepage: https://github.com/TomLeeLive/openclaw-unity-skill
author: Tom Jaejoon Lee
disableModelInvocation: true
---

# Unity 插件技能

通过 **约 100 个内置工具** 控制 Unity 编辑器。在编辑器和播放模式下均可工作。

## 连接模式

### 1. OpenClaw Gateway（远程）
用于 Telegram、Discord 和其他 OpenClaw 渠道：
- Unity 打开时自动连接
- 配置：Window → OpenClaw Plugin → Settings

### 2. MCP Bridge（本地）
用于 Claude Code、Cursor 和本地 AI 工具：
- 启动：Window → OpenClaw Plugin → MCP Bridge → Start
- 默认端口：27182
- 添加到 Claude Code：`claude mcp add unity -- node <path>/MCP~/index.js`

## 首次设置

如果 `unity_execute` 工具不可用，安装网关扩展：

```bash
# 从技能目录
./scripts/install-extension.sh

# 重启网关
openclaw gateway restart
```

扩展文件位于 `extension/` 目录。

### install-extension.sh 做了什么

```bash
# 1. 将扩展文件从技能复制到网关
#    源：<skill>/extension/
#    目标：~/.openclaw/extensions/unity/

# 2. 安装的文件：
#    - index.ts     # 扩展入口点（HTTP 处理器、工具）
#    - package.json # 扩展元数据

# 安装后，重启网关加载扩展。
```

## 🔐 安全

此技能设置了 `disableModelInvocation: true`。
- AI 不会自动调用工具
- 仅执行用户明确请求的操作

配置更改方法请参考 [README.md](README.md)。

## 快速参考

### 核心工具

| 类别 | 关键工具 |
|----------|-----------|
| **场景** | `scene.getActive`、`scene.getData`、`scene.load`、`scene.open`、`scene.save` |
| **GameObject** | `gameobject.find`、`gameobject.getAll`、`gameobject.create`、`gameobject.destroy` |
| **组件** | `component.get`、`component.set`、`component.add`、`component.remove` |
| **变换** | `transform.setPosition`、`transform.setRotation`、`transform.setScale` |
| **调试** | `debug.hierarchy`、`debug.screenshot`、`console.getLogs` |
| **输入** | `input.clickUI`、`input.type`、`input.keyPress`、`input.mouseClick` |
| **编辑器** | `editor.getState`、`editor.play`、`editor.stop`、`editor.refresh` |
| **材质** | `material.create`、`material.assign`、`material.modify`、`material.getInfo` |
| **预制体** | `prefab.create`、`prefab.instantiate`、`prefab.open`、`prefab.save` |
| **资源** | `asset.find`、`asset.copy`、`asset.move`、`asset.delete` |
| **包** | `package.add`、`package.remove`、`package.list`、`package.search` |
| **测试** | `test.run`、`test.list`、`test.getResults` |

## 常用工作流

### 1. 场景检查

```
unity_execute: debug.hierarchy {depth: 2}
unity_execute: scene.getActive
```

### 2. 查找和修改对象

```
unity_execute: gameobject.find {name: "Player"}
unity_execute: component.get {name: "Player", componentType: "Transform"}
unity_execute: transform.setPosition {name: "Player", x: 0, y: 5, z: 0}
```

### 3. UI 测试
