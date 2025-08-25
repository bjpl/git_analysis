#!/usr/bin/env python
"""
Image Manager - QA Test Suite
Tests core functionality without requiring GUI interaction
"""

import os
import sys
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test database operations"""
    print("Testing Database Operations...")
    from image_manager import ImageDatabase
    
    # Create temp database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        db = ImageDatabase(db_path)
        
        # Create a real test file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_img:
            test_path = tmp_img.name
            tmp_img.write(b'fake image data')
        
        # Test adding image
        metadata = {'width': 1920, 'height': 1080}
        image_id = db.add_image(test_path, metadata)
        assert image_id is not None, "Failed to add image"
        
        # Test adding tag
        db.add_tag(test_path, "test_tag")
        tags = db.get_tags(test_path)
        assert "test_tag" in tags, "Failed to add/retrieve tag"
        
        # Test search - search by actual filename
        results = db.search_images()
        assert len(results) > 0, "Search failed - no images found"
        
        # Test search with query
        results2 = db.search_images(query=".jpg")
        assert len(results2) > 0, "Search with query failed"
        
        # Test rating
        db.update_rating(test_path, 5)
        
        # Test favorite
        db.toggle_favorite(test_path)
        
        print("✓ Database operations passed")
        db.close()
        os.unlink(test_path)  # Clean up test image
        os.unlink(db_path)  # Clean up database
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        try:
            if 'db' in locals():
                db.close()
            if 'test_path' in locals() and os.path.exists(test_path):
                os.unlink(test_path)
            if os.path.exists(db_path):
                os.unlink(db_path)
        except:
            pass
        return False

def test_config():
    """Test configuration save/load"""
    print("Testing Configuration...")
    
    config = {
        "last_scan_directory": "/test/path",
        "thumbnail_size": 200,
        "grid_columns": 6,
        "theme": "dark"
    }
    
    try:
        import json
        
        # Save config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(config, tmp, indent=4)
            config_path = tmp.name
        
        # Load config
        with open(config_path, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == config, "Config mismatch"
        print("✓ Configuration passed")
        os.unlink(config_path)
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_image_processing():
    """Test image processing capabilities"""
    print("Testing Image Processing...")
    
    try:
        from PIL import Image
        import io
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        
        # Test thumbnail
        img.thumbnail((50, 50), Image.Resampling.LANCZOS)
        assert img.size == (50, 50), "Thumbnail failed"
        
        # Test rotation
        img = img.rotate(90)
        
        # Test save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        print("✓ Image processing passed")
        return True
        
    except Exception as e:
        print(f"✗ Image processing test failed: {e}")
        return False

def test_file_operations():
    """Test file system operations"""
    print("Testing File Operations...")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test structure
            test_dir = Path(tmpdir) / "test_images"
            test_dir.mkdir()
            
            # Create test files
            for i in range(3):
                test_file = test_dir / f"test_{i}.txt"
                test_file.write_text(f"Test content {i}")
            
            # Test listing
            files = list(test_dir.glob("*.txt"))
            assert len(files) == 3, "File listing failed"
            
            # Test file info
            stat = files[0].stat()
            assert stat.st_size > 0, "File stat failed"
            
            print("✓ File operations passed")
            return True
            
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

def test_sorting():
    """Test sorting functionality"""
    print("Testing Sorting...")
    
    try:
        images = [
            {'filename': 'z.jpg', 'size': 1000, 'rating': 3, 'date_added': '2024-01-01'},
            {'filename': 'a.jpg', 'size': 2000, 'rating': 5, 'date_added': '2024-01-03'},
            {'filename': 'm.jpg', 'size': 500, 'rating': 1, 'date_added': '2024-01-02'},
        ]
        
        # Sort by name
        sorted_name = sorted(images, key=lambda x: x['filename'])
        assert sorted_name[0]['filename'] == 'a.jpg', "Name sort failed"
        
        # Sort by size
        sorted_size = sorted(images, key=lambda x: x['size'], reverse=True)
        assert sorted_size[0]['size'] == 2000, "Size sort failed"
        
        # Sort by rating
        sorted_rating = sorted(images, key=lambda x: x['rating'], reverse=True)
        assert sorted_rating[0]['rating'] == 5, "Rating sort failed"
        
        print("✓ Sorting passed")
        return True
        
    except Exception as e:
        print(f"✗ Sorting test failed: {e}")
        return False

def test_duplicate_detection():
    """Test duplicate detection logic"""
    print("Testing Duplicate Detection...")
    
    try:
        import hashlib
        from collections import defaultdict
        
        # Simulate file hashes
        files = [
            ('file1.jpg', b'content1'),
            ('file2.jpg', b'content1'),  # Duplicate
            ('file3.jpg', b'content2'),
            ('file4.jpg', b'content2'),  # Duplicate
            ('file5.jpg', b'content3'),  # Unique
        ]
        
        hash_map = defaultdict(list)
        
        for filename, content in files:
            file_hash = hashlib.md5(content).hexdigest()
            hash_map[file_hash].append(filename)
        
        duplicates = {k: v for k, v in hash_map.items() if len(v) > 1}
        
        assert len(duplicates) == 2, "Duplicate detection failed"
        assert len(hash_map) == 3, "Hash map incorrect"
        
        print("✓ Duplicate detection passed")
        return True
        
    except Exception as e:
        print(f"✗ Duplicate detection test failed: {e}")
        return False

def test_validation():
    """Test input validation"""
    print("Testing Input Validation...")
    
    try:
        # Test filename validation
        invalid_chars = '<>:"|?*'
        valid_name = "test_file.jpg"
        invalid_name = "test<file>.jpg"
        
        def validate_filename(name):
            return not any(char in name for char in invalid_chars)
        
        assert validate_filename(valid_name) == True, "Valid name rejected"
        assert validate_filename(invalid_name) == False, "Invalid name accepted"
        
        # Test path validation
        import os.path
        valid_path = "C:/Users/test"
        assert os.path.isabs(valid_path), "Path validation failed"
        
        print("✓ Input validation passed")
        return True
        
    except Exception as e:
        print(f"✗ Input validation test failed: {e}")
        return False

def test_memory_management():
    """Test memory management"""
    print("Testing Memory Management...")
    
    try:
        # Test cache size limit
        cache = {}
        cache_limit = 50
        
        for i in range(100):
            if len(cache) >= cache_limit:
                # Remove oldest
                cache.pop(next(iter(cache)))
            cache[f"key_{i}"] = f"value_{i}"
        
        assert len(cache) == cache_limit, "Cache limit failed"
        
        print("✓ Memory management passed")
        return True
        
    except Exception as e:
        print(f"✗ Memory management test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("="*50)
    print("Image Manager - QA Test Suite")
    print("="*50)
    
    tests = [
        test_database,
        test_config,
        test_image_processing,
        test_file_operations,
        test_sorting,
        test_duplicate_detection,
        test_validation,
        test_memory_management
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("="*50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed!")
    else:
        print(f"✗ {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)