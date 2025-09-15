#!/usr/bin/env python3
"""
Enhanced Report Generator
========================
Generates comprehensive, detailed HTML reports for git repositories.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.enhanced_evolution_tracker import EnhancedEvolutionTracker


def generate_enhanced_report(repo_path: str = None):
    """Generate enhanced report for a repository."""
    if not repo_path:
        repo_path = os.getcwd()

    repo_path = Path(repo_path)

    print(f"🚀 Enhanced Git Evolution Report Generator")
    print(f"=" * 50)
    print(f"📁 Repository: {repo_path.name}")
    print(f"📂 Path: {repo_path}")
    print(f"=" * 50)

    try:
        # Initialize tracker
        tracker = EnhancedEvolutionTracker(repo_path)

        # Perform comprehensive analysis
        print("\n🔍 Performing comprehensive analysis...")
        print("  ├─ Analyzing repository metadata...")
        print("  ├─ Processing commit history...")
        print("  ├─ Tracking file evolution...")
        print("  ├─ Analyzing contributors...")
        print("  ├─ Calculating code metrics...")
        print("  ├─ Detecting activity patterns...")
        print("  ├─ Identifying milestones...")
        print("  ├─ Computing health scores...")
        print("  └─ Generating insights...")

        analysis = tracker.analyze_repository()

        # Generate report
        print("\n📄 Generating enhanced HTML report...")

        # Create reports directory
        reports_dir = repo_path / 'reports'
        reports_dir.mkdir(exist_ok=True)

        # Generate report with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = reports_dir / f'enhanced_evolution_report_{timestamp}.html'

        output_path = tracker.generate_html_report(analysis, report_path)

        print(f"\n✅ Enhanced report generated successfully!")
        print(f"📄 Report location: {output_path}")

        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open(f'file://{Path(output_path).absolute()}')
            print(f"🌐 Opening report in browser...")
        except:
            print(f"⚠️  Could not open browser automatically")
            print(f"    Please open the file manually: {output_path}")

        # Print summary statistics
        print(f"\n📊 Analysis Summary:")
        print(f"  ├─ Repository Age: {analysis['metadata'].get('age_days', 0)} days")
        print(f"  ├─ Total Commits: {analysis['commit_analysis']['statistics'].get('total', 0)}")
        print(f"  ├─ Total Files: {analysis['file_evolution'].get('total_files', 0)}")
        print(f"  ├─ Contributors: {analysis['contributor_metrics'].get('total_contributors', 0)}")
        print(f"  └─ Health Score: {analysis['health_score'].get('overall_score', 0):.1f}/100 ({analysis['health_score'].get('status', 'Unknown')})")

        # Print insights
        if analysis.get('insights'):
            print(f"\n💡 Key Insights:")
            for i, insight in enumerate(analysis['insights'][:3], 1):
                print(f"  {i}. {insight.get('insight', '')}")

        return output_path

    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate enhanced repository evolution report')
    parser.add_argument('path', nargs='?', default='.',
                       help='Path to git repository (default: current directory)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    args = parser.parse_args()

    # Resolve path
    repo_path = Path(args.path).resolve()

    if not repo_path.exists():
        print(f"❌ Error: Path does not exist: {repo_path}")
        sys.exit(1)

    if not (repo_path / '.git').exists():
        print(f"❌ Error: Not a git repository: {repo_path}")
        print(f"    (no .git directory found)")
        sys.exit(1)

    # Generate report
    report_path = generate_enhanced_report(str(repo_path))

    if report_path:
        print(f"\n🎉 Report generation complete!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()