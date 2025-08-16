# LangTool

**LangTool** is a terminal-based language learning assistant powered by GPT-4o. It helps you:

- Chat and role-play with realistic conversational presets (WhatsApp, Slack).  
- Run grammar drills and quizzes.  
- Collect flashcards and export them to CSV/TSV for Anki.  
- Log tutoring sessions and video/series watch notes.  
- Customize settings on the fly (API key, theme, language, export options).  
- Navigate efficiently via keyboard shortcuts, command palette, and side panels.  

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/langtool.git
   cd langtool

    Install dependencies

poetry install

Configure

    Copy .env.example to .env and add your OpenAI API key:

        cp .env.example .env
        # Then edit .env and set OPENAI_API_KEY

        Or set OPENAI_API_KEY in langtool/config.toml under [api].

Usage

Run the CLI via the langtool command (installed by Poetry):

# Start a chat session
langtool chat

# Role-play with a preset
langtool roleplay --preset "Informal WhatsApp"

# Grammar drills
langtool drills

# Manage logs
langtool logs tutor   # Tutor session logs
langtool logs video   # Video/series logs

# Export flashcards
langtool export

# Edit runtime settings
langtool settings

# (Future) Show dashboard summary
langtool dashboard

Development

    Run tests:

pytest

Lint and type-check:

    flake8
    mypy

Contributing

Contributions are welcome! Please fork, create a feature branch, and submit a pull request.
License

This project is licensed under the MIT License. See LICENSE for details.