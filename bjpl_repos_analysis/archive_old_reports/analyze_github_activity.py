#!/usr/bin/env python3
"""
GitHub Activity Analysis for bjpl repositories
Analyzes the last month of development activity
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from collections import defaultdict
import urllib.request

def get_github_repos(username="bjpl"):
    """Fetch all public repositories for a user"""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                if not data:
                    break
                repos.extend(data)
                page += 1
        except Exception as e:
            print(f"Error fetching repos: {e}")
            break
    return repos

def analyze_local_repo(repo_path):
    """Analyze a local git repository"""
    if not os.path.exists(os.path.join(repo_path, '.git')):
        return None
    
    os.chdir(repo_path)
    
    # Get last month's date
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    stats = {
        'path': repo_path,
        'name': os.path.basename(repo_path),
        'commits': [],
        'files_changed': 0,
        'insertions': 0,
        'deletions': 0
    }
    
    try:
        # Get commit history
        commit_log = subprocess.run(
            ['git', 'log', f'--since={one_month_ago}', '--pretty=format:%H|%ad|%s|%an', '--date=short'],
            capture_output=True, text=True
        ).stdout.strip()
        
        if commit_log:
            for line in commit_log.split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        stats['commits'].append({
                            'hash': parts[0][:7],
                            'date': parts[1],
                            'message': parts[2],
                            'author': parts[3]
                        })
        
        # Get overall stats
        diff_stat = subprocess.run(
            ['git', 'diff', '--shortstat', f'{one_month_ago}..HEAD'],
            capture_output=True, text=True
        ).stdout.strip()
        
        if diff_stat:
            import re
            files_match = re.search(r'(\d+) files? changed', diff_stat)
            insertions_match = re.search(r'(\d+) insertions?', diff_stat)
            deletions_match = re.search(r'(\d+) deletions?', diff_stat)
            
            if files_match:
                stats['files_changed'] = int(files_match.group(1))
            if insertions_match:
                stats['insertions'] = int(insertions_match.group(1))
            if deletions_match:
                stats['deletions'] = int(deletions_match.group(1))
    
    except Exception as e:
        print(f"Error analyzing {repo_path}: {e}")
    
    return stats

def generate_summary_report(all_stats, github_repos):
    """Generate a comprehensive summary report"""
    report = []
    report.append("=" * 80)
    report.append("GitHub Activity Summary for bjpl - Last 30 Days")
    report.append("=" * 80)
    report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # GitHub Repository Overview
    report.append("## GITHUB REPOSITORIES OVERVIEW")
    report.append("-" * 40)
    
    active_repos = [r for r in github_repos if datetime.fromisoformat(r['updated_at'].replace('Z', '+00:00')) > datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=30)]
    
    report.append(f"Total Repositories: {len(github_repos)}")
    report.append(f"Active in Last Month: {len(active_repos)}")
    report.append("")
    
    report.append("### Recently Updated Repositories:")
    for repo in sorted(github_repos, key=lambda x: x['updated_at'], reverse=True)[:10]:
        updated = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        days_ago = (datetime.now(datetime.now().astimezone().tzinfo) - updated).days
        report.append(f"  • {repo['name']:<30} (Updated {days_ago} days ago)")
        if repo['description']:
            report.append(f"    {repo['description'][:70]}")
    
    report.append("")
    
    # Local Repository Analysis
    if all_stats:
        report.append("## LOCAL REPOSITORY ANALYSIS")
        report.append("-" * 40)
        
        total_commits = sum(len(s['commits']) for s in all_stats if s)
        total_insertions = sum(s['insertions'] for s in all_stats if s)
        total_deletions = sum(s['deletions'] for s in all_stats if s)
        
        report.append(f"Total Commits: {total_commits}")
        report.append(f"Total Lines Added: {total_insertions:,}")
        report.append(f"Total Lines Deleted: {total_deletions:,}")
        report.append(f"Net Change: {total_insertions - total_deletions:+,} lines")
        report.append("")
        
        # Activity by repository
        report.append("### Activity by Repository:")
        for stats in all_stats:
            if stats and stats['commits']:
                report.append(f"\n#### {stats['name']}")
                report.append(f"  Commits: {len(stats['commits'])}")
                report.append(f"  Changes: +{stats['insertions']} / -{stats['deletions']} lines")
                report.append("  Recent commits:")
                for commit in stats['commits'][:5]:
                    report.append(f"    • {commit['date']} - {commit['message'][:60]}")
        
        # Activity timeline
        report.append("\n### Activity Timeline:")
        date_activity = defaultdict(int)
        for stats in all_stats:
            if stats:
                for commit in stats['commits']:
                    date_activity[commit['date']] += 1
        
        for date in sorted(date_activity.keys(), reverse=True)[:15]:
            bar = '█' * min(date_activity[date], 20)
            report.append(f"  {date}: {bar} ({date_activity[date]} commits)")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    print("Fetching GitHub repository information...")
    github_repos = get_github_repos("bjpl")
    
    print(f"Found {len(github_repos)} repositories on GitHub")
    
    # Analyze local repositories
    base_path = "C:\\Users\\brand\\Development\\Project_Workspace"
    all_stats = []
    
    if os.path.exists(base_path):
        os.chdir(base_path)
        print(f"\nAnalyzing local repositories in {base_path}...")
        
        # Check current directory
        if os.path.exists('.git'):
            print("Analyzing current repository...")
            stats = analyze_local_repo('.')
            if stats:
                all_stats.append(stats)
        
        # Check subdirectories
        for item in os.listdir('.'):
            item_path = os.path.join('.', item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, '.git')):
                print(f"Analyzing {item}...")
                stats = analyze_local_repo(item_path)
                if stats:
                    all_stats.append(stats)
    
    # Generate report
    report = generate_summary_report(all_stats, github_repos)
    
    # Save report
    report_path = "C:\\Users\\brand\\Development\\bjpl_repos_analysis\\github_activity_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    print("\n" + "=" * 40)
    print("SUMMARY PREVIEW:")
    print("=" * 40)
    print(report[:2000] + "..." if len(report) > 2000 else report)

if __name__ == "__main__":
    main()