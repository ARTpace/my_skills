#!/usr/bin/env python3
"""
🐱 Web Analyzer Interactive CLI — 交互式网页分析工具
=====================================================
终端交互菜单，让你选择要分析的内容。

使用方式：
  python web_interactive_cli.py
  python web_interactive_cli.py https://example.com

版本: 1.0.0
"""

import json
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COLORS = {
    "GREEN": "\033[92m", "YELLOW": "\033[93m", "CYAN": "\033[96m",
    "RED": "\033[91m", "MAGENTA": "\033[95m", "BOLD": "\033[1m",
    "DIM": "\033[2m", "RESET": "\033[0m",
}


def c(text, color):
    return f"{COLORS[color]}{text}{COLORS['RESET']}"


def print_banner():
    print()
    print(c("  ╔══════════════════════════════════════╗", "CYAN"))
    print(c("  ║     🐱 Web Analyzer Interactive      ║", "CYAN"))
    print(c("  ║     网页全维度分析工具  v3.1          ║", "CYAN"))
    print(c("  ╚══════════════════════════════════════╝", "CYAN"))
    print()


def show_menu():
    """展示交互菜单"""
    print(c("  主人想分析这个网站的什么呢？喵～ 🐱", "BOLD"))
    print()
    print(f"  {c('①', 'GREEN')}  {c('完整全面分析', 'BOLD')}")
    print("     API接口 + 爬虫分析 + 设计风格，一次看完所有信息")
    print()
    print(f"  {c('②', 'YELLOW')}  {c('爬虫前期分析', 'BOLD')}")
    print("     预检/反爬/渲染/分页/增量/安全，生成爬虫策略和代码")
    print()
    print(f"  {c('③', 'CYAN')}  {c('API 接口分析', 'BOLD')}")
    print("     拦截网络请求，提取所有API端点、参数、鉴权方式")
    print()
    print(f"  {c('④', 'MAGENTA')}  {c('设计风格分析', 'BOLD')}")
    print("     提取色彩/字体/组件/布局/动效，生成复刻方案")
    print()
    print(f"  {c('⑤', 'DIM')}  {c('快速概览', 'BOLD')}")
    print("     5秒快速扫描，了解网站基本情况")
    print()
    print(f"  {c('q', 'RED')}  {c('退出', 'BOLD')}")
    print()

    while True:
        choice = input(c("  请选择 [1-5/q]: ", "YELLOW")).strip().lower()
        if choice in ("1", "2", "3", "4", "5", "q"):
            return choice
        print(c("  输入无效，请重新选择", "RED"))


def get_url():
    """获取目标 URL"""
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input(c("  请输入目标网址: ", "YELLOW")).strip()

    if not url:
        print(c("  ❌ 请输入网址", "RED"))
        sys.exit(1)

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def run_analyzer(url, wait=5):
    """运行分析引擎"""
    print(f"\n  {c('[⚡]', 'YELLOW')} 正在分析: {c(url, 'CYAN')}")
    print(f"  {c('  请稍候...', 'DIM')}")
    print()

    script = os.path.join(SCRIPT_DIR, "web_api_analyzer.py")
    result = subprocess.run(
        [sys.executable, script, url, "--json-only", "-w", str(wait)],
        capture_output=True, text=True, timeout=120,
    )

    if result.returncode != 0:
        print(c(f"  ❌ 分析失败: {result.stderr[:500]}", "RED"))
        sys.exit(1)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(c(f"  ❌ JSON 解析失败: {e}", "RED"))
        print(c(f"  stderr: {result.stderr[:200]}", "DIM"))
        sys.exit(1)


def run_scraping_advisor(report):
    """生成爬虫方案"""
    print(f"\n  {c('[🕷️]', 'YELLOW')} 生成爬虫方案...")
    script = os.path.join(SCRIPT_DIR, "web_scraping_advisor.py")
    result = subprocess.run(
        [sys.executable, script, "--stdin"],
        input=json.dumps(report, ensure_ascii=False),
        capture_output=True, text=True, timeout=30,
    )
    print(result.stdout)
    if result.stderr:
        print(c(f"  stderr: {result.stderr[:200]}", "DIM"))


def run_design_advisor(report):
    """生成设计复刻方案"""
    print(f"\n  {c('[🎨]', 'MAGENTA')} 生成设计复刻方案...")
    script = os.path.join(SCRIPT_DIR, "web_design_advisor.py")
    result = subprocess.run(
        [sys.executable, script, "--stdin", "--all"],
        input=json.dumps(report, ensure_ascii=False),
        capture_output=True, text=True, timeout=30,
    )
    print(result.stdout)
    if result.stderr:
        print(c(f"  stderr: {result.stderr[:200]}", "DIM"))


def print_quick_overview(report):
    """打印快速概览"""
    s = report.get("stats", {})
    pi = report.get("page_info", {})
    pf = report.get("preflight", {})
    af = report.get("anti_scraping", {})
    rd = report.get("rendering", {})
    da = report.get("design_analysis", {})
    eps = [e for e in report.get("api_endpoints", []) if e["type"] != "Page Document"]

    print()
    print(c("  ══════════════════════════════════════", "GREEN"))
    print(c("   ⚡ 快速概览", "BOLD"))
    print(c("  ══════════════════════════════════════", "GREEN"))

    print(f"\n  📄 页面: {c(pi.get('title', 'N/A'), 'CYAN')}")
    print(f"  📊 请求: {s.get('total_requests', 0)}次 | "
          f"🎯 API: {s.get('api_endpoints', 0)}个 | "
          f"📝 表单: {s.get('forms_found', 0)}个")
    print(f"  🏗️  技术栈: {c(', '.join(s.get('tech_stack', [])) or '未检测', 'MAGENTA')}")

    if pf:
        print(f"  🖥️  服务器: {c(pf.get('server_tech') or '未知', 'DIM')}")
        print(f"  🤖 robots: {c('允许' if pf.get('robots_allowed', True) else '禁止', 'GREEN' if pf.get('robots_allowed', True) else 'RED')}")

    if af.get("waf_detected"):
        print(f"  🛡️  WAF: {c(af['waf_detected'], 'RED')}")

    if rd.get("mode") and rd["mode"] != "unknown":
        print(f"  🎨 渲染模式: {c(rd['mode'].upper(), 'CYAN')} | "
              f"推荐: {c(rd.get('suggested_tool', '?'), 'GREEN')}")

    if eps:
        print(f"\n  {c('🎯 前5个API端点:', 'BOLD')}")
        for i, ep in enumerate(eps[:5], 1):
            print(f"    {c(ep['method'], 'GREEN')} {ep['url'][:100]}")

    cp = da.get("color_palette", {})
    if cp.get("most_used"):
        print(f"\n  🎨 主色: {c(cp['most_used'][0]['color'], 'CYAN')}")

    print()
    print(c("  提示: 使用 --full 查看完整报告", "DIM"))
    print()


def run_interactive():
    """交互式主流程"""
    print_banner()
    url = get_url()
    parsed = urllib.parse.urlparse(url)

    print()
    print(c(f"  🌐 目标: {url}", "CYAN"))
    print(c(f"  🏠 域名: {parsed.netloc}", "YELLOW"))
    print()

    choice = show_menu()

    if choice == "q":
        print(c("\n  拜拜喵～ 🐱", "CYAN"))
        return

    print()
    print(c("  ══════════════════════════════════════", "GREEN"))
    print(c(f"  开始分析...", "BOLD"))
    print(c("  ══════════════════════════════════════", "GREEN"))

    if choice in ("1", "2", "3", "4"):
        report = run_analyzer(url)

    if choice == "1":  # 完整全面
        run_scraping_advisor(report)
        run_design_advisor(report)

    elif choice == "2":  # 爬虫分析
        run_scraping_advisor(report)

    elif choice == "3":  # API分析
        eps = [e for e in report.get("api_endpoints", []) if e["type"] != "Page Document"]
        print(f"\n  {c(f'[🎯]', 'CYAN')} 发现 {len(eps)} 个 API 端点")
        print()
        if eps:
            for i, ep in enumerate(eps[:15], 1):
                mc = "GREEN" if ep["method"] == "GET" else ("YELLOW" if ep["method"] == "POST" else "CYAN")
                sc = "GREEN" if ep.get("status") and 200 <= ep["status"] < 300 else "RED"
                print(f"  {c(f'#{i}', 'DIM')} {c(ep['method'], mc)} {c(str(ep.get('status','?')), sc)} {c(ep.get('type',''), 'MAGENTA')}")
                print(f"     {c(ep['url'][:120], 'DIM')}")

        forms = report.get("forms", [])
        if forms:
            print(f"\n  {c(f'[📝]', 'YELLOW')} {len(forms)} 个表单")
            for f in forms[:3]:
                hidden = [i for i in f.get("inputs", []) if i["type"] == "hidden"]
                print(f"     Form #{f['index']}: action={c(f.get('action','?'), 'CYAN')}")
                if hidden:
                    print(f"       隐藏字段: {len(hidden)} 个")

    elif choice == "4":  # 设计分析
        run_design_advisor(report)

    elif choice == "5":  # 快速概览
        report = run_analyzer(url, wait=3)
        print_quick_overview(report)

    print()
    print(c("  ✅ 分析完成！", "BOLD"))
    print(c(f"  💡 使用 python {os.path.basename(__file__)} 重新分析", "DIM"))
    print()


def main():
    try:
        run_interactive()
    except KeyboardInterrupt:
        print(c("\n\n  拜拜喵～ 🐱", "CYAN"))
    except Exception as e:
        print(c(f"\n  ❌ 发生错误: {e}", "RED"))


if __name__ == "__main__":
    main()
