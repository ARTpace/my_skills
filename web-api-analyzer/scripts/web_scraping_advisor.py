#!/usr/bin/env python3
"""
爬虫策略生成器 —— Web Scraping Advisor
===========================================
读取 WebAnalyzer 的分析报告，综合所有检测结果，
自动生成爬虫实施策略、技术选型、代码模板和风险评估。

使用方式：
  # 读取已生成的报告
  python web_scraping_advisor.py report.json

  # 管道模式（一行完成）
  python web_api_analyzer.py URL --json-only | python web_scraping_advisor.py --stdin

  # 保存策略
  python web_scraping_advisor.py report.json -o scraping_plan.md

版本: 1.0.0
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


class ScrapingAdvisor:
    """爬虫策略生成器"""

    def __init__(self, report: dict):
        self.report = report
        self.stats = report.get("stats", {})
        self.page_info = report.get("page_info", {})

    # ══════════════════════════════════════════════════════
    # 风险评估
    # ══════════════════════════════════════════════════════
    def assess_risk(self) -> dict:
        """综合评估爬取风险等级"""
        score = 0
        factors = []

        af = self.report.get("anti_scraping", {})

        # WAF
        if af.get("waf_detected"):
            score += 30
            factors.append(f"⛔ WAF 防火墙: {af['waf_detected']}")

        # CAPTCHA
        if af.get("has_captcha"):
            score += 25
            factors.append("⛔ 有验证码 (CAPTCHA)")

        # Rate limit
        rl = af.get("rate_limit_statuses", [])
        if rl:
            score += min(len(rl) * 5, 20)
            factors.append(f"⚠️ 检测到 Rate Limit ({len(rl)} 次)")

        # 浏览器指纹
        if af.get("has_browser_fingerprint"):
            score += 15
            factors.append("⚠️ 有浏览器指纹检测")

        # JS 必要性
        if af.get("requires_js"):
            score += 5
            factors.append("⚠️ 需要 JS 执行")

        # 渲染模式
        rd = self.report.get("rendering", {})
        mode = rd.get("mode", "unknown")
        if mode == "spa":
            score += 5
            factors.append("📱 SPA 单页应用 (需处理路由)")
        if mode == "csr":
            score += 3

        # Cookie necessity
        cookies = self.report.get("cookies", [])
        if cookies:
            has_session = any(
                "session" in c.get("name", "").lower()
                or "token" in c.get("name", "").lower()
                for c in cookies
            )
            if has_session:
                score += 10
                factors.append("🔑 需要 Session/Token 管理")

        # 鉴权
        eps = self.report.get("api_endpoints", [])
        has_auth_eps = any(
            any(p in e.get("url", "").lower() for p in ("/login", "/auth", "/token"))
            for e in eps
        )
        if has_auth_eps:
            score += 10
            factors.append("🔐 需要先登录获取凭证")

        if score == 0:
            level = "⚪ 无风险"
            summary = "网站对爬虫友好，可直接使用简单工具爬取"
        elif score <= 20:
            level = "🟢 低风险"
            summary = "有基本防护，控制好频率即可"
        elif score <= 40:
            level = "🟡 中风险"
            summary = "需要一定的反爬对抗能力，建议用浏览器自动化"
        elif score <= 60:
            level = "🟠 较高风险"
            summary = "反爬较强，需要代理池 + 浏览器自动化"
        else:
            level = "🔴 高风险"
            summary = "反爬非常严格，实施成本较高"

        return {
            "score": score,
            "level": level,
            "summary": summary,
            "factors": factors,
        }

    # ══════════════════════════════════════════════════════
    # 技术选型
    # ══════════════════════════════════════════════════════
    def recommend_tools(self) -> dict:
        """推荐爬虫工具和库"""
        rd = self.report.get("rendering", {})
        af = self.report.get("anti_scraping", {})
        risk = self.assess_risk()
        mode = rd.get("mode", "unknown")
        data_loc = rd.get("data_location", "unknown")

        tools = []
        scraping_framework = ""
        http_client = ""
        data_parser = ""
        proxy_strategy = ""
        notes = []

        # 根据渲染模式 + 数据位置推荐
        if data_loc == "api" or data_loc == "script_json":
            http_client = "requests"
            data_parser = "json (内置)"
            scraping_framework = "纯 requests 脚本"
            notes.append("数据直接来自 API，无需渲染页面")
        elif mode == "ssr" or data_loc == "html":
            http_client = "requests"
            data_parser = "BeautifulSoup + lxml"
            scraping_framework = "requests + BeautifulSoup"
            notes.append("数据在 HTML 中，用 CSS Selector / XPath 提取")
        elif mode in ("csr", "spa") or af.get("waf_detected"):
            http_client = "httpx (支持 HTTP/2)"
            data_parser = "BeautifulSoup + lxml 或 Playwright"
            scraping_framework = "Playwright / Scrapy + Playwright"
            notes.append("需要浏览器渲染或调 API")
        else:
            http_client = "requests"
            data_parser = "BeautifulSoup"
            scraping_framework = "requests + BeautifulSoup"

        # 代理策略
        if risk["score"] > 30:
            proxy_strategy = "✅ 推荐使用代理池 / 住宅代理"
            if risk["score"] > 50:
                proxy_strategy += "\n   ✅ 建议轮换 User-Agent + 随机延迟 (2-5s)"
        else:
            proxy_strategy = "✅ 基本不需要代理，注意请求间隔即可"

        # 反爬对抗
        if af.get("has_captcha"):
            notes.append("需接入 CAPTCHA 识别服务 (2captcha / 打码平台)")
        if af.get("has_browser_fingerprint"):
            notes.append("建议使用 undetected-chromedriver 或 Playwright stealth")
        if risk["score"] > 40:
            notes.append("建议分布式爬取，分散 IP 和请求时间")

        # 增量更新
        ic = self.report.get("incremental", {})
        if ic.get("supports_etag") or ic.get("supports_last_modified"):
            notes.append("支持增量更新，可大幅减少请求量")
            scraping_framework += " (支持增量)"

        # 分页
        pg = self.report.get("pagination", {})
        if pg.get("pagination_type") != "none":
            notes.append(f"分页类型: {pg['pagination_type']}")

        # 最终推荐
        if risk["score"] <= 20:
            tools = ["requests", "BeautifulSoup", "lxml"]
        elif risk["score"] <= 40:
            tools = ["requests / httpx", "BeautifulSoup", "playwright (备用)"]
        else:
            tools = ["playwright", "scrapy", "fake-useragent", "代理池"]

        return {
            "tools": tools,
            "http_client": http_client,
            "data_parser": data_parser,
            "framework": scraping_framework,
            "proxy_strategy": proxy_strategy,
            "notes": notes,
        }

    # ══════════════════════════════════════════════════════
    # 代码模板生成
    # ══════════════════════════════════════════════════════
    def generate_code_template(self) -> str:
        """根据分析结果生成爬虫代码模板"""
        eps = [e for e in self.report.get("api_endpoints", []) if e["type"] != "Page Document"]
        rd = self.report.get("rendering", {})
        af = self.report.get("anti_scraping", {})
        pg = self.report.get("pagination", {})
        ic = self.report.get("incremental", {})
        forms = self.report.get("forms", [])
        url = self.report.get("target_url", "")
        parsed = urllib.parse.urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        # 提取关键 headers
        ref_headers = {}
        for ep in eps[:3]:
            h = ep.get("request_headers", {})
            for k in ("User-Agent", "Accept", "Accept-Language", "Referer", "Origin",
                       "Authorization", "X-CSRF-Token", "X-Requested-With", "Content-Type"):
                if k in h or k.lower() in h:
                    actual_k = k if k in h else k.lower()
                    ref_headers[actual_k] = h[actual_k]
            if ref_headers:
                break

        # 提取 Cookie
        cookies = self.report.get("cookies", [])
        cookie_dict = {c.get("name", ""): c.get("value", "") for c in cookies if c.get("name")}

        # 提取认证端点
        auth_eps = [e for e in eps if any(
            p in e.get("url", "").lower() for p in ("/login", "/auth", "/signin", "/token")
        )]

        # 拼装代码
        lines = ['"""', f"爬虫脚本 — {self.page_info.get('title', '')}", f"目标: {url}",
                 f"生成时间: {datetime.now().isoformat()}", '"""', ""]

        # imports
        lines.extend([
            "import requests",
            "import json",
            "import time",
            "import random",
            "from bs4 import BeautifulSoup",
            "",
        ])

        # 配置
        lines.append("# ===== 配置 ===== ")
        if ref_headers:
            lines.append(f"HEADERS = {json.dumps(ref_headers, ensure_ascii=False, indent=2)}")
        else:
            lines.append(textwrap.dedent("""\
            HEADERS = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/json,*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
            }"""))

        lines.append("")
        lines.append(f"BASE_URL = {json.dumps(base)}")
        lines.append("")

        # 分页
        if pg.get("pagination_type") != "none":
            lines.append("# ===== 分页配置 =====")
            params = pg.get("url_params", [])
            if "page" in params:
                lines.append('PAGE_PARAM = "page"')
            elif "offset" in params:
                lines.append('PAGE_PARAM = "offset"')
            else:
                lines.append('PAGE_PARAM = "page"  # 请根据实际情况修改')

            if "limit" in params or "per_page" in params:
                key = "limit" if "limit" in params else "per_page"
                lines.append(f'LIMIT_PARAM = "{key}"')
                lines.append("PAGE_SIZE = 20  # 请根据实际情况修改")
            lines.append("")

        # Cookie / Session
        lines.append("# ===== Session =====")
        lines.append("session = requests.Session()")
        lines.append("session.headers.update(HEADERS)")
        if cookie_dict:
            lines.append("# 预置 Cookie")
            for name, value in list(cookie_dict.items())[:5]:
                lines.append(f"session.cookies.set('{name}', '{value}')")
        lines.append("")

        # 认证
        if auth_eps:
            ae = auth_eps[0]
            lines.append("# ===== 认证 =====")
            lines.append("def login(username, password):")
            lines.append('    """登录获取凭证"""')
            lines.append(f'    url = "{ae["url"]}"')
            lines.append("    data = {")
            lines.append('        "username": username,')
            lines.append('        "password": password,')
            lines.append("    }")
            lines.append("    resp = session.post(url, headers=HEADERS, json=data)")
            lines.append("    resp.raise_for_status()")
            lines.append("    return resp.json()")
            lines.append("")

        # 主抓取函数
        if pg.get("pagination_type") != "none":
            lines.append("# ===== 数据抓取（分页） =====")
            target_eps = [e for e in eps if e.get("method") == "GET" and e["type"] != "Page Document"]
            target_url = target_eps[0]["url"] if target_eps else f"{base}/api/data"
            lines.append(f'FETCH_URL = "{target_url}"')
            lines.append("")
            lines.append("def fetch_page(page=1):")
            lines.append('    """获取一页数据"""')
            lines.append("    params = {PAGE_PARAM: page}")
            if "limit" in params or "per_page" in params:
                lines.append("    params[LIMIT_PARAM] = PAGE_SIZE")
            lines.append("    resp = session.get(FETCH_URL, headers=HEADERS, params=params)")
            lines.append("    resp.raise_for_status()")
            lines.append("    return resp.json()")
            lines.append("")
            lines.append("def fetch_all():")
            lines.append('    """获取所有页数据"""')
            lines.append("    all_data = []")
            lines.append("    page = 1")
            lines.append("    while True:")
            lines.append("        try:")
            lines.append("            data = fetch_page(page)")
            lines.append("            if not data:")
            lines.append("                break")
            lines.append("            all_data.extend(data)")

            # 根据分页字段智能判断
            resp_fields = pg.get("response_fields", [])
            if "has_more" in resp_fields or "hasMore" in resp_fields:
                lines.append("            if not data.get('has_more', True):")
                lines.append("                break")
            elif "total" in resp_fields or "total_count" in resp_fields:
                lines.append("            # 检查总数")
                lines.append("            total = data.get('total', 0) or data.get('total_count', 0)")
                lines.append("            if len(all_data) >= total:")
                lines.append("                break")
            else:
                lines.append("            if len(data) == 0:")
                lines.append("                break")

            lines.append("            page += 1")
            lines.append(f"            time.sleep(random.uniform(1, 3))  # 礼貌延迟")
            lines.append("        except Exception as e:")
            lines.append("            print(f'第{page}页失败: {e}')")
            lines.append("            break")
            lines.append("    return all_data")
            lines.append("")
            lines.append("if __name__ == '__main__':")
            lines.append("    result = fetch_all()")
            lines.append("    print(f'共获取 {len(result)} 条数据')")
            lines.append("    # 保存到文件")
            lines.append("    with open('data.json', 'w', encoding='utf-8') as f:")
            lines.append("        json.dump(result, f, ensure_ascii=False, indent=2)")
            lines.append("    print('数据已保存到 data.json'")
        else:
            # 单一请求
            target_eps = [e for e in eps if e.get("method") == "GET" and e["type"] != "Page Document"]
            target_url = target_eps[0]["url"] if target_eps else base
            lines.append("# ===== 数据抓取 =====")
            lines.append(f'FETCH_URL = "{target_url}"')
            lines.append("")
            lines.append("def fetch_data():")
            lines.append("    resp = session.get(FETCH_URL, headers=HEADERS)")
            lines.append("    resp.raise_for_status()")
            lines.append("    return resp.json()")
            lines.append("")
            lines.append("if __name__ == '__main__':")
            lines.append("    data = fetch_data()")
            lines.append("    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])")

        # 增量更新
        if ic.get("supports_etag") or ic.get("supports_last_modified"):
            lines.extend([
                "",
                "# ===== 增量更新 =====",
                "CACHE_FILE = 'cache.json'",
                "",
                "def load_cache():",
                "    try:",
                "        with open(CACHE_FILE) as f:",
                "            return json.load(f)",
                "    except (FileNotFoundError, json.JSONDecodeError):",
                "        return {}",
                "",
                "def save_cache(etag, data):",
                "    with open(CACHE_FILE, 'w') as f:",
                "        json.dump({'etag': etag, 'data': data, 'updated_at': ",
                "                  datetime.now().isoformat()}, f)",
                "",
                "def fetch_with_cache():",
                "    cache = load_cache()",
                "    headers = HEADERS.copy()",
            ])
            if ic.get("etag_values"):
                lines.append(f'    headers["If-None-Match"] = cache.get("etag", "")')
            lines.extend([
                "    resp = session.get(FETCH_URL, headers=headers)",
                "    if resp.status_code == 304:",
                "        print('数据无变化，使用缓存')",
                "        return cache.get('data', [])",
                "    data = resp.json()",
                "    etag = resp.headers.get('ETag', '')",
                "    save_cache(etag, data)",
                "    return data",
            ])

        lines.append("")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════
    # 执行建议
    # ══════════════════════════════════════════════════════
    def execution_plan(self) -> dict:
        """生成执行计划建议"""
        risk = self.assess_risk()
        rd = self.report.get("rendering", {})
        af = self.report.get("anti_scraping", {})

        # 推荐频率
        if risk["score"] <= 10:
            freq = "每 0.5-1 秒 1 个请求"
        elif risk["score"] <= 30:
            freq = "每 1-3 秒 1 个请求"
        elif risk["score"] <= 50:
            freq = "每 3-5 秒 1 个请求，使用代理"
        else:
            freq = "每 5-10 秒 1 个请求，必须使用代理池"

        # 预估
        pf = self.report.get("preflight", {})
        delay = pf.get("crawl_delay", 0) or 1
        rec_delay = max(delay, 1)

        data_loc = rd.get("data_location", "unknown")
        if data_loc == "api":
            speed = "快 (直接调 API)"
        elif data_loc == "script_json":
            speed = "较快 (提取 JSON)"
        elif data_loc == "html":
            speed = "中等 (解析 HTML)"
        else:
            speed = "慢 (需要浏览器)"

        # 反爬对抗策略
        strategies = []
        if af.get("waf_detected"):
            strategies.append(f"绕过 {af['waf_detected']} WAF（使用真实浏览器指纹）")
        if af.get("has_captcha"):
            strategies.append("集成 CAPTCHA 识别服务")
        if af.get("has_browser_fingerprint"):
            strategies.append("使用 undetected-chromedriver 或 Playwright stealth 模式")
        if risk["score"] > 30:
            strategies.append("使用代理池，轮换 IP")
            strategies.append("随机 User-Agent + 随机延迟")
        if af.get("requires_cookie", False) is True:
            strategies.append("维护 Cookie/Session 会话")
        if not strategies:
            strategies.append("无需特殊处理")

        return {
            "recommended_frequency": freq,
            "recommended_delay": rec_delay,
            "estimated_speed": speed,
            "strategies": strategies,
        }

    # ══════════════════════════════════════════════════════
    # 完整报告
    # ══════════════════════════════════════════════════════
    def generate_full_report(self) -> str:
        """生成完整的爬虫方案报告"""
        risk = self.assess_risk()
        tools = self.recommend_tools()
        code = self.generate_code_template()
        plan = self.execution_plan()

        rd = self.report.get("rendering", {})
        af = self.report.get("anti_scraping", {})
        pg = self.report.get("pagination", {})
        ic = self.report.get("incremental", {})
        url = self.report.get("target_url", "")

        lines = [
            f"# 🕷️ 爬虫方案报告",
            f"",
            f"**目标**: {url}",
            f"**页面**: {self.page_info.get('title', 'N/A')}",
            f"**生成时间**: {datetime.now().isoformat()}",
            f"",
            f"---",
            f"",
            f"## 1. 📊 风险评估",
            f"",
            f"| 指标 | 结果 |",
            f"|------|------|",
            f"| 风险等级 | {risk['level']} |",
            f"| 风险分数 | {risk['score']}/100 |",
            f"| 概要 | {risk['summary']} |",
            f"",
        ]
        if risk["factors"]:
            lines.append("**风险因素**:")
            for f in risk["factors"]:
                lines.append(f"- {f}")
            lines.append("")

        lines.extend([
            f"## 2. 🛠️ 技术选型",
            f"",
            f"| 组件 | 推荐 |",
            f"|------|------|",
            f"| 爬虫框架 | {tools['framework']} |",
            f"| HTTP 客户端 | {tools['http_client']} |",
            f"| 数据解析 | {tools['data_parser']} |",
            f"| 代理策略 | {tools['proxy_strategy']} |",
            f"",
        ])
        if tools["notes"]:
            lines.append("**注意事项**:")
            for n in tools["notes"]:
                lines.append(f"- {n}")
            lines.append("")

        lines.extend([
            f"## 3. 🔄 执行计划",
            f"",
            f"| 维度 | 建议 |",
            f"|------|------|",
            f"| 请求频率 | {plan['recommended_frequency']} |",
            f"| 预期速度 | {plan['estimated_speed']} |",
            f"| 推荐延迟 | {plan['recommended_delay']}秒 |",
            f"",
            f"**反爬对抗策略**:",
        ])
        for s in plan["strategies"]:
            lines.append(f"- {s}")

        lines.extend([
            f"",
            f"## 4. 🔬 技术细节",
            f"",
            f"### 渲染模式",
            f"- **模式**: {rd.get('mode', 'unknown').upper()}",
            f"- **数据位置**: {rd.get('data_location', 'unknown')}",
            f"- **推荐工具**: {rd.get('suggested_tool', 'Playwright')}",
            f"",
            f"### 反爬检测",
            f"- **WAF**: {af.get('waf_detected') or '未检测到'}",
            f"- **验证码**: {'⚠️ 有' if af.get('has_captcha') else '✓ 无'}",
            f"- **浏览器指纹**: {'⚠️ 有' if af.get('has_browser_fingerprint') else '✓ 无'}",
            f"- **需要 JS**: {'是' if af.get('requires_js') else '否'}",
            f"",
            f"### 分页分析",
            f"- **类型**: {pg.get('pagination_type', 'none')}",
            f"- **URL 参数**: {', '.join(pg.get('url_params', [])) or '无'}",
            f"- **响应字段**: {', '.join(pg.get('response_fields', [])) or '无'}",
            f"",
            f"### 增量更新",
            f"- **ETag**: {'✓' if ic.get('supports_etag') else '✗'}",
            f"- **Last-Modified**: {'✓' if ic.get('supports_last_modified') else '✗'}",
            f"- **Cache-Control**: {ic.get('cache_control') or '未设置'}",
            f"",
            f"## 5. 💻 代码模板",
        ])
        lines.append("")
        lines.append("```python")
        lines.append(code)
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("*由 🐱 Web Scraping Advisor 自动生成*")

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="🐱 Web Scraping Advisor - 爬虫策略生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  %(prog)s report.json
  %(prog)s report.json -o scraping_plan.md
  python web_api_analyzer.py URL --json-only | %(prog)s --stdin
        """,
    )
    parser.add_argument("input", nargs="?",
                        help="分析报告 JSON 文件")
    parser.add_argument("--stdin", action="store_true",
                        help="从 stdin 读取报告")
    parser.add_argument("-o", "--output",
                        help="输出到文件 (.md)")
    parser.add_argument("--code-only", action="store_true",
                        help="只输出代码模板")

    args = parser.parse_args()

    # 读取报告
    report = None
    if args.stdin:
        try:
            report = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.input:
        try:
            with open(args.input, encoding="utf-8") as f:
                report = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ 读取失败: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        print("\n请指定报告文件路径或 --stdin")
        sys.exit(1)

    advisor = ScrapingAdvisor(report)

    if args.code_only:
        output = advisor.generate_code_template()
        print(output)
        return

    report_text = advisor.generate_full_report()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"💾 爬虫方案已保存: {args.output}")
    else:
        print(report_text)


if __name__ == "__main__":
    main()
