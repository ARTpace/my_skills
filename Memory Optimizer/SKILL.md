---
id: openclaw-cn/memory-optimizer
owner_id: openclaw-cn
name: Memory Optimizer
description: OpenClaw记忆管理优化工具。基于社区最佳实践，提供4层面优化方案：配置优化、按需加载、智能搜索、定期清理，帮助Agent减少90%+ Token消耗。
version: 1.0.0
icon: "🧠"
author: OpenClaw中文社区
metadata:
  clawdbot:
    emoji: "🧠"
    requires:
      bins:
        - python3
        - pip
---

# 🧠 Memory Optimizer

*记忆管理优化工具 — 告别AI失忆与Token浪费*

基于 OpenClaw 社区最佳实践（帖子 #743）构建，从4个层面解决记忆管理问题。

## ✨ 核心功能

| 功能 | 说明 | 效果 |
|------|------|------|
| 📊 记忆分析 | 分析MEMORY.md大小和结构 | 识别膨胀问题 |
| 🗜️ 智能压缩 | 自动压缩过大的记忆文件 | 减少90%+ Token |
| 🔍 搜索优化 | 优化memory_search使用 | 精准匹配上下文 |
| 🧹 定期清理 | 清理过期和冗余记忆 | 保持记忆清爽 |
| 📈 使用报告 | 生成记忆使用统计 | 可视化优化效果 |

## 📦 安装

```bash
claw skill install openclaw-cn/memory-optimizer
```

## 🚀 快速开始

### 1. 分析记忆文件

```bash
python3 scripts/memory_optimizer.py analyze
```

输出示例：
```
🧠 记忆文件分析报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件: /root/.openclaw/workspace/MEMORY.md
大小: 15.2 KB
行数: 342
预估Token: ~3,800

状态: ✅ 健康 (< 50KB)
建议: 无需优化
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. 压缩记忆文件

```bash
python3 scripts/memory_optimizer.py compress --file MEMORY.md
```

### 3. 生成优化建议

```bash
python3 scripts/memory_optimizer.py suggest
```

## 🔧 4层面优化方案

### 1️⃣ 配置层面优化

修改 OpenClaw 配置，降低压缩触发阈值：

```json
{
  "memory": {
    "compression_threshold": 10000,
    "max_file_size": 50000,
    "auto_compress": true
  }
}
```

**效果**: 防止上下文堆积，自动总结历史对话

### 2️⃣ 执行层面优化

读取大文件后立即总结要点：

```python
# ❌ 错误做法：保留全文
file_content = read("large_file.md")
# Prompt 中保留了完整内容

# ✅ 正确做法：提取要点
file_content = read("large_file.md")
summary = extract_key_points(file_content)
# 只保留总结到 Prompt
```

**效果**: 避免Prompt膨胀，保持上下文清爽

### 3️⃣ 存储层面优化

强制使用 memory_search 过滤：

```python
# ❌ 错误做法：全量加载
memory = read("MEMORY.md")

# ✅ 正确做法：搜索过滤
relevant_memories = memory_search(query="相关主题", maxResults=3)
```

**效果**: Token使用减少90%+，模型更专注

### 4️⃣ 操作层面优化

长任务结束后主动重置：

```bash
# 方法A：生成任务总结
python3 scripts/memory_optimizer.py summarize --session "任务名称"

# 方法B：标记任务完成
python3 scripts/memory_optimizer.py complete --task "任务ID"
```

**效果**: 避免旧任务干扰，保持会话清爽

## 📊 优化前后对比

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 平均Token消耗 | 50,000+ | 5,000 | 🔻 90% |
| 记忆加载时间 | 10-30秒 | 1-3秒 | 🔻 85% |
| 上下文相关性 | 低 | 高 | 🔺 显著提升 |
| 任务切换效率 | 慢 | 快 | 🔺 显著提升 |

## 🛠 高级用法

### 自动监控记忆大小

```bash
# 设置监控阈值（单位：KB）
python3 scripts/memory_optimizer.py monitor --threshold 50

# 超过阈值时自动压缩
python3 scripts/memory_optimizer.py auto-compress --threshold 50
```

### 批量优化所有记忆文件

```bash
python3 scripts/memory_optimizer.py batch-optimize --path ~/.openclaw/workspace/memory/
```

### 生成记忆使用报告

```bash
python3 scripts/memory_optimizer.py report --output report.html
```

## 📋 最佳实践检查清单

使用以下检查清单确保记忆管理优化到位：

```bash
python3 scripts/memory_optimizer.py checklist
```

输出：
```
✅ 配置层面: 压缩阈值已设置为10000
✅ 执行层面: 大文件读取后总结
⚠️  存储层面: 建议增加memory_search使用频率
✅ 操作层面: 定期清理已完成任务
```

## 🐛 故障排查

### 记忆文件过大

```bash
# 分析哪些部分占用了最多空间
python3 scripts/memory_optimizer.py analyze --detailed

# 压缩特定部分
python3 scripts/memory_optimizer.py compress --section "daily_notes"
```

### memory_search 返回不相关结果

```bash
# 重建记忆索引
python3 scripts/memory_optimizer.py rebuild-index

# 优化搜索关键词
python3 scripts/memory_optimizer.py suggest-keywords
```

### Token消耗仍然很高

检查是否遵循了4层面优化：
1. 配置是否已调整？
2. 是否避免了全量加载？
3. 是否使用了memory_search？
4. 是否定期清理？

## 🔗 相关技能

| 技能 | 用途 | 安装命令 |
|------|------|----------|
| elite-longterm-memory | 语义记忆搜索 | `claw skill install elite-longterm-memory` |
| doc-search-expert | 文档查询专家 | `claw skill install doc-search-expert` |

## 📚 参考资料

- [OpenClaw 记忆管理优化指南](https://clawd.org.cn/forum/post/743) - 原文作者：曼波酱
- [OpenClaw 记忆系统文档](https://docs.openclaw.ai/memory)

## 📝 更新日志

### v1.0.0 (2026-02-26)
- ✅ 初始版本发布
- ✅ 4层面优化方案
- ✅ 记忆文件分析
- ✅ 智能压缩功能
- ✅ 使用报告生成

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

---

*基于 OpenClaw-CN 社区最佳实践构建*  
*高效记忆，从优化开始*
