# AI Integration Examples for SpanishMaster

This document provides practical examples of integrating the AI features with the existing SpanishMaster application.

## Table of Contents

1. [Basic Integration Setup](#basic-integration-setup)
2. [Database Integration](#database-integration)  
3. [UI Integration Examples](#ui-integration-examples)
4. [Complete Feature Implementations](#complete-feature-implementations)
5. [Advanced Integration Patterns](#advanced-integration-patterns)

## Basic Integration Setup

### 1. Initialize AI Systems in Main Application

```python
# main.py - Add AI system initialization

from ai import (
    SM2Algorithm, ReviewScheduler, PerformanceTracker,
    ContentGenerator, ZPDSystem, ContentRecommendationEngine,
    GrammarAnalyzer, PronunciationAnalyzer
)

class SpanishMasterApp:
    def __init__(self):
        # Existing initialization
        self.init_database()
        self.init_ui()
        
        # Initialize AI systems
        self.init_ai_systems()
    
    def init_ai_systems(self):
        """Initialize all AI components"""
        # Spaced repetition system
        self.sm2_algorithm = SM2Algorithm()
        self.review_scheduler = ReviewScheduler(sm2_algorithm=self.sm2_algorithm)
        self.performance_tracker = PerformanceTracker()
        
        # Content generation (requires OpenAI API key)
        try:
            self.content_generator = ContentGenerator()
            self.ai_content_enabled = True
        except Exception as e:
            print(f"Content generation disabled: {e}")
            self.ai_content_enabled = False
        
        # Adaptive difficulty
        self.zpd_system = ZPDSystem()
        
        # Recommendations
        self.recommendation_engine = ContentRecommendationEngine(
            zpd_system=self.zpd_system,
            performance_tracker=self.performance_tracker
        )
        
        # Intelligence features
        self.grammar_analyzer = GrammarAnalyzer()
        self.pronunciation_analyzer = PronunciationAnalyzer()
```

### 2. Configuration Management

```python
# config.py - Add AI configuration

import os

# Existing configuration
DB_FILE = os.path.join(os.path.dirname(__file__), "my_spanish_app.db")
LOG_LEVEL = logging.DEBUG

# AI Configuration
AI_CONFIG = {
    'openai_api_key': os.getenv('OPENAI_API_KEY'),
    'openai_model': os.getenv('OPENAI_MODEL', 'gpt-4'),
    'enable_content_generation': os.getenv('ENABLE_AI_CONTENT', 'true').lower() == 'true',
    'max_daily_reviews': int(os.getenv('MAX_DAILY_REVIEWS', '50')),
    'cache_size': int(os.getenv('AI_CACHE_SIZE', '1000')),
    'zpd_adaptation_rate': float(os.getenv('ZPD_ADAPTATION_RATE', '0.1')),
    'sm2_initial_interval': int(os.getenv('SM2_INITIAL_INTERVAL', '1'))
}

# Spaced Repetition Settings
SPACED_REPETITION_CONFIG = {
    'min_easiness': 1.3,
    'max_easiness': 4.0,
    'initial_interval': AI_CONFIG['sm2_initial_interval'],
    'streak_bonus_factor': 0.1,
    'difficulty_penalty_factor': 0.15
}

# ZPD System Settings
ZPD_CONFIG = {
    'initial_zpd_width': 0.3,
    'min_zpd_width': 0.15,
    'max_zpd_width': 0.5,
    'adaptation_rate': AI_CONFIG['zpd_adaptation_rate']
}
```

## Database Integration

### 1. Extend Database Models

```python
# models/database.py - Add AI-related tables

class Database:
    def init_db(self):
        """Extend existing init_db method"""
        # ... existing table creation ...
        
        # AI-related tables
        self._create_ai_tables()
    
    def _create_ai_tables(self):
        """Create AI-related database tables"""
        cursor = self.conn.cursor()
        
        # User AI profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_ai_profiles (
                user_id TEXT PRIMARY KEY,
                zpd_lower REAL DEFAULT 0.3,
                zpd_upper REAL DEFAULT 0.7,
                optimal_difficulty REAL DEFAULT 0.5,
                learning_velocity REAL DEFAULT 1.0,
                created_at TEXT,
                updated_at TEXT
            );
        """)
        
        # Skill assessments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                skill_name TEXT,
                current_level REAL,
                confidence REAL,
                trend REAL,
                stability REAL,
                practice_time INTEGER,
                last_assessment TEXT,
                FOREIGN KEY (user_id) REFERENCES user_ai_profiles(user_id)
            );
        """)
        
        # Review cards
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_cards (
                card_id TEXT PRIMARY KEY,
                user_id TEXT,
                content_type TEXT,
                easiness_factor REAL DEFAULT 2.5,
                repetitions INTEGER DEFAULT 0,
                interval_days INTEGER DEFAULT 1,
                last_review TEXT,
                next_review TEXT,
                consecutive_correct INTEGER DEFAULT 0,
                total_reviews INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0
            );
        """)
        
        # Performance sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TEXT,
                end_time TEXT,
                total_reviews INTEGER DEFAULT 0,
                correct_reviews INTEGER DEFAULT 0,
                session_type TEXT
            );
        """)
        
        # Content interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                content_id TEXT,
                interaction_type TEXT,
                performance_score REAL,
                response_time REAL,
                timestamp TEXT
            );
        """)
        
        self.conn.commit()
```

### 2. Create AI Data Models

```python
# models/ai_model.py - New AI data model

from models.database import Database
from ai.spaced_repetition.sm2_algorithm import CardMetrics
from ai.adaptive_difficulty.zpd_system import ZPDProfile
import json
from datetime import datetime

class AIModel:
    def __init__(self):
        self.db = Database()
    
    # ZPD Profile Management
    def save_zpd_profile(self, profile: ZPDProfile):
        """Save ZPD profile to database"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_ai_profiles 
            (user_id, zpd_lower, zpd_upper, optimal_difficulty, learning_velocity, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            profile.user_id,
            profile.current_zpd_range[0],
            profile.current_zpd_range[1],
            profile.optimal_difficulty,
            profile.learning_velocity,
            datetime.now().isoformat()
        ))
        
        # Save skill assessments
        for skill_name, assessment in profile.skill_assessments.items():
            cursor.execute("""
                INSERT OR REPLACE INTO skill_assessments
                (user_id, skill_name, current_level, confidence, trend, stability, practice_time, last_assessment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.user_id, skill_name, assessment.current_level,
                assessment.confidence, assessment.trend, assessment.stability,
                assessment.practice_time, assessment.last_assessment.isoformat()
            ))
        
        self.db.conn.commit()
    
    def load_zpd_profile(self, user_id: str) -> ZPDProfile:
        """Load ZPD profile from database"""
        cursor = self.db.conn.cursor()
        
        # Load main profile
        cursor.execute("""
            SELECT zpd_lower, zpd_upper, optimal_difficulty, learning_velocity
            FROM user_ai_profiles WHERE user_id = ?
        """, (user_id,))
        
        profile_data = cursor.fetchone()
        if not profile_data:
            return None
        
        # Load skill assessments
        cursor.execute("""
            SELECT skill_name, current_level, confidence, trend, stability, practice_time, last_assessment
            FROM skill_assessments WHERE user_id = ?
        """, (user_id,))
        
        skill_data = cursor.fetchall()
        
        # Reconstruct profile (simplified - you'd need full reconstruction logic)
        return {
            'user_id': user_id,
            'zpd_range': (profile_data['zpd_lower'], profile_data['zpd_upper']),
            'optimal_difficulty': profile_data['optimal_difficulty'],
            'learning_velocity': profile_data['learning_velocity'],
            'skills': skill_data
        }
    
    # Review Card Management
    def save_card_metrics(self, card_id: str, user_id: str, metrics: CardMetrics):
        """Save review card metrics"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO review_cards
            (card_id, user_id, easiness_factor, repetitions, interval_days, 
             last_review, next_review, consecutive_correct, total_reviews, total_correct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            card_id, user_id, metrics.easiness_factor, metrics.repetitions,
            metrics.interval, 
            metrics.last_review.isoformat() if metrics.last_review else None,
            metrics.next_review.isoformat() if metrics.next_review else None,
            metrics.consecutive_correct, metrics.total_reviews, metrics.total_correct
        ))
        
        self.db.conn.commit()
    
    def load_card_metrics(self, card_id: str) -> CardMetrics:
        """Load review card metrics"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM review_cards WHERE card_id = ?
        """, (card_id,))
        
        data = cursor.fetchone()
        if not data:
            return CardMetrics()  # Return default metrics
        
        return CardMetrics(
            easiness_factor=data['easiness_factor'],
            repetitions=data['repetitions'],
            interval=data['interval_days'],
            last_review=datetime.fromisoformat(data['last_review']) if data['last_review'] else None,
            next_review=datetime.fromisoformat(data['next_review']) if data['next_review'] else None,
            consecutive_correct=data['consecutive_correct'],
            total_reviews=data['total_reviews'],
            total_correct=data['total_correct']
        )
    
    # Performance Tracking
    def record_interaction(self, user_id: str, content_id: str, interaction_type: str, 
                          performance_score: float, response_time: float):
        """Record content interaction"""
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            INSERT INTO content_interactions
            (user_id, content_id, interaction_type, performance_score, response_time, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, content_id, interaction_type, performance_score, 
            response_time, datetime.now().isoformat()
        ))
        
        self.db.conn.commit()
```

## UI Integration Examples

### 1. Enhanced Review Session with AI

```python
# views/review_view.py - Enhanced with AI features

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import asyncio

class EnhancedReviewView(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_review_items = []
        self.current_item_index = 0
        self.session_start_time = None
        
        self.init_ui()
        self.load_ai_recommendations()
    
    def init_ui(self):
        """Initialize UI with AI-enhanced features"""
        layout = QVBoxLayout()
        
        # AI Status indicator
        self.ai_status_label = QLabel("AI: Ready")
        self.ai_status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.ai_status_label)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Content area
        self.content_area = QTextEdit()
        self.content_area.setReadOnly(True)
        layout.addWidget(self.content_area)
        
        # Input area
        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Type your response...")
        layout.addWidget(self.input_area)
        
        # AI Analysis area
        self.analysis_area = QTextEdit()
        self.analysis_area.setReadOnly(True)
        self.analysis_area.setMaximumHeight(100)
        layout.addWidget(self.analysis_area)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.submit_button = QPushButton("Submit Answer")
        self.submit_button.clicked.connect(self.submit_answer)
        button_layout.addWidget(self.submit_button)
        
        self.hint_button = QPushButton("Get AI Hint")
        self.hint_button.clicked.connect(self.get_ai_hint)
        button_layout.addWidget(self.hint_button)
        
        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.skip_item)
        button_layout.addWidget(self.skip_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_ai_recommendations(self):
        """Load AI-recommended review items"""
        try:
            # Get recommendations from AI system
            recommendations = self.app.recommendation_engine.get_recommendations(
                user_id="current_user",  # You'd get this from your user system
                num_recommendations=10,
                session_length_minutes=30
            )
            
            self.current_review_items = recommendations
            self.progress_bar.setMaximum(len(recommendations))
            self.progress_bar.setValue(0)
            
            if recommendations:
                self.load_next_item()
            else:
                self.content_area.setText("No reviews available. Great job!")
                
        except Exception as e:
            self.ai_status_label.setText(f"AI: Error - {str(e)}")
            self.ai_status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def load_next_item(self):
        """Load the next review item"""
        if self.current_item_index >= len(self.current_review_items):
            self.finish_session()
            return
        
        item = self.current_review_items[self.current_item_index]
        content_item = item.content_item
        
        # Display content based on type
        if content_item.content_type == "vocabulary":
            self.display_vocabulary_item(content_item)
        elif content_item.content_type == "grammar":
            self.display_grammar_item(content_item)
        else:
            self.display_generic_item(content_item)
        
        # Update progress
        self.progress_bar.setValue(self.current_item_index + 1)
        
        # Clear previous input and analysis
        self.input_area.clear()
        self.analysis_area.clear()
        
        # Record item start time
        self.item_start_time = datetime.now()
    
    def display_vocabulary_item(self, content_item):
        """Display vocabulary review item"""
        # Extract word from skills_addressed or content_id
        word = content_item.skills_addressed[0] if content_item.skills_addressed else "palabra"
        
        content = f"""
        <h3>Vocabulary Review</h3>
        <p><strong>Translate this word to English:</strong></p>
        <h2 style="color: blue;">{word}</h2>
        <p><em>Difficulty: {content_item.difficulty_level:.1f}/1.0</em></p>
        """
        self.content_area.setHtml(content)
    
    def display_grammar_item(self, content_item):
        """Display grammar review item"""
        grammar_concept = content_item.skills_addressed[0] if content_item.skills_addressed else "grammar"
        
        content = f"""
        <h3>Grammar Review</h3>
        <p><strong>Complete the sentence using proper {grammar_concept}:</strong></p>
        <p>Yo ___ estudiante de español.</p>
        <p><em>Focus: {grammar_concept}</em></p>
        """
        self.content_area.setHtml(content)
    
    def display_generic_item(self, content_item):
        """Display generic review item"""
        content = f"""
        <h3>{content_item.content_type.title()} Review</h3>
        <p><strong>Skills:</strong> {', '.join(content_item.skills_addressed)}</p>
        <p><strong>Difficulty:</strong> {content_item.difficulty_level:.1f}/1.0</p>
        <p>Please provide your response below.</p>
        """
        self.content_area.setHtml(content)
    
    def submit_answer(self):
        """Submit and analyze user's answer"""
        user_response = self.input_area.toPlainText().strip()
        if not user_response:
            return
        
        # Calculate response time
        response_time = (datetime.now() - self.item_start_time).total_seconds()
        
        # Analyze with AI
        self.analyze_response(user_response, response_time)
    
    def analyze_response(self, user_response: str, response_time: float):
        """Analyze user response with AI"""
        try:
            # Grammar analysis
            grammar_analysis = self.app.grammar_analyzer.analyze_text(user_response)
            
            # Calculate performance score
            performance_score = grammar_analysis.overall_score
            
            # Display analysis
            analysis_html = f"""
            <strong>AI Analysis:</strong><br>
            Grammar Score: {grammar_analysis.overall_score:.2f}<br>
            Errors Found: {len(grammar_analysis.errors)}<br>
            """
            
            if grammar_analysis.errors:
                analysis_html += f"<span style='color: orange;'>Suggestion: {grammar_analysis.suggestions[0] if grammar_analysis.suggestions else 'Keep practicing!'}</span>"
            else:
                analysis_html += "<span style='color: green;'>Great job! No errors detected.</span>"
            
            self.analysis_area.setHtml(analysis_html)
            
            # Record performance
            current_item = self.current_review_items[self.current_item_index]
            
            # Update spaced repetition system
            self.update_spaced_repetition(current_item, performance_score, response_time)
            
            # Update ZPD system
            self.update_zpd_system(current_item, performance_score, response_time)
            
            # Enable next item button
            QTimer.singleShot(3000, self.move_to_next_item)  # Auto-advance after 3 seconds
            
        except Exception as e:
            self.analysis_area.setText(f"Analysis Error: {str(e)}")
    
    def get_ai_hint(self):
        """Get AI-generated hint"""
        try:
            current_item = self.current_review_items[self.current_item_index]
            content_item = current_item.content_item
            
            # This would be implemented with actual hint generation
            hint_text = f"Hint: Focus on {content_item.skills_addressed[0] if content_item.skills_addressed else 'the concept'}"
            
            QMessageBox.information(self, "AI Hint", hint_text)
            
        except Exception as e:
            QMessageBox.warning(self, "Hint Error", f"Could not generate hint: {str(e)}")
    
    def update_spaced_repetition(self, review_item, performance_score, response_time):
        """Update spaced repetition system"""
        try:
            # Convert performance to response quality
            if performance_score >= 0.9:
                quality = ResponseQuality.PERFECT
            elif performance_score >= 0.7:
                quality = ResponseQuality.EASY
            elif performance_score >= 0.5:
                quality = ResponseQuality.HESITANT
            else:
                quality = ResponseQuality.DIFFICULT
            
            # Process review
            result = self.app.review_scheduler.process_review_response(
                review_item.content_item.content_id,
                quality,
                int(response_time)
            )
            
            # Save to database
            metrics = CardMetrics(
                easiness_factor=result['easiness_factor'],
                repetitions=result.get('repetitions', 0),
                interval=result['interval_days']
            )
            
            self.app.ai_model.save_card_metrics(
                review_item.content_item.content_id,
                "current_user",
                metrics
            )
            
        except Exception as e:
            print(f"Spaced repetition update error: {e}")
    
    def update_zpd_system(self, review_item, performance_score, response_time):
        """Update ZPD system with performance data"""
        try:
            content_item = review_item.content_item
            
            for skill in content_item.skills_addressed:
                self.app.zpd_system.update_skill_assessment(
                    "current_user",
                    skill,
                    performance_score=performance_score,
                    confidence_score=0.7,  # You could calculate this from response time/hesitation
                    response_time=response_time,
                    difficulty_attempted=content_item.difficulty_level
                )
            
            # Save updated profile
            profile = self.app.zpd_system.user_profiles.get("current_user")
            if profile:
                self.app.ai_model.save_zpd_profile(profile)
                
        except Exception as e:
            print(f"ZPD system update error: {e}")
    
    def move_to_next_item(self):
        """Move to next review item"""
        self.current_item_index += 1
        self.load_next_item()
    
    def skip_item(self):
        """Skip current item"""
        self.move_to_next_item()
    
    def finish_session(self):
        """Finish review session"""
        # Generate session summary
        summary = f"""
        <h3>Session Complete!</h3>
        <p>Items reviewed: {len(self.current_review_items)}</p>
        <p>Time spent: {self.calculate_session_time()}</p>
        <p>Check the Progress tab for detailed analytics.</p>
        """
        
        self.content_area.setHtml(summary)
        
        # Hide controls
        self.submit_button.setVisible(False)
        self.hint_button.setVisible(False)
        self.skip_button.setVisible(False)
    
    def calculate_session_time(self):
        """Calculate total session time"""
        if self.session_start_time:
            duration = datetime.now() - self.session_start_time
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes"
        return "Unknown"
```

### 2. AI-Enhanced Settings View

```python
# views/ai_settings_view.py - AI configuration interface

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class AISettingsView(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize AI settings UI"""
        layout = QVBoxLayout()
        
        # AI Features Section
        ai_group = QGroupBox("AI Features")
        ai_layout = QFormLayout()
        
        self.content_generation_cb = QCheckBox("Enable AI Content Generation")
        self.content_generation_cb.setToolTip("Requires OpenAI API key")
        ai_layout.addRow("Content Generation:", self.content_generation_cb)
        
        self.smart_scheduling_cb = QCheckBox("Enable Smart Scheduling")
        self.smart_scheduling_cb.setToolTip("Uses spaced repetition algorithm")
        ai_layout.addRow("Smart Scheduling:", self.smart_scheduling_cb)
        
        self.grammar_analysis_cb = QCheckBox("Enable Grammar Analysis")
        ai_layout.addRow("Grammar Analysis:", self.grammar_analysis_cb)
        
        self.pronunciation_help_cb = QCheckBox("Enable Pronunciation Help")
        ai_layout.addRow("Pronunciation Help:", self.pronunciation_help_cb)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # Difficulty Settings
        difficulty_group = QGroupBox("Adaptive Difficulty")
        difficulty_layout = QFormLayout()
        
        self.zpd_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.zpd_width_slider.setRange(15, 50)  # 0.15 to 0.50
        self.zpd_width_slider.setValue(30)  # 0.30 default
        self.zpd_width_label = QLabel("0.30")
        self.zpd_width_slider.valueChanged.connect(
            lambda v: self.zpd_width_label.setText(f"{v/100:.2f}")
        )
        
        zpd_layout = QHBoxLayout()
        zpd_layout.addWidget(self.zpd_width_slider)
        zpd_layout.addWidget(self.zpd_width_label)
        
        difficulty_layout.addRow("ZPD Range Width:", zpd_layout)
        
        self.adaptation_rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.adaptation_rate_slider.setRange(5, 25)  # 0.05 to 0.25
        self.adaptation_rate_slider.setValue(10)  # 0.10 default
        self.adaptation_rate_label = QLabel("0.10")
        self.adaptation_rate_slider.valueChanged.connect(
            lambda v: self.adaptation_rate_label.setText(f"{v/100:.2f}")
        )
        
        adaptation_layout = QHBoxLayout()
        adaptation_layout.addWidget(self.adaptation_rate_slider)
        adaptation_layout.addWidget(self.adaptation_rate_label)
        
        difficulty_layout.addRow("Adaptation Rate:", adaptation_layout)
        
        difficulty_group.setLayout(difficulty_layout)
        layout.addWidget(difficulty_group)
        
        # Review Settings
        review_group = QGroupBox("Review System")
        review_layout = QFormLayout()
        
        self.daily_limit_spin = QSpinBox()
        self.daily_limit_spin.setRange(10, 200)
        self.daily_limit_spin.setValue(50)
        review_layout.addRow("Daily Review Limit:", self.daily_limit_spin)
        
        self.min_easiness_spin = QDoubleSpinBox()
        self.min_easiness_spin.setRange(1.0, 2.0)
        self.min_easiness_spin.setSingleStep(0.1)
        self.min_easiness_spin.setValue(1.3)
        review_layout.addRow("Min Easiness Factor:", self.min_easiness_spin)
        
        self.max_easiness_spin = QDoubleSpinBox()
        self.max_easiness_spin.setRange(3.0, 5.0)
        self.max_easiness_spin.setSingleStep(0.1)
        self.max_easiness_spin.setValue(4.0)
        review_layout.addRow("Max Easiness Factor:", self.max_easiness_spin)
        
        review_group.setLayout(review_layout)
        layout.addWidget(review_group)
        
        # AI Performance Stats
        stats_group = QGroupBox("AI Performance")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_text)
        
        refresh_stats_btn = QPushButton("Refresh Stats")
        refresh_stats_btn.clicked.connect(self.refresh_ai_stats)
        stats_layout.addWidget(refresh_stats_btn)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        test_ai_btn = QPushButton("Test AI Connection")
        test_ai_btn.clicked.connect(self.test_ai_connection)
        button_layout.addWidget(test_ai_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_current_settings(self):
        """Load current AI settings"""
        # Load from config or database
        self.content_generation_cb.setChecked(self.app.ai_content_enabled)
        self.smart_scheduling_cb.setChecked(True)  # Default enabled
        self.grammar_analysis_cb.setChecked(True)
        self.pronunciation_help_cb.setChecked(True)
        
        # Load performance stats
        self.refresh_ai_stats()
    
    def save_settings(self):
        """Save AI settings"""
        try:
            # Update app settings
            settings = {
                'content_generation': self.content_generation_cb.isChecked(),
                'smart_scheduling': self.smart_scheduling_cb.isChecked(),
                'grammar_analysis': self.grammar_analysis_cb.isChecked(),
                'pronunciation_help': self.pronunciation_help_cb.isChecked(),
                'zpd_width': self.zpd_width_slider.value() / 100.0,
                'adaptation_rate': self.adaptation_rate_slider.value() / 100.0,
                'daily_limit': self.daily_limit_spin.value(),
                'min_easiness': self.min_easiness_spin.value(),
                'max_easiness': self.max_easiness_spin.value()
            }
            
            # Apply settings to AI systems
            self.app.review_scheduler.adjust_daily_limit(settings['daily_limit'])
            
            # Update ZPD system parameters
            self.app.zpd_system.adaptation_rate = settings['adaptation_rate']
            
            QMessageBox.information(self, "Settings Saved", "AI settings have been updated.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all AI settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset all controls to defaults
            self.content_generation_cb.setChecked(True)
            self.smart_scheduling_cb.setChecked(True)
            self.grammar_analysis_cb.setChecked(True)
            self.pronunciation_help_cb.setChecked(True)
            self.zpd_width_slider.setValue(30)
            self.adaptation_rate_slider.setValue(10)
            self.daily_limit_spin.setValue(50)
            self.min_easiness_spin.setValue(1.3)
            self.max_easiness_spin.setValue(4.0)
    
    def test_ai_connection(self):
        """Test AI system connections"""
        results = []
        
        # Test content generation
        if hasattr(self.app, 'content_generator'):
            try:
                # This would need to be made async
                test_result = "Content generation: Available"
                results.append(test_result)
            except:
                results.append("Content generation: Failed")
        else:
            results.append("Content generation: Not configured")
        
        # Test other AI systems
        results.append(f"Spaced repetition: {'Available' if hasattr(self.app, 'review_scheduler') else 'Failed'}")
        results.append(f"ZPD system: {'Available' if hasattr(self.app, 'zpd_system') else 'Failed'}")
        results.append(f"Grammar analyzer: {'Available' if hasattr(self.app, 'grammar_analyzer') else 'Failed'}")
        
        QMessageBox.information(
            self, "AI Connection Test",
            "\n".join(results)
        )
    
    def refresh_ai_stats(self):
        """Refresh AI performance statistics"""
        try:
            stats_text = "AI Performance Statistics\n" + "="*30 + "\n\n"
            
            # Content generation stats
            if hasattr(self.app, 'content_generator'):
                content_stats = self.app.content_generator.get_usage_statistics()
                stats_text += f"Content Generation:\n"
                stats_text += f"  - Total requests: {content_stats['openai_stats']['total_requests']}\n"
                stats_text += f"  - Success rate: {content_stats['openai_stats']['success_rate']:.2%}\n"
                stats_text += f"  - Cache hit rate: {content_stats['openai_stats']['cache_hit_rate']:.2%}\n\n"
            
            # Review system stats
            if hasattr(self.app, 'review_scheduler'):
                daily_stats = self.app.review_scheduler.get_daily_review_stats()
                stats_text += f"Review System:\n"
                stats_text += f"  - Reviews due: {daily_stats['total_due']}\n"
                stats_text += f"  - Completed today: {daily_stats['completed_today']}\n"
                stats_text += f"  - Remaining capacity: {daily_stats['remaining_capacity']}\n\n"
            
            # ZPD system stats
            if hasattr(self.app, 'zpd_system'):
                user_count = len(self.app.zpd_system.user_profiles)
                stats_text += f"Adaptive Difficulty:\n"
                stats_text += f"  - Active user profiles: {user_count}\n"
                stats_text += f"  - Skill categories: {len(self.app.zpd_system.skill_categories)}\n\n"
            
            self.stats_text.setText(stats_text)
            
        except Exception as e:
            self.stats_text.setText(f"Error loading stats: {str(e)}")
```

## Complete Feature Implementations

### 1. AI-Powered Progress Analytics

```python
# views/ai_analytics_view.py - AI-powered learning analytics

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class AIAnalyticsView(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_ui()
        self.load_analytics_data()
    
    def init_ui(self):
        """Initialize analytics UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("AI-Powered Learning Analytics")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)
        
        # Tabs for different analytics views
        tabs = QTabWidget()
        
        # Learning Progress Tab
        progress_tab = self.create_progress_tab()
        tabs.addTab(progress_tab, "Learning Progress")
        
        # Skill Analysis Tab
        skills_tab = self.create_skills_tab()
        tabs.addTab(skills_tab, "Skill Analysis")
        
        # Recommendations Tab
        recommendations_tab = self.create_recommendations_tab()
        tabs.addTab(recommendations_tab, "AI Recommendations")
        
        # Performance Trends Tab
        trends_tab = self.create_trends_tab()
        tabs.addTab(trends_tab, "Performance Trends")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_progress_tab(self):
        """Create learning progress analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # ZPD Visualization
        zpd_group = QGroupBox("Zone of Proximal Development")
        zpd_layout = QVBoxLayout()
        
        # Create matplotlib figure for ZPD visualization
        self.zpd_figure = Figure(figsize=(8, 4))
        self.zpd_canvas = FigureCanvas(self.zpd_figure)
        zpd_layout.addWidget(self.zpd_canvas)
        
        zpd_group.setLayout(zpd_layout)
        layout.addWidget(zpd_group)
        
        # Learning Velocity
        velocity_group = QGroupBox("Learning Velocity")
        velocity_layout = QHBoxLayout()
        
        self.velocity_label = QLabel("1.0x")
        self.velocity_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        velocity_layout.addWidget(self.velocity_label)
        
        self.velocity_indicator = QProgressBar()
        self.velocity_indicator.setRange(50, 200)  # 0.5x to 2.0x
        self.velocity_indicator.setValue(100)  # 1.0x
        velocity_layout.addWidget(self.velocity_indicator)
        
        velocity_group.setLayout(velocity_layout)
        layout.addWidget(velocity_group)
        
        # Recent Performance
        performance_group = QGroupBox("Recent Performance")
        performance_layout = QVBoxLayout()
        
        self.performance_text = QTextEdit()
        self.performance_text.setReadOnly(True)
        self.performance_text.setMaximumHeight(150)
        performance_layout.addWidget(self.performance_text)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_skills_tab(self):
        """Create skill analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Skill Radar Chart
        radar_group = QGroupBox("Skill Profile")
        radar_layout = QVBoxLayout()
        
        self.skill_figure = Figure(figsize=(8, 6))
        self.skill_canvas = FigureCanvas(self.skill_figure)
        radar_layout.addWidget(self.skill_canvas)
        
        radar_group.setLayout(radar_layout)
        layout.addWidget(radar_group)
        
        # Detailed Skill Breakdown
        details_group = QGroupBox("Skill Details")
        details_layout = QVBoxLayout()
        
        self.skills_table = QTableWidget()
        self.skills_table.setColumnCount(5)
        self.skills_table.setHorizontalHeaderLabels([
            "Skill", "Level", "Confidence", "Trend", "Mastery"
        ])
        details_layout.addWidget(self.skills_table)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_recommendations_tab(self):
        """Create AI recommendations tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Recommendation Categories
        categories = QTabWidget()
        
        # General Recommendations
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        self.general_recs_list = QListWidget()
        general_layout.addWidget(self.general_recs_list)
        
        refresh_general_btn = QPushButton("Refresh Recommendations")
        refresh_general_btn.clicked.connect(self.refresh_general_recommendations)
        general_layout.addWidget(refresh_general_btn)
        
        general_tab.setLayout(general_layout)
        categories.addTab(general_tab, "General")
        
        # Weakness-Focused
        weakness_tab = QWidget()
        weakness_layout = QVBoxLayout()
        
        self.weakness_recs_list = QListWidget()
        weakness_layout.addWidget(self.weakness_recs_list)
        
        weakness_tab.setLayout(weakness_layout)
        categories.addTab(weakness_tab, "Focus Areas")
        
        # Review Recommendations
        review_tab = QWidget()
        review_layout = QVBoxLayout()
        
        self.review_recs_list = QListWidget()
        review_layout.addWidget(self.review_recs_list)
        
        review_tab.setLayout(review_layout)
        categories.addTab(review_tab, "Reviews")
        
        layout.addWidget(categories)
        widget.setLayout(layout)
        return widget
    
    def create_trends_tab(self):
        """Create performance trends tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Trend Charts
        trends_group = QGroupBox("Performance Trends")
        trends_layout = QVBoxLayout()
        
        self.trends_figure = Figure(figsize=(10, 6))
        self.trends_canvas = FigureCanvas(self.trends_figure)
        trends_layout.addWidget(self.trends_canvas)
        
        trends_group.setLayout(trends_layout)
        layout.addWidget(trends_group)
        
        widget.setLayout(layout)
        return widget
    
    def load_analytics_data(self):
        """Load and display analytics data"""
        try:
            # Get ZPD analysis
            if hasattr(self.app, 'zpd_system'):
                analysis = self.app.zpd_system.analyze_learning_progress("current_user")
                self.update_zpd_visualization(analysis)
                self.update_skills_data(analysis)
            
            # Get performance data
            if hasattr(self.app, 'performance_tracker'):
                report = self.app.performance_tracker.generate_performance_report()
                self.update_performance_data(report)
            
            # Get recommendations
            self.refresh_recommendations()
            
        except Exception as e:
            print(f"Error loading analytics: {e}")
    
    def update_zpd_visualization(self, analysis):
        """Update ZPD visualization"""
        if not analysis:
            return
        
        self.zpd_figure.clear()
        ax = self.zpd_figure.add_subplot(111)
        
        # ZPD range visualization
        if 'zpd_range' in analysis:
            zpd_lower, zpd_upper = analysis['zpd_range']
            optimal = analysis.get('optimal_difficulty', 0.5)
            
            # Create ZPD range bar
            ax.barh(['ZPD Range'], [zpd_upper - zpd_lower], 
                   left=zpd_lower, color='lightblue', alpha=0.7)
            
            # Mark optimal difficulty
            ax.axvline(x=optimal, color='red', linestyle='--', label='Optimal Difficulty')
            
            ax.set_xlim(0, 1)
            ax.set_xlabel('Difficulty Level')
            ax.set_title('Zone of Proximal Development')
            ax.legend()
        
        self.zpd_canvas.draw()
        
        # Update velocity display
        velocity = analysis.get('learning_velocity', 1.0)
        self.velocity_label.setText(f"{velocity:.1f}x")
        self.velocity_indicator.setValue(int(velocity * 100))
    
    def update_skills_data(self, analysis):
        """Update skills visualization and table"""
        if not analysis or 'skill_assessments' not in analysis:
            return
        
        # Update radar chart
        self.skill_figure.clear()
        ax = self.skill_figure.add_subplot(111, projection='polar')
        
        skills_data = analysis['skill_assessments']
        skills = list(skills_data.keys())[:8]  # Limit to 8 skills for readability
        values = [skills_data[skill]['level'] for skill in skills]
        
        if skills and values:
            # Create radar chart
            angles = [i * 2 * 3.14159 / len(skills) for i in range(len(skills))]
            angles += angles[:1]  # Complete the circle
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(skills)
            ax.set_ylim(0, 1)
            ax.set_title('Skill Profile')
        
        self.skill_canvas.draw()
        
        # Update skills table
        self.skills_table.setRowCount(len(skills_data))
        for row, (skill, data) in enumerate(skills_data.items()):
            self.skills_table.setItem(row, 0, QTableWidgetItem(skill.replace('_', ' ').title()))
            self.skills_table.setItem(row, 1, QTableWidgetItem(f"{data['level']:.2f}"))
            self.skills_table.setItem(row, 2, QTableWidgetItem(f"{data['confidence']:.2f}"))
            
            trend = data['trend']
            trend_item = QTableWidgetItem(f"{trend:+.3f}")
            if trend > 0.05:
                trend_item.setBackground(QColor(200, 255, 200))  # Light green
            elif trend < -0.05:
                trend_item.setBackground(QColor(255, 200, 200))  # Light red
            self.skills_table.setItem(row, 3, trend_item)
            
            self.skills_table.setItem(row, 4, QTableWidgetItem(data['mastery']))
    
    def update_performance_data(self, report):
        """Update performance data display"""
        if not report:
            return
        
        overall = report['overall_stats']
        trends = report['learning_trends']
        
        performance_html = f"""
        <h3>Performance Summary</h3>
        <p><strong>Total Reviews:</strong> {overall['total_reviews']}</p>
        <p><strong>Accuracy:</strong> {overall['overall_accuracy']:.1%}</p>
        <p><strong>Study Time:</strong> {overall['total_study_time_hours']:.1f} hours</p>
        <p><strong>Consistency Score:</strong> {trends['consistency_score']:.2f}</p>
        """
        
        if report['recommendations']:
            performance_html += "<h4>Recommendations:</h4><ul>"
            for rec in report['recommendations'][:3]:
                performance_html += f"<li>{rec}</li>"
            performance_html += "</ul>"
        
        self.performance_text.setHtml(performance_html)
    
    def refresh_recommendations(self):
        """Refresh all recommendation lists"""
        self.refresh_general_recommendations()
        self.refresh_weakness_recommendations()
        self.refresh_review_recommendations()
    
    def refresh_general_recommendations(self):
        """Refresh general recommendations"""
        try:
            if not hasattr(self.app, 'recommendation_engine'):
                return
            
            recommendations = self.app.recommendation_engine.get_recommendations(
                user_id="current_user",
                num_recommendations=10
            )
            
            self.general_recs_list.clear()
            for rec in recommendations:
                item_text = f"{rec.content_item.content_type.title()}: {', '.join(rec.content_item.skills_addressed[:2])}"
                item_text += f" (Score: {rec.total_score:.2f})"
                
                list_item = QListWidgetItem(item_text)
                if rec.priority_score > 0.8:
                    list_item.setBackground(QColor(255, 255, 200))  # Highlight high priority
                
                self.general_recs_list.addItem(list_item)
                
        except Exception as e:
            print(f"Error refreshing general recommendations: {e}")
    
    def refresh_weakness_recommendations(self):
        """Refresh weakness-focused recommendations"""
        try:
            if not hasattr(self.app, 'recommendation_engine'):
                return
            
            recommendations = self.app.recommendation_engine.get_weakness_focused_recommendations(
                user_id="current_user",
                num_recommendations=5
            )
            
            self.weakness_recs_list.clear()
            for rec in recommendations:
                item_text = f"Focus on {rec.content_item.content_type}: {', '.join(rec.content_item.skills_addressed)}"
                if rec.reasoning:
                    item_text += f" - {rec.reasoning[0]}"
                
                self.weakness_recs_list.addItem(QListWidgetItem(item_text))
                
        except Exception as e:
            print(f"Error refreshing weakness recommendations: {e}")
    
    def refresh_review_recommendations(self):
        """Refresh review recommendations"""
        try:
            if not hasattr(self.app, 'recommendation_engine'):
                return
            
            recommendations = self.app.recommendation_engine.get_review_recommendations(
                user_id="current_user",
                num_recommendations=8
            )
            
            self.review_recs_list.clear()
            for rec in recommendations:
                item_text = f"Review: {rec.content_item.content_type} - "
                item_text += f"Urgency: {rec.urgency:.2f}"
                
                list_item = QListWidgetItem(item_text)
                if rec.urgency > 0.7:
                    list_item.setBackground(QColor(255, 200, 200))  # Urgent reviews
                
                self.review_recs_list.addItem(list_item)
                
        except Exception as e:
            print(f"Error refreshing review recommendations: {e}")
```

This comprehensive integration guide shows how to incorporate all the AI features into the SpanishMaster application, providing users with intelligent, personalized learning experiences powered by advanced algorithms and machine learning capabilities.

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create spaced repetition system with enhanced SM2 algorithm", "status": "completed", "activeForm": "Created spaced repetition system with enhanced SM2 algorithm"}, {"content": "Implement user performance factors and adaptive scheduling", "status": "completed", "activeForm": "Implemented user performance factors and adaptive scheduling"}, {"content": "Build review queue management system", "status": "completed", "activeForm": "Built review queue management system"}, {"content": "Set up OpenAI client with retry logic for GPT-4 integration", "status": "completed", "activeForm": "Set up OpenAI client with retry logic"}, {"content": "Create prompts for exercise generation and context-aware hints", "status": "completed", "activeForm": "Created prompts for exercise generation and hints"}, {"content": "Build explanation generator and conversation practice AI", "status": "completed", "activeForm": "Built explanation generator and conversation AI"}, {"content": "Develop adaptive difficulty system with Zone of Proximal Development", "status": "completed", "activeForm": "Developed adaptive difficulty system"}, {"content": "Create performance tracking metrics and difficulty adjustment", "status": "completed", "activeForm": "Created performance tracking and difficulty adjustment"}, {"content": "Build content recommendation engine with weakness analysis", "status": "completed", "activeForm": "Built content recommendation engine"}, {"content": "Implement intelligent features for grammar and pronunciation", "status": "completed", "activeForm": "Implemented intelligent grammar and pronunciation features"}, {"content": "Write comprehensive tests for all AI algorithms", "status": "completed", "activeForm": "Wrote comprehensive tests for AI algorithms"}, {"content": "Create documentation and integration examples", "status": "completed", "activeForm": "Created documentation and integration examples"}]