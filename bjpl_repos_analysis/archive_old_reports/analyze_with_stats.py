#!/usr/bin/env python3
"""
Fixed GitHub Activity Analysis - with proper statistics
"""

import subprocess
import os
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_repository_stats(repo_path, days_back=30):
    """Get proper statistics for a repository"""
    if not os.path.exists(os.path.join(repo_path, '.git')):
        return None
    
    original_dir = os.getcwd()
    os.chdir(repo_path)
    
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    stats = {
        'path': repo_path,
        'name': os.path.basename(repo_path) or os.path.basename(os.path.dirname(repo_path)),
        'commits': [],
        'total_files': 0,
        'insertions': 0,
        'deletions': 0,
        'files_changed': set()
    }
    
    try:
        # Get commit hashes for the period
        commit_hashes = subprocess.run(
            ['git', 'rev-list', '--since=' + start_date, '--all'],
            capture_output=True, text=True
        ).stdout.strip().split('\n')
        
        if commit_hashes and commit_hashes[0]:
            stats['commits'] = commit_hashes
            
            # Get overall diff stats for the entire period
            oldest_commit = commit_hashes[-1] if commit_hashes else 'HEAD'
            
            # Get numeric stats
            numstat = subprocess.run(
                ['git', 'diff', '--numstat', f'{oldest_commit}^..HEAD'],
                capture_output=True, text=True, stderr=subprocess.DEVNULL
            ).stdout.strip()
            
            if numstat:
                for line in numstat.split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            try:
                                if parts[0] != '-':
                                    stats['insertions'] += int(parts[0])
                                if parts[1] != '-':
                                    stats['deletions'] += int(parts[1])
                                stats['files_changed'].add(parts[2])
                            except ValueError:
                                pass
            
            stats['total_files'] = len(stats['files_changed'])
            
            # Alternative method: use shortstat for the period
            if stats['insertions'] == 0 and stats['deletions'] == 0:
                shortstat = subprocess.run(
                    ['git', 'log', '--since=' + start_date, '--all', '--shortstat', '--pretty=format:'],
                    capture_output=True, text=True
                ).stdout.strip()
                
                if shortstat:
                    import re
                    for line in shortstat.split('\n'):
                        ins_match = re.search(r'(\d+) insertion', line)
                        del_match = re.search(r'(\d+) deletion', line)
                        if ins_match:
                            stats['insertions'] += int(ins_match.group(1))
                        if del_match:
                            stats['deletions'] += int(del_match.group(1))
    
    except Exception as e:
        print(f"  Error getting stats for {repo_path}: {e}")
    
    os.chdir(original_dir)
    return stats

def main():
    print("Analyzing repositories with proper statistics...\n")
    
    base_path = "C:\\Users\\brand\\Development\\Project_Workspace"
    
    # List of key repositories to analyze
    repos_to_analyze = [
        base_path,  # Main workspace
        os.path.join(base_path, 'brandonjplambert'),
        os.path.join(base_path, 'describe_it'),
        os.path.join(base_path, 'letratos'),
        os.path.join(base_path, 'internet'),
        os.path.join(base_path, 'fancy_monkey'),
        os.path.join(base_path, 'subjunctive_practice'),
    ]
    
    total_insertions = 0
    total_deletions = 0
    total_commits = 0
    
    print("=" * 70)
    print("REPOSITORY STATISTICS - Last 30 Days")
    print("=" * 70)
    
    for repo_path in repos_to_analyze:
        if os.path.exists(repo_path):
            print(f"\nAnalyzing: {os.path.basename(repo_path) or 'Project_Workspace'}")
            stats = analyze_repository_stats(repo_path)
            
            if stats and stats['commits']:
                commits_count = len(stats['commits'])
                total_commits += commits_count
                total_insertions += stats['insertions']
                total_deletions += stats['deletions']
                
                print(f"  Commits: {commits_count}")
                print(f"  Files Changed: {stats['total_files']}")
                print(f"  Lines Added: +{stats['insertions']:,}")
                print(f"  Lines Deleted: -{stats['deletions']:,}")
                print(f"  Net Change: {stats['insertions'] - stats['deletions']:+,} lines")
                
                # Show some changed files
                if stats['files_changed']:
                    print(f"  Sample files modified:")
                    for f in list(stats['files_changed'])[:5]:
                        print(f"    • {f}")
    
    print("\n" + "=" * 70)
    print("OVERALL TOTALS")
    print("=" * 70)
    print(f"Total Commits: {total_commits}")
    print(f"Total Lines Added: +{total_insertions:,}")
    print(f"Total Lines Deleted: -{total_deletions:,}")
    print(f"Net Code Change: {total_insertions - total_deletions:+,} lines")
    print("=" * 70)

if __name__ == "__main__":
    main()