"""
Curriculum model with hierarchical structure for courses, modules, and lessons.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import re

from .base import BaseModel, ValidationError


class CurriculumLevel(Enum):
    """Curriculum hierarchy levels."""
    CURRICULUM = "curriculum"
    COURSE = "course"
    MODULE = "module"
    LESSON = "lesson"


class SequenceType(Enum):
    """Content sequence types."""
    LINEAR = "linear"  # Must complete in order
    FLEXIBLE = "flexible"  # Can complete in any order
    ADAPTIVE = "adaptive"  # Order adapts based on performance
    BRANCHING = "branching"  # Multiple paths available


class AssessmentType(Enum):
    """Assessment types."""
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    EXAM = "exam"
    PEER_REVIEW = "peer_review"
    SELF_ASSESSMENT = "self_assessment"
    PORTFOLIO = "portfolio"


@dataclass
class Prerequisites:
    """
    Prerequisites for curriculum content.
    """
    
    required_content_ids: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    minimum_score: float = 0.0  # Minimum score required in prerequisites
    grace_period_days: int = 0  # Days to complete prerequisites after starting
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'required_content_ids': self.required_content_ids,
            'required_skills': self.required_skills,
            'minimum_score': self.minimum_score,
            'grace_period_days': self.grace_period_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prerequisites':
        """Create from dictionary."""
        return cls(
            required_content_ids=data.get('required_content_ids', []),
            required_skills=data.get('required_skills', []),
            minimum_score=data.get('minimum_score', 0.0),
            grace_period_days=data.get('grace_period_days', 0)
        )


@dataclass
class AssessmentCriteria:
    """
    Assessment and grading criteria.
    """
    
    passing_score: float = 70.0  # Percentage required to pass
    max_attempts: int = 3  # Maximum attempts allowed
    time_limit_minutes: int = 0  # 0 means no time limit
    weighted_score: float = 1.0  # Weight in final grade calculation
    auto_grade: bool = True  # Whether assessment is auto-graded
    feedback_enabled: bool = True  # Whether feedback is provided
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'passing_score': self.passing_score,
            'max_attempts': self.max_attempts,
            'time_limit_minutes': self.time_limit_minutes,
            'weighted_score': self.weighted_score,
            'auto_grade': self.auto_grade,
            'feedback_enabled': self.feedback_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssessmentCriteria':
        """Create from dictionary."""
        return cls(
            passing_score=data.get('passing_score', 70.0),
            max_attempts=data.get('max_attempts', 3),
            time_limit_minutes=data.get('time_limit_minutes', 0),
            weighted_score=data.get('weighted_score', 1.0),
            auto_grade=data.get('auto_grade', True),
            feedback_enabled=data.get('feedback_enabled', True)
        )


@dataclass
class Lesson(BaseModel):
    """
    Individual lesson within a module.
    """
    
    title: str = ""
    description: str = ""
    learning_objectives: List[str] = field(default_factory=list)
    
    # Content
    content_ids: List[str] = field(default_factory=list)  # Content items in this lesson
    estimated_duration_minutes: int = 30
    
    # Structure
    module_id: str = ""  # Parent module
    order_index: int = 0  # Position within module
    
    # Prerequisites and dependencies
    prerequisites: Prerequisites = field(default_factory=Prerequisites)
    
    # Assessment
    has_assessment: bool = False
    assessment_type: AssessmentType = AssessmentType.QUIZ
    assessment_criteria: AssessmentCriteria = field(default_factory=AssessmentCriteria)
    
    # Settings
    is_optional: bool = False
    is_visible: bool = True
    
    def validate(self) -> None:
        """Validate the lesson model."""
        if not self.title.strip():
            raise ValidationError("Lesson title is required")
        
        if len(self.title) > 200:
            raise ValidationError("Lesson title must be 200 characters or less")
        
        if not self.module_id:
            raise ValidationError("Module ID is required")
        
        if self.order_index < 0:
            raise ValidationError("Order index cannot be negative")
        
        if self.estimated_duration_minutes < 0:
            raise ValidationError("Duration cannot be negative")
        
        if not isinstance(self.assessment_type, AssessmentType):
            raise ValidationError("Invalid assessment type")
    
    def add_content(self, content_id: str) -> None:
        """Add content to the lesson."""
        if content_id not in self.content_ids:
            self.content_ids.append(content_id)
            self.update_timestamp()
    
    def remove_content(self, content_id: str) -> None:
        """Remove content from the lesson."""
        if content_id in self.content_ids:
            self.content_ids.remove(content_id)
            self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data['prerequisites'] = self.prerequisites.to_dict()
        data['assessment_type'] = self.assessment_type.value
        data['assessment_criteria'] = self.assessment_criteria.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lesson':
        """Create from dictionary."""
        # Extract nested objects
        prerequisites_data = data.pop('prerequisites', {})
        assessment_criteria_data = data.pop('assessment_criteria', {})
        
        # Handle enum
        if 'assessment_type' in data:
            data['assessment_type'] = AssessmentType(data['assessment_type'])
        
        # Create lesson
        lesson = super().from_dict(data)
        
        # Set nested objects
        lesson.prerequisites = Prerequisites.from_dict(prerequisites_data)
        lesson.assessment_criteria = AssessmentCriteria.from_dict(assessment_criteria_data)
        
        return lesson


@dataclass
class Module(BaseModel):
    """
    Module containing multiple lessons within a course.
    """
    
    title: str = ""
    description: str = ""
    learning_objectives: List[str] = field(default_factory=list)
    
    # Structure
    course_id: str = ""  # Parent course
    lesson_ids: List[str] = field(default_factory=list)  # Ordered list of lessons
    order_index: int = 0  # Position within course
    
    # Sequencing
    sequence_type: SequenceType = SequenceType.LINEAR
    
    # Prerequisites
    prerequisites: Prerequisites = field(default_factory=Prerequisites)
    
    # Timing
    estimated_duration_minutes: int = 0  # Auto-calculated from lessons
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Assessment
    has_final_assessment: bool = False
    assessment_type: AssessmentType = AssessmentType.ASSIGNMENT
    assessment_criteria: AssessmentCriteria = field(default_factory=AssessmentCriteria)
    
    # Settings
    is_optional: bool = False
    is_visible: bool = True
    
    def validate(self) -> None:
        """Validate the module model."""
        if not self.title.strip():
            raise ValidationError("Module title is required")
        
        if len(self.title) > 200:
            raise ValidationError("Module title must be 200 characters or less")
        
        if not self.course_id:
            raise ValidationError("Course ID is required")
        
        if self.order_index < 0:
            raise ValidationError("Order index cannot be negative")
        
        if not isinstance(self.sequence_type, SequenceType):
            raise ValidationError("Invalid sequence type")
        
        if not isinstance(self.assessment_type, AssessmentType):
            raise ValidationError("Invalid assessment type")
        
        # Date validation
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date")
    
    def add_lesson(self, lesson_id: str, position: Optional[int] = None) -> None:
        """Add a lesson to the module."""
        if lesson_id not in self.lesson_ids:
            if position is None:
                self.lesson_ids.append(lesson_id)
            else:
                self.lesson_ids.insert(position, lesson_id)
            self.update_timestamp()
    
    def remove_lesson(self, lesson_id: str) -> None:
        """Remove a lesson from the module."""
        if lesson_id in self.lesson_ids:
            self.lesson_ids.remove(lesson_id)
            self.update_timestamp()
    
    def reorder_lesson(self, lesson_id: str, new_position: int) -> None:
        """Reorder a lesson within the module."""
        if lesson_id in self.lesson_ids:
            self.lesson_ids.remove(lesson_id)
            self.lesson_ids.insert(new_position, lesson_id)
            self.update_timestamp()
    
    def get_lesson_count(self) -> int:
        """Get the number of lessons in the module."""
        return len(self.lesson_ids)
    
    def calculate_estimated_duration(self, lessons: List[Lesson]) -> int:
        """
        Calculate estimated duration from lessons.
        
        Args:
            lessons: List of lesson objects
            
        Returns:
            Total estimated duration in minutes
        """
        lesson_dict = {lesson.id: lesson for lesson in lessons}
        total_minutes = 0
        
        for lesson_id in self.lesson_ids:
            if lesson_id in lesson_dict:
                total_minutes += lesson_dict[lesson_id].estimated_duration_minutes
        
        self.estimated_duration_minutes = total_minutes
        return total_minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data['sequence_type'] = self.sequence_type.value
        data['prerequisites'] = self.prerequisites.to_dict()
        data['assessment_type'] = self.assessment_type.value
        data['assessment_criteria'] = self.assessment_criteria.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Module':
        """Create from dictionary."""
        # Extract nested objects
        prerequisites_data = data.pop('prerequisites', {})
        assessment_criteria_data = data.pop('assessment_criteria', {})
        
        # Handle enums
        if 'sequence_type' in data:
            data['sequence_type'] = SequenceType(data['sequence_type'])
        if 'assessment_type' in data:
            data['assessment_type'] = AssessmentType(data['assessment_type'])
        
        # Create module
        module = super().from_dict(data)
        
        # Set nested objects
        module.prerequisites = Prerequisites.from_dict(prerequisites_data)
        module.assessment_criteria = AssessmentCriteria.from_dict(assessment_criteria_data)
        
        return module


@dataclass
class Course(BaseModel):
    """
    Course containing multiple modules within a curriculum.
    """
    
    title: str = ""
    description: str = ""
    short_description: str = ""
    learning_objectives: List[str] = field(default_factory=list)
    
    # Structure
    curriculum_id: str = ""  # Parent curriculum
    module_ids: List[str] = field(default_factory=list)  # Ordered list of modules
    order_index: int = 0  # Position within curriculum
    
    # Course details
    course_code: str = ""  # e.g., "CS101"
    credits: int = 3
    difficulty_level: str = "beginner"
    category: str = ""
    subject: str = ""
    
    # Instructors and staff
    instructor_ids: List[str] = field(default_factory=list)
    ta_ids: List[str] = field(default_factory=list)  # Teaching assistants
    
    # Sequencing
    sequence_type: SequenceType = SequenceType.LINEAR
    
    # Prerequisites
    prerequisites: Prerequisites = field(default_factory=Prerequisites)
    
    # Timing
    estimated_duration_hours: int = 0  # Auto-calculated from modules
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    enrollment_start: Optional[datetime] = None
    enrollment_end: Optional[datetime] = None
    
    # Capacity
    max_enrollment: int = 0  # 0 means unlimited
    current_enrollment: int = 0
    waitlist_enabled: bool = True
    
    # Assessment
    has_final_exam: bool = False
    final_exam_weight: float = 0.0  # Percentage of final grade
    passing_grade: float = 70.0
    
    # Settings
    is_public: bool = True
    is_active: bool = True
    requires_approval: bool = False
    certification_available: bool = False
    
    # Pricing
    is_free: bool = True
    price: float = 0.0
    currency: str = "USD"
    
    def validate(self) -> None:
        """Validate the course model."""
        if not self.title.strip():
            raise ValidationError("Course title is required")
        
        if len(self.title) > 200:
            raise ValidationError("Course title must be 200 characters or less")
        
        if not self.curriculum_id:
            raise ValidationError("Curriculum ID is required")
        
        if self.order_index < 0:
            raise ValidationError("Order index cannot be negative")
        
        if self.credits < 0:
            raise ValidationError("Credits cannot be negative")
        
        if self.max_enrollment < 0:
            raise ValidationError("Max enrollment cannot be negative")
        
        if self.current_enrollment < 0:
            raise ValidationError("Current enrollment cannot be negative")
        
        if self.max_enrollment > 0 and self.current_enrollment > self.max_enrollment:
            raise ValidationError("Current enrollment cannot exceed max enrollment")
        
        if not isinstance(self.sequence_type, SequenceType):
            raise ValidationError("Invalid sequence type")
        
        if not 0.0 <= self.passing_grade <= 100.0:
            raise ValidationError("Passing grade must be between 0 and 100")
        
        if not 0.0 <= self.final_exam_weight <= 100.0:
            raise ValidationError("Final exam weight must be between 0 and 100")
        
        if self.price < 0:
            raise ValidationError("Price cannot be negative")
        
        # Date validation
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("Start date must be before end date")
        
        if (self.enrollment_start and self.enrollment_end and 
            self.enrollment_start >= self.enrollment_end):
            raise ValidationError("Enrollment start must be before enrollment end")
        
        # Course code validation
        if self.course_code and not re.match(r'^[A-Z]{2,4}\d{3,4}$', self.course_code):
            raise ValidationError("Course code must be in format like 'CS101' or 'MATH1234'")
    
    def add_module(self, module_id: str, position: Optional[int] = None) -> None:
        """Add a module to the course."""
        if module_id not in self.module_ids:
            if position is None:
                self.module_ids.append(module_id)
            else:
                self.module_ids.insert(position, module_id)
            self.update_timestamp()
    
    def remove_module(self, module_id: str) -> None:
        """Remove a module from the course."""
        if module_id in self.module_ids:
            self.module_ids.remove(module_id)
            self.update_timestamp()
    
    def reorder_module(self, module_id: str, new_position: int) -> None:
        """Reorder a module within the course."""
        if module_id in self.module_ids:
            self.module_ids.remove(module_id)
            self.module_ids.insert(new_position, module_id)
            self.update_timestamp()
    
    def add_instructor(self, instructor_id: str) -> None:
        """Add an instructor to the course."""
        if instructor_id not in self.instructor_ids:
            self.instructor_ids.append(instructor_id)
            self.update_timestamp()
    
    def add_ta(self, ta_id: str) -> None:
        """Add a teaching assistant to the course."""
        if ta_id not in self.ta_ids:
            self.ta_ids.append(ta_id)
            self.update_timestamp()
    
    def enroll_student(self) -> bool:
        """
        Enroll a student in the course.
        
        Returns:
            True if enrollment successful, False if full
        """
        if self.max_enrollment == 0 or self.current_enrollment < self.max_enrollment:
            self.current_enrollment += 1
            self.update_timestamp()
            return True
        return False
    
    def unenroll_student(self) -> None:
        """Unenroll a student from the course."""
        if self.current_enrollment > 0:
            self.current_enrollment -= 1
            self.update_timestamp()
    
    def get_enrollment_status(self) -> str:
        """Get enrollment status."""
        if not self.is_active:
            return "inactive"
        
        if self.max_enrollment == 0:
            return "open"
        
        if self.current_enrollment < self.max_enrollment:
            return "open"
        elif self.waitlist_enabled:
            return "waitlist"
        else:
            return "full"
    
    def is_enrollment_open(self) -> bool:
        """Check if enrollment is currently open."""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.enrollment_start and now < self.enrollment_start:
            return False
        
        if self.enrollment_end and now > self.enrollment_end:
            return False
        
        return True
    
    def calculate_estimated_duration(self, modules: List[Module]) -> int:
        """
        Calculate estimated duration from modules.
        
        Args:
            modules: List of module objects
            
        Returns:
            Total estimated duration in hours
        """
        module_dict = {module.id: module for module in modules}
        total_minutes = 0
        
        for module_id in self.module_ids:
            if module_id in module_dict:
                total_minutes += module_dict[module_id].estimated_duration_minutes
        
        self.estimated_duration_hours = total_minutes // 60
        return self.estimated_duration_hours
    
    def get_module_count(self) -> int:
        """Get the number of modules in the course."""
        return len(self.module_ids)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data['sequence_type'] = self.sequence_type.value
        data['prerequisites'] = self.prerequisites.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Course':
        """Create from dictionary."""
        # Extract nested objects
        prerequisites_data = data.pop('prerequisites', {})
        
        # Handle enum
        if 'sequence_type' in data:
            data['sequence_type'] = SequenceType(data['sequence_type'])
        
        # Create course
        course = super().from_dict(data)
        
        # Set nested objects
        course.prerequisites = Prerequisites.from_dict(prerequisites_data)
        
        return course


@dataclass
class Curriculum(BaseModel):
    """
    Top-level curriculum containing multiple courses.
    
    Represents a complete curriculum structure with hierarchical
    organization of courses, modules, and lessons.
    """
    
    title: str = ""
    description: str = ""
    short_description: str = ""
    learning_objectives: List[str] = field(default_factory=list)
    
    # Structure
    course_ids: List[str] = field(default_factory=list)  # Ordered list of courses
    
    # Curriculum details
    curriculum_code: str = ""  # e.g., "CS-BACHELOR"
    version: str = "1.0.0"
    academic_level: str = ""  # e.g., "undergraduate", "graduate"
    field_of_study: str = ""
    
    # Institutions and accreditation
    institution_id: str = ""
    department: str = ""
    accreditation_body: str = ""
    accreditation_status: str = ""
    
    # Personnel
    program_director_id: str = ""
    coordinator_ids: List[str] = field(default_factory=list)
    
    # Sequencing
    sequence_type: SequenceType = SequenceType.FLEXIBLE
    
    # Requirements
    total_credits_required: int = 120
    core_credits_required: int = 60
    elective_credits_required: int = 60
    prerequisites: Prerequisites = field(default_factory=Prerequisites)
    
    # Timing
    duration_years: int = 4
    duration_semesters: int = 8
    estimated_hours_per_week: int = 40
    
    # Validity
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    is_published: bool = False
    approval_status: str = "draft"  # draft, review, approved, deprecated
    
    # Analytics
    total_enrollments: int = 0
    completion_rate: float = 0.0
    average_completion_time_months: int = 0
    
    def validate(self) -> None:
        """Validate the curriculum model."""
        if not self.title.strip():
            raise ValidationError("Curriculum title is required")
        
        if len(self.title) > 300:
            raise ValidationError("Curriculum title must be 300 characters or less")
        
        if self.total_credits_required <= 0:
            raise ValidationError("Total credits must be positive")
        
        if self.core_credits_required < 0:
            raise ValidationError("Core credits cannot be negative")
        
        if self.elective_credits_required < 0:
            raise ValidationError("Elective credits cannot be negative")
        
        if (self.core_credits_required + self.elective_credits_required > 
            self.total_credits_required):
            raise ValidationError("Core + elective credits cannot exceed total credits")
        
        if self.duration_years <= 0:
            raise ValidationError("Duration years must be positive")
        
        if self.duration_semesters <= 0:
            raise ValidationError("Duration semesters must be positive")
        
        if not isinstance(self.sequence_type, SequenceType):
            raise ValidationError("Invalid sequence type")
        
        if not 0.0 <= self.completion_rate <= 1.0:
            raise ValidationError("Completion rate must be between 0.0 and 1.0")
        
        # Version validation
        if not re.match(r'^\d+\.\d+\.\d+$', self.version):
            raise ValidationError("Version must be in format 'x.y.z'")
        
        # Date validation
        if (self.effective_date and self.expiry_date and 
            self.effective_date >= self.expiry_date):
            raise ValidationError("Effective date must be before expiry date")
    
    def add_course(self, course_id: str, position: Optional[int] = None) -> None:
        """Add a course to the curriculum."""
        if course_id not in self.course_ids:
            if position is None:
                self.course_ids.append(course_id)
            else:
                self.course_ids.insert(position, course_id)
            self.update_timestamp()
    
    def remove_course(self, course_id: str) -> None:
        """Remove a course from the curriculum."""
        if course_id in self.course_ids:
            self.course_ids.remove(course_id)
            self.update_timestamp()
    
    def reorder_course(self, course_id: str, new_position: int) -> None:
        """Reorder a course within the curriculum."""
        if course_id in self.course_ids:
            self.course_ids.remove(course_id)
            self.course_ids.insert(new_position, course_id)
            self.update_timestamp()
    
    def add_coordinator(self, coordinator_id: str) -> None:
        """Add a coordinator to the curriculum."""
        if coordinator_id not in self.coordinator_ids:
            self.coordinator_ids.append(coordinator_id)
            self.update_timestamp()
    
    def publish(self, approver_id: str) -> None:
        """Publish the curriculum."""
        self.is_published = True
        self.approval_status = "approved"
        self.effective_date = datetime.utcnow()
        self.update_metadata("approved_by", approver_id)
        self.update_timestamp()
    
    def deprecate(self, reason: str = "") -> None:
        """Deprecate the curriculum."""
        self.is_active = False
        self.approval_status = "deprecated"
        self.expiry_date = datetime.utcnow()
        if reason:
            self.update_metadata("deprecation_reason", reason)
        self.update_timestamp()
    
    def increment_version(self, version_type: str = 'minor') -> None:
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
    
    def calculate_total_credits(self, courses: List[Course]) -> int:
        """
        Calculate total credits from courses.
        
        Args:
            courses: List of course objects
            
        Returns:
            Total credits
        """
        course_dict = {course.id: course for course in courses}
        total_credits = 0
        
        for course_id in self.course_ids:
            if course_id in course_dict:
                total_credits += course_dict[course_id].credits
        
        return total_credits
    
    def get_course_count(self) -> int:
        """Get the number of courses in the curriculum."""
        return len(self.course_ids)
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get curriculum progress summary."""
        return {
            'total_enrollments': self.total_enrollments,
            'completion_rate': self.completion_rate,
            'average_completion_time_months': self.average_completion_time_months,
            'total_courses': self.get_course_count(),
            'total_credits_required': self.total_credits_required
        }
    
    def is_current(self) -> bool:
        """Check if curriculum is currently valid."""
        now = datetime.utcnow()
        
        if not self.is_active or not self.is_published:
            return False
        
        if self.effective_date and now < self.effective_date:
            return False
        
        if self.expiry_date and now > self.expiry_date:
            return False
        
        return True
    
    @classmethod
    def search_by_field(cls, 
                       curricula: List['Curriculum'], 
                       field_of_study: str) -> List['Curriculum']:
        """
        Search curricula by field of study.
        
        Args:
            curricula: List of curriculum to search
            field_of_study: Field to search for
            
        Returns:
            List of matching curricula
        """
        field_lower = field_of_study.lower()
        return [c for c in curricula 
                if field_lower in c.field_of_study.lower()]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data['sequence_type'] = self.sequence_type.value
        data['prerequisites'] = self.prerequisites.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Curriculum':
        """Create from dictionary."""
        # Extract nested objects
        prerequisites_data = data.pop('prerequisites', {})
        
        # Handle enum
        if 'sequence_type' in data:
            data['sequence_type'] = SequenceType(data['sequence_type'])
        
        # Create curriculum
        curriculum = super().from_dict(data)
        
        # Set nested objects
        curriculum.prerequisites = Prerequisites.from_dict(prerequisites_data)
        
        return curriculum
    
    def __str__(self) -> str:
        """String representation."""
        return f"Curriculum(title='{self.title}', code='{self.curriculum_code}', version='{self.version}')"