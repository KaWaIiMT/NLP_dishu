#!/usr/bin/env python3
"""
论文格式一键修复脚本
====================
针对 Pandoc → ctexart (XeLaTeX) 工作流的常见问题进行批量修复。

用法:
    python fix_paper.py                                            # 修复 + 检查
    python fix_paper.py --check-only                               # 仅检查不修复
    python fix_paper.py --build                                    # 先 build_overleaf 再修复

解决的问题:
    1. `$N.N` 缺少闭合 $  →  自动补全
    2. `\_gloss$` 多余 $  →  移除多余 $
    3. 重复章节标题           →  检测 + 建议
    4. 空 \\caption{}        →  移除
    5. Pandoc 残留           →  移除 \\tightlist 等
"""

import subprocess, re, sys, os
from pathlib import Path

BASE = Path(r"D:\_College\NLP\Research\_论文写作")
MAIN_TEX = BASE / "output" / "overleaf" / "main.tex"
FIGURES_DIR = BASE / "output" / "overleaf" / "figures"
LINT_SCRIPT = BASE / "latex_linter" / "lint_tex.py"
BUILD_SCRIPT = BASE / "build_overleaf.py"


def fix_stray_dollar_in_tex(path: Path) -> int:
    """修复 literal\_gloss$ → literal\_gloss 等多余 $ 模式"""
    text = path.read_text(encoding='utf-8')
    original = text

    # Fix: \_varname$ followed by CJK text — remove the stray $
    # These come from Pandoc wrapping underscores in $ unnecessarily
    patterns = [
        (r'(literal\\_gloss)\$', r'\1'),
        (r'(morphological\\_features)\$', r'\1'),
        (r'(pragmatic\\_meaning)\$', r'\1'),
        (r'(free\\_translation)\$', r'\1'),
        (r'(semantic\\_primitives)\$', r'\1'),
        (r'(discourse\\_relation)\$', r'\1'),
        (r'(pos\\_like\\_category)\$', r'\1'),
    ]

    for pat, repl in patterns:
        new_text = re.sub(pat, repl, text)
        if new_text != text:
            count = len(re.findall(pat, text))
            print(f"  修复: {pat} → {repl} ({count} 处)")
            text = new_text

    # Remove empty \caption{} lines
    lines = text.split('\n')
    new_lines = [l for l in lines if l.strip() != r'\caption{}']
    if len(new_lines) < len(lines):
        print(f"  修复: 移除 {len(lines) - len(new_lines)} 行空 \\caption{{}}")
        text = '\n'.join(new_lines)

    if text != original:
        path.write_text(text, encoding='utf-8')
        return len(original) - len(text)
    return 0


def run_linter(fix: bool = True) -> int:
    """运行 lint_tex.py"""
    cmd = ["python", str(LINT_SCRIPT), str(MAIN_TEX),
           "--figures-dir", str(FIGURES_DIR)]
    if fix:
        cmd.append("--fix")

    result = subprocess.run(cmd, capture_output=True, text=True,
                           encoding='utf-8', timeout=60)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def main():
    import argparse
    parser = argparse.ArgumentParser(description="论文格式一键修复")
    parser.add_argument("--check-only", action="store_true",
                       help="仅检查不修复")
    parser.add_argument("--build", action="store_true",
                       help="先运行 build_overleaf.py")
    args = parser.parse_args()

    # Step 0: Build if requested
    if args.build:
        print("[1/3] build_overleaf.py → main.tex")
        subprocess.run(["python", str(BUILD_SCRIPT)], check=True, timeout=120)

    # Step 1: Fix known Pandoc→LaTeX artifacts in main.tex
    if not args.check_only and MAIN_TEX.exists():
        print("[2/3] 手动修复已知 Pandoc 产物...")
        fix_stray_dollar_in_tex(MAIN_TEX)

    # Step 2: Run linter (with auto-fix)
    print(f"[3/3] Lint {'检查' if args.check_only else '修复'}: {MAIN_TEX.name}")
    code = run_linter(fix=not args.check_only)

    # Summary
    if code == 0:
        print("\n✓ main.tex 格式检查通过，可以上传 Overleaf 编译。")
    else:
        print(f"\n⚠ 仍有未解决的问题 (exit {code})，请查看上方报告。")

    return code


if __name__ == "__main__":
    sys.exit(main())
