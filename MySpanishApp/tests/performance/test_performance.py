# File: tests/performance/test_performance.py
"""
Performance tests for SpanishMaster application.
Tests load handling, response times, and resource usage.
"""

import pytest
import time
import psutil
import gc
import threading
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from models.database import Database
from models.session_model import SessionModel
from models.vocab_model import VocabModel
from models.grammar_model import GrammarModel


class TestDatabasePerformance:
    """Test database operation performance."""
    
    @pytest.mark.performance
    def test_database_connection_performance(self, performance_timer):
        """Test database connection establishment time."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            performance_timer.start()
            
            # Test multiple connections
            connections = []
            for _ in range(10):
                db = Database(tmp_path)
                db.init_db()
                connections.append(db)
            
            connection_time = performance_timer.stop()
            
            # Close all connections
            for db in connections:
                db.close()
            
            # Should establish 10 connections quickly (< 2 seconds)
            assert connection_time < 2.0
            
            print(f"10 database connections established in {connection_time:.3f} seconds")
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @pytest.mark.performance
    def test_bulk_session_creation_performance(self, temp_db, sample_teacher, performance_timer):
        """Test performance of creating many sessions."""
        session_model = SessionModel(temp_db)
        
        performance_timer.start()
        
        # Create 1000 sessions
        session_ids = []
        for i in range(1000):
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date=f"2025-{4 + i // 100:02d}-{10 + i % 30:02d}",
                start_time="17:00",
                duration="1h"
            )
            session_ids.append(session_id)
        
        creation_time = performance_timer.stop()
        
        # Verify all sessions were created
        assert len(session_ids) == 1000
        assert all(sid is not None for sid in session_ids)
        
        # Should create 1000 sessions in reasonable time (< 10 seconds)
        assert creation_time < 10.0
        
        print(f"Created 1000 sessions in {creation_time:.3f} seconds ({1000/creation_time:.1f} sessions/sec)")
    
    @pytest.mark.performance
    def test_bulk_vocabulary_insertion_performance(self, temp_db, sample_session, performance_timer):
        """Test performance of inserting many vocabulary entries."""
        vocab_model = VocabModel(temp_db)
        
        # Generate test vocabulary data
        test_vocab = []
        for i in range(5000):
            test_vocab.append({
                "word_phrase": f"palabra_{i}",
                "translation": f"word_{i}",
                "context_notes": f"Context for word number {i}"
            })
        
        performance_timer.start()
        
        vocab_ids = []
        for vocab_data in test_vocab:
            vocab_id = vocab_model.add_vocab(
                session_id=sample_session,
                **vocab_data
            )
            vocab_ids.append(vocab_id)
        
        insertion_time = performance_timer.stop()
        
        # Verify all vocabulary was inserted
        assert len(vocab_ids) == 5000
        assert all(vid is not None for vid in vocab_ids)
        
        # Should insert 5000 vocab entries in reasonable time (< 15 seconds)
        assert insertion_time < 15.0
        
        print(f"Inserted 5000 vocab entries in {insertion_time:.3f} seconds ({5000/insertion_time:.1f} entries/sec)")
    
    @pytest.mark.performance
    def test_large_dataset_query_performance(self, performance_timer):
        """Test query performance with large dataset."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Setup large dataset
            db = Database(tmp_path)
            db.init_db()
            
            cursor = db.conn.cursor()
            cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Performance Teacher",))
            db.conn.commit()
            teacher_id = cursor.lastrowid
            
            session_model = SessionModel(db)
            vocab_model = VocabModel(db)
            
            # Create many sessions with vocabulary
            session_ids = []
            for i in range(100):  # 100 sessions
                session_id = session_model.create_session(
                    teacher_id=teacher_id,
                    session_date=f"2025-{4 + i // 30:02d}-{10 + i % 30:02d}",
                    start_time="17:00",
                    duration="1h"
                )
                session_ids.append(session_id)
                
                # Add 50 vocabulary items per session
                for j in range(50):
                    vocab_model.add_vocab(
                        session_id=session_id,
                        word_phrase=f"performance_word_{i}_{j}",
                        translation=f"performance_translation_{i}_{j}"
                    )
            
            # Test query performance
            performance_timer.start()
            
            # Query all sessions
            all_sessions = session_model.get_sessions()
            
            # Query vocabulary for each session
            total_vocab = 0
            for session_id in session_ids:
                vocab_list = vocab_model.get_vocab_for_session(session_id)
                total_vocab += len(vocab_list)
            
            query_time = performance_timer.stop()
            
            # Verify data integrity
            assert len(all_sessions) == 100
            assert total_vocab == 5000  # 100 sessions * 50 vocab each
            
            # Should query large dataset efficiently (< 5 seconds)
            assert query_time < 5.0
            
            print(f"Queried large dataset (100 sessions, 5000 vocab) in {query_time:.3f} seconds")
            
            db.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @pytest.mark.performance
    def test_concurrent_database_operations(self, performance_timer):
        """Test concurrent database operations performance."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Setup
            db = Database(tmp_path)
            db.init_db()
            
            cursor = db.conn.cursor()
            cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Concurrent Teacher",))
            db.conn.commit()
            teacher_id = cursor.lastrowid
            db.close()
            
            def worker_operation(worker_id):
                """Worker function for concurrent operations."""
                worker_db = Database(tmp_path)
                session_model = SessionModel(worker_db)
                vocab_model = VocabModel(worker_db)
                
                results = []
                for i in range(10):  # Each worker creates 10 sessions
                    try:
                        session_id = session_model.create_session(
                            teacher_id=teacher_id,
                            session_date=f"2025-04-{10 + worker_id}-{i:02d}",
                            start_time="17:00",
                            duration="1h"
                        )
                        
                        if session_id:
                            # Add vocabulary to each session
                            vocab_id = vocab_model.add_vocab(
                                session_id=session_id,
                                word_phrase=f"concurrent_word_{worker_id}_{i}",
                                translation=f"concurrent_translation_{worker_id}_{i}"
                            )
                            results.append((session_id, vocab_id))
                        
                        time.sleep(0.01)  # Small delay to simulate real usage
                    except Exception as e:
                        print(f"Worker {worker_id} error: {e}")
                
                worker_db.close()
                return results
            
            performance_timer.start()
            
            # Run concurrent operations
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(worker_operation, i) for i in range(10)]
                
                all_results = []
                for future in as_completed(futures):
                    results = future.result()
                    all_results.extend(results)
            
            concurrent_time = performance_timer.stop()
            
            # Verify results
            successful_operations = len([r for r in all_results if r[0] is not None and r[1] is not None])
            
            # Should handle concurrent operations reasonably well
            assert successful_operations >= 80  # At least 80% success rate
            assert concurrent_time < 10.0
            
            print(f"Completed {successful_operations} concurrent operations in {concurrent_time:.3f} seconds")
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestMemoryPerformance:
    """Test memory usage and performance."""
    
    @pytest.mark.performance
    def test_memory_usage_bulk_operations(self, temp_db, sample_teacher):
        """Test memory usage during bulk operations."""
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        # Perform bulk operations
        session_ids = []
        for i in range(500):
            session_id = session_model.create_session(
                teacher_id=sample_teacher,
                session_date=f"2025-{4 + i // 100:02d}-{10 + i % 30:02d}",
                start_time="17:00",
                duration="1h"
            )
            session_ids.append(session_id)
            
            # Add vocabulary to each session
            for j in range(10):
                vocab_model.add_vocab(
                    session_id=session_id,
                    word_phrase=f"memory_test_word_{i}_{j}",
                    translation=f"memory_test_translation_{i}_{j}"
                )
        
        # Get peak memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Force garbage collection
        gc.collect()
        
        # Get memory usage after cleanup
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_after_cleanup = final_memory - initial_memory
        
        print(f"Memory usage - Initial: {initial_memory:.1f}MB, Peak: {peak_memory:.1f}MB, Final: {final_memory:.1f}MB")
        print(f"Memory increase - Peak: {memory_increase:.1f}MB, After cleanup: {memory_after_cleanup:.1f}MB")
        
        # Memory usage should be reasonable (< 100MB increase)
        assert memory_increase < 100.0
        
        # Memory should be released after operations (< 50MB permanent increase)
        assert memory_after_cleanup < 50.0
    
    @pytest.mark.performance
    def test_memory_leaks_repeated_operations(self, temp_db, sample_teacher):
        """Test for memory leaks during repeated operations."""
        process = psutil.Process()
        session_model = SessionModel(temp_db)
        vocab_model = VocabModel(temp_db)
        
        memory_samples = []
        
        for iteration in range(10):
            # Perform operations
            for i in range(50):
                session_id = session_model.create_session(
                    teacher_id=sample_teacher,
                    session_date=f"2025-04-{iteration:02d}-{i:02d}",
                    start_time="17:00",
                    duration="1h"
                )
                
                vocab_model.add_vocab(
                    session_id=session_id,
                    word_phrase=f"leak_test_{iteration}_{i}",
                    translation=f"leak_translation_{iteration}_{i}"
                )
            
            # Force garbage collection
            gc.collect()
            
            # Sample memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_samples.append(current_memory)
            
            # Clean up some data (simulate application lifecycle)
            sessions = session_model.get_sessions()
            for session in sessions[-25:]:  # Keep only recent sessions
                vocab_list = vocab_model.get_vocab_for_session(session['session_id'])
                for vocab in vocab_list:
                    vocab_model.delete_vocab(vocab['vocab_id'])
                session_model.delete_session(session['session_id'])
        
        # Analyze memory trend
        initial_memory = memory_samples[0]
        final_memory = memory_samples[-1]
        max_memory = max(memory_samples)
        
        memory_growth = final_memory - initial_memory
        
        print(f"Memory samples: {[f'{m:.1f}' for m in memory_samples]}")
        print(f"Memory growth over 10 iterations: {memory_growth:.1f}MB")
        
        # Memory growth should be minimal (< 20MB over 10 iterations)
        assert memory_growth < 20.0
        assert max_memory - initial_memory < 50.0


class TestUIPerformance:
    """Test UI performance characteristics."""
    
    @pytest.mark.performance
    @pytest.mark.gui
    def test_main_window_startup_performance(self, qt_app, performance_timer):
        """Test main window startup performance."""
        with patch('models.database.Database') as mock_db:
            performance_timer.start()
            
            from views.main_window import MainWindow
            window = MainWindow()
            window.show()
            
            # Process all pending events
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
            
            startup_time = performance_timer.stop()
            
            # UI should start quickly (< 3 seconds)
            assert startup_time < 3.0
            
            print(f"Main window startup time: {startup_time:.3f} seconds")
            
            window.close()
    
    @pytest.mark.performance
    @pytest.mark.gui
    def test_large_data_display_performance(self, qt_app, performance_timer):
        """Test UI performance when displaying large amounts of data."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Setup large dataset
            db = Database(tmp_path)
            db.init_db()
            
            cursor = db.conn.cursor()
            cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("UI Performance Teacher",))
            db.conn.commit()
            teacher_id = cursor.lastrowid
            
            session_model = SessionModel(db)
            vocab_model = VocabModel(db)
            
            # Create large dataset
            large_session_id = session_model.create_session(
                teacher_id=teacher_id,
                session_date="2025-04-10",
                start_time="17:00",
                duration="1h"
            )
            
            # Add many vocabulary items
            for i in range(1000):
                vocab_model.add_vocab(
                    session_id=large_session_id,
                    word_phrase=f"ui_performance_word_{i}",
                    translation=f"ui_performance_translation_{i}",
                    context_notes=f"Context notes for performance testing word {i}"
                )
            
            with patch('models.database.Database', return_value=db):
                performance_timer.start()
                
                from views.review_view import ReviewView
                review_view = ReviewView()
                
                # Load large dataset
                if hasattr(review_view, 'load_all_data'):
                    review_view.load_all_data()
                elif hasattr(review_view, 'load_statistics'):
                    review_view.load_statistics()
                
                # Process UI events
                from PyQt6.QtWidgets import QApplication
                QApplication.processEvents()
                
                load_time = performance_timer.stop()
                
                # UI should handle large data efficiently (< 5 seconds)
                assert load_time < 5.0
                
                print(f"Large data UI load time: {load_time:.3f} seconds")
            
            db.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @pytest.mark.performance
    @pytest.mark.gui
    def test_ui_responsiveness_under_load(self, qt_app, performance_timer):
        """Test UI responsiveness during background operations."""
        with patch('models.database.Database') as mock_db:
            from views.main_window import MainWindow
            window = MainWindow()
            window.show()
            
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            
            # Simulate background work
            def background_work():
                """Simulate CPU-intensive background work."""
                for i in range(1000000):
                    _ = i * i
            
            # Start background work in thread
            import threading
            background_thread = threading.Thread(target=background_work)
            
            performance_timer.start()
            background_thread.start()
            
            # Test UI responsiveness during background work
            ui_response_times = []
            for _ in range(10):
                ui_start = time.time()
                QApplication.processEvents()
                ui_end = time.time()
                ui_response_times.append(ui_end - ui_start)
                time.sleep(0.1)
            
            background_thread.join()
            total_time = performance_timer.stop()
            
            # UI should remain responsive (each processEvents < 0.1 seconds)
            max_response_time = max(ui_response_times)
            avg_response_time = sum(ui_response_times) / len(ui_response_times)
            
            assert max_response_time < 0.1
            assert avg_response_time < 0.05
            
            print(f"UI responsiveness - Max: {max_response_time:.4f}s, Avg: {avg_response_time:.4f}s")
            
            window.close()


class TestScalabilityPerformance:
    """Test application scalability characteristics."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_database_size_scalability(self, performance_timer):
        """Test performance as database size increases."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            db = Database(tmp_path)
            db.init_db()
            
            cursor = db.conn.cursor()
            cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Scalability Teacher",))
            db.conn.commit()
            teacher_id = cursor.lastrowid
            
            session_model = SessionModel(db)
            vocab_model = VocabModel(db)
            
            # Test performance at different database sizes
            size_tests = [100, 500, 1000, 2000]  # Number of sessions
            performance_results = []
            
            for target_size in size_tests:
                # Add sessions to reach target size
                current_sessions = len(session_model.get_sessions())
                sessions_to_add = target_size - current_sessions
                
                if sessions_to_add > 0:
                    for i in range(sessions_to_add):
                        session_id = session_model.create_session(
                            teacher_id=teacher_id,
                            session_date=f"2025-{4 + i // 100:02d}-{10 + i % 30:02d}",
                            start_time="17:00",
                            duration="1h"
                        )
                        
                        # Add vocabulary to each session
                        for j in range(5):
                            vocab_model.add_vocab(
                                session_id=session_id,
                                word_phrase=f"scalability_word_{i}_{j}",
                                translation=f"scalability_translation_{i}_{j}"
                            )
                
                # Test query performance at this size
                performance_timer.start()
                
                all_sessions = session_model.get_sessions()
                
                # Test vocabulary queries
                total_vocab = 0
                for session in all_sessions[:10]:  # Test first 10 sessions
                    vocab_list = vocab_model.get_vocab_for_session(session['session_id'])
                    total_vocab += len(vocab_list)
                
                query_time = performance_timer.stop()
                
                performance_results.append((target_size, query_time))
                
                print(f"Database size {target_size} sessions: query time {query_time:.3f}s")
            
            # Analyze scalability
            # Performance should not degrade dramatically with size
            first_time = performance_results[0][1]
            last_time = performance_results[-1][1]
            
            # Performance degradation should be reasonable (not more than 5x slower)
            performance_ratio = last_time / first_time
            assert performance_ratio < 5.0
            
            print(f"Performance scalability ratio (2000 vs 100 sessions): {performance_ratio:.2f}x")
            
            db.close()
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @pytest.mark.performance
    def test_concurrent_user_simulation(self, performance_timer):
        """Simulate multiple concurrent users."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Setup
            db = Database(tmp_path)
            db.init_db()
            
            cursor = db.conn.cursor()
            cursor.execute("INSERT INTO teachers (name) VALUES (?)", ("Concurrent User Teacher",))
            db.conn.commit()
            teacher_id = cursor.lastrowid
            db.close()
            
            def simulate_user_session(user_id):
                """Simulate a user session."""
                user_db = Database(tmp_path)
                session_model = SessionModel(user_db)
                vocab_model = VocabModel(user_db)
                
                operations = []
                
                try:
                    # User creates sessions
                    for i in range(5):
                        session_id = session_model.create_session(
                            teacher_id=teacher_id,
                            session_date=f"2025-04-{user_id:02d}-{i:02d}",
                            start_time=f"{17 + i % 3}:00",
                            duration="1h"
                        )
                        operations.append(f"session_{session_id}")
                        
                        # User adds vocabulary
                        for j in range(10):
                            vocab_id = vocab_model.add_vocab(
                                session_id=session_id,
                                word_phrase=f"user{user_id}_word_{i}_{j}",
                                translation=f"user{user_id}_trans_{i}_{j}"
                            )
                            operations.append(f"vocab_{vocab_id}")
                        
                        time.sleep(0.01)  # Simulate user think time
                    
                    # User queries their data
                    sessions = session_model.get_sessions()
                    for session in sessions[-5:]:  # Get recent sessions
                        vocab_list = vocab_model.get_vocab_for_session(session['session_id'])
                        operations.append(f"query_{len(vocab_list)}")
                
                except Exception as e:
                    operations.append(f"error_{str(e)}")
                
                finally:
                    user_db.close()
                
                return user_id, operations
            
            performance_timer.start()
            
            # Simulate 20 concurrent users
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(simulate_user_session, i) for i in range(20)]
                
                user_results = []
                for future in as_completed(futures):
                    user_id, operations = future.result()
                    user_results.append((user_id, operations))
            
            simulation_time = performance_timer.stop()
            
            # Analyze results
            total_operations = sum(len(ops) for _, ops in user_results)
            successful_users = len([ops for _, ops in user_results if not any('error_' in op for op in ops)])
            
            print(f"Concurrent user simulation - {successful_users}/20 users successful")
            print(f"Total operations: {total_operations} in {simulation_time:.3f} seconds")
            print(f"Operations per second: {total_operations / simulation_time:.1f}")
            
            # Most users should complete successfully
            assert successful_users >= 18  # At least 90% success rate
            assert simulation_time < 30.0  # Should complete in reasonable time
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


# Integration with pytest markers
pytestmark = pytest.mark.performance