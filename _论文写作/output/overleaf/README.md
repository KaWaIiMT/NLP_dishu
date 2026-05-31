# Overleaf 编译指南

## 上传步骤

1. 打开 [overleaf.com](https://www.overleaf.com)，注册/登录（免费）
2. 点击 **New Project** → **Upload Project**（上传整个文件夹）
3. 将 `overleaf/` 文件夹内的所有文件拖拽上传：

```
main.tex           ← 主文件
references.bib     ← 参考文献库（备案用）
figures/           ← 7张配图
  fig1_zipf_slope.pdf
  fig2_ttr_downsampled.pdf
  fig3_normalized_entropy.pdf
  fig4_pos_pie.pdf
  fig5_discourse_bar.pdf
  fig6_morph_bar.pdf
  fig7_radar.pdf
```

## 编译设置

在 Overleaf 编辑器左上角，点击 **Menu**：

| 设置项 | 选择 |
|--------|------|
| Compiler | **XeLaTeX** |
| TeX Live version | 2024（默认即可） |
| Main document | main.tex |

## 编译

点击 **Recompile** 按钮。首次编译约 30-60 秒。

## 已知问题

1. **「摘要」显示为英文 "Abstract"**：ctexart 默认使用英文标签。可在 preamble 添加 `\ctexset{abstractname=摘要}` 修复（已包含在模板中）
2. **表格超出页面宽度**：部分宽表格可能需要手动调整列宽。Overleaf 提供在线编辑，可直接修改 `.tex` 文件
3. **引用编号**：当前使用 GB/T 7714-2015 数字引用格式 `[1]`，正文引用已由 Pandoc 内联处理，无需额外编译步骤
