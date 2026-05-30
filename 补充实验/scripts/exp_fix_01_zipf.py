import os
import json
import math
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
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

def extract_literal_glosses(data_dir):
    word_dir = data_dir / "《地书》标注任务1-词标注"
    sentence_dir = data_dir / "《地书》标注任务2-句标注"
    
    all_glosses = []
    gloss_counter = Counter()
    
    for dir_path, label in [(word_dir, "词标注"), (sentence_dir, "句标注")]:
        if not dir_path.exists():
            print(f"Directory not found: {dir_path}")
            continue
            
        files = list(dir_path.glob("*.txt"))
        print(f"Loading {label}: {len(files)} files")
        
        for filepath in files:
            data = load_annotation_file(str(filepath))
            if data is None:
                continue
            
            for ann in data.get('annotations', []):
                if ann.get('task_id') == 'literal_gloss':
                    value = ann.get('value', '')
                    if isinstance(value, str) and value.strip():
                        all_glosses.append(value.strip())
                        gloss_counter[value.strip()] += 1
                    elif isinstance(value, list):
                        for v in value:
                            if isinstance(v, str) and v.strip():
                                all_glosses.append(v.strip())
                                gloss_counter[v.strip()] += 1
    
    print(f"Total gloss tokens: {len(all_glosses)}")
    print(f"Unique gloss types: {len(gloss_counter)}")
    
    return all_glosses, gloss_counter

def compute_zipf_analysis(counter, label):
    sorted_counts = sorted(counter.values(), reverse=True)
    ranks = list(range(1, len(sorted_counts) + 1))
    
    if len(sorted_counts) < 10:
        print(f"Warning: Not enough data for {label}")
        return None
    
    log_ranks = np.log(ranks)
    log_counts = np.log(sorted_counts)
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_ranks, log_counts)
    r_squared = r_value ** 2
    
    result = {
        'label': label,
        'total_tokens': sum(sorted_counts),
        'unique_types': len(sorted_counts),
        'TTR': len(sorted_counts) / sum(sorted_counts) if sum(sorted_counts) > 0 else 0,
        'zipf_slope': float(slope),
        'zipf_intercept': float(intercept),
        'zipf_r_squared': float(r_squared),
        'zipf_p_value': float(p_value),
        'top_10_words': dict(sorted(counter.items(), key=lambda x: x[1], reverse=True)[:10])
    }
    
    print(f"\n=== {label} Zipf Analysis ===")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Unique types: {result['unique_types']}")
    print(f"TTR: {result['TTR']:.4f}")
    print(f"Zipf slope (s): {slope:.4f}")
    print(f"Zipf R²: {r_squared:.4f}")
    print(f"Top 10 words: {result['top_10_words']}")
    
    return result

def load_corpus_for_comparison(corpus_path, corpus_name, sample_chars=50000):
    filepath = corpus_path / 'all.txt'
    if not filepath.exists():
        filepath = corpus_path / 'train.txt'
    
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if len(text) > sample_chars:
            text = text[:sample_chars]
        
        words = list(text)
        counter = Counter(words)
        
        return compute_zipf_analysis(counter, corpus_name)
    except Exception as e:
        print(f"Error loading {corpus_name}: {e}")
        return None

def run_analysis(output_path):
    print("=" * 60)
    print("EXP-FIX-01: Zipf's Law Analysis Based on literal_gloss")
    print("=" * 60)
    
    data_dir = BASE_DIR / "素材" / "《地书》标注数据"
    corpus_base_dir = BASE_DIR / "任务组A-数据准备" / "Task3-语料库采样" / "采样结果"
    
    all_glosses, gloss_counter = extract_literal_glosses(data_dir)
    
    results = []
    
    if gloss_counter:
        zipf_result = compute_zipf_analysis(gloss_counter, "地书_literal_gloss")
        if zipf_result:
            results.append(zipf_result)
    
    print("\n" + "=" * 60)
    print("Loading comparison corpora...")
    print("=" * 60)
    
    corpora = [
        ('中文_新闻', 'Chinese_News'),
        ('中文_小说', 'Chinese_Novel'),
        ('中文_古文', 'Chinese_Classical'),
        ('中文_名著', 'Chinese_Literature'),
        ('多语言_eng', 'English'),
        ('多语言_deu', 'German'),
        ('多语言_fra', 'French'),
        ('多语言_jpn', 'Japanese'),
    ]
    
    for corpus_dir, corpus_name in corpora:
        corpus_path = corpus_base_dir / corpus_dir
        result = load_corpus_for_comparison(corpus_path, corpus_name)
        if result:
            results.append(result)
    
    comparison_table = []
    for r in results:
        comparison_table.append({
            'Corpus': r['label'],
            'Tokens': r['total_tokens'],
            'Types': r['unique_types'],
            'TTR': f"{r['TTR']:.4f}",
            'Zipf_s': f"{r['zipf_slope']:.4f}",
            'Zipf_R2': f"{r['zipf_r_squared']:.4f}"
        })
    
    output_data = {
        'analysis_type': 'Zipf Law Analysis (EXP-FIX-01)',
        'data_source': 'literal_gloss from original Dishu annotations',
        'results': results,
        'comparison_table': comparison_table
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Comparison Table ===")
    print(f"{'Corpus':<25} {'Tokens':>10} {'Types':>10} {'TTR':>10} {'Zipf_s':>10} {'Zipf_R2':>10}")
    print("-" * 75)
    for row in comparison_table:
        print(f"{row['Corpus']:<25} {row['Tokens']:>10} {row['Types']:>10} {row['TTR']:>10} {row['Zipf_s']:>10} {row['Zipf_R2']:>10}")
    
    print(f"\nResults saved to: {output_path}")
    
    return output_data

if __name__ == "__main__":
    output_path = str(BASE_DIR / "补充实验" / "results" / "zipf_analysis_results.json")
    run_analysis(output_path)
