import os
import json
import pandas as pd
import numpy as np
from datetime import datetime


def load_results(results_dir):
    """Load all result files."""
    results = {}
    
    # Load style features
    features_path = os.path.join(results_dir, 'style_features.csv')
    if os.path.exists(features_path):
        results['style_features'] = pd.read_csv(features_path)
    
    # Load style feature summary
    summary_path = os.path.join(results_dir, 'style_feature_summary.csv')
    if os.path.exists(summary_path):
        results['style_summary'] = pd.read_csv(summary_path)
    
    # Load classification results
    classification_path = os.path.join(results_dir, 'zero_shot_classification_results.csv')
    if os.path.exists(classification_path):
        results['classification'] = pd.read_csv(classification_path)
    
    # Load classification summary
    class_summary_path = os.path.join(results_dir, 'classification_summary.json')
    if os.path.exists(class_summary_path):
        with open(class_summary_path, 'r', encoding='utf-8') as f:
            results['classification_summary'] = json.load(f)
    
    return results


def dataframe_to_simple_table(df):
    """Convert DataFrame to simple markdown table without tabulate."""
    if df.empty:
        return ""
    
    # Get headers
    headers = list(df.columns)
    if hasattr(df, 'index') and df.index.name:
        headers = [df.index.name] + headers
    
    # Create header row
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Add data rows
    for idx, row in df.iterrows():
        row_values = []
        if hasattr(df, 'index') and df.index.name:
            row_values.append(str(idx))
        for val in row:
            if isinstance(val, float):
                row_values.append(f"{val:.3f}")
            else:
                row_values.append(str(val))
        table += "| " + " | ".join(row_values) + " |\n"
    
    return table


def generate_markdown_report(results, output_path):
    """Generate a comprehensive markdown report."""
    
    report = f"""# 任务组B：地书与自然语言的语体特征分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. 执行摘要

本报告总结了任务组B的工作，包括：
- 自然语言数据（新闻、小说）与地书数据的加载和采样
- 多维度语体特征提取
- 基于Gemini API的零样本风格分类（当前为模拟模式）

---

## 2. 数据概览

### 2.1 数据集统计

| 语料类型 | 样本数 | 总字符数 | 来源 |
|---------|--------|----------|------|
| 新闻 | 3 | ~30,000 | THUcNews |
| 小说 | 9 | ~450,000 | 小说数据集 |
| 地书注释 | 1 | ~28,000 | 地书标注数据 |

---

## 3. 语体特征分析

"""
    
    # Add style feature summary
    if 'style_summary' in results:
        summary_df = results['style_summary']
        report += "### 3.1 关键语体特征对比\n\n"
        report += dataframe_to_simple_table(summary_df)
        report += "\n\n"
    
    if 'style_features' in results:
        df = results['style_features']
        
        report += "### 3.2 主要发现\n\n"
        
        # Group by corpus
        corpus_groups = df.groupby('corpus')
        
        for corpus in ['news', 'novel', 'dishu']:
            if corpus in corpus_groups.groups:
                group = corpus_groups.get_group(corpus)
                avg_sent_len = group['avg_sentence_length_chars'].mean()
                avg_ttr = group['ttr'].mean()
                avg_lex_density = group['lexical_density'].mean()
                
                corpus_name = {
                    'news': '新闻',
                    'novel': '小说',
                    'dishu': '地书'
                }[corpus]
                
                report += f"**{corpus_name}语料特征**：\n"
                report += f"- 平均句长: {avg_sent_len:.1f} 字符\n"
                report += f"- 平均类型-标记比(TTR): {avg_ttr:.3f}\n"
                report += f"- 平均词汇密度: {avg_lex_density:.3f}\n\n"
    
    # Add classification results
    report += "---\n\n## 4. 零样本风格分类结果\n\n"
    
    if 'classification_summary' in results:
        summary = results['classification_summary']
        report += f"### 4.1 总体准确率\n\n"
        report += f"**整体准确率**: {summary['overall_accuracy']:.1%}\n\n"
        
        report += "### 4.2 各语料分类表现\n\n"
        for corpus, stats in summary['per_corpus'].items():
            corpus_name = {
                'news': '新闻',
                'novel': '小说',
                'dishu': '地书'
            }.get(corpus, corpus)
            
            report += f"- **{corpus_name}**: {stats['correct']}/{stats['total']} ({stats['accuracy']:.1%})\n"
    
    if 'classification' in results:
        report += "\n### 4.3 详细分类结果\n\n"
        class_df = results['classification']
        report += dataframe_to_simple_table(class_df[['corpus', 'true_style', 'predicted_style', 'confidence']])
    
    # Add methodology section
    report += "\n\n---\n\n## 5. 方法说明\n\n"
    report += "### 5.1 特征提取方法\n\n"
    report += "我们从文本中提取了以下类型的语体特征：\n\n"
    report += "1. **句子层面特征**：句子数量、平均句长、句长标准差等\n"
    report += "2. **词汇层面特征**：词汇量、类型-标记比(TTR)、Zipf定律拟合参数、信息熵等\n"
    report += "3. **标点符号特征**：各类型标点的使用频率\n\n"
    
    report += "### 5.2 Gemini API集成\n\n"
    report += "当前实现使用模拟模式，实际应用时需要：\n"
    report += "1. 配置有效的Gemini API密钥\n"
    report += "2. 使用真实的API调用替换模拟方法\n"
    report += "3. 优化Prompt设计以提高分类准确率\n\n"
    
    report += "---\n\n## 6. 结论与建议\n\n"
    report += "1. **语体差异**：新闻、小说和地书注释在语体特征上存在可观测的差异\n"
    report += "2. **API集成**：当前使用模拟模式，未来可集成真实的Gemini API以获得更好的分类效果\n"
    report += "3. **数据扩展**：可考虑增加更多语料类型（如古文、维基百科等）进行对比分析\n"
    report += "4. **模型训练**：未来可考虑基于提取的特征训练专用的风格分类模型\n\n"
    
    report += "---\n\n## 附录\n\n"
    report += "### 目录结构\n\n"
    report += "```\n"
    report += "task_group_b/\n"
    report += "├── data/\n"
    report += "│   ├── news_samples.json\n"
    report += "│   ├── novel_samples.json\n"
    report += "│   └── dishu_glosses.json\n"
    report += "├── results/\n"
    report += "│   ├── style_features.csv\n"
    report += "│   ├── style_feature_summary.csv\n"
    report += "│   ├── zero_shot_classification_results.csv\n"
    report += "│   └── classification_summary.json\n"
    report += "└── scripts/\n"
    report += "    ├── data_loader.py\n"
    report += "    ├── style_feature_extractor.py\n"
    report += "    ├── gemini_api_client.py\n"
    report += "    ├── zero_shot_classification.py\n"
    report += "    └── generate_report.py\n"
    report += "```\n"
    
    # Save the report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report


def main():
    """Main function to generate the report."""
    base_dir = 'd:/_College/NLP/Research'
    results_dir = os.path.join(base_dir, 'task_group_b', 'results')
    
    print("Loading results...")
    results = load_results(results_dir)
    
    print("Generating report...")
    report_path = os.path.join(base_dir, 'task_group_b', 'Task_B_Report.md')
    report = generate_markdown_report(results, report_path)
    
    print(f"Report saved to: {report_path}")
    print("\n=== Report Preview ===")
    print(report[:1000], "...")


if __name__ == "__main__":
    main()
