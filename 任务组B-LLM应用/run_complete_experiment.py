import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add scripts directory to path
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
sys.path.append(scripts_dir)

from data_loader import main as load_data
from style_feature_extractor import main as extract_features
from zero_shot_classification import main as run_classification


def main():
    """Run complete experiment pipeline."""
    print("=" * 80)
    print("地书图形语言 vs 自然语言分析 - 完整实验流程")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Load data
    print("\n" + "=" * 80)
    print("步骤 1: 加载数据")
    print("=" * 80)
    load_data()
    
    # Step 2: Extract style features
    print("\n" + "=" * 80)
    print("步骤 2: 提取语体特征")
    print("=" * 80)
    extract_features()
    
    # Step 3: Run zero-shot classification
    print("\n" + "=" * 80)
    print("步骤 3: 零样本风格分类")
    print("=" * 80)
    run_classification()
    
    # Generate final report
    print("\n" + "=" * 80)
    print("生成综合报告")
    print("=" * 80)
    generate_final_report()
    
    print("\n" + "=" * 80)
    print("实验流程完成!")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def generate_final_report():
    """Generate final comprehensive report."""
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
    
    # Load classification summary
    classification_path = os.path.join(results_dir, 'classification_summary.json')
    if os.path.exists(classification_path):
        with open(classification_path, 'r', encoding='utf-8') as f:
            classification_data = json.load(f)
        report['sections'].append({
            'title': '零样本分类结果',
            'content': classification_data
        })
    
    # Save report
    report_path = os.path.join(base_dir, '任务组B-LLM应用', 'Task_B_Complete_Report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"综合报告已保存至: {report_path}")
    
    # Print a summary
    print("\n实验完成总结:")
    print("- 已加载所有语料库（中文新闻、小说、古文、名著，多语言语料，地书语料）")
    print("- 已提取所有语料的语体特征")
    print("- 已完成零样本风格分类")
    print("- 结果文件已保存至 results/ 目录")


if __name__ == "__main__":
    main()
