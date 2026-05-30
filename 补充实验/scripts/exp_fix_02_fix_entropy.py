import os
import json
import math
import random
import numpy as np
from collections import Counter
from scipy import stats
import sys
from pathlib import Path
import re

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path("d:/_College/NLP/Research")
random.seed(42)
np.random.seed(42)

def tokenize_chinese(text):
    try:
        import jieba
        return list(jieba.cut(text))
    except:
        return list(text)

def tokenize_ewp(text):
    pattern = r"[a-zA-Zà-üÀ-Üß]+"
    return re.findall(pattern, text.lower())

def tokenize_japanese(text):
    pattern = r'[ぁ-ゟ゠-ヿ一-鿿]+'
    return re.findall(pattern, text)

def get_tokenizer(lang):
    if lang in ['chinese', 'chinese_news', 'chinese_novel', 'chinese_classical', 'chinese_literature']:
        return tokenize_chinese
    elif lang in ['english', 'german', 'french', 'eng', 'deu', 'fra']:
        return tokenize_ewp
    elif lang in ['japanese', 'jpn']:
        return tokenize_japanese
    else:
        return tokenize_chinese

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

def downsampled_ttr(word_list, target_size, n_trials=100):
    tt_ratios = []
    actual_size = min(len(word_list), target_size)
    
    if len(word_list) < target_size:
        return len(set(word_list)) / len(word_list) if word_list else 0, 0.0
    
    for _ in range(n_trials):
        sample = random.sample(word_list, actual_size)
        tt_ratios.append(len(set(sample)) / actual_size)
    
    return np.mean(tt_ratios), np.std(tt_ratios)

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

def compute_diversity_metrics(text_list, label, dishu_size=None):
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
    
    if dishu_size and len(text_list) >= dishu_size:
        ds_ttr, ds_std = downsampled_ttr(text_list, dishu_size)
        result['TTR_Downsampled'] = ds_ttr
        result['TTR_Downsampled_Std'] = ds_std
    else:
        result['TTR_Downsampled'] = result['TTR']
        result['TTR_Downsampled_Std'] = 0.0
    
    print(f"\n=== {label} Diversity Metrics ===")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Unique types: {result['unique_types']}")
    print(f"TTR (raw): {result['TTR']:.4f}")
    if dishu_size and len(text_list) >= dishu_size:
        print(f"TTR (downsampled to {dishu_size}): {result['TTR_Downsampled']:.4f} ± {result['TTR_Downsampled_Std']:.4f}")
    print(f"RTTR: {result['RTTR']:.4f}")
    print(f"Shannon Entropy: {result['Shannon_Entropy']:.4f}")
    print(f"Normalized Entropy: {result['Normalized_Entropy']:.4f}")
    print(f"MTLD: {result['MTLD']:.2f}")
    
    return result

def load_corpus_for_comparison(corpus_path, corpus_name, lang, dishu_size):
    filepath = corpus_path / 'all.txt'
    if not filepath.exists():
        filepath = corpus_path / 'train.txt'
    
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        tokenizer = get_tokenizer(lang)
        words = tokenizer(text)
        
        if len(words) < 100:
            print(f"Warning: {corpus_name} has only {len(words)} tokens, skipping")
            return None
        
        return compute_diversity_metrics(words, corpus_name, dishu_size)
    except Exception as e:
        print(f"Error loading {corpus_name}: {e}")
        return None

def run_analysis(output_path):
    print("=" * 60)
    print("EXP-FIX-02-FIX: Entropy and Lexical Diversity (Fixed Sampling)")
    print("=" * 60)
    
    data_dir = BASE_DIR / "素材" / "《地书》标注数据"
    corpus_base_dir = BASE_DIR / "任务组A-数据准备" / "Task3-语料库采样" / "采样结果"
    
    all_glosses = extract_literal_glosses(data_dir)
    
    dishu_size = len(all_glosses)
    print(f"\n地书 token count: {dishu_size}")
    print(f"Will use this as target for downsampling TTR comparison")
    
    results = []
    
    if all_glosses:
        dishu_result = compute_diversity_metrics(all_glosses, "地书_literal_gloss")
        if dishu_result:
            dishu_result['TTR_Downsampled'] = dishu_result['TTR']
            dishu_result['TTR_Downsampled_Std'] = 0.0
            results.append(dishu_result)
    
    print("\n" + "=" * 60)
    print("Loading comparison corpora with correct tokenization...")
    print("=" * 60)
    
    corpora = [
        ('中文_新闻', 'Chinese_News', 'chinese'),
        ('中文_小说', 'Chinese_Novel', 'chinese'),
        ('中文_古文', 'Chinese_Classical', 'chinese'),
        ('中文_名著', 'Chinese_Literature', 'chinese'),
        ('多语言_eng', 'English', 'english'),
        ('多语言_deu', 'German', 'german'),
        ('多语言_fra', 'French', 'french'),
        ('多语言_jpn', 'Japanese', 'japanese'),
    ]
    
    for corpus_dir, corpus_name, lang in corpora:
        corpus_path = corpus_base_dir / corpus_dir
        result = load_corpus_for_comparison(corpus_path, corpus_name, lang, dishu_size)
        if result:
            results.append(result)
    
    comparison_table = []
    for r in results:
        row = {
            'Corpus': r['label'],
            'Tokens': r['total_tokens'],
            'Types': r['unique_types'],
            'TTR_raw': f"{r['TTR']:.4f}",
            'TTR_ds': f"{r['TTR_Downsampled']:.4f}",
            'RTTR': f"{r['RTTR']:.4f}",
            'Shannon_H': f"{r['Shannon_Entropy']:.4f}",
            'Norm_H': f"{r['Normalized_Entropy']:.4f}",
            'MTLD': f"{r['MTLD']:.2f}"
        }
        comparison_table.append(row)
    
    output_data = {
        'analysis_type': 'Entropy and Lexical Diversity (EXP-FIX-02-FIX) - Fixed Sampling',
        'data_source': 'literal_gloss from original Dishu annotations',
        'dishu_token_count': dishu_size,
        'sampling_note': f'All corpora TTR downsampled to {dishu_size} tokens (100 trials)',
        'tokenization_note': {
            'chinese': 'jieba segmentation',
            'ewp': 'regex word matching [a-zA-Z]+',
            'japanese': 'regex kanji/hiragana/katakana matching'
        },
        'results': results,
        'comparison_table': comparison_table
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Comparison Table (Corrected) ===")
    print(f"{'Corpus':<22} {'Tokens':>8} {'Types':>8} {'TTR_raw':>8} {'TTR_ds':>10} {'H':>8} {'Norm_H':>8}")
    print("-" * 82)
    for row in comparison_table:
        print(f"{row['Corpus']:<22} {row['Tokens']:>8} {row['Types']:>8} {row['TTR_raw']:>8} {row['TTR_ds']:>10} {row['Shannon_H']:>8} {row['Norm_H']:>8}")
    
    print(f"\nResults saved to: {output_path}")
    
    return output_data

if __name__ == "__main__":
    output_path = str(BASE_DIR / "补充实验" / "results" / "entropy_diversity_fixed.json")
    run_analysis(output_path)
