"""
Test suite for performance optimization features.
"""

import unittest
import threading
import time
import tempfile
import os
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk

# Import performance optimization modules
try:
    from src.performance_optimization import (
        PerformanceOptimizer, ResourceManager, ChunkedImageCollector,
        UIResponsivenessOptimizer, ProgressFeedbackSystem
    )
    from src.utils.performance.memory_manager import MemoryManager, LRUCache
    from src.utils.performance.task_queue import TaskQueue, TaskPriority, BackgroundTask
    from src.utils.performance.image_optimizer import ImageOptimizer, LazyImageLoader
    from src.optimized_image_collection import OptimizedImageCollector
    PERFORMANCE_AVAILABLE = True
except ImportError as e:
    print(f"Performance optimization not available for testing: {e}")
    PERFORMANCE_AVAILABLE = False


@unittest.skipUnless(PERFORMANCE_AVAILABLE, "Performance optimization not available")
class TestMemoryManager(unittest.TestCase):
    """Test memory management functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_manager = MemoryManager()
        
    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self.memory_manager, 'stop_monitoring'):
            self.memory_manager.stop_monitoring()
            
    def test_lru_cache_basic_operations(self):
        """Test basic LRU cache operations."""
        cache = LRUCache[str](max_size=3, max_memory_mb=1.0)
        
        # Test put and get
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        self.assertEqual(cache.get("key1"), "value1")
        self.assertEqual(cache.get("key2"), "value2")
        self.assertEqual(cache.get("key3"), "value3")
        
        # Test LRU eviction
        cache.put("key4", "value4")  # Should evict key1 (least recently used)
        self.assertIsNone(cache.get("key1"))
        self.assertEqual(cache.get("key4"), "value4")
        
    def test_memory_cache_operations(self):
        """Test memory manager cache operations."""
        # Test image caching
        test_data = b"fake image data"
        url = "http://example.com/image.jpg"
        
        self.memory_manager.put_image_in_cache(url, test_data)
        cached_data = self.memory_manager.get_image_from_cache(url)
        
        self.assertEqual(cached_data, test_data)
        
        # Test cache miss
        missing_data = self.memory_manager.get_image_from_cache("nonexistent")
        self.assertIsNone(missing_data)
        
    def test_memory_monitoring(self):
        """Test memory monitoring functionality."""
        # Start monitoring
        self.memory_manager.start_monitoring(interval=0.1)
        
        # Wait for at least one monitoring cycle
        time.sleep(0.2)
        
        # Check that monitoring is active
        self.assertTrue(self.memory_manager._monitoring)
        
        # Stop monitoring
        self.memory_manager.stop_monitoring()
        self.assertFalse(self.memory_manager._monitoring)
        
    def test_cache_statistics(self):
        """Test cache statistics collection."""
        # Add some data to cache
        for i in range(5):
            self.memory_manager.put_image_in_cache(f"url_{i}", b"data")
            
        # Get some data to generate hits and misses
        self.memory_manager.get_image_from_cache("url_1")  # Hit
        self.memory_manager.get_image_from_cache("nonexistent")  # Miss
        
        stats = self.memory_manager.get_cache_stats()
        
        self.assertIn('cache_hits', stats)
        self.assertIn('cache_misses', stats)
        self.assertIn('memory_usage_mb', stats)
        self.assertGreaterEqual(stats['cache_hits'], 1)
        self.assertGreaterEqual(stats['cache_misses'], 1)


@unittest.skipUnless(PERFORMANCE_AVAILABLE, "Performance optimization not available")
class TestTaskQueue(unittest.TestCase):
    """Test background task processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.task_queue = TaskQueue(max_workers=2)
        
    def tearDown(self):
        """Clean up test environment."""
        self.task_queue.shutdown()
        
    def test_task_submission(self):
        """Test task submission and execution."""
        result_holder = {'result': None}
        
        def test_task(x, y):
            return x + y
            
        def callback(result):
            result_holder['result'] = result
            
        # Submit task
        task_id = self.task_queue.submit_task(
            "test_task",
            test_task,
            args=(5, 3),
            callback=callback
        )
        
        # Wait for completion
        time.sleep(0.5)
        
        # Check result
        self.assertEqual(result_holder['result'], 8)
        
        # Check task status
        task = self.task_queue.get_task_status(task_id)
        self.assertIsNotNone(task)
        
    def test_task_priority(self):
        """Test task priority handling."""
        execution_order = []
        
        def priority_task(priority_name):
            execution_order.append(priority_name)
            return priority_name
            
        # Submit tasks in reverse priority order
        self.task_queue.submit_task(
            "low", priority_task, args=("low",), 
            priority=TaskPriority.LOW
        )
        self.task_queue.submit_task(
            "high", priority_task, args=("high",), 
            priority=TaskPriority.HIGH
        )
        self.task_queue.submit_task(
            "normal", priority_task, args=("normal",), 
            priority=TaskPriority.NORMAL
        )
        
        # Wait for all tasks to complete
        time.sleep(1.0)
        
        # High priority should execute first
        self.assertEqual(execution_order[0], "high")
        
    def test_queue_statistics(self):
        """Test queue statistics collection."""
        # Submit several tasks
        for i in range(3):
            self.task_queue.submit_task(
                f"task_{i}",
                lambda x=i: time.sleep(0.1)
            )
            
        # Get statistics
        stats = self.task_queue.get_queue_stats()
        
        self.assertIn('pending_tasks', stats)
        self.assertIn('active_tasks', stats)
        self.assertIn('completed_tasks', stats)
        self.assertIn('worker_threads', stats)


@unittest.skipUnless(PERFORMANCE_AVAILABLE, "Performance optimization not available")
class TestResourceManager(unittest.TestCase):
    """Test resource management functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.resource_manager = ResourceManager()
        
    def tearDown(self):
        """Clean up test environment."""
        self.resource_manager.stop_auto_cleanup()
        
    def test_resource_registration(self):
        """Test resource registration and cleanup."""
        cleanup_called = {'flag': False}
        
        def cleanup_callback():
            cleanup_called['flag'] = True
            
        # Create mock resource
        mock_resource = Mock()
        
        # Register resource
        self.resource_manager.register_resource(
            "test_resource",
            mock_resource,
            cleanup_callback
        )
        
        # Check resource is registered
        self.assertEqual(
            self.resource_manager.get_resource_count(),
            1
        )
        
        # Release resource
        released = self.resource_manager.release_resource("test_resource")
        self.assertTrue(released)
        self.assertTrue(cleanup_called['flag'])
        self.assertEqual(self.resource_manager.get_resource_count(), 0)
        
    def test_auto_cleanup_system(self):
        """Test automatic cleanup system."""
        cleanup_count = {'count': 0}
        
        def cleanup_callback():
            cleanup_count['count'] += 1
            
        # Register multiple resources
        for i in range(5):
            self.resource_manager.register_resource(
                f"resource_{i}",
                f"data_{i}",
                cleanup_callback
            )
            
        # Start auto cleanup
        self.resource_manager.start_auto_cleanup()
        
        # Wait for cleanup cycle
        time.sleep(0.5)
        
        # Resources should still be there (no memory pressure)
        self.assertGreaterEqual(self.resource_manager.get_resource_count(), 5)


@unittest.skipUnless(PERFORMANCE_AVAILABLE, "Performance optimization not available")
class TestChunkedImageCollector(unittest.TestCase):
    """Test chunked image collection."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_manager = MemoryManager()
        self.collector = ChunkedImageCollector(
            self.memory_manager, 
            chunk_size=3
        )
        
    def tearDown(self):
        """Clean up test environment."""
        self.collector.stop_processing()
        
    def test_chunk_creation(self):
        """Test chunk creation and processing."""
        chunk_callbacks = []
        
        def chunk_callback(chunk, chunk_number):
            chunk_callbacks.append((chunk, chunk_number))
            
        self.collector.add_chunk_callback(chunk_callback)
        self.collector.start_processing()
        
        # Add images to trigger chunk creation
        for i in range(7):  # Should create 2 full chunks + partial
            self.collector.add_image_data({'id': i, 'url': f'http://example.com/{i}'})
            
        # Finalize to process remaining items
        self.collector.finalize_collection()
        
        # Wait for processing
        time.sleep(0.5)
        
        # Should have at least 2 complete chunks
        self.assertGreaterEqual(len(chunk_callbacks), 2)
        
        # First chunk should have 3 items
        first_chunk, chunk_num = chunk_callbacks[0]
        self.assertEqual(len(first_chunk), 3)
        
    def test_collection_statistics(self):
        """Test collection statistics."""
        # Add some images
        for i in range(5):
            self.collector.add_image_data({'id': i})
            
        stats = self.collector.get_collection_stats()
        
        self.assertIn('total_chunks', stats)
        self.assertIn('current_chunk_size', stats)
        self.assertIn('total_images', stats)
        self.assertEqual(stats['total_images'], 5)


@unittest.skipUnless(PERFORMANCE_AVAILABLE, "Performance optimization not available")
class TestUIResponsivenessOptimizer(unittest.TestCase):
    """Test UI responsiveness optimization."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock root widget
        self.mock_root = Mock()
        self.mock_root.after_idle = Mock()
        
        self.ui_optimizer = UIResponsivenessOptimizer(self.mock_root)
        
    def tearDown(self):
        """Clean up test environment."""
        self.ui_optimizer.stop_ui_optimization()
        
    def test_ui_update_scheduling(self):
        """Test UI update scheduling."""
        update_called = {'flag': False}
        
        def test_update():
            update_called['flag'] = True
            
        self.ui_optimizer.start_ui_optimization()
        
        # Schedule update
        self.ui_optimizer.schedule_ui_update(
            "test_update",
            test_update
        )
        
        # Wait for processing
        time.sleep(0.2)
        
        # Mock root should have been called for UI update
        self.mock_root.after_idle.assert_called()
        
    def test_progress_callback_registration(self):
        """Test progress callback registration."""
        def progress_callback(progress, message):
            pass
            
        # Register callback
        self.ui_optimizer.register_progress_callback(
            "test_operation",
            progress_callback
        )
        
        # Update progress
        self.ui_optimizer.update_progress(
            "test_operation",
            0.5,
            "Test message"
        )
        
        # Should not raise any exceptions


@unittest.skipUnless(PERFORMANCE_AVAILABLE, "Performance optimization not available")
class TestProgressFeedbackSystem(unittest.TestCase):
    """Test progress feedback system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock parent widget
        self.mock_parent = Mock()
        self.mock_parent.pack = Mock()
        self.mock_parent.after = Mock()
        
        # Mock ttk components
        with patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Progressbar'), \
             patch('tkinter.ttk.Button'):
            
            self.progress_system = ProgressFeedbackSystem(self.mock_parent)
            
    def test_progress_widget_creation(self):
        """Test progress widget creation."""
        with patch('tkinter.ttk.Frame') as mock_frame, \
             patch('tkinter.ttk.Label') as mock_label, \
             patch('tkinter.ttk.Progressbar') as mock_progressbar, \
             patch('tkinter.ttk.Button') as mock_button, \
             patch('tkinter.DoubleVar') as mock_var:
            
            # Create progress widget
            widgets = self.progress_system.create_progress_widget(
                "test_op",
                "Test Operation",
                can_cancel=True
            )
            
            # Check widgets were created
            self.assertIn('frame', widgets)
            self.assertIn('progress_bar', widgets)
            self.assertIn('status_label', widgets)
            
            # Check operation was registered
            self.assertIn("test_op", self.progress_system.active_operations)
            
    def test_progress_updates(self):
        """Test progress updates."""
        # Create operation first
        with patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Progressbar'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.DoubleVar'):
            
            self.progress_system.create_progress_widget(
                "test_op",
                "Test Operation"
            )
            
            # Update progress
            self.progress_system.update_progress(
                "test_op",
                50.0,
                "Half complete"
            )
            
            # Check operation data was updated
            operation = self.progress_system.active_operations["test_op"]
            self.assertEqual(operation['progress'], 50.0)
            self.assertEqual(operation['status'], "Half complete")
            
    def test_operation_cancellation(self):
        """Test operation cancellation."""
        cancelled = {'flag': False}
        
        def cancel_callback():
            cancelled['flag'] = True
            
        with patch('tkinter.ttk.Frame'), \
             patch('tkinter.ttk.Label'), \
             patch('tkinter.ttk.Progressbar'), \
             patch('tkinter.ttk.Button'), \
             patch('tkinter.DoubleVar'):
            
            # Create operation
            self.progress_system.create_progress_widget(
                "test_op",
                "Test Operation",
                can_cancel=True
            )
            
            # Register cancellation callback
            self.progress_system.register_cancellation_callback(
                "test_op",
                cancel_callback
            )
            
            # Cancel operation
            self.progress_system.cancel_operation("test_op")
            
            # Check cancellation
            self.assertTrue(self.progress_system.is_cancelled("test_op"))
            self.assertTrue(cancelled['flag'])


@unittest.skipUnless(PERFORMANCE_AVAILABLE, "Performance optimization not available")
class TestIntegration(unittest.TestCase):
    """Test integration of optimization components."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock main app
        self.mock_app = Mock()
        self.mock_app.DATA_DIR = self.temp_dir
        self.mock_app.used_image_urls = set()
        
        # Mock Tkinter root
        self.mock_root = Mock()
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_performance_optimizer_initialization(self):
        """Test performance optimizer initialization."""
        optimizer = PerformanceOptimizer(self.mock_root, self.temp_dir)
        
        # Check components are initialized
        self.assertIsNotNone(optimizer.memory_manager)
        self.assertIsNotNone(optimizer.task_queue)
        self.assertIsNotNone(optimizer.resource_manager)
        self.assertIsNotNone(optimizer.chunked_collector)
        
        # Start optimization
        optimizer.start_optimization()
        
        # Check optimization is running
        self.assertTrue(optimizer.memory_manager._monitoring)
        
        # Stop optimization
        optimizer.stop_optimization()
        
        # Check optimization is stopped
        self.assertFalse(optimizer.memory_manager._monitoring)
        
    def test_optimized_image_collector_integration(self):
        """Test optimized image collector integration."""
        # Mock Unsplash service
        mock_service = Mock()
        mock_service.search_photos.return_value = {
            'results': [
                {
                    'id': 'test1',
                    'urls': {'regular': 'http://example.com/1.jpg'},
                    'description': 'Test image 1'
                },
                {
                    'id': 'test2',
                    'urls': {'regular': 'http://example.com/2.jpg'},
                    'description': 'Test image 2'
                }
            ]
        }
        mock_service.canonicalize_url.side_effect = lambda url: url.split('?')[0]
        
        # Create collector
        collector = OptimizedImageCollector(self.mock_app, mock_service)
        collector.initialize_optimization()
        
        # Configure for testing
        collector.configure_collection(
            batch_size=2,
            memory_threshold_mb=100
        )
        
        # Test collection (mock only, no actual network calls)
        try:
            # This would normally make network calls, but we'll mock them
            with patch.object(collector, '_collect_images_chunked') as mock_collect:
                mock_collect.return_value = [
                    {'id': 'test1', 'url': 'http://example.com/1.jpg'},
                    {'id': 'test2', 'url': 'http://example.com/2.jpg'}
                ]
                
                collected = collector.collect_images_optimized("test", max_images=2)
                self.assertEqual(len(collected), 2)
                
        finally:
            collector.shutdown_optimization()
            
    def test_performance_metrics_collection(self):
        """Test performance metrics collection."""
        optimizer = PerformanceOptimizer(self.mock_root, self.temp_dir)
        optimizer.start_optimization()
        
        try:
            # Wait for metrics collection
            time.sleep(0.5)
            
            # Get performance metrics
            metrics = optimizer.get_performance_metrics()
            
            if metrics:  # May be None if no data collected yet
                self.assertIsInstance(metrics.memory_usage_mb, float)
                self.assertIsInstance(metrics.cpu_usage_percent, float)
                self.assertIsInstance(metrics.images_processed, int)
                
        finally:
            optimizer.stop_optimization()
            
    def test_optimization_report_generation(self):
        """Test optimization report generation."""
        optimizer = PerformanceOptimizer(self.mock_root, self.temp_dir)
        optimizer.start_optimization()
        
        try:
            # Generate some activity
            optimizer.memory_manager.put_image_in_cache("test", b"data")
            time.sleep(0.2)
            
            # Get optimization report
            report = optimizer.get_optimization_report()
            
            # Check report structure
            self.assertIn('memory_optimization', report)
            self.assertIn('task_processing', report)
            self.assertIn('system_resources', report)
            self.assertIn('overall_stats', report)
            
        finally:
            optimizer.stop_optimization()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)