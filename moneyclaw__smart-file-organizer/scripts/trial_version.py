#!/usr/bin/env python3
"""
免费试用版 - 限制整理100个文件，展示核心功能
"""

import sys
import os
from pathlib import Path

# 添加父目录到路径，以便导入organize模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.organize import SmartFileOrganizer
import argparse

class TrialOrganizer(SmartFileOrganizer):
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.file_count = 0
        self.max_files = 100  # 试用版限制
        
    def organize_directory(self, directory_path, rename=False, deduplicate=False, preview=False):
        """试用版整理目录（限制文件数量）"""
        dir_path = Path(directory_path).resolve()
        
        if not dir_path.exists() or not dir_path.is_dir():
            self.log_error(f"目录不存在或不是目录: {dir_path}")
            return False
        
        print("="*60)
        print("🧪 智能文件整理助手 - 免费试用版")
        print("="*60)
        print("⚠️  试用版限制: 最多整理100个文件")
        print("💡 购买完整版解锁无限文件整理和高级功能")
        print("💰 价格: $12.99 (一次性购买，永久使用)")
        print("🌐 购买链接: https://clawd.org.cn/skills/smart-file-organizer")
        print("="*60)
        print(f"📁 开始整理目录: {dir_path}")
        
        # 统计文件数量
        total_files = sum(1 for _ in dir_path.rglob("*") if _.is_file())
        if total_files > self.max_files:
            print(f"⚠️  目录包含 {total_files} 个文件，超过试用限制 ({self.max_files})")
            print(f"💡 建议: 选择较小的目录或购买完整版")
            # 非交互模式下自动继续
            print("⏩ 非交互模式，自动整理前100个文件")
            # 如果是脚本调用，自动继续
            # if choice.lower() != 'y':
            #     print("❌ 已取消整理")
            #     return False
        
        # 调用父类方法，但限制处理数量
        self.file_count = 0
        result = super().organize_directory(directory_path, rename, deduplicate, preview)
        
        # 试用版提示
        if self.stats["total_files"] >= self.max_files * 0.8:
            print("\n" + "="*60)
            print("🎯 试用版限制提醒")
            print("="*60)
            print(f"📊 已整理文件: {self.stats['total_files']}/{self.max_files}")
            print("💡 试用版功能限制:")
            print("  • 最多整理100个文件")
            print("  • 不支持自定义配置文件")
            print("  • 不支持批量重命名高级模式")
            print("  • 不支持定时自动整理")
            print("\n🚀 升级到完整版享受:")
            print("  • 无限文件整理")
            print("  • 所有高级功能")
            print("  • 终身免费更新")
            print("  • 优先技术支持")
            print(f"\n💰 仅需 $12.99")
            print("🌐 立即购买: https://clawd.org.cn/skills/smart-file-organizer")
            print("="*60)
        
        return result
    
    def _is_file_safe(self, filepath):
        """试用版安全检查（增加数量限制）"""
        if self.file_count >= self.max_files:
            return False
        
        result = super()._is_file_safe(filepath)
        if result:
            self.file_count += 1
        
        return result

def main():
    parser = argparse.ArgumentParser(description="智能文件整理助手 - 免费试用版")
    parser.add_argument("--path", default=".", help="要整理的目录路径")
    parser.add_argument("--rename", action="store_true", help="启用重命名")
    parser.add_argument("--preview", action="store_true", help="预览模式")
    
    args = parser.parse_args()
    
    # 试用版不支持重复检测
    if hasattr(args, 'deduplicate'):
        args.deduplicate = False
    
    organizer = TrialOrganizer()
    
    # 更新配置
    if args.preview:
        organizer.config["safety"]["preview_mode"] = True
    
    # 执行整理
    success = organizer.organize_directory(
        directory_path=args.path,
        rename=args.rename,
        deduplicate=False,  # 试用版禁用
        preview=args.preview or organizer.config["safety"]["preview_mode"]
    )
    
    if success:
        organizer.print_summary()
        
        # 试用版结束提示
        print("\n" + "="*60)
        print("🎉 试用体验完成!")
        print("="*60)
        print("📊 试用统计:")
        print(f"  整理文件: {organizer.stats['total_files']}个")
        print(f"  重命名文件: {organizer.stats['renamed_files']}个")
        print(f"  发现错误: {organizer.stats['errors']}个")
        
        print("\n💡 完整版功能预览:")
        print("  ✅ 无限文件整理")
        print("  ✅ 重复文件检测和清理")
        print("  ✅ 自定义分类规则")
        print("  ✅ 高级重命名模式")
        print("  ✅ 定时自动整理")
        print("  ✅ 图形用户界面 (即将推出)")
        
        print("\n💰 升级到完整版仅需 $12.99")
        print("🌐 购买链接: https://clawd.org.cn/skills/smart-file-organizer")
        print("📧 问题反馈: feedback@moneyclaw.ai")
        print("="*60)
        
        # 邀请反馈
        print("\n📝 邀请参与测试反馈:")
        print("您的反馈对我们非常重要！请花2分钟填写问卷:")
        print("🔗 https://forms.gle/xxxxx (测试反馈问卷)")
        print("🎁 前50名反馈者将获得8折优惠码!")
        
        # 保存试用记录
        trial_log = Path.cwd() / f"trial_log_{organizer.stats['start_time'][:10]}.txt"
        with open(trial_log, 'w', encoding='utf-8') as f:
            f.write(f"试用时间: {organizer.stats['start_time']}\n")
            f.write(f"整理目录: {args.path}\n")
            f.write(f"整理文件: {organizer.stats['total_files']}\n")
            f.write(f"重命名文件: {organizer.stats['renamed_files']}\n")
            f.write(f"试用状态: {'完成' if success else '失败'}\n")
        
        print(f"\n📄 试用记录已保存: {trial_log}")

if __name__ == "__main__":
    main()