import os
import re
import json
import math
import numpy as np
import pandas as pd
from collections import Counter, defaultdict


def load_data(data_dir):
    """Load all sampled data."""
    data = {}
    
    # List of all expected corpus files
    expected_corpora = [
        'news', 'novel', 'classical', 'literature',
        'ara', 'cmn', 'deu', 'eng', 'fas', 'fra', 'heb', 'hin',
        'dishu'
    ]
    
    for corpus_name in expected_corpora:
        filepath = os.path.join(data_dir, f'{corpus_name}_samples.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data[corpus_name] = json.load(f)
    
    return data


def extract_sentence_features(text):
    """Extract sentence-level features."""
    sentences = re.split(r'[。！？.!?]+\s*', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {}
    
    sentence_lengths = [len(s) for s in sentences]
    word_counts = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    
    return {
        'num_sentences': len(sentences),
        'avg_sentence_length_chars': np.mean(sentence_lengths),
        'std_sentence_length_chars': np.std(sentence_lengths),
        'median_sentence_length_chars': np.median(sentence_lengths),
        'min_sentence_length_chars': np.min(sentence_lengths),
        'max_sentence_length_chars': np.max(sentence_lengths),
        'avg_sentence_length_words': np.mean(word_counts) if word_counts else 0,
    }


def extract_vocabulary_features(text):
    """Extract vocabulary-level features."""
    # Simple tokenization
    words = re.findall(r'\b\w+\b', text.lower())
    char_count = len(text)
    word_count = len(words)
    
    if word_count == 0:
        return {}
    
    word_counts = Counter(words)
    unique_words = len(word_counts)
    
    # Calculate Zipf's law metrics
    sorted_counts = sorted(word_counts.values(), reverse=True)
    ranks = np.arange(1, len(sorted_counts) + 1)
    
    # Log-log linear regression for Zipf's slope
    log_ranks = np.log(ranks)
    log_freqs = np.log(sorted_counts)
    slope, intercept = np.polyfit(log_ranks, log_freqs, 1)
    r_squared = 1 - (sum((log_freqs - (slope*log_ranks + intercept))**2) / 
                      sum((log_freqs - np.mean(log_freqs))**2))
    
    # Information entropy
    probabilities = [count/word_count for count in word_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    max_entropy = math.log2(unique_words) if unique_words > 0 else 0
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    # Vocabulary richness
    ttr = unique_words / word_count
    rttr = unique_words / math.sqrt(word_count) if word_count > 0 else 0
    
    return {
        'char_count': char_count,
        'word_count': word_count,
        'unique_words': unique_words,
        'ttr': ttr,
        'rttr': rttr,
        'zipf_slope': slope,
        'zipf_r_squared': r_squared,
        'entropy': entropy,
        'normalized_entropy': normalized_entropy,
        'lexical_density': unique_words / char_count if char_count > 0 else 0,
    }


def extract_punctuation_features(text):
    """Extract punctuation usage features."""
    punctuation_patterns = {
        'period': r'[。.]',
        'exclamation': r'[！!]',
        'question': r'[？?]',
        'comma': r'[，,]',
        'semicolon': r'[；;]',
        'colon': r'[：:]',
        'quote': r'[「」『』""'']',
        'dash': r'[—\-]',
        'ellipsis': r'[……...]',
    }
    
    features = {}
    total_chars = len(text)
    
    for name, pattern in punctuation_patterns.items():
        count = len(re.findall(pattern, text))
        features[f'punct_{name}_count'] = count
        features[f'punct_{name}_ratio'] = count / total_chars if total_chars > 0 else 0
    
    return features


def extract_ngram_features(text, n=2):
    """Extract n-gram features (simplified)."""
    words = re.findall(r'\b\w+\b', text.lower())
    if len(words) < n:
        return {}
    
    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    
    ngram_counts = Counter(ngrams)
    top_ngrams = ngram_counts.most_common(10)
    
    return {
        f'top_{n}gram_{i+1}': ngram for i, (ngram, count) in enumerate(top_ngrams)
    }


def analyze_corpus(corpus_data, corpus_name):
    """Analyze an entire corpus."""
    all_features = []
    
    if corpus_name == 'dishu':
        # Dishu glosses are a list of strings
        combined_text = ' '.join(corpus_data)
        features = {
            'corpus': corpus_name,
            'sample_id': 'combined',
        }
        
        # Extract all feature types
        features.update(extract_sentence_features(combined_text))
        features.update(extract_vocabulary_features(combined_text))
        features.update(extract_punctuation_features(combined_text))
        
        all_features.append(features)
        
    else:
        # Other corpora are dictionaries of files or single files
        for filename, text in corpus_data.items():
            features = {
                'corpus': corpus_name,
                'sample_id': filename,
            }
            
            features.update(extract_sentence_features(text))
            features.update(extract_vocabulary_features(text))
            features.update(extract_punctuation_features(text))
            
            all_features.append(features)
    
    return all_features


def main():
    """Main function to extract style features."""
    base_dir = 'd:/_College/NLP/Research'
    data_dir = os.path.join(base_dir, '任务组B-LLM应用', 'data')
    results_dir = os.path.join(base_dir, '任务组B-LLM应用', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Load data
    print("Loading data...")
    data = load_data(data_dir)
    print(f"Loaded {len(data)} corpora: {list(data.keys())}")
    
    # Extract features for each corpus
    all_features = []
    
    for corpus_name in sorted(data.keys()):
        if corpus_name in data:
            print(f"\nAnalyzing {corpus_name} corpus...")
            corpus_features = analyze_corpus(data[corpus_name], corpus_name)
            all_features.extend(corpus_features)
            print(f"  Processed {len(corpus_features)} samples")
    
    # Create DataFrame
    if all_features:
        df = pd.DataFrame(all_features)
        
        # Save features
        output_path = os.path.join(results_dir, 'style_features.csv')
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\nFeatures saved to {output_path}")
        
        # Print summary statistics
        print("\n=== Style Feature Summary ===")
        
        # Group by corpus and compute means
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corpus_means = df.groupby('corpus')[numeric_cols].mean()
        
        print("\nMean values by corpus:")
        print(corpus_means.round(3))
        
        # Save summary
        summary_path = os.path.join(results_dir, 'style_feature_summary.csv')
        corpus_means.to_csv(summary_path, encoding='utf-8-sig')
        
    else:
        print("No data to process!")


if __name__ == "__main__":
    main()
