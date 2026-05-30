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

def extract_morphological_features(data_dir):
    word_dir = data_dir / "《地书》标注任务1-词标注"
    sentence_dir = data_dir / "《地书》标注任务2-句标注"
    
    all_features = []
    feature_counter = Counter()
    
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
                if ann.get('task_id') == 'morphological_features':
                    value = ann.get('value', '')
                    if isinstance(value, str) and value.strip():
                        features = [f.strip() for f in value.split(',') if f.strip()]
                        for feat in features:
                            all_features.append(feat)
                            feature_counter[feat] += 1
                    elif isinstance(value, list):
                        for v in value:
                            if isinstance(v, str) and v.strip():
                                features = [f.strip() for f in v.split(',') if f.strip()] if ',' in v else [v.strip()]
                                for feat in features:
                                    all_features.append(feat)
                                    feature_counter[feat] += 1
    
    print(f"Total morphological feature tokens: {len(all_features)}")
    print(f"Unique features: {len(feature_counter)}")
    
    return all_features, feature_counter

def analyze_morphological_distribution(feature_counter):
    total = sum(feature_counter.values())
    sorted_features = sorted(feature_counter.items(), key=lambda x: x[1], reverse=True)
    
    result = {
        'total_tokens': total,
        'unique_features': len(feature_counter),
        'distribution': {},
        'top_features': {}
    }
    
    for feat, count in sorted_features:
        percentage = (count / total) * 100
        result['distribution'][feat] = {
            'count': count,
            'percentage': round(percentage, 2)
        }
    
    for feat, count in sorted_features[:15]:
        result['top_features'][feat] = count
    
    print("\n=== Morphological Feature Distribution ===")
    print(f"{'Feature':<25} {'Count':>10} {'%':>10}")
    print("-" * 45)
    for feat, count in sorted_features[:20]:
        percentage = (count / total) * 100
        print(f"{feat:<25} {count:>10} {percentage:>9.2f}%")
    
    if len(sorted_features) > 20:
        print(f"... and {len(sorted_features) - 20} more features")
    
    return result

def run_analysis(output_path):
    print("=" * 60)
    print("EXP-FIX-05: Morphological Feature Distribution Analysis")
    print("=" * 60)
    
    data_dir = BASE_DIR / "素材" / "《地书》标注数据"
    all_features, feature_counter = extract_morphological_features(data_dir)
    
    if not feature_counter:
        print("No morphological feature annotations found")
        return
    
    result = analyze_morphological_distribution(feature_counter)
    
    output_data = {
        'analysis_type': 'Morphological Feature Distribution (EXP-FIX-05)',
        'data_source': 'morphological_features from original Dishu annotations',
        'results': result
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    return output_data

if __name__ == "__main__":
    output_path = str(BASE_DIR / "补充实验" / "results" / "morphological_features_results.json")
    run_analysis(output_path)
