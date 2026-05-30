import os
import json
from collections import Counter, defaultdict
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path("d:/_College/NLP/Research")

def load_annotation_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return None

def extract_pos_categories(data_dir):
    word_dir = data_dir / "《地书》标注任务1-词标注"
    sentence_dir = data_dir / "《地书》标注任务2-句标注"
    
    all_categories = []
    category_counter = Counter()
    
    for dir_path, label in [(word_dir, "词标注"), (sentence_dir, "句标注")]:
        if not dir_path.exists():
            continue
            
        files = list(dir_path.glob("*.txt"))
        print(f"Loading {label}: {len(files)} files")
        
        for filepath in files:
            data = load_annotation_file(str(filepath))
            if data is None:
                continue
            
            for ann in data.get('annotations', []):
                if ann.get('task_id') == 'pos_like_category':
                    value = ann.get('value', '')
                    if isinstance(value, str) and value.strip():
                        categories = [c.strip() for c in value.split(',') if c.strip()]
                        for cat in categories:
                            all_categories.append(cat)
                            category_counter[cat] += 1
                    elif isinstance(value, list):
                        for v in value:
                            if isinstance(v, str) and v.strip():
                                categories = [c.strip() for c in v.split(',') if c.strip()] if ',' in v else [v.strip()]
                                for cat in categories:
                                    all_categories.append(cat)
                                    category_counter[cat] += 1
    
    print(f"Total POS category tokens: {len(all_categories)}")
    print(f"Unique POS categories: {len(category_counter)}")
    
    return all_categories, category_counter

def analyze_pos_distribution(category_counter):
    total = sum(category_counter.values())
    sorted_categories = sorted(category_counter.items(), key=lambda x: x[1], reverse=True)
    
    result = {
        'total_tokens': total,
        'unique_categories': len(category_counter),
        'distribution': {},
        'top_categories': {}
    }
    
    for cat, count in sorted_categories:
        percentage = (count / total) * 100
        result['distribution'][cat] = {
            'count': count,
            'percentage': round(percentage, 2)
        }
    
    for cat, count in sorted_categories[:10]:
        result['top_categories'][cat] = count
    
    print("\n=== POS-like Category Distribution ===")
    print(f"{'Category':<25} {'Count':>10} {'%':>10}")
    print("-" * 45)
    for cat, count in sorted_categories[:15]:
        percentage = (count / total) * 100
        print(f"{cat:<25} {count:>10} {percentage:>9.2f}%")
    
    if len(sorted_categories) > 15:
        print(f"... and {len(sorted_categories) - 15} more categories")
    
    return result

def run_analysis(output_path):
    print("=" * 60)
    print("EXP-FIX-03: POS-like Category Distribution Analysis")
    print("=" * 60)
    
    data_dir = BASE_DIR / "素材" / "《地书》标注数据"
    all_categories, category_counter = extract_pos_categories(data_dir)
    
    if not category_counter:
        print("No POS-like category annotations found")
        return
    
    result = analyze_pos_distribution(category_counter)
    
    output_data = {
        'analysis_type': 'POS-like Category Distribution (EXP-FIX-03)',
        'data_source': 'pos_like_category from original Dishu annotations',
        'results': result
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    return output_data

if __name__ == "__main__":
    output_path = str(BASE_DIR / "补充实验" / "results" / "pos_category_results.json")
    run_analysis(output_path)
