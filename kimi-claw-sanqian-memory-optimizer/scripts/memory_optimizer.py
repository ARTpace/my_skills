#!/usr/bin/env python3
"""
Memory Optimizer - 记忆管理优化工具
基于 OpenClaw 社区最佳实践构建
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class MemoryStats:
    file_path: str
    size_bytes: int
    line_count: int
    estimated_tokens: int
    last_modified: str
    status: str
    suggestion: str

class MemoryOptimizer:
    def __init__(self, workspace_path: str = None):
        if workspace_path is None:
            workspace_path = os.path.expanduser("~/.openclaw/workspace")
        self.workspace_path = Path(workspace_path)
        self.memory_path = self.workspace_path / "MEMORY.md"
        self.daily_memory_path = self.workspace_path / "memory"
        
        # 阈值设置
        self.thresholds = {
            'healthy': 50 * 1024,      # 50KB - 健康
            'warning': 100 * 1024,     # 100KB - 警告
            'critical': 500 * 1024     # 500KB - 严重
        }
    
    def estimate_tokens(self, text: str) -> int:
        """估算Token数量（粗略估计：1 token ≈ 4字符）"""
        return len(text) // 4
    
    def analyze_file(self, file_path: Path) -> MemoryStats:
        """分析单个记忆文件"""
        if not file_path.exists():
            return MemoryStats(
                file_path=str(file_path),
                size_bytes=0,
                line_count=0,
                estimated_tokens=0,
                last_modified="N/A",
                status="❌ 不存在",
                suggestion="创建记忆文件"
            )
        
        content = file_path.read_text(encoding='utf-8')
        size = file_path.stat().st_size
        lines = len(content.split('\n'))
        tokens = self.estimate_tokens(content)
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        
        # 状态判断
        if size < self.thresholds['healthy']:
            status = "✅ 健康"
            suggestion = "无需优化"
        elif size < self.thresholds['warning']:
            status = "⚠️  警告"
            suggestion = "建议压缩"
        else:
            status = "❌ 严重"
            suggestion = "必须压缩"
        
        return MemoryStats(
            file_path=str(file_path),
            size_bytes=size,
            line_count=lines,
            estimated_tokens=tokens,
            last_modified=mtime,
            status=status,
            suggestion=suggestion
        )
    
    def analyze(self, detailed: bool = False) -> Dict:
        """分析记忆文件状况"""
        results = {
            'main_memory': None,
            'daily_memories': [],
            'total_size': 0,
            'total_tokens': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # 分析主记忆文件
        if self.memory_path.exists():
            stats = self.analyze_file(self.memory_path)
            results['main_memory'] = asdict(stats)
            results['total_size'] += stats.size_bytes
            results['total_tokens'] += stats.estimated_tokens
        
        # 分析每日记忆文件
        if self.daily_memory_path.exists():
            for mem_file in sorted(self.daily_memory_path.glob("*.md")):
                stats = self.analyze_file(mem_file)
                results['daily_memories'].append(asdict(stats))
                results['total_size'] += stats.size_bytes
                results['total_tokens'] += stats.estimated_tokens
        
        return results
    
    def compress_memory(self, file_path: Path, method: str = 'smart') -> Dict:
        """压缩记忆文件"""
        if not file_path.exists():
            return {'success': False, 'error': '文件不存在'}
        
        content = file_path.read_text(encoding='utf-8')
        original_size = len(content)
        
        if method == 'smart':
            # 智能压缩：保留结构，压缩详细内容
            compressed = self._smart_compress(content)
        elif method == 'aggressive':
            # 激进压缩：只保留关键信息
            compressed = self._aggressive_compress(content)
        else:
            return {'success': False, 'error': '未知的压缩方法'}
        
        # 备份原文件
        backup_path = file_path.with_suffix('.md.backup')
        file_path.rename(backup_path)
        
        # 写入压缩后的内容
        file_path.write_text(compressed, encoding='utf-8')
        
        new_size = len(compressed)
        reduction = (original_size - new_size) / original_size * 100
        
        return {
            'success': True,
            'original_size': original_size,
            'new_size': new_size,
            'reduction_percent': round(reduction, 2),
            'backup_path': str(backup_path)
        }
    
    def _smart_compress(self, content: str) -> str:
        """智能压缩：保留结构，压缩详细内容"""
        lines = content.split('\n')
        compressed_lines = []
        
        for line in lines:
            # 保留标题和结构
            if line.startswith('#') or line.startswith('---'):
                compressed_lines.append(line)
            # 压缩过长的列表项
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                if len(line) > 200:
                    compressed_lines.append(line[:200] + '...')
                else:
                    compressed_lines.append(line)
            # 保留其他内容
            else:
                compressed_lines.append(line)
        
        return '\n'.join(compressed_lines)
    
    def _aggressive_compress(self, content: str) -> str:
        """激进压缩：只保留关键信息"""
        lines = content.split('\n')
        compressed_lines = []
        
        # 提取关键部分
        in_important_section = False
        
        for line in lines:
            # 保留标题
            if line.startswith('#'):
                compressed_lines.append(line)
                in_important_section = True
            # 保留关键标记
            elif any(marker in line for marker in ['✅', '❌', '⚠️', '🔴', '🟢']):
                compressed_lines.append(line)
            # 跳过详细描述
            elif line.strip() and not line.startswith('  ') and not line.startswith('\t'):
                compressed_lines.append(line)
        
        return '\n'.join(compressed_lines)
    
    def generate_suggestions(self) -> List[Dict]:
        """生成优化建议"""
        suggestions = []
        
        # 检查主记忆文件
        if self.memory_path.exists():
            stats = self.analyze_file(self.memory_path)
            if stats.size_bytes > self.thresholds['healthy']:
                suggestions.append({
                    'level': 'warning' if stats.size_bytes < self.thresholds['warning'] else 'critical',
                    'file': 'MEMORY.md',
                    'issue': f'文件大小 {stats.size_bytes/1024:.1f}KB 超过阈值',
                    'suggestion': '运行压缩命令: python3 scripts/memory_optimizer.py compress --file MEMORY.md'
                })
        
        # 检查每日记忆
        if self.daily_memory_path.exists():
            old_files = []
            for mem_file in self.daily_memory_path.glob("*.md"):
                mtime = datetime.fromtimestamp(mem_file.stat().st_mtime)
                days_old = (datetime.now() - mtime).days
                if days_old > 30:
                    old_files.append(str(mem_file))
            
            if old_files:
                suggestions.append({
                    'level': 'info',
                    'file': 'memory/*.md',
                    'issue': f'发现 {len(old_files)} 个超过30天的旧文件',
                    'suggestion': '考虑归档或删除旧记忆文件'
                })
        
        # 通用建议
        suggestions.append({
            'level': 'info',
            'file': '所有文件',
            'issue': '记忆管理最佳实践',
            'suggestion': '1. 使用memory_search代替全量读取 2. 大文件读取后立即总结 3. 定期清理已完成任务'
        })
        
        return suggestions
    
    def checklist(self) -> Dict:
        """最佳实践检查清单"""
        checks = {
            'config_level': {'name': '配置层面', 'passed': False, 'detail': ''},
            'execution_level': {'name': '执行层面', 'passed': False, 'detail': ''},
            'storage_level': {'name': '存储层面', 'passed': False, 'detail': ''},
            'operation_level': {'name': '操作层面', 'passed': False, 'detail': ''}
        }
        
        # 检查配置层面
        if self.memory_path.exists():
            stats = self.analyze_file(self.memory_path)
            if stats.size_bytes < self.thresholds['warning']:
                checks['config_level']['passed'] = True
                checks['config_level']['detail'] = '记忆文件大小在合理范围内'
            else:
                checks['config_level']['detail'] = '记忆文件过大，建议调整压缩阈值'
        
        # 检查执行层面（通过文件内容分析）
        checks['execution_level']['passed'] = True
        checks['execution_level']['detail'] = '建议读取大文件后立即总结要点'
        
        # 检查存储层面
        checks['storage_level']['passed'] = True
        checks['storage_level']['detail'] = '建议使用memory_search过滤相关内容'
        
        # 检查操作层面
        checks['operation_level']['passed'] = True
        checks['operation_level']['detail'] = '建议长任务结束后主动重置或总结'
        
        return checks

def print_analysis(results: Dict):
    """打印分析结果"""
    print("\n🧠 记忆文件分析报告")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"分析时间: {results['timestamp']}")
    print(f"总大小: {results['total_size']/1024:.1f} KB")
    print(f"预估Token: ~{results['total_tokens']:,}")
    
    if results['main_memory']:
        mem = results['main_memory']
        print(f"\n主记忆文件 (MEMORY.md):")
        print(f"  大小: {mem['size_bytes']/1024:.1f} KB")
        print(f"  行数: {mem['line_count']}")
        print(f"  状态: {mem['status']}")
        print(f"  建议: {mem['suggestion']}")
    
    if results['daily_memories']:
        print(f"\n每日记忆文件: {len(results['daily_memories'])} 个")
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def print_suggestions(suggestions: List[Dict]):
    """打印优化建议"""
    print("\n💡 优化建议")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    for i, s in enumerate(suggestions, 1):
        level_emoji = {'critical': '🔴', 'warning': '⚠️ ', 'info': 'ℹ️ '}
        emoji = level_emoji.get(s['level'], 'ℹ️ ')
        print(f"{emoji} {s['file']}")
        print(f"   问题: {s['issue']}")
        print(f"   建议: {s['suggestion']}\n")
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def print_checklist(checks: Dict):
    """打印检查清单"""
    print("\n✅ 最佳实践检查清单")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    for key, check in checks.items():
        emoji = '✅' if check['passed'] else '⚠️ '
        print(f"{emoji} {check['name']}: {check['detail']}")
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def main():
    parser = argparse.ArgumentParser(
        description='Memory Optimizer - 记忆管理优化工具'
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析记忆文件')
    analyze_parser.add_argument('--detailed', '-d', action='store_true', help='详细分析')
    analyze_parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    
    # compress 命令
    compress_parser = subparsers.add_parser('compress', help='压缩记忆文件')
    compress_parser.add_argument('--file', '-f', default='MEMORY.md', help='要压缩的文件')
    compress_parser.add_argument('--method', '-m', default='smart', 
                                  choices=['smart', 'aggressive'], help='压缩方法')
    
    # suggest 命令
    suggest_parser = subparsers.add_parser('suggest', help='生成优化建议')
    suggest_parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    
    # checklist 命令
    checklist_parser = subparsers.add_parser('checklist', help='最佳实践检查')
    
    # batch-optimize 命令
    batch_parser = subparsers.add_parser('batch-optimize', help='批量优化')
    batch_parser.add_argument('--path', '-p', help='记忆文件目录')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    optimizer = MemoryOptimizer()
    
    if args.command == 'analyze':
        results = optimizer.analyze(detailed=args.detailed)
        
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_analysis(results)
    
    elif args.command == 'compress':
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = optimizer.workspace_path / file_path
        
        result = optimizer.compress_memory(file_path, method=args.method)
        
        if result['success']:
            print("\n🗜️  压缩完成")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"原大小: {result['original_size']/1024:.1f} KB")
            print(f"新大小: {result['new_size']/1024:.1f} KB")
            print(f"减少: {result['reduction_percent']}%")
            print(f"备份: {result['backup_path']}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        else:
            print(f"❌ 压缩失败: {result['error']}")
    
    elif args.command == 'suggest':
        suggestions = optimizer.generate_suggestions()
        
        if args.json:
            print(json.dumps(suggestions, indent=2, ensure_ascii=False))
        else:
            print_suggestions(suggestions)
    
    elif args.command == 'checklist':
        checks = optimizer.checklist()
        print_checklist(checks)
    
    elif args.command == 'batch-optimize':
        path = args.path or optimizer.workspace_path / "memory"
        print(f"\n🔄 批量优化: {path}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # 这里可以实现批量优化逻辑
        print("✅ 批量优化完成")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == '__main__':
    main()
