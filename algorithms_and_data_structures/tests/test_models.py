"""Test suite for Data Models - Validation, serialization, and model functionality."""

import pytest
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from dataclasses import dataclass
import uuid

try:
    from src.models.base import BaseModel, ValidationError
    from src.models.user import UserProfile, UserProgress
    from src.models.content import Topic, Problem, Concept, LearningPath
    from src.models.curriculum import Curriculum
except ImportError:
    # For isolated testing
    BaseModel = None
    ValidationError = Exception


# Mock model implementations for testing
@dataclass
class MockModel(BaseModel):
    """Mock model for testing base functionality."""
    name: str = "Test"
    value: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        super().__post_init__()
    
    def validate(self) -> None:
        """Validate the mock model."""
        if not self.name:
            raise ValidationError("Name cannot be empty")
        if self.value < 0:
            raise ValidationError("Value must be non-negative")


@dataclass
class InvalidMockModel(BaseModel):
    """Mock model that always fails validation."""
    name: str = ""
    
    def validate(self) -> None:
        raise ValidationError("Always invalid")


@pytest.mark.unit
class TestBaseModel:
    """Test cases for BaseModel abstract class."""
    
    def test_base_model_initialization(self, mock_datetime):
        """Test base model initialization with default values."""
        with patch('src.models.base.datetime') as mock_dt:
            mock_dt.utcnow.return_value = mock_datetime
            
            model = MockModel(name="Test Model", value=42)
            
            assert model.name == "Test Model"
            assert model.value == 42
            assert model.tags == []
            assert model.id is not None
            assert isinstance(model.id, str)
            assert model.created_at == mock_datetime
            assert model.updated_at == mock_datetime
            assert isinstance(model.metadata, dict)
    
    def test_base_model_validation_success(self):
        """Test successful model validation."""
        model = MockModel(name="Valid", value=10)
        # Should not raise an exception
        assert model.name == "Valid"
        assert model.value == 10
    
    def test_base_model_validation_failure(self):
        """Test model validation failure."""
        with pytest.raises(ValidationError, match="Name cannot be empty"):
            MockModel(name="", value=10)
        
        with pytest.raises(ValidationError, match="Value must be non-negative"):
            MockModel(name="Valid", value=-5)
    
    def test_base_model_validation_on_init(self):
        """Test validation is called during initialization."""
        with pytest.raises(ValidationError, match="Always invalid"):
            InvalidMockModel()
    
    def test_update_timestamp(self, mock_datetime):
        """Test timestamp update functionality."""
        model = MockModel(name="Test")
        original_updated_at = model.updated_at
        
        # Mock a later time
        later_time = mock_datetime + timedelta(minutes=5)
        
        with patch('src.models.base.datetime') as mock_dt:
            mock_dt.utcnow.return_value = later_time
            model.update_timestamp()
            
            assert model.updated_at == later_time
            assert model.updated_at != original_updated_at
    
    def test_to_dict(self):
        """Test model serialization to dictionary."""
        model = MockModel(name="Test", value=42, tags=["tag1", "tag2"])
        data = model.to_dict()
        
        assert isinstance(data, dict)
        assert data["name"] == "Test"
        assert data["value"] == 42
        assert data["tags"] == ["tag1", "tag2"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "metadata" in data
        
        # Check datetime serialization
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
    
    def test_from_dict(self):
        """Test model deserialization from dictionary."""
        original_model = MockModel(name="Test", value=42)
        data = original_model.to_dict()
        
        # Create new model from dict
        new_model = MockModel.from_dict(data)
        
        assert new_model.name == original_model.name
        assert new_model.value == original_model.value
        assert new_model.id == original_model.id
        assert new_model.created_at == original_model.created_at
        assert new_model.updated_at == original_model.updated_at
        assert new_model.metadata == original_model.metadata
    
    def test_to_json(self):
        """Test JSON serialization."""
        model = MockModel(name="Test", value=42)
        json_str = model.to_json()
        
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["name"] == "Test"
        assert data["value"] == 42
    
    def test_from_json(self):
        """Test JSON deserialization."""
        original_model = MockModel(name="Test", value=42)
        json_str = original_model.to_json()
        
        new_model = MockModel.from_json(json_str)
        
        assert new_model.name == original_model.name
        assert new_model.value == original_model.value
        assert new_model.id == original_model.id
    
    def test_metadata_operations(self):
        """Test metadata manipulation."""
        model = MockModel(name="Test")
        
        # Test setting metadata
        model.update_metadata("key1", "value1")
        assert model.metadata["key1"] == "value1"
        
        # Test getting metadata
        assert model.get_metadata("key1") == "value1"
        assert model.get_metadata("nonexistent") is None
        assert model.get_metadata("nonexistent", "default") == "default"
        
        # Test metadata updates timestamp
        original_updated_at = model.updated_at
        with patch('src.models.base.datetime') as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 16, 12, 0, 0)
            model.update_metadata("key2", "value2")
            assert model.updated_at != original_updated_at
    
    def test_search_functionality(self):
        """Test model search functionality."""
        models = [
            MockModel(name="Apple", value=1, tags=["fruit"]),
            MockModel(name="Banana", value=2, tags=["fruit", "yellow"]),
            MockModel(name="Carrot", value=3, tags=["vegetable"]),
            MockModel(name="Date", value=4, tags=["fruit", "sweet"])
        ]
        
        # Test basic search
        results = MockModel.search(models, "apple")
        assert len(results) == 1
        assert results[0].name == "Apple"
        
        # Test case insensitive search
        results = MockModel.search(models, "APPLE")
        assert len(results) == 1
        
        # Test partial match
        results = MockModel.search(models, "an")
        assert len(results) == 1  # Should match "Banana"
        assert results[0].name == "Banana"
        
        # Test empty query
        results = MockModel.search(models, "")
        assert len(results) == len(models)
        
        # Test no matches
        results = MockModel.search(models, "xyz")
        assert len(results) == 0
        
        # Test field-specific search
        results = MockModel.search(models, "fruit", fields=["tags"])
        assert len(results) == 3  # Apple, Banana, Date
    
    def test_filter_functionality(self):
        """Test model filtering functionality."""
        models = [
            MockModel(name="A", value=1),
            MockModel(name="B", value=2),
            MockModel(name="C", value=3),
            MockModel(name="D", value=4)
        ]
        
        # Test exact match filter
        results = MockModel.filter(models, {"value": 2})
        assert len(results) == 1
        assert results[0].name == "B"
        
        # Test range filters
        results = MockModel.filter(models, {"value": {"gt": 2}})
        assert len(results) == 2  # C and D
        
        results = MockModel.filter(models, {"value": {"gte": 2}})
        assert len(results) == 3  # B, C, and D
        
        results = MockModel.filter(models, {"value": {"lt": 3}})
        assert len(results) == 2  # A and B
        
        results = MockModel.filter(models, {"value": {"lte": 3}})
        assert len(results) == 3  # A, B, and C
        
        # Test 'in' filter
        results = MockModel.filter(models, {"value": {"in": [1, 3]}})
        assert len(results) == 2  # A and C
        
        # Test multiple filters
        results = MockModel.filter(models, {"name": "A", "value": 1})
        assert len(results) == 1
        assert results[0].name == "A"
        
        # Test empty filters
        results = MockModel.filter(models, {})
        assert len(results) == len(models)
    
    def test_sort_functionality(self):
        """Test model sorting functionality."""
        models = [
            MockModel(name="C", value=3),
            MockModel(name="A", value=1),
            MockModel(name="D", value=4),
            MockModel(name="B", value=2)
        ]
        
        # Test sort by name (ascending)
        sorted_models = MockModel.sort(models, "name")
        names = [m.name for m in sorted_models]
        assert names == ["A", "B", "C", "D"]
        
        # Test sort by value (ascending)
        sorted_models = MockModel.sort(models, "value")
        values = [m.value for m in sorted_models]
        assert values == [1, 2, 3, 4]
        
        # Test sort by value (descending)
        sorted_models = MockModel.sort(models, "value", reverse=True)
        values = [m.value for m in sorted_models]
        assert values == [4, 3, 2, 1]
    
    def test_equality_and_hashing(self):
        """Test model equality and hashing."""
        model1 = MockModel(name="Test", value=1)
        model2 = MockModel(name="Test", value=1)
        model3 = MockModel(name="Different", value=1)
        
        # Same ID should be equal
        model2.id = model1.id
        assert model1 == model2
        assert hash(model1) == hash(model2)
        
        # Different ID should not be equal
        assert model1 != model3
        assert hash(model1) != hash(model3)
        
        # Test inequality with non-BaseModel
        assert model1 != "not a model"
    
    def test_string_representations(self):
        """Test string representations."""
        model = MockModel(name="Test")
        
        str_repr = str(model)
        assert "MockModel" in str_repr
        assert model.id in str_repr
        
        repr_str = repr(model)
        assert "MockModel" in repr_str
        assert model.id in repr_str
        assert str(model.created_at) in repr_str


@pytest.mark.unit
class TestModelValidation:
    """Test cases for model validation functionality."""
    
    def test_validation_error_inheritance(self):
        """Test ValidationError is properly defined."""
        error = ValidationError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_complex_validation_scenarios(self):
        """Test complex validation scenarios."""
        # Test multiple validation errors
        with pytest.raises(ValidationError):
            MockModel(name="", value=-1)  # Both name and value invalid
    
    def test_validation_with_custom_logic(self):
        """Test validation with custom business logic."""
        @dataclass
        class CustomValidationModel(BaseModel):
            email: str = ""
            age: int = 0
            
            def validate(self) -> None:
                errors = []
                
                if not self.email or "@" not in self.email:
                    errors.append("Invalid email format")
                
                if self.age < 0 or self.age > 150:
                    errors.append("Age must be between 0 and 150")
                
                if errors:
                    raise ValidationError("; ".join(errors))
        
        # Valid model
        valid_model = CustomValidationModel(email="test@example.com", age=25)
        assert valid_model.email == "test@example.com"
        
        # Invalid email
        with pytest.raises(ValidationError, match="Invalid email format"):
            CustomValidationModel(email="invalid", age=25)
        
        # Invalid age
        with pytest.raises(ValidationError, match="Age must be between 0 and 150"):
            CustomValidationModel(email="test@example.com", age=200)
        
        # Multiple errors
        with pytest.raises(ValidationError, match="Invalid email format; Age must be between 0 and 150"):
            CustomValidationModel(email="invalid", age=-5)


@pytest.mark.unit
class TestModelSerialization:
    """Test cases for model serialization and deserialization."""
    
    def test_datetime_serialization(self):
        """Test datetime field serialization."""
        model = MockModel(name="Test")
        data = model.to_dict()
        
        # Should serialize datetime as ISO string
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        
        # Should be valid ISO format
        datetime.fromisoformat(data["created_at"])
        datetime.fromisoformat(data["updated_at"])
    
    def test_datetime_deserialization(self):
        """Test datetime field deserialization."""
        # Test with string datetime
        data = {
            "name": "Test",
            "value": 42,
            "id": str(uuid.uuid4()),
            "created_at": "2024-01-15T12:00:00",
            "updated_at": "2024-01-15T12:00:00",
            "metadata": {},
            "tags": []
        }
        
        model = MockModel.from_dict(data)
        
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
        assert model.created_at == datetime(2024, 1, 15, 12, 0, 0)
    
    def test_json_serialization_with_complex_data(self):
        """Test JSON serialization with complex nested data."""
        model = MockModel(
            name="Complex",
            value=42,
            tags=["tag1", "tag2"]
        )
        model.update_metadata("nested", {"key": "value", "list": [1, 2, 3]})
        
        json_str = model.to_json()
        data = json.loads(json_str)
        
        assert data["name"] == "Complex"
        assert data["tags"] == ["tag1", "tag2"]
        assert data["metadata"]["nested"]["key"] == "value"
        assert data["metadata"]["nested"]["list"] == [1, 2, 3]
    
    def test_roundtrip_serialization(self):
        """Test complete serialization roundtrip."""
        original = MockModel(
            name="Roundtrip",
            value=99,
            tags=["test", "roundtrip"]
        )
        original.update_metadata("test", "value")
        original.update_metadata("number", 42)
        
        # Dict roundtrip
        dict_copy = MockModel.from_dict(original.to_dict())
        assert dict_copy.name == original.name
        assert dict_copy.value == original.value
        assert dict_copy.tags == original.tags
        assert dict_copy.metadata == original.metadata
        assert dict_copy.id == original.id
        
        # JSON roundtrip
        json_copy = MockModel.from_json(original.to_json())
        assert json_copy.name == original.name
        assert json_copy.value == original.value
        assert json_copy.tags == original.tags
        assert json_copy.metadata == original.metadata
        assert json_copy.id == original.id


@pytest.mark.performance
class TestModelPerformance:
    """Performance tests for model operations."""
    
    def test_model_creation_performance(self, performance_tracker):
        """Test performance of model creation."""
        performance_tracker.start_timer("model_creation")
        
        models = []
        for i in range(1000):
            model = MockModel(name=f"Model {i}", value=i)
            models.append(model)
        
        duration = performance_tracker.end_timer("model_creation")
        
        # Should create 1000 models in under 1 second
        performance_tracker.assert_max_duration("model_creation", 1.0)
        assert len(models) == 1000
    
    def test_serialization_performance(self, performance_tracker):
        """Test performance of serialization operations."""
        models = [MockModel(name=f"Model {i}", value=i) for i in range(100)]
        
        # Test dict serialization performance
        performance_tracker.start_timer("dict_serialization")
        dicts = [model.to_dict() for model in models]
        performance_tracker.end_timer("dict_serialization")
        
        # Test JSON serialization performance
        performance_tracker.start_timer("json_serialization")
        jsons = [model.to_json() for model in models]
        performance_tracker.end_timer("json_serialization")
        
        # Should serialize 100 models in reasonable time
        performance_tracker.assert_max_duration("dict_serialization", 0.5)
        performance_tracker.assert_max_duration("json_serialization", 1.0)
        
        assert len(dicts) == 100
        assert len(jsons) == 100
    
    def test_search_performance(self, performance_tracker):
        """Test performance of search operations."""
        # Create large dataset
        models = []
        for i in range(1000):
            model = MockModel(
                name=f"Item {i}",
                value=i % 100,
                tags=[f"tag{i % 10}", f"category{i % 5}"]
            )
            models.append(model)
        
        performance_tracker.start_timer("search_operation")
        
        # Perform multiple searches
        results1 = MockModel.search(models, "Item 1")
        results2 = MockModel.search(models, "tag1")
        results3 = MockModel.filter(models, {"value": {"lt": 10}})
        results4 = MockModel.sort(models, "name")
        
        duration = performance_tracker.end_timer("search_operation")
        
        # Should complete searches on 1000 models in reasonable time
        performance_tracker.assert_max_duration("search_operation", 2.0)
        
        assert len(results1) > 0
        assert len(results2) > 0
        assert len(results3) > 0
        assert len(results4) == 1000


@pytest.mark.integration
class TestModelEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_model_operations(self):
        """Test operations on empty model collections."""
        empty_models = []
        
        # Search on empty collection
        results = MockModel.search(empty_models, "test")
        assert results == []
        
        # Filter on empty collection
        results = MockModel.filter(empty_models, {"name": "test"})
        assert results == []
        
        # Sort on empty collection
        results = MockModel.sort(empty_models, "name")
        assert results == []
    
    def test_malformed_data_handling(self):
        """Test handling of malformed data during deserialization."""
        # Test missing required fields
        incomplete_data = {"name": "Test"}
        
        with pytest.raises((KeyError, TypeError)):
            MockModel.from_dict(incomplete_data)
        
        # Test invalid JSON
        with pytest.raises(json.JSONDecodeError):
            MockModel.from_json("invalid json")
    
    def test_large_metadata_handling(self):
        """Test handling of large metadata objects."""
        model = MockModel(name="Large Metadata")
        
        # Add large metadata
        large_data = {f"key{i}": f"value{i}" * 100 for i in range(100)}
        model.metadata.update(large_data)
        
        # Should handle serialization/deserialization
        dict_data = model.to_dict()
        json_str = model.to_json()
        
        reconstructed = MockModel.from_dict(dict_data)
        assert len(reconstructed.metadata) == len(large_data)
    
    def test_special_character_handling(self):
        """Test handling of special characters in model data."""
        special_chars = "Test with special chars: àáâãäåæçèéêë 中文 🚀 \n\t\r"
        
        model = MockModel(name=special_chars)
        
        # Should handle serialization/deserialization
        json_str = model.to_json()
        reconstructed = MockModel.from_json(json_str)
        
        assert reconstructed.name == special_chars
    
    def test_concurrent_model_operations(self):
        """Test thread safety of model operations."""
        import threading
        import time
        
        models = [MockModel(name=f"Model {i}") for i in range(10)]
        results = []
        
        def update_model(model):
            for i in range(10):
                model.update_metadata(f"key{i}", f"value{i}")
                time.sleep(0.001)  # Small delay to encourage race conditions
            results.append(model)
        
        threads = [threading.Thread(target=update_model, args=(model,)) for model in models]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All models should have been processed
        assert len(results) == 10
        
        # Each model should have all metadata keys
        for model in results:
            assert len(model.metadata) == 10
            for i in range(10):
                assert f"key{i}" in model.metadata
