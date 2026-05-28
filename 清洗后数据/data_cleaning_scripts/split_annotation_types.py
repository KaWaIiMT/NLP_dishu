import os
import json
import shutil

def classify_annotation_file(filepath, word_dir, sentence_dir):
    """Classify a single annotation file as word or sentence annotation."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return None, "Empty file"
                
            data = json.loads(content)
    except Exception as e:
        return None, f"Error reading file: {e}"
    
    # --- Determine annotation type --- 
    # Check based on task types
    student = data.get("student", {})
    word_task_type = student.get("word_task_type")
    sentence_task_type = student.get("sentence_task_type")
    
    # Check based on units
    units = data.get("units", [])
    has_word_units = any(unit.get("unit_type") == "word" for unit in units)
    has_sentence_units = any(unit.get("unit_type") == "sentence" for unit in units)
    
    # Check based on annotations
    annotations = data.get("annotations", [])
    has_word_annotations = any(ann.get("target_type") == "word" for ann in annotations)
    has_sentence_annotations = any(ann.get("target_type") == "sentence" for ann in annotations)
    
    # Classification logic
    if word_task_type and not sentence_task_type:
        return "word", f"Word annotation task: {word_task_type}"
    elif sentence_task_type and not word_task_type:
        return "sentence", f"Sentence annotation task: {sentence_task_type}"
    elif has_word_units and not has_sentence_units:
        return "word", "Contains only word units"
    elif has_sentence_units and not has_word_units:
        return "sentence", "Contains only sentence units"
    elif has_word_annotations and not has_sentence_annotations:
        return "word", "Contains only word annotations"
    elif has_sentence_annotations and not has_word_annotations:
        return "sentence", "Contains only sentence annotations"
    else:
        # Mixed case - check filename for clues
        filename = os.path.basename(filepath).lower()
        if "词标注" in filename or "word" in filename or "pos" in filename:
            return "word", "Filename indicates word annotation"
        elif "句标注" in filename or "sentence" in filename or "discourse" in filename:
            return "sentence", "Filename indicates sentence annotation"
        else:
            return None, "Cannot determine annotation type (mixed content or ambiguous)"

def main(input_dir, word_dir, sentence_dir):
    """Main function to split annotation files into word and sentence types."""
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return
    
    os.makedirs(word_dir, exist_ok=True)
    os.makedirs(sentence_dir, exist_ok=True)
    
    print(f"Starting annotation type classification in '{input_dir}'...")
    
    word_count = 0
    sentence_count = 0
    unclassified_count = 0
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".txt") and not filename.endswith(".bak"):
            filepath = os.path.join(input_dir, filename)
            
            annotation_type, reason = classify_annotation_file(filepath, word_dir, sentence_dir)
            
            if annotation_type == "word":
                shutil.move(filepath, os.path.join(word_dir, filename))
                print(f"  [WORD] {filename} - {reason}")
                word_count += 1
            elif annotation_type == "sentence":
                shutil.move(filepath, os.path.join(sentence_dir, filename))
                print(f"  [SENTENCE] {filename} - {reason}")
                sentence_count += 1
            else:
                print(f"  [UNCLASSIFIED] {filename} - {reason}")
                unclassified_count += 1
    
    print("\n--- Classification Summary ---")
    print(f"Total files processed: {word_count + sentence_count + unclassified_count}")
    print(f"Word annotation files moved to '{word_dir}': {word_count}")
    print(f"Sentence annotation files moved to '{sentence_dir}': {sentence_count}")
    print(f"Unclassified files remaining in '{input_dir}': {unclassified_count}")

if __name__ == "__main__":
    input_dir = "d:/_College/NLP/Research/清洗后数据/合规数据"
    word_dir = "d:/_College/NLP/Research/清洗后数据/词标注"
    sentence_dir = "d:/_College/NLP/Research/清洗后数据/句标注"
    
    main(input_dir, word_dir, sentence_dir)