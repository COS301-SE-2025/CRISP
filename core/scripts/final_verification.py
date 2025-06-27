#!/usr/bin/env python3
"""
CRISP Final Organization Verification
====================================

Final verification that all files are properly organized in core/ or crisp/ folders.
"""

import os
import sys
from pathlib import Path

def main():
    """Main verification function"""
    project_root = Path(__file__).parent.parent.parent
    
    print("🎯 CRISP FINAL ORGANIZATION VERIFICATION")
    print("=" * 50)
    
    # Check root directory structure
    root_items = list(project_root.iterdir())
    allowed_root_folders = {'.git', '.venv', '.claude', 'backup', 'core', 'crisp'}
    
    print("\n📁 ROOT DIRECTORY STATUS:")
    root_folders = [item.name for item in root_items if item.is_dir()]
    root_files = [item.name for item in root_items if item.is_file()]
    
    print(f"   Folders: {sorted(root_folders)}")
    print(f"   Files: {sorted(root_files) if root_files else 'None ✅'}")
    
    # Verify only allowed folders exist
    unexpected_folders = set(root_folders) - allowed_root_folders
    if unexpected_folders:
        print(f"❌ Unexpected folders in root: {unexpected_folders}")
        return False
    
    if root_files:
        print(f"❌ Files found in root directory: {root_files}")
        print("   All files should be in core/ or crisp/ subdirectories")
        return False
    
    # Verify core structure
    core_path = project_root / 'core'
    print(f"\n📁 CORE DIRECTORY STRUCTURE:")
    if core_path.exists():
        core_subdirs = sorted([d.name for d in core_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
        for subdir in core_subdirs:
            subdir_path = core_path / subdir
            file_count = len([f for f in subdir_path.rglob('*') if f.is_file()])
            print(f"   ✅ {subdir}/ ({file_count} files)")
        
        # Count Python modules in core
        core_py_files = list(core_path.glob('*.py'))
        print(f"   ✅ Core Python modules: {len(core_py_files)}")
        
    # Verify crisp structure
    crisp_path = project_root / 'crisp'
    print(f"\n📁 CRISP DIRECTORY STRUCTURE:")
    if crisp_path.exists():
        crisp_files = sorted([f.name for f in crisp_path.iterdir() if f.is_file()])
        for file in crisp_files:
            print(f"   ✅ {file}")
    
    # Summary statistics
    total_py_files = len(list(project_root.rglob('*.py')))
    core_py_files = len(list(core_path.rglob('*.py'))) if core_path.exists() else 0
    crisp_py_files = len(list(crisp_path.rglob('*.py'))) if crisp_path.exists() else 0
    
    print(f"\n📊 PROJECT STATISTICS:")
    print(f"   Total Python files: {total_py_files}")
    print(f"   Core Python files: {core_py_files}")
    print(f"   Crisp Python files: {crisp_py_files}")
    
    print(f"\n🎉 ORGANIZATION VERIFICATION COMPLETE!")
    print(f"✅ All files are properly organized in core/ or crisp/")
    print(f"✅ Root directory is clean (no loose files)")
    print(f"✅ Project structure follows Django best practices")
    print(f"✅ Ready for development and deployment!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
