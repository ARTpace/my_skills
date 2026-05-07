---
name: trello
description: "通过 Trello REST API 管理 Trello 看板、列表和卡片。"
---

# Trello 技能

直接从终端管理 Trello 看板、列表和卡片。

## 设置

1. 获取你的 API 密钥：https://trello.com/app-key
2. 生成令牌（点击该页面上的 "Token" 链接）
3. 设置环境变量：
   ```bash
   export TRELLO_API_KEY="your-api-key"
   export TRELLO_TOKEN="your-token"
   ```

## 用法

所有命令使用 curl 访问 Trello REST API。

### 列出看板
```bash
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

### 列出看板中的列表
```bash
curl -s "https://api.trello.com/1/boards/{boardId}/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

### 创建卡片
```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={listId}" \
  -d "name=卡片标题" \
  -d "desc=卡片描述"
```

### 移动卡片
```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={newListId}"
```

## 注意

- 看板/列表/卡片 ID 可以在 Trello URL 中或通过列表命令找到
- 速率限制：每个 API 密钥每 10 秒 300 个请求
