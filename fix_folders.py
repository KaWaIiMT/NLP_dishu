import os
import shutil

base_folder = r'd:\_College\NLP\Research\地书实验结果\清洗后数据'
duplicate_folder = os.path.join(base_folder, '清洗后数据')

if os.path.exists(duplicate_folder):
    print(f"Found duplicate folder, moving contents...")
    
    for item in os.listdir(duplicate_folder):
        src = os.path.join(duplicate_folder, item)
        dst = os.path.join(base_folder, item)
        
        if os.path.exists(dst):
            print(f"  {item} exists, skipping")
            continue
        
        shutil.move(src, dst)
        print(f"  Moved {item}")
    
    try:
        os.rmdir(duplicate_folder)
        print(f"Removed duplicate folder")
    except Exception as e:
        print(f"Could not remove folder: {e}")

print("Done!")
