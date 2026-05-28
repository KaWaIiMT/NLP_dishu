import os
import json
import pandas as pd
from collections import Counter, defaultdict

def analyze_semantic_roles(filepath):
    """Analyze semantic roles from annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    semantic_roles = []
    for ann in data.get("annotations", []):
        if ann.get("task_label_en") == "Core Semantic Role":
            role = ann.get("value", "")
            if role:
                semantic_roles.append(role)
    
    return semantic_roles

def analyze_discourse_relations(filepath):
    """Analyze discourse relations from annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    discourse_relations = []
    for ann in data.get("annotations", []):
        if ann.get("task_label_en") == "Discourse Relation":
            relation = ann.get("value", "")
            if relation:
                discourse_relations.append(relation)
    
    return discourse_relations

def analyze_pos_categories(filepath):
    """Analyze POS-like categories from annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    pos_categories = []
    for ann in data.get("annotations", []):
        if ann.get("task_label_en") == "POS-like Category":
            categories = ann.get("value", [])
            if isinstance(categories, list):
                pos_categories.extend(categories)
    
    return pos_categories

def analyze_pragmatic_meaning(filepath):
    """Analyze pragmatic meaning annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    pragmatic_meanings = []
    for ann in data.get("annotations", []):
        if ann.get("task_label_en") == "Pragmatic Meaning":
            meaning = ann.get("value", "")
            if meaning:
                pragmatic_meanings.append(meaning)
    
    return pragmatic_meanings

def analyze_literal_gloss(filepath):
    """Analyze literal gloss annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    glosses = []
    for ann in data.get("annotations", []):
        if ann.get("task_label_en") == "Literal Gloss":
            gloss = ann.get("value", "")
            if gloss:
                glosses.append(gloss)
    
    return glosses

def analyze_speech_acts(filepath):
    """Analyze speech act annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    speech_acts = []
    for ann in data.get("annotations", []):
        if ann.get("task_label_en") == "Primary Speech Act":
            act = ann.get("value", "")
            if act:
                speech_acts.append(act)
    
    return speech_acts

def analyze_ambiguity_sources(filepath):
    """Analyze ambiguity source annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
    
    ambiguity_sources = []
    for ann in data.get("annotations", []):
        if ann.get("task_label_en") == "Sources of Ambiguity":
            sources = ann.get("value", [])
            if isinstance(sources, list):
                ambiguity_sources.extend(sources)
    
    return ambiguity_sources

def main():
    """Main function to run micro analysis."""
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
        
        all_semantic_roles = []
        all_discourse_relations = []
        all_pos_categories = []
        all_pragmatic_meanings = []
        all_literal_glosses = []
        all_speech_acts = []
        all_ambiguity_sources = []
        
        # Process all files in directory
        for filename in os.listdir(dir_path):
            if filename.lower().endswith(".txt") and not filename.endswith(".bak"):
                filepath = os.path.join(dir_path, filename)
                
                # Analyze different annotation types
                semantic_roles = analyze_semantic_roles(filepath)
                if semantic_roles:
                    all_semantic_roles.extend(semantic_roles)
                
                discourse_relations = analyze_discourse_relations(filepath)
                if discourse_relations:
                    all_discourse_relations.extend(discourse_relations)
                
                pos_categories = analyze_pos_categories(filepath)
                if pos_categories:
                    all_pos_categories.extend(pos_categories)
                
                pragmatic_meanings = analyze_pragmatic_meaning(filepath)
                if pragmatic_meanings:
                    all_pragmatic_meanings.extend(pragmatic_meanings)
                
                literal_glosses = analyze_literal_gloss(filepath)
                if literal_glosses:
                    all_literal_glosses.extend(literal_glosses)
                
                speech_acts = analyze_speech_acts(filepath)
                if speech_acts:
                    all_speech_acts.extend(speech_acts)
                
                ambiguity_sources = analyze_ambiguity_sources(filepath)
                if ambiguity_sources:
                    all_ambiguity_sources.extend(ambiguity_sources)
        
        # Count frequencies
        results[data_type] = {
            "semantic_roles": Counter(all_semantic_roles),
            "discourse_relations": Counter(all_discourse_relations),
            "pos_categories": Counter(all_pos_categories),
            "speech_acts": Counter(all_speech_acts),
            "ambiguity_sources": Counter(all_ambiguity_sources),
            "pragmatic_meanings_count": len(all_pragmatic_meanings),
            "literal_glosses_count": len(all_literal_glosses)
        }
    
    # Save results to CSV (convert Counters to dictionaries for easier handling)
    for data_type, data in results.items():
        for metric in ["semantic_roles", "discourse_relations", "pos_categories", 
                    "speech_acts", "ambiguity_sources"]:
            df = pd.DataFrame.from_dict(data[metric], orient='index', columns=['count'])
            df.index.name = 'category'
            df.sort_values('count', ascending=False, inplace=True)
            df.to_csv(f"d:/_College/NLP/Research/{data_type}_{metric}_results.csv", 
                    encoding='utf-8-sig')
    
    # Print summary
    print("\n=== Micro Analysis Summary ===")
    for data_type, metrics in results.items():
        print(f"\n{data_type}:")
        
        if metrics["semantic_roles"]:
            print(f"  Top 5 semantic roles: {metrics['semantic_roles'].most_common(5)}")
        
        if metrics["discourse_relations"]:
            print(f"  Top 5 discourse relations: {metrics['discourse_relations'].most_common(5)}")
        
        if metrics["pos_categories"]:
            print(f"  Top 5 POS categories: {metrics['pos_categories'].most_common(5)}")
        
        if metrics["speech_acts"]:
            print(f"  Top 5 speech acts: {metrics['speech_acts'].most_common(5)}")
        
        if metrics["ambiguity_sources"]:
            print(f"  Top 5 ambiguity sources: {metrics['ambiguity_sources'].most_common(5)}")
        
        print(f"  Pragmatic meaning annotations: {metrics['pragmatic_meanings_count']}")
        print(f"  Literal gloss annotations: {metrics['literal_glosses_count']}")
    
    print("\nDetailed results saved to CSV files.")

if __name__ == "__main__":
    main()