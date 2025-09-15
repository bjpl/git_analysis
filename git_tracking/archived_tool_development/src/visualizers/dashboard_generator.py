#!/usr/bin/env python3
"""
BJPL Repository Dashboard Generator
====================================
Creates an interactive HTML dashboard for repository analytics.
"""

import json
from pathlib import Path
from datetime import datetime
import html


class DashboardGenerator:
    """Generate interactive HTML dashboard from analysis data."""

    def __init__(self, analysis_dir: Path):
        self.analysis_dir = Path(analysis_dir)
        self.template_file = self.analysis_dir / "dashboard.html"

    def load_latest_analysis(self) -> dict:
        """Load the latest analysis JSON file."""
        json_file = self.analysis_dir / "latest_analysis.json"
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def generate_dashboard(self):
        """Generate HTML dashboard from analysis data."""
        data = self.load_latest_analysis()
        if not data:
            print("❌ No analysis data found")
            return

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BJPL Repository Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            color: #2d3748;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}

        .header .meta {{
            color: #718096;
            font-size: 0.9rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card .label {{
            color: #718096;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .stat-card .value {{
            color: #2d3748;
            font-size: 2rem;
            font-weight: bold;
        }}

        .chart-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }}

        .chart-container h2 {{
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}

        .repo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}

        .repo-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border-left: 4px solid #667eea;
        }}

        .repo-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }}

        .repo-card h3 {{
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 1.2rem;
        }}

        .repo-card a {{
            color: #667eea;
            text-decoration: none;
        }}

        .repo-card a:hover {{
            text-decoration: underline;
        }}

        .repo-meta {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
            font-size: 0.85rem;
            color: #718096;
        }}

        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .badge.very-active {{
            background: #d4f4dd;
            color: #22543d;
        }}

        .badge.active {{
            background: #bee3f8;
            color: #2c5282;
        }}

        .badge.moderate {{
            background: #feebc8;
            color: #7c2d12;
        }}

        .badge.dormant {{
            background: #fed7d7;
            color: #742a2a;
        }}

        .language-bar {{
            display: flex;
            height: 30px;
            border-radius: 6px;
            overflow: hidden;
            margin-top: 20px;
        }}

        .language-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .timeline {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }}

        .timeline h2 {{
            color: #2d3748;
            margin-bottom: 20px;
        }}

        .timeline-item {{
            padding: 10px 0;
            border-bottom: 1px solid #e2e8f0;
        }}

        .timeline-item:last-child {{
            border-bottom: none;
        }}

        .timeline-period {{
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 5px;
        }}

        .timeline-repos {{
            color: #718096;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 BJPL Repository Analytics Dashboard</h1>
            <div class="meta">
                <p>Generated: {data['metadata']['generated_at']}</p>
                <p>GitHub: <a href="https://github.com/bjpl" target="_blank">github.com/bjpl</a></p>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Repositories</div>
                <div class="value">{data['metadata']['total_repositories']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Stars</div>
                <div class="value">{data['statistics']['total_stars']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Forks</div>
                <div class="value">{data['statistics']['total_forks']}</div>
            </div>
            <div class="stat-card">
                <div class="label">Open Issues</div>
                <div class="value">{data['statistics']['total_issues']}</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>Programming Languages</h2>
            <div class="language-bar">
                {self._generate_language_bar(data['statistics']['languages'])}
            </div>
            <div style="margin-top: 15px;">
                {self._generate_language_legend(data['statistics']['languages'])}
            </div>
        </div>

        <div class="timeline">
            <h2>📅 Recent Activity Timeline</h2>
            {self._generate_timeline_html(data['timeline'])}
        </div>

        <div class="chart-container">
            <h2>Active Repositories</h2>
            <div class="repo-grid">
                {self._generate_repo_cards(data['repositories'][:12])}
            </div>
        </div>
    </div>

    <script>
        // Add interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Animate stat cards on scroll
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }}
                }});
            }});

            document.querySelectorAll('.stat-card, .repo-card').forEach(card => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'all 0.5s ease';
                observer.observe(card);
            }});
        }});
    </script>
</body>
</html>"""

        # Save dashboard
        with open(self.template_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Dashboard generated: {self.template_file}")

    def _generate_language_bar(self, languages: dict) -> str:
        """Generate language distribution bar."""
        if not languages:
            return '<div style="text-align: center; color: #718096;">No language data</div>'

        colors = {
            'Python': '#3776AB',
            'JavaScript': '#F7DF1E',
            'TypeScript': '#3178C6',
            'HTML': '#E34C26',
            'CSS': '#1572B6',
            'SCSS': '#CC6699',
            'Ruby': '#CC342D',
            'Java': '#007396',
            'Go': '#00ADD8',
            'Rust': '#000000',
            'C++': '#00599C',
            'Shell': '#89E051'
        }

        total = sum(languages.values())
        segments = []

        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            color = colors.get(lang, '#718096')
            if percentage > 5:  # Only show label if segment is large enough
                segments.append(f'<div class="language-segment" style="width: {percentage}%; background: {color};">{lang}</div>')
            else:
                segments.append(f'<div class="language-segment" style="width: {percentage}%; background: {color};"></div>')

        return ''.join(segments)

    def _generate_language_legend(self, languages: dict) -> str:
        """Generate language legend."""
        if not languages:
            return ''

        legend_items = []
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            legend_items.append(f'<span style="margin-right: 20px;">● {lang}: {count}</span>')

        return f'<div style="color: #718096; font-size: 0.85rem;">{" ".join(legend_items)}</div>'

    def _generate_timeline_html(self, timeline: dict) -> str:
        """Generate timeline HTML."""
        html_parts = []

        periods = [
            ('last_24_hours', 'Last 24 Hours'),
            ('last_week', 'Last Week'),
            ('last_month', 'Last Month'),
            ('last_3_months', 'Last 3 Months'),
            ('last_6_months', 'Last 6 Months'),
            ('older', 'Older')
        ]

        for key, label in periods:
            if timeline.get(key):
                repos = timeline[key][:5]  # Show max 5 repos per period
                more = len(timeline[key]) - 5 if len(timeline[key]) > 5 else 0

                repos_text = ', '.join(repos)
                if more > 0:
                    repos_text += f' (+{more} more)'

                html_parts.append(f'''
                <div class="timeline-item">
                    <div class="timeline-period">{label}</div>
                    <div class="timeline-repos">{repos_text}</div>
                </div>
                ''')

        return ''.join(html_parts)

    def _generate_repo_cards(self, repositories: list) -> str:
        """Generate repository cards HTML."""
        cards = []

        for repo in repositories:
            status_class = repo['activity_metrics']['activity_status'].lower().replace(' ', '-')

            description = html.escape(repo.get('description', 'No description')[:100]) if repo.get('description') else 'No description'

            cards.append(f'''
            <div class="repo-card">
                <h3><a href="https://github.com/{repo['full_name']}" target="_blank">{repo['name']}</a></h3>
                <p style="color: #718096; font-size: 0.9rem; margin: 10px 0;">{description}</p>
                <div class="repo-meta">
                    <span>📝 {repo['language'] or 'N/A'}</span>
                    <span>⭐ {repo['stars']}</span>
                    <span>🔀 {repo['forks']}</span>
                    <span>📋 {repo['open_issues']}</span>
                </div>
                <div style="margin-top: 10px;">
                    <span class="badge {status_class}">{repo['activity_metrics']['activity_status']}</span>
                    <span style="margin-left: 10px; color: #718096; font-size: 0.8rem;">
                        Updated {repo['activity_metrics']['days_since_update']} days ago
                    </span>
                </div>
            </div>
            ''')

        return ''.join(cards)


def main():
    """Generate dashboard."""
    analysis_dir = Path(r"C:\Users\brand\Development\Project_Workspace\bjpl_repos_analysis")
    generator = DashboardGenerator(analysis_dir)
    generator.generate_dashboard()


if __name__ == "__main__":
    main()