"""
Base model class with common functionality for all data models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar
import json
import uuid
from enum import Enum


T = TypeVar('T', bound='BaseModel')


class ValidationError(Exception):
    """Custom exception for model validation errors."""
    pass


@dataclass
class BaseModel(ABC):
    """
    Base model class with common functionality for all data models.
    
    Provides:
    - Unique ID generation
    - Creation and update timestamps
    - Validation framework
    - Serialization/deserialization
    - Search and filter capabilities
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation."""
        self.validate()
    
    @abstractmethod
    def validate(self) -> None:
        """
        Validate the model instance.
        
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            Model instance
        """
        # Convert ISO strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """
        Convert the model to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        Create a model instance from JSON string.
        
        Args:
            json_str: JSON string containing model data
            
        Returns:
            Model instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Update a metadata field.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.update_timestamp()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    @classmethod
    def search(cls: Type[T], 
              models: List[T], 
              query: str, 
              fields: Optional[List[str]] = None) -> List[T]:
        """
        Search models by query string.
        
        Args:
            models: List of model instances to search
            query: Search query
            fields: Fields to search in (default: all string fields)
            
        Returns:
            List of matching models
        """
        if not query:
            return models
        
        query_lower = query.lower()
        results = []
        
        for model in models:
            model_dict = model.to_dict()
            
            # If no fields specified, search all string fields
            if fields is None:
                search_fields = [k for k, v in model_dict.items() 
                               if isinstance(v, str)]
            else:
                search_fields = fields
            
            # Check if query matches any field
            for field_name in search_fields:
                field_value = model_dict.get(field_name, '')
                if isinstance(field_value, str) and query_lower in field_value.lower():
                    results.append(model)
                    break
        
        return results
    
    @classmethod
    def filter(cls: Type[T], 
              models: List[T], 
              filters: Dict[str, Any]) -> List[T]:
        """
        Filter models by criteria.
        
        Args:
            models: List of model instances to filter
            filters: Dictionary of field:value filters
            
        Returns:
            List of filtered models
        """
        if not filters:
            return models
        
        results = []
        for model in models:
            model_dict = model.to_dict()
            match = True
            
            for field, value in filters.items():
                model_value = model_dict.get(field)
                
                # Handle different filter types
                if isinstance(value, dict):
                    # Range filters: {'gt': 10, 'lt': 20}
                    if 'gt' in value and model_value <= value['gt']:
                        match = False
                        break
                    if 'gte' in value and model_value < value['gte']:
                        match = False
                        break
                    if 'lt' in value and model_value >= value['lt']:
                        match = False
                        break
                    if 'lte' in value and model_value > value['lte']:
                        match = False
                        break
                    if 'in' in value and model_value not in value['in']:
                        match = False
                        break
                else:
                    # Exact match
                    if model_value != value:
                        match = False
                        break
            
            if match:
                results.append(model)
        
        return results
    
    @classmethod
    def sort(cls: Type[T], 
            models: List[T], 
            key: str, 
            reverse: bool = False) -> List[T]:
        """
        Sort models by a field.
        
        Args:
            models: List of model instances to sort
            key: Field name to sort by
            reverse: Sort in descending order
            
        Returns:
            Sorted list of models
        """
        return sorted(models, 
                     key=lambda x: getattr(x, key, None), 
                     reverse=reverse)
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, BaseModel):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(id='{self.id}')"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"{self.__class__.__name__}(id='{self.id}', created_at='{self.created_at}')"