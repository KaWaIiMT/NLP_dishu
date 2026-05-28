import os
import re
import json
import random
from collections import Counter, defaultdict


def load_text_file(filepath, sample_size=None):
    """Load and sample text from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='gbk') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
    
    # Clean text
    text = re.sub(r'\s+', ' ', text).strip()
    
    if sample_size and len(text) > sample_size:
        # Randomly sample a portion
        start = random.randint(0, len(text) - sample_size)
        text = text[start:start + sample_size]
    
    return text


def split_to_sentences(text):
    """Split text into sentences."""
    sentences = re.split(r'[。！？.!?]+\s*', text)
    return [s.strip() for s in sentences if s.strip()]


def split_to_words(text):
    """Simple Chinese word segmentation (split by whitespace and punctuation)."""
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    words = re.split(r'\s+', text)
    return [w for w in words if w]


def load_news_data(base_dir, num_files=5, sample_chars_per_file=10000):
    """Load news data from THUcNews."""
    news_dir = os.path.join(base_dir, '素材', 'THUcNews')
    if not os.path.exists(news_dir):
        print(f"News directory not found: {news_dir}")
        return {}
    
    news_data = {}
    files = [f for f in os.listdir(news_dir) if f.endswith('.txt')]
    
    if not files:
        print("No news files found")
        return {}
    
    # Take first N files
    selected_files = files[:num_files]
    
    for filename in selected_files:
        filepath = os.path.join(news_dir, filename)
        text = load_text_file(filepath, sample_chars_per_file)
        if text:
            news_data[filename] = text
    
    return news_data


def load_novel_data(base_dir, num_files=10, sample_chars_per_file=50000):
    """Load novel data."""
    novel_dir = os.path.join(base_dir, '素材', '小说', '小说')
    if not os.path.exists(novel_dir):
        print(f"Novel directory not found: {novel_dir}")
        return {}
    
    novel_data = {}
    files = [f for f in os.listdir(novel_dir) if f.endswith('.txt')]
    
    if not files:
        print("No novel files found")
        return {}
    
    # Randomly select files
    selected_files = random.sample(files, min(num_files, len(files)))
    
    for filename in selected_files:
        filepath = os.path.join(novel_dir, filename)
        text = load_text_file(filepath, sample_chars_per_file)
        if text:
            novel_data[filename] = text
    
    return novel_data


def load_dishu_data(base_dir):
    """Load Dishu data from cleaned annotations."""
    dishu_data = {
        'word': {},
        'sentence': {}
    }
    
    # Word annotations
    word_dir = os.path.join(base_dir, '清洗后数据', '词标注')
    if os.path.exists(word_dir):
        for filename in os.listdir(word_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(word_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    dishu_data['word'][filename] = data
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    
    # Sentence annotations
    sentence_dir = os.path.join(base_dir, '清洗后数据', '句标注')
    if os.path.exists(sentence_dir):
        for filename in os.listdir(sentence_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(sentence_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    dishu_data['sentence'][filename] = data
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    
    return dishu_data


def extract_literal_glosses(dishu_data):
    """Extract literal glosses from Dishu data."""
    glosses = []
    
    # From word annotations
    for filename, data in dishu_data.get('word', {}).items():
        annotations = data.get('annotations', [])
        for ann in annotations:
            if ann.get('task_label_en') == 'Literal Gloss':
                gloss = ann.get('value', '')
                if gloss:
                    glosses.append(gloss)
    
    # From sentence annotations
    for filename, data in dishu_data.get('sentence', {}).items():
        annotations = data.get('annotations', [])
        for ann in annotations:
            if ann.get('task_label_en') == 'Free Translation':
                gloss = ann.get('value', '')
                if gloss:
                    glosses.append(gloss)
            elif ann.get('task_label_en') == 'Literal Gloss':
                gloss = ann.get('value', '')
                if gloss:
                    glosses.append(gloss)
    
    return glosses


def main():
    """Main function to load all data."""
    base_dir = 'd:/_College/NLP/Research'
    
    print("Loading news data...")
    news_data = load_news_data(base_dir)
    print(f"Loaded {len(news_data)} news files")
    
    print("\nLoading novel data...")
    novel_data = load_novel_data(base_dir)
    print(f"Loaded {len(novel_data)} novel files")
    
    print("\nLoading Dishu data...")
    dishu_data = load_dishu_data(base_dir)
    print(f"Loaded {len(dishu_data['word'])} word annotations, {len(dishu_data['sentence'])} sentence annotations")
    
    # Extract Dishu glosses
    dishu_glosses = extract_literal_glosses(dishu_data)
    print(f"Extracted {len(dishu_glosses)} Dishu glosses/translations")
    
    # Save sampled data
    output_dir = os.path.join(base_dir, 'task_group_b', 'data')
    
    # Save news data
    if news_data:
        with open(os.path.join(output_dir, 'news_samples.json'), 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    # Save novel data
    if novel_data:
        with open(os.path.join(output_dir, 'novel_samples.json'), 'w', encoding='utf-8') as f:
            json.dump(novel_data, f, ensure_ascii=False, indent=2)
    
    # Save Dishu glosses
    if dishu_glosses:
        with open(os.path.join(output_dir, 'dishu_glosses.json'), 'w', encoding='utf-8') as f:
            json.dump(dishu_glosses, f, ensure_ascii=False, indent=2)
    
    print(f"\nData saved to {output_dir}")
    
    # Print some stats
    print("\n=== Data Statistics ===")
    
    if news_data:
        news_chars = sum(len(text) for text in news_data.values())
        print(f"News: {news_chars:,} characters total")
    
    if novel_data:
        novel_chars = sum(len(text) for text in novel_data.values())
        print(f"Novels: {novel_chars:,} characters total")
    
    if dishu_glosses:
        dishu_chars = sum(len(g) for g in dishu_glosses)
        print(f"Dishu glosses: {dishu_chars:,} characters total")


if __name__ == "__main__":
    main()
