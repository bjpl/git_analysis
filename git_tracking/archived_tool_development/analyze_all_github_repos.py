#!/usr/bin/env python3
"""
GitHub All Repositories Analyzer
=================================
Analyzes ALL repositories (public and private) from a GitHub account.
Clones/updates repos locally and generates comprehensive reports.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse
import getpass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.enhanced_evolution_tracker import EnhancedEvolutionTracker
from core.security import SecureConfigManager, InputValidator, CommandSanitizer


class GitHubAllReposAnalyzer:
    """Analyze all GitHub repositories for a user/organization."""

    def __init__(self, username: str, token: Optional[str] = None, workspace: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            username: GitHub username or organization
            token: GitHub personal access token (for private repos)
            workspace: Directory to clone/analyze repos (default: ./github_repos)
        """
        # Validate username
        self.validator = InputValidator()
        self.username = self.validator.validate_username(username)

        # Set up secure token management
        self.config_manager = SecureConfigManager()
        self.command_sanitizer = CommandSanitizer()

        # Use provided token or retrieve from secure storage
        if token:
            self.config_manager.store_token('github', token)
            self.token = token
        else:
            self.token = self.config_manager.get_token('github') or os.environ.get('GITHUB_TOKEN')
        self.workspace = Path(workspace) if workspace else Path.cwd() / 'github_repos'
        self.workspace.mkdir(exist_ok=True)

        # Create subdirectories
        self.repos_dir = self.workspace / 'repositories'
        self.reports_dir = self.workspace / 'reports'
        self.repos_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Store results
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'repositories': [],
            'summary': {}
        }

    def fetch_all_repos(self) -> List[Dict]:
        """Fetch all repositories from GitHub API."""
        print(f"\n🔍 Fetching all repositories for {self.username}...")

        repos = []
        page = 1

        while True:
            # Use GitHub CLI or curl to fetch repos
            if self._has_gh_cli():
                repos_batch = self._fetch_with_gh_cli(page)
            else:
                repos_batch = self._fetch_with_curl(page)

            if not repos_batch:
                break

            repos.extend(repos_batch)
            page += 1

            # GitHub API returns max 100 per page
            if len(repos_batch) < 100:
                break

        print(f"✅ Found {len(repos)} repositories")

        # Separate public and private
        public_repos = [r for r in repos if not r.get('private', False)]
        private_repos = [r for r in repos if r.get('private', False)]

        print(f"   📂 Public: {len(public_repos)}")
        print(f"   🔒 Private: {len(private_repos)}")

        return repos

    def _has_gh_cli(self) -> bool:
        """Check if GitHub CLI is available."""
        try:
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def _fetch_with_gh_cli(self, page: int) -> List[Dict]:
        """Fetch repositories using GitHub CLI."""
        try:
            cmd = [
                'gh', 'repo', 'list', self.username,
                '--limit', '100',
                '--json', 'name,description,url,isPrivate,isFork,isArchived,language,updatedAt,createdAt,defaultBranch',
                '--page', str(page)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if result.stdout:
                repos = json.loads(result.stdout)
                # Transform to match expected format
                return [{
                    'name': r['name'],
                    'full_name': f"{self.username}/{r['name']}",
                    'description': r.get('description', ''),
                    'html_url': r['url'],
                    'clone_url': r['url'] + '.git',
                    'private': r.get('isPrivate', False),
                    'fork': r.get('isFork', False),
                    'archived': r.get('isArchived', False),
                    'language': r.get('language', ''),
                    'updated_at': r.get('updatedAt', ''),
                    'created_at': r.get('createdAt', ''),
                    'default_branch': r.get('defaultBranch', 'main')
                } for r in repos]
            return []
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error fetching with gh CLI: {e}")
            return []

    def _fetch_with_curl(self, page: int) -> List[Dict]:
        """Fetch repositories using curl (requires token for private repos)."""
        try:
            url = f"https://api.github.com/users/{self.username}/repos?per_page=100&page={page}"

            cmd = ['curl', '-s']
            if self.token:
                cmd.extend(['-H', f'Authorization: token {self.token}'])
            cmd.append(url)

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if result.stdout:
                repos = json.loads(result.stdout)
                if isinstance(repos, list):
                    return repos
            return []
        except Exception as e:
            print(f"⚠️  Error fetching with curl: {e}")
            return []

    def clone_or_update_repo(self, repo: Dict) -> Optional[Path]:
        """Clone or update a repository."""
        repo_name = repo['name']
        repo_path = self.repos_dir / repo_name

        try:
            if repo_path.exists():
                # Update existing repo
                print(f"   📥 Updating {repo_name}...")
                subprocess.run(
                    ['git', 'pull', '--quiet'],
                    cwd=repo_path,
                    capture_output=True,
                    check=True
                )
            else:
                # Clone new repo
                print(f"   📦 Cloning {repo_name}...")
                clone_url = repo['clone_url']

                # Use token for private repos if available
                if repo.get('private') and self.token:
                    # Insert token into URL
                    clone_url = clone_url.replace('https://', f'https://{self.token}@')

                subprocess.run(
                    ['git', 'clone', '--quiet', clone_url, str(repo_path)],
                    capture_output=True,
                    check=True
                )

            return repo_path

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to clone/update {repo_name}: {e}")
            return None

    def analyze_repository(self, repo: Dict, repo_path: Path) -> Dict:
        """Analyze a single repository."""
        print(f"\n🔬 Analyzing {repo['name']}...")

        try:
            # Use Enhanced Evolution Tracker
            tracker = EnhancedEvolutionTracker(str(repo_path))
            analysis = tracker.analyze_repository()

            # Add GitHub metadata
            analysis['github_metadata'] = {
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description', ''),
                'url': repo['html_url'],
                'private': repo.get('private', False),
                'fork': repo.get('fork', False),
                'archived': repo.get('archived', False),
                'language': repo.get('language', ''),
                'created_at': repo.get('created_at', ''),
                'updated_at': repo.get('updated_at', '')
            }

            # Generate individual report
            report_path = self.reports_dir / f"{repo['name']}_report.html"
            tracker.generate_html_report(analysis, str(report_path))

            return {
                'success': True,
                'repository': repo['name'],
                'analysis': analysis,
                'report_path': str(report_path)
            }

        except Exception as e:
            print(f"   ⚠️  Error analyzing {repo['name']}: {e}")
            return {
                'success': False,
                'repository': repo['name'],
                'error': str(e)
            }

    def generate_combined_report(self, analyses: List[Dict]):
        """Generate a combined report for all repositories."""
        print("\n📊 Generating combined report...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.reports_dir / f'all_repos_report_{timestamp}.html'

        # Calculate aggregate statistics
        total_repos = len(analyses)
        successful_analyses = [a for a in analyses if a.get('success')]
        failed_analyses = [a for a in analyses if not a.get('success')]

        # Aggregate health scores
        health_scores = []
        total_commits = 0
        total_contributors = set()
        languages = {}

        for analysis in successful_analyses:
            repo_analysis = analysis.get('analysis', {})

            # Health score
            health = repo_analysis.get('health_score', {})
            if health.get('overall_score'):
                health_scores.append(health['overall_score'])

            # Commits
            commit_analysis = repo_analysis.get('commit_analysis', {})
            stats = commit_analysis.get('statistics', {})
            total_commits += stats.get('total', 0)

            # Contributors
            contributors = repo_analysis.get('contributor_metrics', {})
            for contrib in contributors.get('top_contributors', []):
                total_contributors.add(contrib.get('name', 'Unknown'))

            # Languages
            github_meta = repo_analysis.get('github_metadata', {})
            lang = github_meta.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0

        # Generate HTML
        html_content = self._generate_combined_html(
            total_repos=total_repos,
            successful=len(successful_analyses),
            failed=len(failed_analyses),
            avg_health=avg_health,
            total_commits=total_commits,
            total_contributors=len(total_contributors),
            languages=languages,
            analyses=successful_analyses
        )

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Combined report generated: {report_path}")

        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open(f'file://{report_path.absolute()}')
        except:
            pass

        return str(report_path)

    def _generate_combined_html(self, **kwargs) -> str:
        """Generate combined HTML report."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub All Repositories Analysis - {self.username}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .summary-card .value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #2d3748;
            margin: 10px 0;
        }}

        .summary-card .label {{
            color: #718096;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }}

        .repos-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .repo-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .repo-card:hover {{
            transform: translateY(-5px);
        }}

        .repo-card h3 {{
            color: #2d3748;
            margin-bottom: 10px;
        }}

        .repo-card a {{
            color: #667eea;
            text-decoration: none;
        }}

        .repo-card a:hover {{
            text-decoration: underline;
        }}

        .health-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 10px;
        }}

        .health-excellent {{
            background: #d4f4dd;
            color: #22543d;
        }}

        .health-good {{
            background: #bee3f8;
            color: #2c5282;
        }}

        .health-fair {{
            background: #feebc8;
            color: #7c2d12;
        }}

        .health-poor {{
            background: #fed7d7;
            color: #742a2a;
        }}

        .private-badge {{
            background: #805ad5;
            color: white;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 0.8rem;
            margin-left: 10px;
        }}

        .language-chart {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}

        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GitHub Repository Analysis</h1>
            <p style="color: #718096; font-size: 1.2rem;">
                Complete analysis of all repositories for <strong>@{self.username}</strong>
            </p>
            <p style="color: #a0aec0; margin-top: 10px;">
                Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="label">Total Repositories</div>
                <div class="value">{kwargs['total_repos']}</div>
            </div>

            <div class="summary-card">
                <div class="label">Successfully Analyzed</div>
                <div class="value" style="color: #48bb78">{kwargs['successful']}</div>
            </div>

            <div class="summary-card">
                <div class="label">Average Health</div>
                <div class="value" style="color: {'#48bb78' if kwargs['avg_health'] >= 70 else '#f6ad55' if kwargs['avg_health'] >= 50 else '#fc8181'}">{kwargs['avg_health']:.1f}</div>
            </div>

            <div class="summary-card">
                <div class="label">Total Commits</div>
                <div class="value">{kwargs['total_commits']:,}</div>
            </div>

            <div class="summary-card">
                <div class="label">Contributors</div>
                <div class="value">{kwargs['total_contributors']}</div>
            </div>

            <div class="summary-card">
                <div class="label">Languages</div>
                <div class="value">{len(kwargs['languages'])}</div>
            </div>
        </div>

        <div class="language-chart">
            <h2 style="color: #2d3748; margin-bottom: 20px;">Language Distribution</h2>
            <div class="chart-container">
                <canvas id="languageChart"></canvas>
            </div>
        </div>

        <h2 style="color: white; margin-bottom: 20px;">Repository Details</h2>
        <div class="repos-grid">
            {self._generate_repo_cards(kwargs['analyses'])}
        </div>
    </div>

    <script>
        // Language distribution chart
        const ctx = document.getElementById('languageChart').getContext('2d');
        const languages = {json.dumps(kwargs['languages'])};

        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(languages),
                datasets: [{{
                    data: Object.values(languages),
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c',
                        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
                        '#fa709a', '#fee140', '#30cfd0', '#330867'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

    def _generate_repo_cards(self, analyses: List[Dict]) -> str:
        """Generate repository cards HTML."""
        cards = []

        for analysis in analyses:
            repo_analysis = analysis.get('analysis', {})
            github_meta = repo_analysis.get('github_metadata', {})
            health = repo_analysis.get('health_score', {})

            health_score = health.get('overall_score', 0)
            health_class = (
                'health-excellent' if health_score >= 80 else
                'health-good' if health_score >= 60 else
                'health-fair' if health_score >= 40 else
                'health-poor'
            )

            private_badge = '<span class="private-badge">PRIVATE</span>' if github_meta.get('private') else ''

            cards.append(f'''
            <div class="repo-card">
                <h3>
                    <a href="{github_meta.get('url', '#')}" target="_blank">{github_meta.get('name', 'Unknown')}</a>
                    {private_badge}
                </h3>
                <p style="color: #718096; margin: 10px 0;">
                    {(github_meta.get('description', 'No description') or 'No description')[:100]}
                </p>
                <div style="color: #a0aec0; font-size: 0.9rem;">
                    <div>📝 Language: {github_meta.get('language', 'Unknown')}</div>
                    <div>📅 Created: {github_meta.get('created_at', 'Unknown')[:10]}</div>
                    <div>🔄 Updated: {github_meta.get('updated_at', 'Unknown')[:10]}</div>
                </div>
                <div class="health-badge {health_class}">
                    Health Score: {health_score:.0f}/100
                </div>
                <div style="margin-top: 15px;">
                    <a href="file://{analysis.get('report_path', '')}" style="color: #667eea; font-size: 0.9rem;">
                        📊 View Detailed Report →
                    </a>
                </div>
            </div>
            ''')

        return ''.join(cards)

    def run(self, skip_clone: bool = False):
        """Run the complete analysis."""
        print(f"🚀 GitHub All Repositories Analyzer")
        print(f"=" * 50)
        print(f"👤 User: {self.username}")
        print(f"📁 Workspace: {self.workspace}")
        print(f"🔐 Token: {'Configured' if self.token else 'Not configured (public repos only)'}")
        print(f"=" * 50)

        # Fetch all repositories
        repos = self.fetch_all_repos()

        if not repos:
            print("❌ No repositories found")
            return

        # Clone/update and analyze each repository
        analyses = []

        for i, repo in enumerate(repos, 1):
            print(f"\n[{i}/{len(repos)}] Processing {repo['name']}...")

            # Skip cloning if requested (useful for testing)
            if skip_clone:
                repo_path = self.repos_dir / repo['name']
                if not repo_path.exists():
                    print(f"   ⚠️  Skipping {repo['name']} - not cloned")
                    continue
            else:
                repo_path = self.clone_or_update_repo(repo)
                if not repo_path:
                    continue

            # Analyze repository
            analysis = self.analyze_repository(repo, repo_path)
            analyses.append(analysis)

        # Generate combined report
        if analyses:
            report_path = self.generate_combined_report(analyses)

            print(f"\n" + "=" * 50)
            print(f"✅ Analysis Complete!")
            print(f"📊 Analyzed: {len(analyses)} repositories")
            print(f"📄 Report: {report_path}")
            print(f"=" * 50)
        else:
            print("\n❌ No repositories were analyzed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze all GitHub repositories (public and private)'
    )

    parser.add_argument(
        'username',
        nargs='?',
        default='bjpl',
        help='GitHub username or organization (default: bjpl)'
    )

    parser.add_argument(
        '--token',
        help='GitHub personal access token (for private repos)'
    )

    parser.add_argument(
        '--token-env',
        default='GITHUB_TOKEN',
        help='Environment variable containing GitHub token (default: GITHUB_TOKEN)'
    )

    parser.add_argument(
        '--workspace',
        help='Directory to clone/analyze repos (default: ./github_repos)'
    )

    parser.add_argument(
        '--skip-clone',
        action='store_true',
        help='Skip cloning/updating repos (analyze existing only)'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Prompt for token interactively (secure)'
    )

    args = parser.parse_args()

    # Get token
    token = args.token

    if not token and args.interactive:
        print("🔐 Enter GitHub Personal Access Token (for private repos)")
        print("   Create one at: https://github.com/settings/tokens")
        print("   Required scopes: repo (for private repos)")
        token = getpass.getpass("Token: ")
    elif not token:
        # Try environment variable
        token = os.environ.get(args.token_env)

    # Create analyzer and run
    analyzer = GitHubAllReposAnalyzer(
        username=args.username,
        token=token,
        workspace=args.workspace
    )

    analyzer.run(skip_clone=args.skip_clone)


if __name__ == "__main__":
    main()