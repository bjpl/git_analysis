# Questionnaire System Usage Guide

## Overview

This simplified questionnaire system extracts the core dialog and session management functionality from the original PyQt6 image-questionnaire-gpt project. It provides:

1. **Question/Answer Dialog System** - Interactive dialogs for presenting questions and collecting responses
2. **Session Logging to CSV** - Automatic logging of all responses with timestamps and metadata
3. **Progress Tracking** - Visual progress indicators and time estimation
4. **Settings Management** - Configurable session parameters and preferences

## Quick Start

### 1. Running the Application

```bash
cd src
python questionnaire_ui.py
```

### 2. Loading Questions

- Click "Load Questions" to select a text file containing your questions
- Questions can be formatted in several ways:
  - One question per line
  - Questions separated by double newlines
  - Numbered questions (1., 2., etc.)

### 3. Starting a Session

- Click "Start Questionnaire" after loading questions
- Each question will appear in a dialog box
- You can:
  - **Submit Answer**: Type your response and click "Submit Answer"
  - **Skip**: Skip the question (marked as [SKIPPED])
  - **Cancel**: End the questionnaire session

### 4. Viewing Results

- Progress and responses are displayed in the main window
- Session data is automatically saved to CSV files in the configured directory

## File Structure

```
src/
├── questionnaire_core.py    # Core session management and logging
├── questionnaire_ui.py      # Tkinter-based user interface
examples/
├── sample_questions.txt     # Example questions file
sessions/                    # Default session logs directory
├── session_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.csv
├── session_YYYYMMDD_HHMMSS_YYYYMMDD_HHMMSS.json
```

## Session Data Format

### CSV Output Structure

Each session generates a CSV file with:

1. **Session Metadata**:
   - Session ID
   - Start/End times
   - Total and answered question counts

2. **Question Responses**:
   - Question ID and text
   - User's answer
   - Timestamp
   - Processing time in milliseconds
   - Additional metadata (skipped status, etc.)

### Example CSV Content

```csv
Session Metadata
Session ID,session_20250825_143022
Start Time,2025-08-25T14:30:22.123456
End Time,2025-08-25T14:35:45.789012
Total Questions,5
Answered Questions,4

Question Responses
Question ID,Question Text,Answer,Timestamp,Processing Time (ms),Additional Data
0,What is your name?,John Doe,2025-08-25T14:30:30.123456,8234,"{""skipped"": false}"
1,How would you describe your mood?,[SKIPPED],2025-08-25T14:30:35.234567,2156,"{""skipped"": true}"
```

## Settings Configuration

Access settings via the "Settings" button to configure:

- **Session Directory**: Where session files are saved
- **Auto Save**: Automatically save settings changes
- **Show Progress**: Display progress indicators
- **Processing Timeout**: Maximum time for processing operations
- **Enable Timestamps**: Include timestamps in responses
- **Max Sessions to Keep**: Automatic cleanup threshold

## Question File Formats

### Format 1: Simple Line-by-Line
```
What is your name?
How old are you?
What are your hobbies?
```

### Format 2: Double-Newline Separated
```
What is your favorite color and why do you like it?

Describe a memorable experience from your childhood.

What are your career goals for the next five years?
```

### Format 3: Numbered Questions
```
1. What motivates you to get up each morning?

2. If you could learn any skill instantly, what would it be?

3. How do you prefer to spend your free time?
```

## Features Extracted from Original System

### Core Components Retained:
- **Session Management**: Complete session lifecycle tracking
- **CSV Logging**: Structured data export for analysis
- **Progress Tracking**: Visual and time-based progress indicators
- **Settings System**: Configurable application behavior
- **Question Dialog**: Modal dialogs for question presentation

### Simplifications Made:
- **Removed YouTube API dependencies**: No video transcript processing
- **Removed PyQt6**: Replaced with Tkinter for broader compatibility
- **Removed OpenAI integration**: Focus on data collection only
- **Simplified UI**: Streamlined interface without complex layouts
- **Removed annotation system**: Focused on basic Q&A workflow

### Threading and Responsiveness:
- Background threading for questionnaire execution
- Non-blocking UI during question presentation
- Progress updates without freezing the interface

## Error Handling

The system includes robust error handling for:
- Invalid question file formats
- Session save failures
- UI interaction errors
- File system access issues

## Extensibility

The modular design allows for easy extension:

1. **Custom Question Types**: Extend `QuestionDialog` for specialized inputs
2. **Additional Export Formats**: Add methods to `SessionManager`
3. **Advanced Progress Tracking**: Extend `ProgressTracker` with new metrics
4. **Integration Points**: Core classes can be imported and used in other applications

## Performance Considerations

- Sessions are saved incrementally to prevent data loss
- Old session files are automatically cleaned up based on settings
- Memory usage is optimized for long questionnaire sessions
- UI remains responsive during data processing

## Use Cases

This questionnaire system is ideal for:

- **Research Studies**: Collecting structured survey responses
- **User Feedback**: Gathering detailed user experience data
- **Training Data Collection**: Building datasets for ML applications
- **Interview Assistance**: Standardizing interview question presentation
- **Educational Assessments**: Creating interactive learning evaluations