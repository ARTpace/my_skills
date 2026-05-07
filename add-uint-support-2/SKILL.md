---
name: add-uint-support
description: "为 PyTorch 算子添加无符号整数（uint）类型支持，通过更新 AT_DISPATCH 宏实现。用于为算子、内核添加 uint16、uint32、uint64 类型支持，或当用户提到启用无符号类型、barebones 无符号类型或 uint 支持时使用。"
---

# 为算子添加无符号整数（uint）支持

此技能帮助通过更新 AT_DISPATCH 宏为 PyTorch 算子添加无符号整数类型（uint16、uint32、uint64）支持。

## 何时使用此技能

在以下情况使用此技能：
- 为算子添加 uint16、uint32 或 uint64 支持
- 用户提到"无符号类型"、"uint 支持"、"barebones 无符号类型"
- 在内核中启用 kUInt16、kUInt32、kUInt64 支持
- 处理需要扩展类型覆盖的算子实现

## 快速参考

**向现有 dispatch 添加无符号类型：**
```cpp
// 之前
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES));

// 之后（方法 1：显式添加无符号类型）
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES));

// 之后（方法 2：如果存在 AT_INTEGRAL_TYPES，使用 V2 整数类型）
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_INTEGRAL_TYPES_V2), AT_EXPAND(AT_FLOATING_TYPES));
```

## 类型组参考

**无符号类型组：**
- `AT_BAREBONES_UNSIGNED_TYPES`：kUInt16、kUInt32、kUInt64
- `AT_INTEGRAL_TYPES_V2`：AT_INTEGRAL_TYPES + AT_BAREBONES_UNSIGNED_TYPES

**关系：**
```cpp
AT_INTEGRAL_TYPES          // kByte、kChar、kInt、kLong、kShort
AT_BAREBONES_UNSIGNED_TYPES  // kUInt16、kUInt32、kUInt64
AT_INTEGRAL_TYPES_V2       // INTEGRAL_TYPES + BAREBONES_UNSIGNED_TYPES
```

## 说明

### 步骤 1：确定是否需要转换为 V2

检查文件是否使用 AT_DISPATCH_V2：

**如果使用旧的 AT_DISPATCH：**
- 首先使用 at-dispatch-v2 技能转换为 AT_DISPATCH_V2
- 然后继续添加 uint 支持

**如果已使用 AT_DISPATCH_V2：**
- 直接进入步骤 2

### 步骤 2：分析当前 dispatch 宏

识别当前使用的类型组：

```cpp
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  // body
}), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);
    ^^^^^^^^^^^^^^^^^^^^^^^^^
    当前类型覆盖
```

常见模式：
- `AT_EXPAND(AT_ALL_TYPES)` → 包含 AT_INTEGRAL_TYPES + AT_FLOATING_TYPES
- `AT_EXPAND(AT_INTEGRAL_TYPES)` → 仅带符号整数
- `AT_EXPAND(AT_FLOATING_TYPES)` → 浮点类型

### 步骤 3：选择 uint 添加方法

两种方法：

**方法 1：显式添加 AT_BAREBONES_UNSIGNED_TYPES**
- 适用场景：希望显式添加 uint 支持
- 将 `AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES)` 添加到类型列表

**方法 2：用 AT_INTEGRAL_TYPES_V2 替换 AT_INTEGRAL_TYPES**
- 适用场景：dispatch 已使用 `AT_EXPAND(AT_INTEGRAL_TYPES)`
- 更简洁：用一个超集替换一个类型组
- 仅在 AT_INTEGRAL_TYPES 存在时适用

### 步骤 4：应用转换

**方法 1 示例：**
```cpp
// 之前
AT_DISPATCH_V2(
    dtype,
