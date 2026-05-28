# LLM Annotation Data Cleaning Script

This script helps clean and validate LLM-generated annotation data files (`.txt` files containing JSON) based on a provided schema.

## Overview

The script iterates through all `.txt` files in a specified input directory. For each file, it performs the following checks:

1.  **File Existence and Emptiness**: Ensures the file exists and is not empty.
2.  **JSON Validity**: Checks if the file content is valid JSON.
3.  **Schema Conformance**: Validates the JSON structure and specific field values (like `task_id`, `value` types, `llm_used`/`llm_name` consistency) against the rules defined in `标注规范.md`.

Based on the validation results, files are moved to either a `cleaned_data` directory (if valid) or an `invalid_data` directory (if invalid).

## Prerequisites

*   Python 3.6 or higher installed.
*   The `argparse`, `json`, `os`, and `shutil` libraries, which are part of Python's standard library.

## Setup

1.  **Save the script**: Save the provided Python script as `clean_llm_data.py`.
2.  **Save the schema**: Ensure the `标注规范.md` file is accessible at the path specified by the `--schema_path` argument.
3.  **Organize your data**: Place all LLM annotation `.txt` files that need cleaning into a single input directory.

## Usage

Open your terminal or command prompt, navigate to the directory where you saved `clean_llm_data.py`, and run the script with the following command:

```bash
python clean_llm_data.py --input_dir <path_to_your_data_directory> --schema_path <path_to_标注规范.md> [--cleaned_dir <output_cleaned_dir>] [--invalid_dir <output_invalid_dir>]
```

**Arguments:**

*   `--input_dir` (required): The path to the directory containing the `.txt` annotation files you want to clean.
*   `--schema_path` (required): The path to the `标注规范.md` file, which contains the expected JSON structure and rules.
*   `--cleaned_dir` (optional): The directory where valid files will be moved. Defaults to `cleaned_data` in the current working directory.
*   `--invalid_dir` (optional): The directory where invalid files will be moved. Defaults to `invalid_data` in the current working directory.

**Example:**

Assume your annotation files are in `D:\_College\NLP\Research\LLM_Annotations\raw_data` and your `标注规范.md` is at `D:\_College\NLP\Research\schema\标注规范.md`. You can run the script like this:

```bash
python clean_llm_data.py --input_dir "D:\_College\NLP\Research\LLM_Annotations\raw_data" --schema_path "D:\_College\NLP\Research\schema\标注规范.md" --cleaned_dir "D:\_College\NLP\Research\LLM_Annotations\cleaned" --invalid_dir "D:\_College\NLP\Research\LLM_Annotations\invalid"
```

## Output

After execution, the script will provide a summary of the cleaning process, indicating:

*   The total number of files processed.
*   The number of valid files moved to the `cleaned_dir`.
*   The number of invalid files moved to the `invalid_dir`.
*   Details about why files were marked as invalid.

## Important Notes

*   The script expects `.txt` files to contain JSON content. It will treat any `.txt` file it encounters as a potential JSON file for validation.
*   The script uses basic JSON parsing and schema checking. Complex validation rules or highly malformed JSON might require more advanced parsing or manual review.
*   The script does not modify files in place; it moves them to the specified `cleaned_dir` or `invalid_dir`.
