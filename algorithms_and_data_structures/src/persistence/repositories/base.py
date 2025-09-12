"""
Base Repository Pattern Implementation

Provides common repository functionality and abstract base class.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic, Union
from datetime import datetime
import uuid

from ..storage_backend import StorageBackend
from ..exceptions import RepositoryError, ValidationError


T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository class implementing common CRUD operations.
    """
    
    def __init__(self, storage: StorageBackend, entity_name: str):
        """
        Initialize repository.
        
        Args:
            storage: Storage backend instance
            entity_name: Name of the entity type (used for key prefixing)
        """
        self.storage = storage
        self.entity_name = entity_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._key_prefix = f"{entity_name}:"
        
    def _make_key(self, entity_id: str) -> str:
        """Create storage key for entity ID."""
        return f"{self._key_prefix}{entity_id}"
    
    def _extract_id(self, key: str) -> str:
        """Extract entity ID from storage key."""
        return key[len(self._key_prefix):]
    
    def _generate_id(self) -> str:
        """Generate unique ID for new entity."""
        return str(uuid.uuid4())
    
    def _validate_entity(self, entity_data: Dict[str, Any]) -> None:
        """
        Validate entity data before storage.
        
        Args:
            entity_data: Entity data dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(entity_data, dict):
            raise ValidationError(f"Entity data must be a dictionary, got {type(entity_data)}")
        
        # Subclasses should override for specific validation
        self._validate_entity_fields(entity_data)
    
    @abstractmethod
    def _validate_entity_fields(self, entity_data: Dict[str, Any]) -> None:
        """
        Validate specific entity fields.
        
        Args:
            entity_data: Entity data dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    def _serialize_entity(self, entity: T) -> Dict[str, Any]:
        """
        Serialize entity object to dictionary.
        
        Args:
            entity: Entity object
            
        Returns:
            Dictionary representation
        """
        pass
    
    @abstractmethod
    def _deserialize_entity(self, data: Dict[str, Any]) -> T:
        """
        Deserialize dictionary to entity object.
        
        Args:
            data: Dictionary data
            
        Returns:
            Entity object
        """
        pass
    
    def create(self, entity: T) -> str:
        """
        Create new entity.
        
        Args:
            entity: Entity object to create
            
        Returns:
            ID of created entity
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            # Serialize entity
            entity_data = self._serialize_entity(entity)
            
            # Generate ID if not present
            entity_id = entity_data.get('id')
            if not entity_id:
                entity_id = self._generate_id()
                entity_data['id'] = entity_id
            
            # Add metadata
            now = datetime.now().isoformat()
            entity_data.update({
                'created_at': entity_data.get('created_at', now),
                'updated_at': now,
                'version': entity_data.get('version', 1)
            })
            
            # Validate
            self._validate_entity(entity_data)
            
            # Check if already exists
            key = self._make_key(entity_id)
            if self.storage.exists(key):
                raise RepositoryError(f"{self.entity_name} with ID {entity_id} already exists")
            
            # Store
            self.storage.set(key, entity_data)
            
            self.logger.info(f"Created {self.entity_name}: {entity_id}")
            return entity_id
            
        except Exception as e:
            if isinstance(e, (ValidationError, RepositoryError)):
                raise
            raise RepositoryError(f"Failed to create {self.entity_name}: {str(e)}")
    
    def get(self, entity_id: str) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity object or None if not found
            
        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            key = self._make_key(entity_id)
            data = self.storage.get(key)
            
            if data is None:
                return None
            
            return self._deserialize_entity(data)
            
        except Exception as e:
            raise RepositoryError(f"Failed to get {self.entity_name} {entity_id}: {str(e)}")
    
    def update(self, entity_id: str, entity: T) -> bool:
        """
        Update existing entity.
        
        Args:
            entity_id: Entity ID
            entity: Updated entity object
            
        Returns:
            True if entity was updated, False if not found
            
        Raises:
            RepositoryError: If update fails
        """
        try:
            key = self._make_key(entity_id)
            
            # Check if exists
            existing_data = self.storage.get(key)
            if existing_data is None:
                return False
            
            # Serialize updated entity
            entity_data = self._serialize_entity(entity)
            entity_data['id'] = entity_id
            
            # Update metadata
            entity_data.update({
                'created_at': existing_data.get('created_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
                'version': existing_data.get('version', 1) + 1
            })
            
            # Validate
            self._validate_entity(entity_data)
            
            # Store
            self.storage.set(key, entity_data)
            
            self.logger.info(f"Updated {self.entity_name}: {entity_id}")
            return True
            
        except Exception as e:
            if isinstance(e, (ValidationError, RepositoryError)):
                raise
            raise RepositoryError(f"Failed to update {self.entity_name} {entity_id}: {str(e)}")
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if entity was deleted, False if not found
            
        Raises:
            RepositoryError: If deletion fails
        """
        try:
            key = self._make_key(entity_id)
            deleted = self.storage.delete(key)
            
            if deleted:
                self.logger.info(f"Deleted {self.entity_name}: {entity_id}")
            
            return deleted
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete {self.entity_name} {entity_id}: {str(e)}")
    
    def exists(self, entity_id: str) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if entity exists
            
        Raises:
            RepositoryError: If check fails
        """
        try:
            key = self._make_key(entity_id)
            return self.storage.exists(key)
            
        except Exception as e:
            raise RepositoryError(f"Failed to check existence of {self.entity_name} {entity_id}: {str(e)}")
    
    def list_all(self) -> List[T]:
        """
        List all entities.
        
        Returns:
            List of all entity objects
            
        Raises:
            RepositoryError: If listing fails
        """
        try:
            keys = self.storage.list_keys(self._key_prefix)
            entities = []
            
            for key in keys:
                data = self.storage.get(key)
                if data:
                    try:
                        entity = self._deserialize_entity(data)
                        entities.append(entity)
                    except Exception as e:
                        self.logger.warning(f"Failed to deserialize entity from key {key}: {str(e)}")
                        continue
            
            return entities
            
        except Exception as e:
            raise RepositoryError(f"Failed to list {self.entity_name} entities: {str(e)}")
    
    def list_ids(self) -> List[str]:
        """
        List all entity IDs.
        
        Returns:
            List of entity IDs
            
        Raises:
            RepositoryError: If listing fails
        """
        try:
            keys = self.storage.list_keys(self._key_prefix)
            return [self._extract_id(key) for key in keys]
            
        except Exception as e:
            raise RepositoryError(f"Failed to list {self.entity_name} IDs: {str(e)}")
    
    def count(self) -> int:
        """
        Count total entities.
        
        Returns:
            Number of entities
            
        Raises:
            RepositoryError: If count fails
        """
        try:
            keys = self.storage.list_keys(self._key_prefix)
            return len(keys)
            
        except Exception as e:
            raise RepositoryError(f"Failed to count {self.entity_name} entities: {str(e)}")
    
    def clear_all(self) -> int:
        """
        Delete all entities.
        
        Returns:
            Number of entities deleted
            
        Raises:
            RepositoryError: If clearing fails
        """
        try:
            keys = self.storage.list_keys(self._key_prefix)
            deleted_count = 0
            
            for key in keys:
                if self.storage.delete(key):
                    deleted_count += 1
            
            self.logger.info(f"Cleared {deleted_count} {self.entity_name} entities")
            return deleted_count
            
        except Exception as e:
            raise RepositoryError(f"Failed to clear {self.entity_name} entities: {str(e)}")
    
    def batch_create(self, entities: List[T]) -> List[str]:
        """
        Create multiple entities in batch.
        
        Args:
            entities: List of entity objects
            
        Returns:
            List of created entity IDs
            
        Raises:
            RepositoryError: If batch creation fails
        """
        try:
            entity_ids = []
            batch_data = {}
            
            for entity in entities:
                # Serialize entity
                entity_data = self._serialize_entity(entity)
                
                # Generate ID if not present
                entity_id = entity_data.get('id')
                if not entity_id:
                    entity_id = self._generate_id()
                    entity_data['id'] = entity_id
                
                # Add metadata
                now = datetime.now().isoformat()
                entity_data.update({
                    'created_at': entity_data.get('created_at', now),
                    'updated_at': now,
                    'version': entity_data.get('version', 1)
                })
                
                # Validate
                self._validate_entity(entity_data)
                
                # Check if already exists
                key = self._make_key(entity_id)
                if self.storage.exists(key):
                    raise RepositoryError(f"{self.entity_name} with ID {entity_id} already exists")
                
                batch_data[key] = entity_data
                entity_ids.append(entity_id)
            
            # Batch storage operation
            self.storage.batch_set(batch_data)
            
            self.logger.info(f"Batch created {len(entity_ids)} {self.entity_name} entities")
            return entity_ids
            
        except Exception as e:
            if isinstance(e, (ValidationError, RepositoryError)):
                raise
            raise RepositoryError(f"Failed to batch create {self.entity_name} entities: {str(e)}")
    
    def batch_get(self, entity_ids: List[str]) -> Dict[str, Optional[T]]:
        """
        Get multiple entities by IDs.
        
        Args:
            entity_ids: List of entity IDs
            
        Returns:
            Dictionary mapping IDs to entity objects (None if not found)
            
        Raises:
            RepositoryError: If batch retrieval fails
        """
        try:
            keys = [self._make_key(entity_id) for entity_id in entity_ids]
            data_map = self.storage.batch_get(keys)
            
            result = {}
            for entity_id, key in zip(entity_ids, keys):
                data = data_map.get(key)
                if data:
                    try:
                        result[entity_id] = self._deserialize_entity(data)
                    except Exception as e:
                        self.logger.warning(f"Failed to deserialize {self.entity_name} {entity_id}: {str(e)}")
                        result[entity_id] = None
                else:
                    result[entity_id] = None
            
            return result
            
        except Exception as e:
            raise RepositoryError(f"Failed to batch get {self.entity_name} entities: {str(e)}")
    
    def batch_delete(self, entity_ids: List[str]) -> Dict[str, bool]:
        """
        Delete multiple entities by IDs.
        
        Args:
            entity_ids: List of entity IDs
            
        Returns:
            Dictionary mapping IDs to deletion success status
            
        Raises:
            RepositoryError: If batch deletion fails
        """
        try:
            keys = [self._make_key(entity_id) for entity_id in entity_ids]
            deletion_results = self.storage.batch_delete(keys)
            
            result = {}
            for entity_id, key in zip(entity_ids, keys):
                result[entity_id] = deletion_results.get(key, False)
            
            deleted_count = sum(1 for success in result.values() if success)
            self.logger.info(f"Batch deleted {deleted_count}/{len(entity_ids)} {self.entity_name} entities")
            
            return result
            
        except Exception as e:
            raise RepositoryError(f"Failed to batch delete {self.entity_name} entities: {str(e)}")
    
    def find_by_field(self, field_name: str, field_value: Any) -> List[T]:
        """
        Find entities by field value.
        
        Args:
            field_name: Field name to search
            field_value: Field value to match
            
        Returns:
            List of matching entities
            
        Raises:
            RepositoryError: If search fails
        """
        try:
            all_entities = self.list_all()
            matching_entities = []
            
            for entity in all_entities:
                entity_data = self._serialize_entity(entity)
                if entity_data.get(field_name) == field_value:
                    matching_entities.append(entity)
            
            return matching_entities
            
        except Exception as e:
            raise RepositoryError(f"Failed to find {self.entity_name} by {field_name}: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get repository statistics.
        
        Returns:
            Dictionary with repository statistics
        """
        try:
            return {
                'entity_type': self.entity_name,
                'total_count': self.count(),
                'storage_backend': type(self.storage).__name__,
                'key_prefix': self._key_prefix
            }
        except Exception as e:
            return {
                'entity_type': self.entity_name,
                'error': str(e)
            }