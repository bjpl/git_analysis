# ⚙️ Configuration Guide: Interactive Algorithms Learning Platform

## Table of Contents
- [Configuration Overview](#-configuration-overview)
- [Environment Setup](#-environment-setup)
- [User Preferences](#-user-preferences)
- [Learning Settings](#-learning-settings)
- [Display Configuration](#-display-configuration)
- [SPARC Integration](#-sparc-integration)
- [Advanced Settings](#-advanced-settings)
- [Environment Variables](#-environment-variables)

## 🎯 Configuration Overview

The Interactive Algorithms Learning Platform uses a hierarchical configuration system that allows customization at multiple levels:

```
System Defaults → Environment Config → User Config → Session Overrides
      ↓                   ↓                ↓              ↓
   Built-in         .env files      config.json    CLI flags
```

### Configuration File Locations

```bash
# Global configuration (system-wide)
/etc/algorithms-learning/config.json

# User configuration (user-specific)
~/.algorithms-learning/config.json
~/.config/algorithms-learning/config.json  # Linux XDG

# Project configuration (project-specific)  
./algorithms-learning.config.json
./config/settings.json

# Environment variables
.env
.env.local
.env.development
.env.production
```

### Configuration Loading Priority

1. **CLI Flags** (highest priority)
2. **Environment Variables**
3. **Project Configuration Files**
4. **User Configuration Files**
5. **System Configuration Files**
6. **Built-in Defaults** (lowest priority)

## 🌍 Environment Setup

### Development Environment

**Create Development Configuration:**
```bash
# Copy example configuration
cp .env.example .env.development

# Edit with your preferences
nano .env.development
```

**Example Development Configuration:**
```bash
# .env.development

# Environment
NODE_ENV=development
LOG_LEVEL=debug
DEBUG_MODE=true

# Learning Settings
DEFAULT_DIFFICULTY=beginner
ENABLE_HINTS=true
ENABLE_ANALYTICS=false
AUTO_SAVE_PROGRESS=true

# Display Settings
COLOR_OUTPUT=true
ANIMATION_SPEED=normal
SHOW_PROGRESS_BARS=true
PAGE_SIZE=25

# SPARC Integration
ENABLE_SPARC_AGENTS=true
MAX_CONCURRENT_AGENTS=4
AGENT_TIMEOUT=300
COORDINATION_MODE=mesh

# Performance
CACHE_SIZE=100
PERFORMANCE_TRACKING=true
MEMORY_LIMIT=512

# Paths
DATA_DIRECTORY=./data
LOG_DIRECTORY=./logs
CACHE_DIRECTORY=./cache
```

### Production Environment

**Production Configuration:**
```bash
# .env.production

# Environment
NODE_ENV=production
LOG_LEVEL=warn
DEBUG_MODE=false

# Performance Optimizations
CACHE_SIZE=1000
PERFORMANCE_TRACKING=false
MEMORY_LIMIT=1024

# Security
DISABLE_DEBUG_COMMANDS=true
SANITIZE_USER_INPUT=true

# Analytics (if enabled)
ANALYTICS_ENDPOINT=https://analytics.example.com/api
ANALYTICS_API_KEY=your-api-key-here
```

### Testing Environment

**Test Configuration:**
```bash
# .env.test

NODE_ENV=test
LOG_LEVEL=error
ENABLE_ANALYTICS=false
AUTO_SAVE_PROGRESS=false
CACHE_SIZE=10
MEMORY_LIMIT=256
```

## 👤 User Preferences

### Personal Settings Configuration

**Config File Location:** `~/.algorithms-learning/config.json`

```json
{
  "user": {
    "name": "Alex Student",
    "email": "alex@example.com",
    "preferredLanguage": "en",
    "timezone": "America/New_York",
    "theme": "dark",
    "difficulty": "intermediate"
  },
  
  "learning": {
    "enableHints": true,
    "enableAnalytics": false,
    "autoSaveProgress": true,
    "reminderInterval": 30,
    "studyGoal": {
      "hoursPerWeek": 5,
      "modulesPerMonth": 2
    },
    "learningStyle": "visual"
  },
  
  "accessibility": {
    "highContrast": false,
    "largeText": false,
    "reduceMotion": false,
    "screenReader": false,
    "keyboardNavigation": true
  },
  
  "notifications": {
    "studyReminders": true,
    "achievementAlerts": true,
    "progressReports": "weekly"
  }
}
```

### Command-Line Configuration

**Set User Preferences via CLI:**
```bash
# Set basic preferences
npm run config set user.name "Your Name"
npm run config set user.difficulty "intermediate"
npm run config set user.theme "dark"

# Learning preferences
npm run config set learning.enableHints true
npm run config set learning.reminderInterval 60

# Display preferences
npm run config set display.colorOutput true
npm run config set display.animationSpeed "fast"

# View current configuration
npm run config list

# Reset to defaults
npm run config reset
```

### Interactive Configuration Wizard

**Run Configuration Setup:**
```bash
npm run setup
```

**Configuration Wizard Flow:**
```
🎯 Welcome to Algorithm Learning Platform Setup!

Step 1: Personal Information
- Name: [Your Name]
- Learning Goal: [ ] Job Interview Prep
                 [x] General Knowledge  
                 [ ] Academic Study
                 [ ] Professional Development

Step 2: Learning Preferences
- Difficulty Level: [Beginner] [Intermediate] [Advanced]
- Learning Style: [Visual] [Hands-on] [Reading] [Mixed]
- Pace: [Self-paced] [Structured] [Intensive]

Step 3: Display Settings
- Theme: [Light] [Dark] [Auto]
- Colors: [Enabled] [Disabled]
- Animations: [Slow] [Normal] [Fast] [Disabled]

Step 4: Advanced Options
- Analytics: [Enable] [Disable]
- SPARC Agents: [Enable] [Disable]
- Auto-save: [Enable] [Disable]

✅ Configuration saved to ~/.algorithms-learning/config.json
```

## 📚 Learning Settings

### Difficulty Configuration

**Automatic Difficulty Adjustment:**
```json
{
  "learning": {
    "adaptiveDifficulty": {
      "enabled": true,
      "adjustmentThreshold": 0.7,
      "maxAdjustmentSteps": 2,
      "evaluationWindow": 5
    },
    
    "difficultyLevels": {
      "beginner": {
        "conceptExplanationDetail": "high",
        "codeExamples": "extensive",
        "practiceProblems": "guided",
        "hintsAvailable": true,
        "timeoutLimits": "generous"
      },
      "intermediate": {
        "conceptExplanationDetail": "medium",
        "codeExamples": "moderate",
        "practiceProblems": "independent",
        "hintsAvailable": "limited",
        "timeoutLimits": "standard"
      },
      "advanced": {
        "conceptExplanationDetail": "low",
        "codeExamples": "minimal",
        "practiceProblems": "challenging",
        "hintsAvailable": false,
        "timeoutLimits": "strict"
      }
    }
  }
}
```

### Progress Tracking Configuration

```json
{
  "progress": {
    "trackingEnabled": true,
    "metrics": {
      "timeSpent": true,
      "conceptsMastered": true,
      "problemsAttempted": true,
      "problemsSolved": true,
      "averageScore": true,
      "learningVelocity": true
    },
    
    "persistence": {
      "autoSave": true,
      "saveInterval": 30,
      "backupEnabled": true,
      "backupInterval": "daily",
      "retentionPeriod": "1year"
    },
    
    "analytics": {
      "enabled": false,
      "anonymized": true,
      "includePersonalData": false,
      "reportingFrequency": "weekly"
    }
  }
}
```

### Spaced Repetition Settings

```json
{
  "spacedRepetition": {
    "enabled": true,
    "algorithm": "sm2",
    "intervals": [1, 3, 7, 14, 30, 90],
    "reviewThreshold": 0.8,
    "
    
    Schedule": {
      "dailyReviewLimit": 20,
      "reviewTimeSlots": ["morning", "afternoon", "evening"],
      "weekendReviews": true
    }
  }
}
```

## 🎨 Display Configuration

### Theme Configuration

**Available Themes:**
```json
{
  "themes": {
    "light": {
      "background": "white",
      "foreground": "black",
      "accent": "#007acc",
      "success": "#28a745",
      "warning": "#ffc107",
      "error": "#dc3545",
      "info": "#17a2b8"
    },
    
    "dark": {
      "background": "#1e1e1e",
      "foreground": "#d4d4d4",
      "accent": "#569cd6",
      "success": "#4ec9b0",
      "warning": "#dcdcaa",
      "error": "#f44747",
      "info": "#9cdcfe"
    },
    
    "high-contrast": {
      "background": "black",
      "foreground": "white",
      "accent": "yellow",
      "success": "green",
      "warning": "orange",
      "error": "red",
      "info": "cyan"
    }
  }
}
```

### Visual Elements Configuration

```json
{
  "display": {
    "console": {
      "colorOutput": true,
      "unicodeSupport": true,
      "pageSize": 25,
      "wordWrap": true,
      "lineNumbers": false
    },
    
    "animations": {
      "enabled": true,
      "speed": "normal",
      "types": {
        "typewriter": true,
        "progressBars": true,
        "transitions": true,
        "sorting": true
      }
    },
    
    "visualization": {
      "asciiArt": true,
      "diagrams": true,
      "charts": true,
      "trees": "unicode",
      "graphs": "simple"
    },
    
    "feedback": {
      "soundEffects": false,
      "visualCues": true,
      "celebrationAnimations": true,
      "progressIndicators": true
    }
  }
}
```

### Accessibility Settings

```json
{
  "accessibility": {
    "screenReader": {
      "enabled": false,
      "verbosity": "medium",
      "announceProgress": true,
      "describeVisuals": true
    },
    
    "visual": {
      "highContrast": false,
      "largeText": false,
      "reducedMotion": false,
      "focusIndicators": true
    },
    
    "keyboard": {
      "navigationEnabled": true,
      "shortcuts": true,
      "tabNavigation": true,
      "escapeKey": true
    },
    
    "timing": {
      "extendedTimeouts": false,
      "pauseOnFocus": true,
      "noTimeLimit": false
    }
  }
}
```

## 🤖 SPARC Integration

### Agent Configuration

```json
{
  "sparc": {
    "enabled": true,
    "agentPool": {
      "maxConcurrentAgents": 6,
      "agentTimeout": 300,
      "retryAttempts": 3,
      "coordinationMode": "mesh"
    },
    
    "agentTypes": {
      "specification": {
        "enabled": true,
        "priority": "high",
        "resources": {
          "cpu": "normal",
          "memory": "normal"
        }
      },
      "pseudocode": {
        "enabled": true,
        "priority": "high",
        "resources": {
          "cpu": "normal", 
          "memory": "normal"
        }
      },
      "coder": {
        "enabled": true,
        "priority": "medium",
        "resources": {
          "cpu": "high",
          "memory": "high"
        }
      },
      "tester": {
        "enabled": true,
        "priority": "medium",
        "testFrameworks": ["node:test", "jest"],
        "coverageThreshold": 0.8
      },
      "reviewer": {
        "enabled": true,
        "priority": "low",
        "checkTypes": ["syntax", "logic", "performance", "security"]
      }
    }
  }
}
```

### Workflow Configuration

```json
{
  "workflows": {
    "moduleCreation": {
      "phases": ["specification", "pseudocode", "architecture", "implementation", "testing"],
      "parallelExecution": true,
      "checkpoints": true,
      "rollbackEnabled": true
    },
    
    "problemSolving": {
      "phases": ["analysis", "design", "implementation", "optimization"],
      "adaptiveApproach": true,
      "collaborativeMode": false
    }
  }
}
```

### Memory Management

```json
{
  "memory": {
    "crossSessionMemory": {
      "enabled": true,
      "persistenceMode": "sqlite",
      "maxSize": "100MB",
      "compressionEnabled": true
    },
    
    "agentMemory": {
      "sharedKnowledge": true,
      "memoryLimitsPerAgent": "10MB",
      "memoryCleanupInterval": "1hour"
    }
  }
}
```

## ⚡ Advanced Settings

### Performance Configuration

```json
{
  "performance": {
    "caching": {
      "enabled": true,
      "strategy": "lru",
      "maxSize": 1000,
      "ttl": 3600,
      "persistToDisk": false
    },
    
    "optimization": {
      "lazyLoading": true,
      "preloadModules": ["arrays", "linkedlists"],
      "memoryLimit": "512MB",
      "cpuThrottling": false
    },
    
    "monitoring": {
      "performanceTracking": true,
      "memoryProfiling": false,
      "cpuProfiling": false,
      "metricsExport": "json"
    }
  }
}
```

### Logging Configuration

```json
{
  "logging": {
    "level": "info",
    "format": "json",
    "outputs": ["console", "file"],
    
    "file": {
      "path": "./logs/app.log",
      "maxSize": "10MB",
      "maxFiles": 5,
      "rotationPolicy": "daily"
    },
    
    "categories": {
      "learning": "info",
      "sparc": "debug",
      "performance": "warn",
      "security": "error"
    }
  }
}
```

### Security Settings

```json
{
  "security": {
    "inputSanitization": {
      "enabled": true,
      "strictMode": false,
      "allowedPatterns": ["^[a-zA-Z0-9\\s._-]+$"],
      "maxInputLength": 1000
    },
    
    "codeExecution": {
      "sandboxed": true,
      "timeoutMs": 5000,
      "memoryLimitMB": 50,
      "allowedModules": ["fs", "path", "util"],
      "blockedPatterns": ["eval", "Function", "require"]
    },
    
    "dataPrivacy": {
      "anonymizeData": true,
      "encryptStoredData": false,
      "dataRetentionDays": 365,
      "allowDataExport": true
    }
  }
}
```

## 🌐 Environment Variables

### Core Environment Variables

```bash
# Application Environment
NODE_ENV=development|production|test
LOG_LEVEL=error|warn|info|debug
DEBUG_MODE=true|false

# User Settings
USER_NAME="Your Name"
USER_DIFFICULTY=beginner|intermediate|advanced
USER_THEME=light|dark|auto
USER_LANGUAGE=en|es|fr|de

# Learning Configuration
ENABLE_HINTS=true|false
ENABLE_ANALYTICS=true|false
AUTO_SAVE_PROGRESS=true|false
REMINDER_INTERVAL=30

# Display Settings
COLOR_OUTPUT=true|false
ANIMATION_SPEED=slow|normal|fast
SHOW_PROGRESS_BARS=true|false
PAGE_SIZE=25

# Performance Settings
CACHE_SIZE=100
MEMORY_LIMIT=512
PERFORMANCE_TRACKING=true|false

# SPARC Configuration
ENABLE_SPARC_AGENTS=true|false
MAX_CONCURRENT_AGENTS=6
AGENT_TIMEOUT=300
COORDINATION_MODE=mesh|hierarchical|star

# File Paths
DATA_DIRECTORY=./data
LOG_DIRECTORY=./logs  
CACHE_DIRECTORY=./cache
CONFIG_DIRECTORY=./config

# External Services (Optional)
ANALYTICS_ENDPOINT=https://analytics.example.com/api
ANALYTICS_API_KEY=your-api-key
CLOUD_BACKUP_URL=https://backup.example.com
```

### Platform-Specific Variables

**Windows:**
```cmd
REM Windows Command Prompt
set NODE_ENV=development
set COLOR_OUTPUT=true
set USER_THEME=dark

REM PowerShell
$env:NODE_ENV = "development"
$env:COLOR_OUTPUT = "true"
$env:USER_THEME = "dark"
```

**macOS/Linux:**
```bash
# Bash/Zsh
export NODE_ENV=development
export COLOR_OUTPUT=true  
export USER_THEME=dark

# Fish Shell
set -x NODE_ENV development
set -x COLOR_OUTPUT true
set -x USER_THEME dark
```

### Docker Environment Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  learning-platform:
    build: .
    environment:
      - NODE_ENV=production
      - COLOR_OUTPUT=true
      - ENABLE_SPARC_AGENTS=true
      - CACHE_SIZE=1000
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    ports:
      - "3000:3000"
```

## 🔧 Configuration Management

### Dynamic Configuration Updates

**Runtime Configuration Changes:**
```bash
# Update configuration without restart
npm run config set user.theme "light"
npm run config set display.animationSpeed "fast"

# Reload configuration
npm run config reload

# Validate configuration
npm run config validate
```

### Configuration Backup and Restore

```bash
# Backup current configuration
npm run config backup > ~/my-config-backup.json

# Restore configuration from backup
npm run config restore ~/my-config-backup.json

# Export configuration for sharing
npm run config export --format=json > team-config.json

# Import shared configuration
npm run config import team-config.json
```

### Configuration Profiles

**Create Multiple Profiles:**
```bash
# Create profiles for different scenarios
npm run config profile create "interview-prep"
npm run config profile create "casual-learning"
npm run config profile create "teaching-mode"

# Switch between profiles
npm run config profile use "interview-prep"

# List available profiles
npm run config profile list
```

**Profile Configurations:**
```json
{
  "profiles": {
    "interview-prep": {
      "difficulty": "advanced",
      "enableHints": false,
      "focusAreas": ["algorithms", "complexity-analysis"],
      "practiceIntensity": "high"
    },
    
    "casual-learning": {
      "difficulty": "beginner", 
      "enableHints": true,
      "learningPace": "relaxed",
      "gamificationEnabled": true
    },
    
    "teaching-mode": {
      "verboseExplanations": true,
      "showMultipleApproaches": true,
      "emphasizeAnalogies": true,
      "enableStudentTracking": true
    }
  }
}
```

## 📋 Configuration Validation

### Schema Validation

**Configuration Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": {"type": "string", "minLength": 1},
        "difficulty": {"enum": ["beginner", "intermediate", "advanced"]},
        "theme": {"enum": ["light", "dark", "auto", "high-contrast"]}
      },
      "required": ["difficulty"]
    },
    "learning": {
      "type": "object", 
      "properties": {
        "enableHints": {"type": "boolean"},
        "reminderInterval": {"type": "number", "minimum": 1, "maximum": 1440}
      }
    },
    "sparc": {
      "type": "object",
      "properties": {
        "maxConcurrentAgents": {"type": "number", "minimum": 1, "maximum": 20}
      }
    }
  },
  "required": ["user", "learning"]
}
```

### Validation Commands

```bash
# Validate current configuration
npm run config validate

# Validate specific configuration file
npm run config validate ./custom-config.json

# Show configuration issues
npm run config doctor

# Fix common configuration problems
npm run config fix
```

### Configuration Testing

```bash
# Test configuration with dry run
npm run config test

# Test SPARC agent coordination
npm run config test-sparc

# Test display settings
npm run config test-display

# Run full configuration test suite
npm test config
```

---

## 🚀 Quick Configuration Reference

### Essential Settings

**Beginner Setup:**
```bash
npm run config set user.difficulty "beginner"
npm run config set learning.enableHints true
npm run config set display.animationSpeed "slow"
```

**Advanced Setup:**
```bash
npm run config set user.difficulty "advanced"  
npm run config set learning.enableHints false
npm run config set sparc.maxConcurrentAgents 8
```

**Performance Setup:**
```bash
npm run config set performance.caching.enabled true
npm run config set performance.optimization.lazyLoading true
npm run config set logging.level "warn"
```

### Most Common Configurations

1. **Theme Changes:** `npm run config set user.theme "dark"`
2. **Difficulty:** `npm run config set user.difficulty "intermediate"`
3. **Hints:** `npm run config set learning.enableHints false`
4. **Analytics:** `npm run config set learning.enableAnalytics true`
5. **SPARC:** `npm run config set sparc.enabled true`

**For complete setup assistance, run `npm run setup` to launch the interactive configuration wizard!**