---
name: Unity
description: 避免常见的 Unity 错误 —— 生命周期顺序、GetComponent 缓存、物理时序和 Unity 的假空值。
metadata: {"clawdbot":{"emoji":"🎮","os":["linux","darwin","win32"]}}
---

## 生命周期顺序
- `Awake` 在 `Start` 之前 —— 使用 Awake 进行自我初始化，Start 用于交叉引用
- `OnEnable` 在 `Start` 之前调用 —— 但在 `Awake` 之后
- 脚本之间的顺序不保证 —— 如需使用脚本执行顺序
- `Awake` 即使禁用也会调用 —— `Start` 仅在启用时

## GetComponent 性能
- 每帧调用 `GetComponent` 很慢 —— 在 `Awake` 或 `Start` 中缓存
- `GetComponentInChildren` 递归搜索 —— 在深层级上开销大
- `TryGetComponent` 返回 bool —— 避免空检查，稍快
- 使用 `RequireComponent` 属性 —— 确保依赖，记录需求

## 物理时序
- 物理在 `FixedUpdate` 中，不在 `Update` 中 —— 无论帧率如何都一致
- `FixedUpdate` 每帧可能运行 0 次或多次 —— 不要假设 1:1
- `Rigidbody.MovePosition` 在 FixedUpdate 中 —— `transform.position` 绕过物理
- `Time.deltaTime` 在 Update 中，`Time.fixedDeltaTime` 在 FixedUpdate 中 —— 或只使用 deltaTime

## Unity 的假空值
- 销毁的对象不是真正的 null —— `== null` 返回 true，但对象存在
- 空条件 `?.` 不能正常工作 —— 使用 `== null` 或 bool 转换
- `Destroy` 不会立即发生 —— 对象在下一帧消失
- 仅在编辑器中使用 `DestroyImmediate` —— 在构建中会导致问题

## 协程
- `StartCoroutine` 需要 MonoBehaviour 激活 —— 禁用/销毁会停止协程
- `yield return null` 等待一帧 —— `yield return new WaitForSeconds(1)` 用于时间
- `StopCoroutine` 需要相同的方法或 Coroutine 引用 —— 字符串重载不可靠
- 不能返回值 —— 在协程中使用回调或设置字段

## 实例化和对象池
- `Instantiate` 开销大 —— 对频繁创建/销毁的对象使用对象池
- `Instantiate(prefab, parent)` 设置父级 —— 避免额外的 SetParent 调用
- `SetActive(false)` 在返回池之前 —— 不是 Destroy
- 将非活动对象池化在父级下 —— 保持层级整洁

## 序列化
- `[SerializeField]` 用于检查器中的私有字段 —— 优先于 public
- `public` 字段自动序列化 —— 但暴露了你可能不想要的 API
- `[HideInInspector]` 隐藏但仍序列化 —— `[NonSerialized]` 完全跳过
- 序列化字段保留检查器值 —— 首次序列化后忽略代码默认值

## ScriptableObjects
- 作为资源存在的数据容器 —— 在场景/预制体之间共享
- `CreateAssetMenu` 属性便于创建 —— 右键 → 创建
- 不要在构建中运行时修改 —— 更改不会保存（编辑器中除外）
- 非常适合配置、物品数据库 —— 减少预制体重复

## 常见错误
- 每帧使用 `Find` 方法 —— 缓存引用
- 字符串比较标签 —— 使用 `CompareTag("Enemy")`，不是 `tag == "Enemy"`
- 物理查询分配内存 —— 使用 `NonAlloc` 变体：`RaycastNonAlloc`
- UI 锚点错误 —— 在不同分辨率上意外拉伸
- 没有上下文的 `async/await` —— 使用 UniTask 或仔细的错误处理
