#!/usr/bin/env python3
"""
网页 API 接口 & 爬虫前期分析工具 —— Web Scraping Analyzer
============================================================
自动分析目标网页的网络请求、API 接口、反爬机制、渲染方式、
分页模式、增量更新等，输出完整报告，为爬虫开发做前期准备。

功能：
  1. 拦截所有网络请求 (XHR/Fetch/文档/图片/脚本/样式等)
  2. 智能分类 API 端点 (REST/GraphQL/JSON-RPC 等)
  3. 提取请求详情 (Method / URL / Headers / Status / Body)
  4. 预检分析 (robots.txt + 服务器指纹)
  5. 反爬检测 (WAF / CAPTCHA / Rate Limit / JS 必要性)
  6. 渲染与 DOM 分析 (SSR/CSR/SPA/SSG + 数据定位)
  7. 分页模式检测 (URL 参数 / 响应字段 / 无限滚动)
  8. 增量更新检测 (ETag / Last-Modified / Cache)
  9. 安全头分析 (CSP / CORS / HSTS / Cookie 属性)
  10. 提取表单 action 和隐藏字段
  11. 检测 WebSocket 连接
  12. 检测页面使用的技术栈 (框架 / 库)
  13. 导出 JSON / Markdown 报告

使用方式：
  python web_api_analyzer.py <url> [选项]

示例：
  python web_api_analyzer.py https://example.com
  python web_api_analyzer.py https://example.com -o report.json -w 10
  python web_api_analyzer.py https://example.com --cookie "session=abc123"
  python web_api_analyzer.py https://example.com --scrape-mode  # 完整爬虫分析

版本: 2.0.0
作者：主人的小猫咪咪 🐱
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from typing import Any

# ──────────────────────────────────────────────────────────
# 颜色输出 (Windows 兼容)
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
# 工具函数
# ──────────────────────────────────────────────────────────
def safe_truncate(text: str | None, max_len: int = 500) -> str:
    if not text:
        return ""
    text_str = str(text)
    if len(text_str) > max_len:
        return text_str[:max_len] + f"... [截断, 共 {len(text_str)} 字符]"
    return text_str


def is_api_url(url: str) -> tuple[bool, str]:
    path = urllib.parse.urlparse(url).path.lower()
    api_patterns = [
        "/api/", "/v1/", "/v2/", "/v3/", "/rest/", "/graphql",
        "/rpc", "/jsonrpc", "/soap", "/service", "/endpoint",
        "/gateway", "/proxy", "/webhook", "/callback",
        "/data/", "/query", "/search", "/list", "/detail",
        "/users", "/posts", "/products", "/orders", "/items",
        "/login", "/auth", "/token", "/refresh", "/logout",
        "/upload", "/download", "/export", "/import",
        "/config", "/settings", "/profile",
        ".json", ".xml", ".action", ".do", ".ajax",
    ]
    for pattern in api_patterns:
        if pattern in path:
            return True, "REST"
    if "graphql" in path or url.endswith("/graphql"):
        return True, "GraphQL"
    return False, ""


def classify_request(url: str, resource_type: str) -> str:
    if resource_type in ("xhr", "fetch"):
        is_api, api_type = is_api_url(url)
        if is_api:
            return f"API ({api_type})"
        return "XHR / Fetch"
    type_map = {
        "document": "📄 文档", "stylesheet": "🎨 样式表 (CSS)",
        "script": "📜 脚本 (JS)", "image": "🖼️ 图片",
        "media": "🎬 媒体", "font": "🔤 字体",
        "websocket": "🔌 WebSocket", "manifest": "📋 Manifest",
        "prefetch": "⚡ Prefetch", "ping": "📡 Ping",
        "other": "❓ 其他",
    }
    return type_map.get(resource_type, f"❓ {resource_type}")


def parse_content_type(headers: dict[str, str]) -> str:
    ct = headers.get("content-type", headers.get("Content-Type", ""))
    return ct.split(";")[0].strip() if ct else ""


_WAF_FINGERPRINTS = {
    "cloudflare": ["cf-ray", "__cfduid", "cloudflare"],
    "akamai": ["akamai", "x-akamai"],
    "cloudfront": ["x-amz-cf-id", "cloudfront"],
    "incapsula": ["incapsula", "x-iinfo"],
    "sucuri": ["sucuri", "x-sucuri"],
    "modsecurity": ["mod_security", "modsecurity"],
    "aws_waf": ["x-amzn-requestid", "x-amzn-errortype"],
    "f5_bigip": ["bigip", "f5"],
    "腾讯云 WAF": ["tencent", "waf"],
    "阿里云盾": ["aliyun", "x-slb"],
    "安全狗": ["safedog", "yunsuo"],
}


def detect_waf_from_headers(headers: dict) -> str | None:
    """从响应头识别 WAF"""
    h_str = json.dumps({k.lower(): v for k, v in headers.items()}).lower()
    for waf_name, fingerprints in _WAF_FINGERPRINTS.items():
        if any(fp in h_str for fp in fingerprints):
            return waf_name
    return None


def detect_waf_from_body(body: str) -> str | None:
    """从响应体识别 WAF / 拦截页面"""
    if not body:
        return None
    b = body.lower()
    waf_body_patterns = {
        "cloudflare": ["attention required", "cloudflare", "cf-ray"],
        "akamai": ["akamai", "reference number"],
        "sucuri": ["sucuri", "website firewall"],
        "modsecurity": ["mod_security", "not acceptable", "406"],
        "腾讯安全": ["tencent", "web应用防火墙"],
        "阿里云盾": ["阿里云", "web应用防火墙"],
    }
    for waf_name, patterns in waf_body_patterns.items():
        if any(p in b for p in patterns):
            return waf_name
    return None


_PAGINATION_URL_PARAMS = [
    "page", "page_num", "pageno", "p", "offset", "start", "from",
    "limit", "per_page", "page_size", "size", "count",
    "cursor", "next", "skip", "take",
]

_PAGINATION_RESPONSE_FIELDS = [
    "total", "total_count", "total_items", "totalResults",
    "has_more", "hasMore", "is_end", "isEnd",
    "next_page", "nextPage", "next_cursor", "nextCursor",
    "page", "page_num", "offset",
    "per_page", "page_size", "limit",
    "count", "pages", "page_count",
]


# ──────────────────────────────────────────────────────────
# 核心分析器
# ──────────────────────────────────────────────────────────
class WebAnalyzer:
    """网页全面分析器（API + 爬虫前期分析）"""

    def __init__(self, url: str, headless: bool = True, wait_time: int = 5,
                 interactive: bool = False, cookie_str: str = "",
                 save_screenshot: bool = False, verbose: bool = False,
                 json_only: bool = False, scrape_mode: bool = True):
        self.url = url
        self.headless = headless
        self.wait_time = wait_time
        self.interactive = interactive
        self.cookie_str = cookie_str
        self.save_screenshot = save_screenshot
        self.verbose = verbose
        self.json_only = json_only
        self.scrape_mode = scrape_mode

        # 原有数据
        self.all_requests: list[dict] = []
        self.api_endpoints: list[dict] = []
        self.websocket_connections: list[str] = []
        self.forms: list[dict] = []
        self.page_info: dict[str, Any] = {}
        self.tech_stack: set[str] = set()
        self.embedded_apis: set[str] = set()
        self.cookies: list[dict] = []
        self.local_storage: dict[str, str] = {}
        self.js_api_urls: list[str] = []

        # 新增数据
        self.preflight: dict = {}
        self.anti_scraping: dict = {}
        self.rendering: dict = {}
        self.pagination: dict = {}
        self.incremental: dict = {}
        self.security_headers: dict = {}
        self.design_analysis: dict = {}
        self.ws_messages: list[dict] = []
        self.js_bundle_analysis: dict = {}
        self.graphql_schema: dict = {}

    # ── 日志 ──
    def _log(self, msg: str = "", file=None):
        if not msg:
            print(file=file or sys.stderr if self.json_only else sys.stdout)
            return
        print(msg, file=file or sys.stderr if self.json_only else sys.stdout)

    # ── 请求拦截 ──
    def _on_request(self, request):
        req = {
            "method": request.method, "url": request.url,
            "headers": dict(request.headers),
            "resource_type": request.resource_type,
            "timestamp": time.time(), "body": "",
            "status": None, "response_headers": {}, "response_body": "",
        }
        try:
            pd = request.post_data
            if pd:
                req["body"] = safe_truncate(pd, 2000)
        except Exception:
            pass
        self.all_requests.append(req)
        if self.verbose:
            cls = classify_request(request.url, request.resource_type)
            self._log(f"  {c('[→]', Colors.CYAN)} {request.method:6s} "
                      f"{c(cls, Colors.DIM):20s} {request.url[:120]}")

    def _on_response(self, response):
        url = response.url
        for req in reversed(self.all_requests):
            if req["url"] == url and req["status"] is None:
                req["status"] = response.status
                req["response_headers"] = dict(response.headers)
                try:
                    if response.status < 400:
                        body = response.body()
                        if body:
                            try:
                                text = body.decode("utf-8", errors="replace")
                            except Exception:
                                text = str(body)[:500]
                            ct = parse_content_type(req["response_headers"])
                            if any(t in ct for t in ("json", "text", "xml", "html", "javascript")):
                                req["response_body"] = safe_truncate(text, 3000)
                except Exception:
                    pass
                break

    def _on_request_failed(self, request):
        url = request.url
        for req in reversed(self.all_requests):
            if req["url"] == url and req["status"] is None:
                req["status"] = -1
                break

    # ══════════════════════════════════════════════════════
    # 新增模块 A: 预检分析
    # ══════════════════════════════════════════════════════
    def run_preflight(self):
        """浏览器打开前的 HTTP 预检分析"""
        result = {
            "robots_allowed": True,
            "robots_disallowed_paths": [],
            "crawl_delay": None,
            "server_tech": None,
            "x_powered_by": None,
        }
        parsed = urllib.parse.urlparse(self.url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        # robots.txt
        try:
            req = urllib.request.Request(f"{base}/robots.txt",
                headers={"User-Agent": "Mozilla/5.0"},
                method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                robots_text = resp.read().decode("utf-8", errors="replace")
                disallows = re.findall(r"^Disallow:\s*(.+)$", robots_text, re.MULTILINE)
                result["robots_disallowed_paths"] = [d.strip() for d in disallows if d.strip()]
                if result["robots_disallowed_paths"]:
                    # check if target path is disallowed
                    target_path = parsed.path or "/"
                    for d in result["robots_disallowed_paths"]:
                        if target_path.startswith(d):
                            result["robots_allowed"] = False
                            break
                # Crawl-delay
                delays = re.findall(r"^Crawl-delay:\s*(\d+\.?\d*)", robots_text, re.MULTILINE | re.IGNORECASE)
                if delays:
                    result["crawl_delay"] = float(delays[0])
        except Exception:
            result["robots_allowed"] = True  # no robots.txt = allowed

        # HEAD 请求获取服务器指纹
        try:
            req = urllib.request.Request(base,
                headers={"User-Agent": "Mozilla/5.0"},
                method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                h = {k.lower(): v for k, v in resp.headers.items()}
                result["server_tech"] = h.get("server")
                result["x_powered_by"] = h.get("x-powered-by")
        except Exception:
            pass

        self.preflight = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 B: 反爬检测
    # ══════════════════════════════════════════════════════
    def run_anti_scraping_detect(self, page):
        """检测反爬机制"""
        result = {
            "waf_detected": None,
            "waf_source": None,
            "rate_limit_statuses": [],
            "has_captcha": False,
            "requires_js": False,
            "requires_cookie": False,
            "has_browser_fingerprint": False,
            "noscript_warning": False,
        }

        # 从已有请求中分析状态码 / 响应头 / 响应体
        for req in self.all_requests:
            headers = req.get("response_headers", {}) or {}
            body = req.get("response_body", "") or ""
            status = req.get("status")

            # WAF 检测
            waf = detect_waf_from_headers(headers)
            if waf:
                result["waf_detected"] = waf
                result["waf_source"] = "response_headers"
            waf = detect_waf_from_body(body)
            if waf and not result["waf_detected"]:
                result["waf_detected"] = waf
                result["waf_source"] = "response_body"

            # Rate limit 状态码
            if status in (429, 503):
                result["rate_limit_statuses"].append(status)

        # 通过 page JS 检测
        try:
            detection = page.evaluate("""() => {
                const r = { captcha: false, noscript: false,
                            canvas: false, webgl: false };
                // CAPTCHA 元素检测
                const captchaSelectors = [
                    'iframe[src*="recaptcha"]', 'div[class*="recaptcha"]',
                    'div[class*="captcha"]', 'img[alt*="captcha"]',
                    '[id*="captcha"]', '[class*="geetest"]',
                    'div[class*="hcaptcha"]', 'div[class*="turnstile"]',
                ];
                for (const sel of captchaSelectors) {
                    if (document.querySelector(sel)) { r.captcha = true; break; }
                }
                // <noscript> 标签
                const noscripts = document.querySelectorAll('noscript');
                for (const ns of noscripts) {
                    const text = (ns.textContent || '').toLowerCase();
                    if (text.includes('javascript') || text.includes('enable js')) {
                        r.noscript = true; break;
                    }
                }
                return r;
            }""")
            result["has_captcha"] = detection.get("captcha", False)
            result["noscript_warning"] = detection.get("noscript", False)
            result["requires_js"] = detection.get("noscript", False)

            # 浏览器指纹检测 (检查是否有检测脚本)
            fp_check = page.evaluate("""() => {
                const allScripts = Array.from(document.scripts).map(s => s.src).join(' ');
                const patterns = [
                    'fingerprint', 'fingerprintjs', 'fpjs', 'clientjs',
                    'creepjs', 'audioctx', 'canvas2d', 'webgl',
                ];
                for (const p of patterns) {
                    if (allScripts.toLowerCase().includes(p)) return true;
                }
                return false;
            }""")
            result["has_browser_fingerprint"] = fp_check
        except Exception:
            pass

        # Cookie 必要性检测
        result["requires_cookie"] = len(self.cookies) > 0

        self.anti_scraping = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 C: 渲染与 DOM 分析
    # ══════════════════════════════════════════════════════
    def analyze_rendering(self, page):
        """分析页面渲染方式与数据位置"""
        parsed = urllib.parse.urlparse(self.url)

        result = {
            "mode": "unknown",
            "data_location": "unknown",
            "initial_state_json": False,
            "initial_state_sources": [],
            "has_iframe_data": False,
            "has_shadow_dom_data": False,
            "data_selectors": [],
            "html_content_ratio": 0,
            "suggested_tool": "requests",
        }

        # 从页面检测渲染模式
        try:
            rendering = page.evaluate("""() => {
                const r = {
                    hasInitialState: false,
                    initialStateKeys: [],
                    hasIframeData: false,
                    hasShadowDom: false,
                    dataContainers: [],
                    htmlTextLength: document.body ? document.body.innerText.length : 0,
                    isShell: false,
                };
                // 检查 __NEXT_DATA__
                const nd = document.getElementById('__NEXT_DATA__');
                if (nd) { r.hasInitialState = true; r.initialStateKeys.push('__NEXT_DATA__'); }
                // 检查 window.__INITIAL_STATE__
                if (window.__INITIAL_STATE__) {
                    r.hasInitialState = true;
                    r.initialStateKeys.push('window.__INITIAL_STATE__');
                }
                if (window.__NUXT__) {
                    r.hasInitialState = true;
                    r.initialStateKeys.push('window.__NUXT__');
                }
                if (window.__REACT_QUERY_STATE__) {
                    r.hasInitialState = true;
                    r.initialStateKeys.push('window.__REACT_QUERY_STATE__');
                }
                if (window.__APOLLO_STATE__) {
                    r.hasInitialState = true;
                    r.initialStateKeys.push('window.__APOLLO_STATE__');
                }
                // iframe
                if (document.querySelectorAll('iframe').length > 0) {
                    r.hasIframeData = true;
                }
                // <script> JSON 数据
                document.querySelectorAll('script[type="application/json"]').forEach(el => {
                    if (el.id) r.initialStateKeys.push('#' + el.id);
                });
                return r;
            }""")
            result["initial_state_json"] = rendering.get("hasInitialState", False)
            result["initial_state_sources"] = rendering.get("initialStateKeys", [])
            result["has_iframe_data"] = rendering.get("hasIframeData", False)

            # 计算 HTML 内容比例 (纯文本 vs 总 HTML)
            html_len = len(page.content())
            text_len = rendering.get("htmlTextLength", 0)
            if html_len > 0:
                result["html_content_ratio"] = round(text_len / html_len, 3)
        except Exception:
            pass

        # 渲染模式推断
        ts = self.tech_stack
        html_size = len(page.content()) if hasattr(page, 'content') else 0
        initial_json = result["initial_state_json"]

        if "Next.js" in ts or "Nuxt.js" in ts:
            result["mode"] = "ssr" if any("__NEXT_DATA__" in s for s in result["initial_state_sources"]) else "ssg"
            result["data_location"] = "html_and_script_json"
        elif "React" in ts and html_size < 5000 and not initial_json:
            result["mode"] = "spa"
            result["data_location"] = "api"
        elif "Vue" in ts and html_size < 5000:
            result["mode"] = "spa"
            result["data_location"] = "api"
        elif initial_json and html_size < 5000:
            result["mode"] = "csr"
            result["data_location"] = "script_json"
        elif html_size > 10000:
            result["mode"] = "ssr"
            result["data_location"] = "html"
        else:
            result["mode"] = "unknown"

        # 根据模式推荐工具
        tool_map = {
            "ssr": "requests + BeautifulSoup",
            "ssg": "requests + BeautifulSoup",
            "csr": "requests (direct API) 或 Playwright",
            "spa": "直接调 API (推荐) 或 Playwright",
        }
        result["suggested_tool"] = tool_map.get(result["mode"], "Playwright")

        # 数据位置建议 CSS Selector
        try:
            selectors = page.evaluate("""() => {
                const selectors = [];
                // 查找包含大量文本的容器
                const containers = document.querySelectorAll(
                    'main, article, .content, #content, .list, .data-list, ' +
                    'table, .table, .grid, .cards, .items, .results, #results'
                );
                containers.forEach(el => {
                    const text = el.innerText || '';
                    if (text.length > 200 && el.children.length > 1) {
                        const tag = el.tagName.toLowerCase();
                        const id = el.id ? '#' + el.id : '';
                        const cls = el.className && typeof el.className === 'string'
                            ? '.' + el.className.split(' ').filter(Boolean).join('.') : '';
                        selectors.push(tag + id + cls);
                    }
                });
                return selectors.slice(0, 8);
            }""")
            result["data_selectors"] = selectors
        except Exception:
            pass

        self.rendering = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 D: 分页模式检测
    # ══════════════════════════════════════════════════════
    def detect_pagination(self):
        """分析请求中的分页模式"""
        result = {
            "url_params": [],
            "response_fields": [],
            "pagination_type": "none",
            "has_link_header_next": False,
        }

        url_params_found = set()
        resp_fields_found = set()

        for ep in self.api_endpoints:
            url = ep.get("url", "")
            # URL 参数检测
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            for k in qs:
                if k.lower() in _PAGINATION_URL_PARAMS:
                    url_params_found.add(k)

            # 响应体分页字段检测
            body = ep.get("response_body", "") or ""
            if body:
                try:
                    data = json.loads(body)
                    if isinstance(data, dict):
                        for k in data:
                            if k.lower() in _PAGINATION_RESPONSE_FIELDS:
                                resp_fields_found.add(k)
                except (json.JSONDecodeError, TypeError):
                    pass

            # Link header
            headers = ep.get("response_headers", {}) or {}
            link = headers.get("link", headers.get("Link", ""))
            if 'rel="next"' in link or 'rel=next' in link:
                result["has_link_header_next"] = True

        result["url_params"] = sorted(url_params_found)
        result["response_fields"] = sorted(resp_fields_found)

        # 推断分页类型
        has_offset = any(p in ("offset", "start", "skip") for p in result["url_params"])
        has_page = any(p in ("page", "pageno", "page_num") for p in result["url_params"])
        has_cursor = any(p in ("cursor", "next") for p in result["url_params"])
        has_limit = any(p in ("limit", "per_page", "size") for p in result["url_params"])

        if has_cursor:
            result["pagination_type"] = "cursor"
        elif has_page and has_limit:
            result["pagination_type"] = "page_offset"
        elif has_offset and has_limit:
            result["pagination_type"] = "offset_limit"
        elif has_page:
            result["pagination_type"] = "page"
        elif result["has_link_header_next"]:
            result["pagination_type"] = "link_header"
        else:
            result["pagination_type"] = "none"

        self.pagination = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 E: 增量更新检测
    # ══════════════════════════════════════════════════════
    def detect_incremental(self):
        """检测是否支持增量更新"""
        result = {
            "supports_etag": False,
            "supports_last_modified": False,
            "cache_control": None,
            "has_304": False,
            "etag_values": [],
            "last_modified_values": [],
        }

        for req in self.all_requests:
            headers = req.get("response_headers", {}) or {}
            status = req.get("status")

            if status == 304:
                result["has_304"] = True

            etag = headers.get("etag", headers.get("ETag", ""))
            if etag:
                result["supports_etag"] = True
                result["etag_values"].append(etag)

            lm = headers.get("last-modified", headers.get("Last-Modified", ""))
            if lm:
                result["supports_last_modified"] = True
                result["last_modified_values"].append(lm)

            cc = headers.get("cache-control", headers.get("Cache-Control", ""))
            if cc and not result["cache_control"]:
                result["cache_control"] = cc

        result["etag_values"] = result["etag_values"][:3]
        result["last_modified_values"] = result["last_modified_values"][:3]

        self.incremental = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 F: 安全头分析
    # ══════════════════════════════════════════════════════
    def analyze_security_headers(self):
        """分析安全相关 HTTP 头"""
        result = {
            "csp": None,
            "csp_restrictive": False,
            "cors": None,
            "hsts": False,
            "x_frame_options": None,
            "x_content_type_options": None,
            "referrer_policy": None,
            "cookie_http_only": [],
            "cookie_secure": [],
            "cookie_samesite": [],
        }

        for req in self.all_requests:
            headers = req.get("response_headers", {}) or {}
            h = {k.lower(): v for k, v in headers.items()}

            if h.get("content-security-policy"):
                csp = h["content-security-policy"]
                result["csp"] = safe_truncate(csp, 200)
                result["csp_restrictive"] = "'self'" in csp and "*" not in csp

            if h.get("access-control-allow-origin"):
                result["cors"] = h["access-control-allow-origin"]

            if h.get("strict-transport-security"):
                result["hsts"] = True

            if h.get("x-frame-options"):
                result["x_frame_options"] = h["x-frame-options"]

            if h.get("x-content-type-options"):
                result["x_content_type_options"] = h["x-content-type-options"]

            if h.get("referrer-policy"):
                result["referrer_policy"] = h["referrer-policy"]

        # Cookie 属性分析
        for ck in self.cookies:
            name = ck.get("name", "")
            if ck.get("httpOnly", False):
                result["cookie_http_only"].append(name)
            if ck.get("secure", False):
                result["cookie_secure"].append(name)
            if ck.get("sameSite", ""):
                result["cookie_samesite"].append(f"{name}={ck['sameSite']}")

        self.security_headers = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 G: 设计风格分析
    # ══════════════════════════════════════════════════════
    def analyze_design(self, page):
        """分析网页设计风格 (色彩/排版/组件/布局/动效)"""
        result = {
            "design_system": {},
            "color_palette": {},
            "typography": {},
            "components": {},
            "spacing": {},
            "effects": {},
            "animations": {},
        }

        try:
            design = page.evaluate("""() => {
                const r = {
                    designSystem: { framework: 'custom', cssVariables: {}, confidence: 0 },
                    colors: { palette: [], backgrounds: [], texts: [], borders: [], gradients: [] },
                    typography: { headings: {}, families: new Set() },
                    components: { buttons: [], cards: [], inputs: [], navs: [] },
                    spacing: { margins: [], paddings: [], gaps: [], maxWidth: '' },
                    effects: { radii: [], shadows: [] },
                    transitions: [],
                };

                // ---- 1. CSS Variables ----
                try {
                    const root = document.querySelector(':root');
                    if (root) {
                        const cs = getComputedStyle(root);
                        for (let i = 0; i < cs.length; i++) {
                            const name = cs[i];
                            if (name.startsWith('--')) {
                                r.designSystem.cssVariables[name] = cs.getPropertyValue(name).trim();
                            }
                        }
                    }
                } catch(e) {}

                // ---- 2. 框架检测 ----
                try {
                    const stylesheets = Array.from(document.styleSheets);
                    for (const ss of stylesheets) {
                        const href = ss.href || '';
                        if (href.includes('tailwind')) { r.designSystem.framework = 'tailwind'; break; }
                        if (href.includes('bootstrap')) { r.designSystem.framework = 'bootstrap'; break; }
                    }
                    if (document.querySelector('[class*="Mui"]')) r.designSystem.framework = 'mui';
                    if (document.querySelector('[class*="ant-"]')) r.designSystem.framework = 'antd';
                    if (document.querySelector('[class*="chakra"]')) r.designSystem.framework = 'chakra';
                } catch(e) {}

                // ---- 3. 颜色提取 ----
                const colorCount = {};
                const sampleEls = Array.from(document.querySelectorAll(
                    'h1, h2, h3, h4, h5, h6, p, a, button, ' +
                    '.btn, .card, input, nav, header, footer, ' +
                    '[class*="button"], [class*="card"], [class*="header"]'
                )).slice(0, 80);

                sampleEls.forEach(el => {
                    try {
                        const cs = getComputedStyle(el);
                        const addColor = (key, val) => {
                            if (!val || val === 'transparent' || val === 'rgba(0, 0, 0, 0)') return;
                            if (val.startsWith('rgb') || val.startsWith('#')) {
                                if (!colorCount[val]) colorCount[val] = 0;
                                colorCount[val]++;
                                if (key === 'bg' && !val.includes('rgba(0,0,0,0)')) r.colors.backgrounds.push(val);
                                if (key === 'text') r.colors.texts.push(val);
                                if (key === 'border') r.colors.borders.push(val);
                            }
                        };
                        addColor('bg', cs.backgroundColor);
                        addColor('text', cs.color);
                        addColor('border', cs.borderColor);
                        // gradient
                        const bgImg = cs.backgroundImage;
                        if (bgImg && bgImg.startsWith('linear-gradient')) {
                            r.colors.gradients.push(bgImg);
                        }
                    } catch(e) {}
                });

                // 去重并排序
                r.colors.palette = Object.entries(colorCount)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 30)
                    .map(([c, count]) => ({ color: c, count, hex: c }));

                // ---- 4. 排版提取 ----
                ['h1','h2','h3','h4','h5','h6','p','body'].forEach(tag => {
                    const els = tag === 'body'
                        ? [document.body]
                        : Array.from(document.querySelectorAll(tag)).slice(0, 5);
                    if (els.length === 0) return;
                    const cs = getComputedStyle(els[0]);
                    const key = tag === 'p' ? 'body' : tag;
                    r.typography.headings[key] = {
                        family: cs.fontFamily.split(',')[0].replace(/["']/g, ''),
                        size: cs.fontSize,
                        weight: cs.fontWeight,
                        lineHeight: cs.lineHeight,
                        letterSpacing: cs.letterSpacing,
                    };
                    r.typography.families.add(cs.fontFamily.split(',')[0].replace(/["']/g, ''));
                });

                // ---- 5. 组件提取 ----
                // Buttons
                const buttons = document.querySelectorAll('button, a.btn, [class*="btn-"], [class*="button"], ' +
                    'a[class*="button"], [role="button"]');
                buttons.forEach(btn => {
                    try {
                        const cs = getComputedStyle(btn);
                        r.components.buttons.push({
                            bg: cs.backgroundColor,
                            color: cs.color,
                            radius: cs.borderRadius,
                            padding: cs.padding,
                            fontSize: cs.fontSize,
                            fontWeight: cs.fontWeight,
                            border: cs.border,
                            shadow: cs.boxShadow,
                            text: (btn.textContent || '').trim().slice(0, 20),
                        });
                    } catch(e) {}
                });

                // Cards
                const cards = document.querySelectorAll('.card, [class*="card"], [class*="Card"], ' +
                    'article, [class*="panel"], [class*="widget"]');
                cards.forEach(card => {
                    try {
                        const cs = getComputedStyle(card);
                        r.components.cards.push({
                            bg: cs.backgroundColor,
                            radius: cs.borderRadius,
                            padding: cs.padding,
                            shadow: cs.boxShadow,
                            border: cs.border,
                        });
                    } catch(e) {}
                });

                // Inputs
                document.querySelectorAll('input, textarea, select').forEach(inp => {
                    try {
                        const cs = getComputedStyle(inp);
                        r.components.inputs.push({
                            bg: cs.backgroundColor,
                            color: cs.color,
                            border: cs.border,
                            radius: cs.borderRadius,
                            padding: cs.padding,
                            fontSize: cs.fontSize,
                        });
                    } catch(e) {}
                });

                // ---- 6. 间距提取 ----
                const mainEl = document.querySelector('main, .main, #main, .container, #container, ' +
                    '.wrapper, .content, #content') || document.body;
                const mcs = getComputedStyle(mainEl);
                r.spacing.maxWidth = mcs.maxWidth || mcs.width;

                // 从多个元素收集常见间距值
                document.querySelectorAll('section, div, article, header, footer, nav').forEach(el => {
                    try {
                        const cs = getComputedStyle(el);
                        const m = parseInt(cs.marginTop);
                        const p = parseInt(cs.paddingTop);
                        if (m > 0 && m < 200) r.spacing.margins.push(m);
                        if (p > 0 && p < 200) r.spacing.paddings.push(p);
                        const g = cs.gap || cs.columnGap;
                        if (g && parseInt(g) > 0) r.spacing.gaps.push(g);
                    } catch(e) {}
                });

                // ---- 7. 圆角 & 阴影 ----
                sampleEls.forEach(el => {
                    try {
                        const cs = getComputedStyle(el);
                        const br = cs.borderRadius;
                        if (br && br !== '0px' && br !== '0px 0px 0px 0px') r.effects.radii.push(br);
                        const bs = cs.boxShadow;
                        if (bs && bs !== 'none') r.effects.shadows.push(bs);
                    } catch(e) {}
                });

                // ---- 8. 过渡/动画 ----
                try {
                    // stylesheet 中的动画
                    for (const ss of document.styleSheets) {
                        try {
                            for (const rule of ss.cssRules || []) {
                                if (rule.type === CSSRule.KEYFRAMES_RULE) {
                                    // keyframes
                                }
                                if (rule.style) {
                                    const trans = rule.style.transition;
                                    if (trans && trans !== 'none' && trans !== 'all 0s ease 0s') {
                                        r.transitions.push(trans);
                                    }
                                }
                            }
                        } catch(e) {}
                    }
                } catch(e) {}

                // 从元素中提取过渡
                sampleEls.slice(0, 20).forEach(el => {
                    try {
                        const cs = getComputedStyle(el);
                        const t = cs.transition;
                        if (t && t !== 'none' && t !== 'all 0s ease 0s' && !r.transitions.includes(t)) {
                            r.transitions.push(t);
                        }
                    } catch(e) {}
                });

                // 去重
                const unique = arr => [...new Set(arr)];
                r.colors.backgrounds = unique(r.colors.backgrounds);
                r.colors.texts = unique(r.colors.texts);
                r.colors.borders = unique(r.colors.borders);
                r.colors.gradients = unique(r.colors.gradients);
                r.effects.radii = unique(r.effects.radii);
                r.effects.shadows = unique(r.effects.shadows);
                r.transitions = unique(r.transitions);
                r.typography.families = [...r.typography.families];

                return r;
            }""")

            # 处理和分析提取的数据
            result["design_system"] = {
                "detected_framework": design.get("designSystem", {}).get("framework", "custom"),
                "css_variables": design.get("designSystem", {}).get("cssVariables", {}),
            }

            # 色彩处理
            cols = design.get("colors", {})
            palette = cols.get("palette", [])
            result["color_palette"] = {
                "full_palette": [c["color"] for c in palette],
                "backgrounds": cols.get("backgrounds", [])[:8],
                "texts": cols.get("texts", [])[:6],
                "borders": cols.get("borders", [])[:6],
                "gradients": cols.get("gradients", [])[:5],
            }
            if palette:
                result["color_palette"]["most_used"] = palette[:3]

            # 排版处理
            typo = design.get("typography", {})
            result["typography"] = {
                "headings": typo.get("headings", {}),
                "font_families": typo.get("families", []),
            }

            # 组件处理
            comps = design.get("components", {})
            result["components"] = {
                "buttons": comps.get("buttons", [])[:5],
                "cards": comps.get("cards", [])[:5],
                "inputs": comps.get("inputs", [])[:5],
            }

            # 间距
            sp = design.get("spacing", {})
            margins = sp.get("margins", [])
            paddings = sp.get("paddings", [])
            result["spacing"] = {
                "container_max_width": sp.get("maxWidth", ""),
            }
            if margins:
                # 统计频率找最常见间距
                from collections import Counter
                margin_counter = Counter(margins)
                result["spacing"]["common_margins"] = [
                    f"{v}px" for v, _ in margin_counter.most_common(6)
                ]
            if paddings:
                padding_counter = Counter(paddings)
                result["spacing"]["common_paddings"] = [
                    f"{v}px" for v, _ in padding_counter.most_common(6)
                ]

            # 圆角阴影
            eff = design.get("effects", {})
            radii = eff.get("radii", [])
            shadows = eff.get("shadows", [])
            result["effects"] = {"border_radius": {}, "box_shadow": {}}
            if radii:
                from collections import Counter
                rc = Counter(radii)
                most_common = [r for r, _ in rc.most_common(5)]
                result["effects"]["border_radius"]["all_values"] = most_common
                if most_common:
                    sorted_r = sorted(most_common, key=lambda x: int(x.replace("px","") or "0"))
                    if len(sorted_r) >= 3:
                        result["effects"]["border_radius"]["small"] = sorted_r[0]
                        result["effects"]["border_radius"]["medium"] = sorted_r[len(sorted_r)//2]
                        result["effects"]["border_radius"]["large"] = sorted_r[-1]
            if shadows:
                result["effects"]["box_shadow"]["all_values"] = shadows[:5]

            # 动画
            trans = design.get("transitions", [])
            result["animations"] = {"transitions": trans[:5]}

        except Exception as e:
            self._log(f"  {c('[!] 设计分析失败:', Colors.RED)} {e}")

        self.design_analysis = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 H: JS Bundle 反编译分析
    # ══════════════════════════════════════════════════════
    def analyze_js_bundles(self):
        """识别并分析 JS Bundle 文件，提取 API 信息"""
        result = {
            "api_bundles_found": 0,
            "api_bundles": [],
            "extracted_urls": [],
            "extracted_queries": [],
            "extracted_configs": [],
            "extracted_endpoints": [],
        }

        # 找出所有 JS 脚本请求
        js_requests = [r for r in self.all_requests if r.get("resource_type") == "script"]

        # 筛选出可能包含 API 调用的 Bundle（按文件名关键词）
        api_bundle_keywords = [
            "api", "search", "query", "graphql", "rest", "controller",
            "service", "client", "request", "fetch", "ajax", "axios",
            "sdk", "index",
        ]

        api_bundles = []
        for req in js_requests:
            url = req.get("url", "")
            url_lower = url.lower()
            # 检查文件名是否包含 API 相关关键词
            path = urllib.parse.urlparse(url).path
            filename = path.split("/")[-1].lower()
            if any(kw in filename for kw in api_bundle_keywords) or any(kw in url_lower for kw in api_bundle_keywords):
                api_bundles.append({
                    "url": url,
                    "filename": filename,
                    "size": req.get("response_headers", {}).get("content-length", "unknown"),
                })

        if not api_bundles:
            # 如果没有找到关键词匹配，取最大的几个 JS
            js_sizes = []
            for req in js_requests:
                cl = req.get("response_headers", {}).get("content-length")
                if cl:
                    try:
                        js_sizes.append((int(cl), req["url"]))
                    except ValueError:
                        pass
            js_sizes.sort(reverse=True)
            for size, url in js_sizes[:3]:
                path = urllib.parse.urlparse(url).path
                api_bundles.append({
                    "url": url, "filename": path.split("/")[-1],
                    "size": str(size),
                })

        result["api_bundles"] = api_bundles
        result["api_bundles_found"] = len(api_bundles)

        # 从 response_body 中提取信息
        for req in self.all_requests:
            body = req.get("response_body", "") or ""
            url = req.get("url", "")
            if not body or req.get("resource_type") != "script":
                continue
            if len(body) < 100:
                continue  # 太短，不太可能是 bundle

            extracted = {"source_url": url[:120], "findings": []}

            # 提取字符串中的 URL（排除常见图片/字体后缀）
            urls_found = re.findall(r'(?:"|\')(https?://[^\s"\'<>]+?)(?:"|\')', body)
            api_urls = []
            for u in urls_found:
                if not any(u.endswith(ext) for ext in [".js",".css",".png",".jpg",".gif",".svg",".ico",".woff",".woff2",".mp4",".webm"]):
                    api_urls.append(u)
            if api_urls:
                extracted["findings"].append(f"提取到 {len(api_urls)} 个 API URL")
                result["extracted_urls"].extend(api_urls[:20])

            # 提取 GraphQL 查询字符串
            gql_queries = re.findall(r'(?:query|mutation)\s+\w+[\s\S]{0,200}?(?:\{[\s\S]{0,500}?\}|;)', body[:50000])
            if gql_queries:
                for gq in gql_queries[:10]:
                    clean_q = " ".join(gq.split())[:200]
                    extracted["findings"].append(f"GraphQL: {clean_q}")
                    result["extracted_queries"].append(clean_q)

            # 提取配置对象 (apiUrl, baseUrl, endpoint 等)
            config_patterns = [
                (r'["\'](?:apiUrl|baseUrl|BASE_URL|API_URL|endpoint|base_url)["\']\s*[:=]\s*["\']([^"\']+)["\']', "API URL 配置"),
                (r'["\'](?:apiKey|api_key|appId|app_id|clientId|client_id)["\']\s*[:=]\s*["\']([^"\']{8,50})["\']', "API Key/ID"),
                (r'["\'](?:graphql|graphQl|graph_ql)["\']\s*[:=]\s*["\']([^"\']+)["\']', "GraphQL 端点"),
                (r'["\'](?:timeout|timeOut)["\']\s*[:=]\s*(\d+)', "超时配置"),
            ]
            for pattern, label in config_patterns:
                matches = re.findall(pattern, body)
                for m in matches[:3]:
                    extracted["findings"].append(f"{label}: {m[:80]}")
                    result["extracted_configs"].append(f"{label}: {m[:80]}")

            # 提取 API 端点路径模式
            api_paths = re.findall(r'(?:"|\')(/(?:api|v[12]|rest|graphql)/[^"\'? ]+?)(?:"|\')', body)
            if api_paths:
                unique_paths = list(set(api_paths))
                for p in unique_paths[:10]:
                    extracted["findings"].append(f"API 路径: {p}")
                    result["extracted_endpoints"].append(p)

            if extracted["findings"]:
                result.setdefault("bundle_details", []).append(extracted)

        # 去重
        result["extracted_urls"] = list(set(result["extracted_urls"]))[:30]
        result["extracted_queries"] = list(set(result["extracted_queries"]))[:15]
        result["extracted_configs"] = list(set(result["extracted_configs"]))[:15]
        result["extracted_endpoints"] = list(set(result["extracted_endpoints"]))[:20]

        self.js_bundle_analysis = result
        return result

    # ══════════════════════════════════════════════════════
    # 新增模块 I: GraphQL Schema 探索
    # ══════════════════════════════════════════════════════
    def explore_graphql(self, page):
        """探索 GraphQL Schema，尝试 Introspection，失败则从请求推导"""
        result = {
            "endpoints": [],
            "introspection_available": False,
            "schema": None,
            "inferred_operations": [],
            "inferred_types": [],
        }

        # 找出 GraphQL 端点
        for req in self.all_requests:
            url = req.get("url", "").lower()
            if "graphql" in url and url not in [e["url"] for e in result["endpoints"]]:
                result["endpoints"].append({
                    "url": req["url"],
                    "method": req.get("method", "POST"),
                })

        if not result["endpoints"]:
            return result

        # 尝试 Introspection Query
        introspection_query = """{"query":"query { __schema { queryType { name } mutationType { name } types { name kind description fields { name description type { name kind ofType { name kind } } } } } }"}"""

        import urllib.request as url_req
        import json as json_mod

        for ep in result["endpoints"]:
            endpoint_url = ep["url"]
            try:
                req = url_req.Request(
                    endpoint_url,
                    data=introspection_query.encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0",
                    },
                    method="POST",
                )
                with url_req.urlopen(req, timeout=10) as resp:
                    response_data = json_mod.loads(resp.read().decode("utf-8"))
                    if "data" in response_data and response_data["data"]:
                        schema_data = response_data["data"].get("__schema", {})
                        if schema_data and schema_data.get("types"):
                            result["introspection_available"] = True
                            # 提取类型摘要
                            types_summary = []
                            for t in schema_data.get("types", []):
                                if t.get("name") and not t["name"].startswith("__"):
                                    fields = t.get("fields", [])
                                    types_summary.append({
                                        "name": t["name"],
                                        "kind": t.get("kind", ""),
                                        "fields_count": len(fields) if fields else 0,
                                        "field_names": [f.get("name") for f in (fields or [])[:8]],
                                    })
                            result["schema"] = {
                                "query_type": schema_data.get("queryType", {}).get("name", "Query"),
                                "mutation_type": schema_data.get("mutationType", {}).get("name", "Mutation"),
                                "types_count": len(types_summary),
                                "types": types_summary[:30],
                            }
                            break
            except Exception:
                continue

        # 如果 Introspection 不可用，从观测到的请求中推断
        if not result["introspection_available"]:
            observed_operations = set()
            for req in self.all_requests:
                body = req.get("request_body", "") or ""
                if "graphql" in req.get("url", "").lower() and body:
                    # 提取操作名
                    ops = re.findall(r'(?:query|mutation)\s+(\w+)', body)
                    for op in ops:
                        observed_operations.add(op)

            if observed_operations:
                result["inferred_operations"] = sorted(observed_operations)

        # 从请求/响应中推断类型
        for req in self.all_requests:
            url = req.get("url", "").lower()
            if "graphql" not in url:
                continue
            resp_body = req.get("response_body", "") or ""
            if resp_body.startswith("["):
                try:
                    data = json_mod.loads(resp_body)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                inner = item.get("data", {})
                                if isinstance(inner, dict):
                                    for key, val in inner.items():
                                        if isinstance(val, dict):
                                            fields = list(val.keys())
                                            if fields:
                                                result["inferred_types"].append({
                                                    "name": key,
                                                    "fields": fields[:20],
                                                })
                except (json_mod.JSONDecodeError, TypeError):
                    pass

        # 去重 inferred_types
        seen_names = set()
        unique_types = []
        for t in result["inferred_types"]:
            if t["name"] not in seen_names:
                seen_names.add(t["name"])
                unique_types.append(t)
        result["inferred_types"] = unique_types[:20]

        self.graphql_schema = result
        return result

    # ── 页面信息提取 (原有 + 增强) ──
    def _extract_page_info(self, page):
        info = {
            "title": page.title(),
            "url": page.url,
            "html_size": len(page.content()),
        }

        # 表单
        self.forms = page.evaluate("""() => {
            return Array.from(document.forms).map((f, i) => ({
                index: i, id: f.id || '', name: f.name || '',
                action: f.action || '', method: f.method || 'GET',
                enctype: f.enctype || '',
                inputs: Array.from(f.elements).map(e => ({
                    name: e.name || '', type: e.type || '',
                    value: e.value || '', placeholder: e.placeholder || ''
                }))
            }));
        }""")

        # JS 内容提取
        js_content = page.evaluate("""() => {
            return Array.from(document.scripts).map(s => s.textContent || '').join('\\n');
        }""")
        self._extract_urls_from_js(js_content)

        # 技术栈
        tech = page.evaluate("""() => {
            const d = [];
            if (window.React || document.querySelector('[data-reactroot],[data-reactid]')) d.push('React');
            if (window.Vue || document.querySelector('[data-v-]')) d.push('Vue');
            if (window.angular || document.querySelector('[ng-app],[ng-controller]')) d.push('Angular');
            if (window.jQuery || typeof $ !== 'undefined') d.push('jQuery');
            if (window.__NEXT_DATA__) d.push('Next.js');
            if (window.__NUXT__) d.push('Nuxt.js');
            if (window.axios) d.push('Axios');
            if (window.gtag || window.dataLayer) d.push('Google Analytics');
            if (window.Turbolinks || window.Turbo) d.push('Turbo/Hotwire');
            if (window.Alpine) d.push('Alpine.js');
            if (window.htmx) d.push('htmx');
            if (window.Svelte || document.querySelector('[svelte]')) d.push('Svelte');
            if (window.require || window.define) d.push('RequireJS');
            if (window.moment) d.push('Moment.js');
            if (window._ && typeof window._.debounce === 'function') d.push('Underscore/Lodash');
            if (window.Drupal) d.push('Drupal');
            if (window.WordPress || document.querySelector('link[rel="https://api.w.org/"]')) d.push('WordPress');
            try {
                if (window.__r && window.__r.c) d.push('React (hmr)');
            } catch(e) {}
            return [...new Set(d)];
        }""")
        self.tech_stack = set(tech)

        # 全局 API 变量
        inline_calls = page.evaluate("""() => {
            const calls = [];
            const patterns = ['api','baseUrl','base_url','BASE_URL','API_URL','endpoint','host','server'];
            for (const k of patterns) {
                if (window[k] && typeof window[k] === 'string' && window[k].startsWith('http'))
                    calls.push({source:'window.'+k, url: window[k]});
            }
            document.querySelectorAll('meta[name]').forEach(m => {
                const n = m.getAttribute('name')||'', c = m.getAttribute('content')||'';
                if (n.toLowerCase().includes('api') && c.startsWith('http'))
                    calls.push({source:'meta[name='+n+']', url:c});
            });
            return calls;
        }""")
        for call in inline_calls:
            self.embedded_apis.add(f"{call['source']}: {call['url']}")

        try:
            self.cookies = page.context.cookies()
        except Exception:
            pass
        try:
            ls = page.evaluate("""() => {
                const items={}; for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i); items[k]=localStorage.getItem(k);} return items;
            }""")
            self.local_storage = ls
        except Exception:
            pass

        self.page_info = info

    def _extract_urls_from_js(self, js_content: str):
        if not js_content:
            return
        pattern = re.compile(r'(?:"|\')(https?://[^\s"\'<>]+?)(?:"|\')', re.IGNORECASE)
        skip = (".js", ".css", ".png", ".jpg", ".gif", ".svg", ".ico", ".woff")
        found = set()
        for match in pattern.finditer(js_content):
            url = match.group(1)
            if any(ext in url for ext in skip):
                continue
            found.add(url)
        self.js_api_urls = sorted(found)

    def _post_process(self):
        seen = set()
        for req in self.all_requests:
            is_api, api_type = is_api_url(req["url"])
            include = is_api or req["resource_type"] in ("xhr", "fetch") or req["resource_type"] == "document"
            if include and req["url"] not in seen:
                seen.add(req["url"])
                self.api_endpoints.append({
                    "method": req["method"], "url": req["url"],
                    "status": req["status"],
                    "type": api_type if is_api else "Page Document",
                    "request_headers": req["headers"],
                    "request_body": req.get("body", ""),
                    "response_headers": req.get("response_headers", {}),
                    "response_body": req.get("response_body", ""),
                    "content_type": parse_content_type(req.get("response_headers", {})),
                })

    def _stats(self) -> dict:
        api_count = sum(1 for e in self.api_endpoints if e["type"] != "Page Document")
        sc: dict = defaultdict(int)
        mc: dict = defaultdict(int)
        for e in self.api_endpoints:
            s = e.get("status") or 0
            sc[s] += 1
            mc[e["method"]] += 1
        return {
            "total_requests": len(self.all_requests),
            "api_endpoints": api_count,
            "forms_found": len(self.forms),
            "websocket_connections": len(self.websocket_connections),
            "status_codes": dict(sc),
            "methods": dict(mc),
            "tech_stack": sorted(self.tech_stack),
            "embedded_apis": len(self.embedded_apis),
        }

    # ── 主入口 ──
    def run(self) -> dict:
        from playwright.sync_api import sync_playwright

        domain = urllib.parse.urlparse(self.url).netloc

        self._log()
        self._log(c(f"{'='*60}", Colors.GREEN))
        self._log(c(f"  🐱 Web Scraping Analyzer v2", Colors.BOLD))
        self._log(c(f"  {'='*60}", Colors.GREEN))
        self._log(f"  🌐 目标: {c(self.url, Colors.CYAN)}")
        self._log(f"  🏠 域名: {c(domain, Colors.YELLOW)}")
        self._log(f"  ⏱  等待: {self.wait_time}s")
        self._log(f"  📋 模式: {'爬虫前期分析' if self.scrape_mode else '基础 API 分析'}")
        self._log(c(f"{'='*60}", Colors.GREEN))
        self._log()

        # 阶段 1: 预检
        self._log(f"  {c('[🔍]', Colors.CYAN)} 阶段 1/5: HTTP 预检分析...")
        self.run_preflight()

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"),
                locale="zh-CN",
                extra_http_headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"},
            )

            if self.cookie_str:
                try:
                    for part in self.cookie_str.split(";"):
                        part = part.strip()
                        if "=" in part:
                            k, v = part.split("=", 1)
                            context.add_cookies([{"name": k.strip(), "value": v.strip(), "url": self.url}])
                except Exception as e:
                    self._log(f"  {c('[!] Cookie 错误:', Colors.RED)} {e}")

            page = context.new_page()
            page.on("request", self._on_request)
            page.on("response", self._on_response)
            page.on("requestfailed", self._on_request_failed)

            # WebSocket 监听（增强：同时捕获消息）
            def on_websocket(ws):
                self.websocket_connections.append(ws.url)
                try:
                    ws.on("framesent", lambda data: self.ws_messages.append({
                        "type": "sent", "url": ws.url,
                        "payload": (data[:2000] if isinstance(data, str) else f"[binary {len(data)}b]"),
                        "timestamp": time.time(),
                    }))
                    ws.on("framereceived", lambda data: self.ws_messages.append({
                        "type": "received", "url": ws.url,
                        "payload": (data[:2000] if isinstance(data, str) else f"[binary {len(data)}b]"),
                        "timestamp": time.time(),
                    }))
                except Exception:
                    pass
            page.on("websocket", on_websocket)

            # 阶段 2: 页面加载
            self._log(f"  {c('[⚡]', Colors.YELLOW)} 阶段 2/5: 打开页面并捕获请求...")
            try:
                page.goto(self.url, wait_until="networkidle", timeout=30000)
            except Exception:
                pass

            if self.interactive:
                self._log(f"\n  {c('[💡]', Colors.MAGENTA)} 交互模式，请在打开的浏览器中操作，30秒后自动开始捕获...")
                self._log(f"  {c('[💡]', Colors.MAGENTA)} 如果已完成操作并想立即继续，请按 Ctrl+C 跳过等待喵~")
                try:
                    time.sleep(30)
                except KeyboardInterrupt:
                    pass

            self._log(f"  {c('[⏳]', Colors.YELLOW)} 等待额外请求 ({self.wait_time}s)...")
            time.sleep(self.wait_time)

            if self.save_screenshot:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                page.screenshot(path=f"analyzer_{ts}.png", full_page=True)
                self._log(f"  {c('[📸]', Colors.GREEN)} 截图已保存")

            # 阶段 3: 页面信息提取
            self._log(f"  {c('[📊]', Colors.CYAN)} 阶段 3/5: 提取页面信息...")
            self._extract_page_info(page)

            # 阶段 4: 反爬 + 渲染 + 设计分析 (需要 page 上下文)
            if self.scrape_mode:
                self._log(f"  {c('[🛡️]', Colors.CYAN)} 阶段 4/6: 反爬检测 & 渲染分析...")
                self.run_anti_scraping_detect(page)
                self.analyze_rendering(page)
                self._log(f"  {c('[🎨]', Colors.MAGENTA)} 阶段 4/6: 设计风格分析...")
                self.analyze_design(page)
                self._log(f"  {c('[🔮]', Colors.CYAN)} 阶段 4/6: GraphQL Schema 探索...")
                self.explore_graphql(page)

            context.close()
            browser.close()

        # 阶段 5: 后处理分析
        self._log(f"  {c('[🔧]', Colors.CYAN)} 阶段 5/5: 数据后处理...")
        self._post_process()

        if self.scrape_mode:
            self.detect_pagination()
            self.detect_incremental()
            self.analyze_security_headers()
            self._log(f"  {c('[📦]', Colors.YELLOW)} 阶段 5/6: JS Bundle 反编译分析...")
            self.analyze_js_bundles()

        # 组装报告
        report = {
            "analyzed_at": datetime.now().isoformat(),
            "target_url": self.url,
            "domain": domain,
            "analyzer_version": "2.0.0",
            "page_info": self.page_info,
            "stats": self._stats(),
            "api_endpoints": self.api_endpoints,
            "all_requests_summary": [
                {"method": r["method"], "url": r["url"],
                 "resource_type": r["resource_type"], "status": r["status"]}
                for r in self.all_requests
            ],
            "websocket_connections": self.websocket_connections,
            "forms": self.forms,
            "js_embedded_urls": self.js_api_urls,
            "tech_stack": sorted(self.tech_stack),
            "embedded_global_apis": sorted(self.embedded_apis),
            "cookies": self.cookies,
            "local_storage": self.local_storage,
        }

        if self.scrape_mode:
            report.update({
                "preflight": self.preflight,
                "anti_scraping": self.anti_scraping,
                "rendering": self.rendering,
                "pagination": self.pagination,
                "incremental": self.incremental,
                "security_headers": self.security_headers,
                "design_analysis": self.design_analysis,
                "js_bundle_analysis": self.js_bundle_analysis,
                "graphql_schema": self.graphql_schema,
                "ws_messages": self.ws_messages,
            })

        return report


# ──────────────────────────────────────────────────────────
# 报告输出
# ──────────────────────────────────────────────────────────
def print_report(report: dict):
    s = report["stats"]
    pi = report["page_info"]

    def p(msg=""):
        print(msg)

    p()
    p(c(f"{'='*60}", Colors.GREEN))
    p(c(f"  📋 分析报告", Colors.BOLD))
    p(c(f"{'='*60}", Colors.GREEN))
    p(f"  🏠 页面标题: {c(pi.get('title', 'N/A'), Colors.CYAN)}")
    p(f"  🔗 目标 URL: {c(report['target_url'], Colors.CYAN)}")
    p(f"  📊 总请求数: {s['total_requests']} | 🎯 API: {s['api_endpoints']} | 📝 表单: {s['forms_found']}")

    # ---- 爬虫分析结果 ----
    if "preflight" in report:
        pf = report["preflight"]
        p(f"\n  {c('[🔍 预检分析]', Colors.BOLD)}")
        p(f"    Server: {c(pf.get('server_tech') or '未知', Colors.CYAN)}")
        p(f"    X-Powered-By: {c(pf.get('x_powered_by') or '未知', Colors.DIM)}")
        p(f"    robots.txt: {c('允许爬取' if pf.get('robots_allowed', True) else '⛔ 禁止爬取', Colors.GREEN if pf.get('robots_allowed', True) else Colors.RED)}")
        if pf.get("robots_disallowed_paths"):
            p(f"    Disallow 路径: {c(', '.join(pf['robots_disallowed_paths'][:5]), Colors.YELLOW)}")
        if pf.get("crawl_delay"):
            cd_val = pf["crawl_delay"]
            cd_text = f"{cd_val}秒"
            p(f"    Crawl-delay: {c(cd_text, Colors.YELLOW)}")

    if "anti_scraping" in report:
        af = report["anti_scraping"]
        p(f"\n  {c('[🛡️  反爬检测]', Colors.BOLD)}")
        waf = af.get("waf_detected")
        p(f"    WAF: {c(waf or '未检测到', Colors.RED if waf else Colors.GREEN)}")
        p(f"    CAPTCHA: {c('⚠️ 有' if af.get('has_captcha') else '✓ 无', Colors.RED if af.get('has_captcha') else Colors.GREEN)}")
        p(f"    JS 必要性: {c('需要 JS' if af.get('requires_js') else '可能不需要', Colors.YELLOW if af.get('requires_js') else Colors.GREEN)}")
        if af.get("rate_limit_statuses"):
            rl_count = len(af["rate_limit_statuses"])
            rl_text = f"检测到 {rl_count} 次限流"
            p(f"    Rate Limit: {c(rl_text, Colors.RED)}")
        p(f"    浏览器指纹: {c('⚠️ 有' if af.get('has_browser_fingerprint') else '✓ 无', Colors.RED if af.get('has_browser_fingerprint') else Colors.GREEN)}")

    if "rendering" in report:
        rd = report["rendering"]
        mode_emoji = {"ssr": "🖥️", "csr": "💻", "spa": "📱", "ssg": "📄", "unknown": "❓"}
        p(f"\n  {c('[🎨 渲染分析]', Colors.BOLD)}")
        mode = rd.get("mode", "unknown")
        me = mode_emoji.get(mode, "")
        mode_label = f"{me} {mode.upper()}"
        p(f"    渲染模式: {c(mode_label, Colors.MAGENTA)}")
        p(f"    数据位置: {c(rd.get('data_location', 'unknown'), Colors.CYAN)}")
        p(f"    推荐工具: {c(rd.get('suggested_tool', 'Playwright'), Colors.GREEN)}")
        if rd.get("initial_state_json"):
            p(f"    初始状态: {c('✓ ' + ', '.join(rd['initial_state_sources']), Colors.YELLOW)}")
        if rd.get("data_selectors"):
            p(f"    建议选择器: {c(', '.join(rd['data_selectors'][:4]), Colors.DIM)}")

    if "pagination" in report:
        pg = report["pagination"]
        pt = pg.get("pagination_type", "none")
        p(f"\n  {c('[📄 分页分析]', Colors.BOLD)}")
        p(f"    分页类型: {c(pt, Colors.CYAN)}")
        if pg.get("url_params"):
            p(f"    URL 参数: {c(', '.join(pg['url_params']), Colors.YELLOW)}")
        if pg.get("response_fields"):
            p(f"    响应字段: {c(', '.join(pg['response_fields'][:5]), Colors.YELLOW)}")
        if pg.get("has_link_header_next"):
            p(f"    Link Header: {c('有 rel=\"next\"', Colors.GREEN)}")

    if "incremental" in report:
        ic = report["incremental"]
        p(f"\n  {c('[🔄 增量更新]', Colors.BOLD)}")
        p(f"    ETag: {c('✓ 支持' if ic.get('supports_etag') else '✗ 不支持', Colors.GREEN if ic.get('supports_etag') else Colors.DIM)}")
        p(f"    Last-Modified: {c('✓ 支持' if ic.get('supports_last_modified') else '✗ 不支持', Colors.GREEN if ic.get('supports_last_modified') else Colors.DIM)}")
        if ic.get("cache_control"):
            p(f"    Cache-Control: {c(ic['cache_control'], Colors.DIM)}")

    if "security_headers" in report:
        sh = report["security_headers"]
        p(f"\n  {c('[🔒 安全头分析]', Colors.BOLD)}")
        p(f"    CSP: {c(sh.get('csp') and '有设置' or '无', Colors.YELLOW if sh.get('csp') else Colors.DIM)}")
        p(f"    CORS: {c(sh.get('cors') or '未设置', Colors.DIM)}")
        p(f"    HSTS: {c('✓ 开启' if sh.get('hsts') else '✗ 关闭', Colors.GREEN if sh.get('hsts') else Colors.YELLOW)}")
        p(f"    X-Frame-Options: {c(sh.get('x_frame_options') or '未设置', Colors.DIM)}")
        if sh.get("cookie_http_only"):
            p(f"    HttpOnly Cookie: {c(', '.join(sh['cookie_http_only'][:5]), Colors.CYAN)}")

    if "design_analysis" in report:
        da = report["design_analysis"]
        p(f"\n  {c('[🎨 设计风格分析]', Colors.BOLD)}")
        ds = da.get("design_system", {})
        if ds.get("detected_framework") and ds["detected_framework"] != "custom":
            p(f"    设计框架: {c(ds['detected_framework'], Colors.MAGENTA)}")
        cp = da.get("color_palette", {})
        if cp.get("most_used"):
            p(f"    主色: {c(cp['most_used'][0]['color'], Colors.CYAN)} (出现 {cp['most_used'][0]['count']} 次)")
        if cp.get("backgrounds"):
            bg_colors = cp["backgrounds"][:3]
            p(f"    背景色: {c(', '.join(bg_colors), Colors.DIM)}")
        if cp.get("texts"):
            p(f"    文字色: {c(', '.join(cp['texts'][:3]), Colors.DIM)}")
        typo = da.get("typography", {})
        if typo.get("font_families"):
            p(f"    字体: {c(', '.join(typo['font_families'][:3]), Colors.CYAN)}")
        if typo.get("headings"):
            h1 = typo["headings"].get("h1", {})
            if h1:
                h1_size = h1.get("size", "")
                h1_weight = h1.get("weight", "")
                h1_label = f"{h1_size} / {h1_weight}"
                p(f"    h1: {c(h1_label, Colors.YELLOW)} {h1.get('family','')}")
        eff = da.get("effects", {})
        br = eff.get("border_radius", {})
        if br.get("all_values"):
            p(f"    圆角: {c(', '.join(br['all_values'][:4]), Colors.DIM)}")
        comps = da.get("components", {})
        if comps.get("buttons"):
            btn = comps["buttons"][0]
            p(f"    按钮示例: bg={c(btn.get('bg',''), Colors.CYAN)} radius={c(btn.get('radius',''), Colors.DIM)}")

    # ---- 原有 API 分析结果 ----
    p(f"\n  {c('[🎯 API 端点]', Colors.BOLD)}")
    api_eps = [e for e in report["api_endpoints"] if e["type"] != "Page Document"]
    if api_eps:
        for i, ep in enumerate(api_eps[:10], 1):
            mc = Colors.GREEN if ep["method"] == "GET" else (Colors.YELLOW if ep["method"] == "POST" else Colors.CYAN)
            sc = Colors.GREEN if ep["status"] and 200 <= ep["status"] < 300 else Colors.RED
            p(f"    #{i} {c(ep['method'], mc)} {c(str(ep['status'] or '-'), sc)} {c(ep['type'], Colors.MAGENTA)}")
            p(f"       {c(ep['url'][:120], Colors.DIM)}")
            if ep.get("request_body"):
                p(f"       Body: {safe_truncate(ep['request_body'], 150)}")
        if len(api_eps) > 10:
            p(f"    ... 还有 {len(api_eps) - 10} 个端点")
    else:
        p(f"    {c('未检测到 API 端点', Colors.YELLOW)}")

    # ---- JS Bundle 分析 ----
    if "js_bundle_analysis" in report:
        jb = report["js_bundle_analysis"]
        if jb.get("api_bundles_found", 0) > 0:
            p(f"\n  {c('[📦 JS Bundle 分析]', Colors.BOLD)}")
            p(f"    发现 {jb['api_bundles_found']} 个疑似 API Bundle")
            for b in jb.get("api_bundles", [])[:5]:
                p(f"    {c(b.get('filename','?'), Colors.CYAN)} ({b.get('size','?')})")
            if jb.get("extracted_queries"):
                p(f"    📜 提取到 {len(jb['extracted_queries'])} 个 GraphQL 查询")
                for q in jb["extracted_queries"][:3]:
                    p(f"      {c(q[:100], Colors.DIM)}")
            if jb.get("extracted_endpoints"):
                p(f"    🔗 发现 API 路径:")
                for ep in jb["extracted_endpoints"][:5]:
                    p(f"      {c(ep, Colors.CYAN)}")
            if jb.get("extracted_configs"):
                p(f"    ⚙️ 配置信息:")
                for cfg in jb["extracted_configs"][:5]:
                    p(f"      {c(cfg, Colors.YELLOW)}")

    # ---- GraphQL Schema ----
    if "graphql_schema" in report:
        gs = report["graphql_schema"]
        if gs.get("endpoints"):
            p(f"\n  {c('[🔮 GraphQL Schema]', Colors.BOLD)}")
            if gs.get("introspection_available"):
                schema = gs.get("schema", {})
                p(f"    {c('✅ Introspection 可用!', Colors.GREEN)}")
                p(f"    类型数量: {schema.get('types_count', 0)}")
                for t in schema.get("types", [])[:5]:
                    p(f"    {c(t['name'], Colors.CYAN)} ({t.get('fields_count', 0)} 字段)")
            else:
                p(f"    {c('⚠️ Introspection 不可用', Colors.YELLOW)}")
                if gs.get("inferred_operations"):
                    p(f"    从请求推断的操作:")
                    for op in gs["inferred_operations"][:8]:
                        p(f"      {c(op, Colors.GREEN)}")
                if gs.get("inferred_types"):
                    p(f"    推断的数据类型:")
                    for t in gs["inferred_types"][:5]:
                        fields = ', '.join(t.get('fields', [])[:6])
                        p(f"      {c(t['name'], Colors.CYAN)}: {fields}")

    # ---- WebSocket 消息 ----
    if "ws_messages" in report:
        wm = report["ws_messages"]
        if wm:
            p(f"\n  {c('[🔌 WebSocket 消息]', Colors.BOLD)}")
            p(f"    共 {len(wm)} 条消息")
            sent = sum(1 for m in wm if m.get("type") == "sent")
            recv = sum(1 for m in wm if m.get("type") == "received")
            p(f"    发送: {sent} 条 | 接收: {recv} 条")
            for m in wm[:3]:
                et = "→ 发送" if m.get("type") == "sent" else "← 接收"
                p(f"    {c(et, Colors.CYAN)} {m.get('payload','')[:150]}")

    # 表单
    if report.get("forms"):
        p(f"\n  {c(f'[📝 表单 ({len(report["forms"])} 个)]', Colors.BOLD)}")
        for f in report["forms"][:3]:
            hidden = [i for i in f["inputs"] if i["type"] == "hidden"]
            p(f"    Form #{f['index']}: action={c(f['action'] or '(无)', Colors.CYAN)} method={c(f['method'], Colors.GREEN)}")
            if hidden:
                hidden_items = [f'{h["name"]}={h["value"]}' for h in hidden[:5]]
            p(f"      隐藏: {'; '.join(hidden_items)}")

    # 技术栈
    if report.get("tech_stack"):
        p(f"\n  {c('[🏗️  技术栈]', Colors.BOLD)} {', '.join(report['tech_stack'])}")

    p()
    p(c(f"{'='*60}", Colors.GREEN))
    p(c(f"  ✅ 分析完成！使用 web_design_advisor.py 生成设计复刻方案", Colors.BOLD))
    p(c(f"{'='*60}", Colors.GREEN))
    p()


def export_json(report: dict, filepath: str):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"  {c('[💾]', Colors.GREEN)} JSON: {filepath}")


def export_markdown(report: dict, filepath: str):
    s = report["stats"]
    pi = report["page_info"]
    lines = [
        f"# Web 爬虫分析报告",
        f"",
        f"- **目标 URL**: {report['target_url']}",
        f"- **分析时间**: {report['analyzed_at']}",
        f"- **页面标题**: {pi.get('title', 'N/A')}",
        f"",
        f"## 概览",
        f"",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 总请求数 | {s['total_requests']} |",
        f"| API 端点 | {s['api_endpoints']} |",
        f"| 表单 | {s['forms_found']} |",
        f"| WebSocket | {s['websocket_connections']} |",
        f"| 技术栈 | {', '.join(s['tech_stack']) if s['tech_stack'] else '未检测'} |",
    ]

    if "preflight" in report:
        pf = report["preflight"]
        lines.extend([
            f"",
            f"## 预检分析",
            f"",
            f"- **Server**: {pf.get('server_tech') or '未知'}",
            f"- **robots.txt**: {'允许爬取' if pf.get('robots_allowed', True) else '⛔ 禁止爬取'}",
        ])
        if pf.get("robots_disallowed_paths"):
            lines.append(f"- **Disallow 路径**: {', '.join(pf['robots_disallowed_paths'][:5])}")
        if pf.get("crawl_delay"):
            lines.append(f"- **Crawl-delay**: {pf['crawl_delay']}秒")

    if "anti_scraping" in report:
        af = report["anti_scraping"]
        lines.extend([
            f"",
            f"## 反爬检测",
            f"",
            f"- **WAF**: {af.get('waf_detected') or '未检测到'}",
            f"- **CAPTCHA**: {'⚠️ 有' if af.get('has_captcha') else '✓ 无'}",
            f"- **需 JS**: {'是' if af.get('requires_js') else '否'}",
        ])

    if "rendering" in report:
        rd = report["rendering"]
        lines.extend([
            f"",
            f"## 渲染分析",
            f"",
            f"- **渲染模式**: {rd.get('mode', 'unknown').upper()}",
            f"- **数据位置**: {rd.get('data_location', 'unknown')}",
            f"- **推荐工具**: {rd.get('suggested_tool', 'Playwright')}",
        ])
        if rd.get("data_selectors"):
            lines.append(f"- **建议选择器**: {', '.join(rd['data_selectors'][:5])}")

    if "pagination" in report:
        pg = report["pagination"]
        lines.extend([
            f"",
            f"## 分页分析",
            f"",
            f"- **分页类型**: {pg.get('pagination_type', 'none')}",
        ])
        if pg.get("url_params"):
            lines.append(f"- **URL 参数**: {', '.join(pg['url_params'])}")

    if "incremental" in report:
        ic = report["incremental"]
        lines.extend([
            f"",
            f"## 增量更新",
            f"",
            f"- **ETag**: {'✓' if ic.get('supports_etag') else '✗'}",
            f"- **Last-Modified**: {'✓' if ic.get('supports_last_modified') else '✗'}",
        ])

    # API 端点
    lines.extend([f"", f"## API 端点", f"", f"| # | 方法 | 状态 | 类型 | URL |",
                  f"|---|------|------|------|-----|"])
    api_eps = [e for e in report["api_endpoints"] if e["type"] != "Page Document"]
    for i, ep in enumerate(api_eps, 1):
        lines.append(f"| {i} | {ep['method']} | {ep.get('status', '-')} | {ep['type']} | `{ep['url'][:120]}` |")

    if report.get("forms"):
        lines.extend([f"", f"## 表单", f"", f"| # | Action | Method | 隐藏字段 |",
                      f"|---|--------|--------|----------|"])
        for f in report["forms"]:
            hidden = "; ".join(f"{i['name']}={i['value']}" for i in f["inputs"]
                              if i["type"] == "hidden" and i["value"]) or "-"
            lines.append(f"| {f['index']} | `{f['action'] or '-'}` | {f['method']} | {hidden} |")

    lines.extend(["", "---", "*由 🐱 Web Scraping Analyzer v2 自动生成*"])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  {c('[💾]', Colors.GREEN)} Markdown: {filepath}")


# ──────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="🐱 Web Scraping Analyzer - 网页爬虫前期分析工具 v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  %(prog)s https://example.com
  %(prog)s https://example.com -o report.json -w 10
  %(prog)s https://example.com --scrape-mode    # 完整爬虫分析 (默认)
  %(prog)s https://example.com --no-scrape      # 仅 API 分析
  %(prog)s https://example.com --cookie "token=abc123"
  %(prog)s https://example.com --json-only | python web_scraping_advisor.py --stdin
        """,
    )
    parser.add_argument("url", help="目标网页 URL")
    parser.add_argument("-o", "--output", help="导出 JSON 报告 (.json)")
    parser.add_argument("-m", "--markdown", help="导出 Markdown 报告 (.md)")
    parser.add_argument("-w", "--wait", type=int, default=5,
                        help="页面加载后等待秒数 (默认: 5)")
    parser.add_argument("--interactive", action="store_true",
                        help="交互模式，手动操作后再捕获")
    parser.add_argument("--no-headless", action="store_true",
                        help="显示浏览器窗口")
    parser.add_argument("--cookie", default="",
                        help="Cookie, 格式: key1=val1;key2=val2")
    parser.add_argument("--screenshot", action="store_true",
                        help="保存截图")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="实时显示所有请求")
    parser.add_argument("--json-only", action="store_true",
                        help="只输出 JSON 到 stdout")
    scrape_group = parser.add_mutually_exclusive_group()
    scrape_group.add_argument("--scrape-mode", action="store_true", default=True,
                              help="完整爬虫前期分析 (默认)")
    scrape_group.add_argument("--no-scrape", action="store_true", dest="no_scrape",
                              help="仅基础 API 分析 (不分析反爬/渲染等)")

    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        args.url = "https://" + args.url

    analyzer = WebAnalyzer(
        url=args.url,
        headless=not args.no_headless,
        wait_time=args.wait,
        interactive=args.interactive,
        cookie_str=args.cookie,
        save_screenshot=args.screenshot,
        verbose=args.verbose,
        json_only=args.json_only,
        scrape_mode=not args.no_scrape,
    )

    report = analyzer.run()

    if args.json_only:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        return

    print_report(report)

    if args.output:
        export_json(report, args.output)
    if args.markdown:
        export_markdown(report, args.markdown)

    if not args.output and not args.markdown:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_json(report, f"api_report_{ts}.json")
        export_markdown(report, f"api_report_{ts}.md")


if __name__ == "__main__":
    main()
