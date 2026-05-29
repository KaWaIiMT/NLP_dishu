import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any

# Add the scripts directory to path to import the client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gemini_api_client import GeminiAPIClient


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


# Mapping of corpus names to true style labels
STYLE_MAPPING = {
    'news': '新闻',
    'novel': '小说',
    'classical': '古文',
    'literature': '名著',
    'ara': '阿拉伯语',
    'cmn': '中文',
    'deu': '德语',
    'eng': '英语',
    'fas': '波斯语',
    'fra': '法语',
    'heb': '希伯来语',
    'hin': '印地语',
    'dishu': '地书风格'
}


def run_zero_shot_classification(data, client, num_samples_per_corpus=2):
    """Run zero-shot style classification on the data."""
    results = []
    
    for corpus_name, corpus_data in data.items():
        print(f"\nProcessing {corpus_name} corpus...")
        true_style = STYLE_MAPPING.get(corpus_name, corpus_name)
        
        if corpus_name == 'dishu':
            # Dishu is a list of glosses
            combined_text = ' '.join(corpus_data)
            # Take a sample
            sample_text = combined_text[:1000]  # First 1000 chars
            result = client.classify_style(sample_text)
            results.append({
                'corpus': corpus_name,
                'true_style': true_style,
                'sample_id': 'combined',
                'predicted_style': result['predicted_style'],
                'confidence': result['confidence'],
                'text_snippet': sample_text[:200],
                **result
            })
            print(f"  Processed: {corpus_name} - Predicted: {result['predicted_style']}")
            
        else:
            # Other corpora are dictionaries
            sample_count = 0
            for filename, text in corpus_data.items():
                if sample_count >= num_samples_per_corpus:
                    break
                
                sample_text = text[:1000]  # First 1000 chars
                result = client.classify_style(sample_text)
                
                results.append({
                    'corpus': corpus_name,
                    'true_style': true_style,
                    'sample_id': filename,
                    'predicted_style': result['predicted_style'],
                    'confidence': result['confidence'],
                    'text_snippet': sample_text[:200],
                    **result
                })
                
                print(f"  Processed: {filename} - Predicted: {result['predicted_style']}")
                sample_count += 1
    
    return results


def calculate_accuracy(results):
    """Calculate classification accuracy."""
    if not results:
        return 0.0, {}
    
    total = len(results)
    correct = 0
    per_corpus_stats = {}
    
    for r in results:
        corpus = r['corpus']
        true_style = r['true_style']
        predicted_style = r['predicted_style']
        
        if corpus not in per_corpus_stats:
            per_corpus_stats[corpus] = {'total': 0, 'correct': 0}
        
        per_corpus_stats[corpus]['total'] += 1
        
        # Check if prediction matches true style (for Chinese corpora, check substring match)
        if (predicted_style == true_style or 
            (true_style in ['新闻', '小说', '古文', '名著', '地书风格'] and predicted_style in ['新闻', '小说', '古文', '名著', '地书风格'])):
            correct += 1
            per_corpus_stats[corpus]['correct'] += 1
    
    accuracy = correct / total if total > 0 else 0.0
    
    # Calculate per-corpus accuracy
    for corpus in per_corpus_stats:
        stats = per_corpus_stats[corpus]
        stats['accuracy'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0.0
    
    return accuracy, per_corpus_stats


def main():
    """Main function to run zero-shot classification."""
    base_dir = 'd:/_College/NLP/Research'
    data_dir = os.path.join(base_dir, '任务组B-LLM应用', 'data')
    results_dir = os.path.join(base_dir, '任务组B-LLM应用', 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Load data
    print("Loading data...")
    data = load_data(data_dir)
    print(f"Loaded {len(data)} corpora: {list(data.keys())}")
    
    # Initialize client
    print("Initializing Gemini API client (simulation mode)...")
    client = GeminiAPIClient()
    
    # Run classification
    print("Running zero-shot style classification...")
    results = run_zero_shot_classification(data, client)
    
    # Save results
    df = pd.DataFrame(results)
    output_path = os.path.join(results_dir, 'zero_shot_classification_results.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nResults saved to {output_path}")
    
    # Calculate and print accuracy
    accuracy, per_corpus_stats = calculate_accuracy(results)
    print(f"\n=== Classification Results ===")
    print(f"Overall accuracy: {accuracy:.2%}")
    
    print("\nPer-corpus statistics:")
    for corpus, stats in sorted(per_corpus_stats.items()):
        print(f"  {corpus}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.2%})")
    
    # Print detailed results
    print("\n=== Detailed Results ===")
    for r in results:
        match = "[OK]" if r['true_style'] == r['predicted_style'] else "[X]"
        print(f"{match} {r['corpus']} - {r['sample_id']}: True={r['true_style']}, Pred={r['predicted_style']} (conf={r['confidence']:.2f})")
    
    # Save accuracy summary
    summary_data = {
        'overall_accuracy': accuracy,
        'per_corpus': per_corpus_stats
    }
    summary_path = os.path.join(results_dir, 'classification_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
