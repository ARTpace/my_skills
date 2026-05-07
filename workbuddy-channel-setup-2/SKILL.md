---
name: workbuddy-channel-setup
description: "使用 playwright-cli 自动化配置 WorkBuddy 渠道集成。支持飞书和 QQ Bot 渠道，自动完成应用创建、机器人能力配置、权限设置、事件订阅、回调配置和发布上线。"
---

# WorkBuddy 渠道设置自动化

使用 `playwright-cli` 和有头浏览器自动化 WorkBuddy 渠道集成。

支持的渠道：
- **飞书** — 具有机器人能力的企业应用
- **QQ Bot** — QQ 开放平台机器人

## 先决条件

- 已安装 playwright-cli 技能
- 已安装 WorkBuddy 并启用 Claw 远程控制

### 飞书特定
- 具有应用创建权限的飞书企业账户

### QQ 特定
- 已实名认证的 QQ 账户
- QQ 开放平台开发者账户（与 QQ 账户分开，使用邮箱注册）

---

## 开始前：用户交互通知

**重要：开始任何渠道设置前，必须向用户显示以下通知：**

> **提示：本配置过程需要您的参与配合**
>
> 整个流程大部分步骤由我自动完成，但以下环节需要您在手机或桌面端手动操作：
>
> - **扫码登录** — 需要用手机扫描屏幕上的二维码完成平台登录
> - **身份验证** — 生成 AppSecret 等敏感操作时，平台会要求扫码验证身份
> - **WorkBuddy 配置** — 需要您在 WorkBuddy 桌面应用中填入凭证信息
> - **扫码添加机器人**（QQ）— 需要手机 QQ 扫码将机器人添加到消息列表
>
> 每次需要您操作时，我会暂停并明确告知您需要做什么。完成后请回复确认，我会自动继续后续步骤。
>
> 请留意系统通知，配置过程可能持续数分钟。准备好后，请告诉我要配置哪个渠道（飞书 / QQ）。

等待用户确认后再继续任何设置步骤。

---

## 渠道：飞书

完整指南：[references/feishu-setup.md](references/feishu-setup.md)

### 概述（10 步）

1. 打开浏览器并登录飞书
2. 导航到开发者控制台
3. 创建企业应用
4. 添加机器人能力
5. 批量导入权限（通过 React fiber hack 处理 Monaco 编辑器）
6. 获取应用凭证（App ID + App Secret）
7. 配置 WorkBuddy Claw 设置（手动步骤）
8. 配置事件订阅（Webhook URL + "接收消息"事件）
9. 配置卡片回调（"卡片回传交互"）
10. 创建版本 1.0.0 并发布

### 快速开始

```bash
playwright-cli open "https://open.feishu.cn" --headed
```

登录后，按照 `references/feishu-setup.md` 中的分步指南操作。

### 关键注意事项

- **Monaco 编辑器 hack 至关重要** — 步骤 5（批量权限导入）。标准填充/键盘/剪贴板方法均失败。使用 React fiber 方法。
- **步骤 7 是手动的** — 用户必须在 WorkBuddy Claw 设置中配置 App ID 和 App Secret 并提供 Webhook URL。
- **页面加载间元素引用会变化** — 点击前始终使用 `playwright-cli snapshot` 获取当前引用。
- 权限 JSON 在 `references/permissions.json` 中。

---

## 渠道：QQ Bot

完整指南：[references/qq-setup.md](references/qq-setup.md)

### 概述（10 步）

1. 打开浏览器（有头模式）并关闭弹窗
2. 关闭 OpenClaw 推广弹窗
3. 切换到二维码登录
4. 注册 QQ 开放平台账户（如需要，使用邮箱）
5. 登录并切换到"机器人"标签
6. 创建机器人（名称、头像、描述）
7. 获取 AppID 和 AppSecret（需要 QQ 扫码身份验证）
8. 配置回调 URL 和事件订阅（5 个 C2C 事件）
9. 配置 WorkBuddy Claw QQ 集成（手动步骤）
10. **扫码将机器人添加到 QQ 消息列表**（关键，最容易遗漏的步骤！）

### 快速开始
