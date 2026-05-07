#!/usr/bin/env python3
"""
网页设计复刻顾问 —— Web Design Advisor
===========================================
读取 WebAnalyzer 的设计分析数据，生成完整的复刻方案：
  1. 📋 设计规范文档 (Markdown)
  2. 🎨 HTML+CSS 复刻页面 (可直接打开)
  3. ⚙️ Tailwind CSS 配置
  4. 🎯 CSS 设计 Token

使用方式：
  # 从分析报告生成设计规范
  python web_design_advisor.py report.json

  # 生成 HTML 复刻页面
  python web_design_advisor.py report.json --recreate-html

  # 生成 Tailwind 配置
  python web_design_advisor.py report.json --tailwind-config

  # 全部生成
  python web_design_advisor.py report.json --all

  # 管道模式
  python web_api_analyzer.py URL --json-only | python web_design_advisor.py --stdin

版本: 1.0.0
作者：主人的小猫咪咪 🐱
"""

import argparse
import json
import os
import sys
from datetime import datetime


class DesignAdvisor:
    """设计复刻顾问"""

    def __init__(self, report: dict):
        self.report = report
        self.design = report.get("design_analysis", {})
        self.url = report.get("target_url", "")

    # ══════════════════════════════════════════════════════
    # 设计规范文档
    # ══════════════════════════════════════════════════════
    def generate_design_spec(self) -> str:
        """生成设计规范文档"""
        cp = self.design.get("color_palette", {})
        typo = self.design.get("typography", {})
        comps = self.design.get("components", {})
        sp = self.design.get("spacing", {})
        eff = self.design.get("effects", {})
        anim = self.design.get("animations", {})

        lines = [
            f"# 🎨 设计复刻规范",
            f"",
            f"**来源**: {self.url}",
            f"**生成时间**: {datetime.now().isoformat()}",
            f"",
            f"---",
            f"",
            f"## 1. 色板",
            f"",
        ]

        # 主色
        if cp.get("most_used"):
            lines.append(f"| 用途 | 色值 | 出现次数 |")
            lines.append(f"|------|------|----------|")
            for i, c in enumerate(cp["most_used"][:5]):
                label = ["主色", "辅色", "强调色", "常用色", "常用色"][min(i, 4)]
                lines.append(f"| **{label}** | `{c['color']}` | {c['count']}次 |")
            lines.append("")

        # 背景色
        if cp.get("backgrounds"):
            lines.append("**背景色**:")
            for bg in cp["backgrounds"][:4]:
                lines.append(f"- `{bg}`")
            lines.append("")

        # 文字色
        if cp.get("texts"):
            lines.append("**文字色**:")
            for t in cp["texts"][:4]:
                lines.append(f"- `{t}`")
            lines.append("")

        # 渐变色
        if cp.get("gradients"):
            lines.append("**渐变色**:")
            for g in cp["gradients"][:3]:
                lines.append(f"- `{g[:80]}...`")
            lines.append("")

        # 全量色板
        if cp.get("full_palette"):
            palette_str = " | ".join(cp["full_palette"][:12])
            lines.append(f"**完整色板**: {palette_str}")
            lines.append("")

        # 排版
        lines.append("## 2. 排版系统")
        lines.append("")
        headings = typo.get("headings", {})
        if headings:
            lines.append("| 层级 | 字体 | 字号 | 字重 | 行高 | 字间距 |")
            lines.append("|------|------|------|------|------|--------|")
            for tag in ["h1", "h2", "h3", "h4", "h5", "h6", "body"]:
                if tag in headings:
                    h = headings[tag]
                    label = {"h1": "H1 标题", "h2": "H2 标题", "h3": "H3 标题",
                             "h4": "H4 标题", "h5": "H5 标题", "h6": "H6 标题",
                             "body": "正文"}.get(tag, tag)
                    lines.append(
                        f"| {label} | {h.get('family','-')} | {h.get('size','-')} | "
                        f"{h.get('weight','-')} | {h.get('lineHeight','-')} | {h.get('letterSpacing','-')} |"
                    )
            lines.append("")

        # 字体
        families = typo.get("font_families", [])
        if families:
            lines.append(f"**字体系列**: {', '.join(families)}")
            lines.append("")

        # 间距
        lines.append("## 3. 间距系统")
        lines.append("")
        lines.append(f"| 类别 | 值 |")
        lines.append(f"|------|-----|")
        if sp.get("container_max_width"):
            lines.append(f"| 容器最大宽度 | {sp['container_max_width']} |")
        if sp.get("common_margins"):
            lines.append(f"| 常用外间距 | {' · '.join(sp['common_margins'][:6])} |")
        if sp.get("common_paddings"):
            lines.append(f"| 常用内间距 | {' · '.join(sp['common_paddings'][:6])} |")
        lines.append("")

        # 圆角 & 阴影
        lines.append("## 4. 效果系统")
        lines.append("")
        br = eff.get("border_radius", {})
        if br:
            lines.append("**圆角**:")
            if br.get("small"):
                lines.append(f"- 小: `{br['small']}`")
            if br.get("medium"):
                lines.append(f"- 中: `{br['medium']}`")
            if br.get("large"):
                lines.append(f"- 大: `{br['large']}`")
            if br.get("all_values"):
                lines.append(f"- 所有值: {' · '.join(br['all_values'])}")
            lines.append("")

        bs = eff.get("box_shadow", {})
        if bs.get("all_values"):
            lines.append("**阴影**:")
            for s in bs["all_values"][:4]:
                lines.append(f"- `{s}`")
            lines.append("")

        # 组件
        lines.append("## 5. 组件样式")
        lines.append("")
        if comps.get("buttons"):
            lines.append("### Button")
            lines.append("")
            lines.append("| 属性 | 值 |")
            lines.append("|------|-----|")
            btn = comps["buttons"][0]
            for k, v in btn.items():
                if v and k != "text":
                    lines.append(f"| {k} | `{v}` |")
            lines.append("")

        if comps.get("cards"):
            lines.append("### Card")
            lines.append("")
            lines.append("| 属性 | 值 |")
            lines.append("|------|-----|")
            card = comps["cards"][0]
            for k, v in card.items():
                if v:
                    lines.append(f"| {k} | `{v}` |")
            lines.append("")

        if comps.get("inputs"):
            lines.append("### Input")
            lines.append("")
            lines.append("| 属性 | 值 |")
            lines.append("|------|-----|")
            inp = comps["inputs"][0]
            for k, v in inp.items():
                if v:
                    lines.append(f"| {k} | `{v}` |")
            lines.append("")

        # 动画
        if anim.get("transitions"):
            lines.append("## 6. 动效")
            lines.append("")
            for t in anim["transitions"][:5]:
                lines.append(f"- `{t}`")
            lines.append("")

        lines.append("---")
        lines.append("*由 🐱 Web Design Advisor 自动生成*")
        return "\n".join(lines)

    # ══════════════════════════════════════════════════════
    # HTML+CSS 复刻页面
    # ══════════════════════════════════════════════════════
    def generate_recreate_html(self) -> str:
        """生成可直接运行的 HTML 复刻页面"""
        cp = self.design.get("color_palette", {})
        typo = self.design.get("typography", {})
        comps = self.design.get("components", {})
        sp = self.design.get("spacing", {})
        eff = self.design.get("effects", {})
        anim = self.design.get("animations", {})

        # 提取关键设计 Token
        bg_color = "#ffffff"
        text_color = "#333333"
        primary_color = "#3b82f6"
        font_family = "system-ui, sans-serif"
        border_radius = "8px"
        container_width = "1200px"

        if cp.get("backgrounds"):
            bg_color = cp["backgrounds"][0]
        if cp.get("texts"):
            text_color = cp["texts"][0]
        if cp.get("most_used"):
            primary_color = cp["most_used"][0]["color"]
        families = typo.get("font_families", [])
        if families:
            font_family = families[0]
        br = eff.get("border_radius", {})
        if br.get("medium"):
            border_radius = br["medium"]
        if sp.get("container_max_width"):
            container_width = sp["container_max_width"]

        # 字体引用
        font_link = ""
        if font_family and font_family not in ("system-ui", "sans-serif", "serif", "monospace"):
            font_slug = font_family.replace(" ", "+")
            font_link = f'<link href="https://fonts.googleapis.com/css2?family={font_slug}:wght@400;500;600;700&display=swap" rel="stylesheet">'

        # 排版 CSS
        type_css = ""
        headings_data = typo.get("headings", {})
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            if tag in headings_data:
                h = headings_data[tag]
                css = f"  {tag} {{"
                if h.get("family"):
                    css += f"\n    font-family: '{h['family']}', {font_family};"
                if h.get("size"):
                    css += f"\n    font-size: {h['size']};"
                if h.get("weight"):
                    css += f"\n    font-weight: {h['weight']};"
                if h.get("lineHeight"):
                    css += f"\n    line-height: {h['lineHeight']};"
                if h.get("letterSpacing"):
                    css += f"\n    letter-spacing: {h['letterSpacing']};"
                css += "\n  }"
                type_css += css + "\n"

        # 间距 Token
        padding_map = {"4px": "0.25rem", "8px": "0.5rem", "12px": "0.75rem",
                       "16px": "1rem", "20px": "1.25rem", "24px": "1.5rem",
                       "32px": "2rem", "40px": "2.5rem", "48px": "3rem", "64px": "4rem"}
        common_margins = sp.get("common_margins", ["16px", "24px", "32px"])
        common_paddings = sp.get("common_paddings", ["16px", "24px"])

        # 按钮样式
        btn_css = ""
        if comps.get("buttons"):
            btn = comps["buttons"][0]
            btn_css = "  .btn {\n"
            if btn.get("bg"):
                btn_css += f"    background: {btn['bg']};\n"
            if btn.get("color"):
                btn_css += f"    color: {btn['color']};\n"
            if btn.get("radius"):
                btn_css += f"    border-radius: {btn['radius']};\n"
            if btn.get("padding"):
                btn_css += f"    padding: {btn['padding']};\n"
            if btn.get("fontSize"):
                btn_css += f"    font-size: {btn['fontSize']};\n"
            if btn.get("fontWeight"):
                btn_css += f"    font-weight: {btn['fontWeight']};\n"
            if btn.get("border") and btn["border"] != "none":
                btn_css += f"    border: {btn['border']};\n"
            if btn.get("shadow") and btn["shadow"] != "none":
                btn_css += f"    box-shadow: {btn['shadow']};\n"
            btn_css += "    cursor: pointer;\n    display: inline-flex;\n    align-items: center;\n    justify-content: center;\n"
            btn_css += "    text-decoration: none;\n    transition: all 0.2s ease;\n  }"

        # Card 样式
        card_css = ""
        if comps.get("cards"):
            card = comps["cards"][0]
            card_css = "  .card {\n"
            if card.get("bg"):
                card_css += f"    background: {card['bg']};\n"
            if card.get("radius"):
                card_css += f"    border-radius: {card['radius']};\n"
            if card.get("padding"):
                card_css += f"    padding: {card['padding']};\n"
            if card.get("shadow") and card["shadow"] != "none":
                card_css += f"    box-shadow: {card['shadow']};\n"
            if card.get("border") and card["border"] != "none":
                card_css += f"    border: {card['border']};\n"
            card_css += "  }"

        # Input 样式
        input_css = ""
        if comps.get("inputs"):
            inp = comps["inputs"][0]
            input_css = "  .input {\n"
            if inp.get("bg"):
                input_css += f"    background: {inp['bg']};\n"
            if inp.get("color"):
                input_css += f"    color: {inp['color']};\n"
            if inp.get("radius"):
                input_css += f"    border-radius: {inp['radius']};\n"
            if inp.get("padding"):
                input_css += f"    padding: {inp['padding']};\n"
            if inp.get("fontSize"):
                input_css += f"    font-size: {inp['fontSize']};\n"
            if inp.get("border"):
                input_css += f"    border: {inp['border']};\n"
            input_css += "    width: 100%;\n    box-sizing: border-box;\n  }"

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎨 设计复刻 - 原站设计系统</title>
{font_link}
<style>
  /* ===== Design Tokens ===== */
  :root {{
    --primary: {primary_color};
    --bg: {bg_color};
    --text: {text_color};
    --font: '{font_family}', system-ui, sans-serif;
    --radius: {border_radius};
    --container: {container_width};
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: var(--font);
    color: var(--text);
    background: var(--bg);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }}

  .container {{
    max-width: var(--container);
    margin: 0 auto;
    padding: 0 {common_paddings[0] if common_paddings else '1rem'};
  }}

{type_css}
  p {{ font-size: {headings_data.get('body', {}).get('size', '16px')};
       line-height: {headings_data.get('body', {}).get('lineHeight', '1.6')};
       margin-bottom: {common_margins[0] if common_margins else '1rem'}; }}

{btn_css}

{card_css}

{input_css}

  /* ===== Layout ===== */
  .section {{
    padding: 2rem 0;
  }}

  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: {common_margins[0] if common_margins else '1rem'};
  }}

  .flex {{
    display: flex;
    gap: {common_margins[0] if common_margins else '1rem'};
    flex-wrap: wrap;
  }}

  .color-swatch {{
    width: 60px;
    height: 60px;
    border-radius: var(--radius);
    display: inline-block;
  }}

  .color-card {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg);
    border: 1px solid color-mix(in srgb, var(--text) 15%, transparent);
    border-radius: var(--radius);
  }}

  .spacing-demo {{
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    border-radius: var(--radius);
  }}

  hr {{
    border: none;
    border-top: 1px solid color-mix(in srgb, var(--text) 15%, transparent);
    margin: 2rem 0;
  }}
</style>
</head>
<body>
  <div class="container">
    <h1>🎨 设计复刻展示</h1>
    <p>从 <strong>{self.url}</strong> 提取的设计系统</p>
    <hr>

    <!-- 色板 -->
    <h2>1. 色板</h2>
    <div class="grid">
"""

        # 色板展示
        if cp.get("full_palette"):
            colors_shown = set()
            for c in cp["full_palette"][:16]:
                hex_color = c
                if hex_color in colors_shown:
                    continue
                colors_shown.add(hex_color)
                html += f"""      <div class="color-card">
        <div class="color-swatch" style="background: {hex_color};"></div>
        <code>{hex_color}</code>
      </div>
"""

        html += """    </div>
    <hr>

    <!-- 排版 -->
    <h2>2. 排版系统</h2>
"""
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            if tag in headings_data:
                h = headings_data[tag]
                demo_text = f"{tag.upper()} {'标题样式的实际效果'} {h.get('size','')}"
                html += f"    <{tag}>{demo_text}</{tag}>\n"

        body_data = headings_data.get("body", {})
        body_size = body_data.get("size", "16px")
        html += f"""    <p style="font-size: {body_size};">正文段落文本示例。这是从原站提取的正文样式，包含字体、字号、行高和颜色等属性。Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
    <hr>

    <!-- 组件 -->
    <h2>3. 组件</h2>
    <div class="flex">
"""
        # 按钮
        if comps.get("buttons"):
            btn = comps["buttons"][0]
            btn_text = btn.get("text", "Button")
            html += f'      <button class="btn">{btn_text}</button>\n'

        html += """    </div>
    <br>
    <div class="grid" style="grid-template-columns: 1fr 1fr;">
"""

        # Card
        if comps.get("cards"):
            card = comps["cards"][0]
            html += """      <div class="card">
        <h3>卡片标题</h3>
        <p>这是卡片内容区域，展示了从原站提取的卡片样式，包含背景色、圆角、阴影和内间距。</p>
      </div>
"""

        # Input
        if comps.get("inputs"):
            html += """      <div>
        <label>输入框</label>
        <input class="input" type="text" placeholder="请输入内容">
      </div>
"""

        html += """    </div>
    <hr>

    <!-- 间距展示 -->
    <h2>4. 间距系统</h2>
"""
        for m in common_margins[:5]:
            val = m.replace("px", "")
            html += f"""    <div style="margin-bottom: 0.5rem;">
      <code>{m}</code>
      <div class="spacing-demo" style="height: 8px; width: {val}px; max-width: 100%;"></div>
    </div>
"""

        html += """    <hr>

    <!-- 圆角 -->
    <h2>5. 圆角 & 阴影</h2>
    <div class="flex">
"""
        br_vals = br.get("all_values", ["4px", "8px", "12px", "16px"])
        for radius_val in br_vals[:5]:
            html += f"""      <div style="text-align: center;">
        <div style="width: 60px; height: 60px; background: var(--primary); border-radius: {radius_val};"></div>
        <code>{radius_val}</code>
      </div>
"""

        html += """    </div>
    <br>
    <div style="color: color-mix(in srgb, var(--text) 50%, transparent); font-size: 0.85rem; text-align: center; padding: 2rem 0;">
      🐱 由 Web Design Advisor 自动生成 | 设计复刻 v1.0
    </div>
  </div>
</body>
</html>"""
        return html

    # ══════════════════════════════════════════════════════
    # Tailwind 配置生成
    # ══════════════════════════════════════════════════════
    def generate_tailwind_config(self) -> str:
        """生成 Tailwind CSS 配置"""
        cp = self.design.get("color_palette", {})
        typo = self.design.get("typography", {})
        sp = self.design.get("spacing", {})
        eff = self.design.get("effects", {})
        anim = self.design.get("animations", {})

        # Colors
        colors = {}
        if cp.get("full_palette"):
            for i, c in enumerate(cp["full_palette"][:15]):
                name = f"c{i+1}"
                # 尝试给主要颜色取有意义的名字
                if i == 0:
                    name = "primary"
                elif i == 1:
                    name = "secondary"
                colors[name] = c

        # 背景色
        if cp.get("backgrounds"):
            for i, bg in enumerate(cp["backgrounds"][:3]):
                name = f"bg-{['primary', 'secondary', 'tertiary'][i]}"
                colors[name] = bg

        # 文字色
        if cp.get("texts"):
            for i, t in enumerate(cp["texts"][:3]):
                name = f"text-{['primary', 'secondary', 'muted'][i]}"
                colors[name] = t

        # Font families
        families = typo.get("font_families", [])
        if not families:
            families = ["system-ui"]

        # Border radius
        br = eff.get("border_radius", {})
        bv = br.get("all_values", ["8px"])
        radius_config = {}
        if len(bv) >= 1:
            radius_config["sm"] = bv[0]
        if len(bv) >= 2:
            radius_config["md"] = bv[len(bv)//2]
        if len(bv) >= 3:
            radius_config["lg"] = bv[-1]

        # Spacing
        margins = sp.get("common_margins", [])
        spacing_config = {}
        for m in margins[:8]:
            try:
                px_val = int(m.replace("px", ""))
                rem_val = px_val / 16
                spacing_config[str(px_val)] = f"{rem_val}rem"
            except ValueError:
                pass

        # Animations
        anim_config = {}
        if anim.get("transitions"):
            for t in anim["transitions"][:3]:
                parts = t.split(" ")
                if len(parts) >= 2:
                    anim_config[f"trans-{parts[0]}"] = t

        lines = [
            "// tailwind.config.js",
            "// 🐱 由 Web Design Advisor 自动生成",
            f"// 来源: {self.url}",
            f"// 生成时间: {datetime.now().isoformat()}",
            "",
            "/** @type {import('tailwindcss').Config} */",
            "module.exports = {",
            "  content: ['./**/*.{html,js,ts,jsx,tsx,vue}'],",
            "  theme: {",
            "    extend: {",
        ]

        # Colors
        if colors:
            lines.append("      colors: {")
            colors_json = json.dumps(colors, ensure_ascii=False)
            for k, v in colors.items():
                lines.append(f"        '{k}': '{v}',")
            lines.append("      },")

        # Font family
        lines.append("      fontFamily: {")
        lines.append(f"        'primary': ['{families[0]}', '{'system-ui'}'],")
        if len(families) > 1:
            lines.append(f"        'heading': ['{families[1]}', '{'system-ui'}'],")
        lines.append("      },")

        # Border radius
        if radius_config:
            lines.append("      borderRadius: {")
            for k, v in radius_config.items():
                lines.append(f"        '{k}': '{v}',")
            lines.append("      },")

        # Box shadow
        bs = eff.get("box_shadow", {})
        if bs.get("all_values"):
            lines.append("      boxShadow: {")
            for i, s in enumerate(bs["all_values"][:4]):
                lines.append(f"        'level-{i+1}': '{s}',")
            lines.append("      },")

        # Spacing
        if spacing_config:
            lines.append("      spacing: {")
            for k, v in list(spacing_config.items())[:8]:
                lines.append(f"        '{k}': '{v}',")
            lines.append("      },")

        lines.extend([
            "    },",
            "  },",
            "  plugins: [],",
            "};",
        ])

        return "\n".join(lines)


# ──────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="🐱 Web Design Advisor - 网页设计复刻顾问",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  %(prog)s report.json                              # 设计规范文档
  %(prog)s report.json --recreate-html              # HTML 复刻页面
  %(prog)s report.json --tailwind-config            # Tailwind 配置
  %(prog)s report.json --all                        # 全部生成
  python web_api_analyzer.py URL --json-only | %(prog)s --stdin
        """,
    )
    parser.add_argument("input", nargs="?", help="分析报告 JSON 文件")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取")
    parser.add_argument("-o", "--output", help="输出目录 (默认当前目录)")
    parser.add_argument("--recreate-html", action="store_true", help="生成 HTML 复刻页面")
    parser.add_argument("--tailwind-config", action="store_true", help="生成 Tailwind 配置")
    parser.add_argument("--all", action="store_true", help="全部生成")

    args = parser.parse_args()

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

    advisor = DesignAdvisor(report)
    outdir = args.output or "."

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    do_all = args.all or not (args.recreate_html or args.tailwind_config)

    if do_all or args.recreate_html:
        html = advisor.generate_recreate_html()
        html_path = os.path.join(outdir, "design_recreate.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"💾 HTML 复刻: {html_path}")

    if do_all or args.tailwind_config:
        tw = advisor.generate_tailwind_config()
        tw_path = os.path.join(outdir, "tailwind.config.js")
        with open(tw_path, "w", encoding="utf-8") as f:
            f.write(tw)
        print(f"💾 Tailwind 配置: {tw_path}")

    if do_all:
        spec = advisor.generate_design_spec()
        spec_path = os.path.join(outdir, "design_spec.md")
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(spec)
        print(f"💾 设计规范: {spec_path}")
        # 也输出到终端
        print("\n" + spec)

    print("\n🎨 设计复刻方案已生成！可直接打开 design_recreate.html 查看效果喵～ 🐱")


if __name__ == "__main__":
    main()
