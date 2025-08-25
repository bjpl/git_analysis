"""
Comprehensive keyboard navigation system for accessibility.
Provides customizable keyboard shortcuts and navigation patterns.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable, Any, Tuple
import json
import threading


class KeyboardNavigation:
    """
    Manages comprehensive keyboard navigation and shortcuts.
    Provides customizable keyboard shortcuts and navigation patterns.
    """
    
    def __init__(self, root_window: tk.Tk, settings: Dict[str, Any]):
        self.root = root_window
        self.settings = settings
        self.widgets: List[tk.Widget] = []
        self.shortcuts: Dict[str, Callable] = {}
        self.custom_shortcuts: Dict[str, str] = settings.get('custom_shortcuts', {})
        
        # Navigation state
        self.current_context = None
        self.navigation_mode = 'normal'  # normal, forms, tables, menus
        self.skip_invisible = True
        self.wrap_navigation = True
        
        # Key binding storage
        self.bound_keys: Dict[str, List[Tuple[tk.Widget, str]]] = {}
        
        # Initialize default shortcuts
        self._setup_default_shortcuts()
        
        # Setup global key handlers
        self._setup_global_handlers()
    
    def _setup_default_shortcuts(self):
        """Setup default keyboard shortcuts."""
        self.default_shortcuts = {
            # Accessibility shortcuts
            'accessibility_help': {
                'key': '<Control-Alt-a>',
                'description': 'Show accessibility help',
                'category': 'Accessibility'
            },
            'accessibility_settings': {
                'key': '<Control-Alt-s>',
                'description': 'Open accessibility settings',
                'category': 'Accessibility'
            },
            'toggle_high_contrast': {
                'key': '<Control-Alt-h>',
                'description': 'Toggle high contrast mode',
                'category': 'Accessibility'
            },
            'read_current_widget': {
                'key': '<Control-Alt-r>',
                'description': 'Read current widget information',
                'category': 'Screen Reader'
            },
            'read_next_widget': {
                'key': '<Control-Alt-n>',
                'description': 'Move to and read next widget',
                'category': 'Screen Reader'
            },
            'read_previous_widget': {
                'key': '<Control-Alt-p>',
                'description': 'Move to and read previous widget',
                'category': 'Screen Reader'
            },
            
            # Font size shortcuts
            'increase_font': {
                'key': '<Control-plus>',
                'description': 'Increase font size',
                'category': 'Display'
            },
            'increase_font_alt': {
                'key': '<Control-equal>',
                'description': 'Increase font size (alternative)',
                'category': 'Display'
            },
            'decrease_font': {
                'key': '<Control-minus>',
                'description': 'Decrease font size',
                'category': 'Display'
            },
            'reset_font': {
                'key': '<Control-0>',
                'description': 'Reset font size to 100%',
                'category': 'Display'
            },
            
            # Navigation shortcuts
            'focus_first': {
                'key': '<Control-Home>',
                'description': 'Focus first element',
                'category': 'Navigation'
            },
            'focus_last': {
                'key': '<Control-End>',
                'description': 'Focus last element',
                'category': 'Navigation'
            },
            'skip_to_main': {
                'key': '<Control-Alt-m>',
                'description': 'Skip to main content',
                'category': 'Navigation'
            },
            'skip_to_navigation': {
                'key': '<Control-Alt-n>',
                'description': 'Skip to navigation menu',
                'category': 'Navigation'
            },
            
            # Application shortcuts
            'help': {
                'key': '<F1>',
                'description': 'Show help for current context',
                'category': 'Help'
            },
            'context_menu': {
                'key': '<Shift-F10>',
                'description': 'Show context menu',
                'category': 'Menus'
            },
            'escape': {
                'key': '<Escape>',
                'description': 'Cancel current action or close dialog',
                'category': 'General'
            }
        }
    
    def _setup_global_handlers(self):
        """Setup global keyboard event handlers."""
        # Bind all default shortcuts
        for shortcut_id, shortcut_info in self.default_shortcuts.items():
            key = self.custom_shortcuts.get(shortcut_id, shortcut_info['key'])
            self._bind_shortcut(shortcut_id, key)
        
        # Special navigation keys
        self.root.bind_all('<Tab>', self._handle_tab, add='+')
        self.root.bind_all('<Shift-Tab>', self._handle_shift_tab, add='+')
        self.root.bind_all('<Up>', self._handle_arrow, add='+')
        self.root.bind_all('<Down>', self._handle_arrow, add='+')
        self.root.bind_all('<Left>', self._handle_arrow, add='+')
        self.root.bind_all('<Right>', self._handle_arrow, add='+')
        
        # Page navigation
        self.root.bind_all('<Page_Up>', self._handle_page_up, add='+')
        self.root.bind_all('<Page_Down>', self._handle_page_down, add='+')
        self.root.bind_all('<Home>', self._handle_home, add='+')
        self.root.bind_all('<End>', self._handle_end, add='+')
        
        # Enter and space for activation
        self.root.bind_all('<Return>', self._handle_enter, add='+')
        self.root.bind_all('<KP_Enter>', self._handle_enter, add='+')
        self.root.bind_all('<space>', self._handle_space, add='+')
        
        # Context menu
        self.root.bind_all('<App>', self._handle_context_menu, add='+')
        
        # Debug key for accessibility info
        self.root.bind_all('<Control-Alt-d>', self._debug_accessibility_info, add='+')
    
    def _bind_shortcut(self, shortcut_id: str, key_sequence: str):
        """Bind a keyboard shortcut to its handler."""
        handler_name = f"_handle_{shortcut_id}"
        if hasattr(self, handler_name):
            handler = getattr(self, handler_name)
        else:
            # Create generic handler
            handler = lambda event, sid=shortcut_id: self._handle_generic_shortcut(event, sid)
        
        try:
            self.root.bind_all(key_sequence, handler, add='+')
            
            # Track binding
            if key_sequence not in self.bound_keys:
                self.bound_keys[key_sequence] = []
            self.bound_keys[key_sequence].append((self.root, shortcut_id))
        
        except tk.TclError as e:
            print(f"Failed to bind shortcut {shortcut_id} ({key_sequence}): {e}")
    
    def add_widget(self, widget: tk.Widget, **options):
        """
        Add a widget to keyboard navigation.
        
        Args:
            widget: Widget to add
            **options: Navigation options:
                - shortcut_keys: Dict of key->callback mappings
                - context: Navigation context (forms, tables, etc.)
                - skip_tab: Skip this widget in tab navigation
                - role: Widget role for specialized navigation
        """
        if widget not in self.widgets:
            self.widgets.append(widget)
        
        # Add custom shortcuts for this widget
        shortcut_keys = options.get('shortcut_keys', {})
        for key, callback in shortcut_keys.items():
            self._bind_widget_shortcut(widget, key, callback)
        
        # Setup role-specific navigation
        role = options.get('role', '')
        if role:
            self._setup_role_navigation(widget, role)
        
        # Context-specific setup
        context = options.get('context', 'normal')
        if context != 'normal':
            self._setup_context_navigation(widget, context)
    
    def _bind_widget_shortcut(self, widget: tk.Widget, key: str, callback: Callable):
        """Bind shortcut key to specific widget."""
        def handler(event):
            if event.widget == widget or self._is_child_of(event.widget, widget):
                return callback(event)
        
        try:
            self.root.bind_all(key, handler, add='+')
        except tk.TclError as e:
            print(f"Failed to bind widget shortcut {key}: {e}")
    
    def _setup_role_navigation(self, widget: tk.Widget, role: str):
        """Setup role-specific keyboard navigation."""
        if role == 'listbox':
            self._setup_listbox_navigation(widget)
        elif role == 'treeview':
            self._setup_treeview_navigation(widget)
        elif role == 'notebook':
            self._setup_notebook_navigation(widget)
        elif role == 'menu':
            self._setup_menu_navigation(widget)
        elif role == 'dialog':
            self._setup_dialog_navigation(widget)
    
    def _setup_listbox_navigation(self, widget: tk.Widget):
        """Setup listbox-specific navigation."""
        def handle_char(event):
            # Type-ahead search in listboxes
            if event.char.isalnum():
                self._do_typeahead_search(widget, event.char)
        
        widget.bind('<KeyPress>', handle_char, add='+')
        widget.bind('<Control-a>', lambda e: self._select_all_listbox(widget), add='+')
    
    def _setup_treeview_navigation(self, widget: tk.Widget):
        """Setup treeview-specific navigation."""
        # Expand/collapse with +/- keys
        widget.bind('<plus>', lambda e: self._expand_treeview_item(widget), add='+')
        widget.bind('<minus>', lambda e: self._collapse_treeview_item(widget), add='+')
        widget.bind('<asterisk>', lambda e: self._expand_all_treeview(widget), add='+')
    
    def _setup_notebook_navigation(self, widget: tk.Widget):
        """Setup notebook tab navigation."""
        widget.bind('<Control-Tab>', lambda e: self._next_notebook_tab(widget), add='+')
        widget.bind('<Control-Shift-Tab>', lambda e: self._prev_notebook_tab(widget), add='+')
        widget.bind('<Control-Page_Down>', lambda e: self._next_notebook_tab(widget), add='+')
        widget.bind('<Control-Page_Up>', lambda e: self._prev_notebook_tab(widget), add='+')
    
    def _setup_context_navigation(self, widget: tk.Widget, context: str):
        """Setup context-specific navigation patterns."""
        if context == 'forms':
            # Form navigation patterns
            widget.bind('<Control-Return>', self._handle_form_submit, add='+')
            widget.bind('<Control-Escape>', self._handle_form_cancel, add='+')
        elif context == 'tables':
            # Table navigation patterns
            widget.bind('<Control-Left>', lambda e: self._navigate_table(widget, 'left'), add='+')
            widget.bind('<Control-Right>', lambda e: self._navigate_table(widget, 'right'), add='+')
            widget.bind('<Control-Up>', lambda e: self._navigate_table(widget, 'up'), add='+')
            widget.bind('<Control-Down>', lambda e: self._navigate_table(widget, 'down'), add='+')
    
    # Event handlers for standard navigation
    def _handle_tab(self, event):
        """Handle Tab key for forward navigation."""
        widget = event.widget
        
        # Check if widget has custom tab handling
        if self._has_custom_tab_handling(widget):
            return  # Let widget handle it
        
        # Find next focusable widget
        next_widget = self._find_next_focusable(widget)
        if next_widget:
            next_widget.focus_set()
            self._announce_focus_change(next_widget)
            return "break"
    
    def _handle_shift_tab(self, event):
        """Handle Shift+Tab for backward navigation."""
        widget = event.widget
        
        if self._has_custom_tab_handling(widget):
            return
        
        prev_widget = self._find_previous_focusable(widget)
        if prev_widget:
            prev_widget.focus_set()
            self._announce_focus_change(prev_widget)
            return "break"
    
    def _handle_arrow(self, event):
        """Handle arrow key navigation."""
        widget = event.widget
        direction = event.keysym.lower()
        
        # Check for widget-specific arrow handling
        if isinstance(widget, (tk.Listbox, ttk.Treeview, ttk.Notebook)):
            return  # Let widget handle it
        
        # Check if we're in a grid or table context
        if self._is_in_grid_context(widget):
            return self._handle_grid_navigation(widget, direction)
        
        # Default arrow navigation (similar to tab)
        if direction in ['down', 'right']:
            return self._handle_tab(event)
        else:  # up, left
            return self._handle_shift_tab(event)
    
    def _handle_page_up(self, event):
        """Handle Page Up navigation."""
        widget = event.widget
        
        # If widget supports page navigation, let it handle
        if hasattr(widget, 'yview'):
            return
        
        # Otherwise, jump to previous section/group
        section_widget = self._find_previous_section(widget)
        if section_widget:
            section_widget.focus_set()
            return "break"
    
    def _handle_page_down(self, event):
        """Handle Page Down navigation."""
        widget = event.widget
        
        if hasattr(widget, 'yview'):
            return
        
        section_widget = self._find_next_section(widget)
        if section_widget:
            section_widget.focus_set()
            return "break"
    
    def _handle_home(self, event):
        """Handle Home key navigation."""
        widget = event.widget
        
        # If it's a text widget, let it handle
        if isinstance(widget, (tk.Text, tk.Entry, ttk.Entry)):
            return
        
        # Otherwise, go to first widget in container
        first_widget = self._find_first_in_container(widget)
        if first_widget:
            first_widget.focus_set()
            return "break"
    
    def _handle_end(self, event):
        """Handle End key navigation."""
        widget = event.widget
        
        if isinstance(widget, (tk.Text, tk.Entry, ttk.Entry)):
            return
        
        last_widget = self._find_last_in_container(widget)
        if last_widget:
            last_widget.focus_set()
            return "break"
    
    def _handle_enter(self, event):
        """Handle Enter key for activation."""
        widget = event.widget
        
        # Buttons and button-like widgets
        if isinstance(widget, (tk.Button, ttk.Button)):
            widget.invoke()
            return "break"
        elif isinstance(widget, (tk.Checkbutton, ttk.Checkbutton)):
            widget.invoke()
            return "break"
        elif isinstance(widget, (tk.Radiobutton, ttk.Radiobutton)):
            widget.invoke()
            return "break"
        
        # Links (labels with click handlers)
        if isinstance(widget, (tk.Label, ttk.Label)) and widget.bind('<Button-1>'):
            widget.event_generate('<Button-1>')
            return "break"
    
    def _handle_space(self, event):
        """Handle Space key for activation."""
        widget = event.widget
        
        # Similar to Enter but more selective
        if isinstance(widget, (tk.Button, ttk.Button)):
            widget.invoke()
            return "break"
        elif isinstance(widget, (tk.Checkbutton, ttk.Checkbutton)):
            widget.invoke()
            return "break"
    
    def _handle_context_menu(self, event):
        """Handle context menu key."""
        widget = event.widget
        
        # Try to show context menu at widget location
        try:
            x = widget.winfo_x() + widget.winfo_width() // 2
            y = widget.winfo_y() + widget.winfo_height() // 2
            
            # Generate right-click event
            widget.event_generate('<Button-3>', x=x, y=y)
            return "break"
        except:
            pass
    
    # Shortcut handlers
    def _handle_accessibility_help(self, event):
        """Show accessibility help."""
        try:
            # Get accessibility manager from root
            if hasattr(self.root, '_accessibility_manager'):
                self.root._accessibility_manager._show_accessibility_help()
            return "break"
        except:
            pass
    
    def _handle_accessibility_settings(self, event):
        """Open accessibility settings."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                self.root._accessibility_manager._show_accessibility_settings()
            return "break"
        except:
            pass
    
    def _handle_toggle_high_contrast(self, event):
        """Toggle high contrast mode."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                self.root._accessibility_manager.toggle_high_contrast()
            return "break"
        except:
            pass
    
    def _handle_increase_font(self, event):
        """Increase font size."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                current = self.root._accessibility_manager.settings.get('font_scale', 1.0)
                new_scale = min(2.0, current + 0.1)
                self.root._accessibility_manager.set_font_scale(new_scale)
            return "break"
        except:
            pass
    
    _handle_increase_font_alt = _handle_increase_font  # Alias for alternative key
    
    def _handle_decrease_font(self, event):
        """Decrease font size."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                current = self.root._accessibility_manager.settings.get('font_scale', 1.0)
                new_scale = max(0.5, current - 0.1)
                self.root._accessibility_manager.set_font_scale(new_scale)
            return "break"
        except:
            pass
    
    def _handle_reset_font(self, event):
        """Reset font size to 100%."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                self.root._accessibility_manager.set_font_scale(1.0)
            return "break"
        except:
            pass
    
    def _handle_read_current_widget(self, event):
        """Read current widget information."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                self.root._accessibility_manager._read_current_widget()
            return "break"
        except:
            pass
    
    def _handle_read_next_widget(self, event):
        """Read next widget."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                self.root._accessibility_manager._read_next_widget()
            return "break"
        except:
            pass
    
    def _handle_read_previous_widget(self, event):
        """Read previous widget."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                self.root._accessibility_manager._read_previous_widget()
            return "break"
        except:
            pass
    
    def _handle_focus_first(self, event):
        """Focus first element."""
        first_widget = self._find_first_focusable()
        if first_widget:
            first_widget.focus_set()
            return "break"
    
    def _handle_focus_last(self, event):
        """Focus last element."""
        last_widget = self._find_last_focusable()
        if last_widget:
            last_widget.focus_set()
            return "break"
    
    def _handle_help(self, event):
        """Show context help."""
        widget = event.widget
        
        # Try to show help for current widget
        if hasattr(widget, '_accessibility') and hasattr(widget._accessibility, 'show_help'):
            widget._accessibility.show_help()
            return "break"
        
        # Fallback to general help
        return self._handle_accessibility_help(event)
    
    def _handle_escape(self, event):
        """Handle escape key."""
        widget = event.widget
        
        # Close dialogs
        if isinstance(widget.winfo_toplevel(), tk.Toplevel):
            widget.winfo_toplevel().destroy()
            return "break"
        
        # Cancel current operation
        if hasattr(widget, 'cancel') and callable(widget.cancel):
            widget.cancel()
            return "break"
    
    def _handle_generic_shortcut(self, event, shortcut_id: str):
        """Handle generic shortcut that doesn't have specific handler."""
        print(f"Generic shortcut handler called for: {shortcut_id}")
        return "break"
    
    # Navigation helper methods
    def _find_next_focusable(self, current_widget: tk.Widget) -> Optional[tk.Widget]:
        """Find next focusable widget."""
        try:
            next_widget = current_widget.tk_focusNext()
            
            # Skip invisible or disabled widgets
            while next_widget and self.skip_invisible:
                if self._is_widget_focusable(next_widget):
                    return next_widget
                next_widget = next_widget.tk_focusNext()
                
                # Prevent infinite loop
                if next_widget == current_widget:
                    break
            
            return next_widget
        except:
            return None
    
    def _find_previous_focusable(self, current_widget: tk.Widget) -> Optional[tk.Widget]:
        """Find previous focusable widget."""
        try:
            prev_widget = current_widget.tk_focusPrev()
            
            while prev_widget and self.skip_invisible:
                if self._is_widget_focusable(prev_widget):
                    return prev_widget
                prev_widget = prev_widget.tk_focusPrev()
                
                if prev_widget == current_widget:
                    break
            
            return prev_widget
        except:
            return None
    
    def _find_first_focusable(self) -> Optional[tk.Widget]:
        """Find first focusable widget in application."""
        for widget in self.widgets:
            if self._is_widget_focusable(widget):
                return widget
        return None
    
    def _find_last_focusable(self) -> Optional[tk.Widget]:
        """Find last focusable widget in application."""
        for widget in reversed(self.widgets):
            if self._is_widget_focusable(widget):
                return widget
        return None
    
    def _is_widget_focusable(self, widget: tk.Widget) -> bool:
        """Check if widget can receive focus."""
        try:
            # Widget must exist and be visible
            if not widget.winfo_exists() or not widget.winfo_viewable():
                return False
            
            # Check if widget accepts focus
            takefocus = widget.cget('takefocus')
            if takefocus == 0 or takefocus == '0':
                return False
            
            # Check if widget is disabled
            try:
                state = widget.cget('state')
                if state in ['disabled', 'readonly']:
                    return False
            except:
                pass
            
            return True
        except:
            return False
    
    def _has_custom_tab_handling(self, widget: tk.Widget) -> bool:
        """Check if widget has custom tab handling."""
        return isinstance(widget, (tk.Text, ttk.Notebook, tk.Listbox, ttk.Treeview))
    
    def _is_child_of(self, child: tk.Widget, parent: tk.Widget) -> bool:
        """Check if child widget is descendant of parent."""
        try:
            current = child.winfo_parent()
            while current:
                if self.root.nametowidget(current) == parent:
                    return True
                current = self.root.nametowidget(current).winfo_parent()
            return False
        except:
            return False
    
    def _announce_focus_change(self, widget: tk.Widget):
        """Announce focus change to screen reader."""
        try:
            if hasattr(self.root, '_accessibility_manager'):
                am = self.root._accessibility_manager
                if hasattr(am, 'screen_reader'):
                    info = am.get_widget_info(widget)
                    message = f"{info.get('name', info.get('widget_class', 'Element'))}"
                    if info.get('description'):
                        message += f", {info['description']}"
                    am.screen_reader.announce(message, 'polite')
        except Exception as e:
            print(f"Focus announcement failed: {e}")
    
    def _debug_accessibility_info(self, event):
        """Debug handler to show accessibility info for current widget."""
        widget = event.widget
        try:
            if hasattr(self.root, '_accessibility_manager'):
                info = self.root._accessibility_manager.get_widget_info(widget)
                print(f"Accessibility Info for {widget}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                print("-" * 40)
        except Exception as e:
            print(f"Debug info failed: {e}")
        return "break"
    
    # Specialized navigation methods
    def _do_typeahead_search(self, widget: tk.Widget, char: str):
        """Perform typeahead search in listbox."""
        if isinstance(widget, tk.Listbox):
            try:
                # Simple typeahead - find first item starting with character
                size = widget.size()
                for i in range(size):
                    item_text = widget.get(i).lower()
                    if item_text.startswith(char.lower()):
                        widget.selection_clear(0, tk.END)
                        widget.selection_set(i)
                        widget.see(i)
                        widget.activate(i)
                        break
            except:
                pass
    
    def _select_all_listbox(self, widget: tk.Widget):
        """Select all items in listbox."""
        if isinstance(widget, tk.Listbox):
            try:
                widget.selection_set(0, tk.END)
            except:
                pass
    
    def customize_shortcut(self, shortcut_id: str, new_key: str) -> bool:
        """
        Customize a keyboard shortcut.
        
        Args:
            shortcut_id: ID of shortcut to customize
            new_key: New key sequence (e.g., '<Control-Alt-x>')
        
        Returns:
            True if successful, False otherwise
        """
        if shortcut_id not in self.default_shortcuts:
            return False
        
        try:
            # Unbind old key
            old_key = self.custom_shortcuts.get(shortcut_id, 
                                               self.default_shortcuts[shortcut_id]['key'])
            self.root.unbind_all(old_key)
            
            # Bind new key
            self._bind_shortcut(shortcut_id, new_key)
            
            # Store customization
            self.custom_shortcuts[shortcut_id] = new_key
            
            # Update settings
            self.settings['custom_shortcuts'] = self.custom_shortcuts
            
            return True
        except Exception as e:
            print(f"Failed to customize shortcut {shortcut_id}: {e}")
            return False
    
    def get_shortcuts(self) -> Dict[str, Dict[str, str]]:
        """Get all current shortcuts with their information."""
        shortcuts = {}
        for shortcut_id, shortcut_info in self.default_shortcuts.items():
            shortcuts[shortcut_id] = {
                'key': self.custom_shortcuts.get(shortcut_id, shortcut_info['key']),
                'description': shortcut_info['description'],
                'category': shortcut_info['category'],
                'is_custom': shortcut_id in self.custom_shortcuts
            }
        return shortcuts
    
    def reset_shortcut(self, shortcut_id: str) -> bool:
        """Reset shortcut to default."""
        if shortcut_id not in self.default_shortcuts:
            return False
        
        if shortcut_id in self.custom_shortcuts:
            # Remove customization
            del self.custom_shortcuts[shortcut_id]
            
            # Re-bind default
            default_key = self.default_shortcuts[shortcut_id]['key']
            self._bind_shortcut(shortcut_id, default_key)
            
            return True
        
        return False
    
    def export_shortcuts(self, filename: str):
        """Export current shortcuts to file."""
        shortcuts_data = {
            'custom_shortcuts': self.custom_shortcuts,
            'export_version': '1.0'
        }
        
        with open(filename, 'w') as f:
            json.dump(shortcuts_data, f, indent=2)
    
    def import_shortcuts(self, filename: str) -> bool:
        """Import shortcuts from file."""
        try:
            with open(filename, 'r') as f:
                shortcuts_data = json.load(f)
            
            if 'custom_shortcuts' in shortcuts_data:
                # Apply each custom shortcut
                for shortcut_id, key in shortcuts_data['custom_shortcuts'].items():
                    self.customize_shortcut(shortcut_id, key)
                
                return True
            
            return False
        except Exception as e:
            print(f"Failed to import shortcuts: {e}")
            return False