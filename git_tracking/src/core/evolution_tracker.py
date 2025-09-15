#!/usr/bin/env python3
"""
Repository Evolution & Journey Tracker for BJPL
================================================
Tracks the complete development timeline, evolution patterns, and growth stories
of all repositories, providing deep insights into project journeys.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
import requests
from collections import defaultdict, Counter
import re


class RepositoryEvolutionTracker:
    """
    Comprehensive evolution tracker that analyzes the complete journey
    of each repository from inception to current state.
    """

    def __init__(self, workspace_path: str = r"C:\Users\brand\Development\Project_Workspace"):
        self.workspace_path = Path(workspace_path)
        self.analysis_dir = self.workspace_path / "bjpl_repos_analysis"
        self.analysis_dir.mkdir(exist_ok=True)

        self.github_api = "https://api.github.com"
        self.username = "bjpl"

        # Evolution patterns to track
        self.evolution_patterns = {
            'rapid_growth': 'Sudden increase in commits/activity',
            'steady_development': 'Consistent commit pattern',
            'burst_pattern': 'Periodic intense development',
            'maintenance_mode': 'Occasional updates and fixes',
            'dormant': 'No recent activity',
            'revival': 'Activity after long pause',
            'experimental': 'Frequent changes in direction',
            'mature': 'Stable with occasional updates'
        }

    def fetch_repository_commits(self, repo_name: str, max_commits: int = 100) -> List[Dict]:
        """Fetch commit history for a repository."""
        commits = []
        page = 1

        while len(commits) < max_commits:
            url = f"{self.github_api}/repos/{self.username}/{repo_name}/commits"
            params = {"per_page": min(100, max_commits - len(commits)), "page": page}

            try:
                response = requests.get(url, params=params)
                if response.status_code == 404:
                    print(f"  ⚠️  Repository {repo_name} not found or no commits")
                    return []
                elif response.status_code == 409:  # Empty repository
                    print(f"  ⚠️  Repository {repo_name} is empty")
                    return []

                response.raise_for_status()
                page_commits = response.json()

                if not page_commits:
                    break

                commits.extend(page_commits)
                page += 1

            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error fetching commits for {repo_name}: {e}")
                break

        return commits[:max_commits]

    def analyze_commit_patterns(self, commits: List[Dict]) -> Dict:
        """Analyze patterns in commit history."""
        if not commits:
            return {
                'pattern': 'no_history',
                'total_commits': 0,
                'contributors': [],
                'commit_frequency': {},
                'peak_periods': []
            }

        # Extract commit data
        commit_dates = []
        contributors = set()
        commit_messages = []

        for commit in commits:
            if commit.get('commit'):
                date_str = commit['commit']['author']['date']
                commit_dates.append(datetime.fromisoformat(date_str.replace('Z', '+00:00')))

                if commit['commit']['author']:
                    contributors.add(commit['commit']['author']['name'])

                commit_messages.append(commit['commit']['message'])

        if not commit_dates:
            return {
                'pattern': 'no_history',
                'total_commits': 0,
                'contributors': [],
                'commit_frequency': {},
                'peak_periods': []
            }

        # Analyze commit frequency
        commit_frequency = self._calculate_commit_frequency(commit_dates)

        # Identify development pattern
        pattern = self._identify_development_pattern(commit_dates)

        # Find peak development periods
        peak_periods = self._identify_peak_periods(commit_dates)

        # Analyze commit message patterns
        message_insights = self._analyze_commit_messages(commit_messages)

        return {
            'pattern': pattern,
            'total_commits': len(commits),
            'contributors': list(contributors),
            'commit_frequency': commit_frequency,
            'peak_periods': peak_periods,
            'message_insights': message_insights,
            'first_commit': commit_dates[-1].isoformat() if commit_dates else None,
            'last_commit': commit_dates[0].isoformat() if commit_dates else None
        }

    def _calculate_commit_frequency(self, dates: List[datetime]) -> Dict:
        """Calculate commit frequency statistics."""
        if not dates:
            return {}

        # Group by various time periods
        frequency = {
            'daily': defaultdict(int),
            'weekly': defaultdict(int),
            'monthly': defaultdict(int),
            'yearly': defaultdict(int)
        }

        for date in dates:
            frequency['daily'][date.strftime('%Y-%m-%d')] += 1
            frequency['weekly'][date.strftime('%Y-W%U')] += 1
            frequency['monthly'][date.strftime('%Y-%m')] += 1
            frequency['yearly'][date.strftime('%Y')] += 1

        # Calculate averages
        total_days = (dates[0] - dates[-1]).days + 1 if len(dates) > 1 else 1

        return {
            'avg_commits_per_day': len(dates) / max(total_days, 1),
            'avg_commits_per_week': len(dates) / max(total_days / 7, 1),
            'avg_commits_per_month': len(dates) / max(total_days / 30, 1),
            'most_active_month': max(frequency['monthly'].items(), key=lambda x: x[1])[0] if frequency['monthly'] else None,
            'most_active_year': max(frequency['yearly'].items(), key=lambda x: x[1])[0] if frequency['yearly'] else None
        }

    def _identify_development_pattern(self, dates: List[datetime]) -> str:
        """Identify the development pattern based on commit history."""
        if not dates or len(dates) < 2:
            return 'insufficient_data'

        # Calculate time gaps between commits
        gaps = []
        for i in range(len(dates) - 1):
            gap = (dates[i] - dates[i + 1]).days
            gaps.append(gap)

        avg_gap = sum(gaps) / len(gaps)
        max_gap = max(gaps)

        # Recent activity check
        days_since_last = (datetime.now(dates[0].tzinfo) - dates[0]).days

        # Pattern identification
        if days_since_last > 180:
            if max_gap < 30 and avg_gap < 7:
                return 'dormant_after_active'
            else:
                return 'dormant'
        elif avg_gap < 3:
            return 'rapid_development'
        elif avg_gap < 7:
            return 'steady_development'
        elif max_gap > 60 and min(gaps) < 7:
            return 'burst_pattern'
        elif avg_gap > 30:
            return 'maintenance_mode'
        else:
            return 'moderate_activity'

    def _identify_peak_periods(self, dates: List[datetime]) -> List[Dict]:
        """Identify periods of peak development activity."""
        if not dates:
            return []

        # Group commits by week
        weekly_commits = defaultdict(list)
        for date in dates:
            week_key = date.strftime('%Y-W%U')
            weekly_commits[week_key].append(date)

        # Find weeks with above-average activity
        avg_weekly = len(dates) / len(weekly_commits) if weekly_commits else 0

        peak_periods = []
        for week, commits in weekly_commits.items():
            if len(commits) > avg_weekly * 1.5:  # 50% above average
                peak_periods.append({
                    'week': week,
                    'commits': len(commits),
                    'intensity': 'high' if len(commits) > avg_weekly * 2 else 'moderate'
                })

        return sorted(peak_periods, key=lambda x: x['commits'], reverse=True)[:10]

    def _analyze_commit_messages(self, messages: List[str]) -> Dict:
        """Analyze patterns in commit messages."""
        if not messages:
            return {}

        # Common patterns to look for
        patterns = {
            'features': r'(feat|feature|add|new|implement)',
            'fixes': r'(fix|bug|patch|resolve|correct)',
            'refactoring': r'(refactor|restructure|reorganize|clean)',
            'documentation': r'(doc|docs|readme|comment)',
            'testing': r'(test|spec|coverage)',
            'dependencies': r'(update|upgrade|bump|dependency)',
            'merge': r'(merge|pull request|pr)',
            'initial': r'(initial|init|setup|scaffold)',
            'breaking': r'(breaking|major|migrate)',
            'performance': r'(perf|optimize|speed|fast)'
        }

        insights = {
            'categories': defaultdict(int),
            'evolution_markers': [],
            'major_milestones': []
        }

        for msg in messages:
            msg_lower = msg.lower()

            # Categorize commits
            for category, pattern in patterns.items():
                if re.search(pattern, msg_lower):
                    insights['categories'][category] += 1

            # Look for version markers
            version_match = re.search(r'v?\d+\.\d+\.\d+', msg)
            if version_match:
                insights['evolution_markers'].append({
                    'type': 'version',
                    'value': version_match.group(),
                    'message': msg[:100]
                })

            # Identify major milestones
            if any(word in msg_lower for word in ['major', 'release', 'launch', 'deploy', 'v1', 'v2', 'beta', 'alpha']):
                insights['major_milestones'].append(msg[:100])

        # Calculate focus areas
        total_categorized = sum(insights['categories'].values())
        if total_categorized > 0:
            insights['primary_focus'] = max(insights['categories'].items(), key=lambda x: x[1])[0]
            insights['focus_distribution'] = {
                k: f"{(v/total_categorized)*100:.1f}%"
                for k, v in insights['categories'].items()
            }

        return insights

    def analyze_repository_evolution(self, repo_data: Dict) -> Dict:
        """Analyze complete evolution of a repository."""
        repo_name = repo_data['name']
        print(f"\n🔍 Analyzing evolution of {repo_name}...")

        # Fetch commit history
        commits = self.fetch_repository_commits(repo_name)

        # Analyze commit patterns
        commit_analysis = self.analyze_commit_patterns(commits)

        # Calculate lifecycle stage
        lifecycle_stage = self._determine_lifecycle_stage(repo_data, commit_analysis)

        # Generate evolution story
        evolution_story = self._generate_evolution_story(repo_data, commit_analysis, lifecycle_stage)

        # Create timeline events
        timeline_events = self._create_timeline_events(repo_data, commits)

        return {
            'repository': repo_name,
            'created': repo_data['created_at'],
            'last_updated': repo_data['updated_at'],
            'lifecycle_stage': lifecycle_stage,
            'development_pattern': commit_analysis.get('pattern', 'unknown'),
            'commit_analysis': commit_analysis,
            'evolution_story': evolution_story,
            'timeline_events': timeline_events,
            'metrics': {
                'total_commits': commit_analysis.get('total_commits', 0),
                'contributors': len(commit_analysis.get('contributors', [])),
                'age_days': (datetime.now(datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00')).tzinfo) -
                           datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))).days,
                'activity_score': self._calculate_activity_score(commit_analysis),
                'evolution_velocity': self._calculate_evolution_velocity(commit_analysis)
            }
        }

    def _determine_lifecycle_stage(self, repo_data: Dict, commit_analysis: Dict) -> str:
        """Determine the current lifecycle stage of the repository."""
        created_date = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
        age_days = (datetime.now(created_date.tzinfo) - created_date).days

        pattern = commit_analysis.get('pattern', 'unknown')
        total_commits = commit_analysis.get('total_commits', 0)

        if age_days < 30:
            return 'inception'
        elif age_days < 90 and total_commits < 50:
            return 'early_development'
        elif pattern in ['rapid_development', 'steady_development']:
            return 'active_growth'
        elif pattern == 'burst_pattern':
            return 'iterative_evolution'
        elif pattern == 'maintenance_mode':
            return 'mature'
        elif pattern in ['dormant', 'dormant_after_active']:
            if total_commits > 100:
                return 'archived_complete'
            else:
                return 'abandoned'
        else:
            return 'stabilizing'

    def _generate_evolution_story(self, repo_data: Dict, commit_analysis: Dict, lifecycle_stage: str) -> str:
        """Generate a narrative story of the repository's evolution."""
        stories = []

        # Opening
        created_date = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
        age_days = (datetime.now(created_date.tzinfo) - created_date).days

        stories.append(f"📖 **The Journey of {repo_data['name']}**\n")
        stories.append(f"Born {age_days} days ago on {created_date.strftime('%B %d, %Y')}, this repository ")

        # Describe the journey based on patterns
        pattern = commit_analysis.get('pattern', 'unknown')
        total_commits = commit_analysis.get('total_commits', 0)

        if lifecycle_stage == 'inception':
            stories.append("is just beginning its journey, full of potential and promise.")
        elif lifecycle_stage == 'early_development':
            stories.append(f"has seen {total_commits} commits as it takes shape and finds its direction.")
        elif lifecycle_stage == 'active_growth':
            stories.append(f"is experiencing rapid growth with {total_commits} commits from {len(commit_analysis.get('contributors', []))} contributors.")
        elif lifecycle_stage == 'mature':
            stories.append(f"has matured into a stable project with {total_commits} commits, now in maintenance mode.")
        elif lifecycle_stage == 'archived_complete':
            stories.append(f"completed its mission with {total_commits} commits and now rests as a finished work.")
        else:
            stories.append(f"continues to evolve with {total_commits} commits marking its progress.")

        # Add pattern-specific narrative
        if pattern == 'burst_pattern':
            stories.append(" Development happens in intense bursts of creativity, followed by periods of reflection.")
        elif pattern == 'steady_development':
            stories.append(" The consistent commit pattern shows disciplined, methodical progress.")
        elif pattern == 'rapid_development':
            stories.append(" Rapid-fire commits demonstrate intense focus and fast iteration.")

        # Add insights from commit messages
        if commit_analysis.get('message_insights'):
            insights = commit_analysis['message_insights']
            if insights.get('primary_focus'):
                stories.append(f" The primary focus has been on {insights['primary_focus']}.")
            if insights.get('major_milestones'):
                stories.append(f" Major milestones include: {insights['major_milestones'][0]}")

        # Add language and technology journey
        if repo_data.get('language'):
            stories.append(f" Built primarily in {repo_data['language']},")
            stories.append(" it represents a journey through modern software development.")

        return " ".join(stories)

    def _create_timeline_events(self, repo_data: Dict, commits: List[Dict]) -> List[Dict]:
        """Create significant timeline events from repository history."""
        events = []

        # Repository creation
        events.append({
            'date': repo_data['created_at'],
            'type': 'creation',
            'title': 'Repository Created',
            'description': f"{repo_data['name']} begins its journey"
        })

        # First commit
        if commits and len(commits) > 0:
            first_commit = commits[-1]
            events.append({
                'date': first_commit['commit']['author']['date'],
                'type': 'first_commit',
                'title': 'First Commit',
                'description': first_commit['commit']['message'][:100]
            })

        # Look for significant commits
        for commit in commits[:20]:  # Check recent commits
            msg = commit['commit']['message'].lower()

            # Version releases
            if re.search(r'v?\d+\.\d+\.\d+', msg):
                events.append({
                    'date': commit['commit']['author']['date'],
                    'type': 'release',
                    'title': 'Version Release',
                    'description': commit['commit']['message'][:100]
                })

            # Major features
            elif any(word in msg for word in ['major', 'feature', 'launch', 'release']):
                events.append({
                    'date': commit['commit']['author']['date'],
                    'type': 'milestone',
                    'title': 'Major Update',
                    'description': commit['commit']['message'][:100]
                })

        # Sort by date
        events.sort(key=lambda x: x['date'])

        return events[:15]  # Return top 15 events

    def _calculate_activity_score(self, commit_analysis: Dict) -> float:
        """Calculate an activity score from 0-100."""
        if not commit_analysis or commit_analysis.get('total_commits', 0) == 0:
            return 0.0

        score = 0.0

        # Base score from commit count (max 40 points)
        commits = commit_analysis.get('total_commits', 0)
        score += min(40, commits / 2.5)

        # Pattern bonus (max 30 points)
        pattern = commit_analysis.get('pattern', '')
        pattern_scores = {
            'rapid_development': 30,
            'steady_development': 25,
            'burst_pattern': 20,
            'moderate_activity': 15,
            'maintenance_mode': 10,
            'dormant_after_active': 5,
            'dormant': 0
        }
        score += pattern_scores.get(pattern, 5)

        # Contributor bonus (max 20 points)
        contributors = len(commit_analysis.get('contributors', []))
        score += min(20, contributors * 5)

        # Frequency bonus (max 10 points)
        freq = commit_analysis.get('commit_frequency', {})
        if freq.get('avg_commits_per_week', 0) > 1:
            score += min(10, freq['avg_commits_per_week'] * 2)

        return min(100, score)

    def _calculate_evolution_velocity(self, commit_analysis: Dict) -> str:
        """Calculate how fast the repository is evolving."""
        if not commit_analysis or commit_analysis.get('total_commits', 0) == 0:
            return 'static'

        freq = commit_analysis.get('commit_frequency', {})
        avg_per_week = freq.get('avg_commits_per_week', 0)

        if avg_per_week > 10:
            return 'hyperspeed'
        elif avg_per_week > 5:
            return 'fast'
        elif avg_per_week > 2:
            return 'moderate'
        elif avg_per_week > 0.5:
            return 'slow'
        else:
            return 'glacial'

    def generate_evolution_report(self, all_evolutions: List[Dict]) -> Dict:
        """Generate comprehensive evolution report for all repositories."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_repositories': len(all_evolutions),
            'repository_evolutions': all_evolutions,
            'aggregate_insights': self._generate_aggregate_insights(all_evolutions),
            'evolution_timeline': self._create_master_timeline(all_evolutions),
            'lifecycle_distribution': self._calculate_lifecycle_distribution(all_evolutions),
            'pattern_analysis': self._analyze_patterns_across_repos(all_evolutions)
        }

        return report

    def _generate_aggregate_insights(self, evolutions: List[Dict]) -> Dict:
        """Generate insights across all repositories."""
        total_commits = sum(e['metrics']['total_commits'] for e in evolutions)
        total_contributors = len(set(
            contributor
            for e in evolutions
            for contributor in e['commit_analysis'].get('contributors', [])
        ))

        activity_scores = [e['metrics']['activity_score'] for e in evolutions]
        avg_activity = sum(activity_scores) / len(activity_scores) if activity_scores else 0

        return {
            'total_commits_all_repos': total_commits,
            'unique_contributors': total_contributors,
            'average_activity_score': round(avg_activity, 2),
            'most_active_repo': max(evolutions, key=lambda x: x['metrics']['activity_score'])['repository'] if evolutions else None,
            'oldest_repo': min(evolutions, key=lambda x: x['created'])['repository'] if evolutions else None,
            'newest_repo': max(evolutions, key=lambda x: x['created'])['repository'] if evolutions else None,
            'evolution_velocities': Counter(e['metrics']['evolution_velocity'] for e in evolutions)
        }

    def _create_master_timeline(self, evolutions: List[Dict]) -> List[Dict]:
        """Create a master timeline combining all repository events."""
        all_events = []

        for evolution in evolutions:
            for event in evolution.get('timeline_events', []):
                event_copy = event.copy()
                event_copy['repository'] = evolution['repository']
                all_events.append(event_copy)

        # Sort by date
        all_events.sort(key=lambda x: x['date'], reverse=True)

        return all_events[:50]  # Return top 50 most recent events

    def _calculate_lifecycle_distribution(self, evolutions: List[Dict]) -> Dict:
        """Calculate distribution of repositories across lifecycle stages."""
        stages = Counter(e['lifecycle_stage'] for e in evolutions)
        total = sum(stages.values())

        return {
            'stages': dict(stages),
            'percentages': {k: f"{(v/total)*100:.1f}%" for k, v in stages.items()} if total > 0 else {}
        }

    def _analyze_patterns_across_repos(self, evolutions: List[Dict]) -> Dict:
        """Analyze development patterns across all repositories."""
        patterns = Counter(e['development_pattern'] for e in evolutions)

        # Group by pattern similarity
        pattern_groups = {
            'active': ['rapid_development', 'steady_development', 'moderate_activity'],
            'periodic': ['burst_pattern', 'maintenance_mode'],
            'inactive': ['dormant', 'dormant_after_active', 'insufficient_data']
        }

        grouped = {}
        for group, group_patterns in pattern_groups.items():
            grouped[group] = sum(patterns.get(p, 0) for p in group_patterns)

        return {
            'individual_patterns': dict(patterns),
            'grouped_patterns': grouped,
            'most_common_pattern': max(patterns.items(), key=lambda x: x[1])[0] if patterns else None
        }


def main():
    """Execute repository evolution analysis."""
    tracker = RepositoryEvolutionTracker()

    # Load repository data
    repos_file = Path(r"C:\Users\brand\Development\Project_Workspace\bjpl_repos_analysis\github_repos.json")
    with open(repos_file, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
        repos = data['value'] if isinstance(data, dict) and 'value' in data else data

    print("🚀 Starting Repository Evolution Analysis...")
    print(f"   Analyzing {len(repos)} repositories")

    # Analyze each repository's evolution
    all_evolutions = []
    for repo in repos:
        evolution = tracker.analyze_repository_evolution(repo)
        all_evolutions.append(evolution)

    # Generate comprehensive report
    print("\n📊 Generating Evolution Report...")
    report = tracker.generate_evolution_report(all_evolutions)

    # Save report
    output_file = tracker.analysis_dir / f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    # Also save as latest
    latest_file = tracker.analysis_dir / "latest_evolution.json"
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✅ Evolution analysis complete!")
    print(f"   Report saved to: {output_file.name}")

    # Print summary
    insights = report['aggregate_insights']
    print(f"\n📈 Evolution Summary:")
    print(f"   Total Commits: {insights['total_commits_all_repos']}")
    print(f"   Unique Contributors: {insights['unique_contributors']}")
    print(f"   Average Activity Score: {insights['average_activity_score']}/100")
    print(f"   Most Active Repo: {insights['most_active_repo']}")

    return report


if __name__ == "__main__":
    main()