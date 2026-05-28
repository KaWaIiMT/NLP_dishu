import json
import os
from collections import Counter, defaultdict
import csv

# 配置路径
WORD_ANNOTATION_DIR = r"d:\_College\NLP\Research\地书实验结果\清洗后数据\词标注"
SENTENCE_ANNOTATION_DIR = r"d:\_College\NLP\Research\地书实验结果\清洗后数据\句标注"
OUTPUT_DIR = r"d:\_College\NLP\Research\任务组A-数据准备\Task2-复合词元生成\生成结果"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_annotations(annotation_dir, output_prefix):
    """处理指定目录下的标注文件并生成复合词元"""
    
    composite_tokens = []  # 存储复合词元
    annotation_stats = defaultdict(Counter)  # 统计信息
    
    file_count = 0
    token_count = 0
    
    for filename in os.listdir(annotation_dir):
        if not filename.endswith('.txt') or filename.endswith('.bak'):
            continue
            
        file_path = os.path.join(annotation_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"无法读取文件 {filename}: {e}")
            continue
            
        file_count += 1
        
        # 提取units和annotations
        units = data.get('units', [])
        annotations = data.get('annotations', [])
        
        # 建立unit_id到unit的映射
        unit_map = {unit['unit_id']: unit for unit in units}
        
        # 按target_id组织annotations
        ann_by_target = defaultdict(list)
        for ann in annotations:
            ann_by_target[ann['target_id']].append(ann)
            
        # 为每个词单元生成复合词元
        for unit in units:
            if unit['unit_type'] != 'word':
                continue
                
            unit_id = unit['unit_id']
            word_text = unit['text']
            
            # 收集该词的所有标注
            anns_for_word = ann_by_target.get(unit_id, [])
            
            # 提取有用的标注信息
            pos_cats = []
            semantic_roles = []
            literal_gloss = []
            semantic_primitives = []
            
            for ann in anns_for_word:
                task_type = ann.get('task_label_en', '')
                value = ann.get('value', [])
                
                if 'POS-like Category' in task_type:
                    if isinstance(value, list):
                        pos_cats.extend(value)
                    elif isinstance(value, str):
                        pos_cats.append(value)
                        
                elif 'Core Semantic Role' in task_type:
                    if isinstance(value, list):
                        semantic_roles.extend(value)
                    elif isinstance(value, str):
                        semantic_roles.append(value)
                        
                elif 'Literal Gloss' in task_type:
                    if isinstance(value, list):
                        literal_gloss.extend(value)
                    elif isinstance(value, str):
                        literal_gloss.append(value)
                        
                elif 'Semantic Primitives' in task_type:
                    if isinstance(value, list):
                        semantic_primitives.extend(value)
                    elif isinstance(value, str):
                        semantic_primitives.append(value)
                        
            # 构建复合词元
            if pos_cats or literal_gloss or semantic_roles:
                token_info = {
                    'original_word': word_text,
                    'unit_id': unit_id,
                    'file': filename,
                    'pos_categories': pos_cats,
                    'semantic_roles': semantic_roles,
                    'literal_gloss': literal_gloss,
                    'semantic_primitives': semantic_primitives
                }
                
                composite_tokens.append(token_info)
                token_count += 1
                
                # 更新统计
                for cat in pos_cats:
                    annotation_stats['pos_categories'][cat] += 1
                for role in semantic_roles:
                    annotation_stats['semantic_roles'][role] += 1
                for gloss in literal_gloss:
                    annotation_stats['literal_gloss'][gloss] += 1
    
    # 保存复合词元结果
    json_output = os.path.join(OUTPUT_DIR, f"{output_prefix}_复合词元.json")
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(composite_tokens, f, ensure_ascii=False, indent=2)
        
    # 保存为文本格式（易读）
    txt_output = os.path.join(OUTPUT_DIR, f"{output_prefix}_复合词元.txt")
    with open(txt_output, 'w', encoding='utf-8') as f:
        for token in composite_tokens:
            f.write(f"词: {token['original_word']}\n")
            f.write(f"文件: {token['file']}\n")
            if token['pos_categories']:
                f.write(f"词性: {', '.join(token['pos_categories'])}\n")
            if token['semantic_roles']:
                f.write(f"语义角色: {', '.join(token['semantic_roles'])}\n")
            if token['literal_gloss']:
                f.write(f"字面翻译: {', '.join(token['literal_gloss'])}\n")
            if token['semantic_primitives']:
                f.write(f"语义基元: {', '.join(token['semantic_primitives'])}\n")
            f.write("---\n")
            
    # 保存统计报告
    stats_output = os.path.join(OUTPUT_DIR, f"{output_prefix}_统计报告.md")
    with open(stats_output, 'w', encoding='utf-8') as f:
        f.write(f"# {output_prefix}复合词元统计报告\n\n")
        f.write(f"- 处理文件数: {file_count}\n")
        f.write(f"- 生成复合词元数: {token_count}\n\n")
        
        f.write("## 词性类别分布 (Top 20)\n")
        for cat, count in annotation_stats['pos_categories'].most_common(20):
            f.write(f"- {cat}: {count}\n")
            
        f.write("\n## 语义角色分布 (Top 20)\n")
        for role, count in annotation_stats['semantic_roles'].most_common(20):
            f.write(f"- {role}: {count}\n")
            
        f.write("\n## 字面翻译分布 (Top 50)\n")
        for gloss, count in annotation_stats['literal_gloss'].most_common(50):
            f.write(f"- {gloss}: {count}\n")
            
    return file_count, token_count, annotation_stats

def main():
    print("=== 开始生成地书-自然语言复合词元 ===\n")
    
    # 处理词标注
    print("1. 处理词标注文件...")
    word_file_count, word_token_count, word_stats = process_annotations(
        WORD_ANNOTATION_DIR, "词标注"
    )
    print(f"   词标注 - 文件: {word_file_count}, 复合词元: {word_token_count}\n")
    
    # 处理句标注
    print("2. 处理句标注文件...")
    sent_file_count, sent_token_count, sent_stats = process_annotations(
        SENTENCE_ANNOTATION_DIR, "句标注"
    )
    print(f"   句标注 - 文件: {sent_file_count}, 复合词元: {sent_token_count}\n")
    
    # 生成总报告
    total_report = os.path.join(OUTPUT_DIR, "总体报告.md")
    with open(total_report, 'w', encoding='utf-8') as f:
        f.write("# 地书-自然语言复合词元生成总体报告\n\n")
        f.write(f"- 词标注: {word_file_count}文件, {word_token_count}词元\n")
        f.write(f"- 句标注: {sent_file_count}文件, {sent_token_count}词元\n")
        f.write(f"- 总计: {word_file_count + sent_file_count}文件, {word_token_count + sent_token_count}词元\n\n")
        f.write("---\n生成时间: 2026-05-29\n")
        
    print(f"=== 完成！结果已保存到 {OUTPUT_DIR} ===")

if __name__ == "__main__":
    main()
