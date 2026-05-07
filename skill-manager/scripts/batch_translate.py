#!/usr/bin/env python3
"""
技能批量翻译脚本
自动将所有英文技能翻译成中文
"""

import os
import re
import yaml
from pathlib import Path

SKILLS_DIR = Path("c:/Users/ARTpace/.skills-manager/skills")

def extract_frontmatter(content):
    """提取 YAML frontmatter"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        return match.group(1), content[match.end():]
    return None, content

def translate_skill_file(skill_path):
    """翻译单个技能文件"""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 frontmatter
    frontmatter, body = extract_frontmatter(content)
    if not frontmatter:
        return False
    
    # 解析 frontmatter
    try:
        metadata = yaml.safe_load(frontmatter)
    except:
        return False
    
    if not metadata or 'description' not in metadata:
        return False
    
    # 检查是否已经是中文
    desc = metadata.get('description', '')
    if any('\u4e00' <= char <= '\u9fff' for char in desc):
        print(f"  跳过（已是中文）: {skill_path.parent.name}")
        return False
    
    print(f"  需要翻译: {skill_path.parent.name}")
    return True

def list_all_skills():
    """列出所有技能"""
    skills = []
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skills.append(skill_dir.name)
    return sorted(skills)

def main():
    print("=" * 60)
    print("技能批量翻译工具")
    print("=" * 60)
    
    skills = list_all_skills()
    print(f"\n找到 {len(skills)} 个技能\n")
    
    needs_translation = []
    already_chinese = []
    
    for skill_name in skills:
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, _ = extract_frontmatter(content)
        if frontmatter:
            try:
                metadata = yaml.safe_load(frontmatter)
                desc = metadata.get('description', '')
                if any('\u4e00' <= char <= '\u9fff' for char in desc):
                    already_chinese.append(skill_name)
                else:
                    needs_translation.append(skill_name)
            except:
                needs_translation.append(skill_name)
    
    print(f"\n【已是中文】({len(already_chinese)} 个):")
    for name in already_chinese[:10]:
        print(f"  ✓ {name}")
    if len(already_chinese) > 10:
        print(f"  ... 还有 {len(already_chinese) - 10} 个")
    
    print(f"\n【需要翻译】({len(needs_translation)} 个):")
    for name in needs_translation[:20]:
        print(f"  • {name}")
    if len(needs_translation) > 20:
        print(f"  ... 还有 {len(needs_translation) - 20} 个")
    
    print("\n" + "=" * 60)
    print("使用说明:")
    print("  1. 对 AI 说: '翻译 [技能名] 技能'")
    print("  2. 或: '批量翻译前 10 个技能'")
    print("  3. 或: '翻译所有未翻译的技能'")
    print("=" * 60)

if __name__ == "__main__":
    main()
