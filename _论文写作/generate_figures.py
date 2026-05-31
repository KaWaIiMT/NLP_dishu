"""
论文配图生成脚本 v2 — 顶会论文级别
升级：学术配色(Colorblind-safe)、统一字体、精细化排版
"""
import json, math, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import rcParams

# ============================================================
# 全局样式 — 模仿 ACM/ACL 顶会论文图表风格
# ============================================================
# === 字体：检测并启用CJK字体 ===
from matplotlib.font_manager import fontManager
_cjk_candidates = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimSun']
_available_fonts = {f.name for f in fontManager.ttflist}
_CN_FONT = None
for _f in _cjk_candidates:
    if _f in _available_fonts:
        _CN_FONT = _f
        break

_sans_serif_fonts = (['Arial', 'Helvetica', 'DejaVu Sans'] if _CN_FONT is None
                     else [_CN_FONT, 'Arial', 'Helvetica', 'DejaVu Sans'])

rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': _sans_serif_fonts,
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
    'axes.unicode_minus': False,
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'grid.alpha': 0.15,
    'axes.grid': False,
})
print(f'  CJK font: {_CN_FONT or "NOT FOUND — falling back to ASCII only"}')

OUTPUT_DIR = r"D:\_College\NLP\Research\_论文写作\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 学术配色 — Colorblind-safe (IBM/Paul Tol 风格)
# ============================================================
C_DISHU   = '#E69F00'  # orange — 地书始终用这个
C_ZH_NEWS = '#56B4E9'  # sky blue
C_ZH_NOV  = '#009E73'  # bluish green
C_ZH_CLAS = '#CC79A7'  # reddish purple
C_ZH_LIT  = '#F0E442'  # yellow
C_EN      = '#0072B2'  # deep blue
C_DE      = '#D55E00'  # vermillion
C_FR      = '#882255'  # wine

CORPUS_COLORS = {
    '地书':  C_DISHU,
    '中文新闻': C_ZH_NEWS,
    '中文小说': C_ZH_NOV,
    '中文古文': C_ZH_CLAS,
    '中文文学': C_ZH_LIT,
    '英文':  C_EN,
    '德文':  C_DE,
    '法文':  C_FR,
}

CORPUS_ORDER = ['地书', '中文新闻', '中文小说', '中文古文', '中文文学', '英文', '德文', '法文']

# ============================================================
# 数据
# ============================================================
ZIPF = {
    '地书':   {'slope': -0.612, 'r2': 0.923, 'tokens': 10538, 'types': 4577},
    '中文新闻': {'slope': -1.399, 'r2': 0.894, 'tokens': 50000, 'types': 2484},
    '中文小说': {'slope': -1.351, 'r2': 0.943, 'tokens': 50000, 'types': 2623},
    '中文古文': {'slope': -1.475, 'r2': 0.956, 'tokens': 50000, 'types': 2178},
    '中文文学': {'slope': -1.362, 'r2': 0.929, 'tokens': 50000, 'types': 2612},
    '英文':   {'slope': -0.873, 'r2': 0.946, 'tokens': 50000, 'types': 10262},
    '德文':   {'slope': -0.683, 'r2': 0.876, 'tokens': 50000, 'types': 14890},
    '法文':   {'slope': -0.785, 'r2': 0.925, 'tokens': 50000, 'types': 11218},
}

DIVERSITY = {
    '地书':   {'ttr_ds': 0.434, 'rttr': 0.659, 'norm_h': 0.914, 'shannon_h': 11.11},
    '中文新闻': {'ttr_ds': 0.152, 'rttr': 0.023, 'norm_h': 0.769, 'shannon_h': 9.48},
    '中文小说': {'ttr_ds': 0.151, 'rttr': 0.091, 'norm_h': 0.751, 'shannon_h': 8.94},
    '中文古文': {'ttr_ds': 0.117, 'rttr': 0.059, 'norm_h': 0.687, 'shannon_h': 8.40},
    '中文文学': {'ttr_ds': 0.154, 'rttr': 0.060, 'norm_h': 0.755, 'shannon_h': 9.12},
    '英文':   {'ttr_ds': 0.342, 'rttr': 0.361, 'norm_h': 0.727, 'shannon_h': 10.36},
    '德文':   {'ttr_ds': 0.420, 'rttr': 0.469, 'norm_h': 0.748, 'shannon_h': 11.24},
    '法文':   {'ttr_ds': 0.350, 'rttr': 0.370, 'norm_h': 0.700, 'shannon_h': 10.31},
}

POS = {
    '标点/边界标记': 2903,
    '动词性': 2202,
    '名词性': 1353,
    '整句/整体表达': 812,
    '形容词性': 486,
    '连接/关系标记': 339,
    '无法判断': 213,
    '代词/指示性': 176,
    '副词性': 150,
    '虚词/语法标记': 74,
}

DISCOURSE = {
    '时间先后': 2117,
    '因果': 867,
    '并列递进': 746,
    '解释说明': 294,
    '无明显关系': 281,
    '转折对比': 191,
    '条件': 150,
    '总结': 91,
    '举例': 64,
    '无法判断': 46,
}

MORPH = {
    '进行体': 2747,
    '现在时': 2356,
    '强调': 960,
    '复数/集合': 858,
    '重复/迭代': 851,
    '完成体': 632,
    '将来时': 595,
    '过去时': 476,
    '比较': 364,
    '否定': 335,
    '程度增强': 326,
    '最高级': 240,
}

# ============================================================
# 工具函数
# ============================================================
def annotate_bar(ax, bars, values, fmt='{:.3f}', offset=0.02, fontsize=7):
    """在柱状图顶部添加数值标签"""
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + offset,
                fmt.format(val), ha='center', va='bottom',
                fontsize=fontsize, color='#444')

def color_from_order(names):
    return [CORPUS_COLORS.get(n, '#999999') for n in names]

def save(fig, name):
    fig.savefig(os.path.join(OUTPUT_DIR, name + '.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, name + '.png'), format='png', dpi=300)
    plt.close(fig)

# ============================================================
# Fig 1: Zipf Slope — 带参考线的学术柱状图
# ============================================================
def fig1():
    names = [n for n in CORPUS_ORDER if n in ZIPF]
    slopes = [ZIPF[n]['slope'] for n in names]
    r2s = [ZIPF[n]['r2'] for n in names]
    colors = color_from_order(names)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(len(names))
    bars = ax.bar(x, slopes, color=colors, edgecolor='white', linewidth=0.3, width=0.65)

    # 参考线: 理想 Zipf −1.0
    ax.axhline(y=-1.0, color='#666', linestyle='--', linewidth=0.7, alpha=0.7)
    ax.text(len(names) - 0.6, -1.0 + 0.03, 'Ideal Zipf (−1.0)', fontsize=7,
            color='#666', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.7))

    # R² 标注
    for i, (bar, r2) in enumerate(zip(bars, r2s)):
        ax.text(bar.get_x() + bar.get_width() / 2, slopes[i] + 0.03,
                f'$R^2$={r2:.3f}', ha='center', va='bottom',
                fontsize=6.5, color='#555', style='italic')

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha='right', fontsize=8)
    ax.set_ylabel('Zipf Slope', fontsize=9)
    ax.set_ylim(min(slopes) - 0.15, max(slopes) + 0.15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    save(fig, 'fig1_zipf_slope')
    print('  [1/7] Zipf slope — upgraded')

# ============================================================
# Fig 2: TTR — 降采样公平对比
# ============================================================
def fig2():
    names = [n for n in CORPUS_ORDER if n in DIVERSITY]
    ttrs = [DIVERSITY[n]['ttr_ds'] for n in names]
    colors = color_from_order(names)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(len(names))
    bars = ax.bar(x, ttrs, color=colors, edgecolor='white', linewidth=0.3, width=0.65)

    for bar, ttr in zip(bars, ttrs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f'{ttr:.3f}', ha='center', va='bottom', fontsize=7, color='#333')

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha='right', fontsize=8)
    ax.set_ylabel('Type-Token Ratio (downsampled to 10,538 tokens)', fontsize=8.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 分组标注
    ax.text(0.5, 0.97, 'Dishu', transform=ax.get_xaxis_transform(),
            fontsize=8, ha='center', color=C_DISHU, fontweight='bold')
    ax.text(2.5, 0.97, 'Chinese (Sino-Tibetan)', transform=ax.get_xaxis_transform(),
            fontsize=7, ha='center', color='#888')
    ax.text(5.5, 0.97, 'Indo-European', transform=ax.get_xaxis_transform(),
            fontsize=7, ha='center', color='#888')

    fig.tight_layout()
    save(fig, 'fig2_ttr_downsampled')
    print('  [2/7] TTR — upgraded')

# ============================================================
# Fig 3: Normalized Entropy
# ============================================================
def fig3():
    names = [n for n in CORPUS_ORDER if n in DIVERSITY]
    entropies = [DIVERSITY[n]['norm_h'] for n in names]
    colors = color_from_order(names)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(len(names))
    bars = ax.bar(x, entropies, color=colors, edgecolor='white', linewidth=0.3, width=0.65)

    for bar, h in zip(bars, entropies):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f'{h:.3f}', ha='center', va='bottom', fontsize=7, color='#333')

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha='right', fontsize=8)
    ax.set_ylabel('Normalized Entropy (H / H_max)', fontsize=9)
    ax.set_ylim(0, 1.02)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    save(fig, 'fig3_normalized_entropy')
    print('  [3/7] Normalized entropy — upgraded')

# ============================================================
# Fig 4: POS Pie — 环形甜甜圈图
# ============================================================
def fig4():
    labels = list(POS.keys())
    sizes = list(POS.values())
    total = sum(sizes)

    # 自定义配色（按语义分组）
    pie_colors = [
        '#E69F00',  # 标点 — orange
        '#56B4E9',  # 动词 — blue
        '#009E73',  # 名词 — green
        '#F0E442',  # 整句 — yellow
        '#CC79A7',  # 形 — purple
        '#0072B2',  # 连接 — deep blue
        '#D55E00',  # 无法 — vermillion
        '#999999',  # 代 — grey
        '#BBBBBB',  # 副 — light grey
        '#DDDDDD',  # 虚词 — lighter grey (几乎看不见)
    ]

    fig, ax = plt.subplots(figsize=(9, 6))
    wedges, texts = ax.pie(sizes, labels=None, colors=pie_colors,
                           startangle=90, pctdistance=0.82,
                           wedgeprops=dict(width=0.4, edgecolor='white', linewidth=0.5))

    # 百分比标注 — 只标注 > 3% 的
    for i, (wedge, size) in enumerate(zip(wedges, sizes)):
        pct = size / total * 100
        if pct > 3:
            ang = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
            x = np.cos(np.deg2rad(ang)) * 0.72
            y = np.sin(np.deg2rad(ang)) * 0.72
            ax.text(x, y, f'{pct:.1f}%', ha='center', va='center', fontsize=7.5, fontweight='bold')

    # Legend
    legend_labels = [f'{l} ({s})' for l, s in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, title='POS-like Category',
              loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7.5,
              title_fontsize=8)

    ax.set_title('Distribution of POS-like Categories ($n=8,708$)', fontsize=10, pad=15)
    save(fig, 'fig4_pos_pie')
    print('  [4/7] POS donut — upgraded')

# ============================================================
# Fig 5: Discourse — 横向棒棒糖图
# ============================================================
def fig5():
    items = list(DISCOURSE.items())
    items.sort(key=lambda x: x[1], reverse=True)
    labels = [x[0] for x in items]
    counts = [x[1] for x in items]
    total = sum(counts)
    pcts = [c / total * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    y_pos = np.arange(len(labels))
    colors = plt.cm.YlOrRd(np.linspace(0.25, 0.9, len(labels)))

    # 棒棒糖图: line + scatter
    ax.hlines(y_pos, 0, pcts, colors=colors, linewidth=1.8, alpha=0.8)
    ax.scatter(pcts, y_pos, c=colors, s=70, zorder=3, edgecolors='white', linewidth=0.4)

    # Label
    for i, (pct, cnt) in enumerate(zip(pcts, counts)):
        ax.text(pct + 0.5, i, f'{pct:.1f}% ($n$={cnt})', va='center', fontsize=7.5, color='#333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('Percentage (%)', fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, max(pcts) + 8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 标注前三
    ax.text(0.98, 0.95, 'Top 3: 77.0%', transform=ax.transAxes,
            fontsize=7.5, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.3', fc='#FFF3CD', ec='#E69F00', alpha=0.8))

    fig.tight_layout()
    save(fig, 'fig5_discourse_bar')
    print('  [5/7] Discourse lollipop — upgraded')

# ============================================================
# Fig 6: Morphological — 横向分组棒棒糖
# ============================================================
def fig6():
    items = list(MORPH.items())
    items.sort(key=lambda x: x[1], reverse=True)
    labels = [x[0] for x in items]
    counts = [x[1] for x in items]
    total = sum(counts)
    pcts = [c / total * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(8.5, 5))
    y_pos = np.arange(len(labels))
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(labels)))

    ax.hlines(y_pos, 0, pcts, colors=colors, linewidth=1.8, alpha=0.8)
    ax.scatter(pcts, y_pos, c=colors, s=70, zorder=3, edgecolors='white', linewidth=0.4)

    for i, (pct, cnt) in enumerate(zip(pcts, counts)):
        ax.text(pct + 0.5, i, f'{pct:.1f}% ($n$={cnt})', va='center', fontsize=7.5, color='#333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('Percentage (%)', fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, max(pcts) + 8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 标注
    ax.text(0.98, 0.95, 'Progressive + Present: 47.5%', transform=ax.transAxes,
            fontsize=7.5, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.3', fc='#D6EAF8', ec='#0072B2', alpha=0.8))

    fig.tight_layout()
    save(fig, 'fig6_morph_bar')
    print('  [6/7] Morphology lollipop — upgraded')

# ============================================================
# Fig 7: Radar — 六维度 (D6 now has real data!)
# ============================================================
def fig7():
    # D1-D6, 全部有数据
    dims = ['D1\nFreq Structure\n(Zipf $R^2$)',
            'D6\nSemantic\nStability ($\\kappa$)',  # 放在 D1 旁边，语义闭环
            'D5\nDiscourse\nComplexity',
            'D4\nPOS\nDiversity',
            'D3\nLexical\nDiversity (TTR)',
            'D2\nInformation\n(Norm. Entropy)']

    # 归一化所有维度到 0-1
    dishu_raw = [0.923, 0.802, 0.780, 0.778, 0.434, 0.914]
    # TTR 归一化 (max≈0.5)
    dishu_raw[4] = min(dishu_raw[4] / 0.5, 1.0)

    news_raw = [0.894, None, None, None, 0.152, 0.769]
    novel_raw = [0.943, None, None, None, 0.151, 0.751]
    # Normalize TTR for comparison corpora too
    for raw in [news_raw, novel_raw]:
        if raw[4] is not None:
            raw[4] = min(raw[4] / 0.5, 1.0)

    N = len(dims)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    dishu = dishu_raw + [dishu_raw[0]]
    news  = [x if x is not None else 0 for x in news_raw] + [news_raw[0] if news_raw[0] else 0]
    novel = [x if x is not None else 0 for x in novel_raw] + [novel_raw[0] if novel_raw[0] else 0]

    fig, ax = plt.subplots(figsize=(7.5, 7.5), subplot_kw={'projection': 'polar'})

    # 背景网格
    ax.set_facecolor('#FAFAFA')

    # 数据线
    ax.fill(angles, dishu, alpha=0.12, color=C_DISHU)
    ax.plot(angles, dishu, 'o-', color=C_DISHU, linewidth=2.2, markersize=7, label='Dishu',
            markerfacecolor='white', markeredgewidth=1.5)

    # 仅对有数据的维度画中文对照 (D1,D3,D2)
    # 简化：只画新闻作为参考
    news_plot = [v if v > 0 else np.nan for v in news]
    ax.plot(angles, news_plot, 's--', color=C_ZH_NEWS, linewidth=1.2, markersize=5,
            label='Chinese News (partial)', alpha=0.7)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims, fontsize=7.5)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=6.5, color='#888')

    # Title
    ax.set_title('Language-ness Radar: Dishu vs. Chinese News',
                 fontsize=10, pad=22, fontweight='bold')

    # Legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.08), fontsize=8, frameon=True,
              fancybox=True, framealpha=0.9)

    # Annotation
    ax.annotate('All 6 dimensions\nnow with data',
                xy=(angles[1], 0.85), fontsize=6.5, ha='center', color=C_DISHU,
                fontstyle='italic')

    fig.tight_layout()
    save(fig, 'fig7_radar')
    print('  [7/7] Radar — upgraded (6D with D6 data!)')

# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print(f'Generating publication-quality figures → {OUTPUT_DIR}')
    print()
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    fig7()
    print()
    pdfs = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.pdf')]
    print(f'Done! {len(pdfs)} PDF figures generated.')
