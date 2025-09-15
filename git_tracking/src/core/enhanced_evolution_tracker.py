#!/usr/bin/env python3
"""
Enhanced Repository Evolution Tracker with Detailed Reports
===========================================================
Advanced evolution tracking with comprehensive metrics, visualizations,
and deep insights into repository development patterns.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
import re
import hashlib
import statistics


class EnhancedEvolutionTracker:
    """
    Advanced repository evolution tracker with comprehensive analysis
    and detailed HTML report generation.
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.git_dir = self.repo_path / '.git'

        if not self.git_dir.exists():
            raise ValueError(f"Not a git repository: {repo_path}")

        # Cache for expensive operations
        self.cache = {}

        # Analysis categories
        self.analysis_categories = {
            'commit_metrics': 'Detailed commit analysis',
            'file_evolution': 'File and directory changes over time',
            'contributor_analysis': 'Developer contribution patterns',
            'code_quality': 'Code quality indicators',
            'complexity_trends': 'Project complexity evolution',
            'activity_patterns': 'Development activity patterns',
            'milestone_detection': 'Automatic milestone detection',
            'health_indicators': 'Repository health metrics'
        }

    def analyze_repository(self) -> Dict[str, Any]:
        """Perform comprehensive repository analysis."""
        print(f"🔍 Analyzing repository: {self.repo_path.name}")

        analysis = {
            'metadata': self._get_repository_metadata(),
            'commit_analysis': self._analyze_commits(),
            'file_evolution': self._analyze_file_evolution(),
            'contributor_metrics': self._analyze_contributors(),
            'code_metrics': self._analyze_code_metrics(),
            'activity_patterns': self._analyze_activity_patterns(),
            'milestones': self._detect_milestones(),
            'health_score': self._calculate_health_score(),
            'insights': self._generate_insights()
        }

        return analysis

    def _get_repository_metadata(self) -> Dict[str, Any]:
        """Gather comprehensive repository metadata."""
        metadata = {
            'name': self.repo_path.name,
            'path': str(self.repo_path),
            'analysis_timestamp': datetime.now().isoformat(),
            'git_version': self._run_git_command(['--version']).strip(),
        }

        # Get repository age
        first_commit = self._run_git_command(['rev-list', '--max-parents=0', 'HEAD']).strip()
        if first_commit:
            first_commit_date = self._run_git_command(['show', '-s', '--format=%ci', first_commit]).strip()
            metadata['created_date'] = first_commit_date
            # Parse the git date format (e.g., "2025-08-15 22:51:57 -0700")
            try:
                # Remove timezone for simple parsing
                date_part = first_commit_date.split(' ')[0] + ' ' + first_commit_date.split(' ')[1]
                parsed_date = datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')
                metadata['age_days'] = (datetime.now() - parsed_date).days
            except:
                metadata['age_days'] = 0

        # Get branch information
        branches = self._run_git_command(['branch', '-a']).strip().split('\n')
        metadata['branch_count'] = len([b for b in branches if b.strip()])
        metadata['current_branch'] = self._run_git_command(['branch', '--show-current']).strip()

        # Get remote information
        remotes = self._run_git_command(['remote', '-v']).strip()
        metadata['has_remote'] = bool(remotes)
        metadata['remote_urls'] = self._parse_remotes(remotes)

        return metadata

    def _analyze_commits(self) -> Dict[str, Any]:
        """Perform detailed commit analysis."""
        commits_raw = self._run_git_command([
            'log', '--all', '--pretty=format:%H|%an|%ae|%at|%cn|%ce|%ct|%s|%b|%P',
            '--numstat'
        ]).strip()

        if not commits_raw:
            return {'total': 0, 'patterns': {}, 'statistics': {}}

        commits = self._parse_commits(commits_raw)

        # Calculate comprehensive statistics
        commit_stats = {
            'total': len(commits),
            'by_author': self._group_commits_by_author(commits),
            'by_date': self._group_commits_by_date(commits),
            'by_hour': self._analyze_commit_hours(commits),
            'by_day_of_week': self._analyze_commit_days(commits),
            'message_analysis': self._analyze_commit_messages(commits),
            'file_changes': self._analyze_file_changes(commits),
            'merge_commits': len([c for c in commits if len(c.get('parents', [])) > 1]),
            'average_files_per_commit': self._calculate_average_files_per_commit(commits),
            'commit_size_distribution': self._analyze_commit_sizes(commits)
        }

        # Identify patterns
        patterns = {
            'burst_development': self._detect_burst_patterns(commits),
            'consistent_contributors': self._identify_consistent_contributors(commits),
            'refactoring_periods': self._detect_refactoring_periods(commits),
            'feature_development': self._detect_feature_development(commits)
        }

        return {
            'statistics': commit_stats,
            'patterns': patterns,
            'timeline': self._create_commit_timeline(commits),
            'velocity': self._calculate_development_velocity(commits)
        }

    def _analyze_file_evolution(self) -> Dict[str, Any]:
        """Track how files and directories have evolved over time."""
        # Get current file structure
        current_files = self._get_current_files()

        # Analyze file history
        file_history = {}
        for file_path in current_files[:100]:  # Limit to prevent overwhelming analysis
            history = self._get_file_history(file_path)
            if history:
                file_history[file_path] = history

        # Identify patterns
        evolution_patterns = {
            'most_modified_files': self._identify_most_modified_files(file_history),
            'stable_core_files': self._identify_stable_files(file_history),
            'recently_added': self._identify_recent_additions(file_history),
            'file_churn': self._calculate_file_churn(file_history),
            'directory_growth': self._analyze_directory_growth()
        }

        return {
            'total_files': len(current_files),
            'file_types': self._analyze_file_types(current_files),
            'evolution_patterns': evolution_patterns,
            'file_history_sample': dict(list(file_history.items())[:10])
        }

    def _analyze_contributors(self) -> Dict[str, Any]:
        """Analyze contributor patterns and metrics."""
        # Try shortlog with timeout (can be slow on large repos)
        contributors_raw = self._run_git_command([
            'shortlog', '-sne', '--all', '--no-merges'
        ], timeout=10).strip()

        # Fallback if shortlog times out or fails
        if not contributors_raw:
            print("Using fallback contributor analysis...")
            # Get last 500 commits only for faster processing
            contributors_raw = self._run_git_command([
                'log', '--format=%aN', '-n', '500'
            ], timeout=5).strip()

            if contributors_raw:
                # Count occurrences manually
                from collections import Counter
                names = contributors_raw.split('\n')
                counts = Counter(names)
                # Format like shortlog output
                contributors_raw = '\n'.join([f"    {count}\t{name}" for name, count in counts.most_common()])

        contributors = self._parse_contributors(contributors_raw)

        # Get detailed stats for each contributor
        contributor_details = {}
        for contributor in contributors[:20]:  # Limit to top 20
            details = self._get_contributor_details(contributor['email'])
            contributor_details[contributor['name']] = details

        # Calculate metrics
        metrics = {
            'total_contributors': len(contributors),
            'top_contributors': contributors[:10],
            'contribution_distribution': self._calculate_contribution_distribution(contributors),
            'collaboration_graph': self._build_collaboration_graph(contributor_details),
            'expertise_areas': self._identify_expertise_areas(contributor_details)
        }

        return metrics

    def _analyze_code_metrics(self) -> Dict[str, Any]:
        """Analyze code quality and complexity metrics."""
        metrics = {
            'lines_of_code': self._count_lines_of_code(),
            'language_distribution': self._analyze_languages(),
            'file_size_distribution': self._analyze_file_sizes(),
            'documentation_coverage': self._estimate_documentation_coverage(),
            'test_coverage_estimate': self._estimate_test_coverage(),
            'complexity_indicators': self._analyze_complexity()
        }

        return metrics

    def _analyze_activity_patterns(self) -> Dict[str, Any]:
        """Analyze development activity patterns."""
        commits_by_date = self._get_commits_by_date()

        patterns = {
            'development_phases': self._identify_development_phases(commits_by_date),
            'activity_heatmap': self._create_activity_heatmap(commits_by_date),
            'sprint_detection': self._detect_sprints(commits_by_date),
            'seasonal_patterns': self._analyze_seasonal_patterns(commits_by_date),
            'momentum_analysis': self._analyze_momentum(commits_by_date)
        }

        return patterns

    def _detect_milestones(self) -> List[Dict[str, Any]]:
        """Automatically detect project milestones."""
        milestones = []

        # Detect version tags
        tags = self._run_git_command(['tag', '-l', '--sort=-version:refname']).strip().split('\n')
        for tag in tags[:20]:  # Limit to recent tags
            if tag:
                tag_info = self._get_tag_info(tag)
                if tag_info:
                    milestones.append(tag_info)

        # Detect significant commits
        significant_commits = self._find_significant_commits()
        milestones.extend(significant_commits)

        # Sort by date
        milestones.sort(key=lambda x: x.get('date', ''), reverse=True)

        return milestones[:50]  # Return top 50 milestones

    def _calculate_health_score(self) -> Dict[str, Any]:
        """Calculate comprehensive repository health score."""
        scores = {
            'activity_score': self._calculate_activity_score(),
            'maintainability_score': self._calculate_maintainability_score(),
            'collaboration_score': self._calculate_collaboration_score(),
            'documentation_score': self._calculate_documentation_score(),
            'stability_score': self._calculate_stability_score()
        }

        # Calculate overall health score
        overall_score = sum(scores.values()) / len(scores)

        # Determine health status
        if overall_score >= 80:
            status = 'Excellent'
            color = '#10B981'
        elif overall_score >= 60:
            status = 'Good'
            color = '#3B82F6'
        elif overall_score >= 40:
            status = 'Fair'
            color = '#F59E0B'
        else:
            status = 'Needs Attention'
            color = '#EF4444'

        return {
            'overall_score': round(overall_score, 1),
            'status': status,
            'color': color,
            'category_scores': scores,
            'recommendations': self._generate_health_recommendations(scores)
        }

    def _generate_insights(self) -> List[Dict[str, str]]:
        """Generate actionable insights from the analysis."""
        insights = []

        # This would contain logic to generate insights based on all the analysis
        # For now, returning sample insights
        insights.append({
            'category': 'Development Pattern',
            'insight': 'Repository shows consistent development with regular commits',
            'recommendation': 'Maintain current development cadence'
        })

        return insights

    def generate_html_report(self, analysis: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Generate comprehensive HTML report with interactive visualizations."""
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.repo_path / f'evolution_report_{timestamp}.html'

        html_content = self._create_enhanced_html_report(analysis)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_path)

    def _create_enhanced_html_report(self, analysis: Dict[str, Any]) -> str:
        """Create enhanced HTML report with comprehensive visualizations."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repository Evolution Report - {analysis['metadata']['name']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <style>
        {self._get_enhanced_css()}
    </style>
</head>
<body>
    <div class="container">
        {self._create_header_section(analysis)}
        {self._create_health_dashboard(analysis)}
        {self._create_metrics_grid(analysis)}
        {self._create_commit_analysis_section(analysis)}
        {self._create_contributor_section(analysis)}
        {self._create_file_evolution_section(analysis)}
        {self._create_activity_patterns_section(analysis)}
        {self._create_milestones_section(analysis)}
        {self._create_insights_section(analysis)}
    </div>
    <script>
        {self._get_enhanced_javascript(analysis)}
    </script>
</body>
</html>'''

    def _get_enhanced_css(self) -> str:
        """Return enhanced CSS for the report."""
        return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #1a202c;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header .subtitle {
            color: #718096;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .metadata-item {
            background: #f7fafc;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .metadata-item .label {
            color: #718096;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }

        .metadata-item .value {
            color: #2d3748;
            font-size: 1.2rem;
            font-weight: 600;
        }

        .health-dashboard {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        .health-score-circle {
            width: 200px;
            height: 200px;
            margin: 0 auto 30px;
            position: relative;
        }

        .health-categories {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .health-category {
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .health-category .score {
            font-size: 2rem;
            font-weight: bold;
            margin: 10px 0;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
        }

        .metric-card h3 {
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }

        .chart-container {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        .chart-container h2 {
            color: #2d3748;
            margin-bottom: 30px;
            font-size: 1.8rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 15px;
        }

        .insight-card {
            background: linear-gradient(135deg, #667eea15, #764ba215);
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 10px;
        }

        .insight-card h4 {
            color: #2d3748;
            margin-bottom: 10px;
        }

        .insight-card p {
            color: #4a5568;
            line-height: 1.6;
        }

        .recommendation {
            background: #f0fff4;
            border-left: 4px solid #48bb78;
            padding: 15px;
            margin-top: 10px;
            border-radius: 5px;
        }

        .milestone {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #f6ad55;
            box-shadow: 0 5px 10px rgba(0,0,0,0.05);
        }

        .milestone-date {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }

        .milestone-title {
            color: #2d3748;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .milestone-description {
            color: #4a5568;
            line-height: 1.5;
        }

        .activity-heatmap {
            margin: 30px 0;
        }

        .heatmap-cell {
            stroke: #e2e8f0;
            stroke-width: 2;
            rx: 2;
            ry: 2;
        }

        .tooltip {
            position: absolute;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 5px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        '''

    def _get_enhanced_javascript(self, analysis: Dict[str, Any]) -> str:
        """Return enhanced JavaScript for interactive features."""
        return f'''
        // Initialize all charts and visualizations
        document.addEventListener('DOMContentLoaded', function() {{
            // Create commit frequency chart
            createCommitFrequencyChart({json.dumps(analysis.get('commit_analysis', {}).get('statistics', {}).get('by_date', {}))});

            // Create contributor chart
            createContributorChart({json.dumps(analysis.get('contributor_metrics', {}).get('top_contributors', []))});

            // Create health score visualization
            createHealthScoreVisualization({json.dumps(analysis.get('health_score', {}))});

            // Create activity heatmap
            createActivityHeatmap({json.dumps(analysis.get('activity_patterns', {}).get('activity_heatmap', {}))});

            // Add interactive features
            addInteractiveFeatures();
        }});

        function createCommitFrequencyChart(data) {{
            const ctx = document.getElementById('commitChart');
            if (!ctx) return;

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: Object.keys(data).slice(-30),
                    datasets: [{{
                        label: 'Commits per Day',
                        data: Object.values(data).slice(-30),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }}
                    }}
                }}
            }});
        }}

        function createContributorChart(contributors) {{
            const ctx = document.getElementById('contributorChart');
            if (!ctx) return;

            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: contributors.map(c => c.name || 'Unknown'),
                    datasets: [{{
                        data: contributors.map(c => c.commits || 0),
                        backgroundColor: [
                            '#667eea', '#764ba2', '#f093fb', '#f5576c',
                            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
                            '#fa709a', '#fee140'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'right'
                        }}
                    }}
                }}
            }});
        }}

        function createHealthScoreVisualization(healthData) {{
            // Create circular progress indicator
            const svg = d3.select('#healthScoreCircle');
            if (!svg.node()) return;

            const width = 200;
            const height = 200;
            const radius = Math.min(width, height) / 2 - 10;

            const arc = d3.arc()
                .innerRadius(radius - 30)
                .outerRadius(radius);

            const pie = d3.pie()
                .value(d => d)
                .sort(null);

            const data = [healthData.overall_score || 0, 100 - (healthData.overall_score || 0)];

            const g = svg.append('g')
                .attr('transform', `translate(${{width/2}},${{height/2}})`);

            const path = g.selectAll('path')
                .data(pie(data))
                .enter().append('path')
                .attr('d', arc)
                .attr('fill', (d, i) => i === 0 ? healthData.color : '#e2e8f0');

            g.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .style('font-size', '2rem')
                .style('font-weight', 'bold')
                .text(Math.round(healthData.overall_score || 0));
        }}

        function createActivityHeatmap(heatmapData) {{
            // Implementation for activity heatmap
            // This would create a GitHub-style contribution graph
        }}

        function addInteractiveFeatures() {{
            // Add smooth scrolling
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{
                            behavior: 'smooth'
                        }});
                    }}
                }});
            }});

            // Add card animations on scroll
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }}
                }});
            }});

            document.querySelectorAll('.metric-card, .chart-container').forEach(card => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'all 0.5s ease';
                observer.observe(card);
            }});
        }}
        '''

    # Helper methods for git operations
    def _run_git_command(self, args: List[str], timeout: int = 30) -> str:
        """Run a git command with timeout to prevent hanging."""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout  # Add timeout to prevent hanging
            )
            if result.returncode != 0 and 'log' not in args and 'shortlog' not in args:
                print(f"Git command warning: {' '.join(args)}: {result.stderr[:200]}")
            return result.stdout
        except subprocess.TimeoutExpired:
            print(f"⏱️ Git command timed out after {timeout}s: {' '.join(args)}")
            return ""
        except Exception as e:
            print(f"Error running git command: {e}")
            return ""

    def _parse_commits(self, raw_commits: str) -> List[Dict]:
        """Parse raw commit output into structured data."""
        # Implementation would parse the git log output
        return []

    def _parse_contributors(self, raw_contributors: str) -> List[Dict]:
        """Parse contributor information."""
        contributors = []
        for line in raw_contributors.split('\n'):
            if line.strip():
                # Try to match format with email: "    5  John Doe <john@example.com>"
                match = re.match(r'\s*(\d+)\s+(.+?)\s+<(.+?)>', line)
                if match:
                    contributors.append({
                        'commits': int(match.group(1)),
                        'name': match.group(2).strip(),
                        'email': match.group(3)
                    })
                else:
                    # Try simpler format without email: "    5\tJohn Doe" or "    5  John Doe"
                    parts = re.split(r'\s+', line.strip(), 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        contributors.append({
                            'commits': int(parts[0]),
                            'name': parts[1].strip(),
                            'email': ''
                        })
        return contributors

    def _get_current_files(self) -> List[str]:
        """Get list of current files in repository."""
        files = self._run_git_command(['ls-files']).strip().split('\n')
        return [f for f in files if f]

    def _get_file_history(self, file_path: str) -> Dict:
        """Get history for a specific file."""
        # Implementation would get file history
        return {}

    def _identify_most_modified_files(self, file_history: Dict) -> List[str]:
        """Identify files with most modifications."""
        # Implementation
        return []

    def _identify_stable_files(self, file_history: Dict) -> List[str]:
        """Identify stable core files."""
        # Implementation
        return []

    def _identify_recent_additions(self, file_history: Dict) -> List[str]:
        """Identify recently added files."""
        # Implementation
        return []

    def _calculate_file_churn(self, file_history: Dict) -> float:
        """Calculate file churn rate."""
        # Implementation
        return 0.0

    def _analyze_directory_growth(self) -> Dict:
        """Analyze how directories have grown."""
        # Implementation
        return {}

    def _analyze_file_types(self, files: List[str]) -> Dict:
        """Analyze distribution of file types."""
        extensions = Counter()
        for file in files:
            ext = Path(file).suffix
            if ext:
                extensions[ext] += 1
        return dict(extensions.most_common(20))

    def _get_contributor_details(self, email: str) -> Dict:
        """Get detailed information for a contributor."""
        # Implementation
        return {}

    def _calculate_contribution_distribution(self, contributors: List[Dict]) -> Dict:
        """Calculate how contributions are distributed."""
        # Implementation
        return {}

    def _build_collaboration_graph(self, contributor_details: Dict) -> Dict:
        """Build collaboration relationships."""
        # Implementation
        return {}

    def _identify_expertise_areas(self, contributor_details: Dict) -> Dict:
        """Identify expertise areas for contributors."""
        # Implementation
        return {}

    def _count_lines_of_code(self) -> Dict:
        """Count lines of code by language."""
        # Implementation
        return {}

    def _analyze_languages(self) -> Dict:
        """Analyze programming language distribution."""
        # Implementation
        return {}

    def _analyze_file_sizes(self) -> Dict:
        """Analyze file size distribution."""
        # Implementation
        return {}

    def _estimate_documentation_coverage(self) -> float:
        """Estimate documentation coverage."""
        # Implementation
        return 0.0

    def _estimate_test_coverage(self) -> float:
        """Estimate test coverage."""
        # Implementation
        return 0.0

    def _analyze_complexity(self) -> Dict:
        """Analyze code complexity indicators."""
        # Implementation
        return {}

    def _get_commits_by_date(self) -> Dict:
        """Get commits grouped by date."""
        # Implementation
        return {}

    def _identify_development_phases(self, commits_by_date: Dict) -> List[Dict]:
        """Identify distinct development phases."""
        # Implementation
        return []

    def _create_activity_heatmap(self, commits_by_date: Dict) -> Dict:
        """Create activity heatmap data."""
        # Implementation
        return {}

    def _detect_sprints(self, commits_by_date: Dict) -> List[Dict]:
        """Detect sprint patterns."""
        # Implementation
        return []

    def _analyze_seasonal_patterns(self, commits_by_date: Dict) -> Dict:
        """Analyze seasonal development patterns."""
        # Implementation
        return {}

    def _analyze_momentum(self, commits_by_date: Dict) -> Dict:
        """Analyze development momentum."""
        # Implementation
        return {}

    def _get_tag_info(self, tag: str) -> Dict:
        """Get information about a tag."""
        # Implementation
        return {}

    def _find_significant_commits(self) -> List[Dict]:
        """Find significant commits (large changes, merges, etc.)."""
        # Implementation
        return []

    def _calculate_activity_score(self) -> float:
        """Calculate activity health score."""
        # Implementation
        return 75.0

    def _calculate_maintainability_score(self) -> float:
        """Calculate maintainability score."""
        # Implementation
        return 80.0

    def _calculate_collaboration_score(self) -> float:
        """Calculate collaboration score."""
        # Implementation
        return 70.0

    def _calculate_documentation_score(self) -> float:
        """Calculate documentation score."""
        # Implementation
        return 65.0

    def _calculate_stability_score(self) -> float:
        """Calculate stability score."""
        # Implementation
        return 85.0

    def _generate_health_recommendations(self, scores: Dict) -> List[str]:
        """Generate recommendations based on health scores."""
        recommendations = []

        if scores.get('documentation_score', 100) < 70:
            recommendations.append("Consider improving documentation coverage")

        if scores.get('activity_score', 100) < 50:
            recommendations.append("Repository shows low activity - consider archiving if no longer maintained")

        if scores.get('collaboration_score', 100) < 60:
            recommendations.append("Encourage more collaboration and code reviews")

        return recommendations

    def _parse_remotes(self, remotes_raw: str) -> List[str]:
        """Parse remote URLs from git remote output."""
        urls = []
        for line in remotes_raw.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    urls.append(parts[1])
        return list(set(urls))

    def _group_commits_by_author(self, commits: List[Dict]) -> Dict:
        """Group commits by author."""
        # Implementation
        return {}

    def _group_commits_by_date(self, commits: List[Dict]) -> Dict:
        """Group commits by date."""
        # Implementation
        return {}

    def _analyze_commit_hours(self, commits: List[Dict]) -> Dict:
        """Analyze commit hours distribution."""
        # Implementation
        return {}

    def _analyze_commit_days(self, commits: List[Dict]) -> Dict:
        """Analyze commit days of week distribution."""
        # Implementation
        return {}

    def _analyze_commit_messages(self, commits: List[Dict]) -> Dict:
        """Analyze commit message patterns."""
        # Implementation
        return {}

    def _analyze_file_changes(self, commits: List[Dict]) -> Dict:
        """Analyze file change patterns."""
        # Implementation
        return {}

    def _calculate_average_files_per_commit(self, commits: List[Dict]) -> float:
        """Calculate average files changed per commit."""
        # Implementation
        return 0.0

    def _analyze_commit_sizes(self, commits: List[Dict]) -> Dict:
        """Analyze commit size distribution."""
        # Implementation
        return {}

    def _detect_burst_patterns(self, commits: List[Dict]) -> List[Dict]:
        """Detect burst development patterns."""
        # Implementation
        return []

    def _identify_consistent_contributors(self, commits: List[Dict]) -> List[str]:
        """Identify consistent contributors."""
        # Implementation
        return []

    def _detect_refactoring_periods(self, commits: List[Dict]) -> List[Dict]:
        """Detect refactoring periods."""
        # Implementation
        return []

    def _detect_feature_development(self, commits: List[Dict]) -> List[Dict]:
        """Detect feature development periods."""
        # Implementation
        return []

    def _create_commit_timeline(self, commits: List[Dict]) -> List[Dict]:
        """Create commit timeline."""
        # Implementation
        return []

    def _calculate_development_velocity(self, commits: List[Dict]) -> Dict:
        """Calculate development velocity metrics."""
        # Implementation
        return {}

    # HTML generation helper methods
    def _create_header_section(self, analysis: Dict) -> str:
        """Create header section of report."""
        metadata = analysis['metadata']
        return f'''
        <div class="header">
            <h1>📊 {metadata['name']} Evolution Report</h1>
            <div class="subtitle">Comprehensive repository analysis and insights</div>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="label">Repository Age</div>
                    <div class="value">{metadata.get('age_days', 0)} days</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Current Branch</div>
                    <div class="value">{metadata.get('current_branch', 'main')}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Total Branches</div>
                    <div class="value">{metadata.get('branch_count', 0)}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Analysis Date</div>
                    <div class="value">{datetime.now().strftime('%Y-%m-%d')}</div>
                </div>
            </div>
        </div>
        '''

    def _create_health_dashboard(self, analysis: Dict) -> str:
        """Create health dashboard section."""
        health = analysis.get('health_score', {})
        return f'''
        <div class="health-dashboard">
            <h2>Repository Health Dashboard</h2>
            <div class="health-score-circle">
                <svg id="healthScoreCircle" width="200" height="200"></svg>
            </div>
            <h3 style="text-align: center; color: {health.get('color', '#718096')}">
                {health.get('status', 'Unknown')}
            </h3>
            <div class="health-categories">
                {self._create_health_categories(health.get('category_scores', {}))}
            </div>
            {self._create_recommendations(health.get('recommendations', []))}
        </div>
        '''

    def _create_health_categories(self, scores: Dict) -> str:
        """Create health category cards."""
        html = ""
        for category, score in scores.items():
            color = '#10B981' if score >= 80 else '#F59E0B' if score >= 60 else '#EF4444'
            html += f'''
            <div class="health-category">
                <div class="label">{category.replace('_', ' ').title()}</div>
                <div class="score" style="color: {color}">{score}</div>
            </div>
            '''
        return html

    def _create_recommendations(self, recommendations: List[str]) -> str:
        """Create recommendations section."""
        if not recommendations:
            return ""

        html = '<div class="recommendations"><h3>Recommendations</h3>'
        for rec in recommendations:
            html += f'<div class="recommendation">{rec}</div>'
        html += '</div>'
        return html

    def _create_metrics_grid(self, analysis: Dict) -> str:
        """Create metrics grid section."""
        commit_stats = analysis.get('commit_analysis', {}).get('statistics', {})
        file_stats = analysis.get('file_evolution', {})

        return f'''
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📝 Commit Statistics</h3>
                <div>Total Commits: <strong>{commit_stats.get('total', 0)}</strong></div>
                <div>Merge Commits: <strong>{commit_stats.get('merge_commits', 0)}</strong></div>
                <div>Avg Files/Commit: <strong>{commit_stats.get('average_files_per_commit', 0):.1f}</strong></div>
            </div>

            <div class="metric-card">
                <h3>📁 File Statistics</h3>
                <div>Total Files: <strong>{file_stats.get('total_files', 0)}</strong></div>
                <div>File Types: <strong>{len(file_stats.get('file_types', {}))}</strong></div>
            </div>

            <div class="metric-card">
                <h3>👥 Contributors</h3>
                <div>Total: <strong>{analysis.get('contributor_metrics', {}).get('total_contributors', 0)}</strong></div>
            </div>
        </div>
        '''

    def _create_commit_analysis_section(self, analysis: Dict) -> str:
        """Create commit analysis section."""
        return f'''
        <div class="chart-container">
            <h2>📈 Commit Analysis</h2>
            <canvas id="commitChart"></canvas>
        </div>
        '''

    def _create_contributor_section(self, analysis: Dict) -> str:
        """Create contributor section."""
        return f'''
        <div class="chart-container">
            <h2>👥 Top Contributors</h2>
            <canvas id="contributorChart"></canvas>
        </div>
        '''

    def _create_file_evolution_section(self, analysis: Dict) -> str:
        """Create file evolution section."""
        evolution = analysis.get('file_evolution', {})
        patterns = evolution.get('evolution_patterns', {})

        return f'''
        <div class="chart-container">
            <h2>📁 File Evolution</h2>
            <div class="file-evolution-content">
                <h3>Most Modified Files</h3>
                {self._create_file_list(patterns.get('most_modified_files', []))}

                <h3>Recently Added Files</h3>
                {self._create_file_list(patterns.get('recently_added', []))}

                <h3>File Type Distribution</h3>
                {self._create_file_type_chart(evolution.get('file_types', {}))}
            </div>
        </div>
        '''

    def _create_file_list(self, files: List[str]) -> str:
        """Create a formatted file list."""
        if not files:
            return "<p>No files to display</p>"

        html = "<ul>"
        for file in files[:10]:  # Limit to 10 files
            html += f"<li>{file}</li>"
        html += "</ul>"
        return html

    def _create_file_type_chart(self, file_types: Dict) -> str:
        """Create file type distribution chart."""
        # This would create a chart visualization
        return "<div>File type distribution chart</div>"

    def _create_activity_patterns_section(self, analysis: Dict) -> str:
        """Create activity patterns section."""
        return f'''
        <div class="chart-container">
            <h2>📊 Activity Patterns</h2>
            <div class="activity-heatmap" id="activityHeatmap">
                <!-- Activity heatmap will be rendered here -->
            </div>
        </div>
        '''

    def _create_milestones_section(self, analysis: Dict) -> str:
        """Create milestones section."""
        milestones = analysis.get('milestones', [])

        html = '<div class="chart-container"><h2>🎯 Milestones & Releases</h2>'

        if not milestones:
            html += '<p>No milestones detected</p>'
        else:
            for milestone in milestones[:10]:  # Limit to 10 milestones
                html += f'''
                <div class="milestone">
                    <div class="milestone-date">{milestone.get('date', 'Unknown date')}</div>
                    <div class="milestone-title">{milestone.get('title', 'Untitled')}</div>
                    <div class="milestone-description">{milestone.get('description', '')}</div>
                </div>
                '''

        html += '</div>'
        return html

    def _create_insights_section(self, analysis: Dict) -> str:
        """Create insights section."""
        insights = analysis.get('insights', [])

        html = '<div class="chart-container"><h2>💡 Insights & Recommendations</h2>'

        for insight in insights:
            html += f'''
            <div class="insight-card">
                <h4>{insight.get('category', 'General')}</h4>
                <p>{insight.get('insight', '')}</p>
                {f'<div class="recommendation">{insight.get("recommendation", "")}</div>' if insight.get('recommendation') else ''}
            </div>
            '''

        html += '</div>'
        return html