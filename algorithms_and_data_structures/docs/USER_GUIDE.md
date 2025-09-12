# User Guide - Interactive Algorithms Learning Platform

Welcome to the Interactive Algorithms Learning Platform! This comprehensive guide will help you navigate the system, maximize your learning experience, and master algorithms and data structures through intuitive analogies.

## 🚀 Getting Started

### System Requirements

- **Node.js**: Version 18.0 or higher
- **Terminal**: Any modern terminal (Windows Command Prompt, PowerShell, macOS Terminal, Linux Terminal)
- **Memory**: Minimum 512MB available RAM
- **Storage**: 100MB free disk space

### Installation

#### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd algorithms_and_data_structures

# Install dependencies
npm install

# Launch the platform
npm start
```

### First Launch

When you first launch the platform, you'll see:

```
╔════════════════════════════════════════════════════════════════╗
║     ALGORITHMS & DATA STRUCTURES: INTUITIVE LEARNING          ║
╚════════════════════════════════════════════════════════════════╝

Welcome! This platform teaches algorithms through everyday analogies.
No STEM background required - just curiosity and willingness to learn.
```

## 📚 Learning Modules Overview

The platform offers 11 comprehensive learning modules, each using real-world analogies to make complex concepts accessible.

### Foundation Level

#### 🏗️ Foundation: Mental Models
**Prerequisites**: None  
**Duration**: 20-30 minutes

Learn how to think about algorithms and data structures. This module establishes the fundamental mental frameworks you'll use throughout your learning journey.

### Data Structures

#### 📚 Arrays: Organizing Books
**Prerequisites**: Foundation  
**Duration**: 45 minutes

Learn arrays through the familiar concept of organizing books on a bookshelf.

**Real-World Analogy**: Think of arrays like a bookshelf where:
- Each shelf position has a specific number (index)
- You can quickly find any book if you know its position
- Inserting a book in the middle requires moving other books
- All books are arranged in a line

#### 🚂 Linked Lists: Train Cars
**Prerequisites**: Arrays  
**Duration**: 50 minutes

Understand linked lists through the analogy of connected train cars.

#### 🍽️ Stacks: Plate Dispensers
**Prerequisites**: Arrays  
**Duration**: 35 minutes

Master stacks through cafeteria plate dispenser analogy.

#### ☕ Queues: Coffee Shop Lines
**Prerequisites**: Arrays  
**Duration**: 35 minutes

Learn queues through the familiar coffee shop waiting line.

#### 🏢 Trees: Organization Charts
**Prerequisites**: Linked Lists  
**Duration**: 60 minutes

Understand trees through company organization charts.

#### 🗺️ Graphs: City Maps
**Prerequisites**: Trees  
**Duration**: 70 minutes

Master graphs through city map and social network analogies.

### Algorithms

#### 🎵 Sorting: Music Playlists
**Prerequisites**: Arrays  
**Duration**: 55 minutes

Learn sorting algorithms through music playlist organization.

#### 📱 Searching: Phone Contacts
**Prerequisites**: Arrays  
**Duration**: 40 minutes

Master searching through phone contact lookup analogy.

#### 🪆 Recursion: Nesting Dolls
**Prerequisites**: Foundation  
**Duration**: 50 minutes

Understand recursion through Russian nesting dolls (Matryoshka).

#### 🚗 Dynamic Programming: Road Trips
**Prerequisites**: Recursion  
**Duration**: 75 minutes

Learn dynamic programming through optimal road trip planning.

## 🎮 Interactive Features

### Navigation System

#### Main Menu Navigation
Use arrow keys or numbers to navigate:
- **↑/↓ or ↩**: Move between options
- **Enter**: Select current option
- **Escape**: Go back to previous menu
- **Ctrl+C**: Exit application

#### Keyboard Shortcuts

##### Global Shortcuts
- **F1**: Show help
- **F2**: Toggle theme (light/dark)
- **F3**: Show progress overview
- **F4**: Access settings
- **Ctrl+S**: Save progress
- **Ctrl+Q**: Quick exit

### Progress Tracking

#### Progress Dashboard
Access your progress dashboard anytime by:
1. Selecting "📊 View Progress" from main menu
2. Using **F3** keyboard shortcut
3. Typing `progress` in any module

The dashboard shows:
```
📊 YOUR LEARNING PROGRESS

┌────────────────────┬─────────────────┬───────────┐
│ Module             │ Status          │ Score     │
├────────────────────┼─────────────────┼───────────┤
│ foundation         │ ✓ Complete      │ 95        │
│ arrays             │ ✓ Complete      │ 87        │
│ linkedlists        │ In Progress     │ -         │
│ stacks             │ Not Started     │ -         │
└────────────────────┴─────────────────┴───────────┘

Total Score: 182 | Completion: 18%
```

## 🎯 Learning Strategies

### For Complete Beginners

#### Recommended Path
1. **Start with Foundation** - Essential for all subsequent learning
2. **Choose Arrays** - Most fundamental data structure
3. **Try Stacks or Queues** - Pick based on interest
4. **Progress to Trees** - Natural evolution from arrays
5. **Explore Sorting** - Practical and immediately useful

### For Intermediate Learners

#### Accelerated Path
1. **Review Foundation** - Refresh problem-solving approaches
2. **Data Structures**: Arrays → Linked Lists → Stacks/Queues → Trees → Graphs
3. **Algorithms**: Searching → Sorting → Recursion → Dynamic Programming

## 🛠️ Practice Problems

### Accessing Practice Mode

From the main menu, select **"🎯 Practice Challenges"** or use:
```bash
npm run challenges
```

### Problem Categories

#### Beginner Problems
- Array manipulation basics
- Simple string operations
- Stack/queue implementations
- Basic tree traversal

#### Intermediate Problems
- Two-pointer techniques
- Sliding window problems
- Binary search applications
- Graph traversal challenges

#### Advanced Problems
- Dynamic programming classics
- Complex tree algorithms
- Graph optimization
- System design scenarios

## 🔧 Troubleshooting

### Common Issues

#### Installation Problems

**Issue**: `npm install` fails with permissions error
**Solution**:
```bash
# On macOS/Linux:
sudo npm install

# On Windows (Run as Administrator):
npm install
```

**Issue**: Node.js version too old
**Solution**:
```bash
# Check current version
node --version

# Update Node.js (recommended: use nvm)
nvm install 18
nvm use 18
```

#### Runtime Problems

**Issue**: Terminal display is corrupted
**Solution**:
1. Clear terminal: `clear` or `Ctrl+L`
2. Resize terminal window
3. Restart the application
4. Try different terminal application

**Issue**: Progress not saving
**Solution**:
1. Check file permissions in project directory
2. Ensure sufficient disk space
3. Try manual save: `Ctrl+S`
4. Check `progress.json` file exists and is writable

---

**Happy Learning!** 🚀

This platform is designed to make algorithms and data structures accessible and enjoyable. Take your time, enjoy the journey, and don't hesitate to use the help system whenever you need guidance.

*Last Updated: September 2024 | Version: 1.0.0*