#!/usr/bin/env python3
"""
AI 智能 API 分析器 —— Web API AI Analyzer
===========================================
配合 web_api_analyzer.py 使用，将捕获的 API 报告交给 AI 模型
进行智能分析和整理，输出：

  1. 🎯 API 端点语义解读 — 每个接口是做什么的
  2. 🔄 API 调用流程 — 登录→获取数据→操作的完整链路
  3. 🔐 鉴权/认证分析 — Cookie、Token、Session 机制
  4. 📋 参数说明 — 每个参数的用途和类型
  5. 💻 自动化代码生成 — Python / JS 调用示例
  6. 🏗️ 数据结构关联 — 请求/响应的数据模型
  7. ⚠️ 安全建议 — 潜在的安全风险和注意事项
  8. 📊 思维导图输出 — API 调用关系图

使用方式：
  # 先捕获 API
  python web_api_analyzer.py https://example.com -o report.json

  # 然后用 AI 分析 (支持多种 AI 后端)
  python web_api_ai_analyzer.py report.json                      # 默认 OpenAI
  python web_api_ai_analyzer.py report.json -o analysis.md        # 输出分析报告
  python web_api_ai_analyzer.py report.json --provider ollama     # 使用 Ollama
  python web_api_ai_analyzer.py report.json --provider deepseek   # 使用 DeepSeek
  python web_api_ai_analyzer.py report.json --no-llm              # 只做本地分析

  # 一行完成：捕获+分析
  python web_api_analyzer.py https://example.com --json-only | python web_api_ai_analyzer.py --stdin

作者：主人的小猫咪咪 🐱
"""

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.parse
from datetime import datetime
from typing import Any

# ──────────────────────────────────────────────────────────
# 颜色工具
# ──────────────────────────────────────────────────────────
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def c(text: str, color: str) -> str:
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass
    return f"{color}{text}{Colors.RESET}"


# ──────────────────────────────────────────────────────────
# 本地分析工具（不需要 LLM）
# ──────────────────────────────────────────────────────────
class LocalAnalyzer:
    """不下调 AI 的本地智能分析"""

    @staticmethod
    def analyze(report: dict) -> dict:
        result = {
            "domain_basics": LocalAnalyzer._domain_basics(report),
            "endpoint_categories": LocalAnalyzer._categorize_endpoints(report),
            "auth_analysis": LocalAnalyzer._analyze_auth(report),
            "api_flow": LocalAnalyzer._infer_flow(report),
            "parameter_map": LocalAnalyzer._extract_params(report),
            "response_shapes": LocalAnalyzer._extract_response_shapes(report),
            "endpoint_patterns": LocalAnalyzer._find_patterns(report),
        }
        return result

    @staticmethod
    def _domain_basics(report: dict) -> dict:
        """域名基本信息"""
        pi = report.get("page_info", {})
        s = report.get("stats", {})
        return {
            "title": pi.get("title", ""),
            "url": report.get("target_url", ""),
            "tech_stack": s.get("tech_stack", []),
            "has_websocket": s.get("websocket_connections", 0) > 0,
            "form_count": s.get("forms_found", 0),
        }

    @staticmethod
    def _categorize_endpoints(report: dict) -> dict:
        """对端点按路径模式分类"""
        eps = report.get("api_endpoints", [])
        categories = {
            "auth_login": [],
            "data_query": [],
            "data_mutation": [],
            "file_upload": [],
            "config_settings": [],
            "analytics": [],
            "other": [],
        }

        auth_paths = ("/login", "/auth", "/signin", "/token", "/logout",
                      "/register", "/signup", "/forgot", "/reset")
        data_query_paths = ("/list", "/search", "/query", "/get", "/detail",
                            "/info", "/profile", "/status", "/page")
        data_mutation_paths = ("/create", "/add", "/update", "/edit",
                               "/delete", "/remove", "/save", "/post")
        file_paths = ("/upload", "/download", "/file", "/image", "/attach")
        config_paths = ("/config", "/settings", "/preference")
        analytics_paths = ("/analytics", "/track", "/log", "/stat", "/report",
                           "/metric", "/monitor")

        for ep in eps:
            url = ep.get("url", "")
            method = ep.get("method", "GET")
            path = urllib.parse.urlparse(url).path.lower()
            categorized = False
            for name, patterns in [
                ("auth_login", auth_paths),
                ("data_query", data_query_paths),
                ("data_mutation", data_mutation_paths),
                ("file_upload", file_paths),
                ("config_settings", config_paths),
                ("analytics", analytics_paths),
            ]:
                if any(p in path for p in patterns):
                    categories[name].append({
                        "method": method,
                        "url": url,
                        "status": ep.get("status"),
                    })
                    categorized = True
                    break
            if not categorized:
                categories["other"].append({
                    "method": method,
                    "url": url,
                    "status": ep.get("status"),
                })

        return {k: v for k, v in categories.items() if v}

    @staticmethod
    def _analyze_auth(report: dict) -> dict:
        """分析鉴权机制"""
        eps = report.get("api_endpoints", [])
        cookies = report.get("cookies", [])
        ls = report.get("local_storage", {})
        result = {
            "has_login_endpoint": False,
            "has_token_endpoint": False,
            "auth_type_hints": [],
            "session_cookies": [],
            "tokens_in_storage": [],
            "auth_headers_observed": set(),
        }

        for ep in eps:
            url = ep.get("url", "").lower()
            if "/login" in url or "/auth" in url or "/signin" in url:
                result["has_login_endpoint"] = True
            if "/token" in url or "/refresh" in url:
                result["has_token_endpoint"] = True

        for ck in cookies:
            cname = ck.get("name", "").lower()
            if any(k in cname for k in ("session", "token", "auth", "sid", "jwt")):
                result["session_cookies"].append(ck.get("name"))

        for k, v in ls.items():
            kl = k.lower()
            if any(t in kl for t in ("token", "auth", "session", "jwt", "access", "refresh")):
                result["tokens_in_storage"].append(k)

        for ep in eps:
            headers = ep.get("request_headers", {})
            for hk in headers:
                hkl = hk.lower()
                if hkl in ("authorization", "x-auth-token", "x-api-key",
                           "x-csrf-token", "x-xsrf-token", "x-access-token"):
                    result["auth_headers_observed"].add(hk)

        if result["session_cookies"]:
            result["auth_type_hints"].append("🍪 Cookie/Session 鉴权")
        if result["tokens_in_storage"]:
            result["auth_type_hints"].append("🔑 LocalStorage Token 鉴权")
        if result["auth_headers_observed"]:
            result["auth_type_hints"].append(f"📨 Header 鉴权: {', '.join(result['auth_headers_observed'])}")
        if result["has_token_endpoint"]:
            result["auth_type_hints"].append("🔄 有 Token 刷新端点 (JWT 可能性大)")
        if not result["auth_type_hints"]:
            result["auth_type_hints"].append("⚠️ 未检测到明显的鉴权机制")

        result["auth_headers_observed"] = sorted(result["auth_headers_observed"])
        return result

    @staticmethod
    def _infer_flow(report: dict) -> list:
        """推断 API 调用流程"""
        eps = report.get("api_endpoints", [])
        flow = []

        login_eps = [e for e in eps if any(
            p in e.get("url", "").lower()
            for p in ("/login", "/auth", "/signin", "/token")
        )]
        if login_eps:
            flow.append({
                "step": 1,
                "type": "🔐 认证",
                "endpoints": [e["url"] for e in login_eps],
                "description": "登录/获取 Token，后续请求需要带上认证信息",
            })

        query_eps = [e for e in eps if e.get("method") == "GET" and e not in login_eps]
        if query_eps:
            flow.append({
                "step": 2,
                "type": "📥 数据获取",
                "endpoints": [e["url"] for e in query_eps[:5]],
                "description": "GET 请求获取数据（可能有分页/筛选参数）",
            })

        mutation_eps = [e for e in eps if e.get("method") in ("POST", "PUT", "PATCH", "DELETE")
                        and e not in login_eps]
        if mutation_eps:
            flow.append({
                "step": 3,
                "type": "✏️ 数据操作",
                "endpoints": [e["url"] for e in mutation_eps[:5]],
                "description": "增删改操作，通常需要请求体 (JSON/FormData)",
            })

        return flow

    @staticmethod
    def _extract_params(report: dict) -> list:
        """从请求 URL 和 Body 中提取参数"""
        params = []
        seen = set()
        for ep in report.get("api_endpoints", []):
            url = ep.get("url", "")
            parsed = urllib.parse.urlparse(url)
            # URL 查询参数
            qs = urllib.parse.parse_qs(parsed.query)
            for k, v in qs.items():
                if k not in seen:
                    seen.add(k)
                    params.append({
                        "name": k,
                        "source": "URL Query",
                        "sample_value": v[0] if v else "",
                        "endpoint": url[:100],
                    })
            # 路径参数
            path_parts = parsed.path.split("/")
            for p in path_parts:
                if p.startswith("{") or p.startswith(":") or re.match(r"^\d+$", p):
                    param_name = p.strip("{}:")
                    if param_name not in seen and param_name:
                        seen.add(param_name)
                        params.append({
                            "name": param_name,
                            "source": "URL Path",
                            "sample_value": p,
                            "endpoint": url[:100],
                        })
            # Body 参数（JSON 解析）
            body = ep.get("request_body", "")
            if body:
                try:
                    body_json = json.loads(body)
                    for k in body_json.keys():
                        if k not in seen:
                            seen.add(k)
                            v = body_json[k]
                            params.append({
                                "name": k,
                                "source": "Request Body",
                                "sample_value": str(v)[:50] if v else "",
                                "type": type(v).__name__ if v else "unknown",
                                "endpoint": url[:100],
                            })
                except (json.JSONDecodeError, TypeError):
                    # 可能是 form data 或其它格式
                    if "=" in body:
                        for pair in body.split("&"):
                            if "=" in pair:
                                k, v = pair.split("=", 1)
                                if k not in seen:
                                    seen.add(k)
                                    params.append({
                                        "name": k,
                                        "source": "Form Body",
                                        "sample_value": v[:50],
                                        "endpoint": url[:100],
                                    })
            # 隐藏表单字段
            for f in report.get("forms", []):
                for inp in f.get("inputs", []):
                    if inp.get("type") == "hidden" and inp.get("name"):
                        name = inp["name"]
                        if name not in seen:
                            seen.add(name)
                            params.append({
                                "name": name,
                                "source": f"Hidden Field (Form #{f.get('index','?')})",
                                "sample_value": inp.get("value", ""),
                            })
        return params

    @staticmethod
    def _extract_response_shapes(report: dict) -> list:
        """从响应体中提取数据结构"""
        shapes = []
        for ep in report.get("api_endpoints", []):
            body = ep.get("response_body", "")
            if not body:
                continue
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    fields = list(data.keys())[:20]
                elif isinstance(data, list) and data:
                    fields = list(data[0].keys())[:20] if isinstance(data[0], dict) else ["array_items"]
                else:
                    continue
                shapes.append({
                    "url": ep["url"][:100],
                    "method": ep["method"],
                    "fields": fields,
                    "top_level_type": type(data).__name__,
                })
            except json.JSONDecodeError:
                # HTML 或其他格式
                if body.strip().startswith("<"):
                    shapes.append({
                        "url": ep["url"][:100],
                        "method": ep["method"],
                        "fields": ["HTML 响应"],
                        "top_level_type": "html",
                    })
        return shapes

    @staticmethod
    def _find_patterns(report: dict) -> list:
        """发现端点中的模式"""
        patterns = []
        eps = report.get("api_endpoints", [])
        urls = [e["url"] for e in eps]

        # 检查 RESTful 模式
        rest_count = sum(1 for u in urls if re.search(r"/api/\w+/\d+", u))
        if rest_count > 0:
            patterns.append(f"📐 RESTful 资源模式 ({rest_count} 个端点含 ID 路径)")

        # 检查分页模式
        pagination = ["page", "limit", "offset", "per_page", "page_size", "cursor"]
        found_pagination = [p for p in pagination if any(p in u.lower() for u in urls)]
        if found_pagination:
            patterns.append(f"📄 分页参数: {', '.join(found_pagination)}")

        # 检查版本号
        versions = set()
        for u in urls:
            m = re.search(r"/v(\d+)/", u)
            if m:
                versions.add(f"v{m.group(1)}")
        if versions:
            patterns.append(f"🔖 API 版本: {', '.join(sorted(versions))}")

        # 检查 GraphQL
        if any("graphql" in u.lower() for u in urls):
            patterns.append("🔮 GraphQL 端点")

        # 检查 WebSocket
        if report.get("websocket_connections"):
            patterns.append(f"🔌 WebSocket [{len(report['websocket_connections'])} 个连接]")

        return patterns


# ──────────────────────────────────────────────────────────
# AI 分析（LLM 驱动）
# ──────────────────────────────────────────────────────────
class AIAnalyzer:
    """调用 LLM 进行智能分析"""

    # 各 Provider 的 API 配置
    PROVIDERS = {
        "openai": {
            "api_base": "https://api.openai.com/v1",
            "model": "gpt-4o",
            "env_key": "OPENAI_API_KEY",
        },
        "deepseek": {
            "api_base": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "env_key": "DEEPSEEK_API_KEY",
        },
        "ollama": {
            "api_base": "http://localhost:11434/v1",
            "model": "qwen2.5:14b",
            "env_key": None,
        },
        "claude": {
            "api_base": "https://api.anthropic.com/v1",
            "model": "claude-3-5-sonnet-20241022",
            "env_key": "ANTHROPIC_API_KEY",
        },
        "custom": {
            "api_base": None,
            "model": None,
            "env_key": "CUSTOM_API_KEY",
        },
    }

    def __init__(self, provider: str = "openai",
                 api_key: str = "", api_base: str = "",
                 model: str = ""):
        self.provider = provider.lower()
        config = self.PROVIDERS.get(self.provider, self.PROVIDERS["openai"])

        self.api_key = api_key or os.environ.get(config["env_key"], "") if config["env_key"] else ""
        self.api_base = api_base or config["api_base"] or "http://localhost:11434/v1"
        self.model = model or config["model"]

    def is_available(self) -> bool:
        """检查 AI 后端是否可用"""
        if not self.api_key and self.provider != "ollama":
            return False
        return True

    def analyze(self, report: dict, local_analysis: dict = None) -> str:
        """调用 AI 进行深度分析"""
        prompt = self._build_prompt(report, local_analysis)
        return self._call_llm(prompt)

    def _build_prompt(self, report: dict, local_analysis: dict = None) -> str:
        """构建 AI 提示词"""
        eps = report.get("api_endpoints", [])
        forms = report.get("forms", [])
        tech = report.get("tech_stack", [])
        ws = report.get("websocket_connections", [])
        cookies = report.get("cookies", [])
        ls_items = report.get("local_storage", {})
        js_urls = report.get("js_embedded_urls", [])

        # 整理 API 端点信息（精简版）
        api_summary = []
        for ep in eps:
            entry = {
                "method": ep["method"],
                "url": ep["url"],
                "status": ep.get("status"),
                "type": ep.get("type", ""),
                "content_type": ep.get("content_type", ""),
            }
            if ep.get("request_body"):
                entry["request_body_snippet"] = ep["request_body"][:300]
            if ep.get("response_body"):
                entry["response_body_snippet"] = ep["response_body"][:300]
            api_summary.append(entry)

        local_section = ""
        if local_analysis:
            local_section = f"""
## 本地分析结果（供参考）
### 端点分类
{json.dumps(local_analysis.get('endpoint_categories', {}), ensure_ascii=False, indent=2)}

### 鉴权分析
{json.dumps(local_analysis.get('auth_analysis', {}), ensure_ascii=False, indent=2)}

### 推断的 API 流程
{json.dumps(local_analysis.get('api_flow', []), ensure_ascii=False, indent=2)}

### 提取的参数
{json.dumps(local_analysis.get('parameter_map', [])[:15], ensure_ascii=False, indent=2)}
"""

        prompt = f"""## 任务
你是一个专业的 Web API 逆向分析专家。请分析以下网页的 API 报告，生成一份**全面的 API 分析文档**。

## 目标网页
- URL: {report.get('target_url', '')}
- 页面标题: {report.get('page_info', {}).get('title', 'N/A')}
- 技术栈: {', '.join(tech) if tech else '未检测'}

## API 端点 ({len(api_summary)} 个)
```json
{json.dumps(api_summary, ensure_ascii=False, indent=2)}
```

## 表单 ({len(forms)} 个)
```json
{json.dumps(forms, ensure_ascii=False, indent=2)}
```

## 其他信息
- WebSocket 连接: {ws}
- JS 中嵌入的 URL: {js_urls[:20]}
- 技术栈: {tech}
- Cookie: {[{c.get('name'): c.get('value','')[:20]} for c in cookies[:10]]}

{local_section}

## 要求输出 (Markdown 格式)

请输出以下内容（用中文）：

### 1. 📊 总体概览
- 网站功能推测（根据 API 命名和结构推断这个网站是干什么的）
- API 架构风格（REST / GraphQL / RPC / 混合）
- 主要端点数量及分布

### 2. 🔐 鉴权与安全分析
- 使用的鉴权方式（Cookie / Token / JWT / OAuth / API Key）
- Session 管理机制
- CSRF/XSRF 防护
- 安全建议

### 3. 🎯 各端点详细解读
对每个 API 端点，推断：
- 此 API 的用途（命名推测）
- 是否需要鉴权
- 请求/响应格式
- 关键参数说明

### 4. 🔄 API 调用流程
根据端点的依赖关系，给出典型的调用顺序：
  步骤1 → 步骤2 → 步骤3 ...

### 5. 📋 表单与数据提交
- 表格字段含义
- 隐藏字段的作用（CSRF Token?）
- 提交流程

### 6. 💻 自动化代码建议
- 针对主要 API 给出 Python (requests) 和 JavaScript (fetch) 调用示例
- 完整的认证流程代码
- 批量操作建议

### 7. ⚠️ 发现的问题与建议
- 潜在的安全风险
- 可以优化的地方
- 自动化开发需要注意的点

请用 Markdown 表格、代码块等格式使报告清晰易读。不要输出空话套话，直接给出有价值的分析。
"""
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        import http.client
        import json as json_mod

        if self.provider == "ollama":
            return self._call_openai_compatible(prompt)
        elif self.provider == "claude":
            return self._call_anthropic(prompt)
        else:
            return self._call_openai_compatible(prompt)

    def _call_openai_compatible(self, prompt: str) -> str:
        """调用 OpenAI 兼容 API (OpenAI / DeepSeek / Ollama / 自定义)"""
        import urllib.request
        import json as json_mod

        url = f"{self.api_base.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        if self.provider == "ollama":
            # Ollama 不需要 Authorization header
            headers.pop("Authorization", None)

        data = json_mod.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 8192,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json_mod.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            return f"❌ API 调用失败 (HTTP {e.code}): {error_body[:500]}"
        except Exception as e:
            return f"❌ API 调用异常: {str(e)}"

    def _call_anthropic(self, prompt: str) -> str:
        """调用 Anthropic Claude API"""
        import urllib.request
        import json as json_mod

        url = f"{self.api_base.rstrip('/')}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        data = json_mod.dumps({
            "model": self.model,
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json_mod.loads(resp.read().decode("utf-8"))
                return result["content"][0]["text"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            return f"❌ Claude API 调用失败 (HTTP {e.code}): {error_body[:500]}"
        except Exception as e:
            return f"❌ Claude API 调用异常: {str(e)}"


# ──────────────────────────────────────────────────────────
# 报告输出
# ──────────────────────────────────────────────────────────
def print_local_report(analysis: dict):
    """打印本地分析报告"""
    ba = analysis["domain_basics"]
    print(f"\n  {c('📊 本地智能分析', Colors.BOLD)}")
    print(f"  {'─'*50}")
    print(f"  🔗 {c(ba['url'], Colors.CYAN)}")
    print(f"  🏗️  技术栈: {c(', '.join(ba['tech_stack']) if ba['tech_stack'] else '未检测', Colors.MAGENTA)}")
    print(f"  📝 表单: {ba['form_count']}   🔌 WebSocket: {'是' if ba['has_websocket'] else '否'}")

    # 端点分类
    cats = analysis.get("endpoint_categories", {})
    if cats:
        print(f"\n  {c('🎯 端点分类', Colors.BOLD)}")
        cat_names = {
            "auth_login": "🔐 认证/登录",
            "data_query": "📥 数据查询",
            "data_mutation": "✏️ 数据操作",
            "file_upload": "📎 文件操作",
            "config_settings": "⚙️ 配置设置",
            "analytics": "📈 分析统计",
            "other": "❓ 其他",
        }
        for cat_key, cat_items in cats.items():
            name = cat_names.get(cat_key, cat_key)
            print(f"    {c(name, Colors.YELLOW)}: {len(cat_items)} 个端点")
            for item in cat_items[:3]:
                print(f"      {c(item['method'], Colors.GREEN)} {item['url'][:90]}")

    # 鉴权
    auth = analysis.get("auth_analysis", {})
    if auth:
        print(f"\n  {c('🔐 鉴权分析', Colors.BOLD)}")
        for hint in auth.get("auth_type_hints", []):
            print(f"    {hint}")

    # API 流程
    flow = analysis.get("api_flow", [])
    if flow:
        print(f"\n  {c('🔄 推断的 API 调用流程', Colors.BOLD)}")
        for step in flow:
            print(f"    {c(f'Step {step["step"]}', Colors.CYAN)}: {step['type']}")
            print(f"      {step['description']}")
            for e in step["endpoints"][:3]:
                print(f"      → {c(e, Colors.DIM)}")

    # 参数
    params = analysis.get("parameter_map", [])
    if params:
        print(f"\n  {c('📋 参数清单', Colors.BOLD)}")
        for p in params[:10]:
            print(f"    {c(p['name'], Colors.GREEN)} ({p.get('source','')})")

    # 模式发现
    patterns = analysis.get("endpoint_patterns", [])
    if patterns:
        print(f"\n  {c('🔍 发现的模式', Colors.BOLD)}")
        for p in patterns:
            print(f"    {p}")

    # 响应结构
    shapes = analysis.get("response_shapes", [])
    if shapes:
        print(f"\n  {c('📦 响应数据结构', Colors.BOLD)}")
        for s in shapes[:5]:
            print(f"    {c(s['method'], Colors.GREEN)} {s['url']}")
            print(f"      {c('字段:', Colors.DIM)} {', '.join(s['fields'][:8])}")


# ──────────────────────────────────────────────────────────
# 全流程：捕获 + AI 分析
# ──────────────────────────────────────────────────────────
def run_full_pipeline(url: str, **kwargs):
    """先捕获 API，再用 AI 分析（一键完成）"""
    from web_api_analyzer import WebAnalyzer

    analyzer = WebAnalyzer(
        url=url,
        headless=not kwargs.get("no_headless", False),
        wait_time=kwargs.get("wait", 5),
        interactive=kwargs.get("interactive", False),
        cookie_str=kwargs.get("cookie", ""),
        verbose=kwargs.get("verbose", False),
        json_only=True,
    )
    report = analyzer.run()

    ai_analyzer = AIAnalyzer(
        provider=kwargs.get("provider", "openai"),
        api_key=kwargs.get("api_key", ""),
        api_base=kwargs.get("api_base", ""),
        model=kwargs.get("model", ""),
    )

    return report, ai_analyzer


# ──────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="🐱 Web API AI Analyzer - AI 智能分析 API 报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            示例:
              %(prog)s report.json                                          # 分析已有报告
              %(prog)s report.json --no-llm                                  # 仅本地分析
              %(prog)s report.json -o analysis.md                            # 导出分析报告
              %(prog)s report.json --provider deepseek                       # 用 DeepSeek
              %(prog)s report.json --provider ollama                         # 用 Ollama 本地模型
              %(prog)s report.json --provider ollama --model qwen2.5:7b      # 指定模型
              %(prog)s report.json --provider custom --api-base https://...  # 自定义 API
              python web_api_analyzer.py URL --json-only | %(prog)s --stdin  # 管道输入
        """),
    )
    parser.add_argument("input", nargs="?",
                        help="API 报告 JSON 文件路径")
    parser.add_argument("--stdin", action="store_true",
                        help="从 stdin 读取报告 (管道模式)")
    parser.add_argument("-o", "--output",
                        help="输出分析报告到文件 (.md)")
    parser.add_argument("--provider", default="openai",
                        choices=["openai", "deepseek", "claude", "ollama", "custom"],
                        help="AI 提供商 (默认: openai)")
    parser.add_argument("--api-key", default="",
                        help="API Key (默认从环境变量读取)")
    parser.add_argument("--api-base", default="",
                        help="自定义 API Base URL")
    parser.add_argument("--model", default="",
                        help="模型名称 (默认使用各 provider 的默认模型)")
    parser.add_argument("--no-llm", action="store_true",
                        help="仅做本地分析，不调用 AI")
    parser.add_argument("--capture-url",
                        help="一键完成：先捕获 URL 的 API，再 AI 分析")

    args = parser.parse_args()

    # ── 加载报告数据 ──
    report = None

    if args.capture_url:
        print(f"\n  {c('[⚡]', Colors.YELLOW)} 一键模式：先捕获 API，再 AI 分析...")
        report_raw, ai = run_full_pipeline(
            url=args.capture_url,
            wait=10,
            no_headless=False,
        )
        report = report_raw
        # 用命令行参数覆盖
        args.provider = getattr(args, "provider", ai.provider)
        args.api_key = getattr(args, "api_key", ai.api_key)
        args.api_base = getattr(args, "api_base", ai.api_base)
        args.model = getattr(args, "model", ai.model)
        print(f"  {c('[✅]', Colors.GREEN)} API 捕获完成！开始分析...")

    elif args.stdin:
        try:
            report = json.load(sys.stdin)
            print(f"  {c('[✅]', Colors.GREEN)} 从 stdin 读取报告成功", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"  {c('[❌]', Colors.RED)} JSON 解析失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                report = json.load(f)
            print(f"  {c('[✅]', Colors.GREEN)} 从文件读取报告成功: {args.input}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"  {c('[❌]', Colors.RED)} 读取失败: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        print(f"\n  {c('[❌]', Colors.RED)} 请指定报告文件路径、--stdin 或 --capture-url")
        sys.exit(1)

    if not report:
        print(f"  {c('[❌]', Colors.RED)} 未能加载报告数据")
        sys.exit(1)

    # ── 本地分析 ──
    print(f"\n  {c('[🔍]', Colors.CYAN)} 正在进行本地智能分析...")
    local_analysis = LocalAnalyzer.analyze(report)
    print_local_report(local_analysis)

    # ── AI 分析 ──
    output_content = ""
    if not args.no_llm:
        ai = AIAnalyzer(
            provider=args.provider,
            api_key=args.api_key,
            api_base=args.api_base,
            model=args.model,
        )

        if not ai.is_available():
            print(f"\n  {c('[⚠️]', Colors.YELLOW)} AI 后端不可用，仅显示本地分析结果")
            print(f"  {c('💡', Colors.DIM)} 可设置环境变量:")
            for pname, pconf in AIAnalyzer.PROVIDERS.items():
                if pconf["env_key"]:
                    print(f"    {pname}: {c(f'{pconf["env_key"]}=your_key', Colors.CYAN)}")
            print(f"    或使用 {c('ollama', Colors.GREEN)} 本地模型 (无需 API Key)")
        else:
            print(f"\n  {c('[🤖]', Colors.MAGENTA)} 正在调用 {args.provider} ({ai.model}) 进行 AI 分析...")
            print(f"  {c('[⏳]', Colors.YELLOW)} 等待 AI 响应...(可能需要 10-30 秒)")

            ai_result = ai.analyze(report, local_analysis)
            output_content = ai_result

            print()
            print(c(f"{'='*60}", Colors.MAGENTA))
            print(c(f"  🤖 AI 分析报告", Colors.BOLD))
            print(c(f"{'='*60}", Colors.MAGENTA))
            print()
            print(ai_result)
            print()
            print(c(f"{'='*60}", Colors.MAGENTA))
    else:
        print(f"\n  {c('[💡]', Colors.YELLOW)} --no-llm 模式，跳过 AI 分析")

    # ── 导出 ──
    output_path = args.output
    if not output_path and not args.no_llm and output_content:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"api_ai_analysis_{ts}.md"

    if output_path and output_content:
        with open(output_path, "w", encoding="utf-8") as f:
            # 加个头部
            header = f"""# 🤖 AI API 分析报告

- **目标**: {report.get('target_url', 'N/A')}
- **分析时间**: {datetime.now().isoformat()}
- **AI 模型**: {args.provider} / {AIAnalyzer.PROVIDERS.get(args.provider, {}).get('model', '')}
- **API 端点数**: {report.get('stats', {}).get('api_endpoints', 0)}

---
"""
            f.write(header)
            f.write(output_content)
        print(f"  {c('[💾]', Colors.GREEN)} AI 分析报告已导出: {output_path}")

    print(f"\n  {c('✅ 分析完成！', Colors.BOLD)}")


if __name__ == "__main__":
    main()
