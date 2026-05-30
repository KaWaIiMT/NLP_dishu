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

def extract_discourse_relations(data_dir):
    sentence_dir = data_dir / "《地书》标注任务2-句标注"
    
    all_relations = []
    relation_counter = Counter()
    
    if not sentence_dir.exists():
        print(f"Directory not found: {sentence_dir}")
        return all_relations, relation_counter
    
    files = list(sentence_dir.glob("*.txt"))
    print(f"Loading 句标注: {len(files)} files")
    
    for filepath in files:
        data = load_annotation_file(str(filepath))
        if data is None:
            continue
        
        for ann in data.get('annotations', []):
            if ann.get('task_id') == 'discourse_relation':
                value = ann.get('value', '')
                if isinstance(value, str) and value.strip():
                    all_relations.append(value.strip())
                    relation_counter[value.strip()] += 1
                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, str) and v.strip():
                            all_relations.append(v.strip())
                            relation_counter[v.strip()] += 1
    
    print(f"Total discourse relation annotations: {len(all_relations)}")
    print(f"Unique relations: {len(relation_counter)}")
    
    return all_relations, relation_counter

def analyze_discourse_distribution(relation_counter):
    total = sum(relation_counter.values())
    sorted_relations = sorted(relation_counter.items(), key=lambda x: x[1], reverse=True)
    
    result = {
        'total_annotations': total,
        'unique_relations': len(relation_counter),
        'distribution': {},
        'top_relations': {}
    }
    
    for rel, count in sorted_relations:
        percentage = (count / total) * 100
        result['distribution'][rel] = {
            'count': count,
            'percentage': round(percentage, 2)
        }
    
    for rel, count in sorted_relations[:10]:
        result['top_relations'][rel] = count
    
    print("\n=== Discourse Relation Distribution ===")
    print(f"{'Relation':<25} {'Count':>10} {'%':>10}")
    print("-" * 45)
    for rel, count in sorted_relations:
        percentage = (count / total) * 100
        print(f"{rel:<25} {count:>10} {percentage:>9.2f}%")
    
    return result

def run_analysis(output_path):
    print("=" * 60)
    print("EXP-FIX-04: Discourse Relation Distribution Analysis")
    print("=" * 60)
    
    data_dir = BASE_DIR / "素材" / "《地书》标注数据"
    all_relations, relation_counter = extract_discourse_relations(data_dir)
    
    if not relation_counter:
        print("No discourse relation annotations found")
        return
    
    result = analyze_discourse_distribution(relation_counter)
    
    output_data = {
        'analysis_type': 'Discourse Relation Distribution (EXP-FIX-04)',
        'data_source': 'discourse_relation from original Dishu annotations',
        'results': result
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    return output_data

if __name__ == "__main__":
    output_path = str(BASE_DIR / "补充实验" / "results" / "discourse_relation_results.json")
    run_analysis(output_path)
