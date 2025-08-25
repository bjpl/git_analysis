"""
Empty state manager that provides helpful messages when there's no content
Creates engaging and informative messages for various empty states in the app
"""

import tkinter as tk
from typing import Dict, Any, Optional


class EmptyStateManager:
    """
    Manages empty states throughout the application
    Provides helpful, contextual messages when users encounter empty screens
    """
    
    def __init__(self, theme_manager, help_manager=None):
        self.theme_manager = theme_manager
        self.help_manager = help_manager
        
        # Define all empty states
        self.empty_states = {
            'no_search_results': {
                'icon': '🔍',
                'title': 'No Images Found',
                'message': 'We couldn\'t find any images for your search term.',
                'suggestions': [
                    'Try different keywords (e.g., "comida" instead of "food")',
                    'Check your spelling',
                    'Use simpler, more general terms',
                    'Try searching in Spanish for better results'
                ],
                'actions': [
                    {'text': 'Search Tips', 'action': 'show_search_help'},
                    {'text': 'Popular Topics', 'action': 'show_popular_topics'}
                ]
            },
            
            'no_image_loaded': {
                'icon': '🖼️',
                'title': 'No Image Selected',
                'message': 'Search for an image to get started with your Spanish learning.',
                'suggestions': [
                    'Use the search box above to find images',
                    'Try topics like "mercado", "naturaleza", or "familia"',
                    'Images with clear objects work best for vocabulary learning'
                ],
                'actions': [
                    {'text': 'Getting Started', 'action': 'show_getting_started'},
                    {'text': 'Sample Search', 'action': 'perform_sample_search'}
                ]
            },
            
            'no_description_generated': {
                'icon': '🤖',
                'title': 'Ready for AI Description',
                'message': 'Load an image and click "Generate Description" to create Spanish content.',
                'suggestions': [
                    'Add your own notes first for better context',
                    'Make sure your image is clear and detailed',
                    'The AI will analyze everything it sees in the image'
                ],
                'actions': [
                    {'text': 'How It Works', 'action': 'show_ai_help'},
                    {'text': 'View Sample', 'action': 'show_sample_description'}
                ]
            },
            
            'no_vocabulary_extracted': {
                'icon': '📚',
                'title': 'No Vocabulary Yet',
                'message': 'Generate a description first to extract Spanish vocabulary automatically.',
                'suggestions': [
                    'Click "Generate Description" to create Spanish content',
                    'The AI will identify useful words and phrases',
                    'Blue words can be clicked to add to your learning list'
                ],
                'actions': [
                    {'text': 'Vocabulary Guide', 'action': 'show_vocabulary_help'},
                    {'text': 'Learning Tips', 'action': 'show_learning_tips'}
                ]
            },
            
            'vocabulary_list_empty': {
                'icon': '📝',
                'title': 'Your Vocabulary List is Empty',
                'message': 'Click on blue words from descriptions to start building your vocabulary.',
                'suggestions': [
                    'Look for nouns, verbs, and adjectives in descriptions',
                    'Start with words that interest you most',
                    'Each word includes English translation and context'
                ],
                'actions': [
                    {'text': 'How to Add Words', 'action': 'show_vocabulary_help'},
                    {'text': 'Study Methods', 'action': 'show_study_methods'}
                ]
            },
            
            'api_keys_missing': {
                'icon': '🔑',
                'title': 'API Keys Required',
                'message': 'You need to configure your API keys to use this application.',
                'suggestions': [
                    'Unsplash API key for searching images',
                    'OpenAI API key for generating descriptions',
                    'Both services offer free tiers to get started'
                ],
                'actions': [
                    {'text': 'Setup Guide', 'action': 'show_api_setup'},
                    {'text': 'Get API Keys', 'action': 'show_api_links'}
                ]
            },
            
            'connection_error': {
                'icon': '🌐',
                'title': 'Connection Problem',
                'message': 'Unable to connect to the internet or API services.',
                'suggestions': [
                    'Check your internet connection',
                    'Verify your API keys are correct',
                    'Try again in a few moments',
                    'Check if the services are experiencing outages'
                ],
                'actions': [
                    {'text': 'Troubleshooting', 'action': 'show_troubleshooting'},
                    {'text': 'Test Connection', 'action': 'test_connection'}
                ]
            },
            
            'first_time_user': {
                'icon': '🎉',
                'title': 'Welcome to Spanish Learning!',
                'message': 'You\'re about to discover a fun new way to build vocabulary through images.',
                'suggestions': [
                    'Take the interactive tour to learn the basics',
                    'Try the sample walkthrough to see how it works',
                    'Start with simple topics like food or family'
                ],
                'actions': [
                    {'text': 'Start Tour', 'action': 'start_tour'},
                    {'text': 'Sample Demo', 'action': 'start_demo'},
                    {'text': 'Skip to App', 'action': 'skip_onboarding'}
                ]
            },
            
            'export_no_data': {
                'icon': '📤',
                'title': 'Nothing to Export Yet',
                'message': 'Build your vocabulary first, then export it for studying.',
                'suggestions': [
                    'Search for images and generate descriptions',
                    'Click on vocabulary words to add them to your list',
                    'Aim for at least 10-20 words before exporting'
                ],
                'actions': [
                    {'text': 'Start Learning', 'action': 'show_search_help'},
                    {'text': 'Export Guide', 'action': 'show_export_help'}
                ]
            },
            
            'search_history_empty': {
                'icon': '📋',
                'title': 'No Search History',
                'message': 'Your search history will appear here as you explore topics.',
                'suggestions': [
                    'Search for images to build your history',
                    'Recent searches help you return to favorite topics',
                    'History is saved between sessions'
                ],
                'actions': [
                    {'text': 'Popular Searches', 'action': 'show_popular_topics'}
                ]
            }
        }
    
    def get_empty_state(self, state_type: str) -> Dict[str, Any]:
        """Get empty state configuration"""
        return self.empty_states.get(state_type, {
            'icon': '❓',
            'title': 'Empty State',
            'message': 'No content available.',
            'suggestions': [],
            'actions': []
        })
    
    def create_empty_state_widget(self, parent: tk.Widget, state_type: str, 
                                 custom_actions: Dict[str, callable] = None) -> tk.Widget:
        """Create a complete empty state widget"""
        empty_state = self.get_empty_state(state_type)
        colors = self.theme_manager.get_colors()
        
        # Main container
        container = tk.Frame(parent, bg=colors['bg'])
        
        # Center content frame
        content_frame = tk.Frame(container, bg=colors['bg'])
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Icon
        icon_label = tk.Label(
            content_frame,
            text=empty_state['icon'],
            font=('TkDefaultFont', 48),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        icon_label.pack(pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            content_frame,
            text=empty_state['title'],
            font=('TkDefaultFont', 16, 'bold'),
            bg=colors['bg'],
            fg=colors['fg']
        )
        title_label.pack(pady=(0, 10))
        
        # Message
        message_label = tk.Label(
            content_frame,
            text=empty_state['message'],
            font=('TkDefaultFont', 11),
            bg=colors['bg'],
            fg=colors['disabled_fg'],
            wraplength=400,
            justify=tk.CENTER
        )
        message_label.pack(pady=(0, 20))
        
        # Suggestions
        if empty_state.get('suggestions'):
            suggestions_frame = tk.Frame(content_frame, bg=colors['bg'])
            suggestions_frame.pack(pady=(0, 20))
            
            suggestions_title = tk.Label(
                suggestions_frame,
                text="💡 Suggestions:",
                font=('TkDefaultFont', 10, 'bold'),
                bg=colors['bg'],
                fg=colors['info']
            )
            suggestions_title.pack(anchor=tk.W)
            
            for suggestion in empty_state['suggestions']:
                suggestion_label = tk.Label(
                    suggestions_frame,
                    text=f"• {suggestion}",
                    font=('TkDefaultFont', 10),
                    bg=colors['bg'],
                    fg=colors['fg'],
                    anchor=tk.W,
                    justify=tk.LEFT,
                    wraplength=380
                )
                suggestion_label.pack(anchor=tk.W, pady=2)
        
        # Action buttons
        if empty_state.get('actions'):
            actions_frame = tk.Frame(content_frame, bg=colors['bg'])
            actions_frame.pack()
            
            for action in empty_state['actions']:
                action_callback = None
                
                # Check for custom actions first
                if custom_actions and action['action'] in custom_actions:
                    action_callback = custom_actions[action['action']]
                else:
                    # Use default actions
                    action_callback = getattr(self, f"_{action['action']}", None)
                
                if action_callback:
                    action_button = tk.Button(
                        actions_frame,
                        text=action['text'],
                        font=('TkDefaultFont', 10),
                        bg=colors['select_bg'],
                        fg=colors['select_fg'],
                        relief=tk.FLAT,
                        command=action_callback,
                        padx=20,
                        pady=5
                    )
                    action_button.pack(side=tk.LEFT, padx=5)
        
        return container
    
    def create_inline_empty_message(self, parent: tk.Widget, state_type: str) -> tk.Widget:
        """Create a simple inline empty state message"""
        empty_state = self.get_empty_state(state_type)
        colors = self.theme_manager.get_colors()
        
        # Simple message frame
        message_frame = tk.Frame(parent, bg=colors['bg'])
        
        # Icon and text on same line
        content_frame = tk.Frame(message_frame, bg=colors['bg'])
        content_frame.pack(expand=True)
        
        icon_label = tk.Label(
            content_frame,
            text=empty_state['icon'],
            font=('TkDefaultFont', 16),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        text_label = tk.Label(
            content_frame,
            text=empty_state['message'],
            font=('TkDefaultFont', 10),
            bg=colors['bg'],
            fg=colors['disabled_fg']
        )
        text_label.pack(side=tk.LEFT)
        
        return message_frame
    
    # Default action methods
    def _show_search_help(self):
        """Show search help"""
        if self.help_manager:
            self.help_manager.show_help(context=self.help_manager.HelpContext.SEARCH)
    
    def _show_getting_started(self):
        """Show getting started guide"""
        if self.help_manager:
            self.help_manager.show_help(topic_id="getting_started")
    
    def _show_api_setup(self):
        """Show API setup help"""
        if self.help_manager:
            self.help_manager.show_help(topic_id="api_setup")
    
    def _show_vocabulary_help(self):
        """Show vocabulary help"""
        if self.help_manager:
            self.help_manager.show_help(topic_id="vocabulary_extraction")
    
    def _show_ai_help(self):
        """Show AI description help"""
        if self.help_manager:
            self.help_manager.show_help(topic_id="image_analysis")
    
    def _show_export_help(self):
        """Show export help"""
        if self.help_manager:
            self.help_manager.show_help(topic_id="export_options")
    
    def _show_troubleshooting(self):
        """Show troubleshooting"""
        if self.help_manager:
            self.help_manager.show_troubleshooting()
    
    def _show_learning_tips(self):
        """Show learning methodology"""
        if self.help_manager:
            self.help_manager.show_help(topic_id="learning_methodology")
    
    def _show_study_methods(self):
        """Show study methods"""
        if self.help_manager:
            self.help_manager.show_help(topic_id="learning_methodology")
    
    def _show_popular_topics(self):
        """Show popular topics (placeholder)"""
        # This would integrate with the main app to show popular search terms
        pass
    
    def _show_api_links(self):
        """Show API service links (placeholder)"""
        # This would open browser links to API signup pages
        pass
    
    def _perform_sample_search(self):
        """Perform a sample search (placeholder)"""
        # This would trigger a sample search in the main app
        pass
    
    def _show_sample_description(self):
        """Show sample description (placeholder)"""
        # This would show the sample walkthrough
        pass
    
    def _start_tour(self):
        """Start onboarding tour (placeholder)"""
        # This would integrate with the onboarding system
        pass
    
    def _start_demo(self):
        """Start demo walkthrough (placeholder)"""
        # This would start the sample walkthrough
        pass
    
    def _skip_onboarding(self):
        """Skip onboarding (placeholder)"""
        # This would skip the onboarding process
        pass
    
    def _test_connection(self):
        """Test internet connection (placeholder)"""
        # This would test API connectivity
        pass