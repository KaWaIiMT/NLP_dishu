"""
生成 Overleaf 上传包 v2

核心思路：
1. Pandoc 将 paper.md → LaTeX body（不包含 preamble）
2. 手动写 ctex 中文排版 preamble
3. 清理 Pandoc 输出中的重复/冲突内容
"""
import os, shutil, subprocess, re

BASE = r"D:\_College\NLP\Research\_论文写作"
PAPER_MD = os.path.join(BASE, "paper.md")
OUTPUT = os.path.join(BASE, "output", "overleaf")
FIGURES_SRC = os.path.join(BASE, "figures")
FIGURES_DST = os.path.join(OUTPUT, "figures")
BIB = os.path.join(BASE, "references.bib")

os.makedirs(FIGURES_DST, exist_ok=True)

# ============================================================
# Step 1: Pandoc → LaTeX body (NO preamble, NO citeproc)
#    We handle citations natively in the tex, not via CSL
#    because Overleaf + biblatex will handle them
# ============================================================
print("Step 1: Pandoc converting paper.md → LaTeX...")

# First, let's use Pandoc without citeproc - keep [@key] references
# Then use a pandoc filter or manual post-processing

# Actually the simplest approach: let Pandoc output with --citeproc
# which resolves all citations to plain text. Then we don't need bibtex.
body_result = subprocess.run(
    ["pandoc", PAPER_MD, "-t", "latex", "--citeproc", "--wrap=preserve",
     f"--bibliography={BIB}",
     "--csl=https://www.zotero.org/styles/china-national-standard-gb-t-7714-2015-numeric"],
    capture_output=True, text=True, encoding='utf-8', timeout=120
)
body = body_result.stdout

print(f"  Raw body: {len(body)} chars")

# ============================================================
# Step 2: Clean up the body
# ============================================================

# --- Remove manual section numbers from titles ---
# Pandoc generates numbered sections, so we don't need manual numbers in titles
body = re.sub(r'\\section\{(\d+) ', r'\\section{', body)
body = re.sub(r'\\subsection\{(\d+\.\d+) ', r'\\subsection{', body)
body = re.sub(r'\\subsubsection\{(\d+\.\d+\.\d+) ', r'\\subsubsection{', body)

# --- Fix table formatting for Overleaf ---
# Change LTcaptype from none to table to fix table alignment issues
body = re.sub(r'\\def\\LTcaptype\{none\}', r'\\def\\LTcaptype\{table\}', body)

# --- Fix mathematical symbols in tables ---
# Wrap underscores and special symbols in $ for proper LaTeX rendering
# NOTE: do NOT wrap already-escaped underscores (\_) — those are intentional
body = re.sub(r'([^\$\\])(_[a-zA-Z0-9]+)([^\$])', r'\1$\2$\3', body)
body = re.sub(r'([^\$])(−?\d+\.\d+)([^\$])', r'\1$\2$\3', body)

# --- Remove the duplicate abstract section ---
# Pandoc puts the YAML abstract as a \section{摘要}
body = re.sub(
    r'\\section\{摘要\}.*?\\newpage\s*',
    '',
    body,
    flags=re.DOTALL
)

# --- Remove any \tightlist (incompatible with ctex) ---
body = body.replace('\\tightlist\n', '\n')
body = body.replace('\\tightlist', '')

# --- Fix \\passthrough{\\newpage} ---
body = body.replace('\\passthrough{\\newpage}', '\\newpage')

# --- Fix unicode minus U+2212 → plain hyphen (XeLaTeX handles this) ---
body = body.replace('−', '-')

# --- Fix mangled underscores in texttt blocks ---
body = body.replace('\\$_', '\\_')
body = body.replace('$\\_', '\\_')
body = body.replace('\\_ ', '\\_')
# --- Remove stray $ before } in texttt blocks ---
body = body.replace('$}', '}')

# ============================================================
# TABLE FIX: Extract tables from Markdown, build clean LaTeX
# ============================================================
def extract_md_tables(md_content):
    """
    Parse Markdown pipe tables into structured data.
    Returns list of tables, each = {'headers': [...], 'rows': [[...], ...]}
    """
    tables = []
    lines = md_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Detect table: line contains | and next line is a separator |---|
        if line.startswith('|') and '|' in line:
            if i + 1 < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i+1].strip()):
                # This is a table header + separator
                headers = [c.strip() for c in line.split('|')[1:-1]]
                i += 2  # Skip separator line
                rows = []
                while i < len(lines) and lines[i].strip().startswith('|') and '|' in lines[i]:
                    row = [c.strip() for c in lines[i].strip().split('|')[1:-1]]
                    rows.append(row)
                    i += 1
                tables.append({'headers': headers, 'rows': rows})
                continue
        i += 1
    return tables

def build_latex_table(table_data):
    """Build clean LaTeX tabular + table float from parsed table data"""
    headers = table_data['headers']
    rows = table_data['rows']
    ncols = len(headers)

    # Column spec: all left-aligned for simplicity
    colspec = 'l' * ncols

    lines = []
    lines.append(r'\begin{table}[htbp]')
    lines.append(r'\centering')
    lines.append(r'\small')
    lines.append(r'\begin{tabular}{@{}' + colspec + r'@{}}')
    lines.append(r'\toprule')

    # Header row
    clean_headers = [h.replace('**', '') for h in headers]
    lines.append(' & '.join(clean_headers) + r' \\')
    lines.append(r'\midrule')

    # Data rows
    for row in rows:
        escaped = []
        for cell in row:
            # Strip Markdown bold markers **
            cell = cell.replace('**', '')
            # Escape LaTeX specials (only what's needed in tabular)
            cell = cell.replace('_', '\\_')
            cell = cell.replace('&', '\\&')
            cell = cell.replace('%', '\\%')
            cell = cell.replace('#', '\\#')
            cell = cell.replace('$', '\\$')
            cell = cell.replace('{', '\\{')
            cell = cell.replace('}', '\\}')
            cell = cell.replace('~', '\\textasciitilde ')
            escaped.append(cell)
        lines.append(' & '.join(escaped) + r' \\')

    lines.append(r'\bottomrule')
    lines.append(r'\end{tabular}')
    lines.append(r'\end{table}')
    lines.append('')
    return '\n'.join(lines)

def fix_pandoc_tables(body, md_content):
    """
    Replace all Pandoc-generated longtable blocks with clean LaTeX tables
    built from the original Markdown table data.
    """
    md_tables = extract_md_tables(md_content)
    print(f"  Found {len(md_tables)} Markdown tables")

    # Find all longtable blocks in LaTeX body
    # Pandoc output: {\def\LTcaptype\{table\} % ...\begin{longtable}...\end{longtable}\n}
    lt_pattern = re.compile(
        r'\{\\def\\LTcaptype\\{[^}]*\\}\s*%[^\n]*\n'
        r'\\begin\{longtable\}.*?\\end\{longtable\}\n\}',
        re.DOTALL
    )

    matches = list(lt_pattern.finditer(body))
    print(f"  Found {len(matches)} longtable blocks in LaTeX")

    # Replace each longtable with corresponding Markdown-built table
    # Process in reverse to preserve string positions
    result = body
    for idx in range(min(len(matches), len(md_tables))):
        match_pos = matches[idx]
        clean_table = build_latex_table(md_tables[idx])
        # Find and replace this specific occurrence
        result = result.replace(match_pos.group(0), clean_table, 1)
        print(f"  Table {idx+1}: {len(md_tables[idx]['rows'])} data rows, {len(md_tables[idx]['headers'])} cols → replaced")

    # Clean up any remaining longtable/orphaned defs (same escaped brace pattern)
    result = re.sub(r'\{\\def\\LTcaptype\\{[^}]*\\}\s*%[^\n]*\n', '', result)
    result = re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}\n\}', '', result, flags=re.DOTALL)

    return result

# Read paper.md for table data (needed below)
with open(PAPER_MD, 'r', encoding='utf-8') as f:
    _md_content = f.read()

body = fix_pandoc_tables(body, _md_content)
# ============================================================

# --- Fix Chinese quotes from Pandoc ---
body = body.replace("''", "''")  # Pandoc's smart quotes - leave as is for LaTeX
# Actually, Pandoc uses `` and '' for LaTeX quotes which is correct

# --- Remove the standalone abstract/keywords block (already in preamble) ---
body = re.sub(
    r'\n\\textbf\{关键词\}.*?\n\n',
    '\n',
    body
)

# --- Fix section numbering ---
# Pandoc outputs \section{1 引言} etc. Let's keep as is since we want numbered chapters

# --- Fix escaped % in tables ---
body = body.replace(r'\%', r'\%')

# --- Fix relative image paths: ../../figures/ → figures/ ---
body = body.replace('../../figures/', 'figures/')

# --- Fix mangled image paths: remove all $ signs from \includegraphics ---
# Pandoc sometimes wraps underscores in filenames as $_{word}$ which breaks the path
body = re.sub(
    r'(\\includegraphics\[.*?\]\{)([^}]+)(\})',
    lambda m: m.group(1) + m.group(2).replace('$', '') + m.group(3),
    body
)

print(f"  Cleaned body: {len(body)} chars")

# ============================================================
# Step 3: Extract the abstract text from paper.md YAML
# ============================================================
with open(PAPER_MD, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Extract abstract from YAML front matter
abstract_match = re.search(
    r'abstract:\s*\|\s*\n((?:\s{2}.+\n)+?)keywords:',
    md_content
)
abstract_text = ""
if abstract_match:
    abs_raw = abstract_match.group(1)
    # Remove leading 2-space indent and join lines
    abs_lines = [line[2:] if line.startswith('  ') else line for line in abs_raw.strip().split('\n')]
    abstract_text = ' '.join(abs_lines)
    abstract_text = re.sub(r'\s+', ' ', abstract_text).strip()

# Fix unicode minus in abstract too
abstract_text = abstract_text.replace('−', '$-$')

print(f"  Abstract: {len(abstract_text)} chars")

# ============================================================
# Step 4: Assemble main.tex
# ============================================================
print("Step 4: Assembling main.tex...")

# Helper: escape any % in abstract for LaTeX
abstract_escaped = abstract_text.replace('%', r'\%')

preamble = r"""% !TEX program = xelatex
\documentclass[12pt,a4paper,UTF8,fontset=founder]{ctexart}

% === 中文支持 ===
% fontset=founder 使用方正书宋，覆盖最全的汉字字符集（包括所有罕见字）


% === 页面 ===
\usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
\usepackage{setspace}
\onehalfspacing

% === 表格 ===
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{threeparttable}
\usepackage{tabularx}

% === 图表 ===
\usepackage{graphicx}
\usepackage{caption}
\graphicspath{{figures/}}
\usepackage{float}

% === 数学 ===
\usepackage{amsmath,amssymb}

% === 超链接 ===
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}  % 更好的 URL 换行

% === 页眉页脚 ===
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small 《地书》图形语言的语言性量化评估}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% === 参考文献格式 ===
% Pandoc --citeproc 内联引用格式支持
\newlength{\cslhangindent}
\setlength{\cslhangindent}{1.5em}
\newlength{\csllabelwidth}
\setlength{\csllabelwidth}{3em}
\newenvironment{CSLReferences}[2]%
  {\begin{list}{}{%
    \setlength{\leftmargin}{0pt}%
    \setlength{\itemindent}{0pt}%
    \setlength{\itemsep}{0pt}%
    \setlength{\parsep}{0pt}%
    \setlength{\listparindent}{\parindent}%
    \setlength{\topsep}{0pt}}}%
  {\end{list}}
\newcommand{\CSLLeftMargin}[1]{%
  \leavevmode\par\noindent
  \makebox[\csllabelwidth][l]{#1}%
  \hspace{0pt}}
\newcommand{\CSLRightInline}[1]{%
  \parbox[t]{\dimexpr\linewidth-\csllabelwidth\relax}{#1}}

% === 标题信息 ===
\title{{\Large \textbf{《地书》图形语言的语言性量化评估}}\\[4pt]
       {\large ——基于多维标注体系的统计分析}}
\author{
  池长俊\thanks{人工智能与计算机学院，江南大学} \quad
  王顺祺 \quad
  刘棪 \quad
  高子阳}
\date{}

\begin{document}

\maketitle

% === 摘要 ===
\begin{center}
\begin{minipage}{0.92\textwidth}
\small
\setlength{\baselineskip}{1.6\baselineskip}
\textbf{摘\quad 要：}"""

postamble_abstract = r"""\end{minipage}
\end{center}

\vspace{0.3cm}

\begin{center}
\begin{minipage}{0.92\textwidth}
\small
\textbf{关键词：}地书；图形语言；语言性评估；标注者间一致性；齐夫定律；计算语言学
\end{minipage}
\end{center}

\vspace{0.5cm}

\begin{center}
\small
\textbf{English Title:} A Quantitative Language-ness Assessment of EarthScript (Di Shu):\\
Statistical Analysis Based on a Multi-Dimensional Annotation Framework
\end{center}

\newpage

% === 正文 ===
"""

end_document = r"""
\end{document}
"""

# Assemble everything
main_tex = (
    preamble + '\n' +
    abstract_escaped + '\n' +
    postamble_abstract + '\n' +
    body + '\n' +
    end_document
)

# --- Post-assembly fixes ---
# Remove multiple consecutive blank lines
main_tex = re.sub(r'\n{3,}', '\n\n', main_tex)

# Fix any double-dollar-sign issues from minus replacement
main_tex = main_tex.replace('$$-$', '$-$')
main_tex = main_tex.replace('$-$$', '$-$')

# Write
main_tex_path = os.path.join(OUTPUT, "main.tex")
with open(main_tex_path, 'w', encoding='utf-8') as f:
    f.write(main_tex)
print(f"  main.tex: {len(main_tex)} chars")

# ============================================================
# Step 5: Copy assets
# ============================================================
print("Step 5: Copying assets...")

# Figures (PDF)
for f in os.listdir(FIGURES_SRC):
    if f.endswith('.pdf'):
        shutil.copy2(os.path.join(FIGURES_SRC, f), os.path.join(FIGURES_DST, f))

# References
shutil.copy2(BIB, os.path.join(OUTPUT, "references.bib"))

# ============================================================
# Step 6: Run LaTeX linter
# ============================================================
print("Step 6: Running LaTeX linter...")
lint_script = os.path.join(BASE, "latex_linter", "lint_tex.py")
lint_result = subprocess.run(
    ["python", lint_script, main_tex_path, "--figures-dir", FIGURES_DST],
    capture_output=True, text=True, encoding='utf-8', timeout=30
)
print(lint_result.stdout)
if lint_result.stderr:
    print(lint_result.stderr)

# ============================================================
# Summary
# ============================================================
print(f"\n{'='*60}")
print(f"Overleaf package → {OUTPUT}")
print(f"Upload contents to overleaf.com:")
for item in sorted(os.listdir(OUTPUT)):
    full = os.path.join(OUTPUT, item)
    if os.path.isfile(full):
        print(f"  [{item}] ({os.path.getsize(full)/1024:.1f} KB)")
    else:
        nfiles = len(os.listdir(full))
        print(f"  [{item}/] ({nfiles} files)")
