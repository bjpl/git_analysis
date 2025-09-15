#!/usr/bin/env python3
"""
Final Accurate GitHub Activity Analysis for bjpl
Gathers real metrics without double-counting
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

def count_lines_of_code(repo_path):
    """Count actual lines of code, excluding dependencies"""
    extensions = ['.js', '.ts', '.tsx', '.jsx', '.py', '.html', '.css', '.scss', '.md', '.yml', '.yaml', '.json']
    exclude_dirs = ['node_modules', '.git', 'dist', 'build', '.next', '_site', 'coverage']
    
    total_lines = 0
    file_count = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Remove excluded directories from search
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1
                except:
                    pass
    
    return total_lines, file_count

def get_repo_stats(repo_path):
    """Get comprehensive stats for a repository"""
    os.chdir(repo_path)
    
    stats = {
        'name': os.path.basename(repo_path) or 'Project_Workspace',
        'path': repo_path,
        'current_loc': 0,
        'file_count': 0,
        'commits_30d': 0,
        'commits_total': 0,
        'authors': set(),
        'recent_commits': [],
        'primary_language': 'Unknown',
        'is_archived': 'archive' in repo_path.lower()
    }
    
    # Count lines of code
    stats['current_loc'], stats['file_count'] = count_lines_of_code(repo_path)
    
    try:
        # Get commit counts
        commits_30d = subprocess.run(
            ['git', 'log', '--since=30 days ago', '--oneline'],
            capture_output=True, text=True
        ).stdout.strip().split('\n')
        stats['commits_30d'] = len([c for c in commits_30d if c])
        
        # Total commits
        total_commits = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True, text=True
        ).stdout.strip()
        stats['commits_total'] = int(total_commits) if total_commits else 0
        
        # Get recent commit messages
        recent = subprocess.run(
            ['git', 'log', '--since=30 days ago', '--pretty=format:%ad | %s', '--date=short', '-5'],
            capture_output=True, text=True
        ).stdout.strip()
        if recent:
            stats['recent_commits'] = recent.split('\n')[:3]
        
        # Get authors
        authors = subprocess.run(
            ['git', 'log', '--since=30 days ago', '--pretty=format:%an'],
            capture_output=True, text=True
        ).stdout.strip()
        if authors:
            stats['authors'] = set(authors.split('\n'))
        
        # Determine primary language
        language_counts = {}
        files = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True, text=True
        ).stdout.strip().split('\n')
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.js', '.jsx']:
                language_counts['JavaScript'] = language_counts.get('JavaScript', 0) + 1
            elif ext in ['.ts', '.tsx']:
                language_counts['TypeScript'] = language_counts.get('TypeScript', 0) + 1
            elif ext == '.py':
                language_counts['Python'] = language_counts.get('Python', 0) + 1
            elif ext in ['.html', '.css', '.scss']:
                language_counts['Web'] = language_counts.get('Web', 0) + 1
            elif ext == '.md':
                language_counts['Markdown'] = language_counts.get('Markdown', 0) + 1
        
        if language_counts:
            stats['primary_language'] = max(language_counts, key=language_counts.get)
        
        # Get remote URL to determine if public/private
        remote = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True, text=True
        ).stdout.strip()
        stats['remote_url'] = remote
        stats['is_public'] = 'github.com/bjpl' in remote.lower()
        
    except Exception as e:
        print(f"Error processing {repo_path}: {e}")
    
    return stats

def main():
    base_path = "C:\\Users\\brand\\Development\\Project_Workspace"
    
    # Find all repositories
    repos_to_analyze = []
    
    # Add main workspace
    if os.path.exists(os.path.join(base_path, '.git')):
        repos_to_analyze.append(base_path)
    
    # Add subdirectories
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            if os.path.exists(os.path.join(item_path, '.git')):
                repos_to_analyze.append(item_path)
            # Check archive folder
            elif item == 'archive':
                for archived in os.listdir(item_path):
                    archived_path = os.path.join(item_path, archived)
                    if os.path.isdir(archived_path) and os.path.exists(os.path.join(archived_path, '.git')):
                        repos_to_analyze.append(archived_path)
    
    # Analyze all repositories
    all_stats = []
    for repo_path in repos_to_analyze:
        print(f"Analyzing: {os.path.basename(repo_path) or 'Project_Workspace'}...")
        stats = get_repo_stats(repo_path)
        all_stats.append(stats)
    
    # Sort by commits and activity
    active_repos = [r for r in all_stats if r['commits_30d'] > 0 and not r['is_archived']]
    archived_repos = [r for r in all_stats if r['is_archived']]
    inactive_repos = [r for r in all_stats if r['commits_30d'] == 0 and not r['is_archived']]
    
    active_repos.sort(key=lambda x: x['commits_30d'], reverse=True)
    
    # Calculate totals
    total_loc = sum(r['current_loc'] for r in all_stats)
    total_commits_30d = sum(r['commits_30d'] for r in all_stats)
    total_files = sum(r['file_count'] for r in all_stats)
    
    # Output results
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(f"Total Repositories: {len(all_stats)}")
    print(f"Active (30 days): {len(active_repos)}")
    print(f"Archived: {len(archived_repos)}")
    print(f"Total Current LOC: {total_loc:,}")
    print(f"Total Files: {total_files:,}")
    print(f"Total Commits (30 days): {total_commits_30d}")
    
    # Save detailed JSON
    output = {
        'generated': datetime.now().isoformat(),
        'summary': {
            'total_repositories': len(all_stats),
            'active_repositories': len(active_repos),
            'archived_repositories': len(archived_repos),
            'total_current_loc': total_loc,
            'total_files': total_files,
            'total_commits_30d': total_commits_30d
        },
        'repositories': {
            'active': [dict(r, authors=list(r['authors'])) for r in active_repos],
            'archived': [dict(r, authors=list(r['authors'])) for r in archived_repos],
            'inactive': [dict(r, authors=list(r['authors'])) for r in inactive_repos]
        }
    }
    
    with open('C:\\Users\\brand\\Development\\bjpl_repos_analysis\\final_stats.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nDetailed stats saved to final_stats.json")
    
    return output

if __name__ == "__main__":
    main()