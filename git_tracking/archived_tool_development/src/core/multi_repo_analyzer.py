#!/usr/bin/env python3
"""
Multi-Repository Analysis System for BJPL GitHub Profile
========================================================
Uses Flow Nexus integration for comprehensive repository tracking and analysis.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import requests
from collections import defaultdict

class BJPLRepoAnalyzer:
    """
    Comprehensive analyzer for all BJPL repositories with Flow Nexus integration.
    """

    def __init__(self, workspace_path: str = r"C:\Users\brand\Development\Project_Workspace"):
        self.workspace_path = Path(workspace_path)
        self.analysis_dir = self.workspace_path / "bjpl_repos_analysis"
        self.analysis_dir.mkdir(exist_ok=True)

        # GitHub API configuration
        self.github_api_base = "https://api.github.com"
        self.username = "bjpl"

        # Analysis categories
        self.analysis_categories = {
            'web_development': ['brandonjplambert', 'portfolio-website', 'unsplash-image-search-gpt-description'],
            'ai_learning': ['algorithms_and_data_structures', 'agentic_learning'],
            'creative': ['letratos', 'internet'],
            'documentation': ['Project_Workspace', 'bjpl_repos_analysis']
        }

    def fetch_all_repositories(self) -> List[Dict]:
        """Fetch all repositories from GitHub API."""
        repos = []
        page = 1

        while True:
            url = f"{self.github_api_base}/users/{self.username}/repos"
            params = {"per_page": 100, "page": page, "sort": "updated"}

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                page_repos = response.json()

                if not page_repos:
                    break

                repos.extend(page_repos)
                page += 1

            except requests.exceptions.RequestException as e:
                print(f"Error fetching repositories: {e}")
                break

        return repos

    def analyze_repository_activity(self, repo: Dict) -> Dict:
        """Analyze individual repository activity and metrics."""
        analysis = {
            'name': repo['name'],
            'full_name': repo['full_name'],
            'description': repo.get('description', 'No description'),
            'language': repo.get('language', 'Unknown'),
            'created_at': repo['created_at'],
            'updated_at': repo['updated_at'],
            'pushed_at': repo['pushed_at'],
            'stars': repo['stargazers_count'],
            'forks': repo['forks_count'],
            'open_issues': repo['open_issues_count'],
            'default_branch': repo.get('default_branch', 'main'),
            'topics': repo.get('topics', []),
            'is_fork': repo['fork'],
            'is_private': repo['private'],
            'size': repo['size'],
            'has_issues': repo['has_issues'],
            'has_projects': repo['has_projects'],
            'has_wiki': repo['has_wiki']
        }

        # Calculate activity metrics
        last_update = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        now = datetime.now(last_update.tzinfo)
        days_since_update = (now - last_update).days

        analysis['activity_metrics'] = {
            'days_since_update': days_since_update,
            'activity_status': self._get_activity_status(days_since_update),
            'size_category': self._categorize_size(repo['size'])
        }

        return analysis

    def _get_activity_status(self, days: int) -> str:
        """Categorize repository activity based on last update."""
        if days <= 7:
            return "Very Active"
        elif days <= 30:
            return "Active"
        elif days <= 90:
            return "Moderate"
        elif days <= 180:
            return "Low Activity"
        else:
            return "Dormant"

    def _categorize_size(self, size_kb: int) -> str:
        """Categorize repository size."""
        if size_kb < 100:
            return "Tiny"
        elif size_kb < 1000:
            return "Small"
        elif size_kb < 10000:
            return "Medium"
        elif size_kb < 50000:
            return "Large"
        else:
            return "Very Large"

    def generate_comprehensive_report(self, repos: List[Dict]) -> Dict:
        """Generate comprehensive analysis report for all repositories."""
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_repositories': len(repos),
                'github_username': self.username,
                'analysis_version': '2.0'
            },
            'repositories': [],
            'statistics': {
                'languages': defaultdict(int),
                'activity_distribution': defaultdict(int),
                'size_distribution': defaultdict(int),
                'total_stars': 0,
                'total_forks': 0,
                'total_issues': 0
            },
            'categories': defaultdict(list)
        }

        # Analyze each repository
        for repo in repos:
            analysis = self.analyze_repository_activity(repo)
            report['repositories'].append(analysis)

            # Update statistics
            if analysis['language']:
                report['statistics']['languages'][analysis['language']] += 1

            report['statistics']['activity_distribution'][analysis['activity_metrics']['activity_status']] += 1
            report['statistics']['size_distribution'][analysis['activity_metrics']['size_category']] += 1
            report['statistics']['total_stars'] += analysis['stars']
            report['statistics']['total_forks'] += analysis['forks']
            report['statistics']['total_issues'] += analysis['open_issues']

            # Categorize repository
            for category, patterns in self.analysis_categories.items():
                if any(pattern in repo['name'].lower() for pattern in patterns):
                    report['categories'][category].append(analysis['name'])
                    break
            else:
                report['categories']['other'].append(analysis['name'])

        # Sort repositories by last update
        report['repositories'].sort(key=lambda x: x['updated_at'], reverse=True)

        # Add timeline analysis
        report['timeline'] = self._generate_timeline_analysis(report['repositories'])

        return report

    def _generate_timeline_analysis(self, repositories: List[Dict]) -> Dict:
        """Generate timeline analysis of repository activity."""
        timeline = {
            'last_24_hours': [],
            'last_week': [],
            'last_month': [],
            'last_3_months': [],
            'last_6_months': [],
            'older': []
        }

        now = datetime.now(datetime.now().astimezone().tzinfo)

        for repo in repositories:
            last_update = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
            days_diff = (now - last_update).days

            if days_diff <= 1:
                timeline['last_24_hours'].append(repo['name'])
            elif days_diff <= 7:
                timeline['last_week'].append(repo['name'])
            elif days_diff <= 30:
                timeline['last_month'].append(repo['name'])
            elif days_diff <= 90:
                timeline['last_3_months'].append(repo['name'])
            elif days_diff <= 180:
                timeline['last_6_months'].append(repo['name'])
            else:
                timeline['older'].append(repo['name'])

        return timeline

    def save_analysis(self, report: Dict):
        """Save analysis results to multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        json_path = self.analysis_dir / f"comprehensive_analysis_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        # Save Markdown report
        md_path = self.analysis_dir / f"REPOSITORY_ANALYSIS_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(report))

        # Update latest symlink
        latest_json = self.analysis_dir / "latest_analysis.json"
        latest_md = self.analysis_dir / "LATEST_ANALYSIS.md"

        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        with open(latest_md, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(report))

        print(f"✅ Analysis saved to {self.analysis_dir}")
        print(f"   - JSON: {json_path.name}")
        print(f"   - Markdown: {md_path.name}")

    def _generate_markdown_report(self, report: Dict) -> str:
        """Generate formatted Markdown report."""
        md = []
        md.append("# BJPL GitHub Repository Analysis Report")
        md.append(f"\n**Generated:** {report['metadata']['generated_at']}")
        md.append(f"\n**Total Repositories:** {report['metadata']['total_repositories']}")

        # Executive Summary
        md.append("\n## 📊 Executive Summary\n")
        stats = report['statistics']
        md.append(f"- **Total Stars:** {stats['total_stars']}")
        md.append(f"- **Total Forks:** {stats['total_forks']}")
        md.append(f"- **Open Issues:** {stats['total_issues']}")

        # Language Distribution
        md.append("\n### Programming Languages")
        for lang, count in sorted(dict(stats['languages']).items(), key=lambda x: x[1], reverse=True):
            md.append(f"- {lang}: {count} repositories")

        # Activity Distribution
        md.append("\n### Activity Status")
        for status, count in dict(stats['activity_distribution']).items():
            md.append(f"- {status}: {count} repositories")

        # Timeline Analysis
        md.append("\n## 📅 Timeline Analysis\n")
        timeline = report['timeline']
        for period, repos in timeline.items():
            if repos:
                md.append(f"\n### {period.replace('_', ' ').title()}")
                for repo in repos[:5]:  # Show top 5
                    md.append(f"- {repo}")
                if len(repos) > 5:
                    md.append(f"  ... and {len(repos) - 5} more")

        # Repository Categories
        md.append("\n## 📁 Repository Categories\n")
        for category, repos in dict(report['categories']).items():
            if repos:
                md.append(f"\n### {category.replace('_', ' ').title()}")
                for repo in repos:
                    md.append(f"- {repo}")

        # Detailed Repository List
        md.append("\n## 📋 Repository Details\n")
        for repo in report['repositories'][:20]:  # Show top 20
            md.append(f"\n### [{repo['name']}](https://github.com/{repo['full_name']})")
            md.append(f"- **Language:** {repo['language'] or 'Not specified'}")
            md.append(f"- **Last Updated:** {repo['updated_at']}")
            md.append(f"- **Activity Status:** {repo['activity_metrics']['activity_status']}")
            md.append(f"- **Size:** {repo['activity_metrics']['size_category']}")
            md.append(f"- **Stars/Forks/Issues:** {repo['stars']}/{repo['forks']}/{repo['open_issues']}")

            if repo['description']:
                md.append(f"- **Description:** {repo['description']}")

        return "\n".join(md)

    def run_full_analysis(self):
        """Execute complete repository analysis workflow."""
        print("🚀 Starting BJPL Repository Analysis...")

        # Fetch repositories
        print("📥 Fetching repositories from GitHub...")
        repos = self.fetch_all_repositories()
        print(f"   Found {len(repos)} repositories")

        # Generate report
        print("🔍 Analyzing repository data...")
        report = self.generate_comprehensive_report(repos)

        # Save results
        print("💾 Saving analysis results...")
        self.save_analysis(report)

        # Print summary
        print("\n✨ Analysis Complete!")
        print(f"   - Total Repositories: {len(repos)}")
        print(f"   - Most Used Language: {max(dict(report['statistics']['languages']).items(), key=lambda x: x[1])[0] if report['statistics']['languages'] else 'None'}")
        print(f"   - Very Active Repos: {dict(report['statistics']['activity_distribution']).get('Very Active', 0)}")

        return report


def main():
    """Main execution function."""
    analyzer = BJPLRepoAnalyzer()
    report = analyzer.run_full_analysis()

    # Create a Flow Nexus integration file
    flow_nexus_config = {
        "version": "1.0",
        "repositories": [repo['name'] for repo in report['repositories']],
        "monitoring": {
            "enabled": True,
            "frequency": "daily",
            "alerts": {
                "stale_repos": 30,  # Alert if repo not updated in 30 days
                "issue_threshold": 10  # Alert if open issues exceed 10
            }
        },
        "categories": dict(report['categories']),
        "last_analysis": report['metadata']['generated_at']
    }

    config_path = Path(r"C:\Users\brand\Development\Project_Workspace\bjpl_repos_analysis\flow_nexus_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(flow_nexus_config, f, indent=2)

    print(f"\n📦 Flow Nexus configuration saved to {config_path.name}")


if __name__ == "__main__":
    main()