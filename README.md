# GHD - GitHub Data Tool

A powerful CLI tool for tracking and analyzing GitHub repository activity, providing insights into development patterns, commit history, and project metrics.

## 🚀 Features

- **Repository Analytics** - Track commits, PRs, issues, and contributor activity
- **Development Insights** - Analyze coding patterns and project velocity
- **Daily Summaries** - Get quick overviews of recent repository activity
- **Focus Mode** - Deep dive into specific repositories or time periods
- **Rich Terminal UI** - Beautiful, interactive displays with charts and tables
- **Caching** - Smart caching for improved performance
- **Multiple Output Formats** - Export data as JSON, CSV, or formatted reports

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/bjpl/ghd.git
cd ghd

# Install using pip
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## 🔧 Configuration

1. **Set up your GitHub token**:
   ```bash
   # Create a .env file
   cp .env.example .env

   # Add your GitHub personal access token
   echo "GITHUB_TOKEN=your_token_here" >> .env
   ```

2. **Generate a GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` and `read:user` permissions
   - Copy the token to your `.env` file

## 💻 Usage

### Basic Commands

```bash
# Show today's activity across all repos
ghd today

# Get a recap of recent activity
ghd recap

# List all repositories
ghd repos

# Focus on a specific repository
ghd focus owner/repo

# Show the dashboard
ghd dashboard

# Clean up cache
ghd cleanup
```

### Examples

```bash
# View activity for the last week
ghd recap --days 7

# Focus on a specific repo with detailed stats
ghd focus bjpl/ghd --detailed

# Export repository data as JSON
ghd repos --format json > repos.json

# Get help for any command
ghd help
ghd help focus
```

## 🎨 Features in Detail

### Today Command
Shows a summary of today's GitHub activity including:
- Commits pushed
- Pull requests opened/merged
- Issues created/closed
- Code review activity

### Recap Command
Provides a comprehensive overview of recent activity:
- Contribution graphs
- Language statistics
- Most active repositories
- Contributor leaderboard

### Focus Command
Deep dive into a specific repository:
- Commit history analysis
- PR/Issue metrics
- Contributor statistics
- Code frequency graphs
- Activity heatmaps

### Dashboard
Interactive terminal dashboard showing:
- Real-time activity feed
- Repository health metrics
- Trending repositories
- Personal productivity stats

## 🏗️ Architecture

```
ghd/
├── src/
│   └── ghd/
│       ├── api/          # GitHub API integration
│       ├── commands/     # CLI command implementations
│       ├── formatters/   # Output formatting and display
│       ├── utils/        # Utility functions
│       └── cli.py        # Main CLI entry point
├── docs/                 # Documentation
├── tests/               # Test suite
└── .env.example         # Environment configuration template
```

## 🧪 Development

```bash
# Run tests
pytest

# Run with debug logging
GHD_DEBUG=1 ghd today

# Development installation
pip install -e ".[dev]"

# Code formatting
black src/
flake8 src/
```

## 📊 Data Storage

GHD stores cached data and configurations in:
- **Unix/Linux**: `~/.ghd/`
- **Windows**: `%APPDATA%\ghd\`
- **macOS**: `~/Library/Application Support/ghd/`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [git_analysis](https://github.com/bjpl/git_analysis) - Repository for ad-hoc GitHub analysis
- [GitHub CLI](https://cli.github.com/) - Official GitHub command-line tool

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note**: This tool requires a GitHub personal access token to function. Ensure you keep your token secure and never commit it to version control.