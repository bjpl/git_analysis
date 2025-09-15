#!/bin/bash

echo "======================================"
echo "Complete Repository Analysis"
echo "======================================"
echo ""

# Main workspace
echo "=== Project_Workspace (Main) ==="
cd /c/Users/brand/Development/Project_Workspace
echo -n "Current lines of code: "
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.py" -o -name "*.html" -o -name "*.css" -o -name "*.md" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}'
echo -n "Commits (30 days): "
git log --since="30 days ago" --oneline 2>/dev/null | wc -l
echo -n "Files changed (30 days): "
git diff --stat HEAD~68 HEAD 2>/dev/null | tail -1 | awk '{print $1}'
git log --since="30 days ago" --shortstat --pretty=format: | grep -E "file|insertion|deletion" | awk '{files+=$1; inserted+=$4; deleted+=$6} END {print "Added:", inserted, "lines\nDeleted:", deleted, "lines"}'
echo ""

# Key repositories
repos=("brandonjplambert" "describe_it" "letratos" "internet" "fancy_monkey" "subjunctive_practice" "hablas")

for repo in "${repos[@]}"; do
    if [ -d "/c/Users/brand/Development/Project_Workspace/$repo" ]; then
        echo "=== $repo ==="
        cd "/c/Users/brand/Development/Project_Workspace/$repo"
        echo -n "Current lines of code: "
        find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.py" -o -name "*.html" -o -name "*.css" -o -name "*.md" \) -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}'
        echo -n "Commits (30 days): "
        git log --since="30 days ago" --oneline 2>/dev/null | wc -l
        git log --since="30 days ago" --shortstat --pretty=format: | grep -E "file|insertion|deletion" | awk '{files+=$1; inserted+=$4; deleted+=$6} END {print "Added:", inserted, "lines\nDeleted:", deleted, "lines"}'
        echo -n "Primary language: "
        git ls-files | grep -E '\.(js|ts|py|rb|java|cpp|c|go|rs|php|swift)$' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}'
        echo ""
    fi
done

# Archive repositories
echo "=== ARCHIVED REPOSITORIES ==="
for repo in /c/Users/brand/Development/Project_Workspace/archive/*/; do
    if [ -d "$repo/.git" ]; then
        name=$(basename "$repo")
        cd "$repo"
        echo -n "$name - Lines: "
        find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.html" \) -not -path "*/node_modules/*" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}'
    fi
done