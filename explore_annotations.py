import json
import os

# 读取一个标注文件
file_path = r"d:\_College\NLP\Research\地书实验结果\清洗后数据\词标注\967207936846.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 打印文件的顶层键
print("顶层键:", list(data.keys()))

# 检查是否有annotations
if 'annotations' in data:
    print(f"\n找到 {len(data['annotations'])} 个标注：")
    for i, ann in enumerate(data['annotations'][:5]):  # 只看前5个
        print(f"\n标注 {i+1}:")
        print(list(ann.keys()))
        if 'task_label_en' in ann:
            print(f"任务类型: {ann['task_label_en']}")
        if 'value' in ann:
            print(f"值类型: {type(ann['value'])}")
            if isinstance(ann['value'], list):
                print(f"列表长度: {len(ann['value'])}")
else:
    print("\n没有找到annotations键")

# 检查是否有其他可能的键
print("\n所有顶层键:")
for key in data.keys():
    value = data[key]
    if isinstance(value, list):
        print(f"  {key}: list, 长度 {len(value)}")
    elif isinstance(value, dict):
        print(f"  {key}: dict, 键: {list(value.keys())}")
    else:
        print(f"  {key}: {type(value)}")
