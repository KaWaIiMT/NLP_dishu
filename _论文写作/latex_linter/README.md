# LaTeX Linter — 论文格式检查与修复工具

针对 **Pandoc (Markdown → LaTeX) + ctexart (XeLaTeX)** 工作流的静态格式检查器。

## 快速开始

```bash
# 在 build_overleaf.py 生成 main.tex 之后运行：

# 1. 仅检查，输出报告
python latex_linter/lint_tex.py output/overleaf/main.tex --figures-dir output/overleaf/figures

# 2. 检查并自动修复
python latex_linter/lint_tex.py output/overleaf/main.tex --figures-dir output/overleaf/figures --fix

# 3. 预览修复（不实际修改文件）
python latex_linter/lint_tex.py output/overleaf/main.tex --figures-dir output/overleaf/figures --fix --dry-run

# 4. 结合 Overleaf 编译日志
python latex_linter/lint_tex.py output/overleaf/main.tex --log output/overleaf/main.log

# 5. JSON 输出（用于 CI 集成）
python latex_linter/lint_tex.py output/overleaf/main.tex --json
```

## 检查项目

### Error（会导致编译失败）

| 代码 | 说明 |
|------|------|
| E001 | `\begin{env}` 与 `\end{env}` 不配对 |
| E002 | 缺少 `\begin{document}` / `\end{document}` |
| E003 | 数学模式 `$` 符号在文档末尾仍不配对 |
| E004 | `\usepackage` 出现在 `\documentclass` 之前 |

### Warning（可能导致格式问题）

| 代码 | 说明 |
|------|------|
| W001 | 重复的 `\label{}` |
| W002 | 引用了不存在的 `\label{}` |
| W003 | 空的命令（`\section{}` 等） |
| W004 | `\includegraphics{}` 引用的文件不存在 |
| W005 | 表格列数过多（含 CJK 时容易超宽） |
| W006 | Pandoc 残留物（`\tightlist`、`\passthrough`） |
| W007 | 重复的章节标题 |
| W008 | 连续空行过多（≥3 行） |
| W009 | 空的 `\caption{}` |
| W010 | 行尾有空白字符 |
| W011 | 半开数学模式：中文文字被渲染为数学体 |

### Info（风格建议）

| 代码 | 说明 |
|------|------|
| I001 | 文档末尾多余的 `\newpage` |
| I002 | 缺少推荐的宏包 |

## 典型工作流

```
paper.md                    ← 你编辑的 Markdown 论文
    │
    ▼
build_overleaf.py           ← 转换为 main.tex
    │
    ▼
lint_tex.py --fix           ← 检查 + 自动修复格式问题
    │
    ▼
上传到 Overleaf              ← 编译，下载 .log
    │
    ▼
lint_tex.py --log main.log  ← 解析编译警告
```

## 常见问题

### Q: 为什么 `--fix` 不能修复所有问题？

某些问题（如重复的章节标题、缺失的图片文件、表格列数过多）需要人工判断才能确定正确的修改方式。自动修复仅适用于确定性错误（如 `$N.N` 缺闭合 `$`、`\tightlist` 残留、环境名拼写错误等）。

### Q: 为什么 `\caption{}` 为空被标记为 Warning？

因为 `build_overleaf.py` 生成的表格使用 `\caption{}` + 下方的 `\textbf{}` 描述文字来模拟表格标题。这在功能上是正确的（表格有描述），但 `\caption{}` 标签本身是空的。如果你希望表格标题正确显示在 PDF 目录中（`\listoftables`），应该把描述文字移到 `\caption{...}` 中。

## 与 build_overleaf.py 集成

在 `build_overleaf.py` 末尾添加：

```python
# Auto-lint after build
import subprocess
lint_script = os.path.join(BASE, "latex_linter", "lint_tex.py")
subprocess.run(["python", lint_script, main_tex_path, "--figures-dir", FIGURES_DST])
```
