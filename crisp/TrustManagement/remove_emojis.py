#!/usr/bin/env python3
"""
Script to remove emojis from test files while preserving colors
"""

import os
import re

# Emoji patterns to remove
EMOJI_PATTERNS = [
    r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
    r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
    r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
    r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
    r'', r'', r'', r'', r'', r'', r'', r'', r'', r'',
    r'', r'', r''
]

def remove_emojis_from_file(file_path):
    """Remove emojis from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove emojis (with optional space after)
        for emoji in EMOJI_PATTERNS:
            content = re.sub(emoji + r'\s?', '', content)
        
        # If content changed, write it back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all Python files in the UserManagment directory"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_updated = 0
    
    # Walk through all Python files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if remove_emojis_from_file(file_path):
                    files_updated += 1
    
    print(f"\nTotal files updated: {files_updated}")

if __name__ == '__main__':
    main()
