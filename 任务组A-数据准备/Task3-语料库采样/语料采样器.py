import os
import random
import json
from collections import defaultdict

# 配置路径
BASE_DIR = r"d:\_College\NLP\Research"
SOURCE_DATA_DIR = os.path.join(BASE_DIR, "素材")
DISHU_DATA_DIR = os.path.join(BASE_DIR, "地书实验结果", "清洗后数据")
OUTPUT_DIR = os.path.join(BASE_DIR, "任务组A-数据准备", "Task3-语料库采样", "采样结果")

# 采样配置
SAMPLE_SIZE_PER_CATEGORY = 10000  # 每类采样1万句
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# 设置随机种子保证可复现
random.seed(42)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def sample_sentences_from_text(file_path, max_sentences):
    """从文本文件中采样句子（按行分割）"""
    sentences = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    sentences.append(line)
                    if len(sentences) >= max_sentences * 2:  # 多取一些再随机采样
                        break
    except UnicodeDecodeError:
        # 尝试GBK编码
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        sentences.append(line)
                        if len(sentences) >= max_sentences * 2:
                            break
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")
            return []
    
    # 随机采样
    if len(sentences) > max_sentences:
        sentences = random.sample(sentences, max_sentences)
    return sentences

def process_directory(dir_path, max_sentences_per_file=1000, recursive=True):
    """处理目录下的所有文本文件"""
    all_sentences = []
    
    if not os.path.exists(dir_path):
        print(f"目录不存在: {dir_path}")
        return all_sentences
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.txt') and not file.endswith('.bak'):
                file_path = os.path.join(root, file)
                sentences = sample_sentences_from_text(file_path, max_sentences_per_file)
                all_sentences.extend(sentences)
                if len(all_sentences) >= SAMPLE_SIZE_PER_CATEGORY:
                    break
        if len(all_sentences) >= SAMPLE_SIZE_PER_CATEGORY:
            break
            
    # 总体采样
    if len(all_sentences) > SAMPLE_SIZE_PER_CATEGORY:
        all_sentences = random.sample(all_sentences, SAMPLE_SIZE_PER_CATEGORY)
    return all_sentences

def extract_dishu_sentences():
    """从地书标注数据中提取句子"""
    sentences = []
    word_dir = os.path.join(DISHU_DATA_DIR, "词标注")
    sentence_dir = os.path.join(DISHU_DATA_DIR, "句标注")
    
    for data_dir in [word_dir, sentence_dir]:
        if not os.path.exists(data_dir):
            continue
            
        for filename in os.listdir(data_dir):
            if not filename.endswith('.txt') or filename.endswith('.bak'):
                continue
                
            file_path = os.path.join(data_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                source_text = data.get('source_text', {})
                raw_text = source_text.get('raw_text', '')
                if raw_text:
                    # 简单按换行符分割
                    for line in raw_text.split('\n'):
                        line = line.strip()
                        if line:
                            sentences.append(line)
                            
            except Exception as e:
                print(f"处理地书文件 {filename} 时出错: {e}")
    
    # 采样
    if len(sentences) > SAMPLE_SIZE_PER_CATEGORY:
        sentences = random.sample(sentences, SAMPLE_SIZE_PER_CATEGORY)
    return sentences

def split_dataset(sentences):
    """将数据集划分为训练/验证/测试集"""
    random.shuffle(sentences)
    
    n_total = len(sentences)
    n_train = int(n_total * TRAIN_RATIO)
    n_val = int(n_total * VAL_RATIO)
    
    train = sentences[:n_train]
    val = sentences[n_train:n_train + n_val]
    test = sentences[n_train + n_val:]
    
    return train, val, test

def save_dataset(output_dir, name, sentences):
    """保存数据集"""
    train, val, test = split_dataset(sentences)
    
    data_dir = os.path.join(output_dir, name)
    os.makedirs(data_dir, exist_ok=True)
    
    with open(os.path.join(data_dir, 'train.txt'), 'w', encoding='utf-8') as f:
        for s in train:
            f.write(s + '\n')
            
    with open(os.path.join(data_dir, 'val.txt'), 'w', encoding='utf-8') as f:
        for s in val:
            f.write(s + '\n')
            
    with open(os.path.join(data_dir, 'test.txt'), 'w', encoding='utf-8') as f:
        for s in test:
            f.write(s + '\n')
            
    # 保存全部
    with open(os.path.join(data_dir, 'all.txt'), 'w', encoding='utf-8') as f:
        for s in sentences:
            f.write(s + '\n')
            
    return {
        'name': name,
        'total': len(sentences),
        'train': len(train),
        'val': len(val),
        'test': len(test)
    }

def main():
    print("=== 开始语料库采样与划分 ===\n")
    
    stats = []
    
    # 1. 地书数据
    print("1. 处理地书数据...")
    dishu_sentences = extract_dishu_sentences()
    if dishu_sentences:
        stat = save_dataset(OUTPUT_DIR, "地书", dishu_sentences)
        stats.append(stat)
        print(f"   地书: {stat['total']} 句\n")
    
    # 2. THUcNews新闻
    print("2. 处理中文新闻语料...")
    news_dir = os.path.join(SOURCE_DATA_DIR, "THUcNews")
    news_sentences = process_directory(news_dir, max_sentences_per_file=5000)
    if news_sentences:
        stat = save_dataset(OUTPUT_DIR, "中文_新闻", news_sentences)
        stats.append(stat)
        print(f"   中文新闻: {stat['total']} 句\n")
    
    # 3. 世界名著
    print("3. 处理世界名著语料...")
    classic_dir = os.path.join(SOURCE_DATA_DIR, "世界名著")
    classic_sentences = process_directory(classic_dir, max_sentences_per_file=2000)
    if classic_sentences:
        stat = save_dataset(OUTPUT_DIR, "中文_名著", classic_sentences)
        stats.append(stat)
        print(f"   中文名著: {stat['total']} 句\n")
    
    # 4. 四库全书
    print("4. 处理四库全书语料...")
    ancient_dir = os.path.join(SOURCE_DATA_DIR, "四库全书数据库")
    ancient_sentences = process_directory(ancient_dir, max_sentences_per_file=1000)
    if ancient_sentences:
        stat = save_dataset(OUTPUT_DIR, "中文_古文", ancient_sentences)
        stats.append(stat)
        print(f"   中文古文: {stat['total']} 句\n")
    
    # 5. 小说
    print("5. 处理小说语料...")
    novel_dir = os.path.join(SOURCE_DATA_DIR, "小说")
    novel_sentences = process_directory(novel_dir, max_sentences_per_file=500)
    if novel_sentences:
        stat = save_dataset(OUTPUT_DIR, "中文_小说", novel_sentences)
        stats.append(stat)
        print(f"   中文小说: {stat['total']} 句\n")
    
    # 6. 多语言Wiki
    print("6. 处理多语言Wiki语料...")
    wiki_dir = os.path.join(SOURCE_DATA_DIR, "WikiSentences30k_16Lans")
    if os.path.exists(wiki_dir):
        for file in os.listdir(wiki_dir):
            if file.endswith('.txt'):
                lang_name = file.split('_')[0] if '_' in file else file[:-4]
                file_path = os.path.join(wiki_dir, file)
                sentences = sample_sentences_from_text(file_path, SAMPLE_SIZE_PER_CATEGORY)
                if sentences:
                    stat = save_dataset(OUTPUT_DIR, f"多语言_{lang_name}", sentences)
                    stats.append(stat)
                    print(f"   {lang_name}: {stat['total']} 句")
        print()
    
    # 生成报告
    report_path = os.path.join(OUTPUT_DIR, "总体报告.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 语料库采样总体报告\n\n")
        f.write(f"- 采样时间: 2026-05-29\n")
        f.write(f"- 每类采样目标: {SAMPLE_SIZE_PER_CATEGORY} 句\n")
        f.write(f"- 划分比例: 训练 {TRAIN_RATIO*100:.0f}%, 验证 {VAL_RATIO*100:.0f}%, 测试 {TEST_RATIO*100:.0f}%\n\n")
        
        f.write("## 语料统计\n\n")
        f.write("| 语料类型 | 总句子数 | 训练集 | 验证集 | 测试集 |\n")
        f.write("|----------|----------|--------|--------|--------|\n")
        for s in stats:
            f.write(f"| {s['name']} | {s['total']} | {s['train']} | {s['val']} | {s['test']} |\n")
    
    print(f"=== 完成！结果已保存到 {OUTPUT_DIR} ===")

if __name__ == "__main__":
    main()
