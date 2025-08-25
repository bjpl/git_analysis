# SpanishMaster AI Features Documentation

## Overview

SpanishMaster integrates advanced AI features to provide personalized, intelligent language learning experiences. The AI system consists of five main components that work together to optimize learning outcomes.

## Architecture

```
AI System
├── Spaced Repetition System
│   ├── Enhanced SM2 Algorithm
│   ├── Review Scheduler  
│   └── Performance Tracker
├── Content Generation System
│   ├── OpenAI GPT-4 Integration
│   ├── Prompt Templates
│   └── Content Generator
├── Adaptive Difficulty System
│   ├── Zone of Proximal Development (ZPD)
│   ├── Difficulty Adjuster
│   └── Learning Path Manager
├── Content Recommendation Engine
│   ├── Weakness Analysis
│   ├── Content Matching
│   └── Lesson Sequencing
└── Intelligence Features
    ├── Grammar Analyzer
    ├── Pronunciation Analyzer
    ├── Writing Feedback
    └── Vocabulary Suggester
```

## Core Components

### 1. Spaced Repetition System

**Purpose**: Optimize review timing based on forgetting curves and individual performance.

**Key Features**:
- Enhanced SM2 algorithm with user performance factors
- Adaptive scheduling based on response quality and timing
- Priority-based review queue management
- Performance trend analysis
- Streak bonuses and difficulty penalties

**Algorithm Improvements**:
- User performance factor integration
- Streak bonus calculation
- Difficulty penalty for struggling cards
- Learning velocity adjustment
- Context-aware interval calculation

**Usage**:
```python
from ai.spaced_repetition import SM2Algorithm, ReviewScheduler

# Initialize system
sm2 = SM2Algorithm()
scheduler = ReviewScheduler(sm2_algorithm=sm2)

# Add new content
scheduler.add_new_card("vocab_casa", "vocabulary")

# Process review response
result = scheduler.process_review_response(
    "vocab_casa", 
    ResponseQuality.EASY, 
    review_duration_seconds=12
)

# Get next reviews
next_reviews = scheduler.get_next_reviews(limit=10)
```

### 2. Content Generation System

**Purpose**: Generate dynamic, personalized learning content using GPT-4.

**Key Features**:
- OpenAI GPT-4 integration with retry logic and rate limiting
- Structured prompt templates for different content types
- Caching system for cost optimization
- Context-aware content generation
- Multi-language support

**Content Types**:
- Vocabulary lessons with cultural context
- Grammar explanations with examples
- Conversation practice scenarios
- Interactive exercises
- Contextual hints and corrections
- Educational stories

**Usage**:
```python
from ai.content_generation import ContentGenerator

generator = ContentGenerator()

# Generate vocabulary lesson
vocab_lesson = await generator.generate_vocabulary_lesson(
    word="casa",
    user_level="intermediate",
    difficulty="medium"
)

# Generate grammar explanation
grammar_help = await generator.generate_grammar_explanation(
    concept="subjunctive mood",
    user_level="advanced",
    user_context="struggling with subjunctive triggers"
)

# Batch generation
batch_requests = [
    {'type': 'vocabulary', 'word': 'perro', 'user_level': 'beginner'},
    {'type': 'exercise', 'grammar_point': 'ser vs estar', 'user_level': 'intermediate'}
]
results = await generator.batch_generate_content(batch_requests)
```

### 3. Adaptive Difficulty System

**Purpose**: Maintain optimal challenge level using Zone of Proximal Development theory.

**Key Features**:
- ZPD-based difficulty adjustment
- Multi-skill assessment and tracking
- Learning velocity calculation
- Personalized challenge levels
- Trend analysis and prediction

**Skill Categories**:
- Vocabulary (basic words, advanced vocabulary, expressions)
- Grammar (tenses, moods, structures)
- Listening (speeds, accents, contexts)
- Reading (text types, complexity levels)
- Speaking (pronunciation, fluency, accuracy)
- Writing (sentence construction, essays, formal writing)
- Culture (customs, history, regional differences)

**Usage**:
```python
from ai.adaptive_difficulty import ZPDSystem

zpd_system = ZPDSystem()

# Initialize user profile
profile = zpd_system.initialize_user_profile("user_123")

# Update skill assessment
zpd_system.update_skill_assessment(
    "user_123", 
    "present_tense",
    performance_score=0.8,
    confidence_score=0.7,
    response_time=10.0,
    difficulty_attempted=0.6
)

# Get recommended difficulty
difficulty, learning_state = zpd_system.get_recommended_difficulty(
    "user_123", 
    "subjunctive"
)

# Analyze learning progress
analysis = zpd_system.analyze_learning_progress("user_123")
```

### 4. Content Recommendation Engine

**Purpose**: Suggest personalized learning content based on user performance and preferences.

**Key Features**:
- Multi-factor scoring algorithm
- Weakness-focused recommendations
- Spaced repetition integration
- Content variety optimization
- Session length consideration

**Recommendation Factors**:
- Difficulty match (25%)
- Skill relevance (20%)
- Weakness targeting (20%)
- Spaced repetition timing (15%)
- Content variety (10%)
- Engagement score (10%)

**Usage**:
```python
from ai.recommendation import ContentRecommendationEngine

engine = ContentRecommendationEngine()

# Get general recommendations
recommendations = engine.get_recommendations(
    user_id="user_123",
    num_recommendations=10,
    session_length_minutes=30
)

# Get weakness-focused recommendations
weakness_recs = engine.get_weakness_focused_recommendations(
    user_id="user_123",
    num_recommendations=5
)

# Get review recommendations
review_recs = engine.get_review_recommendations(
    user_id="user_123",
    num_recommendations=8
)
```

### 5. Intelligence Features

**Purpose**: Provide intelligent analysis and feedback for grammar, pronunciation, and writing.

#### Grammar Analyzer

**Features**:
- Error detection for 10+ grammar categories
- Contextual corrections with explanations
- Confidence scoring for corrections
- Learning suggestions based on error patterns
- Positive feedback generation

**Error Types**:
- Verb conjugation
- Gender agreement
- Number agreement
- Ser/estar usage
- Subjunctive mood
- Preposition usage
- Word order
- Article usage
- Pronoun placement
- Accent marks

**Usage**:
```python
from ai.intelligence import GrammarAnalyzer

analyzer = GrammarAnalyzer()

# Analyze text
analysis = analyzer.analyze_text(
    "Yo eres estudiante y estoy un profesor.",
    user_level="intermediate"
)

print(f"Errors found: {len(analysis.errors)}")
print(f"Grammar score: {analysis.overall_score}")
print(f"Corrected text: {analysis.corrected_text}")
```

#### Pronunciation Analyzer

**Features**:
- Text-based pronunciation difficulty assessment
- IPA and simplified phonetic transcriptions
- Stress pattern analysis
- Minimal pairs generation
- Exercise creation for difficult sounds

**Analysis Areas**:
- Silent H detection
- RR trill identification
- B/V distinction
- Vowel clarity
- Stress patterns
- Diphthongs
- Consonant clusters

**Usage**:
```python
from ai.intelligence import PronunciationAnalyzer

analyzer = PronunciationAnalyzer()

# Analyze text
analysis = analyzer.analyze_text(
    "El perro corre rápido",
    user_native_language="english"
)

# Get phonetic transcription
phonetic = analyzer.get_phonetic_transcription("rápido", style="ipa")

# Get stress analysis
stress_info = analyzer.get_stress_analysis("médico")

# Generate exercises
exercises = analyzer.generate_pronunciation_exercises(["rr", "stress"])
```

## Integration Examples

### Complete Learning Session

```python
import asyncio
from ai import *

async def learning_session(user_id: str, session_length: int = 30):
    """Complete AI-powered learning session"""
    
    # Initialize systems
    zpd_system = ZPDSystem()
    recommendation_engine = ContentRecommendationEngine(zpd_system=zpd_system)
    content_generator = ContentGenerator()
    grammar_analyzer = GrammarAnalyzer()
    performance_tracker = PerformanceTracker()
    
    # Start session tracking
    session_id = performance_tracker.start_session()
    
    # Get personalized recommendations
    recommendations = recommendation_engine.get_recommendations(
        user_id=user_id,
        num_recommendations=5,
        session_length_minutes=session_length
    )
    
    session_results = []
    
    for recommendation in recommendations:
        content_item = recommendation.content_item
        
        # Generate dynamic content if needed
        if content_item.content_type == "vocabulary":
            content = await content_generator.generate_vocabulary_lesson(
                word=content_item.skills_addressed[0],
                user_level="intermediate"
            )
        elif content_item.content_type == "grammar":
            content = await content_generator.generate_grammar_explanation(
                concept=content_item.skills_addressed[0],
                user_level="intermediate"
            )
        
        # Present content to user and get response
        # ... (UI interaction) ...
        
        # Simulate user response
        user_response = "Yo soy estudiante de español"
        response_time = 15.0
        
        # Analyze response
        grammar_analysis = grammar_analyzer.analyze_text(user_response)
        
        # Calculate performance score
        performance_score = grammar_analysis.overall_score
        
        # Track performance
        performance_tracker.record_review(
            content_item.content_id,
            ResponseQuality.EASY if performance_score > 0.7 else ResponseQuality.DIFFICULT,
            response_time,
            content_item.content_type
        )
        
        # Update ZPD system
        for skill in content_item.skills_addressed:
            zpd_system.update_skill_assessment(
                user_id, skill, performance_score, 0.7, response_time, 0.6
            )
        
        session_results.append({
            'content': content,
            'analysis': grammar_analysis,
            'performance': performance_score
        })
    
    # End session
    session_summary = performance_tracker.end_session()
    
    # Generate session report
    report = performance_tracker.generate_performance_report()
    
    return {
        'session_summary': session_summary,
        'results': session_results,
        'performance_report': report,
        'recommendations': recommendations
    }
```

### Adaptive Assessment

```python
def adaptive_assessment(user_id: str, skill_area: str):
    """Adaptive assessment that adjusts difficulty based on performance"""
    
    zpd_system = ZPDSystem()
    content_generator = ContentGenerator()
    
    # Get user's current level in skill area
    difficulty, state = zpd_system.get_recommended_difficulty(user_id, skill_area)
    
    assessment_items = []
    current_difficulty = difficulty
    
    for i in range(10):  # 10 assessment items
        # Generate content at current difficulty
        if skill_area == "grammar":
            content = await content_generator.generate_exercise(
                exercise_type="fill_in_blanks",
                grammar_point=skill_area,
                difficulty=current_difficulty
            )
        
        # Present to user and get response
        # ... (UI interaction) ...
        
        # Simulate response
        performance = 0.8 if current_difficulty < 0.7 else 0.4
        
        # Update skill assessment
        zpd_system.update_skill_assessment(
            user_id, skill_area, performance, 0.7, 12.0, current_difficulty
        )
        
        # Adjust difficulty for next item
        if performance > 0.8:
            current_difficulty = min(1.0, current_difficulty + 0.1)
        elif performance < 0.5:
            current_difficulty = max(0.1, current_difficulty - 0.1)
        
        assessment_items.append({
            'item': content,
            'difficulty': current_difficulty,
            'performance': performance
        })
    
    # Final analysis
    final_analysis = zpd_system.analyze_learning_progress(user_id)
    
    return {
        'items': assessment_items,
        'final_level': final_analysis['skill_assessments'][skill_area],
        'recommendations': final_analysis['recommendations']
    }
```

## Configuration and Setup

### Environment Variables

```bash
# Required for content generation
OPENAI_API_KEY=your_openai_api_key_here

# Optional configurations
OPENAI_MODEL=gpt-4  # Default model
MAX_REQUESTS_PER_MINUTE=50  # Rate limiting
CACHE_SIZE=1000  # Response cache size
```

### Installation Requirements

```bash
# Core dependencies
pip install openai>=1.0.0
pip install asyncio
pip install dataclasses
pip install pytest  # For testing

# Optional dependencies for enhanced features
pip install numpy  # For advanced analytics
pip install scipy  # For statistical analysis
```

### Database Integration

The AI systems can be integrated with your existing database models:

```python
# Example integration with existing models
from models.vocab_model import VocabModel
from ai.spaced_repetition import ReviewScheduler

def integrate_with_database():
    scheduler = ReviewScheduler()
    vocab_model = VocabModel()
    
    # Load existing vocabulary items
    vocab_items = vocab_model.get_all_vocab()
    
    for item in vocab_items:
        scheduler.add_new_card(
            card_id=f"vocab_{item.vocab_id}",
            content_type="vocabulary"
        )
```

## Performance and Optimization

### Caching Strategy

- **Content Generation**: Responses are cached based on prompt hash
- **ZPD Calculations**: Skill assessments cached for quick retrieval
- **Recommendations**: Pre-computed recommendations for common scenarios

### Batch Processing

- **Content Generation**: Support for batch requests to reduce API calls
- **Skill Updates**: Batch skill assessment updates
- **Recommendations**: Bulk recommendation generation

### Memory Management

- **LRU Cache**: Automatic cleanup of old cached responses
- **Rolling Windows**: Fixed-size windows for performance tracking
- **Periodic Cleanup**: Scheduled cleanup of old data

## Monitoring and Analytics

### Performance Metrics

- **Content Generation**: Token usage, cost tracking, cache hit rates
- **Learning Progress**: Skill improvement rates, difficulty adaptation
- **Engagement**: Session lengths, completion rates, content preferences

### Error Handling

- **Graceful Degradation**: Fallback strategies when AI services are unavailable
- **Retry Logic**: Exponential backoff for API failures
- **Validation**: Input validation and sanitization

## Customization

### Prompt Templates

Templates can be customized for different learning styles:

```python
from ai.content_generation import PromptTemplates

templates = PromptTemplates()

# Add custom template
custom_template = PromptTemplate(
    template="Create a {content_type} lesson for {skill_level} learners focusing on {topic}",
    required_fields=["content_type", "skill_level", "topic"]
)

templates.templates[ContentType.CUSTOM] = {"my_template": custom_template}
```

### Algorithm Parameters

ZPD and SM2 parameters can be tuned:

```python
# Custom ZPD system
zpd_system = ZPDSystem(
    initial_zpd_width=0.25,  # Narrower initial range
    adaptation_rate=0.15,    # Faster adaptation
    min_zpd_width=0.1       # Tighter minimum range
)

# Custom SM2 algorithm
sm2 = SM2Algorithm(
    min_easiness=1.2,       # Lower minimum easiness
    streak_bonus_factor=0.15, # Higher streak bonuses
    difficulty_penalty_factor=0.2  # Higher difficulty penalties
)
```

This comprehensive AI system provides SpanishMaster with intelligent, adaptive learning capabilities that personalize the experience for each user while optimizing learning outcomes through data-driven approaches.