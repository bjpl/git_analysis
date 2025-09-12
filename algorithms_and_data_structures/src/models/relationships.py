"""
Model relationships and dependency documentation for the curriculum management system.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .user import User
from .content import Content
from .curriculum import Curriculum, Course, Module, Lesson
from .progress import Progress


class RelationshipType(Enum):
    """Types of relationships between models."""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"
    HIERARCHICAL = "hierarchical"
    DEPENDENCY = "dependency"


@dataclass
class ModelRelationship:
    """
    Defines a relationship between two models.
    """
    from_model: str
    to_model: str
    relationship_type: RelationshipType
    foreign_key_field: str
    description: str
    is_required: bool = True
    cascade_delete: bool = False


class ModelRelationshipManager:
    """
    Manages and documents all model relationships in the curriculum system.
    """
    
    def __init__(self):
        self.relationships = self._define_relationships()
    
    def _define_relationships(self) -> List[ModelRelationship]:
        """Define all model relationships in the system."""
        return [
            # User relationships
            ModelRelationship(
                from_model="User",
                to_model="Curriculum",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="courses_enrolled",
                description="Users can enroll in multiple curricula",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="User",
                to_model="Course",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="courses_enrolled",
                description="Users can enroll in multiple courses",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="User",
                to_model="Progress",
                relationship_type=RelationshipType.ONE_TO_MANY,
                foreign_key_field="user_id",
                description="Each user has multiple progress records",
                cascade_delete=True
            ),
            
            # Content relationships
            ModelRelationship(
                from_model="Content",
                to_model="User",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="author_id",
                description="Each content item has one author",
                is_required=True
            ),
            
            ModelRelationship(
                from_model="Content",
                to_model="User",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="reviewer_ids",
                description="Content can have multiple reviewers",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Content",
                to_model="Content",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="dependency_content_ids",
                description="Content can depend on other content",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Content",
                to_model="Content",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="related_content_ids",
                description="Content can be related to other content",
                is_required=False
            ),
            
            # Curriculum hierarchy relationships
            ModelRelationship(
                from_model="Curriculum",
                to_model="Course",
                relationship_type=RelationshipType.ONE_TO_MANY,
                foreign_key_field="course_ids",
                description="Curriculum contains multiple courses",
                cascade_delete=True
            ),
            
            ModelRelationship(
                from_model="Course",
                to_model="Module",
                relationship_type=RelationshipType.ONE_TO_MANY,
                foreign_key_field="module_ids",
                description="Course contains multiple modules",
                cascade_delete=True
            ),
            
            ModelRelationship(
                from_model="Module",
                to_model="Lesson",
                relationship_type=RelationshipType.ONE_TO_MANY,
                foreign_key_field="lesson_ids",
                description="Module contains multiple lessons",
                cascade_delete=True
            ),
            
            ModelRelationship(
                from_model="Lesson",
                to_model="Content",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="content_ids",
                description="Lesson can contain multiple content items",
                is_required=False
            ),
            
            # Course staff relationships
            ModelRelationship(
                from_model="Course",
                to_model="User",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="instructor_ids",
                description="Course can have multiple instructors",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Course",
                to_model="User",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="ta_ids",
                description="Course can have multiple teaching assistants",
                is_required=False
            ),
            
            # Curriculum staff relationships
            ModelRelationship(
                from_model="Curriculum",
                to_model="User",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="program_director_id",
                description="Each curriculum has one program director",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Curriculum",
                to_model="User",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="coordinator_ids",
                description="Curriculum can have multiple coordinators",
                is_required=False
            ),
            
            # Progress relationships
            ModelRelationship(
                from_model="Progress",
                to_model="User",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="user_id",
                description="Each progress record belongs to one user",
                is_required=True
            ),
            
            ModelRelationship(
                from_model="Progress",
                to_model="Curriculum",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="curriculum_id",
                description="Progress can be tracked at curriculum level",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Progress",
                to_model="Course",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="course_id",
                description="Progress can be tracked at course level",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Progress",
                to_model="Module",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="module_id",
                description="Progress can be tracked at module level",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Progress",
                to_model="Lesson",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="lesson_id",
                description="Progress can be tracked at lesson level",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Progress",
                to_model="Content",
                relationship_type=RelationshipType.MANY_TO_ONE,
                foreign_key_field="content_id",
                description="Progress can be tracked at content level",
                is_required=False
            ),
            
            # Prerequisite relationships
            ModelRelationship(
                from_model="Course",
                to_model="Content",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="prerequisites.required_content_ids",
                description="Course can have content prerequisites",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Module",
                to_model="Content",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="prerequisites.required_content_ids",
                description="Module can have content prerequisites",
                is_required=False
            ),
            
            ModelRelationship(
                from_model="Lesson",
                to_model="Content",
                relationship_type=RelationshipType.MANY_TO_MANY,
                foreign_key_field="prerequisites.required_content_ids",
                description="Lesson can have content prerequisites",
                is_required=False
            ),
        ]
    
    def get_relationships_for_model(self, model_name: str) -> List[ModelRelationship]:
        """Get all relationships for a specific model."""
        return [
            rel for rel in self.relationships 
            if rel.from_model == model_name or rel.to_model == model_name
        ]
    
    def get_dependent_models(self, model_name: str) -> List[str]:
        """Get models that depend on the given model."""
        dependents = []
        for rel in self.relationships:
            if rel.to_model == model_name and rel.cascade_delete:
                dependents.append(rel.from_model)
        return dependents
    
    def get_relationship_graph(self) -> Dict[str, Dict[str, List[str]]]:
        """Get a graph representation of all relationships."""
        graph = {}
        
        for rel in self.relationships:
            if rel.from_model not in graph:
                graph[rel.from_model] = {"outgoing": [], "incoming": []}
            if rel.to_model not in graph:
                graph[rel.to_model] = {"outgoing": [], "incoming": []}
            
            graph[rel.from_model]["outgoing"].append(rel.to_model)
            graph[rel.to_model]["incoming"].append(rel.from_model)
        
        return graph
    
    def validate_relationship_integrity(self) -> List[str]:
        """Validate the integrity of all relationships."""
        issues = []
        
        # Check for circular dependencies
        graph = self.get_relationship_graph()
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, {}).get("outgoing", []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    issues.append(f"Circular dependency detected involving {node}")
        
        return issues


# Global instance for easy access
relationship_manager = ModelRelationshipManager()


def get_model_relationships() -> Dict[str, Any]:
    """
    Get a comprehensive overview of all model relationships.
    
    Returns:
        Dictionary containing relationship information
    """
    return {
        "models": [
            {
                "name": "User",
                "description": "Learner profiles and authentication",
                "key_relationships": [
                    "Can enroll in multiple courses",
                    "Has multiple progress records",
                    "Can author content",
                    "Can be instructor or TA"
                ]
            },
            {
                "name": "Content",
                "description": "Educational materials and resources",
                "key_relationships": [
                    "Authored by one user",
                    "Can be reviewed by multiple users",
                    "Can depend on other content",
                    "Used in lessons"
                ]
            },
            {
                "name": "Curriculum",
                "description": "Top-level educational programs",
                "key_relationships": [
                    "Contains multiple courses",
                    "Has program director",
                    "Has coordinators",
                    "Tracked by progress records"
                ]
            },
            {
                "name": "Course",
                "description": "Subject-specific learning paths",
                "key_relationships": [
                    "Belongs to curriculum",
                    "Contains multiple modules",
                    "Has instructors and TAs",
                    "Students can enroll"
                ]
            },
            {
                "name": "Module",
                "description": "Thematic learning units",
                "key_relationships": [
                    "Belongs to course",
                    "Contains multiple lessons",
                    "Can have prerequisites",
                    "Tracked by progress"
                ]
            },
            {
                "name": "Lesson",
                "description": "Individual learning sessions",
                "key_relationships": [
                    "Belongs to module",
                    "Contains content items",
                    "Can have assessments",
                    "Tracked by progress"
                ]
            },
            {
                "name": "Progress",
                "description": "User learning progress and analytics",
                "key_relationships": [
                    "Belongs to one user",
                    "Tracks any curriculum level",
                    "Contains activity history",
                    "Calculates metrics"
                ]
            }
        ],
        "hierarchy": {
            "description": "Main curriculum hierarchy",
            "levels": [
                "Curriculum (top level)",
                "Course (subject areas)", 
                "Module (thematic units)",
                "Lesson (individual sessions)",
                "Content (learning materials)"
            ]
        },
        "key_patterns": [
            "Hierarchical structure for curriculum organization",
            "Many-to-many relationships for enrollment and staffing",
            "Prerequisite dependencies for learning paths",
            "Comprehensive progress tracking at all levels",
            "Content reusability across lessons",
            "User role-based access control"
        ],
        "data_integrity": {
            "cascade_deletes": [
                "Deleting curriculum removes courses",
                "Deleting course removes modules", 
                "Deleting module removes lessons",
                "Deleting user removes their progress"
            ],
            "required_relationships": [
                "Content must have author",
                "Progress must have user",
                "Course must belong to curriculum",
                "Module must belong to course",
                "Lesson must belong to module"
            ]
        }
    }


def validate_model_instance_relationships(instance: Any, 
                                        related_instances: Dict[str, List[Any]]) -> List[str]:
    """
    Validate that a model instance's relationships are satisfied.
    
    Args:
        instance: Model instance to validate
        related_instances: Dictionary of related model instances
        
    Returns:
        List of validation errors
    """
    errors = []
    model_name = instance.__class__.__name__
    
    # Get relationships for this model
    relationships = relationship_manager.get_relationships_for_model(model_name)
    
    for rel in relationships:
        if rel.from_model == model_name:
            # Check outgoing relationships
            if hasattr(instance, rel.foreign_key_field.split('.')[0]):
                field_value = getattr(instance, rel.foreign_key_field.split('.')[0])
                
                if rel.is_required and not field_value:
                    errors.append(f"{model_name}.{rel.foreign_key_field} is required but empty")
                
                # Validate referenced IDs exist
                if isinstance(field_value, list):
                    related_models = related_instances.get(rel.to_model, [])
                    related_ids = [m.id for m in related_models]
                    
                    for ref_id in field_value:
                        if ref_id not in related_ids:
                            errors.append(f"{model_name}.{rel.foreign_key_field} references non-existent {rel.to_model} ID: {ref_id}")
                
                elif isinstance(field_value, str) and field_value:
                    related_models = related_instances.get(rel.to_model, [])
                    related_ids = [m.id for m in related_models]
                    
                    if field_value not in related_ids:
                        errors.append(f"{model_name}.{rel.foreign_key_field} references non-existent {rel.to_model} ID: {field_value}")
    
    return errors