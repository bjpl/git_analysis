"""
Content model for different content types and materials.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import re

from .base import BaseModel, ValidationError


class ContentType(Enum):
    """Content type enumeration."""
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    SIMULATION = "simulation"
    DOCUMENT = "document"
    CODE = "code"
    PRESENTATION = "presentation"
    WEBINAR = "webinar"
    PODCAST = "podcast"
    EBOOK = "ebook"
    INFOGRAPHIC = "infographic"


class DifficultyLevel(Enum):
    """Difficulty level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ContentStatus(Enum):
    """Content status enumeration."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class ContentMetadata:
    """
    Metadata for content items.
    """
    
    # Basic metadata
    title: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    category: str = ""
    subject: str = ""
    
    # Educational metadata
    learning_objectives: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    estimated_duration_minutes: int = 0
    age_group: str = ""
    grade_level: str = ""
    
    # Content properties
    language: str = "en"
    accessibility_features: List[str] = field(default_factory=list)
    content_warnings: List[str] = field(default_factory=list)
    copyright_info: str = ""
    license: str = ""
    
    # Quality metrics
    rating: float = 0.0  # Average rating
    rating_count: int = 0
    view_count: int = 0
    completion_rate: float = 0.0
    
    # Technical metadata
    file_size_bytes: int = 0
    format: str = ""
    resolution: str = ""
    codec: str = ""
    bitrate: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'description': self.description,
            'keywords': self.keywords,
            'tags': self.tags,
            'category': self.category,
            'subject': self.subject,
            'learning_objectives': self.learning_objectives,
            'prerequisites': self.prerequisites,
            'difficulty_level': self.difficulty_level.value,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'age_group': self.age_group,
            'grade_level': self.grade_level,
            'language': self.language,
            'accessibility_features': self.accessibility_features,
            'content_warnings': self.content_warnings,
            'copyright_info': self.copyright_info,
            'license': self.license,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'view_count': self.view_count,
            'completion_rate': self.completion_rate,
            'file_size_bytes': self.file_size_bytes,
            'format': self.format,
            'resolution': self.resolution,
            'codec': self.codec,
            'bitrate': self.bitrate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentMetadata':
        """Create from dictionary."""
        # Handle enum field
        difficulty_level = DifficultyLevel.BEGINNER
        if 'difficulty_level' in data:
            difficulty_level = DifficultyLevel(data['difficulty_level'])
        
        return cls(
            title=data.get('title', ''),
            description=data.get('description', ''),
            keywords=data.get('keywords', []),
            tags=data.get('tags', []),
            category=data.get('category', ''),
            subject=data.get('subject', ''),
            learning_objectives=data.get('learning_objectives', []),
            prerequisites=data.get('prerequisites', []),
            difficulty_level=difficulty_level,
            estimated_duration_minutes=data.get('estimated_duration_minutes', 0),
            age_group=data.get('age_group', ''),
            grade_level=data.get('grade_level', ''),
            language=data.get('language', 'en'),
            accessibility_features=data.get('accessibility_features', []),
            content_warnings=data.get('content_warnings', []),
            copyright_info=data.get('copyright_info', ''),
            license=data.get('license', ''),
            rating=data.get('rating', 0.0),
            rating_count=data.get('rating_count', 0),
            view_count=data.get('view_count', 0),
            completion_rate=data.get('completion_rate', 0.0),
            file_size_bytes=data.get('file_size_bytes', 0),
            format=data.get('format', ''),
            resolution=data.get('resolution', ''),
            codec=data.get('codec', ''),
            bitrate=data.get('bitrate', 0)
        )


@dataclass
class Content(BaseModel):
    """
    Content model for different content types and materials.
    
    Represents any type of educational content in the curriculum system,
    from text and videos to interactive simulations and assessments.
    """
    
    # Core content properties
    content_type: ContentType = ContentType.TEXT
    status: ContentStatus = ContentStatus.DRAFT
    metadata: ContentMetadata = field(default_factory=ContentMetadata)
    
    # Content data
    content_url: str = ""  # URL or file path
    content_data: Union[str, Dict[str, Any]] = ""  # Actual content or structured data
    thumbnail_url: str = ""
    preview_data: str = ""  # Preview text or description
    
    # Versioning
    version: str = "1.0.0"
    parent_content_id: Optional[str] = None  # For content variations/translations
    revision_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Publishing
    author_id: str = ""  # User ID of content creator
    reviewer_ids: List[str] = field(default_factory=list)  # User IDs of reviewers
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Dependencies and relationships
    dependency_content_ids: List[str] = field(default_factory=list)  # Required content
    related_content_ids: List[str] = field(default_factory=list)  # Suggested content
    successor_content_ids: List[str] = field(default_factory=list)  # Next content
    
    # Analytics
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    
    # Settings
    is_interactive: bool = False
    requires_internet: bool = False
    downloadable: bool = True
    shareable: bool = True
    
    def validate(self) -> None:
        """
        Validate the content model.
        
        Raises:
            ValidationError: If validation fails
        """
        # Content type validation
        if not isinstance(self.content_type, ContentType):
            raise ValidationError("Invalid content type")
        
        # Status validation
        if not isinstance(self.status, ContentStatus):
            raise ValidationError("Invalid content status")
        
        # Title validation (from metadata)
        if not self.metadata.title.strip():
            raise ValidationError("Content title is required")
        
        if len(self.metadata.title) > 200:
            raise ValidationError("Content title must be 200 characters or less")
        
        # URL validation
        if self.content_url and not self._is_valid_url(self.content_url):
            raise ValidationError("Invalid content URL format")
        
        # Version validation
        if not re.match(r'^\d+\.\d+\.\d+$', self.version):
            raise ValidationError("Version must be in format 'x.y.z'")
        
        # Duration validation
        if self.metadata.estimated_duration_minutes < 0:
            raise ValidationError("Duration cannot be negative")
        
        # Rating validation
        if not 0.0 <= self.metadata.rating <= 5.0:
            raise ValidationError("Rating must be between 0.0 and 5.0")
        
        # Author validation
        if not self.author_id:
            raise ValidationError("Author ID is required")
        
        # Expiration validation
        if self.expires_at and self.expires_at <= datetime.utcnow():
            if self.status == ContentStatus.PUBLISHED:
                raise ValidationError("Cannot publish content that has already expired")
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL format is valid."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def publish(self, reviewer_id: str) -> None:
        """
        Publish the content.
        
        Args:
            reviewer_id: ID of the user approving publication
        """
        if self.status != ContentStatus.REVIEW:
            raise ValidationError("Content must be in review status to publish")
        
        self.status = ContentStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        
        if reviewer_id not in self.reviewer_ids:
            self.reviewer_ids.append(reviewer_id)
        
        self.add_revision("Published", reviewer_id)
        self.update_timestamp()
    
    def archive(self, user_id: str, reason: str = "") -> None:
        """
        Archive the content.
        
        Args:
            user_id: ID of the user archiving the content
            reason: Reason for archiving
        """
        self.status = ContentStatus.ARCHIVED
        self.add_revision(f"Archived: {reason}", user_id)
        self.update_timestamp()
    
    def add_revision(self, description: str, user_id: str) -> None:
        """
        Add a revision to the history.
        
        Args:
            description: Description of the change
            user_id: ID of the user making the change
        """
        revision = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'description': description,
            'version': self.version
        }
        self.revision_history.append(revision)
    
    def increment_version(self, version_type: str = 'patch') -> None:
        """
        Increment the version number.
        
        Args:
            version_type: Type of version increment ('major', 'minor', 'patch')
        """
        major, minor, patch = map(int, self.version.split('.'))
        
        if version_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif version_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        self.version = f"{major}.{minor}.{patch}"
        self.update_timestamp()
    
    def add_view(self) -> None:
        """Increment view count."""
        self.metadata.view_count += 1
        self.analytics_data['last_viewed'] = datetime.utcnow().isoformat()
        self.update_timestamp()
    
    def add_rating(self, rating: float) -> None:
        """
        Add a rating to the content.
        
        Args:
            rating: Rating value (0.0 to 5.0)
        """
        if not 0.0 <= rating <= 5.0:
            raise ValidationError("Rating must be between 0.0 and 5.0")
        
        # Calculate new average
        total_rating = self.metadata.rating * self.metadata.rating_count
        self.metadata.rating_count += 1
        self.metadata.rating = (total_rating + rating) / self.metadata.rating_count
        self.update_timestamp()
    
    def is_accessible_to_user(self, user_role: str, user_id: str = "") -> bool:
        """
        Check if content is accessible to a user.
        
        Args:
            user_role: User's role
            user_id: User's ID
            
        Returns:
            True if accessible
        """
        # Admin can access everything
        if user_role == "admin":
            return True
        
        # Published content is accessible to everyone
        if self.status == ContentStatus.PUBLISHED:
            return True
        
        # Author can access their own content
        if user_id == self.author_id:
            return True
        
        # Reviewers can access content in review
        if self.status == ContentStatus.REVIEW and user_id in self.reviewer_ids:
            return True
        
        return False
    
    def is_expired(self) -> bool:
        """Check if content has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_file_size_human_readable(self) -> str:
        """Get file size in human-readable format."""
        size = self.metadata.file_size_bytes
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def get_estimated_reading_time(self) -> int:
        """
        Estimate reading time based on content.
        
        Returns:
            Estimated reading time in minutes
        """
        if self.content_type == ContentType.TEXT and isinstance(self.content_data, str):
            # Average reading speed is about 200 words per minute
            word_count = len(self.content_data.split())
            return max(1, word_count // 200)
        
        return self.metadata.estimated_duration_minutes
    
    def add_dependency(self, content_id: str) -> None:
        """
        Add a content dependency.
        
        Args:
            content_id: ID of the required content
        """
        if content_id not in self.dependency_content_ids:
            self.dependency_content_ids.append(content_id)
            self.update_timestamp()
    
    def add_related_content(self, content_id: str) -> None:
        """
        Add related content.
        
        Args:
            content_id: ID of the related content
        """
        if content_id not in self.related_content_ids:
            self.related_content_ids.append(content_id)
            self.update_timestamp()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        return {
            'view_count': self.metadata.view_count,
            'rating': self.metadata.rating,
            'rating_count': self.metadata.rating_count,
            'completion_rate': self.metadata.completion_rate,
            'engagement_score': self._calculate_engagement_score()
        }
    
    def _calculate_engagement_score(self) -> float:
        """Calculate engagement score based on various metrics."""
        # Simple engagement score calculation
        score = 0.0
        
        if self.metadata.view_count > 0:
            score += min(self.metadata.view_count / 100, 1.0) * 0.3
        
        if self.metadata.rating_count > 0:
            score += (self.metadata.rating / 5.0) * 0.4
        
        score += self.metadata.completion_rate * 0.3
        
        return min(score, 1.0)
    
    @classmethod
    def search_by_metadata(cls, 
                          contents: List['Content'], 
                          query: str) -> List['Content']:
        """
        Search content by metadata fields.
        
        Args:
            contents: List of content to search
            query: Search query
            
        Returns:
            List of matching content
        """
        query_lower = query.lower()
        results = []
        
        for content in contents:
            metadata = content.metadata
            
            # Search in various metadata fields
            search_fields = [
                metadata.title,
                metadata.description,
                metadata.category,
                metadata.subject,
                ' '.join(metadata.keywords),
                ' '.join(metadata.tags),
                ' '.join(metadata.learning_objectives)
            ]
            
            if any(query_lower in field.lower() for field in search_fields if field):
                results.append(content)
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with nested objects."""
        data = super().to_dict()
        data['content_type'] = self.content_type.value
        data['status'] = self.status.value
        data['metadata'] = self.metadata.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Content':
        """Create from dictionary with nested objects."""
        # Extract nested objects
        metadata_data = data.pop('metadata', {})
        
        # Handle enums
        if 'content_type' in data:
            data['content_type'] = ContentType(data['content_type'])
        if 'status' in data:
            data['status'] = ContentStatus(data['status'])
        
        # Create content
        content = super().from_dict(data)
        
        # Set nested objects
        content.metadata = ContentMetadata.from_dict(metadata_data)
        
        return content
    
    def __str__(self) -> str:
        """String representation."""
        return f"Content(title='{self.metadata.title}', type='{self.content_type.value}', status='{self.status.value}')"