"""
Searchable help browser with navigation and content display
Main interface for accessing help topics
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, Dict, Any
import re
from .help_manager import HelpTopic, HelpContext


class HelpBrowser:
    """
    Main help browser interface with search, navigation, and content display
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, help_topics: List[HelpTopic],
                 on_topic_view: Callable[[str], None] = None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.help_topics = help_topics
        self.on_topic_view = on_topic_view
        
        self.help_window = None
        self.current_topic = None
        self.search_results = []
        self.history = []
        self.history_index = -1
        
        # UI components
        self.search_var = None
        self.topic_tree = None
        self.content_text = None
        self.back_button = None
        self.forward_button = None
        self.breadcrumb_label = None
    
    def show(self, context: HelpContext = HelpContext.GENERAL):
        """Show the help browser"""
        if self.help_window:
            self.help_window.lift()
            return
        
        self._create_help_window()
        
        # Show context-relevant topics
        context_topics = [t for t in self.help_topics if t.context == context]
        if context_topics:
            self._show_topic(context_topics[0])
        else:
            self._show_welcome()
    
    def show_topic(self, topic: HelpTopic):
        """Show a specific help topic"""
        if not self.help_window:
            self._create_help_window()
        
        self._show_topic(topic)
        self.help_window.lift()
    
    def _create_help_window(self):
        """Create the main help browser window"""
        colors = self.theme_manager.get_colors()
        
        # Create window
        self.help_window = tk.Toplevel(self.parent)
        self.help_window.title("Help & Documentation")
        self.help_window.geometry("900x700")
        self.help_window.configure(bg=colors['bg'])
        self.help_window.resizable(True, True)
        self.help_window.transient(self.parent)
        
        # Center window
        self.help_window.update_idletasks()
        x = (self.help_window.winfo_screenwidth() // 2) - 450
        y = (self.help_window.winfo_screenheight() // 2) - 350
        self.help_window.geometry(f"+{x}+{y}")
        
        # Create UI
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()
        
        # Bind events
        self._bind_events()
    
    def _create_toolbar(self):
        """Create the help browser toolbar"""
        colors = self.theme_manager.get_colors()
        
        toolbar = tk.Frame(self.help_window, bg=colors['frame_bg'], relief=tk.RAISED, borderwidth=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        # Navigation buttons
        nav_frame = tk.Frame(toolbar, bg=colors['frame_bg'])
        nav_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.back_button = tk.Button(
            nav_frame,
            text="← Back",
            font=('TkDefaultFont', 9),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            command=self._go_back,
            state=tk.DISABLED,
            padx=10
        )
        self.back_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.forward_button = tk.Button(
            nav_frame,
            text="Forward →",
            font=('TkDefaultFont', 9),
            bg=colors['button_bg'],
            fg=colors['button_fg'],
            relief=tk.FLAT,
            command=self._go_forward,
            state=tk.DISABLED,
            padx=10
        )
        self.forward_button.pack(side=tk.LEFT)
        
        # Search
        search_frame = tk.Frame(toolbar, bg=colors['frame_bg'])
        search_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        tk.Label(
            search_frame,
            text="Search:",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['fg']
        ).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('TkDefaultFont', 10),
            width=25,
            bg=colors['entry_bg'],
            fg=colors['entry_fg']
        )
        search_entry.pack(side=tk.LEFT, padx=(5, 0))
        search_entry.bind('<Return>', self._perform_search)
        search_entry.bind('<KeyRelease>', self._on_search_change)
        
        search_button = tk.Button(
            search_frame,
            text="🔍",
            font=('TkDefaultFont', 10),
            bg=colors['info'],
            fg=colors['select_fg'],
            relief=tk.FLAT,
            command=self._perform_search,
            width=3
        )
        search_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Breadcrumb
        breadcrumb_frame = tk.Frame(toolbar, bg=colors['frame_bg'])
        breadcrumb_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.breadcrumb_label = tk.Label(
            breadcrumb_frame,
            text="Help > Getting Started",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['info'],
            anchor=tk.W
        )
        self.breadcrumb_label.pack(fill=tk.X)
    
    def _create_main_content(self):
        """Create the main content area"""
        colors = self.theme_manager.get_colors()
        
        # Main container
        main_frame = tk.Frame(self.help_window, bg=colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar - topic tree
        sidebar_frame = tk.Frame(main_frame, bg=colors['frame_bg'], width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        sidebar_frame.pack_propagate(False)  # Maintain width
        
        # Topic tree with scrollbar
        tree_frame = tk.Frame(sidebar_frame, bg=colors['frame_bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tree widget
        style = ttk.Style()
        
        self.topic_tree = ttk.Treeview(
            tree_frame,
            selectmode='browse',
            height=20
        )
        
        # Scrollbars for tree
        tree_v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.topic_tree.yview)
        self.topic_tree.configure(yscrollcommand=tree_v_scrollbar.set)
        
        # Pack tree and scrollbar
        self.topic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate tree
        self._populate_topic_tree()
        
        # Bind tree selection
        self.topic_tree.bind('<<TreeviewSelect>>', self._on_topic_select)
        
        # Right content area
        content_frame = tk.Frame(main_frame, bg=colors['bg'])
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content text with scrollbar
        text_frame = tk.Frame(content_frame, bg=colors['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.content_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('TkDefaultFont', 11),
            bg=colors['text_bg'],
            fg=colors['text_fg'],
            padx=20,
            pady=15,
            state=tk.DISABLED
        )
        
        content_scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.content_text.yview
        )
        self.content_text.configure(yscrollcommand=content_scrollbar.set)
        
        # Pack content and scrollbar
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_status_bar(self):
        """Create status bar"""
        colors = self.theme_manager.get_colors()
        
        status_frame = tk.Frame(self.help_window, bg=colors['frame_bg'], relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            text=f"Ready - {len(self.help_topics)} help topics available",
            font=('TkDefaultFont', 9),
            bg=colors['frame_bg'],
            fg=colors['disabled_fg'],
            anchor=tk.W,
            padx=10,
            pady=2
        )
        self.status_label.pack(fill=tk.X)
    
    def _populate_topic_tree(self):
        """Populate the topic tree with help topics"""
        # Group topics by context
        contexts = {}
        for topic in self.help_topics:
            context_name = topic.context.value.replace('_', ' ').title()
            if context_name not in contexts:
                contexts[context_name] = []
            contexts[context_name].append(topic)
        
        # Add topics to tree
        for context_name, topics in contexts.items():
            context_node = self.topic_tree.insert('', 'end', text=context_name, open=True)
            
            # Sort topics by difficulty then title
            topics.sort(key=lambda t: (t.difficulty, t.title))
            
            for topic in topics:
                difficulty_icon = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}.get(topic.difficulty, '⚪')
                topic_text = f"{difficulty_icon} {topic.title}"
                
                self.topic_tree.insert(
                    context_node, 
                    'end', 
                    text=topic_text,
                    values=(topic.id,)
                )
    
    def _bind_events(self):
        """Bind keyboard and mouse events"""
        self.help_window.bind('<F1>', lambda e: self._show_help_about())
        self.help_window.bind('<Control-f>', lambda e: self._focus_search())
        self.help_window.bind('<Control-w>', lambda e: self.help_window.destroy())
        self.help_window.bind('<Alt-Left>', lambda e: self._go_back())
        self.help_window.bind('<Alt-Right>', lambda e: self._go_forward())
    
    def _on_topic_select(self, event):
        """Handle topic selection from tree"""
        selection = self.topic_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.topic_tree.item(item, 'values')
        
        if values:  # Topic item (has topic_id)
            topic_id = values[0]
            topic = self._find_topic(topic_id)
            if topic:
                self._show_topic(topic)
    
    def _show_topic(self, topic: HelpTopic):
        """Display a help topic"""
        self.current_topic = topic
        
        # Add to history
        if not self.history or self.history[-1] != topic.id:
            if self.history_index < len(self.history) - 1:
                # Remove forward history when navigating to new topic
                self.history = self.history[:self.history_index + 1]
            
            self.history.append(topic.id)
            self.history_index = len(self.history) - 1
        
        self._update_navigation_buttons()
        
        # Update breadcrumb
        context_name = topic.context.value.replace('_', ' ').title()
        self.breadcrumb_label.config(text=f"Help > {context_name} > {topic.title}")
        
        # Display content
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete('1.0', tk.END)
        
        # Add title
        self.content_text.insert(tk.END, topic.title + "\\n", 'title')
        self.content_text.insert(tk.END, "=" * len(topic.title) + "\\n\\n", 'separator')
        
        # Add difficulty indicator
        difficulty_colors = {
            'beginner': self.theme_manager.get_colors()['success'],
            'intermediate': self.theme_manager.get_colors()['warning'],
            'advanced': self.theme_manager.get_colors()['error']
        }
        
        difficulty_text = f"Difficulty: {topic.difficulty.title()}\\n\\n"
        self.content_text.insert(tk.END, difficulty_text, 'difficulty')
        
        # Add main content
        content = self._format_content(topic.content)
        self.content_text.insert(tk.END, content)
        
        # Add related topics section
        if topic.related_topics:
            self.content_text.insert(tk.END, "\\n\\n" + "Related Topics:" + "\\n", 'section_header')
            for related_id in topic.related_topics:
                related_topic = self._find_topic(related_id)
                if related_topic:
                    self.content_text.insert(tk.END, f"• {related_topic.title}\\n", 'related_link')
        
        # Add video link if available
        if topic.video_url:
            self.content_text.insert(tk.END, "\\n" + "📺 Video Tutorial Available\\n", 'video_link')
        
        self._configure_text_tags()
        self.content_text.config(state=tk.DISABLED)
        
        # Track topic view
        if self.on_topic_view:
            self.on_topic_view(topic.id)
        
        self.status_label.config(text=f"Viewing: {topic.title}")
    
    def _show_welcome(self):
        """Show welcome content"""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete('1.0', tk.END)
        
        welcome_text = \"\"\"Welcome to Help & Documentation
        
This help system provides comprehensive guidance for using the Unsplash Image Search & GPT application for Spanish learning.

Getting Started:
• Browse topics in the left panel organized by category
• Use the search box to find specific information
• Click on any topic to view detailed instructions
• Use navigation buttons to move between topics

Quick Links:
• Getting Started - Essential first steps
• API Setup - Configure your keys  
• Effective Searching - Find the best images
• Vocabulary Building - Learn systematically
• Export Options - Save your progress
• Troubleshooting - Solve common problems

Need More Help?
• Press F1 for keyboard shortcuts
• Use the FAQ for common questions  
• Try the troubleshooting wizard for problems
• Submit feedback for improvements

Happy Learning! 📚✨\"\"\"
        
        self.content_text.insert(tk.END, welcome_text)
        self._configure_text_tags()
        self.content_text.config(state=tk.DISABLED)
        
        self.breadcrumb_label.config(text="Help > Welcome")
        self.status_label.config(text="Welcome to Help")
    
    def _format_content(self, content: str) -> str:
        """Format content with markdown-like styling"""
        # Convert **bold** to tags
        content = re.sub(r'\\*\\*(.*?)\\*\\*', r'\\1', content)
        
        # Convert bullet points to proper formatting
        lines = content.split('\\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                formatted_lines.append('  • ' + line.strip()[2:])
            elif line.strip().startswith('• '):
                formatted_lines.append('  ' + line.strip())
            else:
                formatted_lines.append(line)
        
        return '\\n'.join(formatted_lines)
    
    def _configure_text_tags(self):
        """Configure text styling tags"""
        colors = self.theme_manager.get_colors()
        
        self.content_text.tag_configure(
            'title',
            font=('TkDefaultFont', 16, 'bold'),
            foreground=colors['info']
        )
        
        self.content_text.tag_configure(
            'separator',
            foreground=colors['border']
        )
        
        self.content_text.tag_configure(
            'section_header',
            font=('TkDefaultFont', 12, 'bold'),
            foreground=colors['fg']
        )
        
        self.content_text.tag_configure(
            'difficulty',
            font=('TkDefaultFont', 10, 'italic'),
            foreground=colors['info']
        )
        
        self.content_text.tag_configure(
            'related_link',
            foreground=colors['info'],
            underline=True
        )
        
        self.content_text.tag_configure(
            'video_link',
            foreground=colors['success'],
            font=('TkDefaultFont', 10, 'bold')
        )
    
    def _perform_search(self, event=None):
        """Perform help search"""
        query = self.search_var.get().strip()
        if not query:
            return
        
        results = self._search_topics(query)
        self._show_search_results(query, results)
    
    def _on_search_change(self, event=None):
        """Handle search text changes (for live search)"""
        # Could implement live search here
        pass
    
    def _search_topics(self, query: str) -> List[HelpTopic]:
        """Search help topics"""
        query = query.lower()
        results = []
        
        for topic in self.help_topics:
            score = 0
            
            # Title match (highest weight)
            if query in topic.title.lower():
                score += 10
            
            # Keyword match (high weight)  
            for keyword in topic.keywords:
                if query in keyword.lower():
                    score += 5
            
            # Content match (lower weight)
            if query in topic.content.lower():
                score += 1
            
            if score > 0:
                results.append((topic, score))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return [topic for topic, score in results]
    
    def _show_search_results(self, query: str, results: List[HelpTopic]):
        """Display search results"""
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete('1.0', tk.END)
        
        self.content_text.insert(tk.END, f"Search Results for: '{query}'\\n", 'title')
        self.content_text.insert(tk.END, "=" * (len(query) + 20) + "\\n\\n", 'separator')
        
        if not results:
            self.content_text.insert(tk.END, "No results found.\\n\\n")
            self.content_text.insert(tk.END, "Try different keywords or browse topics by category.")
        else:
            self.content_text.insert(tk.END, f"Found {len(results)} matching topics:\\n\\n")
            
            for i, topic in enumerate(results, 1):
                difficulty_icon = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}.get(topic.difficulty, '⚪')
                result_text = f"{i}. {difficulty_icon} {topic.title}\\n"
                
                # Add clickable link
                start_pos = self.content_text.index(tk.INSERT)
                self.content_text.insert(tk.END, result_text, 'search_result')
                end_pos = self.content_text.index(tk.INSERT)
                
                # Make result clickable
                self.content_text.tag_add(f'link_{topic.id}', start_pos, end_pos)
                self.content_text.tag_configure(
                    f'link_{topic.id}',
                    foreground=self.theme_manager.get_colors()['info'],
                    underline=True
                )
                self.content_text.tag_bind(
                    f'link_{topic.id}',
                    '<Button-1>',
                    lambda e, t=topic: self._show_topic(t)
                )
                
                # Add preview of content
                preview = topic.content[:200] + "..." if len(topic.content) > 200 else topic.content
                self.content_text.insert(tk.END, f"   {preview}\\n\\n")
        
        self._configure_text_tags()
        self.content_text.config(state=tk.DISABLED)
        
        self.breadcrumb_label.config(text=f"Help > Search Results > '{query}'")
        self.status_label.config(text=f"Search: {len(results)} results for '{query}'")
    
    def _go_back(self):
        """Navigate back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            topic_id = self.history[self.history_index]
            topic = self._find_topic(topic_id)
            if topic:
                # Don't add to history when navigating
                current_topic = self.current_topic
                self._show_topic(topic)
                self.current_topic = current_topic
                self._update_navigation_buttons()
    
    def _go_forward(self):
        """Navigate forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            topic_id = self.history[self.history_index]
            topic = self._find_topic(topic_id)
            if topic:
                # Don't add to history when navigating
                current_topic = self.current_topic
                self._show_topic(topic)
                self.current_topic = current_topic
                self._update_navigation_buttons()
    
    def _update_navigation_buttons(self):
        """Update back/forward button states"""
        can_go_back = self.history_index > 0
        can_go_forward = self.history_index < len(self.history) - 1
        
        self.back_button.config(state=tk.NORMAL if can_go_back else tk.DISABLED)
        self.forward_button.config(state=tk.NORMAL if can_go_forward else tk.DISABLED)
    
    def _find_topic(self, topic_id: str) -> Optional[HelpTopic]:
        """Find topic by ID"""
        for topic in self.help_topics:
            if topic.id == topic_id:
                return topic
        return None
    
    def _focus_search(self):
        """Focus the search entry"""
        # Implementation would focus search entry
        pass
    
    def _show_help_about(self):
        """Show help about dialog"""
        # Implementation would show keyboard shortcuts and about info
        pass
    
    def refresh_topics(self):
        """Refresh the topic tree (called when topics are updated)"""
        # Clear and repopulate tree
        for item in self.topic_tree.get_children():
            self.topic_tree.delete(item)
        self._populate_topic_tree()
    
    def hide(self):
        """Hide the help browser"""
        if self.help_window:
            self.help_window.destroy()
            self.help_window = None