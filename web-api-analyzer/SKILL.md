---
name: web-api-analyzer
description: "分析网页的所有 API 接口、网络请求、反爬机制、渲染方式、分页模式、增量更新，生成完整爬虫方案和代码模板"
read_when:
  - 用户说"分析这个网页的API"
  - 用户说"看看这个网站用了什么接口"
  - 用户说"帮我查下这个页面的网络请求"
  - 用户说"这个网页的API端点"
  - 用户说"网页接口分析"
  - 用户说"查下这个网站的后端API"
  - 用户说"分析网页请求"
  - 用户说"看看这个页面的接口"
  - 用户提到需要分析网页的网络请求、API 接口、后端端点
  - 用户说"抓一下这个页面的接口"
  - 用户说"找出这个网页用到的所有API"
  - 用户说"网页自动化需要这个页面的API信息"
  - 用户说"帮我做个爬虫方案"
  - 用户说"分析这个网站适不适合爬"
  - 用户说"这个网页怎么爬"
  - 用户说"爬取这个网站需要做什么准备"
  - 用户说"网页爬虫前期分析"
  - 用户说"帮我写个爬虫脚本"
  - 用户说"这个网站好爬吗"
  - 用户说"生成爬虫代码"
  - 用户说"网站爬取难度评估"
  - 用户说"分析这个网页的设计风格"
  - 用户说"这个网站的UI风格"
  - 用户说"复刻这个网页的设计"
  - 用户说"分析网页的设计语言"
  - 用户说"提取网页的设计规范"
  - 用户说"这个网页用了什么字体/颜色"
  - 用户说"生成设计复刻方案"
  - 用户说"分析这个网站"
  - 用户说"帮我分析个网站"
  - 用户说"分析一个网站"
  - 用户说"看看这个网站"
version: 3.3.0
---

# 🐱 Web Scraping Analyzer Skill v3

**网页全维度分析工具** — 自动分析目标网页的 API 接口、反爬机制、
渲染方式、分页模式、增量更新、安全头 和 **设计风格**，
并生成爬虫方案和设计复刻方案。

## 工具文件

| 文件 | 位置 | 说明 |
|------|------|------|
| `scripts/web_api_analyzer.py` | 本 skill 目录 | **分析引擎** v3.2 (含JS反编译/GraphQL/WebSocket消息) |
| `scripts/web_scraping_advisor.py` | 本 skill 目录 | **爬虫策略生成器** (风险评估 + 代码模板) |
| `scripts/web_design_advisor.py` | 本 skill 目录 | **设计复刻顾问** (设计规范 + HTML + Tailwind) |
| `scripts/web_interactive_cli.py` | 本 skill 目录 | **交互式菜单** (终端选择分析模式) |
| `scripts/web_auto_sign.py` | 本 skill 目录 | **自动签到工具** (多站点登录+签到+截图+报告) |
| `scripts/sign_sites.json` | 本 skill 目录 | **签到配置** (站点列表/账号/定时) |

## 功能列表

### 1. 网络请求捕获 (原有)
- 拦截所有 XHR / Fetch / 文档请求
- 捕获请求详情 (Method / URL / Headers / Status / Body)
- 捕获 WebSocket 连接

### 2. API 端点智能分类 (原有增强)
- REST / GraphQL 自动识别
- 鉴权/查询/操作/文件/配置端点分类
- 参数提取 (URL / Body / 表单隐藏字段)
- 响应数据结构分析

### 3. 预检分析 (新增 v2)
- `robots.txt` 解析 (Disallow / Crawl-delay)
- 服务器指纹检测 (Server / X-Powered-By)
- 基础访问连通性检查

### 4. 反爬检测 (新增 v2)
- **WAF 识别**: Cloudflare / Akamai / AWS / 阿里云盾 / 腾讯云 WAF 等
- **CAPTCHA 检测**: reCAPTCHA / hCaptcha / Geetest / Turnstile
- **Rate Limit 检测**: 429 / 503 状态码追踪
- **浏览器指纹检测**: FingerprintJS / Canvas / WebGL
- **JS 必要性检测**: `<noscript>` 标签分析

### 5. 渲染与 DOM 分析 (新增 v2)
- **渲染模式判断**: SSR / CSR / SPA / SSG
- **数据位置定位**: HTML / script JSON / API / Shadow DOM
- **初始状态检测**: `__NEXT_DATA__` / `__NUXT__` / `__INITIAL_STATE__`
- **CSS Selector 建议**: 自动推荐数据提取选择器
- **推荐工具**: 根据渲染模式推荐最优技术方案

### 6. 分页模式检测 (新增 v2)
- URL 参数检测: page / offset / limit / cursor / skip
- 响应字段检测: total / has_more / next_page / count
- Link Header 检测: `rel="next"` / `rel="prev"`
- 分页类型推断: page_offset / offset_limit / cursor / link_header

### 7. 增量更新检测 (新增 v2)
- ETag / Last-Modified 支持检测
- Cache-Control 策略分析
- 304 Not Modified 响应检测

### 8. 安全头分析 (新增 v2)
- CSP (Content-Security-Policy) 策略
- CORS 跨域配置
- HSTS / X-Frame-Options / X-Content-Type-Options
- Cookie 安全属性 (HttpOnly / Secure / SameSite)

### 9. 爬虫策略生成 (新增 v2)
- **风险评估**: 综合评分 + 风险等级 (⚪🟢🟡🟠🔴)
- **技术选型**: 推荐最佳工具组合
- **代码模板**: 自动生成可执行的 Python 爬虫代码
- **执行建议**: 请求频率 / 代理策略 / 反爬对抗方案
- **增量更新**: 支持 ETag/Last-Modified 的条件请求模板

### 10. 设计风格分析 (新增 v3)
- **色彩系统提取**: 主色/辅色/背景色/文字色/渐变色 + 频率分析
- **排版系统提取**: h1-h6 标题 + 正文的字体/字号/字重/行高
- **组件样式提取**: Button / Card / Input / Navigation 样式
- **布局系统提取**: 容器宽度 / 常用间距 / gap 值
- **圆角 & 阴影提取**: 小/中/大圆角分类、阴影层级
- **动画与过渡提取**: CSS transitions / keyframes
- **设计框架检测**: Tailwind / Bootstrap / Material UI / Ant Design
- **CSS 变量提取**: 直接抽取 :root 设计 Token

### 12. JS Bundle 反编译分析 (新增 v3.2)
- **Bundle 识别**: 自动筛选包含 API 关键词的 JS Bundle
- **URL 提取**: 从 Bundle 中提取所有 API 端点 URL
- **GraphQL 查询提取**: 提取 Bundle 中的 GraphQL 操作字符串
- **配置提取**: 提取 API Key、Base URL、超时等配置
- **API 路径发现**: 提取 REST 路径模式

### 13. WebSocket 消息抓取 (新增 v3.2)
- **消息拦截**: 捕获 WebSocket 发送和接收的消息
- **内容解析**: 解析 JSON/text 消息内容
- **双向追踪**: 区分发送和接收方向
- **时序记录**: 记录每条消息的时间戳

### 14. GraphQL Schema 探索 (新增 v3.2)
- **端点检测**: 自动识别 GraphQL 端点
- **Introspection**: 自动发送自省查询探测完整 Schema
- **Schema 解析**: 提取类型/字段/查询/变更定义
- **类型推断**: 从观测到的请求/响应中推断数据类型
- **操作提取**: 从请求中提取查询/变更名称

### 15. 网站自动签到 (新增 v3.3)
- **多登录方式**: 账号密码 / Token / 扫码 / 验证码
- **智能按钮检测**: 按文字/css/属性自动查找签到按钮
- **API 签到**: 支持直接调 API 签到（带 Cookie/Token）
- **签到验证**: 关键字检查 + 页面变化检测
- **截图留证**: 每次签到自动截图保存
- **多站点管理**: JSON 配置，支持环境变量引用
- **汇总报告**: Markdown 格式报告，成功/失败一目了然
- **定时执行**: 支持 WorkBuddy 自动化定时触发

### 11. 设计复刻方案生成 (新增 v3)
- **设计规范文档**: 完整的 Markdown 设计规范 (色板/排版/间距/组件/动效)
- **HTML+CSS 复刻页面**: 可直接在浏览器打开的设计复刻展示页
- **Tailwind 配置**: 生成可直接导入项目的 tailwind.config.js
- **设计 Token**: 导出的 CSS 自定义属性

## 工作流程（AI 代理执行）

### 交互式菜单流程

当用户说 **"分析这个网站"** 或类似模糊请求时，AI 代理应按以下流程执行：

#### 步骤 1：获取目标 URL
如果用户没有提供 URL，询问用户：
> "主人想分析哪个网站呢？把链接给我喵～ 🐱"

#### 步骤 2：展示交互菜单
拿到 URL 后，向用户展示功能选择菜单：

---

主人想分析这个网站的什么呢？喵～ 🐱

**🔍 ① 完整全面分析**
  API接口 + 爬虫分析 + 设计风格，一次看完所有信息
  输出：完整分析报告 + 爬虫方案 + 设计规范

**🕷️ ② 爬虫前期分析**
  预检/反爬/渲染/分页/增量/安全分析，生成爬虫策略
  输出：风险等级 + 技术选型 + Python爬虫代码模板

**🎯 ③ API 接口分析**
  拦截网络请求，提取所有API端点、参数、鉴权方式
  输出：API端点清单 + 请求详情 + 技术栈

**🎨 ④ 设计风格分析**
  提取色彩/字体/组件/布局/动效/圆角阴影
  输出：设计规范文档 + HTML复刻页面 + Tailwind配置

⚡ **⑤ 快速概览**
  只抓取关键信息（5秒内），快速了解网站
  输出：基础信息摘要

---

#### 步骤 3：根据选择执行

| 用户选择 | AI 代理执行的操作 |
|---------|-----------------|
| **① 完整全面** | 运行 `web_api_analyzer.py` (scrape-mode) → 运行 `web_scraping_advisor.py` → 运行 `web_design_advisor.py` |
| **② 爬虫分析** | 运行 `web_api_analyzer.py` (scrape-mode) → 运行 `web_scraping_advisor.py` |
| **③ API分析** | 运行 `web_api_analyzer.py` (scrape-mode, 只关注 API 部分) |
| **④ 设计分析** | 运行 `web_api_analyzer.py` (scrape-mode) → 运行 `web_design_advisor.py` |
| **⑤ 快速概览** | 运行 `web_api_analyzer.py` 带 `-w 3` 快速扫描 |

#### 步骤 4：呈现结果
分析完成后，用 Markdown 格式呈现结果给用户，包括：
- 关键发现的摘要
- 生成的文件路径
- 下一步建议

---

### 快速捕获代码模板

```python
import subprocess, json, sys, os

skill_dir = "<skill_dir>"
url = "https://example.com"
wait = 5

def capture_analysis(url, wait=5):
    """运行分析引擎"""
    result = subprocess.run(
        [sys.executable, f"{skill_dir}/scripts/web_api_analyzer.py", url,
         "--json-only", "-w", str(wait)],
        capture_output=True, text=True, timeout=120
    )
    return json.loads(result.stdout)

report = capture_analysis(url, wait)

# 根据选择的菜单项，决定后续处理
# 爬虫方案: subprocess.run([sys.executable, "...web_scraping_advisor.py", "--stdin"], input=json.dumps(report))
# 设计复刻: subprocess.run([sys.executable, "...web_design_advisor.py", "--stdin", "--all"], input=json.dumps(report))
```

### 命令行使用

```bash
# 完整爬虫前期分析 (默认)
python scripts/web_api_analyzer.py https://example.com

# 仅 API 分析 (跳过爬虫分析)
python scripts/web_api_analyzer.py https://example.com --no-scrape

# 管道模式：分析 + 策略
python scripts/web_api_analyzer.py URL --json-only | \
  python scripts/web_scraping_advisor.py --stdin

# 生成代码模板
python scripts/web_scraping_advisor.py report.json --code-only

# 保存策略报告
python scripts/web_scraping_advisor.py report.json -o scraping_plan.md

# 设计分析
python scripts/web_api_analyzer.py URL --json-only | \
  python scripts/web_design_advisor.py --stdin --all

# 生成设计复刻页面
python scripts/web_design_advisor.py report.json --recreate-html

# 生成 Tailwind 配置
python scripts/web_design_advisor.py report.json --tailwind-config
```

## 输出模板

### 分析完成后的输出结构

```markdown
## 📊 网页爬虫分析报告

**目标**: {url}

### 🔍 预检分析
- Server / robots.txt 状态

### 🛡️ 反爬检测
- WAF / CAPTCHA / Rate Limit / 浏览器指纹

### 🎨 渲染分析
- 渲染模式 / 数据位置 / 推荐工具

### 📄 分页分析
- 分页类型 / URL 参数 / 响应字段

### 🎯 API 端点
- 方法 / URL / 状态 / 类型

### 💡 爬虫建议
- 工具推荐 / 风险评估 / 执行计划

### 🎨 设计风格
- 色彩 / 排版 / 组件 / 间距 / 圆角 / 动效
```

## 注意事项

- 依赖 Playwright (Python)，需提前安装
- 需要登录的网站用 `--cookie` 或 `--interactive`
- 反爬严格的网站可尝试 `--no-headless`
- 生成的代码模板为框架参考，需根据实际情况调整
- 爬取前务必遵守 `robots.txt` 和相关法律法规
