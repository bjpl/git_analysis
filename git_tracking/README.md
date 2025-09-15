# Git Evolution Tracker 🚀

A powerful standalone tool for tracking and visualizing the evolution of git repositories over time. Built using Flow Nexus development environment but runs completely independently.

## Features

### 📊 Comprehensive Repository Analysis
- **Timeline Tracking**: Complete history from inception to current state
- **Evolution Patterns**: Detect development patterns (rapid growth, steady development, burst patterns)
- **Lifecycle Stages**: Track repos through inception → development → maturity → maintenance/archive
- **Activity Metrics**: Measure development velocity and activity levels

### 🔍 Deep Commit Analysis
- Commit frequency patterns
- Author contribution analysis
- Development rhythm detection
- Peak activity period identification
- Commit type classification (features, fixes, refactoring, etc.)

### 📈 Evolution Metrics
- Repository age and maturity tracking
- Days since last update
- Activity level classification
- Development stage identification
- Evolution velocity calculation

### 🎨 Visual Reports
- Interactive HTML dashboards
- Timeline visualizations
- JSON data exports
- Markdown reports

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd git_tracking

# Install dependencies (optional, for enhanced features)
pip install pygithub pandas plotly rich click
```

The tool works with minimal dependencies but installing the optional packages enables additional features.

## Usage

### Analyze GitHub Repositories

```bash
# Analyze all repositories for a GitHub user
python git_evolution_tracker.py --mode github --target bjpl

# Use default (analyzes bjpl repositories)
python git_evolution_tracker.py
```

### Analyze Local Repository

```bash
# Analyze current directory
python git_evolution_tracker.py --mode local

# Analyze specific repository
python git_evolution_tracker.py --mode local --target /path/to/repo
```

### Custom Workspace

```bash
# Specify output directory
python git_evolution_tracker.py --workspace /custom/output/path
```

## Output Structure

```
git_tracking/
├── data/
│   ├── repos/          # Repository data cache
│   └── timelines/      # Timeline analysis data
├── reports/
│   ├── evolution_analysis_*.json   # Detailed JSON analysis
│   └── evolution_report_*.html     # Interactive HTML reports
└── git_evolution_tracker.py        # Main tool
```

## Report Contents

Each analysis generates:

1. **JSON Analysis File**: Complete data including:
   - Repository metadata
   - Commit patterns
   - Evolution metrics
   - Activity distribution
   - Development insights

2. **HTML Report**: Visual dashboard with:
   - Repository cards with metrics
   - Activity level indicators
   - Development stage badges
   - Language distribution
   - Timeline visualization

## Evolution Metrics Explained

### Activity Levels
- **Very Active**: Updated within 7 days
- **Active**: Updated within 30 days
- **Moderate**: Updated within 90 days
- **Low**: Updated within 180 days
- **Dormant**: Not updated for 180+ days

### Development Stages
- **Inception**: < 30 days old
- **Early Development**: < 180 days old
- **Growing**: < 365 days old
- **Established**: Mature and active
- **Mature/Archived**: Old and inactive

### Evolution Velocity
Measures how actively a repository is evolving:
- Calculated as: `(age - days_since_update) / age`
- Range: 0.0 (dormant) to 1.0 (constantly active)

## Advanced Features

### Pattern Detection
The tool identifies various development patterns:
- **Rapid Development**: Frequent, consistent commits
- **Steady Development**: Regular, methodical progress
- **Burst Pattern**: Intense development periods followed by quiet periods
- **Maintenance Mode**: Occasional updates and fixes
- **Dormant**: No recent activity

### Commit Type Classification
Automatically categorizes commits:
- Features (feat, feature, add, new)
- Fixes (fix, bug, patch, resolve)
- Refactoring (refactor, clean, improve)
- Documentation (doc, readme, comment)
- Testing (test, spec)

### Timeline Events
Tracks significant events:
- Repository creation
- First and latest commits
- Version releases (detected from commit messages)
- Major milestones

## Development

This tool was developed using Flow Nexus as the development environment:
- Flow Nexus sandboxes for isolated testing
- Development agents for component building
- Workflow orchestration for testing

However, the final tool is completely standalone and doesn't require Flow Nexus to run.

## Examples

### Sample Output

```json
{
  "timestamp": "2025-09-14T17:30:55",
  "mode": "github",
  "target": "bjpl",
  "repositories": [
    {
      "name": "algorithms_and_data_structures",
      "language": "Python",
      "evolution": {
        "activity_level": "Very Active",
        "stage": "Established",
        "evolution_velocity": 0.95
      }
    }
  ],
  "summary": {
    "total_repos": 10,
    "total_stars": 0,
    "activity_distribution": {
      "Very Active": 8,
      "Active": 2
    }
  }
}
```

## Contributing

Feel free to contribute by:
- Adding new analysis metrics
- Improving pattern detection
- Enhancing visualizations
- Adding support for other version control systems

## License

MIT License - Use freely for your repository analysis needs!

---

Built with ❤️ for developers who want to understand their code's journey through time.