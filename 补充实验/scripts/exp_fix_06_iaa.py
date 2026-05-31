import os
import json
import glob
import sys
from pathlib import Path
from collections import defaultdict, Counter
from scipy.stats import pearsonr, spearmanr

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path("d:/_College/NLP/Research")

def load_annotation_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def cohens_kappa(annotations1, annotations2):
    if len(annotations1) != len(annotations2):
        return None
    
    n = len(annotations1)
    if n == 0:
        return None
    
    agreement = sum(1 for a, b in zip(annotations1, annotations2) if a == b)
    p0 = agreement / n
    
    freq1 = Counter(annotations1)
    freq2 = Counter(annotations2)
    
    pe = sum((freq1[k] / n) * (freq2[k] / n) for k in freq1.keys())
    
    if pe == 1.0:
        return 1.0
    
    return (p0 - pe) / (1 - pe)

def fleiss_kappa(annotations_matrix):
    n = len(annotations_matrix)
    if n == 0:
        return None
    
    k = len(annotations_matrix[0]) if n > 0 else 0
    
    categories = set()
    for row in annotations_matrix:
        categories.update(row)
    
    num_categories = len(categories)
    
    p_j = []
    for category in categories:
        count = sum(row.count(category) for row in annotations_matrix)
        p_j.append(count / (n * k))
    
    P_i = []
    for row in annotations_matrix:
        row_counts = Counter(row)
        p_i = (sum(c * c for c in row_counts.values()) - k) / (k * (k - 1))
        P_i.append(p_i)
    
    P_bar = sum(P_i) / n
    P_e_bar = sum(p * p for p in p_j)
    
    if P_e_bar == 1.0:
        return 1.0
    
    if P_bar == P_e_bar:
        return 0.0
    
    return (P_bar - P_e_bar) / (1 - P_e_bar)

def multi_label_jaccard(label_sets1, label_sets2):
    if len(label_sets1) != len(label_sets2):
        return None
    
    similarities = []
    for set1, set2 in zip(label_sets1, label_sets2):
        s1 = set(set1) if isinstance(set1, list) else set([set1])
        s2 = set(set2) if isinstance(set2, list) else set([set2])
        
        if len(s1) == 0 and len(s2) == 0:
            sim = 1.0
        elif len(s1) == 0 or len(s2) == 0:
            sim = 0.0
        else:
            intersection = len(s1 & s2)
            union = len(s1 | s2)
            sim = intersection / union if union > 0 else 0.0
        
        similarities.append(sim)
    
    return sum(similarities) / len(similarities) if similarities else None

def scale_correlation(scores1, scores2):
    if len(scores1) != len(scores2):
        return None, None
    
    valid_pairs = [(s1, s2) for s1, s2 in zip(scores1, scores2) if s1 is not None and s2 is not None]
    
    if len(valid_pairs) < 2:
        return None, None
    
    s1_vals, s2_vals = zip(*valid_pairs)
    
    try:
        pearson_r, pearson_p = pearsonr(s1_vals, s2_vals)
        spearman_r, spearman_p = spearmanr(s1_vals, s2_vals)
        return pearson_r, spearman_r
    except:
        return None, None

def extract_overlapping_annotations():
    word_files = list(BASE_DIR.glob("素材/*标注数据*/*词标注/*.txt"))
    sentence_files = list(BASE_DIR.glob("素材/*标注数据*/*句标注/*.txt"))
    
    print(f"Found {len(word_files)} word annotation files")
    print(f"Found {len(sentence_files)} sentence annotation files")
    
    all_files = word_files + sentence_files
    print(f"Total annotation files: {len(all_files)}")
    
    target_annotations = defaultdict(lambda: defaultdict(list))
    
    for filepath in all_files:
        data = load_annotation_file(str(filepath))
        if data is None:
            continue
        
        for ann in data.get('annotations', []):
            target_id = ann.get('target_id', '')
            task_id = ann.get('task_id', '')
            value = ann.get('value', '')
            
            if target_id and task_id:
                target_annotations[target_id][task_id].append({
                    'file': filepath.name,
                    'value': value,
                    'updated_at': ann.get('updated_at', '')
                })
    
    overlapping_data = {}
    
    for target_id, task_annotations in target_annotations.items():
        for task_id, annotations in task_annotations.items():
            if len(annotations) >= 2:
                key = (target_id, task_id)
                overlapping_data[key] = annotations
    
    print(f"\nTotal overlapping (target, task) pairs: {len(overlapping_data)}")
    
    task_overlap_counts = Counter()
    for (target_id, task_id), annotations in overlapping_data.items():
        task_overlap_counts[task_id] += 1
    
    print("\n=== Overlap by Task ===")
    for task_id, count in sorted(task_overlap_counts.items(), key=lambda x: -x[1]):
        print(f"  {task_id}: {count} overlapping targets")
    
    return overlapping_data

def analyze_iaa(overlapping_data):
    iaa_results = {}
    
    task_annotations = defaultdict(list)
    
    for (target_id, task_id), annotations in overlapping_data.items():
        values = [ann['value'] for ann in annotations]
        task_annotations[task_id].append(values)
    
    for task_id, all_annotations in task_annotations.items():
        num_targets = len(all_annotations)
        
        if num_targets < 2:
            continue
        
        task_result = {
            'num_targets': num_targets,
            'num_annotators': len(all_annotations[0]) if all_annotations else 0,
            'iaa_metrics': {}
        }
        
        if task_id in ['cognitive_linguistic_metrics', 'syntactic_semantic_fitness', 'annotation_confidence']:
            subitems = {}
            for row in all_annotations:
                for ann in row:
                    if isinstance(ann, dict):
                        for key, val in ann.items():
                            if key not in subitems:
                                subitems[key] = []
                            subitems[key].append(val)
            
            for subitem, values in subitems.items():
                if len(values) >= 2:
                    pearson, spearman = scale_correlation(values[::2], values[1::2])
                    task_result['iaa_metrics'][subitem] = {
                        'pearson_r': pearson,
                        'spearman_r': spearman
                    }
        
        elif task_id in ['pos_like_category', 'morphological_features', 'semantic_primitives', 
                        'visual_cues', 'communication_functions', 'ambiguity_sources']:
            jaccard_scores = []
            for annotations in all_annotations:
                if len(annotations) >= 2:
                    jaccard = multi_label_jaccard([annotations[0]], [annotations[1]])
                    if jaccard is not None:
                        jaccard_scores.append(jaccard)
            
            if jaccard_scores:
                avg_jaccard = sum(jaccard_scores) / len(jaccard_scores)
                task_result['iaa_metrics']['avg_jaccard'] = avg_jaccard
        
        elif task_id in ['semantic_role_core', 'dependency_head_relation', 'discourse_relation',
                        'speech_act_primary', 'reference_type']:
            flat_annotations = []
            for annotations in all_annotations:
                flat_annotations.append([str(a) for a in annotations])
            
            if len(flat_annotations) >= 2 and len(flat_annotations[0]) >= 2:
                kappa = cohens_kappa([a[0] for a in flat_annotations], 
                                    [a[1] for a in flat_annotations])
                task_result['iaa_metrics']['cohens_kappa'] = kappa
                
                fleiss_result = fleiss_kappa(flat_annotations)
                task_result['iaa_metrics']['fleiss_kappa'] = fleiss_result
        
        elif task_id == 'literal_gloss':
            flat_annotations = []
            for annotations in all_annotations:
                flat_annotations.append([str(a).strip() for a in annotations])
            
            if len(flat_annotations) >= 2 and len(flat_annotations[0]) >= 2:
                kappa = cohens_kappa([a[0] for a in flat_annotations], 
                                    [a[1] for a in flat_annotations])
                task_result['iaa_metrics']['cohens_kappa'] = kappa
                
                fleiss_result = fleiss_kappa(flat_annotations)
                task_result['iaa_metrics']['fleiss_kappa'] = fleiss_result
        
        elif task_id in ['free_translation', 'pragmatic_meaning', 'event_description', 
                        'context_note']:
            jaccard_scores = []
            for annotations in all_annotations:
                if len(annotations) >= 2:
                    s1 = set(str(annotations[0]).split()) if annotations[0] else set()
                    s2 = set(str(annotations[1]).split()) if annotations[1] else set()
                    if len(s1) == 0 and len(s2) == 0:
                        jaccard = 1.0
                    elif len(s1) == 0 or len(s2) == 0:
                        jaccard = 0.0
                    else:
                        jaccard = len(s1 & s2) / len(s1 | s2)
                    jaccard_scores.append(jaccard)
            
            if jaccard_scores:
                avg_jaccard = sum(jaccard_scores) / len(jaccard_scores)
                task_result['iaa_metrics']['avg_jaccard'] = avg_jaccard
        
        elif task_id in ['wsd_candidates', 'possible_translations', 'collocational_associations',
                        'crosslinguistic_equivalents']:
            jaccard_scores = []
            for annotations in all_annotations:
                if len(annotations) >= 2:
                    s1 = set(annotations[0]) if isinstance(annotations[0], list) else set([annotations[0]])
                    s2 = set(annotations[1]) if isinstance(annotations[1], list) else set([annotations[1]])
                    if len(s1) == 0 and len(s2) == 0:
                        jaccard = 1.0
                    elif len(s1) == 0 or len(s2) == 0:
                        jaccard = 0.0
                    else:
                        jaccard = len(s1 & s2) / len(s1 | s2)
                    jaccard_scores.append(jaccard)
            
            if jaccard_scores:
                avg_jaccard = sum(jaccard_scores) / len(jaccard_scores)
                task_result['iaa_metrics']['avg_jaccard'] = avg_jaccard
        
        elif task_id == 'frame_or_metaphor_mapping':
            exact_matches = 0
            total = 0
            for annotations in all_annotations:
                if len(annotations) >= 2:
                    total += 1
                    if annotations[0] == annotations[1]:
                        exact_matches += 1
            
            if total > 0:
                task_result['iaa_metrics']['agreement_rate'] = exact_matches / total
        
        iaa_results[task_id] = task_result
    
    return iaa_results

def generate_heatmap_data(overlapping_data, iaa_results):
    semantic_types = {
        'entity': ['reference_type', 'semantic_role_core'],
        'morphology': ['morphological_features', 'pos_like_category'],
        'pragmatics': ['pragmatic_meaning', 'speech_act_primary', 'discourse_relation'],
        'cognitive': ['cognitive_linguistic_metrics', 'annotation_confidence'],
        'visual': ['visual_cues'],
        'translation': ['literal_gloss', 'free_translation']
    }
    
    heatmap_data = {
        'matrix': [],
        'row_labels': [],
        'col_labels': [],
        'summary': {}
    }
    
    for semantic_type, tasks in semantic_types.items():
        type_results = []
        for task in tasks:
            if task in iaa_results:
                metrics = iaa_results[task]['iaa_metrics']
                if 'cohens_kappa' in metrics:
                    type_results.append(metrics['cohens_kappa'])
                elif 'fleiss_kappa' in metrics:
                    type_results.append(metrics['fleiss_kappa'])
                elif 'avg_jaccard' in metrics:
                    type_results.append(metrics['avg_jaccard'])
                elif 'pearson_r' in metrics:
                    avg_r = sum(v.get('pearson_r', 0) for v in metrics.values()) / len(metrics)
                    type_results.append(avg_r)
        
        if type_results:
            heatmap_data['summary'][semantic_type] = {
                'mean': sum(type_results) / len(type_results),
                'min': min(type_results),
                'max': max(type_results),
                'count': len(type_results)
            }
    
    heatmap_data['row_labels'] = list(semantic_types.keys())
    heatmap_data['col_labels'] = ['mean_iaa', 'min_iaa', 'max_iaa']
    
    for semantic_type in semantic_types.keys():
        if semantic_type in heatmap_data['summary']:
            summary = heatmap_data['summary'][semantic_type]
            heatmap_data['matrix'].append([summary['mean'], summary['min'], summary['max']])
    
    return heatmap_data

def main():
    print("=== D6 Inter-Annotator Agreement Analysis ===")
    print("Loading overlapping annotations...")
    
    overlapping_data = extract_overlapping_annotations()
    
    print("\n=== Analyzing Inter-Annotator Agreement ===")
    iaa_results = analyze_iaa(overlapping_data)
    
    print("\n=== IAA Results by Task ===")
    for task_id, result in sorted(iaa_results.items()):
        print(f"\n{task_id}:")
        print(f"  Targets: {result['num_targets']}")
        print(f"  Annotators: {result['num_annotators']}")
        for metric, value in result['iaa_metrics'].items():
            if isinstance(value, dict):
                for submetric, subval in value.items():
                    print(f"    {metric}.{submetric}: {subval:.4f}" if isinstance(subval, float) else f"    {metric}.{submetric}: {subval}")
            else:
                print(f"    {metric}: {value:.4f}" if isinstance(value, float) else f"    {metric}: {value}")
    
    print("\n=== Generating Heatmap Data ===")
    heatmap_data = generate_heatmap_data(overlapping_data, iaa_results)
    
    print("\n=== Semantic Type IAA Summary ===")
    for semantic_type, summary in heatmap_data['summary'].items():
        print(f"{semantic_type}: mean={summary['mean']:.4f}, min={summary['min']:.4f}, max={summary['max']:.4f}")
    
    output_dir = BASE_DIR / "补充实验" / "results"
    os.makedirs(output_dir, exist_ok=True)
    
    iaa_output_path = output_dir / "iaa_results.json"
    with open(iaa_output_path, 'w', encoding='utf-8') as f:
        json.dump(iaa_results, f, ensure_ascii=False, indent=2)
    print(f"\nIAA results saved to: {iaa_output_path}")
    
    heatmap_output_path = output_dir / "iaa_heatmap_data.json"
    with open(heatmap_output_path, 'w', encoding='utf-8') as f:
        json.dump(heatmap_data, f, ensure_ascii=False, indent=2)
    print(f"Heatmap data saved to: {heatmap_output_path}")
    
    literal_gloss_iaa = None
    if 'literal_gloss' in iaa_results:
        metrics = iaa_results['literal_gloss']['iaa_metrics']
        if 'cohens_kappa' in metrics:
            literal_gloss_iaa = metrics['cohens_kappa']
        elif 'fleiss_kappa' in metrics:
            literal_gloss_iaa = metrics['fleiss_kappa']
    
    print(f"\n=== Summary ===")
    print(f"Total overlapping pairs analyzed: {len(overlapping_data)}")
    print(f"Tasks with IAA computed: {len(iaa_results)}")
    if literal_gloss_iaa is not None:
        print(f"literal_gloss Cohen's κ: {literal_gloss_iaa:.4f}")
    
    return {
        'iaa_results': iaa_results,
        'heatmap_data': heatmap_data,
        'literal_gloss_iaa': literal_gloss_iaa
    }

if __name__ == "__main__":
    main()