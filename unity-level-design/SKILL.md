---
name: unity-level-design
description: "用于创建 Unity 游戏场景和原型、构建关卡设计，或自动化 Unity 编辑器工作流程，包括地形、光照、环境设置和玩家控制器。适用于后末日场景、奇幻森林、地牢爬行等需要快速原型制作的游戏环境。"
---

# Unity 关卡设计

## 概述

使用编辑器自动化、现代 Unity API 和关卡设计最佳实践快速制作 Unity 游戏场景原型。此技能自动化地形生成、光照设置、环境布置和玩家控制器创建，让你快速实现游戏创意。

## 何时使用

在以下情况使用此技能：
- 创建原型场景（后末日、奇幻、科幻、地牢爬行等）
- 设置 Unity 地形、网格和地面几何体
- 自动化光照、后处理和環境设置
- 构建玩家控制器和基础游戏系统
- 需要从概念快速到可玩场景

## 核心工作流

### 步骤 1：研究当前 API

实现前，检查 Unity 最新 API 和最佳实践：

**现代 Unity 系统：**
- Terrain Tools 包（GPU 加速雕刻）
- Universal Render Pipeline (URP) 或 High Definition Render Pipeline (HDRP)
- DOTS/ECS 用于性能关键场景
- Shader Graph 用于自定义材质
- VFX Graph 用于粒子效果

**关键 API 参考：**
- `UnityEngine.Terrain` - 地形操作
- `UnityEditor.TerrainTools` - 编辑器地形工具
- `UnityEngine.Rendering.Universal` - URP 组件
- `UnityEditor.SceneManagement` - 场景自动化

### 步骤 2：场景设置自动化

使用编辑器脚本自动化重复设置：

```csharp
// 示例：自动化场景初始化
public static class SceneSetupHelper
{
    [MenuItem("Level Design/Create Basic Scene")]
    public static void CreateBasicScene()
    {
        SetupLighting();
        CreateTerrain();
        SetupPostProcessing();
        CreatePlayerController();
    }
}
```

### 步骤 3：地形生成

**选项：**
1. **Unity Terrain** - 最适合自然景观
2. **Mesh Generation** - 最适合风格化/建筑
3. **Procedural Generation** - 最适合无尽/可重玩世界

### 步骤 4：环境与道具

自动化布置：
- 植被（树木、草地、岩石）
- 建筑（建筑物、废墟、地牢）
- 光照（太阳、环境光、点光源）
- 效果（雾、粒子、后处理）

### 步骤 5：玩家与游戏玩法

创建基础：
- 玩家控制器（FPS、第三人称、俯视）
- 相机设置
- 输入处理
- 基础交互

## 场景类型

### 后末日场景
- 被摧毁的城市环境
- 废墟建筑和碎片
- 过度生长的植被
- 大气雾和光照
- 散落的资源/道具

### 奇幻森林
- 茂密林地地形
- 河流和湖泊
