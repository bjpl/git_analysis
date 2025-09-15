#!/usr/bin/env python3
"""
Complete GitHub Activity Analysis for ALL bjpl repositories (public and private)
Analyzes the last month of development activity across all local repositories
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from collections import defaultdict
import urllib.request

def get_repo_info(repo_path):
    """Get repository information including remote URL"""
    os.chdir(repo_path)
    try:
        # Get remote URL
        remote_url = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True, text=True
        ).stdout.strip()
        
        # Get current branch
        branch = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True
        ).stdout.strip()
        
        return {
            'remote_url': remote_url,
            'branch': branch,
            'is_private': 'bjpl' not in remote_url or remote_url == ''
        }
    except:
        return {
            'remote_url': 'local only',
            'branch': 'unknown',
            'is_private': True
        }

def analyze_repository(repo_path, days_back=30):
    """Analyze a git repository for recent activity"""
    if not os.path.exists(os.path.join(repo_path, '.git')):
        return None
    
    original_dir = os.getcwd()
    os.chdir(repo_path)
    
    # Get date range
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    stats = {
        'path': repo_path,
        'name': os.path.basename(repo_path) or os.path.basename(os.path.dirname(repo_path)),
        'commits': [],
        'files_changed': set(),
        'insertions': 0,
        'deletions': 0,
        'authors': set(),
        'branches': [],
        'info': get_repo_info(repo_path)
    }
    
    try:
        # Get all branches
        branches_output = subprocess.run(
            ['git', 'branch', '-a'],
            capture_output=True, text=True
        ).stdout.strip()
        
        if branches_output:
            stats['branches'] = [b.strip().replace('* ', '') for b in branches_output.split('\n')]
        
        # Get commit history from all branches
        commit_log = subprocess.run(
            ['git', 'log', '--all', f'--since={start_date}', 
             '--pretty=format:%H|%ad|%s|%an|%ae', '--date=short'],
            capture_output=True, text=True
        ).stdout.strip()
        
        if commit_log:
            for line in commit_log.split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        stats['commits'].append({
                            'hash': parts[0][:7],
                            'date': parts[1],
                            'message': parts[2],
                            'author': parts[3],
                            'email': parts[4]
                        })
                        stats['authors'].add(parts[3])
        
        # Get files changed in the time period
        files_changed = subprocess.run(
            ['git', 'diff', '--name-only', f'{start_date}..HEAD'],
            capture_output=True, text=True
        ).stdout.strip()
        
        if files_changed:
            stats['files_changed'] = set(files_changed.split('\n'))
        
        # Get detailed statistics
        for commit in stats['commits']:
            diff_stat = subprocess.run(
                ['git', 'diff', '--shortstat', f'{commit["hash"]}^..{commit["hash"]}'],
                capture_output=True, text=True, stderr=subprocess.DEVNULL
            ).stdout.strip()
            
            if diff_stat:
                import re
                insertions_match = re.search(r'(\d+) insertion', diff_stat)
                deletions_match = re.search(r'(\d+) deletion', diff_stat)
                
                if insertions_match:
                    stats['insertions'] += int(insertions_match.group(1))
                if deletions_match:
                    stats['deletions'] += int(deletions_match.group(1))
    
    except Exception as e:
        print(f"Error analyzing {repo_path}: {e}")
    
    os.chdir(original_dir)
    return stats

def categorize_repository(repo_stats):
    """Categorize repository based on name and content"""
    name = repo_stats['name'].lower()
    
    # Language learning
    if any(keyword in name for keyword in ['spanish', 'conjugat', 'subjunctive', 'hablas', 'vocab', 'langtool']):
        return 'Language Learning'
    
    # Portfolio/Personal
    if any(keyword in name for keyword in ['portfolio', 'brandon', 'lambert', 'personal']):
        return 'Portfolio/Personal'
    
    # Poetry/Creative
    if any(keyword in name for keyword in ['letratos', 'poetry', 'poem']):
        return 'Creative/Poetry'
    
    # Visualization
    if any(keyword in name for keyword in ['internet', 'map', 'visual', 'globe']):
        return 'Data Visualization'
    
    # Educational/Learning
    if any(keyword in name for keyword in ['algorithm', 'learn', 'teach', 'edu']):
        return 'Educational Tools'
    
    # Food/Nutrition
    if any(keyword in name for keyword in ['meal', 'nutri', 'food', 'pantry']):
        return 'Food/Nutrition'
    
    # Development Tools
    if any(keyword in name for keyword in ['anki', 'tool', 'generator', 'describe']):
        return 'Development Tools'
    
    # Archived
    if 'archive' in repo_stats['path']:
        return 'Archived Projects'
    
    return 'Other Projects'

def generate_comprehensive_report(all_stats):
    """Generate a comprehensive report of all repository activity"""
    report = []
    report.append("=" * 100)
    report.append("COMPLETE GitHub Activity Analysis - ALL Repositories (Public & Private)")
    report.append("=" * 100)
    report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Filter out empty repos
    active_stats = [s for s in all_stats if s and s['commits']]
    archived_stats = [s for s in all_stats if s and not s['commits'] and 'archive' in s['path']]
    
    # Overall statistics
    report.append("## OVERALL STATISTICS")
    report.append("-" * 50)
    total_repos = len(all_stats)
    active_repos = len(active_stats)
    total_commits = sum(len(s['commits']) for s in active_stats)
    total_insertions = sum(s['insertions'] for s in active_stats)
    total_deletions = sum(s['deletions'] for s in active_stats)
    all_authors = set()
    for s in active_stats:
        all_authors.update(s['authors'])
    
    report.append(f"Total Repositories Analyzed: {total_repos}")
    report.append(f"Active Repositories (with commits in last 30 days): {active_repos}")
    report.append(f"Archived/Inactive Repositories: {len(archived_stats)}")
    report.append(f"Total Commits: {total_commits}")
    report.append(f"Total Lines Added: {total_insertions:,}")
    report.append(f"Total Lines Deleted: {total_deletions:,}")
    report.append(f"Net Code Change: {total_insertions - total_deletions:+,} lines")
    report.append(f"Contributing Authors: {', '.join(all_authors)}")
    report.append("")
    
    # Categorize repositories
    categories = defaultdict(list)
    for stats in all_stats:
        if stats:
            category = categorize_repository(stats)
            categories[category].append(stats)
    
    report.append("## REPOSITORY CATEGORIES")
    report.append("-" * 50)
    for category, repos in sorted(categories.items()):
        active_in_category = sum(1 for r in repos if r['commits'])
        report.append(f"\n### {category} ({len(repos)} repos, {active_in_category} active)")
        
        for repo in sorted(repos, key=lambda x: len(x['commits']), reverse=True)[:5]:
            visibility = "🔒 Private" if repo['info']['is_private'] else "🌐 Public"
            commits_count = len(repo['commits'])
            if commits_count > 0:
                report.append(f"  • {repo['name']:<30} {visibility} - {commits_count} commits")
                if repo['info']['remote_url'] != 'local only':
                    report.append(f"    Remote: {repo['info']['remote_url']}")
    
    report.append("")
    
    # Active development details
    report.append("## ACTIVE DEVELOPMENT (Last 30 Days)")
    report.append("-" * 50)
    
    for stats in sorted(active_stats, key=lambda x: len(x['commits']), reverse=True):
        visibility = "🔒 Private" if stats['info']['is_private'] else "🌐 Public"
        report.append(f"\n### {stats['name']} {visibility}")
        report.append(f"  Path: {stats['path']}")
        report.append(f"  Commits: {len(stats['commits'])}")
        report.append(f"  Authors: {', '.join(stats['authors'])}")
        report.append(f"  Changes: +{stats['insertions']} / -{stats['deletions']} lines")
        report.append(f"  Files Modified: {len(stats['files_changed'])}")
        
        if stats['commits']:
            report.append("  Recent Activity:")
            for commit in stats['commits'][:3]:
                report.append(f"    • {commit['date']} - {commit['message'][:60]}")
    
    # Timeline analysis
    report.append("\n## ACTIVITY TIMELINE (All Repositories)")
    report.append("-" * 50)
    
    date_activity = defaultdict(lambda: {'commits': 0, 'repos': set()})
    for stats in active_stats:
        for commit in stats['commits']:
            date_activity[commit['date']]['commits'] += 1
            date_activity[commit['date']]['repos'].add(stats['name'])
    
    for date in sorted(date_activity.keys(), reverse=True)[:20]:
        data = date_activity[date]
        bar = '█' * min(data['commits'], 30)
        repos_list = ', '.join(list(data['repos'])[:3])
        if len(data['repos']) > 3:
            repos_list += f" +{len(data['repos']) - 3} more"
        report.append(f"  {date}: {bar} ({data['commits']} commits across {len(data['repos'])} repos)")
        report.append(f"           Repos: {repos_list}")
    
    # Archived repositories summary
    if archived_stats:
        report.append("\n## ARCHIVED REPOSITORIES")
        report.append("-" * 50)
        report.append(f"Total Archived: {len(archived_stats)}")
        for repo in archived_stats[:10]:
            report.append(f"  • {repo['name']}")
    
    report.append("")
    report.append("=" * 100)
    
    return "\n".join(report)

def main():
    print("Analyzing ALL local repositories (including private)...")
    
    # Define paths to check
    paths_to_check = [
        "C:\\Users\\brand\\Development\\Project_Workspace",
        "C:\\Users\\brand\\Development\\vocab_tool",
        "C:\\Users\\brand\\Development\\Project_Workspace\\archive"
    ]
    
    all_stats = []
    repos_analyzed = set()
    
    for base_path in paths_to_check:
        if os.path.exists(base_path):
            print(f"\nScanning {base_path}...")
            
            # Check if the path itself is a repo
            if os.path.exists(os.path.join(base_path, '.git')):
                if base_path not in repos_analyzed:
                    print(f"  Analyzing {os.path.basename(base_path)}...")
                    stats = analyze_repository(base_path)
                    if stats:
                        all_stats.append(stats)
                        repos_analyzed.add(base_path)
            
            # Check subdirectories
            if os.path.isdir(base_path):
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path) and item_path not in repos_analyzed:
                        if os.path.exists(os.path.join(item_path, '.git')):
                            print(f"  Analyzing {item}...")
                            stats = analyze_repository(item_path)
                            if stats:
                                all_stats.append(stats)
                                repos_analyzed.add(item_path)
    
    print(f"\nTotal repositories analyzed: {len(all_stats)}")
    
    # Generate report
    report = generate_comprehensive_report(all_stats)
    
    # Save report
    report_path = "C:\\Users\\brand\\Development\\bjpl_repos_analysis\\complete_github_activity.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nComplete report saved to: {report_path}")
    
    # Show summary
    active_count = sum(1 for s in all_stats if s and s['commits'])
    total_commits = sum(len(s['commits']) for s in all_stats if s)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    print(f"Total Repositories: {len(all_stats)}")
    print(f"Active Repositories: {active_count}")
    print(f"Total Commits (30 days): {total_commits}")
    print("=" * 50)

if __name__ == "__main__":
    main()