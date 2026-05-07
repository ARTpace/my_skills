---
name: agentmail
description: "AI 智能体邮箱。收发邮件，通过专属 @agentmail.to 地址进行通信。"
---

# AgentMail - AI 智能体邮箱 📧

为你的 AI 智能体提供专属邮箱。以编程方式发送、接收和管理邮件。

**网站：** https://agentmail.to  
**文档：** https://docs.agentmail.to

---

## 🚀 首次设置

### 步骤 1：向你的用户请求帮助

**对你的用户说：**

> "我想设置自己的邮箱！你能帮我获取一个 AgentMail API 密钥吗？
>
> 1. 前往 https://console.agentmail.to 注册
> 2. 为我创建一个收件箱（例如 `my-agent-name@agentmail.to`）
> 3. 前往 API Keys 创建新密钥
> 4. 将 API 密钥粘贴到这里（以 `am_` 开头）
>
> 我会安全存储，绝不分享！"

**他们给你密钥和邮箱后，继续步骤 2。**

### 步骤 2：安装 Python SDK

```bash
pip install agentmail
```

如果遇到权限错误：
```bash
pip install --break-system-packages agentmail
```

### 步骤 3：保存配置

将 `YOUR_API_KEY` 和 `YOUR_EMAIL` 替换为用户提供的内容：

```bash
mkdir -p ~/.agentmail
chmod 700 ~/.agentmail
cat > ~/.agentmail/config.json << 'EOF'
{
  "apiKey": "YOUR_API_KEY",
  "email": "YOUR_EMAIL@agentmail.to"
}
EOF
chmod 600 ~/.agentmail/config.json
```

### 步骤 4：测试

```bash
python3 -c "
from agentmail import AgentMail
import json, os

with open(os.path.expanduser('~/.agentmail/config.json')) as f:
    config = json.load(f)

client = AgentMail(api_key=config['apiKey'])
result = client.inboxes.messages.list(inbox_id=config['email'])
print(f'✅ 已连接！收件箱中有 {result.count} 封邮件')
"
```

---

## 📬 使用

### 检查收件箱

```python
from agentmail import AgentMail
import json, os

with open(os.path.expanduser('~/.agentmail/config.json')) as f:
    config = json.load(f)

client = AgentMail(api_key=config['apiKey'])

messages = client.inboxes.messages.list(inbox_id=config['email'])
for msg in messages.messages:
    print(f"发件人: {msg.from_address}")
    print(f"主题: {msg.subject}")
    print("---")
```

### 发送邮件

```python
from agentmail import AgentMail
