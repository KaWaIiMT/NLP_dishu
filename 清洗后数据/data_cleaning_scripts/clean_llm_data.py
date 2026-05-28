
import os
import json
import shutil
import argparse

def load_schema(schema_path):
    """Loads the JSON schema from a markdown file."""
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            # We need to parse the markdown to extract the JSON schema.
            # This is a simplification; a more robust solution would parse markdown carefully.
            # For now, we'll look for JSON examples within the markdown.
            schema_content = f.read()
            # Basic attempt to find a full JSON example within the markdown
            json_start = schema_content.find("```json")
            if json_start == -1:
                json_start = schema_content.find("```") # Fallback if ```json is not used

            if json_start != -1:
                json_end = schema_content.find("```", json_start + 7) # Find the closing ```
                if json_end != -1:
                    json_str = schema_content[json_start + 7 : json_end].strip()
                    # Remove potential leading/trailing empty lines or comments from the JSON string itself
                    json_str = "\n".join([line for line in json_str.splitlines() if line.strip() and not line.strip().startswith("//")])
                    return json.loads(json_str)
                else:
                    print(f"Warning: Could not find closing ``` for JSON schema in {schema_path}")
                    return None
            else:
                print(f"Warning: Could not find JSON schema example in {schema_path}")
                return None
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON schema from {schema_path}. Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading schema: {e}")
        return None

def validate_llm_data(filepath, schema):
    """Validates a single .txt file containing LLM annotation data."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return False, "File is empty"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Ensure content is not just whitespace
            if not content.strip():
                return False, "File contains only whitespace"

            data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

    # --- Schema Validation ---
    # Ensure data is a dictionary (JSON object), not a list or other type
    if not isinstance(data, dict):
        return False, "Top-level JSON structure is not an object (expected {{...}})"

    # Top-level keys validation
    required_top_keys = {"project", "student", "source_text", "units", "annotations"}
    if not required_top_keys.issubset(data.keys()):
        missing_keys = required_top_keys - data.keys()
        return False, f"Missing top-level keys: {missing_keys}"

    # Validate "project" structure (basic check for presence of key fields)
    if "project" in data:
        if not all(k in data["project"] for k in ["project_name", "data_type", "schema_version", "annotation_language"]):
            return False, "Project section missing required keys (e.g., project_name, data_type)"
        if data["project"].get("data_type") != "natural_language_text":
             return False, "Project data_type is not 'natural_language_text'"
        if data["project"].get("schema_version") != "1.0":
             return False, "Project schema_version is not '1.0'"

    # Validate "student" structure
    if "student" in data:
        if not all(k in data["student"] for k in ["student_id", "student_name", "word_task_type", "sentence_task_type"]):
             return False, "Student section missing required keys (e.g., student_id, word_task_type)"
        # Check task types against schema's recommended options
        valid_word_tasks = {"pos_like_category", "morphological_like_features", "semantic_primitives", "pragmatic_meaning", "literal_gloss"}
        valid_sentence_tasks = {"discourse_relation", "free_translation"}
        if data["student"].get("word_task_type") not in valid_word_tasks:
            return False, f"Invalid word_task_type: {data['student'].get('word_task_type')}"
        if data["student"].get("sentence_task_type") not in valid_sentence_tasks:
            return False, f"Invalid sentence_task_type: {data['student'].get('sentence_task_type')}"

    # Validate "source_text" structure
    if "source_text" in data:
        if not all(k in data["source_text"] for k in ["text_id", "raw_text"]):
             return False, "Source_text section missing required keys (e.g., text_id, raw_text)"

    # Validate "units" structure (basic checks)
    if not isinstance(data.get("units"), list) or not data["units"]:
        return False, "Units section is missing, empty, or not a list"
    for unit in data["units"]:
        if not all(k in unit for k in ["unit_id", "unit_type", "text"]):
            return False, "Unit missing required keys (e.g., unit_id, unit_type, text)"
        if unit.get("unit_type") not in ["word", "sentence"]:
             return False, f"Invalid unit_type: {unit.get('unit_type')}"

    # Validate "annotations" structure
    if not isinstance(data.get("annotations"), list):
        return False, "Annotations section is missing or not a list"

    for ann in data.get("annotations", []):
        if not all(k in ann for k in ["annotation_id", "target_id", "target_type", "task_id", "task_label_zh", "task_label_en", "value", "llm_used"]):
            return False, "Annotation missing required keys (e.g., annotation_id, value, llm_used)"

        # Validate value type based on task_id (simplified for common types)
        task_id = ann.get("task_id")
        value = ann.get("value")

        if task_id in ["semantic_primitives", "pos_like_category", "morphological_like_features", "ambiguity_sources", "communication_functions", "visual_cues"]: # Multi-value tasks
            if not isinstance(value, list):
                return False, f"Annotation for task '{task_id}' has incorrect value type: expected list, got {type(value).__name__}"
        elif task_id in ["pragmatic_meaning", "free_translation", "literal_gloss"]: # Text value tasks
            if not isinstance(value, str):
                return False, f"Annotation for task '{task_id}' has incorrect value type: expected string, got {type(value).__name__}"
        elif task_id in ["discourse_relation", "semantic_role_core", "reference_type", "speech_act_primary"]: # Single value tasks
            if not isinstance(value, str):
                 return False, f"Annotation for task '{task_id}' has incorrect value type: expected string, got {type(value).__name__}"
        # Add checks for scale tasks if needed, though the schema example shows them as items within tasks.

        # Validate llm_used and llm_name consistency
        if ann.get("llm_used") and ann.get("llm_name") is None:
            return False, f"Annotation for task '{task_id}' has llm_used=true but llm_name is null"
        if not ann.get("llm_used") and ann.get("llm_name") is not None:
             return False, f"Annotation for task '{task_id}' has llm_used=false but llm_name is not null"

    return True, "Valid"

def main(input_dir, cleaned_dir, invalid_dir, schema_path):
    """Main function to clean LLM data files."""
    if not os.path.exists(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        return

    os.makedirs(cleaned_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)

    schema = load_schema(schema_path)
    if schema is None:
        print("Failed to load schema. Cannot proceed with validation.")
        return

    print(f"Starting data cleaning process in '{input_dir}'...")
    print(f"Schema loaded successfully from '{schema_path}'.")

    valid_files = []
    invalid_files = []

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".txt"):
            filepath = os.path.join(input_dir, filename)
            is_valid, reason = validate_llm_data(filepath, schema)

            if is_valid:
                print(f"  [VALID] {filename}")
                shutil.move(filepath, os.path.join(cleaned_dir, filename))
                valid_files.append(filename)
            else:
                print(f"  [INVALID] {filename} - Reason: {reason}")
                shutil.move(filepath, os.path.join(invalid_dir, filename))
                invalid_files.append(filename)
        else:
            # Optionally handle non-txt files, or just ignore them
            pass

    print("\n--- Cleaning Summary ---")
    print(f"Total files processed: {len(valid_files) + len(invalid_files)}")
    print(f"Valid files moved to '{cleaned_dir}': {len(valid_files)}")
    print(f"Invalid files moved to '{invalid_dir}': {len(invalid_files)}")
    if invalid_files:
        print("Details of invalid files:")
        for fname in invalid_files:
            # Re-run validation on moved files to get the reason again, as files are moved
            # This is a bit inefficient, ideally reason is stored. For simplicity here, we assume reason is printed above.
            # A better approach would be to store reasons in a list of tuples.
            pass # Reason was already printed during iteration

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean LLM annotation data.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing the LLM .txt annotation files.")
    parser.add_argument("--cleaned_dir", type=str, default="cleaned_data", help="Directory to move valid files to.")
    parser.add_argument("--invalid_dir", type=str, default="invalid_data", help="Directory to move invalid files to.")
    parser.add_argument("--schema_path", type=str, required=True, help="Path to the schema markdown file (标注规范.md).")

    args = parser.parse_args()

    # Construct absolute path for schema if it's relative
    # Assuming schema_path is relative to the script or project root
    # If schema_path is absolute, this join will just use the absolute path
    schema_full_path = os.path.abspath(args.schema_path)

    # Ensure input_dir is also absolute for robustness
    input_dir_full_path = os.path.abspath(args.input_dir)
    cleaned_dir_full_path = os.path.abspath(args.cleaned_dir)
    invalid_dir_full_path = os.path.abspath(args.invalid_dir)

    main(input_dir_full_path, cleaned_dir_full_path, invalid_dir_full_path, schema_full_path)
