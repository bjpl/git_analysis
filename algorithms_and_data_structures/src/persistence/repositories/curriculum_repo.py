"""
Curriculum Repository

Repository for managing curriculum data including courses, modules, and lessons.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .base import BaseRepository
from ..exceptions import ValidationError


@dataclass
class Curriculum:
    """Curriculum entity representing a complete learning curriculum."""
    
    id: Optional[str] = None
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    difficulty_level: str = "beginner"  # beginner, intermediate, advanced
    estimated_duration_hours: int = 0
    prerequisites: List[str] = None
    learning_objectives: List[str] = None
    modules: List[Dict[str, Any]] = None
    tags: List[str] = None
    author: str = ""
    is_published: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.prerequisites is None:
            self.prerequisites = []
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.modules is None:
            self.modules = []
        if self.tags is None:
            self.tags = []


@dataclass
class Module:
    """Module entity representing a curriculum module."""
    
    id: Optional[str] = None
    curriculum_id: str = ""
    name: str = ""
    description: str = ""
    order: int = 0
    estimated_duration_hours: int = 0
    learning_objectives: List[str] = None
    lessons: List[Dict[str, Any]] = None
    assessments: List[Dict[str, Any]] = None
    prerequisites: List[str] = None
    is_required: bool = True
    
    def __post_init__(self):
        """Initialize default values."""
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.lessons is None:
            self.lessons = []
        if self.assessments is None:
            self.assessments = []
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass  
class Lesson:
    """Lesson entity representing a learning lesson."""
    
    id: Optional[str] = None
    module_id: str = ""
    curriculum_id: str = ""
    name: str = ""
    description: str = ""
    order: int = 0
    lesson_type: str = "lecture"  # lecture, exercise, project, quiz, assessment
    estimated_duration_minutes: int = 0
    content: Dict[str, Any] = None
    resources: List[Dict[str, Any]] = None
    learning_objectives: List[str] = None
    prerequisites: List[str] = None
    difficulty_level: str = "beginner"
    is_required: bool = True
    
    def __post_init__(self):
        """Initialize default values."""
        if self.content is None:
            self.content = {}
        if self.resources is None:
            self.resources = []
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.prerequisites is None:
            self.prerequisites = []


class CurriculumRepository(BaseRepository[Curriculum]):
    """Repository for curriculum management."""
    
    def __init__(self, storage):
        super().__init__(storage, "curriculum")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate curriculum-specific fields."""
        required_fields = ['name', 'description']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Curriculum {field} is required")
        
        # Validate difficulty level
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if entity_data.get('difficulty_level') not in valid_levels:
            raise ValidationError(f"Difficulty level must be one of: {valid_levels}")
        
        # Validate version format
        version = entity_data.get('version', '1.0.0')
        if not isinstance(version, str) or not version:
            raise ValidationError("Version must be a non-empty string")
        
        # Validate duration
        duration = entity_data.get('estimated_duration_hours', 0)
        if not isinstance(duration, int) or duration < 0:
            raise ValidationError("Estimated duration must be a non-negative integer")
    
    def _serialize_entity(self, entity: Curriculum) -> Dict[str, Any]:
        """Serialize curriculum to dictionary."""
        return {
            'id': entity.id,
            'name': entity.name,
            'description': entity.description,
            'version': entity.version,
            'difficulty_level': entity.difficulty_level,
            'estimated_duration_hours': entity.estimated_duration_hours,
            'prerequisites': entity.prerequisites,
            'learning_objectives': entity.learning_objectives,
            'modules': entity.modules,
            'tags': entity.tags,
            'author': entity.author,
            'is_published': entity.is_published,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Curriculum:
        """Deserialize dictionary to curriculum."""
        return Curriculum(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            estimated_duration_hours=data.get('estimated_duration_hours', 0),
            prerequisites=data.get('prerequisites', []),
            learning_objectives=data.get('learning_objectives', []),
            modules=data.get('modules', []),
            tags=data.get('tags', []),
            author=data.get('author', ''),
            is_published=data.get('is_published', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def find_by_difficulty(self, difficulty_level: str) -> List[Curriculum]:
        """Find curricula by difficulty level."""
        return self.find_by_field('difficulty_level', difficulty_level)
    
    def find_published(self) -> List[Curriculum]:
        """Find published curricula."""
        return self.find_by_field('is_published', True)
    
    def find_by_author(self, author: str) -> List[Curriculum]:
        """Find curricula by author."""
        return self.find_by_field('author', author)
    
    def find_by_tags(self, tags: List[str]) -> List[Curriculum]:
        """Find curricula that have any of the specified tags."""
        try:
            all_curricula = self.list_all()
            matching_curricula = []
            
            for curriculum in all_curricula:
                if any(tag in curriculum.tags for tag in tags):
                    matching_curricula.append(curriculum)
            
            return matching_curricula
            
        except Exception as e:
            raise RepositoryError(f"Failed to find curricula by tags: {str(e)}")
    
    def get_curriculum_stats(self, curriculum_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a curriculum."""
        curriculum = self.get(curriculum_id)
        if not curriculum:
            return None
        
        total_modules = len(curriculum.modules)
        total_lessons = sum(len(module.get('lessons', [])) for module in curriculum.modules)
        
        return {
            'curriculum_id': curriculum_id,
            'name': curriculum.name,
            'total_modules': total_modules,
            'total_lessons': total_lessons,
            'estimated_duration_hours': curriculum.estimated_duration_hours,
            'difficulty_level': curriculum.difficulty_level,
            'is_published': curriculum.is_published,
            'tags': curriculum.tags
        }
    
    def publish_curriculum(self, curriculum_id: str) -> bool:
        """Mark curriculum as published."""
        curriculum = self.get(curriculum_id)
        if not curriculum:
            return False
        
        curriculum.is_published = True
        return self.update(curriculum_id, curriculum)
    
    def unpublish_curriculum(self, curriculum_id: str) -> bool:
        """Mark curriculum as unpublished."""
        curriculum = self.get(curriculum_id)
        if not curriculum:
            return False
        
        curriculum.is_published = False
        return self.update(curriculum_id, curriculum)


class ModuleRepository(BaseRepository[Module]):
    """Repository for module management."""
    
    def __init__(self, storage):
        super().__init__(storage, "module")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate module-specific fields."""
        required_fields = ['curriculum_id', 'name', 'description']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Module {field} is required")
        
        # Validate order
        order = entity_data.get('order', 0)
        if not isinstance(order, int) or order < 0:
            raise ValidationError("Module order must be a non-negative integer")
    
    def _serialize_entity(self, entity: Module) -> Dict[str, Any]:
        """Serialize module to dictionary.""" 
        return {
            'id': entity.id,
            'curriculum_id': entity.curriculum_id,
            'name': entity.name,
            'description': entity.description,
            'order': entity.order,
            'estimated_duration_hours': entity.estimated_duration_hours,
            'learning_objectives': entity.learning_objectives,
            'lessons': entity.lessons,
            'assessments': entity.assessments,
            'prerequisites': entity.prerequisites,
            'is_required': entity.is_required
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Module:
        """Deserialize dictionary to module."""
        return Module(
            id=data.get('id'),
            curriculum_id=data.get('curriculum_id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            order=data.get('order', 0),
            estimated_duration_hours=data.get('estimated_duration_hours', 0),
            learning_objectives=data.get('learning_objectives', []),
            lessons=data.get('lessons', []),
            assessments=data.get('assessments', []),
            prerequisites=data.get('prerequisites', []),
            is_required=data.get('is_required', True)
        )
    
    def find_by_curriculum(self, curriculum_id: str) -> List[Module]:
        """Find modules by curriculum ID."""
        modules = self.find_by_field('curriculum_id', curriculum_id)
        # Sort by order
        return sorted(modules, key=lambda m: m.order)
    
    def find_required_modules(self, curriculum_id: str) -> List[Module]:
        """Find required modules for a curriculum."""
        modules = self.find_by_curriculum(curriculum_id)
        return [module for module in modules if module.is_required]


class LessonRepository(BaseRepository[Lesson]):
    """Repository for lesson management."""
    
    def __init__(self, storage):
        super().__init__(storage, "lesson")
        
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """Validate lesson-specific fields."""
        required_fields = ['module_id', 'curriculum_id', 'name']
        for field in required_fields:
            if not entity_data.get(field):
                raise ValidationError(f"Lesson {field} is required")
        
        # Validate lesson type
        valid_types = ['lecture', 'exercise', 'project', 'quiz', 'assessment']
        if entity_data.get('lesson_type') not in valid_types:
            raise ValidationError(f"Lesson type must be one of: {valid_types}")
        
        # Validate difficulty level
        valid_levels = ['beginner', 'intermediate', 'advanced']
        if entity_data.get('difficulty_level') not in valid_levels:
            raise ValidationError(f"Difficulty level must be one of: {valid_levels}")
    
    def _serialize_entity(self, entity: Lesson) -> Dict[str, Any]:
        """Serialize lesson to dictionary."""
        return {
            'id': entity.id,
            'module_id': entity.module_id,
            'curriculum_id': entity.curriculum_id,
            'name': entity.name,
            'description': entity.description,
            'order': entity.order,
            'lesson_type': entity.lesson_type,
            'estimated_duration_minutes': entity.estimated_duration_minutes,
            'content': entity.content,
            'resources': entity.resources,
            'learning_objectives': entity.learning_objectives,
            'prerequisites': entity.prerequisites,
            'difficulty_level': entity.difficulty_level,
            'is_required': entity.is_required
        }
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Lesson:
        """Deserialize dictionary to lesson."""
        return Lesson(
            id=data.get('id'),
            module_id=data.get('module_id', ''),
            curriculum_id=data.get('curriculum_id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            order=data.get('order', 0),
            lesson_type=data.get('lesson_type', 'lecture'),
            estimated_duration_minutes=data.get('estimated_duration_minutes', 0),
            content=data.get('content', {}),
            resources=data.get('resources', []),
            learning_objectives=data.get('learning_objectives', []),
            prerequisites=data.get('prerequisites', []),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            is_required=data.get('is_required', True)
        )
    
    def find_by_module(self, module_id: str) -> List[Lesson]:
        """Find lessons by module ID."""
        lessons = self.find_by_field('module_id', module_id)
        # Sort by order
        return sorted(lessons, key=lambda l: l.order)
    
    def find_by_curriculum(self, curriculum_id: str) -> List[Lesson]:
        """Find all lessons in a curriculum."""
        lessons = self.find_by_field('curriculum_id', curriculum_id)
        # Sort by order
        return sorted(lessons, key=lambda l: l.order)
    
    def find_by_type(self, lesson_type: str) -> List[Lesson]:
        """Find lessons by type."""
        return self.find_by_field('lesson_type', lesson_type)
    
    def find_required_lessons(self, module_id: str) -> List[Lesson]:
        """Find required lessons for a module."""
        lessons = self.find_by_module(module_id)
        return [lesson for lesson in lessons if lesson.is_required]