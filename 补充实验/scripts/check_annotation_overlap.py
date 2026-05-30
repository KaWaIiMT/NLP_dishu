import os
import json
from collections import defaultdict, Counter
import glob
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path("d:/_College/NLP/Research")

def load_annotation_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return None

def check_annotation_overlap(output_path):
    word_files = list(BASE_DIR.glob("素材/*标注数据*/*词标注/*.txt"))
    sentence_files = list(BASE_DIR.glob("素材/*标注数据*/*句标注/*.txt"))
    
    print(f"Found {len(word_files)} word annotation files")
    print(f"Found {len(sentence_files)} sentence annotation files")
    
    target_annotations = defaultdict(list)
    
    all_files = word_files + sentence_files
    
    for filepath in all_files:
        data = load_annotation_file(str(filepath))
        if data is None:
            continue
        
        for ann in data.get('annotations', []):
            target_id = ann.get('target_id', '')
            task_id = ann.get('task_id', '')
            if target_id and task_id:
                key = (target_id, task_id)
                target_annotations[key].append({
                    'file': filepath.name,
                    'value': ann.get('value', ''),
                    'updated_at': ann.get('updated_at', '')
                })
    
    overlapping_targets = {}
    single_annotations = {}
    
    for (target_id, task_id), annotations in target_annotations.items():
        if len(annotations) > 1:
            overlapping_targets[(target_id, task_id)] = annotations
        else:
            single_annotations[(target_id, task_id)] = annotations[0] if annotations else None
    
    print(f"\n=== Annotation Overlap Statistics ===")
    print(f"Total unique (target, task) pairs: {len(target_annotations)}")
    print(f"Overlapping pairs (>1 annotator): {len(overlapping_targets)}")
    print(f"Single-annotated pairs: {len(single_annotations)}")
    
    if overlapping_targets:
        overlap_rate = len(overlapping_targets) / len(target_annotations) * 100
        print(f"Overlap rate: {overlap_rate:.2f}%")
        
        task_overlap = defaultdict(list)
        for (target_id, task_id), annotations in overlapping_targets.items():
            task_overlap[task_id].append({
                'target_id': target_id,
                'annotations': annotations
            })
        
        print(f"\n=== Overlap by Task ===")
        for task_id, overlaps in sorted(task_overlap.items()):
            print(f"  {task_id}: {len(overlaps)} overlapping targets")
    else:
        overlap_rate = 0
    
    result = {
        'total_pairs': len(target_annotations),
        'overlapping_pairs': len(overlapping_targets),
        'single_annotated': len(single_annotations),
        'overlap_rate': overlap_rate,
        'sample_overlaps': {
            f"{k[0]}_{k[1]}": v 
            for k, v in list(overlapping_targets.items())[:10]
        } if overlapping_targets else {}
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    return result

if __name__ == "__main__":
    output_path = str(BASE_DIR / "补充实验" / "results" / "annotation_overlap_check.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    result = check_annotation_overlap(output_path)
    
    if result['overlap_rate'] > 0:
        print(f"\n✓ Data has annotation overlap - can proceed with inter-annotator agreement analysis")
    else:
        print(f"\n✗ No annotation overlap found - cannot compute inter-annotator agreement")
        print("Note: Each annotator may have annotated different targets, not the same targets")
