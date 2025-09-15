# Git Evolution Tracker 🔍

A comprehensive repository analysis and evolution tracking system that provides deep insights into git repository development patterns, health metrics, and collaborative dynamics.

## Features ✨

### 🎯 Core Capabilities
- **Repository Evolution Analysis**: Track complete development timeline from inception to current state
- **Health Scoring System**: Comprehensive 0-100 health score across multiple dimensions
- **Interactive HTML Reports**: Beautiful, responsive reports with Chart.js and D3.js visualizations
- **Multi-Repository Support**: Analyze multiple repositories simultaneously
- **Pattern Detection**: Automatically identify development patterns and phases
- **Contributor Analytics**: Deep insights into collaboration and contribution patterns

### 📊 Analysis Dimensions

#### 1. Commit Analysis
- Total commits, merge commits, and commit frequency
- Temporal patterns (hourly, daily, weekly, monthly)
- Commit size distribution
- Development velocity tracking

#### 2. File Evolution
- Most modified files identification
- Stable core files detection
- File churn analysis
- Directory growth patterns
- Language distribution

#### 3. Contributor Metrics
- Contribution distribution analysis
- Collaboration graph generation
- Expertise area identification
- Consistent contributor tracking

#### 4. Activity Patterns
- Development phase identification
- Sprint detection
- Seasonal pattern analysis
- Momentum tracking
- Activity heatmaps

#### 5. Health Scoring
- **Activity Score**: Repository activity level
- **Maintainability Score**: Code maintainability indicators
- **Collaboration Score**: Team collaboration health
- **Documentation Score**: Documentation coverage
- **Stability Score**: Codebase stability

## Installation 📦

```bash
# Clone the repository
git clone https://github.com/yourusername/git-evolution-tracker.git
cd git-evolution-tracker

# Install dependencies (if any)
pip install -r requirements.txt  # Coming soon
```

## Usage 🚀

### Generate Enhanced Report

```bash
# Analyze current directory
python generate_enhanced_report.py

# Analyze specific repository
python generate_enhanced_report.py /path/to/repository

# With verbose output
python generate_enhanced_report.py /path/to/repository --verbose
```

### Output

Reports are generated in the `reports/` directory with timestamp:
- `enhanced_evolution_report_YYYYMMDD_HHMMSS.html`

The report includes:
- Interactive visualizations
- Health dashboard
- Comprehensive metrics
- Timeline analysis
- Actionable insights

## Project Structure 📁

```
git-evolution-tracker/
├── src/
│   ├── core/
│   │   ├── enhanced_evolution_tracker.py  # Main analysis engine
│   │   ├── evolution_tracker.py          # Evolution tracking logic
│   │   ├── git_evolution_tracker.py      # Git-specific operations
│   │   └── multi_repo_analyzer.py        # Multi-repo analysis
│   ├── orchestrators/
│   │   └── flow_nexus_orchestrator.py    # Orchestration logic
│   ├── visualizers/
│   │   └── dashboard_generator.py        # Dashboard generation
│   ├── agents/                           # Analysis agents
│   └── analyzers/                        # Specialized analyzers
├── config/                                # Configuration files
├── data/                                  # Data storage
│   ├── repos/                            # Repository data
│   └── timelines/                        # Timeline data
├── reports/                               # Generated reports
├── generate_enhanced_report.py           # Main entry point
├── README.md                              # Documentation
└── .gitignore                            # Git ignore rules
```

## Report Features 🎨

### Interactive Visualizations
- **Commit Frequency Chart**: Line chart showing commit patterns over time
- **Contributor Distribution**: Donut chart of contribution percentages
- **Health Score Circle**: Circular progress indicator for repository health
- **Activity Heatmap**: GitHub-style contribution graph
- **Language Distribution**: Bar chart of programming languages

### Responsive Design
- Mobile-optimized layout
- Smooth animations and transitions
- Interactive hover effects
- Modern gradient design
- Card-based information architecture

### Insights & Recommendations
- Automated pattern detection
- Development phase identification
- Health improvement suggestions
- Milestone tracking
- Evolution story generation

## Evolution Metrics Explained 📈

### Activity Levels
- **Very Active**: Updated within 7 days
- **Active**: Updated within 30 days
- **Moderate**: Updated within 90 days
- **Low**: Updated within 180 days
- **Dormant**: Not updated for 180+ days

### Development Patterns
- **Rapid Development**: Frequent, consistent commits
- **Steady Development**: Regular, methodical progress
- **Burst Pattern**: Intense development periods followed by quiet periods
- **Maintenance Mode**: Occasional updates and fixes
- **Dormant**: No recent activity

### Lifecycle Stages
- **Inception**: < 30 days old
- **Early Development**: < 90 days old, < 50 commits
- **Active Growth**: Rapid or steady development pattern
- **Iterative Evolution**: Burst pattern development
- **Mature**: Stable with maintenance mode
- **Archived/Complete**: Dormant with 100+ commits
- **Abandoned**: Dormant with < 100 commits

### Evolution Velocity
- **Hyperspeed**: > 10 commits/week average
- **Fast**: > 5 commits/week
- **Moderate**: > 2 commits/week
- **Slow**: > 0.5 commits/week
- **Glacial**: < 0.5 commits/week

## Advanced Features 🔧

### Customization
- Configurable analysis depth
- Custom health scoring weights
- Flexible report templates
- Extensible analyzer framework

### Performance
- Efficient git command execution
- Smart caching for expensive operations
- Parallel processing support
- Incremental analysis capability

## Examples 📝

### Basic Usage
```python
from src.core.enhanced_evolution_tracker import EnhancedEvolutionTracker

# Initialize tracker
tracker = EnhancedEvolutionTracker('/path/to/repo')

# Perform analysis
analysis = tracker.analyze_repository()

# Generate HTML report
report_path = tracker.generate_html_report(analysis)
print(f"Report generated: {report_path}")
```

### Multi-Repository Analysis
```python
from src.core.multi_repo_analyzer import MultiRepoAnalyzer

# Analyze multiple repositories
analyzer = MultiRepoAnalyzer()
results = analyzer.analyze_repositories([
    '/path/to/repo1',
    '/path/to/repo2',
    '/path/to/repo3'
])
```

## Requirements 📋

- Python 3.7+
- Git (accessible via command line)
- Modern web browser for viewing reports

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

Areas for contribution:
- Adding new analysis metrics
- Improving pattern detection algorithms
- Enhancing visualizations
- Adding support for other VCS (SVN, Mercurial)
- Performance optimizations
- Additional export formats (PDF, Markdown)

## License 📄

MIT License - feel free to use this tool for your projects!

## Roadmap 🗺️

- [ ] Add support for GitHub API integration
- [ ] Implement real-time monitoring
- [ ] Add export to PDF functionality
- [ ] Create CLI with rich terminal output
- [ ] Add support for GitLab and Bitbucket
- [ ] Implement machine learning for pattern prediction
- [ ] Add team collaboration features
- [ ] Create web-based dashboard
- [ ] Add CI/CD integration
- [ ] Implement webhook support

## Support 💬

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for developers who love understanding their code evolution**