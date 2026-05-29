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


def load_sampled_corpus(base_dir, corpus_name, sample_chars=None):
    """Load corpus from Task 3's sampled data."""
    corpus_dir = os.path.join(base_dir, '任务组A-数据准备', 'Task3-语料库采样', '采样结果', corpus_name)
    if not os.path.exists(corpus_dir):
        print(f"Corpus directory not found: {corpus_dir}")
        return {}
    
    # Load train.txt as the main corpus
    filepath = os.path.join(corpus_dir, 'all.txt')
    if not os.path.exists(filepath):
        filepath = os.path.join(corpus_dir, 'train.txt')
    
    text = load_text_file(filepath, sample_chars)
    if text:
        return {f'{corpus_name}_sample': text}
    
    return {}


def load_dishu_data(base_dir):
    """Load Dishu data from cleaned annotations."""
    dishu_data = {
        'word': {},
        'sentence': {}
    }
    
    # Word annotations
    word_dir = os.path.join(base_dir, '地书实验结果', '清洗后数据', '词标注')
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
    sentence_dir = os.path.join(base_dir, '地书实验结果', '清洗后数据', '句标注')
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
    output_dir = os.path.join(base_dir, '任务组B-LLM应用', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    # Define all corpora to load
    chinese_corpora = [
        ('中文_新闻', 'news'),
        ('中文_小说', 'novel'),
        ('中文_古文', 'classical'),
        ('中文_名著', 'literature')
    ]
    
    multilingual_corpora = [
        '多语言_ara', '多语言_cmn', '多语言_deu', '多语言_eng', 
        '多语言_fas', '多语言_fra', '多语言_heb', '多语言_hin',
        '多语言_ita', '多语言_jpn', '多语言_kor', '多语言_por',
        '多语言_rus', '多语言_spa', '多语言_urd', '多语言_vie'
    ]
    
    all_data = {}
    
    # Load Chinese corpora
    print("=== Loading Chinese Corpora ===")
    for corpus_dir, corpus_name in chinese_corpora:
        print(f"Loading {corpus_name} data...")
        data = load_sampled_corpus(base_dir, corpus_dir, sample_chars=100000)
        if data:
            all_data[corpus_name] = data
            chars = sum(len(text) for text in data.values())
            print(f"  Loaded {chars:,} characters")
    
    # Load multilingual corpora (sample some languages)
    print("\n=== Loading Multilingual Corpora ===")
    selected_multilingual = multilingual_corpora[:8]  # First 8 languages for initial analysis
    for corpus_dir in selected_multilingual:
        lang_code = corpus_dir.split('_')[-1]
        print(f"Loading {lang_code} data...")
        data = load_sampled_corpus(base_dir, corpus_dir, sample_chars=50000)
        if data:
            all_data[lang_code] = data
            chars = sum(len(text) for text in data.values())
            print(f"  Loaded {chars:,} characters")
    
    # Load Dishu data
    print("\n=== Loading Dishu Data ===")
    dishu_data = load_dishu_data(base_dir)
    dishu_glosses = extract_literal_glosses(dishu_data)
    all_data['dishu'] = dishu_glosses
    print(f"Extracted {len(dishu_glosses)} Dishu glosses")
    
    # Save all data
    print(f"\n=== Saving Data to {output_dir} ===")
    for corpus_name, data in all_data.items():
        output_path = os.path.join(output_dir, f'{corpus_name}_samples.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {corpus_name} data")
    
    # Print final stats
    print("\n=== Data Loading Complete ===")
    total_chars = 0
    for corpus_name, data in all_data.items():
        if corpus_name == 'dishu':
            chars = sum(len(g) for g in data)
        else:
            chars = sum(len(text) for text in data.values())
        total_chars += chars
        print(f"{corpus_name}: {chars:,} chars")
    
    print(f"\nTotal: {total_chars:,} characters loaded")


if __name__ == "__main__":
    main()
