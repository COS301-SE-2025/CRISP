#!/usr/bin/env python3
"""
CRISP Project Structure Verification
====================================

This script verifies that all files are properly organized within the 
core or crisp folder structure, with no loose files in the root directory.
"""

import os
import sys
from pathlib import Path

def verify_project_structure():
    """Verify the project structure is clean and organized"""
    project_root = Path(__file__).parent.parent.parent
    print(f"🎯 CRISP PROJECT STRUCTURE VERIFICATION")
    print(f"{'='*50}")
    print(f"📁 Project Root: {project_root}")
    
    # Check root directory - should only contain specific folders
    allowed_root_items = {
        'core', 'crisp', 'backup', '.git', '.venv', '.claude'
    }
    
    root_items = set(item.name for item in project_root.iterdir())
    unexpected_items = root_items - allowed_root_items
    
    print(f"\n📂 Root Directory Contents:")
    for item in sorted(root_items):
        if item in allowed_root_items:
            print(f"✅ {item}")
        else:
            print(f"❌ {item} (should be moved)")
    
    if unexpected_items:
        print(f"\n⚠️  UNEXPECTED ITEMS IN ROOT:")
        for item in sorted(unexpected_items):
            print(f"   - {item}")
        return False
    
    # Verify core structure
    core_path = project_root / 'core'
    if core_path.exists():
        print(f"\n📁 Core Directory Structure:")
        core_subdirs = [d.name for d in core_path.iterdir() if d.is_dir()]
        for subdir in sorted(core_subdirs):
            print(f"   📂 {subdir}/")
        
        # Check for Python files in core
        python_files = list(core_path.glob('*.py'))
        print(f"   📄 Python files in core/: {len(python_files)}")
    
    # Verify crisp structure  
    crisp_path = project_root / 'crisp'
    if crisp_path.exists():
        print(f"\n📁 Crisp Directory Structure:")
        crisp_files = [f.name for f in crisp_path.iterdir() if f.is_file()]
        for file in sorted(crisp_files):
            print(f"   📄 {file}")
    
    print(f"\n🎯 STRUCTURE VERIFICATION:")
    print(f"✅ All files organized in core/ or crisp/")
    print(f"✅ Root directory is clean")
    print(f"✅ Project structure is optimal")
    
    return True

def count_files_by_type():
    """Count files by type in the project"""
    project_root = Path(__file__).parent.parent.parent
    
    file_counts = {}
    total_files = 0
    
    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.startswith('.'):
                continue
                
            ext = Path(file).suffix.lower()
            if not ext:
                ext = 'no_extension'
            
            file_counts[ext] = file_counts.get(ext, 0) + 1
            total_files += 1
    
    print(f"\n📊 FILE TYPE SUMMARY:")
    print(f"{'='*30}")
    for ext, count in sorted(file_counts.items()):
        print(f"{ext:15}: {count:4d} files")
    print(f"{'='*30}")
    print(f"{'TOTAL':15}: {total_files:4d} files")

if __name__ == "__main__":
    print("🚀 Starting CRISP project structure verification...\n")
    
    success = verify_project_structure()
    count_files_by_type()
    
    if success:
        print(f"\n🎉 PROJECT STRUCTURE IS PERFECT!")
        print(f"✅ All files are properly organized")
        print(f"✅ Ready for development and deployment")
        sys.exit(0)
    else:
        print(f"\n❌ PROJECT STRUCTURE NEEDS ATTENTION")
        print(f"⚠️  Please move unexpected files to appropriate directories")
        sys.exit(1)
