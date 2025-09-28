#!/bin/bash
# Script to remove console messages from React components

# Find all JS/JSX files and remove console statements
find "/mnt/c/Users/jadyn/CRISP/Capstone-Unified/frontend/crisp-react/src" -name "*.js" -o -name "*.jsx" | while read file; do
    # Skip if file doesn't exist or is empty
    [ ! -s "$file" ] && continue
    
    echo "Processing: $file"
    
    # Create backup
    cp "$file" "$file.bak"
    
    # Remove console.log/error/warn/debug/info lines (but keep commented ones and PERFORMANCE FIX ones)
    sed -i '/^ *\/\/ PERFORMANCE FIX: console\./!{
        /^ *console\.\(log\|error\|warn\|info\|debug\)/d
        /^ *\/\/ *console\.\(log\|error\|warn\|info\|debug\)/!s/\(.*\)console\.\(log\|error\|warn\|info\|debug\)([^;]*);*\(.*\)/\1\3/g
    }' "$file"
    
    # Check if file was modified
    if ! cmp -s "$file" "$file.bak"; then
        echo "  - Modified: $file"
    else
        # Remove backup if no changes
        rm "$file.bak"
    fi
done
