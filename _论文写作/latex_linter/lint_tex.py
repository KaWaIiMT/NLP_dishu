#!/usr/bin/env python3
"""
LaTeX 论文格式检查与修复工具
==============================
针对 Pandoc (Markdown → LaTeX) + ctexart (XeLaTeX) 工作流的静态格式检查器。

用法:
    python lint_tex.py main.tex                     # 仅检查，输出报告
    python lint_tex.py main.tex --fix               # 检查并自动修复
    python lint_tex.py main.tex --log main.log      # 结合编译日志检查
    python lint_tex.py main.tex --json              # JSON 输出
    python lint_tex.py main.tex --fix --dry-run     # 预览修复但不写入

检查项目 (E=Error会编译失败, W=Warning可能格式异常, I=Info风格建议):
    E001  环境配对不平衡 (begin/end mismatch)
    E002  document 环境缺失
    E003  数学模式分隔符不配对 ($)
    E004  documentclass 必须在 usepackage 之前
    W001  重复的 label
    W002  引用了不存在的 label
    W003  空命令 (section/caption/label 等)
    W004  引用的图片/文件不存在
    W005  表格列数过多 (含 CJK 文字时容易超宽)
    W006  Pandoc 残留物 (tightlist, passthrough)
    W007  重复的章节标题
    W008  连续空行过多
    W009  caption 为空
    W010  不规范的空白字符
    I001  newpage 出现在文档末尾
    I002  建议的包是否缺失
"""

import re
import sys
import os
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Tuple, Optional


# ============================================================
# Data structures
# ============================================================

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
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


@dataclass
class Fix:
    line: int
    old: str
    new: str
    description: str


# ============================================================
# LaTeX Checker
# ============================================================

class LaTeXChecker:
    """LaTeX 静态格式检查器"""

    def __init__(self, filepath: str, figures_dir: str = None):
        self.filepath = Path(filepath)
        self.figures_dir = Path(figures_dir) if figures_dir else self.filepath.parent / "figures"
        self.text = ""
        self.lines: List[str] = []
        self.issues: List[Issue] = []
        self.fixes: List[Fix] = []

        # Cached extractions
        self._labels: Dict[str, int] = {}       # label_value → line_number
        self._refs: Dict[str, List[int]] = defaultdict(list)  # ref_value → [lines]
        self._environments: List[Tuple[str, int, bool]] = []  # (env_name, line, is_begin)
        self._sections: Dict[str, List[int]] = defaultdict(list)

    def load(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.lines = self.text.split('\n')

    # ----------------------------------------------------------
    # E001: 环境配对检查
    # ----------------------------------------------------------
    def _check_environment_balance(self):
        """检查 \\begin{} 和 \\end{} 是否配对"""
        # Extract all environments, ignoring comments and verbatim-like envs
        text_no_comment = re.sub(r'(?<!\\)%.*$', '', self.text, flags=re.MULTILINE)

        begins = re.finditer(r'\\(begin|end)\{([^}]+)\}', text_no_comment)
        stack: List[Tuple[str, int]] = []  # (env_name, line_number)

        for m in begins:
            cmd_type = m.group(1)  # "begin" or "end"
            env_name = m.group(2)
            # Calculate line number from position
            line_num = self.text[:m.start()].count('\n') + 1

            if '*' in env_name:
                # Handle starred envs: align*, equation*, etc.
                # begin{align*} ... end{align*} — they must match exactly
                pass

            if cmd_type == "begin":
                stack.append((env_name, line_num))
            else:  # "end"
                if not stack:
                    self.issues.append(Issue(
                        Severity.ERROR, "E001",
                        f"多余的 \\end{{{env_name}}}，前面没有对应的 \\begin",
                        line_num,
                        f"\\end{{{env_name}}}",
                        fixable=False
                    ))
                else:
                    expected_env, begin_line = stack.pop()
                    if expected_env != env_name:
                        self.issues.append(Issue(
                            Severity.ERROR, "E001",
                            f"环境不匹配：\\begin{{{expected_env}}} (L{begin_line}) 被 \\end{{{env_name}}} 关闭",
                            line_num,
                            f"期望 \\end{{{expected_env}}}，实际 \\end{{{env_name}}}",
                            fixable=True
                        ))
                        self.fixes.append(Fix(
                            line_num,
                            f"\\end{{{env_name}}}",
                            f"\\end{{{expected_env}}}",
                            f"修正环境名 {env_name} → {expected_env}"
                        ))

        # Remaining unclosed environments
        for env_name, begin_line in reversed(stack):
            self.issues.append(Issue(
                Severity.ERROR, "E001",
                f"未关闭的环境：\\begin{{{env_name}}} (L{begin_line}) 缺少 \\end{{{env_name}}}",
                begin_line,
                f"\\begin{{{env_name}}}",
                fixable=False
            ))

    # ----------------------------------------------------------
    # E002: document 环境
    # ----------------------------------------------------------
    def _check_document_structure(self):
        """检查 document 环境和 documentclass 顺序"""
        has_begin = bool(re.search(r'\\begin\{document\}', self.text))
        has_end = bool(re.search(r'\\end\{document\}', self.text))

        if not has_begin:
            self.issues.append(Issue(
                Severity.ERROR, "E002",
                "缺少 \\begin{document}",
                fixable=False
            ))
        if not has_end:
            line_num = len(self.lines)
            self.issues.append(Issue(
                Severity.ERROR, "E002",
                "缺少 \\end{document}",
                line_num,
                fixable=True
            ))
            self.fixes.append(Fix(
                line_num,
                "",
                "\\end{document}\n",
                "在文件末尾添加 \\end{document}"
            ))

        # Check \documentclass is before \usepackage
        docclass_pos = None
        usepackage_positions = []
        for i, line in enumerate(self.lines, 1):
            if '\\documentclass' in line and not line.strip().startswith('%'):
                docclass_pos = i
            if '\\usepackage' in line and not line.strip().startswith('%'):
                usepackage_positions.append(i)

        if docclass_pos and usepackage_positions:
            for pkg_line in usepackage_positions:
                if pkg_line < docclass_pos:
                    self.issues.append(Issue(
                        Severity.ERROR, "E004",
                        f"\\usepackage 出现在 \\documentclass 之前",
                        pkg_line,
                        self.lines[pkg_line - 1].strip(),
                        fixable=False
                    ))

    # ----------------------------------------------------------
    # E003: 数学模式配对
    # ----------------------------------------------------------
    def _check_math_delimiters(self):
        """检查 $...$ 是否配对（跨整个文档，因为数学模式可以跨行）"""
        # Remove comments
        clean = re.sub(r'(?<!\\)%.*$', '', self.text, flags=re.MULTILINE)
        # Count all unescaped $ in the entire document
        dollar_positions = [(m.start(), m.group()) for m in re.finditer(r'(?<!\\)\$', clean)]

        if len(dollar_positions) % 2 != 0:
            # Find the approximate line of the first unmatched $
            # Report a few problem spots
            # Count until we find the position where it becomes unbalanced
            stack = 0
            for pos, _ in dollar_positions:
                stack += 1
                line_num = clean[:pos].count('\n') + 1
                if stack % 2 == 1:
                    # This is an opening $
                    pass
                else:
                    # This is a closing $
                    pass

            # Report the general issue with problem locations
            # Find the first uneven position
            line_num = clean[:dollar_positions[-1][0]].count('\n') + 1
            self.issues.append(Issue(
                Severity.ERROR, "E003",
                f"数学模式 $ 符号不配对：文档中共 {len(dollar_positions)} 个 $ 符号（奇数个）",
                line_num,
                "检查是否缺少闭合的 $，特别是表格编号附近（如 \\textbf{表$3.1} 缺少闭合 $）",
                fixable=False
            ))

    # ----------------------------------------------------------
    # W011: 半开数学模式（$N.N 模式，Pandoc 常见问题）
    # ----------------------------------------------------------
    def _check_math_number_refs(self):
        """检查文档中的半开数学模式。

        扫描每一行（去除注释），检测行内 $ 符号数量为奇数的情况。
        当一行内有奇数个 $ 且包含 CJK 文字时，说明存在未闭合的数学模式，
        通常是 Pandoc 输出的 $N.N 模式缺少闭合 $ 导致的。
        只报告每一行的第一个问题。
        """
        for i, line in enumerate(self.lines, 1):
            clean = re.sub(r'(?<!\\)%.*$', '', line)
            # Count $ not preceded by \
            dollar_positions = [m.start() for m in re.finditer(r'(?<!\\)\$', clean)]
            dollar_count = len(dollar_positions)

            if dollar_count == 0:
                continue
            if dollar_count % 2 == 0:
                continue

            # Odd count: some $ is unclosed on this line.
            # Check if the line contains CJK chars (meaning text is being rendered as math)
            if not re.search(r'[一-鿿]', clean):
                # No CJK — might be a legitimate multi-line math expression
                continue

            # Find the first unclosed $ — walk through the $ signs on this line
            # and check which one opens a math block that contains CJK text
            in_math = False
            math_start = 0
            for pos in dollar_positions:
                if not in_math:
                    in_math = True
                    math_start = pos
                else:
                    # Math closed — check if segment contained CJK
                    segment = clean[math_start + 1:pos]
                    if re.search(r'[一-鿿]', segment):
                        # Found a problematic segment
                        # Try to identify the root cause number
                        num_match = re.search(r'^(\d+(?:\.\d+)?)', segment)
                        num_str = num_match.group(1) if num_match else ""
                        self.issues.append(Issue(
                            Severity.WARNING, "W011",
                            f"半开数学模式: 行内 $ 数量为奇数，中文文字可能被渲染为数学模式",
                            i,
                            f"检查 ${{{num_str}}} 是否遗漏了闭合的 $" if num_str else "该行 $ 数量为奇数，需手动检查配对",
                            fixable=bool(num_str)
                        ))
                        if num_str:
                            self.fixes.append(Fix(
                                i,
                                f"${num_str}",
                                f"${num_str}$",
                                f"闭合数学: ${num_str} → ${num_str}$"
                            ))
                        break  # One issue per line is enough
                    in_math = False

            # Handle lone $ (only 1 $, math opened but never closed on this line)
            if not in_math:
                continue
            segment = clean[math_start + 1:]
            num_match = re.match(r'^(\d+(?:\.\d+)?)\}', segment)
            if num_match:
                num_str = num_match.group(1)
                self.issues.append(Issue(
                    Severity.WARNING, "W011",
                    f"半开数学模式: ${{{num_str}}} 缺少闭合的 $",
                    i,
                    f"检查 ${{{num_str}}} 是否遗漏了闭合的 $",
                    fixable=True
                ))
                self.fixes.append(Fix(
                    i,
                    f"${num_str}",
                    f"${num_str}$",
                    f"闭合数学: ${num_str} → ${num_str}$"
                ))
            elif re.search(r'[一-鿿]', segment):
                self.issues.append(Issue(
                    Severity.WARNING, "W011",
                    f"半开数学模式: 行内 $ 数量为奇数，中文文字可能被渲染为数学模式",
                    i,
                    "该行 $ 数量为奇数，需手动检查配对",
                    fixable=False
                ))

    # ----------------------------------------------------------
    # W001 / W002: Labels and References
    # ----------------------------------------------------------
    def _check_labels(self):
        """检查 label 重复"""
        labels_seen: Dict[str, int] = {}  # label → first_line
        for i, line in enumerate(self.lines, 1):
            for m in re.finditer(r'\\label\{([^}]+)\}', line):
                lbl = m.group(1)
                if lbl in labels_seen:
                    self.issues.append(Issue(
                        Severity.WARNING, "W001",
                        f"重复的 label: '{lbl}'（首次出现在 L{labels_seen[lbl]}）",
                        i,
                        line.strip()[:80],
                        fixable=True
                    ))
                    # Generate unique label
                    new_lbl = f"{lbl}_dup{i}"
                    self.fixes.append(Fix(
                        i,
                        f"\\label{{{lbl}}}",
                        f"\\label{{{new_lbl}}}",
                        f"重命名重复的 label: {lbl} → {new_lbl}"
                    ))
                else:
                    labels_seen[lbl] = i
                self._labels[lbl] = i

    def _check_references(self):
        """检查引用了不存在的 label"""
        all_refs: Dict[str, List[int]] = defaultdict(list)
        for i, line in enumerate(self.lines, 1):
            for m in re.finditer(r'\\(?:ref|eqref|autoref|pageref|cite|citep|citeproc)\{([^}]+)\}', line):
                ref_val = m.group(1)
                all_refs[ref_val].append(i)

        # Also catch \textsuperscript{[N]} — these are resolved citeproc refs, skip
        # Check refs against labels
        for ref_val, line_nums in all_refs.items():
            # Skip multi-key refs like [1--6]
            if '--' in ref_val or ',' in ref_val:
                continue
            if ref_val not in self._labels:
                for ln in line_nums:
                    self.issues.append(Issue(
                        Severity.WARNING, "W002",
                        f"引用了不存在的 label: '{ref_val}'",
                        ln,
                        self.lines[ln - 1].strip()[:80],
                        fixable=False
                    ))

    # ----------------------------------------------------------
    # W003 / W009: Empty commands
    # ----------------------------------------------------------
    def _check_empty_commands(self):
        """检查空的命令"""
        checks = [
            (r'\\section\*?\{\s*\}', "空的 \\section{}"),
            (r'\\subsection\*?\{\s*\}', "空的 \\subsection{}"),
            (r'\\subsubsection\*?\{\s*\}', "空的 \\subsubsection{}"),
            (r'\\caption\{\s*\}', "空的 \\caption{}（表格/图片标题为空）", "W009"),
            (r'\\textbf\{\s*\}', "空的 \\textbf{}"),
            (r'\\emph\{\s*\}', "空的 \\emph{}"),
            (r'\\texttt\{\s*\}', "空的 \\texttt{}"),
            (r'\\label\{\s*\}', "空的 \\label{}"),
            (r'\\ref\{\s*\}', "空的 \\ref{}"),
        ]
        for i, line in enumerate(self.lines, 1):
            if line.strip().startswith('%'):
                continue
            for pattern, msg, *codes in checks:
                if re.search(pattern, line):
                    code = codes[0] if codes else "W003"
                    self.issues.append(Issue(
                        Severity.ERROR if code == "W003" else Severity.WARNING,
                        code,
                        msg,
                        i,
                        line.strip()[:80],
                        fixable=False
                    ))

    # ----------------------------------------------------------
    # W004: Figure files
    # ----------------------------------------------------------
    def _check_figures(self):
        """检查引用的图片文件是否存在"""
        # Find all \includegraphics{...}
        for i, line in enumerate(self.lines, 1):
            for m in re.finditer(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}', line):
                filename = m.group(1)
                # Handle paths without extension (LaTeX auto-adds)
                found = False
                for ext in ['', '.pdf', '.png', '.jpg', '.eps', '.jpeg']:
                    candidate = self.figures_dir / (filename + ext)
                    if candidate.exists():
                        found = True
                        break
                    # Also check relative to main tex file
                    candidate2 = self.filepath.parent / (filename + ext)
                    if candidate2.exists():
                        found = True
                        break

                if not found:
                    self.issues.append(Issue(
                        Severity.WARNING, "W004",
                        f"图片文件不存在: '{filename}'（在 {self.figures_dir} 中未找到）",
                        i,
                        line.strip()[:80],
                        fixable=False
                    ))

    # ----------------------------------------------------------
    # W005: Table column count
    # ----------------------------------------------------------
    def _check_tables(self):
        """检查表格列数，含中文时多列容易超宽"""
        # Find tabular column specs
        for i, line in enumerate(self.lines, 1):
            m = re.search(r'\\begin\{tabular\}\{([^}]*)\}', line)
            if m:
                colspec = m.group(1)
                # Count actual column definitions (l, c, r, p{...}, etc.)
                col_count = len(re.findall(r'[lcr](?:\{[^}]*\})?|\|[^lcr]*[lcr]', colspec))
                if col_count == 0:
                    # Fallback: count | separators + baseline columns
                    col_count = len(re.findall(r'[lcr]', colspec))

                if col_count >= 6:
                    # Check if there's CJK content nearby (next 20 lines)
                    has_cjk = False
                    for j in range(i, min(i + 30, len(self.lines))):
                        if re.search(r'[一-鿿]', self.lines[j]):
                            has_cjk = True
                            break

                    sev = Severity.WARNING if (has_cjk and col_count >= 7) else Severity.INFO
                    code = "W005" if sev == Severity.WARNING else "I005"
                    self.issues.append(Issue(
                        sev, code,
                        f"表格有 {col_count} 列{'，含 CJK 文字，极易超宽' if has_cjk else '，注意页宽'}",
                        i,
                        f"列定义: {colspec[:60]}",
                        fixable=False
                    ))

    # ----------------------------------------------------------
    # W006: Pandoc artifacts
    # ----------------------------------------------------------
    def _check_pandoc_artifacts(self):
        """检查 Pandoc 残留物"""
        artifacts = [
            ('\\tightlist', "Pandoc 残留: \\tightlist 在 ctex 中无效"),
            ('\\passthrough{', "Pandoc 残留: \\passthrough 应被展开"),
            ('\\def\\LTcaptype', "Pandoc 残留: longtable 配置应被替换为 tabular"),
        ]
        for i, line in enumerate(self.lines, 1):
            for pattern, msg in artifacts:
                if pattern in line:
                    # tightlist fix
                    fixable = pattern == '\\tightlist'
                    self.issues.append(Issue(
                        Severity.WARNING, "W006",
                        msg,
                        i,
                        line.strip()[:80],
                        fixable=fixable
                    ))
                    if fixable:
                        self.fixes.append(Fix(
                            i,
                            line,
                            line.replace('\\tightlist', ''),
                            "移除 \\tightlist"
                        ))

    # ----------------------------------------------------------
    # W007: Duplicate section titles
    # ----------------------------------------------------------
    def _check_duplicate_titles(self):
        """检查重复的章节标题"""
        title_pattern = re.compile(r'\\(section|subsection|subsubsection|chapter)\*?\{([^}]+)\}')
        titles: Dict[str, List[Tuple[int, str]]] = defaultdict(list)

        for i, line in enumerate(self.lines, 1):
            for m in title_pattern.finditer(line):
                level = m.group(1)
                title_text = m.group(2).strip()
                key = f"{level}:{title_text}"
                titles[key].append((i, title_text))

        for key, occurrences in titles.items():
            if len(occurrences) > 1:
                lines_str = ", ".join(f"L{ln}" for ln, _ in occurrences)
                self.issues.append(Issue(
                    Severity.WARNING, "W007",
                    f"重复的章节标题: '{occurrences[0][1]}' 出现在 {lines_str}",
                    occurrences[1][0],
                    f"首次 L{occurrences[0][0]}",
                    fixable=False
                ))

    # ----------------------------------------------------------
    # W008: 连续空行
    # ----------------------------------------------------------
    def _check_formatting_issues(self):
        """检查格式问题：连续空行、尾部空白、不规范字符等"""
        blank_run = 0
        for i, line in enumerate(self.lines, 1):
            if line.strip() == '':
                blank_run += 1
            else:
                if blank_run >= 3:
                    self.issues.append(Issue(
                        Severity.WARNING, "W008",
                        f"连续 {blank_run} 个空行（L{i - blank_run}–L{i - 1}），建议合并为 1-2 行",
                        i - blank_run,
                        fixable=True
                    ))
                blank_run = 0

        # Check trailing whitespace
        for i, line in enumerate(self.lines, 1):
            if line.endswith(' ') or line.endswith('\t'):
                self.issues.append(Issue(
                    Severity.INFO, "W010",
                    "行尾有空白字符",
                    i,
                    fixable=True
                ))
                self.fixes.append(Fix(
                    i,
                    line,
                    line.rstrip(),
                    "移除行尾空白"
                ))

        # Check for \newpage at very end (before \end{document})
        for i in range(len(self.lines) - 1, max(len(self.lines) - 10, 0), -1):
            if '\\newpage' in self.lines[i] and '\\end{document}' in self.text:
                # Check if \end{document} is within 3 lines after
                nearby = '\n'.join(self.lines[i:min(i + 4, len(self.lines))])
                if '\\end{document}' in nearby:
                    self.issues.append(Issue(
                        Severity.INFO, "I001",
                        "文档末尾有多余的 \\newpage（\\end{document} 前会自动换页）",
                        i + 1,
                        self.lines[i].strip()[:60],
                        fixable=True
                    ))
                    self.fixes.append(Fix(
                        i + 1,
                        self.lines[i],
                        '',
                        "移除末尾多余的 \\newpage"
                    ))

    # ----------------------------------------------------------
    # I003: Recommended packages
    # ----------------------------------------------------------
    def _check_recommended_packages(self):
        """检查建议使用的包是否缺失（仅 ctexart 中文论文）"""
        recommended = {
            'booktabs': '专业表格线 (\\toprule, \\midrule, \\bottomrule)',
            'graphicx': '图片支持',
            'hyperref': '超链接支持',
            'amsmath': '数学公式增强',
            'geometry': '页面边距设置',
            'setspace': '行距设置',
        }
        for pkg, desc in recommended.items():
            # Check for \usepackage{pkg} or \usepackage[opts]{pkg} or \usepackage{pkg1,pkg2,...}
            found = bool(re.search(rf'\\usepackage(?:\[.*?\])?\{{[^}}]*\b{re.escape(pkg)}\b[^}}]*\}}', self.text))
            if not found:
                    self.issues.append(Issue(
                        Severity.INFO, "I002",
                        f"建议添加: \\usepackage{{{pkg}}} ({desc})",
                        fixable=False
                    ))

    # ----------------------------------------------------------
    # Run all checks
    # ----------------------------------------------------------
    def check_all(self):
        self.issues = []
        self._check_environment_balance()
        self._check_document_structure()
        self._check_math_delimiters()
        self._check_math_number_refs()
        self._check_labels()
        self._check_references()
        self._check_empty_commands()
        self._check_figures()
        self._check_tables()
        self._check_pandoc_artifacts()
        self._check_duplicate_titles()
        self._check_formatting_issues()
        self._check_recommended_packages()
        return self.issues

    # ----------------------------------------------------------
    # Auto-fix
    # ----------------------------------------------------------
    def apply_fixes(self, dry_run: bool = False) -> List[str]:
        """应用所有可自动修复的问题，返回修改描述列表"""
        if not self.fixes:
            return []

        # Sort fixes by line number (descending, to preserve line numbers)
        sorted_fixes = sorted(self.fixes, key=lambda f: f.line, reverse=True)
        applied = []
        new_lines = list(self.lines)

        for fix in sorted_fixes:
            idx = fix.line - 1
            if idx < 0 or idx >= len(new_lines):
                continue

            if fix.new == '':  # Remove line
                if not dry_run:
                    new_lines.pop(idx)
                applied.append(f"  L{fix.line}: 删除 ─ {fix.description}")
            elif fix.old == '':  # Insert new line (at end)
                if not dry_run:
                    new_lines.append(fix.new)
                applied.append(f"  L{fix.line}: 添加 ─ {fix.description}")
            else:  # Replace
                if fix.old in new_lines[idx]:
                    if not dry_run:
                        new_lines[idx] = new_lines[idx].replace(fix.old, fix.new, 1)
                    applied.append(f"  L{fix.line}: 替换 ─ {fix.description}")
                else:
                    # Try line-level match
                    if not dry_run:
                        new_lines[idx] = fix.new if fix.new else new_lines[idx]
                    applied.append(f"  L{fix.line}: 替换整行 ─ {fix.description}")

        if not dry_run:
            self.text = '\n'.join(new_lines)
            self.lines = new_lines
            # Remove 3+ consecutive blank lines
            self.text = re.sub(r'\n{3,}', '\n\n', self.text)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(self.text)

        return applied

    # ----------------------------------------------------------
    # Report
    # ----------------------------------------------------------
    def report(self, show_fixes: bool = False) -> str:
        """生成可读的报告"""
        if not self.issues:
            return "✓ 未发现格式问题。"

        errors = [i for i in self.issues if i.severity == Severity.ERROR]
        warnings = [i for i in self.issues if i.severity == Severity.WARNING]
        infos = [i for i in self.issues if i.severity == Severity.INFO]

        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"LaTeX 格式检查报告: {self.filepath.name}")
        lines.append(f"{'='*60}")
        lines.append(f"  Errors:   {len(errors)}  (会导致编译失败)")
        lines.append(f"  Warnings: {len(warnings)} (可能导致格式问题)")
        lines.append(f"  Info:     {len(infos)}   (风格建议)")
        lines.append(f"  Fixable:  {len(self.fixes)}  (可自动修复)")
        lines.append("")

        for section, items in [("ERRORS", errors), ("WARNINGS", warnings), ("INFO", infos)]:
            if items:
                lines.append(f"--- {section} ---")
                for item in items:
                    lines.append(item.format())
                lines.append("")

        if show_fixes and self.fixes:
            lines.append("--- AUTO-FIX AVAILABLE ---")
            for fix in self.fixes:
                lines.append(f"  L{fix.line}: {fix.description}")
            lines.append(f"  共 {len(self.fixes)} 处可自动修复")
            lines.append("")

        return '\n'.join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "file": str(self.filepath),
            "summary": {
                "errors": sum(1 for i in self.issues if i.severity == Severity.ERROR),
                "warnings": sum(1 for i in self.issues if i.severity == Severity.WARNING),
                "info": sum(1 for i in self.issues if i.severity == Severity.INFO),
                "fixable": len(self.fixes),
            },
            "issues": [
                {
                    "severity": i.severity.value,
                    "code": i.code,
                    "message": i.message,
                    "line": i.line,
                    "context": i.context,
                    "fixable": i.fixable,
                }
                for i in self.issues
            ],
            "fixes": [
                {"line": f.line, "old": f.old, "new": f.new, "description": f.description}
                for f in self.fixes
            ]
        }, ensure_ascii=False, indent=2)


# ============================================================
# CLI
# ============================================================

def main():
    # Fix Windows console encoding
    import io
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(
        description="LaTeX 论文格式检查与修复工具 (Pandoc + ctexart/XeLaTeX 工作流)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python lint_tex.py main.tex                    # 检查并输出报告
  python lint_tex.py main.tex --fix              # 检查并自动修复
  python lint_tex.py main.tex --fix --dry-run    # 预览修复但不写入
  python lint_tex.py main.tex --json             # JSON 格式（CI 集成）
  python lint_tex.py main.tex --log main.log     # 结合编译日志
        """
    )
    parser.add_argument("texfile", help="LaTeX 文件路径")
    parser.add_argument("--fix", action="store_true", help="自动修复可修复的问题")
    parser.add_argument("--dry-run", action="store_true", help="预览修复但不实际写入")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--figures-dir", help="图片目录（默认: 同目录下的 figures/）")
    parser.add_argument("--log", help="Overleaf .log 文件路径（编译日志分析）")
    parser.add_argument("--ci", action="store_true", help="CI 模式: 有 Error 时 exit 1")

    args = parser.parse_args()

    tex_path = Path(args.texfile)
    if not tex_path.exists():
        print(f"错误: 文件不存在: {args.texfile}", file=sys.stderr)
        sys.exit(1)

    checker = LaTeXChecker(str(tex_path), args.figures_dir)
    checker.load()
    checker.check_all()

    # If log file provided, parse it and merge issues
    if args.log:
        log_path = Path(args.log)
        if log_path.exists():
            from log_parser import parse_xelatex_log
            log_issues = parse_xelatex_log(str(log_path))
            checker.issues.extend(log_issues)
        else:
            print(f"警告: 日志文件不存在: {args.log}", file=sys.stderr)

    # Auto-fix
    if args.fix:
        applied = checker.apply_fixes(dry_run=args.dry_run)
        if args.dry_run:
            print("[DRY RUN] 以下修复将被应用（未实际修改文件）:\n")
            for a in applied:
                print(a)
            print()
        else:
            if applied:
                print(f"已应用 {len(applied)} 处修复:\n")
                for a in applied:
                    print(a)
                print()
            # Re-check after fixes
            checker.load()
            checker.check_all()

    # Output
    if args.json:
        print(checker.to_json())
    else:
        print(checker.report(show_fixes=not args.fix))

    # CI mode: exit with error code if errors found
    error_count = sum(1 for i in checker.issues if i.severity == Severity.ERROR)
    if args.ci and error_count > 0:
        sys.exit(1)
    # Also exit 1 if any errors (non-ci mode but useful for scripts)
    if error_count > 0 and not args.json:
        print(f"→ 发现 {error_count} 个会导致编译失败的问题，请修复后再编译。")
        sys.exit(1)


if __name__ == "__main__":
    main()
