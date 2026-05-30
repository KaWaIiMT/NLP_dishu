"""
论文配图生成脚本
生成 _论文写作/figures/ 下的所有数据图
"""
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os, sys

# === 中文字体配置 ===
rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False
rcParams['figure.dpi'] = 150
rcParams['savefig.dpi'] = 300
rcParams['savefig.bbox'] = 'tight'

OUTPUT_DIR = r"D:\_College\NLP\Research\_论文写作\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === 配色方案（colorblind-safe） ===
C_DISHU = '#E69F00'      # orange
C_ZH = '#56B4E9'          # sky blue
C_ZHT = '#009E73'         # green
C_EN = '#CC79A7'          # purple
C_OTHER = '#999999'       # grey

ZH_CORPORA = ['Chinese_News', 'Chinese_Novel', 'Chinese_Classical', 'Chinese_Literature']
ZH_LABELS = ['新闻', '小说', '古文', '文学']
ZH_COLORS = ['#56B4E9', '#009E73', '#D55E00', '#F0E442']

# ============================================================
# 数据
# ============================================================

zipf_data = {
    '地书':      {'slope': -0.612, 'r2': 0.923, 'tokens': 10538, 'types': 4577},
    '中文新闻':   {'slope': -1.399, 'r2': 0.894, 'tokens': 50000, 'types': 2484},
    '中文小说':   {'slope': -1.351, 'r2': 0.943, 'tokens': 50000, 'types': 2623},
    '中文古文':   {'slope': -1.475, 'r2': 0.956, 'tokens': 50000, 'types': 2178},
    '中文文学':   {'slope': -1.362, 'r2': 0.929, 'tokens': 50000, 'types': 2612},
    '英文':      {'slope': -0.873, 'r2': 0.946, 'tokens': 50000, 'types': 10262},
    '德文':      {'slope': -0.683, 'r2': 0.876, 'tokens': 50000, 'types': 14890},
    '法文':      {'slope': -0.785, 'r2': 0.925, 'tokens': 50000, 'types': 11218},
}

ttr_entropy_data = {
    '地书':      {'ttr_ds': 0.434, 'rttr': 0.659, 'norm_h': 0.914, 'shannon_h': 11.11},
    '中文新闻':   {'ttr_ds': 0.152, 'rttr': 0.023, 'norm_h': 0.769, 'shannon_h': 9.48},
    '中文小说':   {'ttr_ds': 0.151, 'rttr': 0.091, 'norm_h': 0.751, 'shannon_h': 8.94},
    '中文古文':   {'ttr_ds': 0.117, 'rttr': 0.059, 'norm_h': 0.687, 'shannon_h': 8.40},
    '中文文学':   {'ttr_ds': 0.154, 'rttr': 0.060, 'norm_h': 0.755, 'shannon_h': 9.12},
    '英文':      {'ttr_ds': 0.342, 'rttr': 0.361, 'norm_h': 0.727, 'shannon_h': 10.36},
    '德文':      {'ttr_ds': 0.420, 'rttr': 0.469, 'norm_h': 0.748, 'shannon_h': 11.24},
    '法文':      {'ttr_ds': 0.350, 'rttr': 0.370, 'norm_h': 0.700, 'shannon_h': 10.31},
}

pos_data = {
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

discourse_data = {
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

morph_data = {
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

radar_dims = ['频率结构\n(Zipf R²)', '信息密度\n(归一化熵)', '词汇多样性\n(降采样TTR)',
              '语法多样性\n(POS均匀度)', '篇章复杂度\n(关系均匀度)', '语义稳定性\n(Fleiss κ)']
radar_dishu = [0.923, 0.914, 0.434, 0.778, 0.780, None]  # D6 pending
radar_news  = [0.894, 0.769, 0.152, None, None, None]
radar_novel = [0.943, 0.751, 0.151, None, None, None]

# ============================================================
# FIG 1: Zipf 斜率对比柱状图
# ============================================================
def fig1_zipf_slope():
    names = list(zipf_data.keys())
    slopes = [zipf_data[n]['slope'] for n in names]
    r2s = [zipf_data[n]['r2'] for n in names]
    colors = [C_DISHU if n == '地书' else C_ZH if '中文' in n else C_EN if n in ('英文','德文','法文') else C_OTHER for n in names]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, slopes, color=colors, edgecolor='white', linewidth=0.5)
    ax.axhline(y=-1.0, color='gray', linestyle='--', alpha=0.5, label='理想 Zipf 斜率 (−1.0)')
    ax.set_ylabel('Zipf 斜率')
    ax.set_title('图1  各语料 Zipf 斜率对比')
    for bar, slope, r2 in zip(bars, slopes, r2s):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                f'R²={r2:.3f}', ha='center', va='bottom', fontsize=7, color='gray')
    ax.legend(fontsize=8)
    plt.xticks(rotation=30, ha='right', fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_zipf_slope.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig1_zipf_slope.png'), format='png')
    plt.close()

# ============================================================
# FIG 2: 降采样 TTR 对比柱状图
# ============================================================
def fig2_ttr_downsampled():
    names = list(ttr_entropy_data.keys())
    ttrs = [ttr_entropy_data[n]['ttr_ds'] for n in names]
    colors = [C_DISHU if n == '地书' else C_ZH if '中文' in n else C_EN if n in ('英文','德文','法文') else C_OTHER for n in names]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, ttrs, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_ylabel('TTR（降采样至 10,538 tokens）')
    ax.set_title('图2  各语料降采样 TTR 对比（100次随机采样均值）')
    for bar, ttr in zip(bars, ttrs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{ttr:.3f}', ha='center', va='bottom', fontsize=8)
    plt.xticks(rotation=30, ha='right', fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_ttr_downsampled.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig2_ttr_downsampled.png'), format='png')
    plt.close()

# ============================================================
# FIG 3: 归一化熵对比柱状图
# ============================================================
def fig3_normalized_entropy():
    names = list(ttr_entropy_data.keys())
    entropies = [ttr_entropy_data[n]['norm_h'] for n in names]
    colors = [C_DISHU if n == '地书' else C_ZH if '中文' in n else C_EN if n in ('英文','德文','法文') else C_OTHER for n in names]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, entropies, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_ylabel('归一化熵 (H / H_max)')
    ax.set_title('图3  各语料归一化熵对比')
    ax.set_ylim(0, 1.05)
    for bar, h in zip(bars, entropies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{h:.3f}', ha='center', va='bottom', fontsize=8)
    plt.xticks(rotation=30, ha='right', fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_normalized_entropy.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig3_normalized_entropy.png'), format='png')
    plt.close()

# ============================================================
# FIG 4: POS-like Category 分布饼图
# ============================================================
def fig4_pos_pie():
    labels = list(pos_data.keys())
    sizes = list(pos_data.values())
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(labels)))

    fig, ax = plt.subplots(figsize=(8, 7))
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%',
                                       colors=colors_pie, startangle=90,
                                       pctdistance=0.75)
    for t in autotexts:
        t.set_fontsize(8)
    ax.legend(wedges, [f'{l} ({s})' for l, s in zip(labels, sizes)],
              title='POS-like Category', loc='center left',
              bbox_to_anchor=(1, 0.5), fontsize=7)
    ax.set_title('图4  地书 POS-like Category 分布（n=8,708）')
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4_pos_pie.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig4_pos_pie.png'), format='png')
    plt.close()

# ============================================================
# FIG 5: 篇章关系分布柱状图
# ============================================================
def fig5_discourse_bar():
    labels = list(discourse_data.keys())
    counts = list(discourse_data.values())
    total = sum(counts)
    percentages = [c/total*100 for c in counts]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(labels)))
    bars = ax.barh(labels, percentages, color=colors, edgecolor='white')
    ax.set_xlabel('占比 (%)')
    ax.set_title('图5  地书篇章关系分布（n=4,847）')
    ax.invert_yaxis()
    for bar, pct in zip(bars, percentages):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{pct:.1f}%', va='center', fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig5_discourse_bar.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig5_discourse_bar.png'), format='png')
    plt.close()

# ============================================================
# FIG 6: 形态特征分布柱状图
# ============================================================
def fig6_morph_bar():
    labels = list(morph_data.keys())
    counts = list(morph_data.values())
    total = sum(counts)
    percentages = [c/total*100 for c in counts]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(labels)))
    bars = ax.barh(labels, percentages, color=colors, edgecolor='white')
    ax.set_xlabel('占比 (%)')
    ax.set_title('图6  地书形态特征分布（n=10,740）')
    ax.invert_yaxis()
    for bar, pct in zip(bars, percentages):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f'{pct:.1f}%', va='center', fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig6_morph_bar.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig6_morph_bar.png'), format='png')
    plt.close()

# ============================================================
# FIG 7: 六维度雷达图 (地书 vs 中文新闻)
# ============================================================
def fig7_radar():
    # Only plot D1-D3 which have both dishu and natural language data
    dims_plot = ['D1 频率结构\n(Zipf R²)', 'D2 信息密度\n(归一化熵)', 'D3 词汇多样性\n(降采样TTR)']
    dishu_vals = [0.923, 0.914, 0.434]
    news_vals  = [0.894, 0.769, 0.152]
    novel_vals = [0.943, 0.751, 0.151]
    classical_vals = [0.956, 0.687, 0.117]
    literature_vals = [0.929, 0.755, 0.154]

    # Normalize TTR to 0-1 scale (max TTR in our data is 0.434)
    ttr_max = 0.5
    dishu_vals[2] = dishu_vals[2] / ttr_max
    news_vals[2] = news_vals[2] / ttr_max
    novel_vals[2] = novel_vals[2] / ttr_max
    classical_vals[2] = classical_vals[2] / ttr_max
    literature_vals[2] = literature_vals[2] / ttr_max

    N = len(dims_plot)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    dishu_vals += dishu_vals[:1]
    news_vals += news_vals[:1]
    novel_vals += novel_vals[:1]
    classical_vals += classical_vals[:1]
    literature_vals += literature_vals[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={'projection': 'polar'})
    ax.plot(angles, dishu_vals, 'o-', color=C_DISHU, linewidth=2, markersize=6, label='地书')
    ax.plot(angles, news_vals, 's--', color='#56B4E9', linewidth=1.5, markersize=5, label='中文新闻')
    ax.plot(angles, novel_vals, '^--', color='#009E73', linewidth=1.5, markersize=5, label='中文小说')
    ax.plot(angles, classical_vals, 'v--', color='#D55E00', linewidth=1.5, markersize=5, label='中文古文')
    ax.plot(angles, literature_vals, 'd--', color='#F0E442', linewidth=1.5, markersize=5, label='中文文学')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims_plot, fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=7)
    ax.set_title('图7  语言性三维度雷达图\n（D3 TTR 已归一化至 0–1）', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=7)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig7_radar.pdf'), format='pdf')
    fig.savefig(os.path.join(OUTPUT_DIR, 'fig7_radar.png'), format='png')
    plt.close()

# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print(f'Generating figures to: {OUTPUT_DIR}')
    fig1_zipf_slope()
    print('  [1/7] Zipf slope bar chart')
    fig2_ttr_downsampled()
    print('  [2/7] TTR downsampled bar chart')
    fig3_normalized_entropy()
    print('  [3/7] Normalized entropy bar chart')
    fig4_pos_pie()
    print('  [4/7] POS-like category pie chart')
    fig5_discourse_bar()
    print('  [5/7] Discourse relation bar chart')
    fig6_morph_bar()
    print('  [6/7] Morphological features bar chart')
    fig7_radar()
    print('  [7/7] Radar chart')
    print(f'Done! {len(os.listdir(OUTPUT_DIR))} files in {OUTPUT_DIR}')
