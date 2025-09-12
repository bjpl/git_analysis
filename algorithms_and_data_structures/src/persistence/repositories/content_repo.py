"""
Content Repository

Repository for managing educational content including articles, examples, and resources.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .base import BaseRepository
from ..exceptions import ValidationError, RepositoryError


class ContentType(Enum):
    """Content type enumeration."""
    ARTICLE = "article"
    VIDEO = "video"
    CODE_EXAMPLE = "code_example"
    EXERCISE = "exercise"
    QUIZ = "quiz"
    RESOURCE = "resource"
    REFERENCE = "reference"


class ContentStatus(Enum):
    """Content status enumeration."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class Content:
    """Content entity representing educational content."""
    
    id: Optional[str] = None
    title: str = ""
    description: str = ""
    content_type: str = ContentType.ARTICLE.value
    status: str = ContentStatus.DRAFT.value
    body: str = ""
    metadata: Dict[str, Any] = None
    tags: List[str] = None
    difficulty_level: str = "beginner"
    estimated_read_time_minutes: int = 0
    author: str = ""
    curriculum_id: Optional[str] = None
    module_id: Optional[str] = None
    lesson_id: Optional[str] = None
    prerequisites: List[str] = None
    learning_objectives: List[str] = None
    resources: List[Dict[str, Any]] = None
    version: str = "1.0.0"
    language: str = "en"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    published_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
        if self.tags is None:
            self.tags = []
        if self.prerequisites is None:
            self.prerequisites = []
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.resources is None:
            self.resources = []


@dataclass
class CodeExample:
    """Code example entity for programming content."""
    
    id: Optional[str] = None
    content_id: str = ""
    title: str = ""
    description: str = ""
    code: str = ""
    language: str = "python"
    output: Optional[str] = None
    explanation: str = ""
    complexity: Dict[str, str] = None  # time/space complexity
    tags: List[str] = None
    difficulty_level: str = "beginner"
    is_runnable: bool = False
    test_cases: List[Dict[str, Any]] = None
    order: int = 0
    
    def __post_init__(self):
        """Initialize default values."""
        if self.complexity is None:
            self.complexity = {"time": "O(1)", "space": "O(1)"}
        if self.tags is None:
            self.tags = []
        if self.test_cases is None:
            self.test_cases = []


@dataclass
class Exercise:
    """Exercise entity for practice problems."""
    
    id: Optional[str] = None
    content_id: str = ""
    title: str = ""
    description: str = ""
    problem_statement: str = ""
    difficulty_level: str = "beginner"
    estimated_time_minutes: int = 30
    hints: List[str] = None
    solution: Dict[str, Any] = None
    test_cases: List[Dict[str, Any]] = None
    constraints: List[str] = None
    topics: List[str] = None
    companies: List[str] = None  # Companies that asked this problem
    acceptance_rate: float = 0.0
    order: int = 0
    
    def __post_init__(self):
        """Initialize default values."""
        if self.hints is None:
            self.hints = []
        if self.solution is None:
            self.solution = {}
        if self.test_cases is None:
            self.test_cases = []
        if self.constraints is None:
            self.constraints = []
        if self.topics is None:
            self.topics = []
        if self.companies is None:
            self.companies = []


class ContentRepository(BaseRepository[Content]):
    """Repository for content management."""
    
    def __init__(self, storage):
        super().__init__(storage, "content")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate content-specific fields."""
        required_fields = ['title', 'content_type']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Content {field} is required")
        
        # Validate content type
        valid_types = [ct.value for ct in ContentType]
        if entity_data.get('content_type') not in valid_types:
            raise ValidationError(f"Content type must be one of: {valid_types}")
        
        # Validate status
        valid_statuses = [cs.value for cs in ContentStatus]
        if entity_data.get('status') not in valid_statuses:
            raise ValidationError(f"Content status must be one of: {valid_statuses}")
        
        # Validate difficulty level
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if entity_data.get('difficulty_level') not in valid_levels:
            raise ValidationError(f"Difficulty level must be one of: {valid_levels}")
        
        # Validate read time
        read_time = entity_data.get('estimated_read_time_minutes', 0)
        if not isinstance(read_time, int) or read_time < 0:
            raise ValidationError("Estimated read time must be a non-negative integer")
    
    def _serialize_entity(self, entity: Content) -> Dict[str, Any]:
        """Serialize content to dictionary."""
        return {
            'id': entity.id,
            'title': entity.title,
            'description': entity.description,
            'content_type': entity.content_type,
            'status': entity.status,
            'body': entity.body,
            'metadata': entity.metadata,
            'tags': entity.tags,
            'difficulty_level': entity.difficulty_level,
            'estimated_read_time_minutes': entity.estimated_read_time_minutes,
            'author': entity.author,
            'curriculum_id': entity.curriculum_id,
            'module_id': entity.module_id,
            'lesson_id': entity.lesson_id,
            'prerequisites': entity.prerequisites,
            'learning_objectives': entity.learning_objectives,
            'resources': entity.resources,
            'version': entity.version,
            'language': entity.language,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at,
            'published_at': entity.published_at
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Content:
        """Deserialize dictionary to content."""
        return Content(
            id=data.get('id'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            content_type=data.get('content_type', ContentType.ARTICLE.value),
            status=data.get('status', ContentStatus.DRAFT.value),
            body=data.get('body', ''),
            metadata=data.get('metadata', {}),
            tags=data.get('tags', []),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            estimated_read_time_minutes=data.get('estimated_read_time_minutes', 0),
            author=data.get('author', ''),
            curriculum_id=data.get('curriculum_id'),
            module_id=data.get('module_id'),
            lesson_id=data.get('lesson_id'),
            prerequisites=data.get('prerequisites', []),
            learning_objectives=data.get('learning_objectives', []),
            resources=data.get('resources', []),
            version=data.get('version', '1.0.0'),
            language=data.get('language', 'en'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            published_at=data.get('published_at')
        )
    
    def find_by_type(self, content_type: str) -> List[Content]:
        """Find content by type."""
        return self.find_by_field('content_type', content_type)
    
    def find_by_status(self, status: str) -> List[Content]:
        """Find content by status."""
        return self.find_by_field('status', status)
    
    def find_by_author(self, author: str) -> List[Content]:
        """Find content by author."""
        return self.find_by_field('author', author)
    
    def find_by_curriculum(self, curriculum_id: str) -> List[Content]:
        """Find content by curriculum."""
        return self.find_by_field('curriculum_id', curriculum_id)
    
    def find_by_module(self, module_id: str) -> List[Content]:
        """Find content by module."""
        return self.find_by_field('module_id', module_id)
    
    def find_by_lesson(self, lesson_id: str) -> List[Content]:
        """Find content by lesson."""
        return self.find_by_field('lesson_id', lesson_id)
    
    def find_published(self) -> List[Content]:
        """Find published content."""
        return self.find_by_status(ContentStatus.PUBLISHED.value)
    
    def find_by_tags(self, tags: List[str]) -> List[Content]:
        """Find content that has any of the specified tags."""
        try:
            all_content = self.list_all()
            matching_content = []
            
            for content in all_content:
                if any(tag in content.tags for tag in tags):
                    matching_content.append(content)
            
            return matching_content
            
        except Exception as e:
            raise RepositoryError(f"Failed to find content by tags: {str(e)}")
    
    def find_by_difficulty(self, difficulty_level: str) -> List[Content]:
        """Find content by difficulty level."""
        return self.find_by_field('difficulty_level', difficulty_level)
    
    def publish_content(self, content_id: str) -> bool:
        """Publish content."""
        content = self.get(content_id)
        if not content:
            return False
        
        content.status = ContentStatus.PUBLISHED.value
        content.published_at = datetime.now().isoformat()
        return self.update(content_id, content)
    
    def archive_content(self, content_id: str) -> bool:
        """Archive content."""
        content = self.get(content_id)
        if not content:
            return False
        
        content.status = ContentStatus.ARCHIVED.value
        return self.update(content_id, content)
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get content repository statistics."""
        try:
            all_content = self.list_all()
            
            stats = {
                'total_count': len(all_content),
                'by_type': {},
                'by_status': {},
                'by_difficulty': {},
                'by_author': {},
                'total_read_time_minutes': 0
            }
            
            for content in all_content:
                # Count by type
                content_type = content.content_type
                stats['by_type'][content_type] = stats['by_type'].get(content_type, 0) + 1
                
                # Count by status
                status = content.status
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by difficulty
                difficulty = content.difficulty_level
                stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1
                
                # Count by author
                author = content.author
                if author:
                    stats['by_author'][author] = stats['by_author'].get(author, 0) + 1
                
                # Sum read time
                stats['total_read_time_minutes'] += content.estimated_read_time_minutes
            
            return stats
            
        except Exception as e:
            raise RepositoryError(f"Failed to get content stats: {str(e)}")


class CodeExampleRepository(BaseRepository[CodeExample]):
    """Repository for code example management."""
    
    def __init__(self, storage):
        super().__init__(storage, "code_example")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate code example-specific fields."""
        required_fields = ['content_id', 'title', 'code', 'language']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Code example {field} is required")
        
        # Validate programming language
        valid_languages = [
            'python', 'javascript', 'java', 'cpp', 'c', 'csharp',
            'go', 'rust', 'kotlin', 'swift', 'typescript', 'php'
        ]
        if entity_data.get('language') not in valid_languages:
            raise ValidationError(f"Programming language must be one of: {valid_languages}")
        
        # Validate difficulty level
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if entity_data.get('difficulty_level') not in valid_levels:
            raise ValidationError(f"Difficulty level must be one of: {valid_levels}")
    
    def _serialize_entity(self, entity: CodeExample) -> Dict[str, Any]:
        """Serialize code example to dictionary."""
        return {
            'id': entity.id,
            'content_id': entity.content_id,
            'title': entity.title,
            'description': entity.description,
            'code': entity.code,
            'language': entity.language,
            'output': entity.output,
            'explanation': entity.explanation,
            'complexity': entity.complexity,
            'tags': entity.tags,
            'difficulty_level': entity.difficulty_level,
            'is_runnable': entity.is_runnable,
            'test_cases': entity.test_cases,
            'order': entity.order
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> CodeExample:
        """Deserialize dictionary to code example."""
        return CodeExample(
            id=data.get('id'),
            content_id=data.get('content_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            code=data.get('code', ''),
            language=data.get('language', 'python'),
            output=data.get('output'),
            explanation=data.get('explanation', ''),
            complexity=data.get('complexity', {"time": "O(1)", "space": "O(1)"}),
            tags=data.get('tags', []),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            is_runnable=data.get('is_runnable', False),
            test_cases=data.get('test_cases', []),
            order=data.get('order', 0)
        )
    
    def find_by_content(self, content_id: str) -> List[CodeExample]:
        """Find code examples by content ID."""
        examples = self.find_by_field('content_id', content_id)
        # Sort by order
        return sorted(examples, key=lambda e: e.order)
    
    def find_by_language(self, language: str) -> List[CodeExample]:
        """Find code examples by programming language."""
        return self.find_by_field('language', language)
    
    def find_runnable(self) -> List[CodeExample]:
        """Find runnable code examples."""
        return self.find_by_field('is_runnable', True)


class ExerciseRepository(BaseRepository[Exercise]):
    """Repository for exercise management."""
    
    def __init__(self, storage):
        super().__init__(storage, "exercise")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate exercise-specific fields."""
        required_fields = ['content_id', 'title', 'problem_statement']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Exercise {field} is required")
        
        # Validate difficulty level
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if entity_data.get('difficulty_level') not in valid_levels:
            raise ValidationError(f"Difficulty level must be one of: {valid_levels}")
        
        # Validate estimated time
        time_minutes = entity_data.get('estimated_time_minutes', 30)
        if not isinstance(time_minutes, int) or time_minutes <= 0:
            raise ValidationError("Estimated time must be a positive integer")
        
        # Validate acceptance rate
        rate = entity_data.get('acceptance_rate', 0.0)
        if not isinstance(rate, (int, float)) or rate < 0 or rate > 100:
            raise ValidationError("Acceptance rate must be between 0 and 100")
    
    def _serialize_entity(self, entity: Exercise) -> Dict[str, Any]:
        """Serialize exercise to dictionary."""
        return {
            'id': entity.id,
            'content_id': entity.content_id,
            'title': entity.title,
            'description': entity.description,
            'problem_statement': entity.problem_statement,
            'difficulty_level': entity.difficulty_level,
            'estimated_time_minutes': entity.estimated_time_minutes,
            'hints': entity.hints,
            'solution': entity.solution,
            'test_cases': entity.test_cases,
            'constraints': entity.constraints,
            'topics': entity.topics,
            'companies': entity.companies,
            'acceptance_rate': entity.acceptance_rate,
            'order': entity.order
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Exercise:
        """Deserialize dictionary to exercise."""
        return Exercise(
            id=data.get('id'),
            content_id=data.get('content_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            problem_statement=data.get('problem_statement', ''),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            estimated_time_minutes=data.get('estimated_time_minutes', 30),
            hints=data.get('hints', []),
            solution=data.get('solution', {}),
            test_cases=data.get('test_cases', []),
            constraints=data.get('constraints', []),
            topics=data.get('topics', []),
            companies=data.get('companies', []),
            acceptance_rate=data.get('acceptance_rate', 0.0),
            order=data.get('order', 0)
        )
    
    def find_by_content(self, content_id: str) -> List[Exercise]:
        """Find exercises by content ID."""
        exercises = self.find_by_field('content_id', content_id)
        # Sort by order
        return sorted(exercises, key=lambda e: e.order)
    
    def find_by_topics(self, topics: List[str]) -> List[Exercise]:
        """Find exercises by topics."""
        try:
            all_exercises = self.list_all()
            matching_exercises = []
            
            for exercise in all_exercises:
                if any(topic in exercise.topics for topic in topics):
                    matching_exercises.append(exercise)
            
            return matching_exercises
            
        except Exception as e:
            raise RepositoryError(f"Failed to find exercises by topics: {str(e)}")
    
    def find_by_companies(self, companies: List[str]) -> List[Exercise]:
        """Find exercises by companies."""
        try:
            all_exercises = self.list_all()
            matching_exercises = []
            
            for exercise in all_exercises:
                if any(company in exercise.companies for company in companies):
                    matching_exercises.append(exercise)
            
            return matching_exercises
            
        except Exception as e:
            raise RepositoryError(f"Failed to find exercises by companies: {str(e)}")
    
    def find_by_difficulty_range(self, min_acceptance_rate: float = 0.0, max_acceptance_rate: float = 100.0) -> List[Exercise]:
        """Find exercises by acceptance rate range."""
        try:
            all_exercises = self.list_all()
            matching_exercises = []
            
            for exercise in all_exercises:
                if min_acceptance_rate <= exercise.acceptance_rate <= max_acceptance_rate:
                    matching_exercises.append(exercise)
            
            return matching_exercises
            
        except Exception as e:
            raise RepositoryError(f"Failed to find exercises by acceptance rate: {str(e)}")