#!/usr/bin/env python3
"""
Git Repository Evolution Tracker
=================================
A standalone tool for tracking and visualizing the evolution of git repositories.
Built using Flow Nexus development environment, but runs independently.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import argparse
from collections import defaultdict, Counter
import re

try:
    from github import Github
    HAS_GITHUB = True
except ImportError:
    HAS_GITHUB = False
    print("Warning: PyGithub not installed. Some features limited.")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


class GitEvolutionTracker:
    """
    Standalone git repository evolution tracker.
    Analyzes repository history, patterns, and generates insights.
    """

    def __init__(self, workspace_path: str = None):
        """Initialize the tracker with optional workspace path."""
        if workspace_path:
            self.workspace_path = Path(workspace_path)
        else:
            self.workspace_path = Path.cwd() / "git_tracking"

        self.workspace_path.mkdir(exist_ok=True)
        self.data_dir = self.workspace_path / "data"
        self.reports_dir = self.workspace_path / "reports"
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Configuration
        self.github_username = "bjpl"
        self.analysis_depth = 100  # Number of commits to analyze

        print(f"📁 Workspace: {self.workspace_path}")

    def analyze_local_repo(self, repo_path: str) -> Dict:
        """Analyze a local git repository."""
        repo_path = Path(repo_path)
        if not (repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

        print(f"🔍 Analyzing local repository: {repo_path.name}")

        # Get repository info
        repo_info = {
            'name': repo_path.name,
            'path': str(repo_path),
            'type': 'local',
            'analysis_date': datetime.now().isoformat()
        }

        # Get commit history
        try:
            result = subprocess.run(
                ['git', 'log', '--format=%H|%ai|%an|%s', f'-{self.analysis_depth}'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            'hash': parts[0],
                            'date': parts[1],
                            'author': parts[2],
                            'message': parts[3]
                        })

            repo_info['total_commits'] = len(commits)
            repo_info['commits'] = commits

            # Analyze patterns
            repo_info['patterns'] = self._analyze_commit_patterns(commits)
            repo_info['timeline'] = self._create_timeline(commits)
            repo_info['insights'] = self._generate_insights(repo_info)

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error analyzing repository: {e}")
            repo_info['error'] = str(e)

        return repo_info

    def analyze_github_repos(self, username: str = None) -> List[Dict]:
        """Analyze GitHub repositories for a user."""
        username = username or self.github_username
        print(f"🌐 Fetching GitHub repositories for: {username}")

        if not HAS_GITHUB:
            # Fallback to API without library
            import urllib.request
            import json

            url = f"https://api.github.com/users/{username}/repos?per_page=100"
            try:
                with urllib.request.urlopen(url) as response:
                    repos = json.loads(response.read())
            except Exception as e:
                print(f"❌ Error fetching repos: {e}")
                return []
        else:
            g = Github()
            try:
                user = g.get_user(username)
                repos = list(user.get_repos())
            except Exception as e:
                print(f"❌ Error fetching repos: {e}")
                return []

        analyzed_repos = []
        for repo in repos:
            if isinstance(repo, dict):
                # Direct API response
                repo_data = {
                    'name': repo['name'],
                    'description': repo.get('description', ''),
                    'language': repo.get('language', 'Unknown'),
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'pushed_at': repo['pushed_at'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'open_issues': repo['open_issues_count']
                }
            else:
                # PyGithub object
                repo_data = {
                    'name': repo.name,
                    'description': repo.description or '',
                    'language': repo.language or 'Unknown',
                    'created_at': repo.created_at.isoformat(),
                    'updated_at': repo.updated_at.isoformat(),
                    'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'open_issues': repo.open_issues_count
                }

            # Calculate evolution metrics
            repo_data['evolution'] = self._calculate_evolution_metrics(repo_data)
            analyzed_repos.append(repo_data)

        return analyzed_repos

    def _analyze_commit_patterns(self, commits: List[Dict]) -> Dict:
        """Analyze patterns in commit history."""
        if not commits:
            return {}

        patterns = {
            'total': len(commits),
            'authors': Counter(),
            'daily_distribution': defaultdict(int),
            'hourly_distribution': defaultdict(int),
            'message_keywords': Counter(),
            'commit_types': Counter()
        }

        for commit in commits:
            # Author analysis
            patterns['authors'][commit['author']] += 1

            # Time analysis
            try:
                date = datetime.fromisoformat(commit['date'].replace(' ', 'T').split('+')[0])
                patterns['daily_distribution'][date.strftime('%A')] += 1
                patterns['hourly_distribution'][date.hour] += 1
            except:
                pass

            # Message analysis
            msg = commit['message'].lower()

            # Detect commit types
            if any(word in msg for word in ['fix', 'bug', 'patch']):
                patterns['commit_types']['fixes'] += 1
            elif any(word in msg for word in ['feat', 'feature', 'add', 'new']):
                patterns['commit_types']['features'] += 1
            elif any(word in msg for word in ['refactor', 'clean', 'improve']):
                patterns['commit_types']['refactoring'] += 1
            elif any(word in msg for word in ['doc', 'readme', 'comment']):
                patterns['commit_types']['documentation'] += 1
            elif any(word in msg for word in ['test', 'spec']):
                patterns['commit_types']['tests'] += 1
            else:
                patterns['commit_types']['other'] += 1

            # Extract keywords
            words = re.findall(r'\b[a-z]+\b', msg)
            for word in words:
                if len(word) > 4:  # Only meaningful words
                    patterns['message_keywords'][word] += 1

        # Convert to serializable format
        patterns['authors'] = dict(patterns['authors'].most_common(10))
        patterns['message_keywords'] = dict(patterns['message_keywords'].most_common(20))
        patterns['commit_types'] = dict(patterns['commit_types'])

        return patterns

    def _create_timeline(self, commits: List[Dict]) -> List[Dict]:
        """Create a timeline of significant events."""
        timeline = []

        if not commits:
            return timeline

        # First and last commits
        timeline.append({
            'date': commits[-1]['date'],
            'event': 'First Commit',
            'description': commits[-1]['message']
        })

        timeline.append({
            'date': commits[0]['date'],
            'event': 'Latest Commit',
            'description': commits[0]['message']
        })

        # Look for version releases
        for commit in commits:
            if re.search(r'v?\d+\.\d+\.\d+', commit['message']):
                timeline.append({
                    'date': commit['date'],
                    'event': 'Version Release',
                    'description': commit['message']
                })

        # Sort by date
        timeline.sort(key=lambda x: x['date'])

        return timeline

    def _calculate_evolution_metrics(self, repo_data: Dict) -> Dict:
        """Calculate evolution metrics for a repository."""
        metrics = {}

        # Age calculation
        created = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
        updated = datetime.fromisoformat(repo_data['updated_at'].replace('Z', '+00:00'))

        age_days = (datetime.now(created.tzinfo) - created).days
        days_since_update = (datetime.now(updated.tzinfo) - updated).days

        metrics['age_days'] = age_days
        metrics['days_since_update'] = days_since_update

        # Activity level
        if days_since_update < 7:
            metrics['activity_level'] = 'Very Active'
        elif days_since_update < 30:
            metrics['activity_level'] = 'Active'
        elif days_since_update < 90:
            metrics['activity_level'] = 'Moderate'
        elif days_since_update < 180:
            metrics['activity_level'] = 'Low'
        else:
            metrics['activity_level'] = 'Dormant'

        # Development stage
        if age_days < 30:
            metrics['stage'] = 'Inception'
        elif age_days < 180:
            metrics['stage'] = 'Early Development'
        elif age_days < 365:
            metrics['stage'] = 'Growing'
        elif days_since_update > 180:
            metrics['stage'] = 'Mature/Archived'
        else:
            metrics['stage'] = 'Established'

        # Evolution velocity
        if age_days > 0:
            metrics['evolution_velocity'] = round((age_days - days_since_update) / age_days, 2)
        else:
            metrics['evolution_velocity'] = 0

        return metrics

    def _generate_insights(self, repo_info: Dict) -> List[str]:
        """Generate insights from repository analysis."""
        insights = []

        if 'patterns' in repo_info:
            patterns = repo_info['patterns']

            # Author insights
            if patterns.get('authors'):
                top_author = max(patterns['authors'].items(), key=lambda x: x[1])
                insights.append(f"Top contributor: {top_author[0]} with {top_author[1]} commits")

            # Commit type insights
            if patterns.get('commit_types'):
                dominant_type = max(patterns['commit_types'].items(), key=lambda x: x[1])
                insights.append(f"Primary focus: {dominant_type[0]} ({dominant_type[1]} commits)")

            # Activity insights
            if patterns.get('daily_distribution'):
                most_active_day = max(patterns['daily_distribution'].items(), key=lambda x: x[1])
                insights.append(f"Most active day: {most_active_day[0]}")

        return insights

    def generate_html_report(self, analysis_data: Dict) -> str:
        """Generate an HTML report from analysis data."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Git Repository Evolution Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2d3748;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .repo-card {{
            background: #f7fafc;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-label {{
            color: #718096;
            font-size: 0.9em;
        }}
        .metric-value {{
            color: #2d3748;
            font-size: 1.2em;
            font-weight: bold;
        }}
        .insight {{
            background: #edf2f7;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }}
        .timeline-item {{
            border-left: 2px solid #cbd5e0;
            padding-left: 20px;
            margin-left: 10px;
            padding-bottom: 20px;
            position: relative;
        }}
        .timeline-item:before {{
            content: '';
            position: absolute;
            left: -5px;
            top: 0;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Git Repository Evolution Analysis</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""

        # Add repository analysis
        if 'repositories' in analysis_data:
            for repo in analysis_data['repositories']:
                html += f"""
        <div class="repo-card">
            <h2>{repo['name']}</h2>
            <p>{repo.get('description', 'No description')}</p>

            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Language</div>
                    <div class="metric-value">{repo.get('language', 'Unknown')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Stars</div>
                    <div class="metric-value">{repo.get('stars', 0)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Activity</div>
                    <div class="metric-value">{repo.get('evolution', {}).get('activity_level', 'Unknown')}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Stage</div>
                    <div class="metric-value">{repo.get('evolution', {}).get('stage', 'Unknown')}</div>
                </div>
            </div>
        </div>
"""

        html += """
    </div>
</body>
</html>"""

        return html

    def run_analysis(self, mode: str = 'github', target: str = None) -> Dict:
        """Run complete analysis based on mode."""
        print(f"🚀 Starting Git Evolution Analysis (mode: {mode})")

        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'mode': mode,
            'target': target or self.github_username
        }

        if mode == 'local':
            if not target:
                target = '.'
            analysis_results['repository'] = self.analyze_local_repo(target)

        elif mode == 'github':
            repos = self.analyze_github_repos(target)
            analysis_results['repositories'] = repos

            # Summary statistics
            if repos:
                analysis_results['summary'] = {
                    'total_repos': len(repos),
                    'languages': Counter(r['language'] for r in repos),
                    'activity_distribution': Counter(r['evolution']['activity_level'] for r in repos),
                    'total_stars': sum(r['stars'] for r in repos),
                    'total_forks': sum(r['forks'] for r in repos)
                }

        # Save results
        output_file = self.reports_dir / f"evolution_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, default=str)

        print(f"✅ Analysis complete! Results saved to: {output_file}")

        # Generate HTML report
        html_file = self.reports_dir / f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        html_content = self.generate_html_report(analysis_results)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📄 HTML report generated: {html_file}")

        return analysis_results


def main():
    """Main entry point with CLI."""
    parser = argparse.ArgumentParser(description='Git Repository Evolution Tracker')
    parser.add_argument('--mode', choices=['local', 'github'], default='github',
                       help='Analysis mode: local repo or GitHub repos')
    parser.add_argument('--target', help='Target repository path or GitHub username')
    parser.add_argument('--workspace', help='Workspace directory for output')

    args = parser.parse_args()

    # Create tracker
    tracker = GitEvolutionTracker(workspace_path=args.workspace)

    # Run analysis
    results = tracker.run_analysis(mode=args.mode, target=args.target)

    # Print summary
    if 'summary' in results:
        print("\n📊 Summary:")
        print(f"  Total Repositories: {results['summary']['total_repos']}")
        print(f"  Total Stars: {results['summary']['total_stars']}")
        print(f"  Total Forks: {results['summary']['total_forks']}")
        print("\n  Activity Distribution:")
        for level, count in results['summary']['activity_distribution'].items():
            print(f"    {level}: {count}")


if __name__ == "__main__":
    main()