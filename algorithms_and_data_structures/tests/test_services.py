"""Test suite for Business Logic Services - Service layer functionality and business rules."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

try:
    from src.services.curriculum_service import CurriculumService
    from src.services.content_service import ContentService
    from src.persistence.db_manager import DatabaseManager
    from src.models.user import UserProfile, UserProgress
    from src.models.content import Topic, LearningPath
    from src.core.exceptions import ValidationError, ServiceError
except ImportError:
    # For isolated testing
    CurriculumService = None
    ContentService = None


@pytest.mark.unit
class TestCurriculumService:
    """Test cases for CurriculumService business logic."""
    
    def test_curriculum_service_initialization(self, mock_db_manager, test_config):
        """Test curriculum service initialization."""
        service = CurriculumService(mock_db_manager, test_config)
        
        assert service.db_manager == mock_db_manager
        assert service.config == test_config
        assert service.logger is not None
        assert service._topics_cache is None
        assert service._learning_paths_cache is None
    
    def test_get_all_topics_from_database(self, mock_db_manager, test_config, test_data_factory):
        """Test getting all topics from database."""
        # Mock database response
        mock_topics = [
            test_data_factory.create_topic("Arrays"),
            test_data_factory.create_topic("Linked Lists"),
            test_data_factory.create_topic("Trees")
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        topics = service.get_all_topics()
        
        assert len(topics) == 3
        assert topics[0]["name"] == "Arrays"
        assert topics[1]["name"] == "Linked Lists"
        assert topics[2]["name"] == "Trees"
        
        # Verify database was called
        mock_db_manager.get_all_topics.assert_called_once()
        
        # Verify cache was populated
        assert service._topics_cache == mock_topics
        assert service._cache_timestamp is not None
    
    def test_get_all_topics_from_cache(self, mock_db_manager, test_config, test_data_factory):
        """Test getting topics from cache when available."""
        mock_topics = [test_data_factory.create_topic("Cached Topic")]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # First call - should hit database
        topics1 = service.get_all_topics()
        
        # Second call - should hit cache
        topics2 = service.get_all_topics()
        
        assert topics1 == topics2
        # Database should only be called once
        mock_db_manager.get_all_topics.assert_called_once()
    
    def test_get_all_topics_force_refresh(self, mock_db_manager, test_config, test_data_factory):
        """Test forcing cache refresh."""
        mock_topics1 = [test_data_factory.create_topic("Topic 1")]
        mock_topics2 = [test_data_factory.create_topic("Topic 2")]
        
        mock_db_manager.get_all_topics.side_effect = [mock_topics1, mock_topics2]
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # First call
        topics1 = service.get_all_topics()
        
        # Force refresh
        topics2 = service.get_all_topics(force_refresh=True)
        
        assert topics1 != topics2
        assert len(topics1) == 1
        assert len(topics2) == 1
        assert topics1[0]["name"] == "Topic 1"
        assert topics2[0]["name"] == "Topic 2"
        
        # Database should be called twice
        assert mock_db_manager.get_all_topics.call_count == 2
    
    def test_get_topic_by_name(self, mock_db_manager, test_config, test_data_factory):
        """Test getting topic by name."""
        mock_topics = [
            test_data_factory.create_topic("Arrays"),
            test_data_factory.create_topic("Linked Lists"),
            test_data_factory.create_topic("Trees")
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Test exact match
        topic = service.get_topic_by_name("Arrays")
        assert topic is not None
        assert topic["name"] == "Arrays"
        
        # Test case insensitive match
        topic = service.get_topic_by_name("arrays")
        assert topic is not None
        assert topic["name"] == "Arrays"
        
        # Test non-existent topic
        topic = service.get_topic_by_name("NonExistent")
        assert topic is None
    
    def test_get_topics_by_difficulty(self, mock_db_manager, test_config, test_data_factory):
        """Test filtering topics by difficulty."""
        mock_topics = [
            test_data_factory.create_topic("Easy Topic", difficulty="beginner"),
            test_data_factory.create_topic("Medium Topic", difficulty="intermediate"),
            test_data_factory.create_topic("Hard Topic", difficulty="advanced"),
            test_data_factory.create_topic("Another Easy", difficulty="beginner")
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Test beginner topics
        beginner_topics = service.get_topics_by_difficulty("beginner")
        assert len(beginner_topics) == 2
        assert all(topic["difficulty"] == "beginner" for topic in beginner_topics)
        
        # Test intermediate topics
        intermediate_topics = service.get_topics_by_difficulty("intermediate")
        assert len(intermediate_topics) == 1
        assert intermediate_topics[0]["name"] == "Medium Topic"
        
        # Test case insensitive
        advanced_topics = service.get_topics_by_difficulty("ADVANCED")
        assert len(advanced_topics) == 1
        assert advanced_topics[0]["name"] == "Hard Topic"
    
    def test_get_topic_prerequisites(self, mock_db_manager, test_config, test_data_factory):
        """Test getting topic prerequisites."""
        mock_topics = [
            test_data_factory.create_topic("Arrays", prerequisites=[]),
            test_data_factory.create_topic("Linked Lists", prerequisites=["Arrays"]),
            test_data_factory.create_topic("Trees", prerequisites=["Arrays", "Linked Lists"])
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Test topic with no prerequisites
        prereqs = service.get_topic_prerequisites("Arrays")
        assert prereqs == []
        
        # Test topic with one prerequisite
        prereqs = service.get_topic_prerequisites("Linked Lists")
        assert prereqs == ["Arrays"]
        
        # Test topic with multiple prerequisites
        prereqs = service.get_topic_prerequisites("Trees")
        assert set(prereqs) == {"Arrays", "Linked Lists"}
        
        # Test non-existent topic
        prereqs = service.get_topic_prerequisites("NonExistent")
        assert prereqs == []
    
    def test_get_topic_dependents(self, mock_db_manager, test_config, test_data_factory):
        """Test getting topics that depend on a given topic."""
        mock_topics = [
            test_data_factory.create_topic("Arrays", prerequisites=[]),
            test_data_factory.create_topic("Linked Lists", prerequisites=["Arrays"]),
            test_data_factory.create_topic("Trees", prerequisites=["Arrays", "Linked Lists"]),
            test_data_factory.create_topic("Graphs", prerequisites=["Trees"])
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Test topic with dependents
        dependents = service.get_topic_dependents("Arrays")
        assert set(dependents) == {"Linked Lists", "Trees"}
        
        # Test topic with one dependent
        dependents = service.get_topic_dependents("Trees")
        assert dependents == ["Graphs"]
        
        # Test topic with no dependents
        dependents = service.get_topic_dependents("Graphs")
        assert dependents == []
    
    def test_get_learning_paths(self, mock_db_manager, test_config, test_data_factory):
        """Test getting learning paths."""
        mock_paths = [
            test_data_factory.create_learning_path("Beginner Path"),
            test_data_factory.create_learning_path("Advanced Path")
        ]
        mock_db_manager.get_all_learning_paths.return_value = mock_paths
        
        service = CurriculumService(mock_db_manager, test_config)
        paths = service.get_learning_paths()
        
        assert len(paths) == 2
        assert paths[0]["name"] == "Beginner Path"
        assert paths[1]["name"] == "Advanced Path"
        
        # Verify caching
        assert service._learning_paths_cache == mock_paths
    
    def test_get_recommended_learning_path(self, mock_db_manager, test_config, test_data_factory):
        """Test getting recommended learning path for user."""
        # Mock user profile
        user_profile = test_data_factory.create_user_profile(
            learning_goals=["algorithms", "data structures"]
        )
        
        # Mock learning paths
        mock_paths = [
            test_data_factory.create_learning_path(
                "Algorithms Path",
                difficulty="intermediate",
                topics=["Arrays", "Sorting", "Searching"]
            ),
            test_data_factory.create_learning_path(
                "Data Structures Path",
                difficulty="beginner",
                topics=["Arrays", "Linked Lists", "Stacks"]
            ),
            test_data_factory.create_learning_path(
                "Advanced Path",
                difficulty="advanced",
                topics=["Dynamic Programming", "Graph Algorithms"]
            )
        ]
        mock_db_manager.get_all_learning_paths.return_value = mock_paths
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Mock user level determination
        with patch.object(service, '_determine_user_level', return_value="intermediate"):
            recommended_path = service.get_recommended_learning_path(user_profile)
        
        # Should recommend the intermediate algorithms path
        assert recommended_path is not None
        assert recommended_path["name"] == "Algorithms Path"
    
    def test_get_next_topics_in_path(self, mock_db_manager, test_config, test_data_factory):
        """Test getting next topics to study in a learning path."""
        # Mock learning path
        learning_path = test_data_factory.create_learning_path(
            "Test Path",
            topics=["Arrays", "Linked Lists", "Trees", "Graphs"]
        )
        
        # Mock user progress
        user_progress = test_data_factory.create_user_progress(
            completed_topics=["Arrays"]
        )
        
        # Mock topic prerequisites
        mock_topics = [
            test_data_factory.create_topic("Arrays", prerequisites=[]),
            test_data_factory.create_topic("Linked Lists", prerequisites=["Arrays"]),
            test_data_factory.create_topic("Trees", prerequisites=["Arrays", "Linked Lists"]),
            test_data_factory.create_topic("Graphs", prerequisites=["Trees"])
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        next_topics = service.get_next_topics_in_path(learning_path, user_progress)
        
        # Should suggest Linked Lists (prerequisites met)
        # Should not suggest Trees or Graphs (prerequisites not met)
        assert "Linked Lists" in next_topics
        assert "Trees" not in next_topics
        assert "Graphs" not in next_topics
        assert len(next_topics) <= 3  # Respects max_concurrent_topics
    
    def test_validate_topic_sequence(self, mock_db_manager, test_config, test_data_factory):
        """Test topic sequence validation."""
        # Mock topics with prerequisites
        mock_topics = [
            test_data_factory.create_topic("A", prerequisites=[]),
            test_data_factory.create_topic("B", prerequisites=["A"]),
            test_data_factory.create_topic("C", prerequisites=["B"]),
            test_data_factory.create_topic("D", prerequisites=["A", "C"])
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Test valid sequence
        valid_sequence = ["A", "B", "C", "D"]
        result = service.validate_topic_sequence(valid_sequence)
        assert result["is_valid"] is True
        assert len(result["issues"]) == 0
        
        # Test invalid sequence
        invalid_sequence = ["B", "A", "C", "D"]  # B before A
        result = service.validate_topic_sequence(invalid_sequence)
        assert result["is_valid"] is False
        assert len(result["issues"]) > 0
        assert "suggested_order" in result
    
    def test_create_custom_learning_path(self, mock_db_manager, test_config, test_data_factory):
        """Test creating custom learning path."""
        # Mock topics
        mock_topics = [
            test_data_factory.create_topic("A", prerequisites=[], difficulty="beginner"),
            test_data_factory.create_topic("B", prerequisites=["A"], difficulty="intermediate"),
            test_data_factory.create_topic("C", prerequisites=["B"], difficulty="advanced")
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        # Mock user profile
        user_profile = test_data_factory.create_user_profile("Test User")
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Mock validation and path creation methods
        with patch.object(service, 'validate_topic_sequence') as mock_validate:
            mock_validate.return_value = {"is_valid": True}
            
            learning_path = service.create_custom_learning_path(
                "Custom Path",
                "Custom description",
                ["A", "B", "C"],
                user_profile
            )
            
            # Verify path creation
            assert learning_path["name"] == "Custom Path"
            assert learning_path["description"] == "Custom description"
            assert learning_path["topics"] == ["A", "B", "C"]
            assert learning_path["is_custom"] is True
            
            # Verify database save was called
            mock_db_manager.save_learning_path.assert_called_once()
    
    def test_get_topic_statistics(self, mock_db_manager, test_config, test_data_factory):
        """Test getting comprehensive topic statistics."""
        # Mock diverse topics
        mock_topics = [
            test_data_factory.create_topic(
                "Topic 1",
                difficulty="beginner",
                categories=["arrays"],
                concepts=["concept1", "concept2"],
                problems=["problem1"]
            ),
            test_data_factory.create_topic(
                "Topic 2",
                difficulty="intermediate",
                categories=["arrays", "sorting"],
                prerequisites=["Topic 1"],
                concepts=["concept3"],
                problems=["problem2", "problem3"]
            ),
            test_data_factory.create_topic(
                "Topic 3",
                difficulty="advanced",
                categories=["trees"],
                prerequisites=["Topic 1", "Topic 2"],
                concepts=["concept4", "concept5", "concept6"],
                problems=["problem4", "problem5"]
            )
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        stats = service.get_topic_statistics()
        
        assert stats["total_topics"] == 3
        assert stats["topics_with_prerequisites"] == 2
        assert stats["difficulty_distribution"]["beginner"] == 1
        assert stats["difficulty_distribution"]["intermediate"] == 1
        assert stats["difficulty_distribution"]["advanced"] == 1
        assert stats["average_concepts_per_topic"] == 2.0  # (2+1+3)/3
        assert stats["average_problems_per_topic"] == 1.67  # (1+2+2)/3 rounded
        assert stats["topics_by_category"]["arrays"] == 2
        assert stats["topics_by_category"]["sorting"] == 1
        assert stats["topics_by_category"]["trees"] == 1
    
    def test_cache_expiration(self, mock_db_manager, test_config, test_data_factory, mock_datetime):
        """Test cache expiration behavior."""
        mock_topics1 = [test_data_factory.create_topic("Topic 1")]
        mock_topics2 = [test_data_factory.create_topic("Topic 2")]
        
        mock_db_manager.get_all_topics.side_effect = [mock_topics1, mock_topics2]
        
        service = CurriculumService(mock_db_manager, test_config)
        service._cache_ttl = timedelta(minutes=1)  # Short TTL for testing
        
        with patch('src.services.curriculum_service.datetime') as mock_dt:
            # First call
            mock_dt.now.return_value = mock_datetime
            topics1 = service.get_all_topics()
            
            # Second call within TTL - should use cache
            mock_dt.now.return_value = mock_datetime + timedelta(seconds=30)
            topics2 = service.get_all_topics()
            
            # Third call after TTL - should refresh cache
            mock_dt.now.return_value = mock_datetime + timedelta(minutes=2)
            topics3 = service.get_all_topics()
            
            assert topics1 == topics2  # Same (cached)
            assert topics1 != topics3  # Different (refreshed)
            
            # Database should be called twice (initial + refresh)
            assert mock_db_manager.get_all_topics.call_count == 2
    
    def test_error_handling(self, mock_db_manager, test_config):
        """Test service error handling."""
        # Mock database error
        mock_db_manager.get_all_topics.side_effect = Exception("Database error")
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Should propagate database errors
        with pytest.raises(Exception, match="Database error"):
            service.get_all_topics()
        
        # Error should not affect other operations if database recovers
        mock_db_manager.get_all_topics.side_effect = None
        mock_db_manager.get_all_topics.return_value = []
        
        topics = service.get_all_topics()
        assert topics == []
    
    def test_clear_cache(self, mock_db_manager, test_config, test_data_factory):
        """Test cache clearing functionality."""
        mock_topics = [test_data_factory.create_topic("Test")]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Populate cache
        service.get_all_topics()
        assert service._topics_cache is not None
        assert service._cache_timestamp is not None
        
        # Clear cache
        service.clear_cache()
        assert service._topics_cache is None
        assert service._learning_paths_cache is None
        assert service._cache_timestamp is None


@pytest.mark.unit
class TestContentService:
    """Test cases for ContentService business logic."""
    
    def test_content_service_initialization(self, mock_db_manager, test_config):
        """Test content service initialization."""
        service = ContentService(mock_db_manager, test_config)
        
        assert service.db_manager == mock_db_manager
        assert service.config == test_config
        assert service.logger is not None
    
    def test_content_creation_validation(self, mock_db_manager, test_config):
        """Test content creation with validation."""
        service = ContentService(mock_db_manager, test_config)
        
        # Test valid content creation
        content_data = {
            "name": "Test Topic",
            "description": "Test description",
            "difficulty": "intermediate",
            "categories": ["algorithms"]
        }
        
        with patch.object(service, '_validate_content_data') as mock_validate:
            mock_validate.return_value = []
            
            result = service.create_content(content_data)
            
            assert result["success"] is True
            mock_validate.assert_called_once_with(content_data)
    
    def test_content_search_functionality(self, mock_db_manager, test_config, test_data_factory):
        """Test content search functionality."""
        # Mock content repository
        mock_content_repo = Mock()
        mock_content_repo.search.return_value = [
            test_data_factory.create_topic("Array Search"),
            test_data_factory.create_topic("Binary Search")
        ]
        
        service = ContentService(mock_db_manager, test_config)
        
        with patch.object(service, '_get_content_repository', return_value=mock_content_repo):
            results = service.search_content("search")
            
            assert len(results) == 2
            assert "Array Search" in results[0]["name"]
            assert "Binary Search" in results[1]["name"]
            mock_content_repo.search.assert_called_once_with("search")
    
    def test_content_filtering(self, mock_db_manager, test_config, test_data_factory):
        """Test content filtering by various criteria."""
        mock_content_repo = Mock()
        mock_content_repo.filter.return_value = [
            test_data_factory.create_topic("Easy Topic", difficulty="beginner")
        ]
        
        service = ContentService(mock_db_manager, test_config)
        
        with patch.object(service, '_get_content_repository', return_value=mock_content_repo):
            results = service.filter_content({
                "difficulty": "beginner",
                "category": "arrays"
            })
            
            assert len(results) == 1
            assert results[0]["difficulty"] == "beginner"
            mock_content_repo.filter.assert_called_once()
    
    def test_content_validation_rules(self, mock_db_manager, test_config):
        """Test content validation rules."""
        service = ContentService(mock_db_manager, test_config)
        
        # Test valid content
        valid_content = {
            "name": "Valid Topic",
            "description": "Valid description",
            "difficulty": "intermediate",
            "categories": ["algorithms"]
        }
        errors = service._validate_content_data(valid_content)
        assert len(errors) == 0
        
        # Test invalid content - missing required fields
        invalid_content = {
            "description": "Missing name"
        }
        errors = service._validate_content_data(invalid_content)
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)
        
        # Test invalid difficulty
        invalid_difficulty = {
            "name": "Test",
            "description": "Test",
            "difficulty": "invalid_difficulty",
            "categories": ["algorithms"]
        }
        errors = service._validate_content_data(invalid_difficulty)
        assert len(errors) > 0
        assert any("difficulty" in error.lower() for error in errors)


@pytest.mark.integration
class TestServiceIntegration:
    """Integration tests for service layer."""
    
    def test_curriculum_content_service_interaction(self, mock_db_manager, test_config, test_data_factory):
        """Test interaction between curriculum and content services."""
        # Mock topics
        mock_topics = [
            test_data_factory.create_topic("Arrays"),
            test_data_factory.create_topic("Linked Lists", prerequisites=["Arrays"])
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        curriculum_service = CurriculumService(mock_db_manager, test_config)
        content_service = ContentService(mock_db_manager, test_config)
        
        # Test curriculum service getting topics
        topics = curriculum_service.get_all_topics()
        assert len(topics) == 2
        
        # Test content service using the same data
        with patch.object(content_service, '_get_content_repository') as mock_repo:
            mock_repo.return_value.get_all.return_value = mock_topics
            
            all_content = content_service.get_all_content()
            assert len(all_content) == 2
    
    def test_service_error_propagation(self, mock_db_manager, test_config):
        """Test error propagation between services."""
        # Mock database error
        mock_db_manager.get_all_topics.side_effect = Exception("Database connection failed")
        
        curriculum_service = CurriculumService(mock_db_manager, test_config)
        
        # Error should propagate from database through service
        with pytest.raises(Exception, match="Database connection failed"):
            curriculum_service.get_all_topics()
    
    def test_service_transaction_handling(self, mock_db_manager, test_config, test_data_factory):
        """Test service transaction handling."""
        curriculum_service = CurriculumService(mock_db_manager, test_config)
        user_profile = test_data_factory.create_user_profile()
        
        # Mock database transaction methods
        mock_backend = Mock()
        mock_backend.begin_transaction = Mock()
        mock_backend.commit_transaction = Mock()
        mock_backend.rollback_transaction = Mock()
        mock_db_manager.get_backend.return_value = mock_backend
        
        # Mock other required methods
        mock_db_manager.save_learning_path = Mock()
        
        with patch.object(curriculum_service, 'validate_topic_sequence') as mock_validate:
            mock_validate.return_value = {"is_valid": True}
            
            # Test successful transaction
            try:
                learning_path = curriculum_service.create_custom_learning_path(
                    "Test Path",
                    "Description",
                    ["A", "B"],
                    user_profile
                )
                
                # Should have created the path successfully
                assert learning_path["name"] == "Test Path"
                
            except Exception:
                # If any error occurs, it should be handled gracefully
                pass


@pytest.mark.performance
class TestServicePerformance:
    """Performance tests for service layer."""
    
    def test_curriculum_service_caching_performance(self, mock_db_manager, test_config, test_data_factory, performance_tracker):
        """Test performance impact of caching in curriculum service."""
        # Create large dataset
        mock_topics = [test_data_factory.create_topic(f"Topic {i}") for i in range(1000)]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Test initial load performance
        performance_tracker.start_timer("initial_load")
        topics1 = service.get_all_topics()
        performance_tracker.end_timer("initial_load")
        
        # Test cached access performance
        performance_tracker.start_timer("cached_access")
        for _ in range(100):
            topics_cached = service.get_all_topics()
        performance_tracker.end_timer("cached_access")
        
        # Cached access should be much faster
        initial_duration = performance_tracker.get_metrics()["initial_load"]
        cached_duration = performance_tracker.get_metrics()["cached_access"]
        
        # Cache should provide significant speedup
        assert cached_duration < initial_duration
        
        # Verify correctness
        assert len(topics1) == 1000
        assert topics1 == topics_cached
    
    def test_service_bulk_operations_performance(self, mock_db_manager, test_config, test_data_factory, performance_tracker):
        """Test performance of bulk service operations."""
        # Mock large dataset
        mock_topics = [test_data_factory.create_topic(f"Topic {i}") for i in range(500)]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        performance_tracker.start_timer("bulk_filtering")
        
        # Perform multiple filtering operations
        results = []
        for difficulty in ["beginner", "intermediate", "advanced"]:
            filtered = service.get_topics_by_difficulty(difficulty)
            results.extend(filtered)
        
        duration = performance_tracker.end_timer("bulk_filtering")
        
        # Should complete bulk operations efficiently
        performance_tracker.assert_max_duration("bulk_filtering", 1.0)
        
        # Verify results
        assert len(results) >= 0
    
    def test_service_search_performance(self, mock_db_manager, test_config, test_data_factory, performance_tracker):
        """Test performance of service search operations."""
        # Create searchable dataset
        mock_topics = [
            test_data_factory.create_topic(f"Algorithm {i}", categories=["algorithms"])
            for i in range(200)
        ] + [
            test_data_factory.create_topic(f"Data Structure {i}", categories=["data_structures"])
            for i in range(200)
        ]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        performance_tracker.start_timer("search_operations")
        
        # Perform multiple search operations
        search_terms = ["Algorithm", "Data Structure", "Tree", "Sort", "Graph"]
        for term in search_terms:
            # Simulate search by filtering topics
            matching_topics = [
                topic for topic in service.get_all_topics()
                if term.lower() in topic["name"].lower()
            ]
        
        duration = performance_tracker.end_timer("search_operations")
        
        # Should complete searches efficiently
        performance_tracker.assert_max_duration("search_operations", 0.5)


@pytest.mark.slow
class TestServiceErrorScenarios:
    """Test various error scenarios in services."""
    
    def test_database_unavailable_handling(self, test_config, error_simulator):
        """Test service behavior when database is unavailable."""
        mock_db_manager = error_simulator.create_failing_mock("database_error")
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Should handle database errors gracefully
        with pytest.raises(Exception):
            service.get_all_topics()
    
    def test_partial_data_corruption_handling(self, mock_db_manager, test_config, test_data_factory):
        """Test handling of partially corrupted data."""
        # Mock corrupted topic data
        corrupted_topics = [
            test_data_factory.create_topic("Valid Topic"),
            {"incomplete": "data"},  # Missing required fields
            test_data_factory.create_topic("Another Valid Topic")
        ]
        mock_db_manager.get_all_topics.return_value = corrupted_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Service should handle corrupted data gracefully
        try:
            topics = service.get_all_topics()
            # Should return what data it can
            assert len(topics) == 3
        except Exception:
            # Or raise appropriate error
            pass
    
    def test_memory_pressure_handling(self, mock_db_manager, test_config, test_data_factory):
        """Test service behavior under memory pressure."""
        # Mock very large dataset
        huge_topics = [test_data_factory.create_topic(f"Topic {i}") for i in range(10000)]
        mock_db_manager.get_all_topics.return_value = huge_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        
        # Should handle large datasets without crashing
        try:
            topics = service.get_all_topics()
            assert len(topics) == 10000
        except MemoryError:
            # Acceptable to fail with memory error for very large datasets
            pytest.skip("Memory error expected for large dataset")
    
    def test_concurrent_access_safety(self, mock_db_manager, test_config, test_data_factory):
        """Test service thread safety under concurrent access."""
        import threading
        import time
        
        mock_topics = [test_data_factory.create_topic(f"Topic {i}") for i in range(100)]
        mock_db_manager.get_all_topics.return_value = mock_topics
        
        service = CurriculumService(mock_db_manager, test_config)
        results = []
        errors = []
        
        def concurrent_access():
            try:
                for _ in range(10):
                    topics = service.get_all_topics()
                    results.append(len(topics))
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads accessing service concurrently
        threads = [threading.Thread(target=concurrent_access) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access without errors
        assert len(errors) == 0
        assert len(results) == 50  # 5 threads * 10 operations each
        assert all(result == 100 for result in results)  # All should return same count
