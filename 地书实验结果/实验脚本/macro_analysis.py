import os
import json
import math
import numpy as np
import pandas as pd
from collections import Counter, defaultdict

def calculate_zipf_law(word_counts):
    """Calculate Zipf's Law metrics."""
    # Sort words by frequency descending
    sorted_counts = sorted(word_counts.values(), reverse=True)
    
    # Calculate theoretical Zipf distribution (rank * frequency = constant)
    ranks = np.arange(1, len(sorted_counts) + 1)
    frequencies = np.array(sorted_counts)
    
    # Calculate Zipf's coefficient (k = rank * frequency)
    zipf_coefficients = ranks * frequencies
    mean_k = np.mean(zipf_coefficients)
    std_k = np.std(zipf_coefficients)
    
    # Calculate R-squared for linear fit on log-log scale
    log_ranks = np.log(ranks)
    log_freqs = np.log(frequencies)
    
    # Linear regression
    slope, intercept = np.polyfit(log_ranks, log_freqs, 1)
    r_squared = 1 - (sum((log_freqs - (slope*log_ranks + intercept))**2) / 
                    sum((log_freqs - np.mean(log_freqs))**2))
    
    return {
        "zipf_mean_k": mean_k,
        "zipf_std_k": std_k,
        "zipf_slope": slope,
        "zipf_r_squared": r_squared,
        "total_words": sum(frequencies),
        "unique_words": len(frequencies)
    }

def calculate_information_entropy(word_counts):
    """Calculate information entropy of the vocabulary."""
    total_words = sum(word_counts.values())
    if total_words == 0:
        return 0.0
    
    probabilities = [count/total_words for count in word_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    
    # Calculate maximum possible entropy (uniform distribution)
    max_entropy = math.log2(len(word_counts)) if len(word_counts) > 0 else 0
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    return {
        "entropy": entropy,
        "max_entropy": max_entropy,
        "normalized_entropy": normalized_entropy
    }

def calculate_vocabulary_richness(word_counts):
    """Calculate vocabulary richness metrics."""
    total_words = sum(word_counts.values())
    unique_words = len(word_counts)
    
    if total_words == 0:
        return {
            "ttr": 0.0,
            "rttr": 0.0,
            "mtld": 0.0
        }
    
    # Type-Token Ratio
    ttr = unique_words / total_words
    
    # Root Type-Token Ratio
    rttr = unique_words / math.sqrt(total_words) if total_words > 0 else 0
    
    # Measure of Textual Lexical Diversity (MTLD)
    mtld = calculate_mtld(list(word_counts.keys()), list(word_counts.values()))
    
    return {
        "ttr": ttr,
        "rttr": rttr,
        "mtld": mtld
    }

def calculate_mtld(words, counts, threshold=0.72):
    """Calculate MTLD (simplified implementation)."""
    # This is a simplified version of MTLD
    token_list = []
    for word, count in zip(words, counts):
        token_list.extend([word] * count)
    
    if not token_list:
        return 0.0
    
    factors = []
    current_words = []
    current_types = set()
    
    for token in token_list:
        current_words.append(token)
        current_types.add(token)
        
        ttr = len(current_types) / len(current_words)
        if ttr <= threshold:
            factors.append(len(current_words))
            current_words = []
            current_types = set()
    
    # Handle remaining tokens
    if current_words:
        remaining_ttr = len(current_types) / len(current_words)
        if remaining_ttr > threshold:
            # Estimate how many more tokens would be needed
            needed = (len(current_types) / threshold) - len(current_words)
            factors.append(len(current_words) + needed)
        else:
            factors.append(len(current_words))
    
    if not factors:
        return 0.0
    
    mtld = len(token_list) / np.mean(factors)
    return mtld

def analyze_sentence_lengths(sentence_lengths):
    """Analyze sentence length distribution."""
    if not sentence_lengths:
        return {}
    
    lengths = np.array(sentence_lengths)
    
    return {
        "mean_length": np.mean(lengths),
        "median_length": np.median(lengths),
        "std_length": np.std(lengths),
        "min_length": np.min(lengths),
        "max_length": np.max(lengths),
        "percentile_25": np.percentile(lengths, 25),
        "percentile_75": np.percentile(lengths, 75)
    }

def process_dishu_file(filepath):
    """Process a single Dishu annotation file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None
    
    # Extract words from literal glosses
    word_counts = Counter()
    sentence_lengths = []
    
    # Process units
    units = data.get("units", [])
    for unit in units:
        unit_type = unit.get("unit_type")
        text = unit.get("text", "")
        
        if unit_type == "word":
            # Count individual words
            word_counts[text] += 1
        elif unit_type == "sentence":
            # Count sentence length (number of words)
            # For Dishu, we'll count the number of word units in the sentence
            sentence_lengths.append(len(unit.get("words", [])))
    
    # Process annotations for additional lexical data
    annotations = data.get("annotations", [])
    for ann in annotations:
        if ann.get("task_label_en") == "Literal Gloss":
            gloss = ann.get("value", "")
            if gloss:
                word_counts[gloss] += 1
    
    return word_counts, sentence_lengths

def process_natural_language_file(filepath):
    """Process a natural language text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None
    
    # Simple word tokenization (split on whitespace and punctuation)
    import re
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)
    
    # Simple sentence segmentation (split on .!?)
    sentences = re.split(r'[.!?]+\s*', text)
    sentence_lengths = [len(re.findall(r'\b\w+\b', sentence)) for sentence in sentences if sentence.strip()]
    
    return word_counts, sentence_lengths

def main():
    """Main function to run macro analysis."""
    # Configuration
    data_dirs = {
        "dishu_word": "d:/_College/NLP/Research/清洗后数据/词标注",
        "dishu_sentence": "d:/_College/NLP/Research/清洗后数据/句标注"
    }
    
    results = {}
    
    # Process each data type
    for data_type, dir_path in data_dirs.items():
        if not os.path.exists(dir_path):
            print(f"Directory not found: {dir_path}")
            continue
        
        all_word_counts = Counter()
        all_sentence_lengths = []
        
        # Process all files in directory
        for filename in os.listdir(dir_path):
            if filename.lower().endswith(".txt") and not filename.endswith(".bak"):
                filepath = os.path.join(dir_path, filename)
                
                # Determine file type
                if data_type.startswith("dishu"):
                    word_counts, sentence_lengths = process_dishu_file(filepath)
                else:
                    word_counts, sentence_lengths = process_natural_language_file(filepath)
                
                if word_counts:
                    all_word_counts.update(word_counts)
                if sentence_lengths:
                    all_sentence_lengths.extend(sentence_lengths)
        
        # Calculate metrics
        zipf_results = calculate_zipf_law(all_word_counts)
        entropy_results = calculate_information_entropy(all_word_counts)
        richness_results = calculate_vocabulary_richness(all_word_counts)
        sentence_results = analyze_sentence_lengths(all_sentence_lengths)
        
        # Combine results
        results[data_type] = {
            **zipf_results,
            **entropy_results,
            **richness_results,
            **sentence_results
        }
    
    # Save results to CSV
    results_df = pd.DataFrame.from_dict(results, orient='index')
    results_df.to_csv("d:/_College/NLP/Research/macro_analysis_results.csv", encoding='utf-8-sig')
    print("Macro analysis results saved to macro_analysis_results.csv")
    
    # Print summary
    print("\n=== Macro Analysis Summary ===")
    for data_type, metrics in results.items():
        print(f"\n{data_type}:")
        print(f"  Total words: {metrics['total_words']}")
        print(f"  Unique words: {metrics['unique_words']}")
        print(f"  Zipf's slope: {metrics['zipf_slope']:.3f} (R²: {metrics['zipf_r_squared']:.3f})")
        print(f"  Entropy: {metrics['entropy']:.3f} (normalized: {metrics['normalized_entropy']:.3f})")
        print(f"  TTR: {metrics['ttr']:.3f}, RTTR: {metrics['rttr']:.3f}, MTLD: {metrics['mtld']:.3f}")
        if 'mean_length' in metrics:
            print(f"  Avg sentence length: {metrics['mean_length']:.1f} words")

if __name__ == "__main__":
    main()