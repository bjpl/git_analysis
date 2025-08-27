"""
Simple test script to verify the modular architecture components work correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing modular architecture imports...")
    
    tests = [
        # Services
        ("src.services.unsplash_service", "UnsplashService"),
        ("src.services.openai_service", "OpenAIService"),
        ("src.services.translation_service", "TranslationService"),
        
        # Models
        ("src.models.session", "SessionManager"),
        ("src.models.vocabulary", "VocabularyManager"),
        ("src.models.image", "ImageSearchState"),
        
        # Utils
        ("src.utils.cache", "ImageCache"),
        ("src.utils.file_manager", "FileManager"),
        
        # UI Components (basic import test only - no GUI)
        ("src.ui.widgets.vocabulary_list", "VocabularyList"),
        ("src.ui.widgets.search_bar", "SearchBar"),
        ("src.ui.widgets.image_viewer", "ImageViewer"),
    ]
    
    passed = 0
    failed = 0
    
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✓ {module_name}.{class_name}")
            passed += 1
        except ImportError as e:
            print(f"✗ {module_name}.{class_name} - Import Error: {e}")
            failed += 1
        except AttributeError as e:
            print(f"✗ {module_name}.{class_name} - Class not found: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {module_name}.{class_name} - Unexpected error: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_basic_functionality():
    """Test basic functionality of core components without external dependencies."""
    print("\nTesting basic functionality...")
    
    try:
        # Test cache functionality
        from src.utils.cache import ImageCache
        cache = ImageCache(max_size=3)
        
        cache.cache_image("url1", b"image_data_1")
        cache.cache_image("url2", b"image_data_2")
        
        assert cache.get_image("url1") == b"image_data_1"
        assert cache.is_image_cached("url2") == True
        assert cache.is_image_cached("url3") == False
        
        print("✓ ImageCache functionality")
        
        # Test file manager
        from src.utils.file_manager import FileManager
        
        clean_name = FileManager.clean_filename("test<file>name.txt")
        assert "<" not in clean_name and ">" not in clean_name
        
        print("✓ FileManager functionality")
        
        # Test vocabulary model (without file operations)
        from src.models.vocabulary import VocabularyEntry
        
        entry = VocabularyEntry("hola", "hello", "greeting", "url", "context")
        row = entry.to_csv_row()
        assert len(row) == 6
        assert row[0] == "hola"
        assert row[1] == "hello"
        
        print("✓ VocabularyEntry functionality")
        
        # Test image search state
        from src.models.image import ImageSearchState
        
        state = ImageSearchState()
        state.current_query = "test"
        state.current_page = 1
        
        info = state.get_search_info()
        assert info['query'] == "test"
        assert info['page'] == 1
        
        print("✓ ImageSearchState functionality")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def test_architecture_structure():
    """Test that the directory structure is correct."""
    print("\nTesting architecture structure...")
    
    base_path = Path("src")
    expected_dirs = [
        base_path,
        base_path / "ui",
        base_path / "ui" / "widgets",
        base_path / "ui" / "dialogs",
        base_path / "services",
        base_path / "models",
        base_path / "utils",
    ]
    
    expected_files = [
        base_path / "__init__.py",
        base_path / "app.py",
        base_path / "ui" / "__init__.py",
        base_path / "ui" / "main_window.py",
        base_path / "services" / "unsplash_service.py",
        base_path / "models" / "session.py",
        base_path / "utils" / "cache.py",
    ]
    
    all_good = True
    
    for directory in expected_dirs:
        if directory.exists():
            print(f"✓ Directory exists: {directory}")
        else:
            print(f"✗ Directory missing: {directory}")
            all_good = False
    
    for file_path in expected_files:
        if file_path.exists():
            print(f"✓ File exists: {file_path}")
        else:
            print(f"✗ File missing: {file_path}")
            all_good = False
    
    return all_good


def main():
    """Run all tests."""
    print("Modular Architecture Test Suite")
    print("=" * 40)
    
    # Test structure
    structure_ok = test_architecture_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test basic functionality
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"Structure: {'PASS' if structure_ok else 'FAIL'}")
    print(f"Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"Functionality: {'PASS' if functionality_ok else 'FAIL'}")
    
    if structure_ok and imports_ok and functionality_ok:
        print("\n🎉 All tests passed! Modular architecture is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())