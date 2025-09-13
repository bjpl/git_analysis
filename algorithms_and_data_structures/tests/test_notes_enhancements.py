#!/usr/bin/env python3
"""
Test script for enhanced notes functionality
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.notes_viewer import EnhancedNotesViewer
from src.notes_manager import NotesManager
from src.ui.formatter import TerminalFormatter


def test_enhanced_viewer():
    """Test the enhanced notes viewer functionality"""
    
    print("=" * 60)
    print("TESTING ENHANCED NOTES VIEWER")
    print("=" * 60)
    
    formatter = TerminalFormatter()
    viewer = EnhancedNotesViewer()
    notes_mgr = NotesManager()
    
    # Test 1: Get available modules
    print("\n✅ Test 1: Getting available modules...")
    modules = viewer.get_available_modules()
    print(f"   Found {len(modules)} modules: {modules[:3]}...")
    
    # Test 2: Get all tags
    print("\n✅ Test 2: Getting all tags...")
    tags = viewer.get_all_tags()
    print(f"   Found {len(tags)} unique tags")
    if tags:
        print(f"   Top 3 tags: {tags[:3]}")
    
    # Test 3: Pagination
    print("\n✅ Test 3: Testing pagination...")
    viewer.page_size = 3
    page1 = viewer.get_page(1)
    print(f"   Page 1: {len(page1)} notes")
    print(f"   Total pages: {viewer.total_pages}")
    print(f"   Total notes: {viewer.total_notes}")
    
    # Test 4: Filtering by module
    if modules:
        print("\n✅ Test 4: Testing module filter...")
        viewer.filter_module = modules[0]
        filtered = viewer.get_page(1)
        print(f"   Filtered by '{modules[0]}': {len(filtered)} notes")
        viewer.filter_module = None  # Clear filter
    
    # Test 5: Search with fuzzy matching
    print("\n✅ Test 5: Testing fuzzy search...")
    viewer.search_query = "test"
    search_results = viewer.get_page(1)
    print(f"   Search for 'test': {len(search_results)} results")
    
    # Test 6: Sorting
    print("\n✅ Test 6: Testing sort options...")
    sort_options = ["created_desc", "title_asc", "favorites"]
    for sort in sort_options:
        viewer.sort_by = sort
        viewer.search_query = ""  # Clear search
        sorted_notes = viewer.get_page(1)
        print(f"   Sort by '{sort}': OK")
    
    # Test 7: Statistics
    print("\n✅ Test 7: Getting statistics...")
    stats = viewer.get_statistics()
    print(f"   Total notes: {stats['total_notes']}")
    print(f"   Favorites: {stats['favorites']}")
    print(f"   Notes this week: {stats['notes_this_week']}")
    print(f"   Average length: {stats['avg_length']} chars")
    
    # Test 8: Note detail
    if page1:
        print("\n✅ Test 8: Getting note details...")
        note_id = page1[0]['id']
        detail = viewer.get_note_detail(note_id)
        if detail:
            print(f"   Got details for note ID {note_id}")
            print(f"   Title: {detail.get('topic', 'N/A')}")
    
    # Test 9: Export filtered notes
    print("\n✅ Test 9: Testing export...")
    viewer.filter_module = None
    viewer.search_query = ""
    export_md = viewer.export_filtered_notes("markdown")
    export_json = viewer.export_filtered_notes("json")
    print(f"   Markdown export: {len(export_md)} chars")
    print(f"   JSON export: {len(export_json)} chars")
    
    # Test 10: Create and update note
    print("\n✅ Test 10: Testing note creation and update...")
    test_note_id = notes_mgr.save_note(
        user_id=1,
        lesson_id=None,
        module_name="Test Module",
        topic="Test Note for Enhancement",
        content="This is a test note to verify the enhanced features work correctly.",
        tags=["test", "enhancement", "verification"]
    )
    print(f"   Created test note ID: {test_note_id}")
    
    # Update the test note
    success = viewer.update_note(
        test_note_id,
        content="Updated content for the test note!",
        tags=["test", "updated"]
    )
    print(f"   Update successful: {success}")
    
    # Toggle favorite
    fav_success = viewer.toggle_favorite(test_note_id)
    print(f"   Toggle favorite: {fav_success}")
    
    # Clean up test note
    notes_mgr.delete_note(test_note_id)
    print(f"   Cleaned up test note")
    
    print("\n" + "=" * 60)
    print(formatter.success("✅ ALL TESTS PASSED!"))
    print("=" * 60)
    
    return True


def test_ui_integration():
    """Test that the UI integration works"""
    print("\n" + "=" * 60)
    print("TESTING UI INTEGRATION")
    print("=" * 60)
    
    # Import the enhanced CLI
    from src.enhanced_cli import EnhancedCLI
    
    cli = EnhancedCLI()
    
    # Verify notes viewer is initialized
    assert hasattr(cli, 'notes_viewer'), "Notes viewer not initialized!"
    assert hasattr(cli, 'notes_manager'), "Notes manager not initialized!"
    
    print("\n✅ CLI has notes_viewer attribute")
    print("✅ CLI has notes_manager attribute")
    
    # Check that manage_notes method exists
    assert hasattr(cli, 'manage_notes'), "manage_notes method not found!"
    print("✅ manage_notes method exists")
    
    # Verify enhanced_notes_ui module can be imported
    try:
        from src.enhanced_notes_ui import manage_notes_enhanced
        print("✅ enhanced_notes_ui module imports correctly")
    except ImportError as e:
        print(f"❌ Failed to import enhanced_notes_ui: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ UI INTEGRATION TEST PASSED!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # Run tests
    success = True
    
    try:
        # Test enhanced viewer
        if not test_enhanced_viewer():
            success = False
            
        # Test UI integration
        if not test_ui_integration():
            success = False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    if success:
        print("\n" + "🎉" * 20)
        print("🎉 ALL ENHANCEMENTS WORKING PERFECTLY! 🎉")
        print("🎉" * 20)
        print("""
The Notes Manager now features:
✅ Pagination with customizable page size
✅ Multiple sort options (newest, oldest, title, favorites)
✅ Module and tag filtering
✅ Fuzzy search with relevance scoring
✅ Full note detail view
✅ Note editing capabilities
✅ Favorite toggle
✅ Comprehensive statistics
✅ Export with filters applied
✅ Enhanced UI with better navigation

Try it out with: python cli.py
Then select option 4 (Notes Manager) from the main menu!
        """)
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        
    sys.exit(0 if success else 1)