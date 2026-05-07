---
name: api-gateway
description: "连接 100+ API 服务（Google Workspace、Microsoft 365、GitHub、Notion、Slack、Airtable、HubSpot 等），通过 OAuth 管理授权。当用户想要与外部服务交互时使用此技能。安全：MATON_API_KEY 用于认证 Maton.ai，但本身不授予对第三方服务的访问权限。每个服务需要用户通过 Maton 的连接流程进行显式 OAuth 授权。访问严格限定在用户已授权的连接范围内。由 Maton (https://maton.ai) 提供。"
version: 1.0.85
metadata:
  author: maton
  version: '1.0'
  clawdbot:
    emoji: 🧠
    homepage: https://maton.ai
    requires:
      env:
      - MATON_API_KEY
compatibility: 需要网络访问和有效的 Maton API 密钥
---

# API 网关

通过托管 OAuth 连接直接访问第三方 API 的透传代理，由 [Maton](https://maton.ai) 提供。API 网关让你直接调用原生 API 端点。

## 快速开始

```bash
# 原生 Slack API 调用
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'channel': 'C0123456', 'text': 'Hello from gateway!'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/slack/api/chat.postMessage', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## 基础 URL

```
https://gateway.maton.ai/{app}/{native-api-path}
```

将 `{app}` 替换为服务名称，`{native-api-path}` 替换为实际 API 端点路径。

重要：URL 路径必须以连接的应用名称开头（如 `/google-mail/...`）。此前缀告诉网关使用哪个应用连接。例如，原生 Gmail API 路径以 `gmail/v1/` 开头，因此完整路径为 `/google-mail/gmail/v1/users/me/messages`。

## 认证

所有请求需要在 Authorization 头中包含 Maton API 密钥：

```
Authorization: Bearer $MATON_API_KEY
```

API 网关自动为目标服务注入适当的 OAuth 令牌。

**环境变量：** 可以将 API 密钥设置为 `MATON_API_KEY` 环境变量：

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

## 获取 API 密钥

1. 在 [maton.ai](https://maton.ai) 登录或创建账户
2. 前往 [maton.ai/settings](https://maton.ai/settings)
3. 点击 API Key 部分右侧的复制按钮复制

## 连接管理

连接管理使用单独的基础 URL：`https://ctrl.maton.ai`

### 列出连接

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=slack&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**查询参数（可选）：**
- `app` - 按服务名称筛选（如 `slack`、`hubspot`、`salesforce`）
- `status` - 按连接状态筛选（`ACTIVE`、`PENDING`、`FAILED`）

**响应：**
```json
{
  "connections": [
    {
