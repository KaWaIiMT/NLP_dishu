# 论文写作工作流

## 文件夹结构

```
_论文写作/
├── README.md              ← 本文件
├── paper.md               ← 最终组装的完整论文
├── references.bib          ← BibTeX 参考文献
├── metadata.yaml           ← 标题、作者、摘要等元数据
├── chapters/               ← 逐章草稿
│   ├── 01-引言.md
│   ├── 02-相关工作.md
│   ├── 03-数据与方法.md
│   ├── 04-结果.md
│   ├── 05-讨论.md
│   └── 06-结论.md
├── figures/                ← 图表
├── data/                   ← 数据表
└── output/                 ← 编译输出 (docx, tex, pdf)
```

## 写作顺序

| 步骤 | 章节 | 原因 |
|:----:|------|------|
| 1 | 03-数据与方法 | 数据已理清，最确定 |
| 2 | 04-结果 | 实验数据驱动 |
| 3 | 02-相关工作 | 文献调研报告已有 |
| 4 | 05-讨论 | 需要等结果写完 |
| 5 | 01-引言 | 全局把握后再写 |
| 6 | 06-结论 | 最后总结 |

## 格式转换

```bash
# Markdown → DOCX（作业提交格式）
pandoc paper.md -o output/paper.docx \
  --metadata-file=metadata.yaml \
  --bibliography=references.bib \
  --citeproc \
  --csl=chinese-gb7714-2005-numeric.csl \
  --reference-doc=reference.docx

# Markdown → LaTeX → PDF
pandoc paper.md -o output/paper.tex --metadata-file=metadata.yaml --bibliography=references.bib --citeproc
```

## 字数目标

| 章节 | 目标字数 |
|------|:------:|
| 01-引言 | ~1800 |
| 02-相关工作 | ~2500 |
| 03-数据与方法 | ~3000 |
| 04-结果 | ~4000 |
| 05-讨论 | ~2500 |
| 06-结论 | ~800 |
| **合计** | **~15,600** |
