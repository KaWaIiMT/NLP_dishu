import os
import json
import math
import numpy as np
from collections import Counter
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

def shannon_entropy(text_list):
    if not text_list:
        return 0
    
    counter = Counter(text_list)
    total = len(text_list)
    
    entropy = 0
    for count in counter.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy

def normalized_entropy(text_list):
    if not text_list:
        return 0
    
    entropy = shannon_entropy(text_list)
    unique_count = len(set(text_list))
    
    if unique_count <= 1:
        return 0
    
    max_entropy = math.log2(unique_count)
    return entropy / max_entropy if max_entropy > 0 else 0

def type_token_ratio(text_list):
    if not text_list:
        return 0
    return len(set(text_list)) / len(text_list)

def root_ttr(text_list):
    if not text_list:
        return 0
    n = len(text_list)
    ttr = len(set(text_list)) / n if n > 0 else 0
    return math.sqrt(ttr) if ttr > 0 else 0

def mtld(text_list, threshold=0.72):
    if not text_list:
        return 0
    
    words = list(text_list)
    n = len(words)
    
    if n < 10:
        return n
    
    factors = []
    
    for i in range(10, n + 1, 10):
        segment = words[:i]
        ttr = len(set(segment)) / i if i > 0 else 0
        
        if ttr <= threshold:
            if len(factors) == 0:
                prev_ttr = len(set(words[:i-10])) / (i-10) if i > 10 else 1.0
                if prev_ttr != ttr:
                    factor = (threshold - prev_ttr) / (ttr - prev_ttr)
                    factors.append(factor)
            break
        
        factors.append(1.0)
    
    if not factors:
        return n
    
    return sum(factors) / len(factors) * 10 if factors else n

def extract_literal_glosses(data_dir):
    word_dir = data_dir / "《地书》标注任务1-词标注"
    sentence_dir = data_dir / "《地书》标注任务2-句标注"
    
    all_glosses = []
    
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
                if ann.get('task_id') == 'literal_gloss':
                    value = ann.get('value', '')
                    if isinstance(value, str) and value.strip():
                        all_glosses.append(value.strip())
                    elif isinstance(value, list):
                        for v in value:
                            if isinstance(v, str) and v.strip():
                                all_glosses.append(v.strip())
    
    return all_glosses

def compute_diversity_metrics(text_list, label):
    if not text_list:
        return None
    
    result = {
        'label': label,
        'total_tokens': len(text_list),
        'unique_types': len(set(text_list)),
        'TTR': type_token_ratio(text_list),
        'RTTR': root_ttr(text_list),
        'Shannon_Entropy': shannon_entropy(text_list),
        'Normalized_Entropy': normalized_entropy(text_list),
        'MTLD': mtld(text_list)
    }
    
    print(f"\n=== {label} Diversity Metrics ===")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Unique types: {result['unique_types']}")
    print(f"TTR: {result['TTR']:.4f}")
    print(f"RTTR: {result['RTTR']:.4f}")
    print(f"Shannon Entropy: {result['Shannon_Entropy']:.4f}")
    print(f"Normalized Entropy: {result['Normalized_Entropy']:.4f}")
    print(f"MTLD: {result['MTLD']:.2f}")
    
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
        return compute_diversity_metrics(words, corpus_name)
    except Exception as e:
        print(f"Error loading {corpus_name}: {e}")
        return None

def run_analysis(output_path):
    print("=" * 60)
    print("EXP-FIX-02: Entropy and Lexical Diversity Analysis")
    print("=" * 60)
    
    data_dir = BASE_DIR / "素材" / "《地书》标注数据"
    corpus_base_dir = BASE_DIR / "任务组A-数据准备" / "Task3-语料库采样" / "采样结果"
    
    all_glosses = extract_literal_glosses(data_dir)
    
    results = []
    
    if all_glosses:
        dishu_result = compute_diversity_metrics(all_glosses, "地书_literal_gloss")
        if dishu_result:
            results.append(dishu_result)
    
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
            'RTTR': f"{r['RTTR']:.4f}",
            'Shannon_H': f"{r['Shannon_Entropy']:.4f}",
            'Norm_H': f"{r['Normalized_Entropy']:.4f}",
            'MTLD': f"{r['MTLD']:.2f}"
        })
    
    output_data = {
        'analysis_type': 'Entropy and Lexical Diversity (EXP-FIX-02)',
        'data_source': 'literal_gloss from original Dishu annotations',
        'results': results,
        'comparison_table': comparison_table
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Comparison Table ===")
    print(f"{'Corpus':<25} {'Tokens':>8} {'Types':>8} {'TTR':>8} {'RTTR':>8} {'H':>8} {'Norm_H':>8} {'MTLD':>8}")
    print("-" * 85)
    for row in comparison_table:
        print(f"{row['Corpus']:<25} {row['Tokens']:>8} {row['Types']:>8} {row['TTR']:>8} {row['RTTR']:>8} {row['Shannon_H']:>8} {row['Norm_H']:>8} {row['MTLD']:>8}")
    
    print(f"\nResults saved to: {output_path}")
    
    return output_data

if __name__ == "__main__":
    output_path = str(BASE_DIR / "补充实验" / "results" / "entropy_diversity_results.json")
    run_analysis(output_path)
