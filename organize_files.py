import os
import shutil

def organize_files():
    """Organize experiment files into Chinese-named folders."""
    base_dir = "d:/_College/NLP/Research"
    target_dir = "d:/_College/NLP/Research/地书实验结果"
    
    # Move CSV files
    macro_dir = os.path.join(target_dir, "宏观分析结果")
    micro_dir = os.path.join(target_dir, "微观分析结果")
    
    for filename in os.listdir(base_dir):
        filepath = os.path.join(base_dir, filename)
        
        if os.path.isfile(filepath):
            # Move macro analysis CSV
            if filename == "macro_analysis_results.csv":
                shutil.move(filepath, os.path.join(macro_dir, filename))
                print(f"Moved: {filename} -> 宏观分析结果/")
            
            # Move micro analysis CSVs
            elif filename.startswith("dishu_") and filename.endswith("_results.csv"):
                shutil.move(filepath, os.path.join(micro_dir, filename))
                print(f"Moved: {filename} -> 微观分析结果/")
            
            # Move scripts
            elif filename in ["macro_analysis.py", "micro_analysis.py"]:
                shutil.copy(filepath, os.path.join(target_dir, "实验脚本", filename))
                print(f"Copied: {filename} -> 实验脚本/")
            
            # Move report
            elif filename == "experiment_report.md":
                shutil.move(filepath, os.path.join(target_dir, filename))
                print(f"Moved: {filename} -> 地书实验结果/")
    
    # Copy cleaned data
    cleaned_src = "d:/_College/NLP/Research/清洗后数据"
    cleaned_dst = os.path.join(target_dir, "清洗后数据")
    
    if os.path.exists(cleaned_src) and not os.path.exists(cleaned_dst):
        shutil.copytree(cleaned_src, cleaned_dst)
        print(f"Copied directory: 清洗后数据 -> 地书实验结果/")

if __name__ == "__main__":
    organize_files()
    print("Files organized successfully!")
