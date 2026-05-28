import os
import json
import shutil

def is_sentence_annotation(filepath):
    """Check if a file contains sentence-level annotations."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return False, "Empty file"
                
            data = json.loads(content)
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    # Check task types
    student = data.get("student", {})
    sentence_task_type = student.get("sentence_task_type")
    
    # Check units
    units = data.get("units", [])
    has_sentence_units = any(unit.get("unit_type") == "sentence" for unit in units)
    
    # Check annotations
    annotations = data.get("annotations", [])
    has_sentence_annotations = any(ann.get("target_type") == "sentence" for ann in annotations)
    
    # Check filename
    filename = os.path.basename(filepath).lower()
    has_sentence_filename = "句标注" in filename or "sentence" in filename or "discourse" in filename
    
    # Classification logic
    if sentence_task_type and sentence_task_type != "none":
        return True, f"Sentence task type: {sentence_task_type}"
    elif has_sentence_units and not any(unit.get("unit_type") == "word" for unit in units):
        return True, "Contains only sentence units"
    elif has_sentence_annotations and not any(ann.get("target_type") == "word" for ann in annotations):
        return True, "Contains only sentence annotations"
    elif has_sentence_filename and not ("词标注" in filename or "word" in filename):
        return True, "Filename indicates sentence annotation"
    else:
        return False, "Not a pure sentence annotation file"

def main(input_dir, sentence_dir):
    """Classify and move sentence annotation files."""
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return
    
    os.makedirs(sentence_dir, exist_ok=True)
    
    print(f"Starting sentence annotation classification in '{input_dir}'...")
    
    sentence_count = 0
    non_sentence_count = 0
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".txt") and not filename.endswith(".bak"):
            filepath = os.path.join(input_dir, filename)
            
            is_sentence, reason = is_sentence_annotation(filepath)
            
            if is_sentence:
                shutil.move(filepath, os.path.join(sentence_dir, filename))
                print(f"  [SENTENCE] {filename} - {reason}")
                sentence_count += 1
            else:
                print(f"  [NON-SENTENCE] {filename} - {reason}")
                non_sentence_count += 1
    
    print("\n--- Sentence Classification Summary ---")
    print(f"Total files processed: {sentence_count + non_sentence_count}")
    print(f"Sentence annotation files moved to '{sentence_dir}': {sentence_count}")
    print(f"Non-sentence files remaining in '{input_dir}': {non_sentence_count}")

if __name__ == "__main__":
    input_dir = "d:/_College/NLP/Research/清洗后数据/临时句标注"
    sentence_dir = "d:/_College/NLP/Research/清洗后数据/句标注"
    
    main(input_dir, sentence_dir)