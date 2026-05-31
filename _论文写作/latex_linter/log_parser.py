#!/usr/bin/env python3
"""
XeLaTeX/Overleaf 编译日志解析器
================================
解析 XeLaTeX 编译产生的 .log 文件，提取 Warning 和 Error 信息。

用法:
    python log_parser.py main.log              # 解析日志，输出报告
    python log_parser.py main.log --json       # JSON 格式

从 Overleaf 下载日志:
    1. 在 Overleaf 项目中，点击 "Logs and output files" 按钮
    2. 点击 "Download log file" (或 "Raw logs")
    3. 将下载的 .log 文件与 main.tex 放在同目录下
"""

import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LogIssue:
    severity: Severity
    code: str
    message: str
    line: int = 0
    context: str = ""
    fixable: bool = False

    def format(self) -> str:
        prefix = {"error": "ERROR", "warning": "WARN ", "info": "INFO "}
        loc = f"L{self.line:04d}" if self.line else "----"
        ctx = f"  → {self.context}" if self.context else ""
        return f"[{prefix[self.severity.value]}][{self.code}] {loc} | {self.message}{ctx}"


def parse_xelatex_log(log_path: str) -> List[LogIssue]:
    """解析 XeLaTeX 编译日志，返回问题列表"""
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    issues = []

    # ----------------------------------------------------------
    # Error patterns
    # ----------------------------------------------------------
    # ! Emergency stop
    for m in re.finditer(r'^!\s+(.+)$', text, re.MULTILINE):
        issues.append(LogIssue(
            Severity.ERROR, "L001",
            f"LaTeX 编译错误: {m.group(1).strip()}",
            context=m.group(0).strip()[:120]
        ))

    # Undefined control sequence
    for m in re.finditer(r'! Undefined control sequence\.\s*\n(l\.(\d+)\s+.*)', text, re.MULTILINE):
        # Extract the problematic line number and content
        line_match = re.search(r'l\.(\d+)\s+(.+)', m.group(0))
        if line_match:
            ln = int(line_match.group(1))
            ctx = line_match.group(2).strip()[:100]
            issues.append(LogIssue(
                Severity.ERROR, "L002",
                f"未定义的控制序列: 编译器不认识此命令",
                line=ln,
                context=ctx[:80]
            ))

    # ----------------------------------------------------------
    # Warning patterns
    # ----------------------------------------------------------
    # LaTeX Warning: Reference ... undefined
    for m in re.finditer(r'LaTeX Warning: Reference `([^`\']+)\' undefined', text):
        issues.append(LogIssue(
            Severity.WARNING, "L101",
            f"引用未定义: '{m.group(1)}'（\\ref 指向不存在的 \\label）",
            context=m.group(0).strip()[:120]
        ))

    # LaTeX Warning: Citation ... undefined
    for m in re.finditer(r'LaTeX Warning: Citation `([^`\']+)\' undefined', text):
        issues.append(LogIssue(
            Severity.WARNING, "L102",
            f"文献引用未定义: '{m.group(1)}'（bibtex/biblatex 中没有此条目）",
            context=m.group(0).strip()[:120]
        ))

    # LaTeX Warning: Label ... multiply defined
    for m in re.finditer(r'LaTeX Warning: Label `([^`\']+)\' multiply defined', text):
        issues.append(LogIssue(
            Severity.WARNING, "L103",
            f"Label 重复定义: '{m.group(1)}'",
            context=m.group(0).strip()[:120]
        ))

    # Overfull \hbox
    for m in re.finditer(r'Overfull \\hbox\s*\(([^)]+)\)', text):
        dims = m.group(1).strip()
        issues.append(LogIssue(
            Severity.WARNING, "L104",
            f"文字溢出边界 (Overfull hbox): 超出 {dims}",
            context=f"内容超出了页面的右边界"
        ))

    # Underfull \hbox
    for m in re.finditer(r'Underfull \\hbox\s*\(([^)]+)\)', text):
        dims = m.group(1).strip()
        issues.append(LogIssue(
            Severity.INFO, "L105",
            f"文字行稀疏 (Underfull hbox): 不足 {dims}",
            context="行内空白过多，可能影响排版美观"
        ))

    # Overfull \vbox
    for m in re.finditer(r'Overfull \\vbox\s*\(([^)]+)\)', text):
        dims = m.group(1).strip()
        issues.append(LogIssue(
            Severity.WARNING, "L106",
            f"垂直溢出 (Overfull vbox): 超出 {dims}",
            context="内容超出页面底部，可能是表格或图片过大"
        ))

    # Fontspec warnings
    for m in re.finditer(r'LaTeX Font Warning: (.+)$', text, re.MULTILINE):
        msg = m.group(1).strip()
        if 'Font shape' in msg and 'substituted' in msg:
            issues.append(LogIssue(
                Severity.WARNING, "L107",
                f"字体形状被替换: {msg[:100]}",
                context="某种字体形状不可用，被替换为默认字体"
            ))

    # Missing character
    for m in re.finditer(r'Missing character: There is no ([^"]+) in font', text):
        issues.append(LogIssue(
            Severity.WARNING, "L108",
            f"字体缺失字符: {m.group(1).strip()}",
            context="该字符在当前字体中不存在，显示为空白/tofu"
        ))

    # Underfull \vbox (pages)
    for m in re.finditer(r'Underfull \\vbox\s*\(([^)]+)\)', text):
        dims = m.group(1).strip()
        issues.append(LogIssue(
            Severity.INFO, "L109",
            f"页面内容不足 (Underfull vbox): 不足 {dims}",
            context="页面内容过少，可能在页面底部留有大片空白"
        ))

    # No file (missing .aux, .toc, etc.)
    for m in re.finditer(r'No file (.+?)\.', text):
        filename = m.group(1).strip()
        if filename.endswith(('.aux', '.toc', '.lof', '.lot')):
            issues.append(LogIssue(
                Severity.INFO, "L110",
                f"缺少辅助文件: {filename}（首次编译正常现象，再编译一次即可）",
                context=m.group(0).strip()
            ))

    # Rerun warnings
    for m in re.finditer(r'LaTeX Warning: Label\(s\) may have changed\. Rerun', text):
        issues.append(LogIssue(
            Severity.INFO, "L111",
            "Label 可能已变，需要再次编译（rerun）",
            context="引用编号需要二次编译才能同步"
        ))

    # Package-specific warnings that are safe to ignore
    # (skip — these are informational only)

    return issues


def report_log(issues: List[LogIssue]) -> str:
    """生成日志分析报告"""
    if not issues:
        return "✓ 编译日志中未发现问题。"

    errors = [i for i in issues if i.severity == Severity.ERROR]
    warnings = [i for i in issues if i.severity == Severity.WARNING]
    infos = [i for i in issues if i.severity == Severity.INFO]

    lines = []
    lines.append(f"{'='*60}")
    lines.append("XeLaTeX 编译日志分析报告")
    lines.append(f"{'='*60}")
    lines.append(f"  Errors:   {len(errors)}")
    lines.append(f"  Warnings: {len(warnings)}")
    lines.append(f"  Info:     {len(infos)}")
    lines.append("")

    for section, items in [("ERRORS", errors), ("WARNINGS", warnings), ("INFO", infos)]:
        if items:
            lines.append(f"--- {section} ---")
            for item in items:
                lines.append(item.format())
            lines.append("")

    return '\n'.join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="XeLaTeX/Overleaf 编译日志解析器")
    parser.add_argument("logfile", help="XeLaTeX .log 文件路径")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    log_path = Path(args.logfile)
    if not log_path.exists():
        print(f"错误: 文件不存在: {args.logfile}", file=sys.stderr)
        sys.exit(1)

    issues = parse_xelatex_log(str(log_path))

    if args.json:
        print(json.dumps([
            {
                "severity": i.severity.value,
                "code": i.code,
                "message": i.message,
                "line": i.line,
                "context": i.context,
            }
            for i in issues
        ], ensure_ascii=False, indent=2))
    else:
        print(report_log(issues))

    error_count = sum(1 for i in issues if i.severity == Severity.ERROR)
    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
