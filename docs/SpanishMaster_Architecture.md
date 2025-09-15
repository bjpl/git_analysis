# SpanishMaster Platform Architecture
## Unified Spanish Learning Platform Design Document

### Executive Summary

**SpanishMaster** is a comprehensive, modular Spanish language learning platform that integrates all existing learning modules into a unified ecosystem. The architecture leverages the best features from each existing project while providing a cohesive user experience through shared services and standardized APIs.

### Vision Statement
Create a comprehensive Spanish learning ecosystem that combines structured lessons, practice modules, visual learning, and AI-powered assistance into a seamless, progressive learning experience.

---

## 1. Current State Analysis

### Existing Spanish Learning Projects

1. **MySpanishApp** - Session tracking and vocabulary management
   - PyQt6 desktop app with SQLite backend
   - Session planning, vocabulary tracking, progress review
   - Teacher management and learning analytics

2. **Conjugation GUI** - Verb conjugation practice
   - PyQt5 desktop app with AI integration
   - Multiple practice modes, progress tracking, spaced repetition
   - Offline capability with GPT-4o enhancement

3. **Subjunctive Practice** - Specialized subjunctive mood training
   - Task-based language teaching (TBLT)
   - AI-powered explanations and adaptive difficulty
   - Streak tracking and performance analytics

4. **Anki Generator** - Flashcard creation from unstructured content
   - GPT-4o powered content extraction
   - CSV/Anki format export
   - Language-agnostic processing

5. **LangTool** - CLI-based conversational practice
   - Multi-modal chat interface
   - Role-play scenarios and grammar drills
   - Session logging and flashcard export

6. **Unsplash GPT Tool** - Visual vocabulary learning
   - Image-based description generation
   - Vocabulary extraction and translation
   - Context-rich learning through visual association

### Common Patterns Identified

#### Technology Stack Commonalities
- **Python** ecosystem (3.8-3.10+)
- **SQLite** for local data persistence
- **OpenAI API** integration (GPT-4o/GPT-4o-mini)
- **PyQt5/PyQt6** for desktop interfaces
- **CSV export** capabilities

#### Functional Commonalities
- **Progress Tracking**: All apps track user performance
- **AI Integration**: GPT-powered explanations and content generation
- **Vocabulary Management**: Word/phrase collection and review
- **Session Management**: Learning session organization
- **Export Capabilities**: Data portability for external tools
- **Offline Functionality**: Local operation when possible

#### Data Patterns
- **SQLite databases** for structured data
- **JSON configurations** for settings
- **CSV exports** for portability
- **Logging systems** for debugging and analytics

---

## 2. Unified System Architecture

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     SpanishMaster Platform                      │
├─────────────────────────────────────────────────────────────────┤
│                    Presentation Layer                           │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│   Web Interface │  Desktop App    │   Mobile App    │  CLI Tools│
│   (React/Vue)   │   (PyQt6)       │   (React Native)│  (Python) │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Authentication │  Rate Limiting  │  Request Router │  Logging  │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                        │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│  Session    │ Practice    │ Vocabulary  │ Progress    │  AI     │
│  Manager    │ Engine      │ Manager     │ Tracker     │ Service │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────┤
│ ┌─────────┐ │┌─────────┐  │┌─────────┐  │┌─────────┐  │┌───────┐│
│ │Schedule │ ││Conjugate│  ││Word Bank│  ││Analytics│  ││GPT-4o ││
│ │Plan     │ ││Practice │  ││Visual   │  ││Spaced   │  ││Vision ││
│ │Track    │ ││Story    │  ││Audio    │  ││Repetition│ ││Chat   ││
│ │Review   │ ││Speed    │  ││Export   │  ││Streaks  │  ││Hints  ││
│ └─────────┘ │└─────────┘  │└─────────┘  │└─────────┘  │└───────┘│
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                      Data Access Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  Repository Pattern │ Unit of Work  │ Query Builder │ Migrations│
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│  PostgreSQL │   Redis     │   S3/Minio  │  External   │  Config │
│  (Primary)  │  (Cache)    │  (Files)    │  APIs       │ Store   │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────┤
│ ┌─────────┐ │┌─────────┐  │┌─────────┐  │┌─────────┐  │┌───────┐│
│ │Users    │ ││Sessions │  ││Images   │  ││OpenAI   │  ││.env   ││
│ │Sessions │ ││Cache    │  ││Audio    │  ││Unsplash │  ││JSON   ││
│ │Progress │ ││Temp Data│  ││Exports  │  ││External │  ││TOML   ││
│ │Vocabulary│││         │  ││         │  ││         │  ││       ││
│ └─────────┘ │└─────────┘  │└─────────┘  │└─────────┘  │└───────┘│
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
```

### 2.2 Microservices vs Modular Monolith Decision

**Recommendation: Modular Monolith with Service Extraction Path**

**Rationale:**
- **Simplicity**: Easier deployment and development for small team
- **Performance**: Lower latency between modules
- **Data Consistency**: Simpler transaction management
- **Migration Path**: Can extract services as platform scales

**Module Structure:**
```
SpanishMaster/
├── core/                    # Shared kernel
│   ├── auth/               # Authentication & authorization
│   ├── config/             # Configuration management
│   ├── logging/            # Centralized logging
│   ├── database/           # Database connections
│   └── exceptions/         # Common exceptions
├── modules/                # Business modules
│   ├── session_manager/    # Session planning & tracking
│   ├── practice_engine/    # All practice types
│   ├── vocabulary/         # Word management
│   ├── progress/           # Analytics & tracking
│   ├── ai_service/         # AI integrations
│   └── export/             # Data export services
├── interfaces/             # Interface adapters
│   ├── web_api/            # REST/GraphQL API
│   ├── desktop_gui/        # PyQt6 interface
│   ├── cli/                # Command line tools
│   └── mobile_api/         # Mobile-specific endpoints
└── infrastructure/         # Infrastructure concerns
    ├── repositories/       # Data access
    ├── external_apis/      # Third-party integrations
    ├── file_storage/       # File handling
    └── cache/              # Caching layer
```

---

## 3. Core Services Architecture

### 3.1 Session Manager Service

**Purpose**: Unified session planning, tracking, and management across all learning modules.

```python
# Session Manager API Contract
class SessionManager:
    def create_session(self, user_id: str, session_type: str, config: dict) -> Session
    def start_session(self, session_id: str) -> SessionContext
    def update_session_progress(self, session_id: str, progress: dict) -> None
    def end_session(self, session_id: str, summary: dict) -> SessionSummary
    def get_session_history(self, user_id: str, filters: dict) -> List[Session]
    def schedule_session(self, user_id: str, datetime: str, config: dict) -> Session
```

**Integration Points:**
- **From MySpanishApp**: Session scheduling and teacher management
- **From All Apps**: Session tracking and progress recording
- **New Features**: Cross-module session continuity

### 3.2 Practice Engine Service

**Purpose**: Unified practice engine supporting all learning modalities.

```python
# Practice Engine API Contract
class PracticeEngine:
    def generate_exercise(self, type: str, config: dict) -> Exercise
    def evaluate_answer(self, exercise_id: str, answer: str) -> Evaluation
    def get_next_exercise(self, session_id: str, performance: dict) -> Exercise
    def adapt_difficulty(self, user_id: str, performance_history: dict) -> DifficultyConfig
    
# Supported Practice Types
class PracticeTypes:
    CONJUGATION = "conjugation"         # From conjugation_gui
    SUBJUNCTIVE = "subjunctive"         # From subjunctive_practice
    CONVERSATION = "conversation"       # From langtool
    VISUAL_VOCABULARY = "visual_vocab"  # From unsplash_gpt
    STORY_MODE = "story"               # From conjugation_gui
    SPEED_PRACTICE = "speed"           # From conjugation_gui
    GRAMMAR_DRILLS = "grammar"         # From langtool
```

**Integration Points:**
- **From Conjugation GUI**: All practice modes and spaced repetition
- **From Subjunctive Practice**: TBLT methodology and adaptive difficulty  
- **From LangTool**: Conversational practice and role-play scenarios
- **New Features**: Cross-modal practice sessions and intelligent routing

### 3.3 Vocabulary Manager Service

**Purpose**: Centralized vocabulary acquisition, management, and review system.

```python
# Vocabulary Manager API Contract
class VocabularyManager:
    def add_word(self, word: str, context: dict, source: str) -> VocabEntry
    def get_vocabulary(self, user_id: str, filters: dict) -> List[VocabEntry]
    def schedule_review(self, user_id: str, spaced_repetition: bool = True) -> List[VocabEntry]
    def extract_from_content(self, content: str, content_type: str) -> List[VocabEntry]
    def export_vocabulary(self, user_id: str, format: str) -> ExportResult
    def get_weak_areas(self, user_id: str) -> List[VocabArea]
```

**Integration Points:**
- **From MySpanishApp**: Structured vocabulary tracking with context
- **From Anki Generator**: Content extraction and card generation
- **From Unsplash GPT**: Visual vocabulary with image associations
- **From All Apps**: Vocabulary collection from practice sessions
- **New Features**: Intelligent vocabulary recommendations and cross-references

### 3.4 Progress Tracker Service

**Purpose**: Comprehensive learning analytics and progress measurement.

```python
# Progress Tracker API Contract
class ProgressTracker:
    def record_performance(self, user_id: str, activity: dict) -> None
    def get_progress_summary(self, user_id: str, timeframe: str) -> ProgressSummary
    def calculate_mastery(self, user_id: str, topic: str) -> MasteryLevel
    def get_learning_path(self, user_id: str) -> LearningPath
    def identify_weak_areas(self, user_id: str) -> List[WeakArea]
    def generate_recommendations(self, user_id: str) -> List[Recommendation]
    def track_streak(self, user_id: str, activity: str) -> StreakInfo
```

**Integration Points:**
- **From All Apps**: Performance data collection and analysis
- **From Subjunctive Practice**: Streak tracking and analytics
- **From Conjugation GUI**: Spaced repetition algorithms
- **New Features**: Comprehensive learning analytics dashboard

### 3.5 AI Service Hub

**Purpose**: Centralized AI service management and intelligent content generation.

```python
# AI Service API Contract
class AIService:
    def generate_explanation(self, topic: str, context: dict) -> Explanation
    def create_exercise(self, type: str, level: str, context: dict) -> Exercise
    def provide_hint(self, exercise: dict, user_attempt: str) -> Hint
    def translate_content(self, content: str, source_lang: str, target_lang: str) -> Translation
    def extract_vocabulary(self, content: str, language: str) -> List[VocabEntry]
    def generate_conversation(self, scenario: str, user_level: str) -> Conversation
    def describe_image(self, image_url: str, learning_context: dict) -> Description
```

**Integration Points:**
- **From All Apps**: GPT-4o integration and AI-powered features
- **From Unsplash GPT**: Image description and vocabulary extraction
- **From LangTool**: Conversational AI and role-play scenarios
- **From Anki Generator**: Content processing and card generation
- **New Features**: Cross-modal AI assistance and personalized content generation

---

## 4. Data Architecture

### 4.1 Unified Database Schema

```sql
-- User Management
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    preferences JSONB,
    learning_goals JSONB
);

-- Session Management
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    session_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'planned',
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    configuration JSONB,
    summary JSONB
);

-- Learning Activities
CREATE TABLE activities (
    activity_id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    user_id UUID REFERENCES users(user_id),
    activity_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    performance JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vocabulary Management
CREATE TABLE vocabulary (
    vocab_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    spanish_term TEXT NOT NULL,
    english_translation TEXT,
    context TEXT,
    source_type VARCHAR(50),
    source_reference TEXT,
    difficulty_level INTEGER DEFAULT 1,
    mastery_score DECIMAL(3,2) DEFAULT 0.0,
    last_reviewed TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Progress Tracking
CREATE TABLE progress_records (
    record_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    activity_type VARCHAR(50) NOT NULL,
    topic VARCHAR(100),
    performance_score DECIMAL(3,2),
    time_spent INTEGER, -- seconds
    correct_answers INTEGER,
    total_attempts INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Spaced Repetition
CREATE TABLE review_schedule (
    schedule_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    item_id UUID, -- references vocabulary or other reviewable items
    item_type VARCHAR(50) NOT NULL,
    next_review TIMESTAMP NOT NULL,
    interval_days INTEGER DEFAULT 1,
    ease_factor DECIMAL(3,2) DEFAULT 2.5,
    repetitions INTEGER DEFAULT 0
);
```

### 4.2 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Flow Diagram                        │
└─────────────────────────────────────────────────────────────────┘

User Input
     │
     ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Interface  │    │ Desktop Client  │    │   Mobile App    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
     │                          │                          │
     └──────────────────────────┼──────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │      API Gateway        │
                    │  - Authentication       │
                    │  - Rate Limiting        │
                    │  - Request Routing      │
                    └─────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Business Logic Layer  │
                    │  - Session Manager      │
                    │  - Practice Engine      │
                    │  - Vocabulary Manager   │
                    │  - Progress Tracker     │
                    │  - AI Service Hub       │
                    └─────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │   PostgreSQL    │ │    Redis    │ │   File Storage  │
    │   (Primary DB)  │ │  (Cache)    │ │  (S3/MinIO)     │
    └─────────────────┘ └─────────────┘ └─────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    External APIs        │
                    │  - OpenAI (GPT-4o)      │
                    │  - Unsplash API         │
                    │  - Translation Services │
                    └─────────────────────────┘
```

---

## 5. Module Integration Strategy

### 5.1 Migration Approach

**Phase 1: Core Infrastructure (Weeks 1-4)**
1. Set up unified database schema
2. Implement core services (Session Manager, base APIs)
3. Create authentication and user management
4. Establish logging and monitoring

**Phase 2: Module Integration (Weeks 5-12)**
1. **MySpanishApp Integration** (Weeks 5-6)
   - Migrate session planning and tracking
   - Integrate teacher management
   - Port vocabulary tracking features

2. **Conjugation GUI Integration** (Weeks 7-8)
   - Extract practice engine logic
   - Integrate spaced repetition algorithms
   - Port all practice modes

3. **Subjunctive Practice Integration** (Weeks 9-10)
   - Integrate TBLT methodology
   - Port adaptive difficulty system
   - Merge analytics capabilities

4. **AI Services Integration** (Weeks 11-12)
   - Unify OpenAI API usage
   - Integrate content generation from Anki Generator
   - Port visual learning from Unsplash GPT
   - Integrate conversational AI from LangTool

**Phase 3: Enhancement & Testing (Weeks 13-16)**
1. Cross-module feature development
2. Comprehensive testing and optimization
3. User interface development
4. Documentation and deployment preparation

### 5.2 Data Migration Strategy

```python
# Migration Orchestrator
class MigrationOrchestrator:
    def migrate_myspanish_app(self):
        """Migrate SQLite data from MySpanishApp"""
        # 1. Extract sessions, vocabulary, grammar data
        # 2. Transform to unified schema
        # 3. Load into PostgreSQL
        # 4. Validate data integrity
    
    def migrate_conjugation_gui(self):
        """Migrate progress data from ConjugationGUI"""
        # 1. Extract progress.db data
        # 2. Transform performance records
        # 3. Migrate spaced repetition data
    
    def migrate_subjunctive_practice(self):
        """Migrate analytics and streaks"""
        # 1. Extract user_data/streaks.json
        # 2. Transform learning analytics
        # 3. Merge with progress tracking system
    
    def consolidate_configurations(self):
        """Merge app configurations"""
        # 1. Extract settings from all apps
        # 2. Create unified user preferences
        # 3. Set up default configurations
```

### 5.3 API Standardization

**Common Response Format:**
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "uuid",
    "version": "1.0"
  },
  "errors": []
}
```

**Common Error Format:**
```json
{
  "success": false,
  "data": null,
  "meta": { ... },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input parameters",
      "field": "session_type"
    }
  ]
}
```

---

## 6. Technology Recommendations

### 6.1 Core Technology Stack

**Backend Framework:**
- **Primary**: FastAPI (Python 3.10+)
  - High performance async framework
  - Automatic API documentation
  - Type hints support
  - Easy testing

**Database:**
- **Primary**: PostgreSQL 15+
  - JSONB support for flexible schemas
  - Full-text search capabilities
  - Excellent performance and reliability
- **Cache**: Redis 7+
  - Session caching
  - Temporary data storage
  - Rate limiting support

**Frontend Options:**
1. **Web Interface**: React 18+ with TypeScript
   - Component reusability
   - Strong ecosystem
   - Mobile-responsive design
   
2. **Desktop Application**: PyQt6
   - Native performance
   - Rich widget library
   - Cross-platform compatibility
   
3. **Mobile Application**: React Native
   - Code sharing with web
   - Native performance
   - Large developer ecosystem

### 6.2 Infrastructure Recommendations

**Container Orchestration:**
- **Docker** for containerization
- **Docker Compose** for local development
- **Kubernetes** for production (optional, for scale)

**File Storage:**
- **MinIO** for self-hosted object storage
- **AWS S3** for cloud deployment
- Support for images, audio files, exports

**Monitoring & Logging:**
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for centralized logging
- **Sentry** for error tracking

**API Documentation:**
- **OpenAPI/Swagger** auto-generated from FastAPI
- **Postman Collections** for testing
- **Interactive documentation** for developers

### 6.3 AI Service Architecture

```python
# AI Service Configuration
class AIServiceConfig:
    PRIMARY_MODEL = "gpt-4o-mini"  # Cost-effective for most tasks
    ADVANCED_MODEL = "gpt-4o"      # For complex tasks
    VISION_MODEL = "gpt-4o"        # For image processing
    
    # Service routing based on task complexity
    def get_model_for_task(self, task_type: str, complexity: str) -> str:
        routing_table = {
            ("translation", "simple"): self.PRIMARY_MODEL,
            ("explanation", "complex"): self.ADVANCED_MODEL,
            ("image_description", "any"): self.VISION_MODEL,
            ("conversation", "any"): self.PRIMARY_MODEL,
        }
        return routing_table.get((task_type, complexity), self.PRIMARY_MODEL)
```

---

## 7. User Experience Integration

### 7.1 Unified Learning Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                     SpanishMaster Dashboard                     │
├─────────────────────────────────────────────────────────────────┤
│  Welcome back, [User]! 🇪🇸          Streak: 15 days 🔥         │
├─────────────────────────────────────────────────────────────────┤
│  Today's Goals                     │  Recent Activity           │
│  ├─ Complete 2 conjugation drills │  ├─ Subjunctive practice   │
│  ├─ Review 10 vocabulary words    │  ├─ Added 5 new words      │
│  ├─ 15 min conversation practice  │  ├─ 85% accuracy on verbs  │
│  └─ Visual vocabulary session     │  └─ Completed story mode   │
├─────────────────────────────────────────────────────────────────┤
│  Learning Modules                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ Conjugation │ │ Conversation│ │   Visual    │ │ Vocabulary  ││
│  │   Practice  │ │     AI      │ │  Learning   │ │   Manager   ││
│  │     85%     │ │  Available  │ │   12 new    │ │ 1,247 words ││
│  │   mastery   │ │             │ │   words     │ │             ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │Subjunctive  │ │   Session   │ │   Export    │ │  Progress   ││
│  │  Mastery    │ │  Planning   │ │    Tools    │ │ Analytics   ││
│  │    67%      │ │ Next: 2 PM  │ │   Ready     │ │ Trends ↗    ││
│  │             │ │  w/ Maria   │ │             │ │             ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Cross-Module User Flows

**Example: Comprehensive Verb Learning Journey**
1. **Discovery**: Visual vocabulary finds verb in image context
2. **Definition**: AI service provides detailed explanation
3. **Practice**: Conjugation engine generates targeted exercises
4. **Mastery**: Subjunctive practice includes verb in advanced scenarios  
5. **Application**: Conversation AI uses verb in role-play scenarios
6. **Retention**: Spaced repetition schedules review sessions
7. **Assessment**: Progress tracker measures mastery progression

### 7.3 Adaptive Learning Pathways

```python
class LearningPathEngine:
    def generate_personalized_path(self, user_profile: UserProfile) -> LearningPath:
        """Generate adaptive learning path based on user's current state"""
        
        # Assess current competencies
        competencies = self.assess_user_level(user_profile)
        
        # Identify knowledge gaps
        gaps = self.identify_gaps(competencies)
        
        # Generate targeted activities
        activities = []
        for gap in gaps:
            activities.extend(
                self.generate_gap_activities(gap, user_profile.preferences)
            )
        
        # Sequence activities for optimal learning
        sequenced_path = self.sequence_activities(activities, user_profile)
        
        return LearningPath(
            user_id=user_profile.user_id,
            activities=sequenced_path,
            estimated_duration=self.calculate_duration(sequenced_path),
            difficulty_progression=self.map_difficulty_curve(sequenced_path)
        )
```

---

## 8. API Contracts & Integration Specifications

### 8.1 Session Management APIs

```python
# REST API Endpoints
POST /api/v1/sessions
GET  /api/v1/sessions/{session_id}
PUT  /api/v1/sessions/{session_id}
DELETE /api/v1/sessions/{session_id}
GET  /api/v1/sessions/user/{user_id}
POST /api/v1/sessions/{session_id}/start
POST /api/v1/sessions/{session_id}/end

# GraphQL Schema
type Session {
  sessionId: ID!
  userId: ID!
  sessionType: SessionType!
  status: SessionStatus!
  scheduledAt: DateTime
  startedAt: DateTime
  endedAt: DateTime
  configuration: JSON
  summary: SessionSummary
  activities: [Activity!]!
}

type SessionSummary {
  totalTimeSpent: Int!
  activitiesCompleted: Int!
  averageScore: Float
  vocabularyLearned: Int!
  areasImproved: [String!]!
  nextRecommendations: [Recommendation!]!
}
```

### 8.2 Practice Engine APIs

```python
# Practice Configuration
class PracticeConfig:
    session_id: str
    practice_type: str  # conjugation, subjunctive, conversation, visual
    difficulty_level: str  # beginner, intermediate, advanced
    focus_areas: List[str]  # specific topics to emphasize
    time_limit: Optional[int]  # session duration in minutes
    adaptive: bool = True  # whether to adjust difficulty dynamically

# Exercise Generation
POST /api/v1/practice/generate
{
  "config": PracticeConfig,
  "user_context": {
    "current_level": "intermediate",
    "weak_areas": ["subjunctive_triggers", "irregular_verbs"],
    "recent_performance": {...}
  }
}

Response:
{
  "exercises": [
    {
      "exercise_id": "uuid",
      "type": "conjugation",
      "content": {...},
      "expected_answers": [...],
      "hints": [...],
      "difficulty": 0.7
    }
  ],
  "session_context": {...}
}
```

### 8.3 Vocabulary Management APIs

```python
# Vocabulary Entry Schema
class VocabEntry:
    vocab_id: str
    spanish_term: str
    english_translation: str
    context: str
    source_type: str  # manual, ai_generated, extracted
    difficulty_level: int  # 1-10
    mastery_score: float  # 0.0-1.0
    review_history: List[ReviewRecord]
    associations: List[Association]  # images, audio, related words

# API Endpoints
POST /api/v1/vocabulary/add
GET  /api/v1/vocabulary/user/{user_id}
PUT  /api/v1/vocabulary/{vocab_id}
DELETE /api/v1/vocabulary/{vocab_id}
POST /api/v1/vocabulary/bulk-import
GET  /api/v1/vocabulary/due-for-review/{user_id}
POST /api/v1/vocabulary/extract-from-content
```

### 8.4 AI Service APIs

```python
# AI Service Interface
class AIServiceInterface:
    async def generate_explanation(
        self, 
        topic: str, 
        context: dict, 
        user_level: str
    ) -> ExplanationResponse
    
    async def create_conversation(
        self, 
        scenario: str, 
        user_level: str, 
        conversation_history: List[Message]
    ) -> ConversationResponse
    
    async def describe_image(
        self, 
        image_url: str, 
        learning_context: dict
    ) -> ImageDescriptionResponse
    
    async def extract_vocabulary(
        self, 
        content: str, 
        source_language: str,
        target_language: str
    ) -> VocabularyExtractionResponse

# Unified AI Request Format
class AIRequest:
    request_id: str
    task_type: str  # explanation, conversation, image_description, etc.
    content: dict  # task-specific content
    context: dict  # user level, preferences, learning goals
    options: dict  # model preferences, output format, etc.
```

---

## 9. Performance & Scalability Considerations

### 9.1 Performance Targets

**Response Time Requirements:**
- API endpoints: < 200ms (95th percentile)
- AI-powered operations: < 5s (95th percentile)
- File uploads: < 30s for 10MB files
- Database queries: < 100ms (average)

**Throughput Requirements:**
- Concurrent users: 1,000+ simultaneous sessions
- API requests: 10,000+ requests per minute
- Database transactions: 5,000+ per minute

**Reliability Requirements:**
- System availability: 99.5% uptime
- Data durability: 99.999% (no data loss)
- API error rate: < 0.1%

### 9.2 Scalability Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer (HAProxy/Nginx)                │
└─────────────────────────────────────────────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Server 1  │    │   API Server 2  │    │   API Server N  │
│   (FastAPI)     │    │   (FastAPI)     │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │     Redis Cluster       │
                    │   (Session & Cache)     │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  PostgreSQL Cluster    │
                    │  (Primary + Replicas)  │
                    └─────────────────────────┘
```

### 9.3 Caching Strategy

```python
# Multi-layered caching approach
class CacheManager:
    def __init__(self):
        self.l1_cache = InMemoryCache()  # Application-level cache
        self.l2_cache = RedisCache()     # Distributed cache
        self.l3_cache = CDNCache()       # Static content cache
    
    async def get_user_progress(self, user_id: str) -> ProgressData:
        # Try L1 cache first
        if data := self.l1_cache.get(f"progress:{user_id}"):
            return data
        
        # Try L2 cache
        if data := await self.l2_cache.get(f"progress:{user_id}"):
            self.l1_cache.set(f"progress:{user_id}", data, ttl=300)
            return data
        
        # Fallback to database
        data = await self.database.get_progress(user_id)
        await self.l2_cache.set(f"progress:{user_id}", data, ttl=3600)
        self.l1_cache.set(f"progress:{user_id}", data, ttl=300)
        return data
```

---

## 10. Security Architecture

### 10.1 Authentication & Authorization

```python
# JWT-based authentication with role-based access control
class AuthenticationService:
    def authenticate_user(self, credentials: UserCredentials) -> AuthToken
    def refresh_token(self, refresh_token: str) -> AuthToken
    def validate_token(self, token: str) -> TokenValidation
    def logout_user(self, token: str) -> bool

class AuthorizationService:
    def check_permission(self, user_id: str, resource: str, action: str) -> bool
    def get_user_roles(self, user_id: str) -> List[Role]
    def grant_permission(self, user_id: str, permission: Permission) -> bool

# Role definitions
class Roles:
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"

# Permission matrix
PERMISSIONS = {
    "student": [
        "read_own_sessions",
        "create_own_sessions", 
        "read_own_progress",
        "export_own_data"
    ],
    "tutor": [
        "read_student_sessions",
        "create_student_sessions",
        "read_student_progress",
        "provide_feedback"
    ],
    "admin": [
        "read_all_data",
        "manage_users",
        "system_configuration"
    ]
}
```

### 10.2 Data Protection

**Encryption Standards:**
- Data at rest: AES-256 encryption
- Data in transit: TLS 1.3
- API keys: Environment variables + secrets management
- User passwords: bcrypt with salt rounds >= 12

**Privacy Measures:**
- GDPR compliance for EU users
- Data minimization principles
- User consent management
- Right to deletion implementation
- Data anonymization for analytics

**API Security:**
```python
# Rate limiting configuration
RATE_LIMITS = {
    "anonymous": "100/hour",
    "authenticated": "1000/hour", 
    "premium": "5000/hour"
}

# Input validation
class APIValidator:
    def validate_session_input(self, data: dict) -> ValidationResult
    def sanitize_user_content(self, content: str) -> str
    def check_file_upload_safety(self, file: UploadFile) -> SecurityCheck
```

---

## 11. Deployment & DevOps Strategy

### 11.1 Containerization Strategy

```dockerfile
# Multi-stage Docker build for API server
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim as runtime
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# Docker Compose for local development
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/spanishmaster
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: spanishmaster
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 11.2 CI/CD Pipeline

```yaml
# GitHub Actions workflow
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t spanishmaster:${{ github.sha }} .
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_TOKEN }} | docker login -u ${{ secrets.DOCKER_USER }} --password-stdin
          docker push spanishmaster:${{ github.sha }}
          
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to staging
        run: |
          # Deploy to staging environment
          kubectl set image deployment/api api=spanishmaster:${{ github.sha }}
```

### 11.3 Monitoring & Observability

```python
# Application metrics
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
EXERCISES_COMPLETED = Counter('exercises_completed_total', 'Total exercises completed', ['exercise_type', 'user_level'])
SESSION_DURATION = Histogram('session_duration_seconds', 'Session duration')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
AI_API_CALLS = Counter('ai_api_calls_total', 'AI API calls', ['model', 'task_type'])

# Technical metrics
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency')
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active DB connections')
CACHE_HIT_RATE = Histogram('cache_hit_rate', 'Cache hit rate by cache type', ['cache_type'])
```

---

## 12. Implementation Roadmap

### 12.1 Development Phases

**Phase 1: Foundation (Months 1-2)**
- [ ] Set up development environment and CI/CD
- [ ] Implement core authentication and user management
- [ ] Create unified database schema and migrations
- [ ] Develop basic API gateway and routing
- [ ] Implement logging, monitoring, and error handling

**Phase 2: Core Services (Months 3-4)**
- [ ] Develop Session Manager service
- [ ] Implement Practice Engine with basic exercise types
- [ ] Create Vocabulary Manager with import/export
- [ ] Build Progress Tracker with basic analytics
- [ ] Integrate AI Service hub with OpenAI

**Phase 3: Module Integration (Months 5-6)**
- [ ] Migrate and integrate MySpanishApp functionality
- [ ] Port Conjugation GUI practice modes
- [ ] Integrate Subjunctive Practice with TBLT methodology
- [ ] Merge LangTool conversational features
- [ ] Include Unsplash GPT visual learning

**Phase 4: Advanced Features (Months 7-8)**
- [ ] Develop adaptive learning pathways
- [ ] Implement cross-module learning flows
- [ ] Add advanced analytics and reporting
- [ ] Create mobile-responsive web interface
- [ ] Optimize performance and scalability

**Phase 5: Polish & Launch (Months 9-10)**
- [ ] Comprehensive testing and bug fixes
- [ ] User experience optimization
- [ ] Documentation completion
- [ ] Production deployment
- [ ] User onboarding and support systems

### 12.2 Success Metrics

**Technical Metrics:**
- System availability: 99.5%
- API response time: < 200ms (95th percentile)
- Test coverage: > 85%
- Zero critical security vulnerabilities

**User Experience Metrics:**
- User session completion rate: > 80%
- Daily active users retention: > 70%
- Feature adoption rate: > 60%
- User satisfaction score: > 4.5/5

**Learning Effectiveness Metrics:**
- Vocabulary retention rate: > 75% after 30 days
- Exercise completion rate: > 85%
- Learning goal achievement: > 70%
- Time to competency improvement: < 50% compared to individual apps

---

## 13. Risk Assessment & Mitigation

### 13.1 Technical Risks

**Risk: AI API Rate Limiting/Costs**
- *Probability*: Medium
- *Impact*: High
- *Mitigation*: Implement intelligent caching, content pre-generation, and fallback to local models

**Risk: Database Performance Bottlenecks**
- *Probability*: Medium  
- *Impact*: Medium
- *Mitigation*: Implement read replicas, optimize queries, add comprehensive caching

**Risk: Complex Module Integration**
- *Probability*: High
- *Impact*: Medium
- *Mitigation*: Incremental integration, extensive testing, rollback capabilities

### 13.2 Business Risks

**Risk: User Adoption Challenges**
- *Probability*: Medium
- *Impact*: High
- *Mitigation*: Gradual migration, maintain feature parity, excellent user support

**Risk: Scope Creep**
- *Probability*: High
- *Impact*: Medium
- *Mitigation*: Clear requirements, phased development, regular stakeholder reviews

---

## 14. Conclusion

The SpanishMaster platform represents a comprehensive integration of all existing Spanish learning tools into a unified, scalable, and intelligent learning ecosystem. By leveraging the best features from each existing application while introducing new cross-modal learning capabilities, the platform will provide users with a superior learning experience.

Key architectural decisions:
1. **Modular Monolith** for initial development with service extraction path
2. **FastAPI + PostgreSQL** for robust, scalable backend
3. **Multi-interface support** (web, desktop, mobile, CLI)
4. **Unified AI service hub** for intelligent content generation
5. **Comprehensive data architecture** supporting all learning modalities

The phased implementation approach ensures gradual migration with minimal disruption while building toward a powerful, integrated learning platform that leverages AI to provide personalized, adaptive Spanish language education.

This architecture provides a solid foundation for creating a world-class Spanish learning platform that can scale from individual learners to educational institutions while maintaining the personal touch and effectiveness of the original specialized applications.

---

**Document Version**: 1.0  
**Last Updated**: 2025-08-23  
**Next Review**: 2025-09-23