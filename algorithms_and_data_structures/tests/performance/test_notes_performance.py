#!/usr/bin/env python3
"""
Performance Tests for Notes System
Testing load times, auto-save performance, search response time, and memory usage
"""

import pytest
import tempfile
import os
import time
import threading
try:
    import memory_profiler
except ImportError:
    # Fallback for when memory_profiler is not available
    memory_profiler = None
    print("Warning: memory_profiler not installed. Memory profiling disabled.")
import psutil
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the classes under test
sys_path = Path(__file__).parent.parent.parent / "src"
import sys
sys.path.insert(0, str(sys_path))

from notes_manager import NotesManager
from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
from ui.formatter import TerminalFormatter


class TestNotesLoadTimePerformance:
    """Test load time performance with various data sizes"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def create_test_notes(self, manager, count, user_id=1):
        """Create test notes for performance testing"""
        note_ids = []
        for i in range(count):
            content = f"Performance test note {i} with sample content about algorithms and data structures. " * 5
            note_id = manager.save_note(
                user_id, i % 100 + 100, content,
                f"Module{i % 10}", f"Topic{i}", 
                [f"tag{i % 5}", "performance", "test"]
            )
            note_ids.append(note_id)
        return note_ids
    
    def test_initialization_performance(self, temp_db):
        """Test database initialization performance"""
        start_time = time.time()
        manager = NotesManager(temp_db)
        init_time = time.time() - start_time
        
        assert init_time < 0.5  # Should initialize in under 500ms
        print(f"Database initialization: {init_time:.4f}s")
    
    def test_bulk_creation_performance(self, temp_db):
        """Test performance of creating many notes"""
        manager = NotesManager(temp_db)
        
        # Test different batch sizes
        batch_sizes = [10, 100, 500, 1000]
        
        for batch_size in batch_sizes:
            start_time = time.time()
            note_ids = self.create_test_notes(manager, batch_size)
            creation_time = time.time() - start_time
            
            # Performance assertions
            assert len(note_ids) == batch_size
            assert creation_time < batch_size * 0.01  # Max 10ms per note
            
            notes_per_second = batch_size / creation_time if creation_time > 0 else float('inf')
            print(f"Created {batch_size} notes in {creation_time:.4f}s ({notes_per_second:.1f} notes/sec)")
            
            # Cleanup for next test
            for note_id in note_ids:
                manager.delete_note(note_id)
    
    def test_load_time_with_large_dataset(self, temp_db):
        """Test load time performance with large number of notes"""
        manager = NotesManager(temp_db)
        
        # Create large dataset
        large_count = 2000
        print(f"Creating {large_count} notes for load time testing...")
        self.create_test_notes(manager, large_count)
        
        # Test loading performance
        load_tests = [
            ("all_notes", lambda: manager.get_notes(1)),
            ("module_filter", lambda: manager.get_notes(1, module_name="Module1")),
            ("search_query", lambda: manager.get_notes(1, search_term="performance")),
            ("lesson_filter", lambda: manager.get_notes(1, lesson_id=150))
        ]
        
        for test_name, test_func in load_tests:
            # Warm up
            test_func()
            
            # Measure performance
            start_time = time.time()
            results = test_func()
            load_time = time.time() - start_time
            
            # Performance assertions
            assert load_time < 2.0  # Should load in under 2 seconds
            assert isinstance(results, list)
            
            print(f"{test_name}: {len(results)} results in {load_time:.4f}s")
    
    def test_concurrent_load_performance(self, temp_db):
        """Test performance under concurrent access"""
        manager = NotesManager(temp_db)
        
        # Create test dataset
        self.create_test_notes(manager, 100)
        
        def concurrent_load_test(thread_id):
            """Load test function for each thread"""
            thread_manager = NotesManager(temp_db)
            start_time = time.time()
            
            # Perform multiple operations
            for _ in range(10):
                notes = thread_manager.get_notes(1)
                search_results = thread_manager.get_notes(1, search_term="performance")
            
            return time.time() - start_time
        
        # Run concurrent tests
        num_threads = 5
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(concurrent_load_test, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        avg_time = sum(results) / len(results)
        max_time = max(results)
        
        assert avg_time < 5.0  # Average should be under 5 seconds
        assert max_time < 10.0  # Worst case under 10 seconds
        
        print(f"Concurrent load test - Avg: {avg_time:.4f}s, Max: {max_time:.4f}s")


class TestAutoSavePerformance:
    """Test auto-save performance and efficiency"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def test_save_operation_performance(self, temp_db):
        """Test individual save operation performance"""
        manager = NotesManager(temp_db)
        
        # Test different content sizes
        content_sizes = [
            ("small", "Small note content"),
            ("medium", "Medium note content " * 100),
            ("large", "Large note content " * 1000),
            ("xlarge", "Extra large note content " * 5000)
        ]
        
        for size_name, content in content_sizes:
            start_time = time.time()
            note_id = manager.save_note(1, None, content, "Module", "Topic", ["test"])
            save_time = time.time() - start_time
            
            # Performance assertions based on content size
            if size_name == "small":
                assert save_time < 0.01  # 10ms for small notes
            elif size_name == "medium":
                assert save_time < 0.05  # 50ms for medium notes
            elif size_name == "large":
                assert save_time < 0.2   # 200ms for large notes
            else:  # xlarge
                assert save_time < 1.0   # 1s for extra large notes
            
            print(f"{size_name} note ({len(content)} chars): {save_time:.4f}s")
            
            # Verify note was saved correctly
            notes = manager.get_notes(1)
            saved_note = next(note for note in notes if note['id'] == note_id)
            assert len(saved_note['content']) == len(content)
    
    def test_update_operation_performance(self, temp_db):
        """Test note update performance"""
        manager = NotesManager(temp_db)
        
        # Create initial note
        note_id = manager.save_note(1, None, "Initial content", "Module", "Topic")
        
        # Test multiple updates
        update_count = 50
        start_time = time.time()
        
        for i in range(update_count):
            updated_content = f"Updated content iteration {i} " * (i + 1)
            manager.update_note(note_id, updated_content, [f"update{i}"])
        
        total_update_time = time.time() - start_time
        avg_update_time = total_update_time / update_count
        
        assert avg_update_time < 0.05  # Average update under 50ms
        assert total_update_time < 5.0  # Total under 5 seconds
        
        print(f"{update_count} updates: {total_update_time:.4f}s (avg: {avg_update_time:.4f}s)")
    
    def test_batch_save_performance(self, temp_db):
        """Test batch save operations performance"""
        manager = NotesManager(temp_db)
        
        # Test batch sizes
        batch_sizes = [10, 50, 100, 200]
        
        for batch_size in batch_sizes:
            start_time = time.time()
            
            # Create batch of notes
            for i in range(batch_size):
                content = f"Batch note {i} content"
                manager.save_note(1, None, content, f"Module{i%5}", f"Topic{i}", [f"batch{i}"])
            
            batch_time = time.time() - start_time
            notes_per_second = batch_size / batch_time
            
            assert batch_time < batch_size * 0.02  # Max 20ms per note in batch
            
            print(f"Batch {batch_size}: {batch_time:.4f}s ({notes_per_second:.1f} notes/sec)")
    
    def test_transaction_performance(self, temp_db):
        """Test database transaction performance"""
        manager = NotesManager(temp_db)
        
        # Test transaction efficiency by monitoring database locks
        transaction_count = 100
        start_time = time.time()
        
        # Simulate rapid-fire operations
        for i in range(transaction_count):
            note_id = manager.save_note(1, None, f"Transaction test {i}", "Module", "Topic")
            manager.update_note(note_id, f"Updated transaction test {i}", ["updated"])
            if i % 2 == 0:  # Delete half the notes
                manager.delete_note(note_id)
        
        total_time = time.time() - start_time
        operations_per_second = (transaction_count * 2.5) / total_time  # 2.5 ops per iteration
        
        assert total_time < 10.0  # Should complete in under 10 seconds
        
        print(f"Transaction performance: {operations_per_second:.1f} ops/sec")


class TestSearchResponseTime:
    """Test search functionality response times"""
    
    @pytest.fixture
    def populated_db(self):
        """Create database populated with search test data"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        manager = NotesManager(path)
        
        # Create diverse dataset for search testing
        search_terms = [
            "algorithm", "data structure", "performance", "complexity", "optimization",
            "binary search", "linear search", "sorting", "tree", "graph", "array", "list"
        ]
        
        modules = ["Algorithms", "Data Structures", "Mathematics", "Programming", "Theory"]
        
        for i in range(1000):
            content = f"Note {i}: " + " ".join(search_terms[i % len(search_terms)]) * 3
            module = modules[i % len(modules)]
            topic = f"Topic {i % 50}"
            tags = [search_terms[j % len(search_terms)] for j in range(i % 5 + 1)]
            
            manager.save_note(1, i % 100 + 100, content, module, topic, tags)
        
        yield path, manager
        
        if os.path.exists(path):
            os.unlink(path)
    
    def test_content_search_performance(self, populated_db):
        """Test content search response times"""
        db_path, manager = populated_db
        
        search_queries = [
            "algorithm", "binary", "performance", "data", "complexity",
            "search optimization", "tree structure", "algorithm performance"
        ]
        
        for query in search_queries:
            # Warm up
            manager.get_notes(1, search_term=query)
            
            # Measure search time
            start_time = time.time()
            results = manager.get_notes(1, search_term=query)
            search_time = time.time() - start_time
            
            # Performance assertions
            assert search_time < 0.5  # Search should complete in under 500ms
            assert len(results) > 0    # Should find some results
            
            print(f"Search '{query}': {len(results)} results in {search_time:.4f}s")
    
    def test_filtered_search_performance(self, populated_db):
        """Test filtered search performance"""
        db_path, manager = populated_db
        
        filter_tests = [
            ("module_filter", {"module_name": "Algorithms"}),
            ("lesson_filter", {"lesson_id": 150}),
            ("combined_filter", {"module_name": "Data Structures", "search_term": "tree"})
        ]
        
        for test_name, filters in filter_tests:
            start_time = time.time()
            results = manager.get_notes(1, **filters)
            filter_time = time.time() - start_time
            
            assert filter_time < 1.0  # Filtered search under 1 second
            
            print(f"{test_name}: {len(results)} results in {filter_time:.4f}s")
    
    def test_complex_search_performance(self, populated_db):
        """Test complex search queries performance"""
        db_path, manager = populated_db
        
        # Test searches that might be computationally expensive
        complex_queries = [
            "algorithm data structure performance",  # Multiple terms
            "a",  # Very short query (might match many)
            "xyz",  # Query with no results
            "binary search optimization complexity"  # Long query
        ]
        
        for query in complex_queries:
            start_time = time.time()
            results = manager.get_notes(1, search_term=query)
            search_time = time.time() - start_time
            
            assert search_time < 2.0  # Even complex searches should be fast
            
            print(f"Complex search '{query}': {len(results)} results in {search_time:.4f}s")
    
    def test_concurrent_search_performance(self, populated_db):
        """Test search performance under concurrent load"""
        db_path, manager = populated_db
        
        def concurrent_search(thread_id):
            """Search function for concurrent testing"""
            thread_manager = NotesManager(db_path)
            queries = ["algorithm", "data", "performance", "binary", "tree"]
            
            start_time = time.time()
            for query in queries:
                results = thread_manager.get_notes(1, search_term=query)
                assert len(results) > 0
            
            return time.time() - start_time
        
        # Run concurrent searches
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(concurrent_search, i) for i in range(num_threads)]
            results = [future.result() for future in as_completed(futures)]
        
        avg_time = sum(results) / len(results)
        max_time = max(results)
        
        assert avg_time < 5.0   # Average concurrent search time
        assert max_time < 10.0  # Worst case concurrent search time
        
        print(f"Concurrent search - Avg: {avg_time:.4f}s, Max: {max_time:.4f}s")


class TestMemoryUsageMonitoring:
    """Test memory usage characteristics"""
    
    @pytest.fixture
    def temp_db(self):
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    def test_baseline_memory_usage(self, temp_db):
        """Test baseline memory usage of empty notes system"""
        baseline_memory = self.get_memory_usage()
        
        # Create notes manager
        manager = NotesManager(temp_db)
        
        after_init_memory = self.get_memory_usage()
        init_overhead = after_init_memory - baseline_memory
        
        # Initialization should not use excessive memory
        assert init_overhead < 50  # Less than 50MB overhead
        
        print(f"Initialization memory overhead: {init_overhead:.1f}MB")
    
    def test_memory_usage_with_notes(self, temp_db):
        """Test memory usage as notes are added"""
        manager = NotesManager(temp_db)
        baseline_memory = self.get_memory_usage()
        
        # Add notes in batches and monitor memory
        batch_sizes = [100, 500, 1000, 2000]
        
        for batch_size in batch_sizes:
            # Create batch of notes
            for i in range(batch_size):
                content = f"Memory test note {i} " * 50  # ~1KB per note
                manager.save_note(1, None, content, "Module", "Topic", ["memory", "test"])
            
            current_memory = self.get_memory_usage()
            memory_increase = current_memory - baseline_memory
            
            # Memory should scale reasonably with data
            expected_data_size = batch_size * 1  # Approximately 1KB per note
            memory_efficiency = expected_data_size / memory_increase if memory_increase > 0 else 0
            
            print(f"{batch_size} notes: {memory_increase:.1f}MB ({memory_efficiency:.2f} efficiency)")
            
            # Memory usage should not be excessive (allowing for overhead)
            assert memory_increase < batch_size * 0.01  # Max 10KB overhead per note
    
    def test_memory_cleanup_after_operations(self, temp_db):
        """Test memory cleanup after various operations"""
        manager = NotesManager(temp_db)
        baseline_memory = self.get_memory_usage()
        
        # Create and delete many notes
        note_ids = []
        for i in range(500):
            content = f"Cleanup test note {i} " * 100
            note_id = manager.save_note(1, None, content, "Module", "Topic")
            note_ids.append(note_id)
        
        peak_memory = self.get_memory_usage()
        
        # Delete all notes
        for note_id in note_ids:
            manager.delete_note(note_id)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = self.get_memory_usage()
        
        # Memory should be mostly reclaimed
        memory_leaked = final_memory - baseline_memory
        assert memory_leaked < 20  # Less than 20MB should remain
        
        print(f"Memory usage - Baseline: {baseline_memory:.1f}MB, Peak: {peak_memory:.1f}MB, Final: {final_memory:.1f}MB")
        print(f"Memory leaked: {memory_leaked:.1f}MB")
    
    def test_memory_usage_ui_notes(self):
        """Test memory usage of UI notes system"""
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            formatter = TerminalFormatter()
            ui_manager = UINotesManager(formatter, temp_dir)
            
            baseline_memory = self.get_memory_usage()
            
            # Create rich notes with formatting
            for i in range(200):
                note = RichNote(
                    f"ui_note_{i}", f"UI Note {i}",
                    f"**Rich content {i}** with *formatting* and `code` elements. " * 20,
                    NoteType.CONCEPT, Priority.MEDIUM, [f"ui{i}", "rich", "formatting"]
                )
                ui_manager.notes[note.id] = note
                ui_manager._update_indices(note)
            
            peak_memory = self.get_memory_usage()
            memory_increase = peak_memory - baseline_memory
            
            # UI notes may use more memory due to formatting and indices
            assert memory_increase < 100  # Should be under 100MB for 200 notes
            
            print(f"UI notes memory usage: {memory_increase:.1f}MB for 200 rich notes")
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_leak_detection(self, temp_db):
        """Test for memory leaks during extended operations"""
        manager = NotesManager(temp_db)
        
        initial_memory = self.get_memory_usage()
        
        # Perform many operations in a loop
        for cycle in range(10):
            cycle_start_memory = self.get_memory_usage()
            
            # Create, search, update, and delete notes
            note_ids = []
            for i in range(50):
                content = f"Cycle {cycle} note {i}"
                note_id = manager.save_note(1, None, content, "Module", f"Topic{i}")
                note_ids.append(note_id)
            
            # Search operations
            manager.get_notes(1, search_term="Cycle")
            manager.get_notes(1, module_name="Module")
            
            # Update operations
            for note_id in note_ids[:25]:
                manager.update_note(note_id, f"Updated cycle {cycle}", ["updated"])
            
            # Delete operations
            for note_id in note_ids:
                manager.delete_note(note_id)
            
            # Check memory after cycle
            cycle_end_memory = self.get_memory_usage()
            cycle_memory_change = cycle_end_memory - cycle_start_memory
            
            print(f"Cycle {cycle}: memory change {cycle_memory_change:.1f}MB")
            
            # Memory should not consistently increase
            assert cycle_memory_change < 5  # Less than 5MB per cycle
        
        final_memory = self.get_memory_usage()
        total_memory_change = final_memory - initial_memory
        
        # Total memory increase should be minimal
        assert total_memory_change < 30  # Less than 30MB total increase
        
        print(f"Total memory change after leak test: {total_memory_change:.1f}MB")


class TestUIPerformance:
    """Test UI-specific performance characteristics"""
    
    @pytest.fixture
    def temp_notes_dir(self):
        import tempfile
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_rich_formatting_performance(self, temp_notes_dir):
        """Test rich text formatting performance"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Test different complexity levels of formatting
        formatting_tests = [
            ("simple", "Simple **bold** and *italic* text"),
            ("medium", "**Bold** *italic* `code` # Header\n- List item 1\n- List item 2"),
            ("complex", "# Main Header\n## Sub Header\n**Bold text** with *italic* and `code`.\n\n- List item 1\n- List item 2\n\n1. Numbered item\n2. Another numbered item\n\n```\nCode block\n```")
        ]
        
        for test_name, content in formatting_tests:
            start_time = time.time()
            
            # Create and format 100 notes
            for i in range(100):
                note = RichNote(
                    f"{test_name}_{i}", f"{test_name.title()} Note {i}",
                    content, NoteType.CONCEPT, Priority.MEDIUM, [test_name]
                )
                # Formatting happens in __post_init__
                ui_manager.notes[note.id] = note
            
            format_time = time.time() - start_time
            notes_per_second = 100 / format_time
            
            assert format_time < 2.0  # Should format 100 notes in under 2 seconds
            
            print(f"{test_name} formatting: {format_time:.4f}s ({notes_per_second:.1f} notes/sec)")
    
    def test_search_indexing_performance(self, temp_notes_dir):
        """Test search indexing performance"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Create notes and measure indexing time
        start_time = time.time()
        
        for i in range(500):
            note = RichNote(
                f"index_{i}", f"Index Note {i}",
                f"Content for indexing test {i} with various tags and topics",
                NoteType.CONCEPT, Priority.MEDIUM, [f"tag{j}" for j in range(i % 5 + 1)]
            )
            note.topic = f"Topic {i % 20}"
            
            ui_manager.notes[note.id] = note
            ui_manager._update_indices(note)
        
        indexing_time = time.time() - start_time
        notes_per_second = 500 / indexing_time
        
        assert indexing_time < 5.0  # Should index 500 notes in under 5 seconds
        
        print(f"Indexing performance: {indexing_time:.4f}s ({notes_per_second:.1f} notes/sec)")
        
        # Verify indices were built correctly
        assert len(ui_manager.tags_index) > 0
        assert len(ui_manager.topics_index) > 0
    
    def test_file_io_performance(self, temp_notes_dir):
        """Test file I/O performance for UI notes"""
        formatter = TerminalFormatter()
        ui_manager = UINotesManager(formatter, temp_notes_dir)
        
        # Create test notes
        for i in range(100):
            note = RichNote(
                f"io_test_{i}", f"I/O Test Note {i}",
                f"File I/O performance test content {i} " * 50,
                NoteType.CONCEPT, Priority.MEDIUM, [f"io{i}"]
            )
            ui_manager.notes[note.id] = note
        
        # Test save performance
        start_time = time.time()
        ui_manager.save_notes()
        save_time = time.time() - start_time
        
        assert save_time < 1.0  # Should save in under 1 second
        
        # Test load performance
        new_manager = UINotesManager(formatter, temp_notes_dir)
        
        start_time = time.time()
        new_manager.load_notes()
        load_time = time.time() - start_time
        
        assert load_time < 2.0  # Should load in under 2 seconds
        assert len(new_manager.notes) == 100
        
        print(f"File I/O - Save: {save_time:.4f}s, Load: {load_time:.4f}s")


if __name__ == '__main__':
    # Run performance tests with detailed output
    pytest.main([__file__, '-v', '-s', '--tb=short'])
