import os
import sys
import json
import pandas as pd
from datetime import datetime


def main():
    """Generate final report from existing results."""
    print("=" * 80)
    print("生成综合实验报告")
    print("=" * 80)
    print()
    
    base_dir = 'd:/_College/NLP/Research'
    results_dir = os.path.join(base_dir, '任务组B-LLM应用', 'results')
    
    # Load results
    report = {
        'experiment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sections': []
    }
    
    # Load style features summary
    features_path = os.path.join(results_dir, 'style_feature_summary.csv')
    if os.path.exists(features_path):
        features_df = pd.read_csv(features_path)
        report['sections'].append({
            'title': '语体特征分析',
            'content': features_df.to_dict(orient='records')
        })
        print("[OK] 已加载语体特征分析结果")
    
    # Load classification summary
    classification_path = os.path.join(results_dir, 'classification_summary.json')
    if os.path.exists(classification_path):
        with open(classification_path, 'r', encoding='utf-8') as f:
            classification_data = json.load(f)
        report['sections'].append({
            'title': '零样本分类结果',
            'content': classification_data
        })
        print("[OK] 已加载零样本分类结果")
    
    # Load detailed features
    detailed_features_path = os.path.join(results_dir, 'style_features.csv')
    if os.path.exists(detailed_features_path):
        detailed_features_df = pd.read_csv(detailed_features_path)
        report['sections'].append({
            'title': '详细语体特征数据',
            'content': detailed_features_df.to_dict(orient='records')
        })
        print("[OK] 已加载详细语体特征数据")
    
    # Save report
    report_path = os.path.join(base_dir, '任务组B-LLM应用', 'Task_B_Complete_Report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n综合报告已保存至: {report_path}")
    
    # Print a summary
    print("\n" + "=" * 80)
    print("实验完成总结:")
    print("=" * 80)
    print("- 已加载所有语料库（中文新闻、小说、古文、名著，多语言语料，地书语料）")
    print("- 已提取所有语料的语体特征")
    print("- 已完成零样本风格分类")
    print("- 结果文件已保存至 results/ 目录")
    
    if classification_path:
        print(f"\n分类准确率: {classification_data.get('overall_accuracy', 0):.2%}")


if __name__ == "__main__":
    main()
