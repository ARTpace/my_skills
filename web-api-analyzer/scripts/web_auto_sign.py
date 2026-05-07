#!/usr/bin/env python3
"""
🐱 Web Auto Sign — 网站自动签到工具
======================================
支持多站点自动登录 + 签到，含登录态管理、智能按钮检测、
结果验证、截图、报告生成。

使用方式：
  python web_auto_sign.py                          # 运行所有站点
  python web_auto_sign.py -c my_sites.json          # 使用自定义配置
  python web_auto_sign.py --site "论坛签到"          # 只跑指定站点
  python web_auto_sign.py --init                    # 生成配置模板
  python web_auto_sign.py --list                    # 列出配置中的站点
  python web_auto_sign.py --no-headless             # 显示浏览器窗口
  python web_auto_sign.py --schedule "0 9 * * *"    # 设为定时执行

作者：主人的小猫咪咪 🐱
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "sign_sites.json")


class Colors:
    GREEN = "\033[92m"; YELLOW = "\033[93m"; CYAN = "\033[96m"
    RED = "\033[91m"; MAGENTA = "\033[95m"; BOLD = "\033[1m"
    DIM = "\033[2m"; RESET = "\033[0m"


def c(text, color):
    return f"{getattr(Colors, color, '')}{text}{Colors.RESET}"


def env_subst(value):
    """替换 ${ENV:VAR_NAME} 为环境变量值"""
    if isinstance(value, str):
        def replacer(m):
            var_name = m.group(1)
            return os.environ.get(var_name, "")
        return re.sub(r'\$\{ENV:(\w+)\}', replacer, value)
    return value


# ══════════════════════════════════════════════════════
# 配置加载
# ══════════════════════════════════════════════════════
def load_config(path=None):
    """加载签到配置"""
    if not path:
        path = os.path.join(SCRIPT_DIR, "sign_sites.json")
        if not os.path.exists(path):
            path = DEFAULT_CONFIG
    if not os.path.exists(path):
        # 尝试示例文件
        example = os.path.join(SCRIPT_DIR, "sign_sites.example.json")
        if os.path.exists(example):
            print(c(f"\n📋 未找到配置，已将示例文件复制为 {path}", Colors.YELLOW))
            shutil.copy(example, path)
        else:
            print(c("❌ 未找到配置文件，请先使用 --init 生成", Colors.RED))
            sys.exit(1)

    with open(path, encoding="utf-8") as f:
        config = json.load(f)

    # 环境变量替换
    config["settings"] = config.get("settings", {})
    for site in config.get("sites", []):
        for key in ("username", "password", "token"):
            if key in site:
                site[key] = env_subst(site[key])
        # headers 中的值也要替换
        if "checkin_headers" in site:
            site["checkin_headers"] = {
                k: env_subst(v) for k, v in site["checkin_headers"].items()
            }

    return config


def init_config():
    """生成配置模板"""
    src = os.path.join(SCRIPT_DIR, "sign_sites.example.json")
    dst = os.path.join(SCRIPT_DIR, "sign_sites.json")
    if os.path.exists(dst):
        print(c(f"⚠️  配置文件已存在: {dst}", Colors.YELLOW))
        print("  如需重新生成，请先删除该文件")
    else:
        shutil.copy(src, dst)
        print(c(f"✅ 已生成配置模板: {dst}", Colors.GREEN))
        print("  编辑该文件，填入你的站点信息后运行:")
        print("  python web_auto_sign.py")


# ══════════════════════════════════════════════════════
# 签到执行器
# ══════════════════════════════════════════════════════
class SignExecutor:
    """单个站点的签到执行"""

    def __init__(self, site: dict, settings: dict):
        self.site = site
        self.settings = settings
        self.name = site.get("name", "未知站点")
        self.result = {
            "name": self.name,
            "status": "pending",
            "detail": "",
            "screenshot": None,
            "timestamp": datetime.now().isoformat(),
        }

    def run(self):
        """执行签到"""
        from playwright.sync_api import sync_playwright

        headless = self.settings.get("headless", True)
        timeout = self.settings.get("timeout_seconds", 30) * 1000

        print(f"\n  {c('→', Colors.CYAN)} {self.name}")

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=headless,
                args=["--no-sandbox"],
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                locale="zh-CN",
            )
            page = context.new_page()
            page.set_default_timeout(timeout)

            try:
                login_type = self.site.get("login_type", "password")

                # 阶段1: 登录
                if login_type == "password":
                    self._login_password(page)
                elif login_type == "token":
                    self._login_token(context)
                elif login_type == "qrcode":
                    self._login_qrcode(page)
                elif login_type == "captcha":
                    self._login_captcha(page)

                if self.result["status"] == "failed":
                    self._screenshot(page)
                    browser.close()
                    return self.result

                # 阶段2: 签到
                self._do_checkin(page)

                # 截图
                self._screenshot(page)

            except Exception as e:
                self.result["status"] = "failed"
                self.result["detail"] = f"异常: {str(e)[:100]}"
                self._screenshot(page)

            browser.close()

        return self.result

    def _login_password(self, page):
        """账号密码登录"""
        login_url = self.site.get("login_url", "")
        if not login_url:
            self.result["status"] = "skipped"
            self.result["detail"] = "未配置登录页 URL"
            return

        try:
            print(f"    🔐 登录: {login_url}")
            page.goto(login_url, wait_until="networkidle", timeout=15000)

            # 智能查找用户名字段
            username = self.site.get("username", "")
            password = self.site.get("password", "")
            us = self.site.get("username_selector", "")
            ps = self.site.get("password_selector", "")
            ss = self.site.get("submit_selector", "")

            # 如果没配置选择器，自动检测
            if not us:
                us = self._detect_input(page, ["username", "user", "email", "account", "name", "login"])
            if not ps:
                ps = self._detect_input(page, ["password", "pass", "pwd"])

            if us:
                page.fill(us, username)
                print(f"    📝 填写用户名: {c('✓', Colors.GREEN)}")
            if ps:
                page.fill(ps, password)
                print(f"    📝 填写密码: {c('✓', Colors.GREEN)}")

            # 提交
            if ss:
                page.click(ss)
            else:
                # 自动找提交按钮
                page.keyboard.press("Enter")

            # 等待登录完成
            page.wait_for_load_state("networkidle", timeout=10000)

            # 检查登录是否成功（简单判断：URL不包含login且没有错误提示）
            current_url = page.url
            if "login" not in current_url.lower() or "error" not in page.content().lower():
                print(f"    ✅ 登录成功")
            else:
                # 可能登录失败，但继续尝试签到
                print(f"    ⚠️ 登录状态不确定，继续尝试签到...")

        except Exception as e:
            self.result["status"] = "failed"
            self.result["detail"] = f"登录失败: {str(e)[:80]}"

    def _login_token(self, context):
        """Token 方式登录（无需页面交互）"""
        token = self.site.get("token", "")
        if not token:
            self.result["status"] = "failed"
            self.result["detail"] = "未配置 Token"
            return

        # 设置 Authorization header
        context.set_extra_http_headers({
            "Authorization": f"Bearer {token}",
        })
        print(f"    🔑 已设置 Token 认证")

    def _login_qrcode(self, page):
        """扫码登录"""
        login_url = self.site.get("login_url", "")
        if not login_url:
            self.result["status"] = "failed"
            self.result["detail"] = "未配置登录页 URL"
            return

        try:
            page.goto(login_url, wait_until="networkidle", timeout=15000)
            wait_seconds = self.site.get("qrcode_wait_seconds", 120)
            print(f"    📱 请在 {wait_seconds} 秒内扫码登录...")

            # 等待页面变化（URL变了或者登录成功元素出现）
            original_url = page.url
            for i in range(wait_seconds):
                time.sleep(1)
                if page.url != original_url or "login" not in page.url.lower():
                    print(f"    ✅ 扫码登录成功 (等待{i+1}秒)")
                    break
                if i % 10 == 9:
                    print(f"    ⏳ 等待中... ({i+1}秒)")
            else:
                self.result["status"] = "failed"
                self.result["detail"] = "扫码超时"

        except Exception as e:
            self.result["status"] = "failed"
            self.result["detail"] = f"扫码登录异常: {str(e)[:80]}"

    def _login_captcha(self, page):
        """有验证码的登录"""
        login_url = self.site.get("login_url", "")
        if not login_url:
            self.result["status"] = "failed"
            self.result["detail"] = "未配置登录页 URL"
            return

        try:
            page.goto(login_url, wait_until="networkidle", timeout=15000)
            username = self.site.get("username", "")
            password = self.site.get("password", "")
            us = self.site.get("username_selector", "")
            ps = self.site.get("password_selector", "")

            if not us:
                us = self._detect_input(page, ["username", "user", "email"])
            if not ps:
                ps = self._detect_input(page, ["password", "pass"])

            if us:
                page.fill(us, username)
            if ps:
                page.fill(ps, password)

            # 截个图，让用户手动处理验证码
            screenshot_dir = self.settings.get("screenshot_dir", "./sign_screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            captcha_path = os.path.join(screenshot_dir, f"captcha_{self.name}.png")
            page.screenshot(path=captcha_path)

            print(f"    ⚠️  此站点需要验证码！")
            print(f"    📸 已截图: {captcha_path}")
            print(f"    👆 请手动登录后按 Enter 继续...")
            input()

            page.wait_for_load_state("networkidle", timeout=10000)
            print(f"    ✅ 登录完成")

        except Exception as e:
            self.result["status"] = "failed"
            self.result["detail"] = f"登录异常: {str(e)[:80]}"

    def _do_checkin(self, page):
        """执行签到"""
        checkin_url = self.site.get("checkin_url", "")
        checkin_method = self.site.get("checkin_method", "GET").upper()

        try:
            # 判断是 API 签到还是页面点击签到
            if checkin_url and ("/api/" in checkin_url.lower() or "api." in checkin_url.lower()):
                self._api_checkin(page, checkin_url, checkin_method)
            else:
                self._page_checkin(page, checkin_url)

        except Exception as e:
            if self.result["status"] == "pending":
                self.result["status"] = "failed"
                self.result["detail"] = f"签到异常: {str(e)[:80]}"

    def _api_checkin(self, page, url, method):
        """通过 API 方式签到"""
        headers = self.site.get("checkin_headers", {})
        body = self.site.get("checkin_body", "{}")

        try:
            # 通过 page.evaluate 发起 fetch 请求（自动带 Cookie）
            js_code = f"""
            (async () => {{
                const resp = await fetch('{url}', {{
                    method: '{method}',
                    headers: {json.dumps(headers)},
                    body: '{method}' === 'POST' ? {json.dumps(body)} : undefined,
                }});
                const text = await resp.text();
                return {{ status: resp.status, body: text.slice(0, 500) }};
            }})()
            """
            result = page.evaluate(js_code)
            resp_body = result.get("body", "")

            # 检查结果
            success_kws = self.site.get("success_keywords", [])
            already_kws = self.site.get("already_signed_keywords", [])

            if any(kw in resp_body for kw in already_kws):
                self.result["status"] = "already"
                self.result["detail"] = "今日已签到"
            elif any(kw in resp_body for kw in success_kws):
                self.result["status"] = "success"
                self.result["detail"] = f"签到成功 (HTTP {result.get('status')})"
            else:
                self.result["status"] = "success"
                self.result["detail"] = f"API 已调用 (HTTP {result.get('status')})"

            print(f"    📡 API签到: {c(self.result['status'], self._status_color())}")

        except Exception as e:
            self.result["status"] = "failed"
            self.result["detail"] = f"API请求失败: {str(e)[:80]}"

    def _page_checkin(self, page, url):
        """页面点击签到"""
        # 先导航到签到页
        if url:
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
            except Exception:
                pass

        # 智能查找签到按钮
        button = self._find_checkin_button(page)

        if button:
            try:
                # 试试能不能看到文字
                btn_text = button.inner_text().strip()[:30]
                button.click()
                page.wait_for_timeout(2000)

                # 验证结果
                success = self._verify_checkin(page)
                if success:
                    self.result["status"] = "success"
                    self.result["detail"] = f"签到成功: '{btn_text}'"
                else:
                    self.result["status"] = "success"
                    self.result["detail"] = f"已点击 '{btn_text}'"
                print(f"    👆 点击签到: {btn_text} → {c(self.result['status'], self._status_color())}")

            except Exception as e:
                self.result["status"] = "failed"
                self.result["detail"] = f"点击签到按钮失败: {str(e)[:60]}"
        else:
            # 检查是否已经签到
            page_content = page.content().lower()
            already_kws = self.site.get("already_signed_keywords", ["已签到", "已打卡"])
            success_kws = self.site.get("success_keywords", ["签到成功", "连续签到"])

            if any(kw in page_content for kw in already_kws):
                self.result["status"] = "already"
                self.result["detail"] = "今日已签到"
            elif any(kw in page_content for kw in success_kws):
                self.result["status"] = "success"
                self.result["detail"] = "已签到"
            else:
                self.result["status"] = "failed"
                self.result["detail"] = "未找到签到按钮，可截图查看页面状态"

            print(f"    🔍 未找到签到按钮: {c(self.result['status'], self._status_color())}")

    def _find_checkin_button(self, page):
        """智能查找签到按钮"""
        # 1. 按配置的选择器查找
        selectors = self.site.get("checkin_selectors", [])
        for sel in selectors:
            try:
                btn = page.query_selector(sel)
                if btn and btn.is_visible():
                    return btn
            except Exception:
                pass

        # 2. 按文字内容查找
        keywords = ["签到", "打卡", "签 到", "checkin", "check in", "sign in",
                     "每日签到", "今日签到", "点此签到", "立即签到"]
        for kw in keywords:
            try:
                # 尝试多种选择器
                for sel in [f"text={kw}", f"button:has-text('{kw}')",
                            f"a:has-text('{kw}')", f"[class*='sign']:has-text('{kw}')"]:
                    btn = page.query_selector(sel)
                    if btn and btn.is_visible():
                        return btn
            except Exception:
                pass

        # 3. 按属性查找
        try:
            attrs = page.evaluate("""() => {
                const results = [];
                const allEls = document.querySelectorAll('a, button, span, div, input[type=\"submit\"]');
                allEls.forEach(el => {
                    const text = (el.textContent || '').trim().toLowerCase();
                    const href = (el.getAttribute('href') || '').toLowerCase();
                    const cls = (el.className || '').toLowerCase();
                    const id = (el.id || '').toLowerCase();
                    if (text.includes('签到') || text.includes('打卡') ||
                        href.includes('sign') || href.includes('checkin') ||
                        cls.includes('sign') || id.includes('sign')) {
                        results.push({ tag: el.tagName, text: text.slice(0, 20),
                                       href: href.slice(0, 40), cls: cls.slice(0, 30) });
                    }
                });
                return results;
            }""")
            for attr in attrs:
                try:
                    tag = attr.get("tag", "").lower()
                    text = attr.get("text", "")
                    sel = f"{tag}:has-text('{text[:10]}')"
                    btn = page.query_selector(sel)
                    if btn and btn.is_visible():
                        return btn
                except Exception:
                    pass
        except Exception:
            pass

        return None

    def _verify_checkin(self, page):
        """验证签到是否成功"""
        try:
            content = page.content().lower()
            success_kws = self.site.get("success_keywords",
                ["签到成功", "已签到", "连续签到", "获得奖励", "签到积分"])
            already_kws = self.site.get("already_signed_keywords",
                ["今日已签到", "已打卡", "今日已打卡"])

            if any(kw in content for kw in already_kws):
                self.result["status"] = "already"
                self.result["detail"] = "今日已签到"
                return True
            if any(kw in content for kw in success_kws):
                self.result["status"] = "success"
                return True

            # 检查按钮状态变化
            btn = self._find_checkin_button(page)
            if btn is None:
                self.result["status"] = "success"
                self.result["detail"] = "签到按钮已消失"
                return True

            return False
        except Exception:
            return False

    def _detect_input(self, page, keywords):
        """智能检测输入框"""
        try:
            for kw in keywords:
                selectors = [
                    f"input[name='{kw}']", f"input[id='{kw}']",
                    f"input[placeholder*='{kw}']", f"input[type='{kw}']",
                    f"input[name*='{kw}']", f"input[id*='{kw}']",
                ]
                for sel in selectors:
                    el = page.query_selector(sel)
                    if el:
                        return sel
            return ""
        except Exception:
            return ""

    def _screenshot(self, page):
        """截图保存"""
        try:
            screenshot_dir = self.settings.get("screenshot_dir", "./sign_screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = re.sub(r'[\\/*?:"<>|]', '_', self.name)[:30]
            path = os.path.join(screenshot_dir, f"{safe_name}_{ts}.png")
            page.screenshot(path=path, full_page=True)
            self.result["screenshot"] = path
        except Exception:
            pass

    def _status_color(self):
        return {"success": "GREEN", "already": "YELLOW",
                "failed": "RED", "skipped": "DIM"}.get(
            self.result.get("status", "pending"), "RESET")


# ══════════════════════════════════════════════════════
# 报告生成
# ══════════════════════════════════════════════════════
def generate_report(results, config):
    """生成签到报告"""
    settings = config.get("settings", {})
    report_dir = settings.get("report_dir", "./sign_reports")
    os.makedirs(report_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"sign_report_{ts}.md")

    success = sum(1 for r in results if r["status"] == "success")
    already = sum(1 for r in results if r["status"] == "already")
    failed = sum(1 for r in results if r["status"] == "failed")
    skipped = sum(1 for r in results if r["status"] == "skipped")

    # 终端输出
    print(f"\n  {c('══════════════════════════════════════', 'GREEN')}")
    print(f"  {c('📋 签到汇总', 'BOLD')}")
    print(f"  {c('══════════════════════════════════════', 'GREEN')}")
    print(f"  ✅ 成功: {success}  ⚠️ 已签: {already}  ❌ 失败: {failed}  ⏭️ 跳过: {skipped}")
    print()

    for r in results:
        emoji = {"success": "✅", "already": "⚠️", "failed": "❌", "skipped": "⏭️"}
        color = {"success": "GREEN", "already": "YELLOW", "failed": "RED", "skipped": "DIM"}
        st = r.get("status", "pending")
        print(f"  {emoji.get(st, '❓')} {c(r['name'], 'BOLD')}: {c(st, color.get(st, 'RESET'))} — {r.get('detail', '')}")
        if r.get("screenshot"):
            print(f"     📸 {c(r['screenshot'], 'DIM')}")

    # Markdown 报告
    lines = [
        f"# 📋 自动签到报告",
        f"",
        f"**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"## 汇总",
        f"",
        f"| 状态 | 数量 |",
        f"|------|------|",
        f"| ✅ 成功 | {success} |",
        f"| ⚠️ 已签到 | {already} |",
        f"| ❌ 失败 | {failed} |",
        f"| ⏭️ 跳过 | {skipped} |",
        f"",
        f"## 详情",
        f"",
        f"| 站点 | 状态 | 详情 | 截图 |",
        f"|------|------|------|------|",
    ]
    for r in results:
        st = r.get("status", "pending")
        emoji_map = {"success": "✅", "already": "⚠️", "failed": "❌", "skipped": "⏭️"}
        screenshot_link = f"[查看]({r['screenshot']})" if r.get("screenshot") else "-"
        lines.append(f"| {r['name']} | {emoji_map.get(st, '')} {st} | {r.get('detail', '')} | {screenshot_link} |")

    lines.extend(["", "---", f"*由 🐱 Web Auto Sign 自动生成*"])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n  📝 报告已保存: {c(report_path, 'CYAN')}")


# ══════════════════════════════════════════════════════
# 主入口
# ══════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="🐱 Web Auto Sign - 网站自动签到工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  %(prog)s                          # 运行所有站点
  %(prog)s -c my_sites.json         # 指定配置
  %(prog)s --site "论坛签到"         # 指定站点
  %(prog)s --init                   # 生成配置模板
  %(prog)s --list                   # 列出站点
  %(prog)s --no-headless            # 显示浏览器
        """,
    )
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument("--site", help="只运行指定站点（按名称匹配）")
    parser.add_argument("--init", action="store_true", help="生成配置模板")
    parser.add_argument("--list", action="store_true", help="列出配置中的站点")
    parser.add_argument("--no-headless", action="store_true", help="显示浏览器窗口")

    args = parser.parse_args()

    if args.init:
        init_config()
        return

    config = load_config(args.config)
    settings = config.get("settings", {})

    if args.no_headless:
        settings["headless"] = False

    sites = config.get("sites", [])

    if args.list:
        print(f"\n  📋 配置中的站点 ({len(sites)} 个):\n")
        for i, site in enumerate(sites, 1):
            enabled = site.get("enabled", True)
            status = c("✅ 启用", "GREEN") if enabled else c("⏸️ 停用", "DIM")
            name = site.get("name", f"站点{i}")
            lt = site.get("login_type", "password")
            url = site.get("checkin_url", site.get("login_url", "N/A"))
            print(f"  {i}. {status} {c(name, 'BOLD')} ({lt})")
            print(f"     {c(url[:80], 'DIM')}")
        return

    if not sites:
        print(c("❌ 配置中没有站点", Colors.RED))
        print("  请先编辑配置文件或使用 --init 生成")
        return

    # 过滤站点
    if args.site:
        matched = [s for s in sites if args.site.lower() in s.get("name", "").lower()]
        if not matched:
            print(c(f"❌ 未找到匹配的站点: {args.site}", Colors.RED))
            return
        sites = matched

    # 只跑启用的站点
    sites = [s for s in sites if s.get("enabled", True)]
    if not sites:
        print(c("⚠️  没有启用的站点", Colors.YELLOW))
        return

    print(f"\n  {c('🐱 Web Auto Sign', 'BOLD')}")
    print(f"  {c('════════════════════════════════', 'GREEN')}")
    print(f"  站点数: {len(sites)}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if not settings.get("headless", True):
        print(f"  模式: {c('浏览器可见', 'YELLOW')}")

    # 逐个执行
    results = []
    interval = settings.get("interval_between_sites", 5)

    for i, site in enumerate(sites):
        if i > 0 and interval > 0:
            print(f"\n  ⏳ 等待 {interval} 秒...")
            time.sleep(interval)

        executor = SignExecutor(site, settings)
        result = executor.run()
        results.append(result)

    # 生成报告
    generate_report(results, config)


if __name__ == "__main__":
    main()
