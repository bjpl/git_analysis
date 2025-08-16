# Spanish Learning Tools Collection

A comprehensive suite of applications and utilities designed to accelerate Spanish language acquisition through various learning methodologies.

## 📚 Overview

This collection represents the core of the workspace, containing 15+ specialized tools for different aspects of Spanish learning, from verb conjugation to vocabulary acquisition through multimedia content.

## 🎯 Learning Approach

The tools follow a multi-modal learning approach:
- **Active Practice**: Conjugation drills, subjunctive exercises
- **Spaced Repetition**: Anki flashcard generation and management
- **Contextual Learning**: YouTube transcripts, image descriptions
- **Immersive Content**: Celebrity quizzes, real-world scenarios

## 📁 Categories

### Core Applications
Full-featured desktop applications for structured learning:

#### MySpanishApp
- **Purpose**: Comprehensive session tracking for Spanish tutoring
- **Features**: Vocabulary tracking, grammar notes, progress monitoring
- **Tech Stack**: PyQt6, SQLite
- **Usage**: `poetry run python main.py`

#### Conjugation GUI
- **Purpose**: Interactive verb conjugation practice
- **Features**: All Spanish tenses, speed practice, progress tracking
- **Tech Stack**: PyQt5, SQLite
- **Special**: Includes task-based scenarios for real-world application

#### Subjunctive Practice
- **Purpose**: Master the challenging subjunctive mood
- **Features**: Contextual exercises, TBLT scenarios, session management
- **Tech Stack**: PyQt5
- **Distribution**: Includes standalone .exe for Windows

### Flashcard & Vocabulary Tools

#### Anki Generator
- **Purpose**: Automated flashcard creation from various sources
- **Features**: Multi-language templates, GPT-enhanced definitions
- **Output**: Anki-compatible CSV/TSV files
- **AI Integration**: OpenAI GPT for context generation

#### Add Tags
- **Purpose**: Semantic tagging for Spanish vocabulary
- **Features**: AI-powered categorization, batch processing
- **Tech Stack**: Transformers, Local LLMs
- **Use Case**: Organizing large vocabulary datasets

#### Merge GUI
- **Purpose**: Consolidate and manage vocabulary lists
- **Features**: Duplicate detection, smart merging, revision logging
- **Tech Stack**: PySimpleGUI
- **Output**: Clean, consolidated CSV files

### Media-Based Learning

#### YouTubeTranscriptGPT
- **Purpose**: Extract learning content from YouTube videos
- **Features**: Transcript processing, GPT analysis, vocabulary extraction
- **API Integration**: YouTube API, OpenAI GPT-4
- **Languages**: Focuses on Spanish content with English translations

#### Image-Questionnaire-GPT
- **Purpose**: Visual vocabulary learning
- **Features**: Image-based questions, vocabulary association
- **Data**: Uses target word lists with visual contexts
- **Memory**: Tracks used images to avoid repetition

#### Unsplash-Image-Search-GPT-Description
- **Purpose**: Generate Spanish descriptions for images
- **Features**: Image search, GPT descriptions, vocabulary extraction
- **APIs**: Unsplash, OpenAI Vision
- **Output**: Spanish phrases with English translations

#### Celebrity GUI
- **Purpose**: Cultural and language learning through celebrities
- **Features**: Wikipedia integration, quiz generation, extended bios
- **Learning**: Combines cultural knowledge with language practice

### Command Line Interface

#### LangTool
- **Purpose**: Comprehensive CLI for language learning
- **Features**: 
  - Chat mode with GPT-4
  - Role-play scenarios
  - Grammar drills
  - Session logging
  - Flashcard export
- **Architecture**: Modular design with multiple modes
- **Database**: SQLite for persistent storage
- **Customization**: Configurable presets and settings

### Utility Scripts

Collection of Python scripts for specific tasks:
- `optimize_anki_cards.py` - Format and enhance Anki cards
- `shuffle_subjunctive.py` - Randomize practice scenarios
- `convert_anki_csv.py` - Convert between formats
- `convert_to_csv.py` - Parse structured text to CSV

## 🚀 Quick Start Guide

### Prerequisites
```bash
# Install Python 3.10+
# Install Poetry
pip install poetry

# Set up OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

### Running Applications

Most apps follow this pattern:
```bash
cd [app-directory]
poetry install
poetry run python main.py
```

### For Scripts
```bash
python script_name.py [arguments]
```

## 🔧 Configuration

### API Keys Required
- **OpenAI API**: For GPT-powered features
- **Unsplash API**: For image search (specific apps)
- **YouTube API**: For transcript fetching

### Environment Setup
Create `.env` file in each project:
```env
OPENAI_API_KEY=sk-...
UNSPLASH_ACCESS_KEY=...
YOUTUBE_API_KEY=...
```

## 📊 Learning Workflow

### Recommended Daily Practice
1. **Morning**: Conjugation practice (15 min)
2. **Afternoon**: Vocabulary review with Anki (20 min)
3. **Evening**: Media content (YouTube/Images) (30 min)
4. **Weekly**: Subjunctive scenarios practice

### Content Pipeline
1. Find content (YouTube, images, texts)
2. Process with appropriate tool
3. Generate flashcards
4. Review in Anki
5. Track progress in MySpanishApp

## 🎓 Learning Strategies

### For Beginners
- Start with Conjugation GUI for verb basics
- Use Image tools for vocabulary building
- Simple flashcards with Anki Generator

### For Intermediate
- Focus on Subjunctive Practice
- Process YouTube content for real Spanish
- Use LangTool for conversation practice

### For Advanced
- Celebrity GUI for cultural immersion
- Complex role-play scenarios in LangTool
- Process native content with YouTubeTranscriptGPT

## 📈 Progress Tracking

Most applications include progress tracking:
- Session logs in SQLite databases
- Export capabilities for analysis
- Visual progress indicators
- Performance metrics

## 🤝 Integration Points

### Data Flow
```
Content Sources → Processing Tools → Anki Generator → Anki App
                ↓                  ↓
            Session Logs    Progress Tracking
```

### Shared Resources
- Common vocabulary lists in CSV format
- Shared prompt templates
- Unified tagging system
- Consistent data schemas

## 🔒 Data Privacy

- All data stored locally
- No automatic cloud sync
- API calls only when explicitly triggered
- Session data remains private

## 📝 Development Notes

### Common Patterns
- PyQt for desktop GUIs
- SQLite for local storage
- Poetry for dependency management
- OpenAI integration for AI features

### Code Style
- PEP 8 compliance
- Type hints where applicable
- Comprehensive docstrings
- Modular architecture

## 🚧 Known Issues

- Some tools require Windows for full functionality
- API rate limits may affect batch processing
- Large vocabulary files may slow down some operations

## 🔮 Future Enhancements

- Unified dashboard across all tools
- Cloud sync capability (optional)
- Mobile companion apps
- Voice recognition integration
- More language support beyond Spanish

## 📚 Resources

### Recommended Companion Tools
- Anki Desktop/Mobile for flashcard review
- Spanish dictionaries (RAE, SpanishDict)
- Language exchange platforms

### Learning Materials
- Structured curriculum integration pending
- Custom course creation tools planned
- Community-shared content library future goal

---

*This collection represents 70% of the Project Workspace and is under active development*