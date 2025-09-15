#!/usr/bin/env python3
"""
Enhanced Notes UI - Advanced interactive notes management interface
"""

from typing import Optional, List, Dict
import os


def manage_notes_enhanced(cli_instance):
    """Enhanced notes management with pagination, filtering, and better UI"""
    
    viewer = cli_instance.notes_viewer
    formatter = cli_instance.formatter
    notes_mgr = cli_instance.notes_manager
    
    while True:
        # Clear screen for cleaner UI
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Show header with statistics
        stats = viewer.get_statistics()
        print(formatter.header("\n📝 NOTES MANAGER"))
        print("═" * 60)
        print(f"📚 Total Notes: {stats['total_notes']} | ")
        print(f"⭐ Favorites: {stats['favorites']} | ")
        print(f"📅 This Week: {stats['notes_this_week']} | ")
        print(f"📂 Modules: {stats['modules_count']}")
        print("═" * 60)
        
        # Show current filters if any
        if viewer.filter_module or viewer.filter_tags or viewer.search_query:
            print(formatter.warning("Active Filters:"))
            if viewer.filter_module:
                print(f"  Module: {viewer.filter_module}")
            if viewer.filter_tags:
                print(f"  Tags: {', '.join(viewer.filter_tags)}")
            if viewer.search_query:
                print(f"  Search: {viewer.search_query}")
            print()
        
        # Main menu
        print("\n1. 📖 Browse Notes (paginated)")
        print("2. 🔍 Search Notes (fuzzy)")
        print("3. ✏️ Add New Note")
        print("4. 🏷️ Filter by Module/Tags")
        print("5. 📊 View Statistics")
        print("6. 💾 Export Notes")
        print("7. 📥 Import Notes")
        print("8. ⚙️ Settings & Sort Options")
        print("9. 🔄 Clear Filters")
        print("0. ⬅️ Back to Main Menu")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            # Browse notes with pagination
            browse_notes_paginated(viewer, formatter, notes_mgr)
            
        elif choice == "2":
            # Advanced search with fuzzy matching
            search_notes_advanced(viewer, formatter)
            
        elif choice == "3":
            # Add new note with enhanced input
            add_note_enhanced(notes_mgr, formatter)
            
        elif choice == "4":
            # Filter interface
            apply_filters(viewer, formatter)
            
        elif choice == "5":
            # Show detailed statistics
            show_statistics(viewer, formatter)
            
        elif choice == "6":
            # Export with current filters
            export_notes_filtered(viewer, notes_mgr, formatter)
            
        elif choice == "7":
            # Import notes
            import_notes_enhanced(notes_mgr, formatter)
            
        elif choice == "8":
            # Settings and sort options
            configure_settings(viewer, formatter)
            
        elif choice == "9":
            # Clear all filters
            viewer.filter_module = None
            viewer.filter_tags = []
            viewer.search_query = ""
            viewer.sort_by = "created_desc"
            print(formatter.success("✅ All filters cleared!"))
            input("\nPress Enter to continue...")
            
        elif choice == "0":
            break
        else:
            print(formatter.error("Invalid choice. Please try again."))
            input("\nPress Enter to continue...")


def browse_notes_paginated(viewer, formatter, notes_mgr):
    """Browse notes with pagination and inline actions"""
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Get current page of notes
        notes = viewer.get_page()
        
        print(formatter.header(f"\n📖 BROWSING NOTES (Page {viewer.current_page}/{viewer.total_pages})"))
        print("═" * 60)
        
        if not notes:
            print(formatter.warning("No notes found with current filters."))
        else:
            # Display notes
            for idx, note in enumerate(notes, 1):
                # Note header
                fav_marker = "⭐ " if note.get('is_favorite') else ""
                note_title = note.get('topic', 'Untitled Note')
                print(f"\n{formatter.info(f'{fav_marker}[{idx}] {note_title}')}")
                
                # Metadata
                print(f"   📂 Module: {note.get('module_name', 'General')}")
                print(f"   📅 Created: {note['created_at'][:16]}")
                
                # Tags
                if note.get('tags'):
                    tags_str = ', '.join(f"#{tag}" for tag in note['tags'])
                    print(f"   🏷️ Tags: {tags_str}")
                
                # Content preview
                preview = viewer.format_note_preview(note, max_length=100)
                print(f"   📝 {preview}")
                print("   " + "─" * 56)
        
        # Pagination controls
        print(f"\n[Page {viewer.current_page}/{viewer.total_pages}] ", end="")
        print(f"Showing {len(notes)} of {viewer.total_notes} notes")
        print("\nActions:")
        print("  [n] Next page | [p] Previous page | [g] Go to page")
        print("  [1-5] View note details | [e] Edit note | [d] Delete note")
        print("  [f] Toggle favorite | [s] Change sort | [q] Back")
        
        action = input("\nAction: ").strip().lower()
        
        if action == 'n' and viewer.current_page < viewer.total_pages:
            viewer.current_page += 1
        elif action == 'p' and viewer.current_page > 1:
            viewer.current_page -= 1
        elif action == 'g':
            try:
                page = int(input("Go to page: "))
                if 1 <= page <= viewer.total_pages:
                    viewer.current_page = page
                else:
                    print(formatter.error(f"Page must be between 1 and {viewer.total_pages}"))
                    input("Press Enter...")
            except ValueError:
                print(formatter.error("Invalid page number"))
                input("Press Enter...")
        elif action.isdigit() and 1 <= int(action) <= len(notes):
            # View note details
            note_idx = int(action) - 1
            view_note_detail(notes[note_idx], viewer, formatter, notes_mgr)
        elif action == 'e':
            # Edit note
            note_num = input("Note number to edit: ")
            if note_num.isdigit() and 1 <= int(note_num) <= len(notes):
                edit_note(notes[int(note_num) - 1], viewer, formatter)
        elif action == 'd':
            # Delete note
            note_num = input("Note number to delete: ")
            if note_num.isdigit() and 1 <= int(note_num) <= len(notes):
                if input("Are you sure? (y/n): ").lower() == 'y':
                    notes_mgr.delete_note(notes[int(note_num) - 1]['id'])
                    print(formatter.success("✅ Note deleted!"))
                    input("Press Enter...")
        elif action == 'f':
            # Toggle favorite
            note_num = input("Note number to favorite/unfavorite: ")
            if note_num.isdigit() and 1 <= int(note_num) <= len(notes):
                viewer.toggle_favorite(notes[int(note_num) - 1]['id'])
                print(formatter.success("✅ Favorite toggled!"))
                input("Press Enter...")
        elif action == 's':
            # Change sort
            configure_sort(viewer, formatter)
        elif action == 'q':
            break


def view_note_detail(note, viewer, formatter, notes_mgr):
    """Display full note details"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Get full note details
    full_note = viewer.get_note_detail(note['id'])
    
    fav_marker = "⭐ " if full_note.get('is_favorite') else ""
    print(formatter.header(f"\n📝 {fav_marker}{full_note.get('topic', 'Untitled Note')}"))
    print("═" * 60)
    
    # Metadata
    print(f"📂 Module: {full_note.get('module_name', 'General')}")
    print(f"📅 Created: {full_note['created_at']}")
    print(f"🔄 Updated: {full_note['updated_at']}")
    
    if full_note.get('lesson_title'):
        print(f"📚 Lesson: {full_note['lesson_title']}")
    
    # Tags
    if full_note.get('tags'):
        tags_str = ', '.join(f"#{tag}" for tag in full_note['tags'])
        print(f"🏷️ Tags: {tags_str}")
    
    # Full content
    print("\n" + "─" * 60)
    print("\n" + full_note.get('content', ''))
    print("\n" + "─" * 60)
    
    # Actions
    print("\nActions:")
    print("  [e] Edit | [f] Toggle Favorite | [d] Delete | [b] Back")
    
    action = input("\nAction: ").strip().lower()
    
    if action == 'e':
        edit_note(full_note, viewer, formatter)
    elif action == 'f':
        viewer.toggle_favorite(full_note['id'])
        print(formatter.success("✅ Favorite toggled!"))
        input("Press Enter...")
    elif action == 'd':
        if input("Are you sure you want to delete? (y/n): ").lower() == 'y':
            notes_mgr.delete_note(full_note['id'])
            print(formatter.success("✅ Note deleted!"))
            input("Press Enter...")


def edit_note(note, viewer, formatter):
    """Edit an existing note"""
    print(formatter.header(f"\n✏️ EDIT NOTE"))
    print("Leave blank to keep current value")
    
    # Edit topic
    print(f"\nCurrent topic: {note.get('topic', '')}")
    new_topic = input("New topic (or Enter to keep): ").strip()
    
    # Edit content
    print(f"\nCurrent content preview: {note.get('content', '')[:100]}...")
    print("Enter new content (type END on new line to finish):")
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    new_content = "\n".join(lines) if lines else None
    
    # Edit tags
    current_tags = note.get('tags', [])
    print(f"\nCurrent tags: {', '.join(current_tags)}")
    new_tags_input = input("New tags (comma-separated, or Enter to keep): ").strip()
    new_tags = [t.strip() for t in new_tags_input.split(",")] if new_tags_input else None
    
    # Apply updates
    if new_topic or new_content or new_tags is not None:
        viewer.update_note(
            note['id'],
            content=new_content,
            topic=new_topic if new_topic else None,
            tags=new_tags
        )
        print(formatter.success("✅ Note updated successfully!"))
    else:
        print(formatter.info("No changes made."))
    
    input("\nPress Enter to continue...")


def search_notes_advanced(viewer, formatter):
    """Advanced search with fuzzy matching"""
    print(formatter.header("\n🔍 ADVANCED SEARCH"))
    
    query = input("Search query: ").strip()
    if query:
        viewer.search_query = query
        
        # Get results with fuzzy matching
        notes = viewer.get_page(1)
        
        if notes:
            print(formatter.success(f"\n✅ Found {viewer.total_notes} matching notes:"))
            
            for idx, note in enumerate(notes[:10], 1):  # Show top 10
                relevance = note.get('relevance_score', 0) * 100
                print(f"\n[{idx}] {note.get('topic', 'Untitled')} ({relevance:.0f}% match)")
                print(f"    Module: {note.get('module_name', 'General')}")
                preview = viewer.format_note_preview(note, max_length=60)
                print(f"    {preview}")
        else:
            print(formatter.warning("No notes found matching your search."))
    
    input("\nPress Enter to continue...")


def add_note_enhanced(notes_mgr, formatter):
    """Enhanced note creation with better input handling"""
    print(formatter.header("\n✏️ ADD NEW NOTE"))
    
    # Get note details
    title = input("Note title: ").strip()
    if not title:
        print(formatter.error("Title is required!"))
        input("Press Enter...")
        return
    
    print("\nEnter note content (type END on a new line to finish):")
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    
    content = "\n".join(lines)
    if not content:
        print(formatter.error("Content is required!"))
        input("Press Enter...")
        return
    
    # Module/Category
    category = input("\nCategory/Module (or Enter for 'General'): ").strip() or "General"
    
    # Tags
    tags_input = input("Tags (comma-separated, optional): ").strip()
    tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
    
    # Save note
    note_id = notes_mgr.save_note(
        user_id=1,
        lesson_id=None,
        module_name=category,
        topic=title,
        content=content,
        tags=tags
    )
    
    print(formatter.success(f"✅ Note saved with ID: {note_id}"))
    
    # Ask if want to mark as favorite
    if input("\nMark as favorite? (y/n): ").lower() == 'y':
        notes_mgr.toggle_favorite(note_id)
        print(formatter.success("⭐ Marked as favorite!"))
    
    input("\nPress Enter to continue...")


def apply_filters(viewer, formatter):
    """Apply module and tag filters"""
    print(formatter.header("\n🏷️ FILTER NOTES"))
    
    # Module filter
    modules = viewer.get_available_modules()
    if modules:
        print("\nAvailable modules:")
        for idx, module in enumerate(modules, 1):
            print(f"  [{idx}] {module}")
        print("  [0] Clear module filter")
        
        choice = input("\nSelect module (or Enter to skip): ").strip()
        if choice == "0":
            viewer.filter_module = None
        elif choice.isdigit() and 1 <= int(choice) <= len(modules):
            viewer.filter_module = modules[int(choice) - 1]
            print(formatter.success(f"✅ Filtering by module: {viewer.filter_module}"))
    
    # Tag filter
    all_tags = viewer.get_all_tags()
    if all_tags:
        print("\nTop tags:")
        for idx, (tag, count) in enumerate(all_tags[:15], 1):
            print(f"  [{idx}] {tag} ({count})")
        print("  [0] Clear tag filter")
        
        choice = input("\nSelect tags (comma-separated numbers, or Enter to skip): ").strip()
        if choice == "0":
            viewer.filter_tags = []
        elif choice:
            selected = []
            for num in choice.split(","):
                if num.strip().isdigit():
                    tag_idx = int(num.strip()) - 1
                    if 0 <= tag_idx < len(all_tags):
                        selected.append(all_tags[tag_idx][0])
            
            if selected:
                viewer.filter_tags = selected
                print(formatter.success(f"✅ Filtering by tags: {', '.join(selected)}"))
    
    # Reset to page 1 after applying filters
    viewer.current_page = 1
    input("\nPress Enter to continue...")


def show_statistics(viewer, formatter):
    """Display detailed statistics"""
    stats = viewer.get_statistics()
    
    print(formatter.header("\n📊 NOTES STATISTICS"))
    print("═" * 60)
    
    # Overall stats
    print(f"\n📚 Total Notes: {stats['total_notes']}")
    print(f"⭐ Favorites: {stats['favorites']}")
    print(f"📝 Average Length: {stats['avg_length']} characters")
    print(f"📅 Notes This Week: {stats['notes_this_week']}")
    print(f"📂 Total Modules: {stats['modules_count']}")
    
    # Top modules
    if stats['top_modules']:
        print("\n📂 Top Modules:")
        for module, count in stats['top_modules']:
            bar = "█" * min(20, count * 2)
            print(f"  {module:20} {bar} ({count})")
    
    # Top tags
    if stats['top_tags']:
        print("\n🏷️ Top Tags:")
        for tag, count in stats['top_tags'][:10]:
            print(f"  #{tag}: {count} uses")
    
    # Recent activity
    if stats['recent_activity']:
        print("\n📅 Recent Activity (last 7 days):")
        for date, count in stats['recent_activity'][:7]:
            bar = "█" * count
            print(f"  {date}: {bar} ({count})")
    
    input("\nPress Enter to continue...")


def export_notes_filtered(viewer, notes_mgr, formatter):
    """Export notes with current filters applied"""
    print(formatter.header("\n💾 EXPORT NOTES"))
    
    formats = ["markdown", "json", "html"]
    print(f"Export format ({'/'.join(formats)}): ", end="")
    format_choice = input().strip().lower()
    
    if format_choice in formats:
        # Export filtered notes
        export_content = viewer.export_filtered_notes(format_choice)
        
        if export_content:
            # Save to file
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"notes/exports/notes_filtered_{timestamp}.{format_choice if format_choice != 'html' else 'html'}"
            
            # Ensure directory exists
            import os
            os.makedirs("notes/exports", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(export_content)
            
            print(formatter.success(f"✅ Exported to: {filename}"))
            print(f"   Exported {viewer.total_notes} notes with current filters")
        else:
            print(formatter.warning("No notes to export with current filters."))
    else:
        print(formatter.error("Invalid format!"))
    
    input("\nPress Enter to continue...")


def import_notes_enhanced(notes_mgr, formatter):
    """Import notes from file"""
    print(formatter.header("\n📥 IMPORT NOTES"))
    
    file_path = input("Import file path: ").strip()
    
    if not file_path:
        print(formatter.error("No file specified!"))
        input("Press Enter...")
        return
    
    from pathlib import Path
    import json
    
    if not Path(file_path).exists():
        print(formatter.error("File not found!"))
        input("Press Enter...")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                notes_data = json.load(f)
                
                if not isinstance(notes_data, list):
                    notes_data = [notes_data]
                
                imported = 0
                for note in notes_data:
                    if 'content' in note:
                        notes_mgr.save_note(
                            user_id=1,
                            lesson_id=note.get('lesson_id'),
                            module_name=note.get('module_name', 'Imported'),
                            topic=note.get('topic', note.get('title', 'Imported Note')),
                            content=note['content'],
                            tags=note.get('tags', ['imported'])
                        )
                        imported += 1
                
                print(formatter.success(f"✅ Imported {imported} notes!"))
            else:
                # Try to import as markdown
                content = f.read()
                title = Path(file_path).stem.replace('_', ' ').title()
                
                notes_mgr.save_note(
                    user_id=1,
                    lesson_id=None,
                    module_name="Imported",
                    topic=title,
                    content=content,
                    tags=['imported', 'markdown']
                )
                
                print(formatter.success(f"✅ Imported as single note: {title}"))
    
    except Exception as e:
        print(formatter.error(f"Import failed: {str(e)}"))
    
    input("\nPress Enter to continue...")


def configure_settings(viewer, formatter):
    """Configure viewer settings and sort options"""
    print(formatter.header("\n⚙️ SETTINGS"))
    
    print("\n1. Change sort order")
    print("2. Set page size")
    print("3. Toggle fuzzy search")
    print("0. Back")
    
    choice = input("\nYour choice: ").strip()
    
    if choice == "1":
        configure_sort(viewer, formatter)
    elif choice == "2":
        try:
            size = int(input(f"Current page size: {viewer.page_size}\nNew size (1-20): "))
            if 1 <= size <= 20:
                viewer.page_size = size
                print(formatter.success(f"✅ Page size set to {size}"))
            else:
                print(formatter.error("Size must be between 1 and 20"))
        except ValueError:
            print(formatter.error("Invalid number"))
    elif choice == "3":
        # Fuzzy search is always enabled, this is just a placeholder
        print(formatter.info("Fuzzy search is always enabled for better results!"))
    
    input("\nPress Enter to continue...")


def configure_sort(viewer, formatter):
    """Configure sort order"""
    print("\nSort options:")
    print("  [1] Newest first (default)")
    print("  [2] Oldest first")
    print("  [3] Recently updated")
    print("  [4] Title A-Z")
    print("  [5] Title Z-A")
    print("  [6] By module")
    print("  [7] Favorites first")
    
    sort_choice = input("\nSelect sort: ").strip()
    
    sort_map = {
        "1": "created_desc",
        "2": "created_asc",
        "3": "updated_desc",
        "4": "title_asc",
        "5": "title_desc",
        "6": "module_asc",
        "7": "favorites"
    }
    
    if sort_choice in sort_map:
        viewer.sort_by = sort_map[sort_choice]
        viewer.current_page = 1  # Reset to first page
        print(formatter.success("✅ Sort order updated!"))
    else:
        print(formatter.error("Invalid choice"))