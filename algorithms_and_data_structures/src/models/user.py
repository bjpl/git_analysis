"""
User model for learner profiles and authentication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import re

from .base import BaseModel, ValidationError


class UserRole(Enum):
    """User role enumeration."""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    GUEST = "guest"


class LearningStyle(Enum):
    """Learning style preferences."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MIXED = "mixed"


class DifficultyPreference(Enum):
    """Difficulty level preferences."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ADAPTIVE = "adaptive"  # Automatically adjust


@dataclass
class LearningPreferences:
    """
    User learning preferences and settings.
    """
    
    learning_style: LearningStyle = LearningStyle.MIXED
    difficulty_preference: DifficultyPreference = DifficultyPreference.ADAPTIVE
    preferred_content_types: List[str] = field(default_factory=list)
    daily_goal_minutes: int = 30
    notification_enabled: bool = True
    auto_advance: bool = True
    review_frequency_days: int = 7
    preferred_languages: List[str] = field(default_factory=lambda: ["en"])
    accessibility_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'learning_style': self.learning_style.value,
            'difficulty_preference': self.difficulty_preference.value,
            'preferred_content_types': self.preferred_content_types,
            'daily_goal_minutes': self.daily_goal_minutes,
            'notification_enabled': self.notification_enabled,
            'auto_advance': self.auto_advance,
            'review_frequency_days': self.review_frequency_days,
            'preferred_languages': self.preferred_languages,
            'accessibility_settings': self.accessibility_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningPreferences':
        """Create from dictionary."""
        return cls(
            learning_style=LearningStyle(data.get('learning_style', 'mixed')),
            difficulty_preference=DifficultyPreference(data.get('difficulty_preference', 'adaptive')),
            preferred_content_types=data.get('preferred_content_types', []),
            daily_goal_minutes=data.get('daily_goal_minutes', 30),
            notification_enabled=data.get('notification_enabled', True),
            auto_advance=data.get('auto_advance', True),
            review_frequency_days=data.get('review_frequency_days', 7),
            preferred_languages=data.get('preferred_languages', ["en"]),
            accessibility_settings=data.get('accessibility_settings', {})
        )


@dataclass
class UserProfile:
    """
    Extended user profile information.
    """
    
    display_name: str = ""
    bio: str = ""
    avatar_url: str = ""
    location: str = ""
    website: str = ""
    social_links: Dict[str, str] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    experience_level: str = "beginner"
    goals: List[str] = field(default_factory=list)
    certifications: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'location': self.location,
            'website': self.website,
            'social_links': self.social_links,
            'skills': self.skills,
            'interests': self.interests,
            'experience_level': self.experience_level,
            'goals': self.goals,
            'certifications': self.certifications
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create from dictionary."""
        return cls(
            display_name=data.get('display_name', ''),
            bio=data.get('bio', ''),
            avatar_url=data.get('avatar_url', ''),
            location=data.get('location', ''),
            website=data.get('website', ''),
            social_links=data.get('social_links', {}),
            skills=data.get('skills', []),
            interests=data.get('interests', []),
            experience_level=data.get('experience_level', 'beginner'),
            goals=data.get('goals', []),
            certifications=data.get('certifications', [])
        )


@dataclass
class User(BaseModel):
    """
    User model for learner profiles and authentication.
    
    Represents a user in the curriculum management system with
    authentication, profile, and learning preference information.
    """
    
    username: str = ""
    email: str = ""
    password_hash: str = ""  # Never store plain passwords
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    login_count: int = 0
    
    # Profile and preferences
    profile: UserProfile = field(default_factory=UserProfile)
    learning_preferences: LearningPreferences = field(default_factory=LearningPreferences)
    
    # Activity tracking
    total_study_time_minutes: int = 0
    courses_enrolled: List[str] = field(default_factory=list)  # Course IDs
    courses_completed: List[str] = field(default_factory=list)  # Course IDs
    achievements: List[Dict[str, Any]] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    
    # Settings
    timezone: str = "UTC"
    language: str = "en"
    theme: str = "light"
    
    def validate(self) -> None:
        """
        Validate the user model.
        
        Raises:
            ValidationError: If validation fails
        """
        # Username validation
        if not self.username:
            raise ValidationError("Username is required")
        
        if len(self.username) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.username):
            raise ValidationError("Username can only contain letters, numbers, hyphens, and underscores")
        
        # Email validation
        if not self.email:
            raise ValidationError("Email is required")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValidationError("Invalid email format")
        
        # Role validation
        if not isinstance(self.role, UserRole):
            raise ValidationError("Invalid user role")
        
        # Study time validation
        if self.total_study_time_minutes < 0:
            raise ValidationError("Total study time cannot be negative")
        
        # Login count validation
        if self.login_count < 0:
            raise ValidationError("Login count cannot be negative")
    
    def authenticate(self, password: str) -> bool:
        """
        Authenticate user with password.
        
        Args:
            password: Plain text password to check
            
        Returns:
            True if password is correct
            
        Note:
            In a real implementation, this would use proper password hashing
            like bcrypt, scrypt, or Argon2.
        """
        # This is a placeholder - use proper password hashing in production
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.password_hash == password_hash
    
    def set_password(self, password: str) -> None:
        """
        Set user password with proper hashing.
        
        Args:
            password: Plain text password to hash and store
        """
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        # This is a placeholder - use proper password hashing in production
        import hashlib
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.update_timestamp()
    
    def record_login(self) -> None:
        """Record a successful login."""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.update_timestamp()
    
    def enroll_in_course(self, course_id: str) -> None:
        """
        Enroll user in a course.
        
        Args:
            course_id: ID of the course to enroll in
        """
        if course_id not in self.courses_enrolled:
            self.courses_enrolled.append(course_id)
            self.update_timestamp()
    
    def complete_course(self, course_id: str) -> None:
        """
        Mark a course as completed.
        
        Args:
            course_id: ID of the completed course
        """
        if course_id not in self.courses_completed:
            self.courses_completed.append(course_id)
            self.update_timestamp()
    
    def add_study_time(self, minutes: int) -> None:
        """
        Add study time to user's total.
        
        Args:
            minutes: Number of minutes to add
        """
        if minutes > 0:
            self.total_study_time_minutes += minutes
            self.update_timestamp()
    
    def add_achievement(self, achievement: Dict[str, Any]) -> None:
        """
        Add an achievement to the user's profile.
        
        Args:
            achievement: Achievement data
        """
        achievement['earned_at'] = datetime.utcnow().isoformat()
        self.achievements.append(achievement)
        self.update_timestamp()
    
    def add_badge(self, badge_name: str) -> None:
        """
        Add a badge to the user's profile.
        
        Args:
            badge_name: Name of the badge
        """
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.update_timestamp()
    
    def get_enrollment_status(self, course_id: str) -> str:
        """
        Get enrollment status for a course.
        
        Args:
            course_id: ID of the course to check
            
        Returns:
            Enrollment status: 'not_enrolled', 'enrolled', 'completed'
        """
        if course_id in self.courses_completed:
            return 'completed'
        elif course_id in self.courses_enrolled:
            return 'enrolled'
        else:
            return 'not_enrolled'
    
    def get_study_streak(self) -> int:
        """
        Calculate current study streak in days.
        
        Returns:
            Number of consecutive days with study activity
            
        Note:
            This is a placeholder implementation. In a real system,
            you'd track daily activity in a separate model.
        """
        # Placeholder implementation
        return self.get_metadata('study_streak', 0)
    
    def update_profile(self, profile_data: Dict[str, Any]) -> None:
        """
        Update user profile.
        
        Args:
            profile_data: Dictionary of profile fields to update
        """
        for key, value in profile_data.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)
        self.update_timestamp()
    
    def update_preferences(self, preferences_data: Dict[str, Any]) -> None:
        """
        Update learning preferences.
        
        Args:
            preferences_data: Dictionary of preference fields to update
        """
        for key, value in preferences_data.items():
            if hasattr(self.learning_preferences, key):
                if key in ['learning_style', 'difficulty_preference']:
                    # Handle enum fields
                    if key == 'learning_style':
                        value = LearningStyle(value)
                    elif key == 'difficulty_preference':
                        value = DifficultyPreference(value)
                setattr(self.learning_preferences, key, value)
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with nested objects."""
        data = super().to_dict()
        data['profile'] = self.profile.to_dict()
        data['learning_preferences'] = self.learning_preferences.to_dict()
        data['role'] = self.role.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create from dictionary with nested objects."""
        # Extract nested objects
        profile_data = data.pop('profile', {})
        preferences_data = data.pop('learning_preferences', {})
        
        # Handle enum
        if 'role' in data:
            data['role'] = UserRole(data['role'])
        
        # Create user
        user = super().from_dict(data)
        
        # Set nested objects
        user.profile = UserProfile.from_dict(profile_data)
        user.learning_preferences = LearningPreferences.from_dict(preferences_data)
        
        return user
    
    def __str__(self) -> str:
        """String representation."""
        return f"User(username='{self.username}', email='{self.email}', role='{self.role.value}')"