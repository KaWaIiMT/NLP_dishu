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
    
    # Load news data
    news_path = os.path.join(data_dir, 'news_samples.json')
    if os.path.exists(news_path):
        with open(news_path, 'r', encoding='utf-8') as f:
            data['news'] = json.load(f)
    
    # Load novel data
    novel_path = os.path.join(data_dir, 'novel_samples.json')
    if os.path.exists(novel_path):
        with open(novel_path, 'r', encoding='utf-8') as f:
            data['novel'] = json.load(f)
    
    # Load Dishu glosses
    dishu_path = os.path.join(data_dir, 'dishu_glosses.json')
    if os.path.exists(dishu_path):
        with open(dishu_path, 'r', encoding='utf-8') as f:
            data['dishu'] = json.load(f)
    
    return data


def run_zero_shot_classification(data, client, num_samples_per_corpus=3):
    """Run zero-shot style classification on the data."""
    results = []
    
    for corpus_name, corpus_data in data.items():
        print(f"\nProcessing {corpus_name} corpus...")
        
        if corpus_name == 'dishu':
            # Dishu is a list of glosses
            combined_text = ' '.join(corpus_data)
            # Take a sample
            sample_text = combined_text[:1000]  # First 1000 chars
            result = client.classify_style(sample_text)
            results.append({
                'corpus': corpus_name,
                'true_style': '地书风格',
                'sample_id': 'combined',
                'predicted_style': result['predicted_style'],
                'confidence': result['confidence'],
                'text_snippet': sample_text[:200],
                **result
            })
            print(f"  Processed: {corpus_name} - Predicted: {result['predicted_style']}")
            
        else:
            # News and novel are dictionaries
            sample_count = 0
            for filename, text in corpus_data.items():
                if sample_count >= num_samples_per_corpus:
                    break
                
                sample_text = text[:1000]  # First 1000 chars
                result = client.classify_style(sample_text)
                
                true_style = '新闻' if corpus_name == 'news' else '小说'
                
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
        
        # Check if prediction matches true style
        if predicted_style == true_style:
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
    data_dir = os.path.join(base_dir, 'task_group_b', 'data')
    results_dir = os.path.join(base_dir, 'task_group_b', 'results')
    
    # Load data
    print("Loading data...")
    data = load_data(data_dir)
    
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
    for corpus, stats in per_corpus_stats.items():
        print(f"  {corpus}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.2%})")
    
    # Print detailed results
    print("\n=== Detailed Results ===")
    for r in results:
        match = "✓" if r['true_style'] == r['predicted_style'] else "✗"
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
