"""
Central help system manager that coordinates all help components
Provides context-sensitive help and integrates with onboarding
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Callable
import json
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .help_browser import HelpBrowser
from .faq_system import FAQSystem
from .troubleshooting_wizard import TroubleshootingWizard
from .feedback_system import FeedbackSystem
from .empty_states import EmptyStateManager
from .tutorial_system import TutorialSystem


class HelpContext(Enum):
    """Different contexts where help can be requested"""
    GENERAL = "general"
    SEARCH = "search" 
    API_SETUP = "api_setup"
    IMAGE_VIEWING = "image_viewing"
    DESCRIPTION_GENERATION = "description_generation"
    VOCABULARY_EXTRACTION = "vocabulary_extraction"
    EXPORT = "export"
    TROUBLESHOOTING = "troubleshooting"
    SETTINGS = "settings"


@dataclass
class HelpTopic:
    """A help topic definition"""
    id: str
    title: str
    content: str
    keywords: List[str]
    context: HelpContext
    difficulty: str = "beginner"  # beginner, intermediate, advanced
    video_url: Optional[str] = None
    related_topics: List[str] = None
    
    def __post_init__(self):
        if self.related_topics is None:
            self.related_topics = []


class HelpManager:
    """
    Central manager for all help system components
    Coordinates help delivery based on context and user needs
    """
    
    def __init__(self, parent: tk.Tk, theme_manager, config_manager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.config_manager = config_manager
        
        # Help system components
        self.help_browser = None
        self.faq_system = None
        self.troubleshooting_wizard = None
        self.feedback_system = None
        self.empty_state_manager = None
        self.tutorial_system = None
        
        # Help content
        self.help_topics = []
        self._load_help_content()
        
        # Usage tracking
        self.help_usage = {
            'topics_viewed': set(),
            'searches_performed': 0,
            'feedback_submitted': 0,
            'tutorials_watched': set()
        }
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all help system components"""
        self.help_browser = HelpBrowser(
            self.parent, 
            self.theme_manager, 
            self.help_topics,
            on_topic_view=self._track_topic_view
        )
        
        self.faq_system = FAQSystem(
            self.parent,
            self.theme_manager,
            self.help_topics
        )
        
        self.troubleshooting_wizard = TroubleshootingWizard(
            self.parent,
            self.theme_manager,
            self.config_manager
        )
        
        self.feedback_system = FeedbackSystem(
            self.parent,
            self.theme_manager,
            self.config_manager,
            on_feedback_submit=self._track_feedback
        )
        
        self.empty_state_manager = EmptyStateManager(
            self.theme_manager,
            self
        )
        
        self.tutorial_system = TutorialSystem(
            self.parent,
            self.theme_manager,
            on_tutorial_complete=self._track_tutorial
        )
    
    def _load_help_content(self):
        """Load help content from definitions"""
        self.help_topics = [
            # Getting Started
            HelpTopic(
                id="getting_started",
                title="Getting Started with Spanish Learning",
                content="""Welcome to your Spanish learning journey with AI-powered image descriptions!
                
This application helps you build vocabulary by:
1. Searching for images on any topic
2. Getting detailed Spanish descriptions from AI
3. Extracting useful vocabulary automatically
4. Exporting words to study apps like Anki

**First Steps:**
- Set up your API keys (Unsplash + OpenAI)
- Try searching for familiar topics like 'comida' or 'naturaleza'
- Read the AI descriptions carefully
- Click blue words to add them to your vocabulary

**Learning Tips:**
- Start with topics you're interested in
- Add notes before generating descriptions for better context
- Review your vocabulary list regularly
- Export words for spaced repetition study""",
                keywords=["getting started", "introduction", "first time", "how to use"],
                context=HelpContext.GENERAL,
                difficulty="beginner",
                related_topics=["api_setup", "first_search", "vocabulary_basics"]
            ),
            
            # API Setup Help
            HelpTopic(
                id="api_setup",
                title="Setting Up API Keys",
                content="""You need two API keys to use this application:

**Unsplash API Key (for images):**
1. Go to https://unsplash.com/developers
2. Create a free developer account
3. Create a new application
4. Copy your Access Key (NOT the Secret Key)
5. Paste it in the app settings

**OpenAI API Key (for AI descriptions):**
1. Go to https://platform.openai.com/api-keys  
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Name your key (e.g., "Spanish Learning App")
5. Copy the key immediately (you won't see it again)
6. Paste it in the app settings

**Important Notes:**
- Keep your API keys private and secure
- Unsplash: 50 free requests/hour
- OpenAI: Pay-per-use (very affordable for learning)
- GPT-4 Vision recommended for best image analysis

**Troubleshooting:**
- If keys don't work, double-check they're copied correctly
- Ensure no extra spaces before/after the keys
- For OpenAI, make sure billing is set up in your account""",
                keywords=["api", "keys", "setup", "unsplash", "openai", "configuration"],
                context=HelpContext.API_SETUP,
                difficulty="beginner",
                video_url="https://example.com/api-setup-tutorial",
                related_topics=["troubleshooting_api", "getting_started"]
            ),
            
            # Search Help
            HelpTopic(
                id="effective_searching",
                title="How to Search Effectively",
                content="""Get the best learning results with smart searching:

**Search Strategies:**
- Use Spanish terms for authentic results: 'mercado', 'playa', 'familia'
- English works too: 'market', 'beach', 'family'
- Try specific topics: 'cocina mexicana', 'arquitectura española'
- Explore categories: food, nature, culture, technology

**Best Topics for Learning:**
- **Beginner:** comida, casa, familia, colores, animales
- **Intermediate:** trabajo, viajes, deportes, música, arte  
- **Advanced:** tecnología, filosofía, arquitectura, literatura

**Search Tips:**
- Be specific: 'tacos mexicanos' vs 'comida'
- Try regional variations: 'paella española', 'empanadas argentinas'
- Use cultural terms: 'día de los muertos', 'flamenco'
- Combine concepts: 'mercado de flores', 'café cubano'

**What Makes a Good Search:**
- Images with clear, identifiable objects
- Cultural context for rich vocabulary
- Multiple elements to describe
- Authentic settings and situations

**Avoiding Poor Results:**
- Avoid abstract concepts without clear visuals
- Skip overly simple images with minimal vocabulary
- Don't use extremely long or complex search terms""",
                keywords=["search", "topics", "vocabulary", "strategies", "tips"],
                context=HelpContext.SEARCH,
                difficulty="beginner",
                related_topics=["vocabulary_basics", "getting_started", "image_analysis"]
            ),
            
            # Image Analysis Help  
            HelpTopic(
                id="image_analysis",
                title="Understanding AI Image Descriptions",
                content="""Learn how to get the most from AI-generated descriptions:

**What the AI Analyzes:**
- Objects, people, animals in the image
- Colors, shapes, and visual details
- Setting and environment (indoor/outdoor)
- Activities and actions occurring
- Cultural and contextual elements
- Mood and atmosphere

**Description Quality Tips:**
- Add your own notes before generating descriptions
- Zoom in to notice more details
- Describe what interests you most
- Mention cultural context you recognize

**Understanding the Spanish:**
- Descriptions use natural, conversational Spanish
- Vocabulary ranges from basic to intermediate
- Grammar structures are educational examples
- Regional variations may appear
- Context helps with comprehension

**Learning from Descriptions:**
- Read the full description first
- Look for new vocabulary patterns
- Notice grammar structures
- Pay attention to adjective agreements
- Observe verb tenses used

**Maximizing Learning:**
- Compare similar images to see vocabulary variations
- Note how the same concepts are expressed differently
- Build connections between related vocabulary
- Practice reading aloud for pronunciation""",
                keywords=["ai", "descriptions", "analysis", "image", "spanish", "quality"],
                context=HelpContext.DESCRIPTION_GENERATION,
                difficulty="intermediate",
                related_topics=["vocabulary_extraction", "spanish_grammar", "learning_tips"]
            ),
            
            # Vocabulary System
            HelpTopic(
                id="vocabulary_extraction",
                title="Building Your Vocabulary List",
                content="""Master the vocabulary extraction and learning system:

**How Extraction Works:**
- AI identifies useful Spanish vocabulary automatically
- Words grouped by type: nouns, verbs, adjectives, phrases
- Includes articles with nouns (el/la/los/las)
- Shows conjugated verb forms as they appear
- Extracts common phrases and expressions

**Selecting Words:**
- Click any blue word to add to your list
- Words are automatically translated to English
- Context from the image description is preserved
- Duplicates are automatically filtered out
- Focus on words relevant to your interests

**Vocabulary Categories:**
- **Sustantivos:** Nouns with correct articles
- **Verbos:** Verbs in their used form
- **Adjetivos:** Descriptive words with gender agreement
- **Adverbios:** Words that modify verbs/adjectives  
- **Frases clave:** Useful multi-word expressions

**Learning Strategies:**
- Start with nouns (easiest to remember)
- Learn adjectives that describe things you see
- Focus on high-frequency verbs
- Collect phrases for natural communication
- Build thematic vocabulary sets

**Vocabulary Management:**
- Review your list regularly in the app
- Export to Anki for spaced repetition
- Group words by topic or difficulty
- Create personal connections with each word
- Practice using words in your own sentences""",
                keywords=["vocabulary", "extraction", "learning", "words", "translation", "lists"],
                context=HelpContext.VOCABULARY_EXTRACTION,
                difficulty="beginner",
                related_topics=["export_options", "study_methods", "spanish_grammar"]
            ),
            
            # Export and Study
            HelpTopic(
                id="export_options", 
                title="Exporting Your Vocabulary for Study",
                content="""Get your vocabulary into your favorite study tools:

**Export Formats Available:**

**📚 Anki Format:**
- Tab-delimited format for easy import
- Spanish on front, English + context on back
- Perfect for spaced repetition learning
- Maintains learning progress and statistics
- Best for long-term retention

**📊 CSV Format:**
- Works with Excel, Google Sheets, Numbers
- Includes search query and image context
- Easy to sort and organize
- Add your own columns for notes
- Great for creating custom study materials

**📝 Text Format:**  
- Simple, readable format
- Perfect for printing or quick reference
- Shows word pairs with context
- Easy to share or email
- Good for traditional study methods

**💾 JSON Format:**
- Structured data with full metadata
- Includes timestamps and context
- For advanced users and developers
- Preserves all collected information

**Study Tips:**
- Export regularly to avoid losing progress
- Use Anki for daily spaced repetition
- Create themed decks by topic
- Review CSV files to see learning patterns
- Combine formats for different study styles

**Best Practices:**
- Export after each learning session
- Organize by difficulty or topic
- Back up your vocabulary data
- Share interesting words with study partners""",
                keywords=["export", "anki", "csv", "study", "vocabulary", "formats"],
                context=HelpContext.EXPORT,
                difficulty="beginner",
                related_topics=["vocabulary_extraction", "study_methods", "anki_setup"]
            ),
            
            # Troubleshooting
            HelpTopic(
                id="common_issues",
                title="Common Issues and Solutions",
                content="""Quick solutions to common problems:

**API Key Issues:**
- **"Invalid API Key":** Double-check key is copied correctly
- **"Rate limit exceeded":** Wait for reset (Unsplash: hourly, OpenAI: varies)
- **"Quota exceeded":** Check your OpenAI billing settings
- **Keys not saving:** Run app as administrator or check file permissions

**Search Problems:**
- **No images found:** Try different search terms or check spelling
- **Same images repeating:** Clear cache or try more specific searches  
- **Images won't load:** Check internet connection
- **Slow searching:** Server may be busy, try again later

**Description Issues:**
- **No description generated:** Verify OpenAI API key and quota
- **Description in wrong language:** Check GPT model settings
- **Poor quality descriptions:** Add more detailed notes before generating
- **Timeouts:** Try with smaller images or check connection

**Vocabulary Problems:**
- **No words extracted:** Description may be too short or simple
- **Words not clickable:** Wait for extraction to complete
- **Translations missing:** Check OpenAI API connectivity
- **Duplicates appearing:** This is normal, duplicates are filtered

**App Performance:**
- **Slow startup:** Check antivirus settings, add app to exclusions
- **High memory usage:** Restart app periodically for long sessions
- **Freezing/crashing:** Update to latest version, restart computer
- **Theme issues:** Try toggling between light/dark themes

**Getting Help:**
- Use the troubleshooting wizard for step-by-step diagnosis
- Check the FAQ for quick answers
- Submit feedback through the app
- Contact support with specific error messages""",
                keywords=["troubleshooting", "problems", "issues", "solutions", "errors", "bugs"],
                context=HelpContext.TROUBLESHOOTING,
                difficulty="beginner",
                related_topics=["api_setup", "performance_tips", "getting_support"]
            ),
            
            # Advanced Features
            HelpTopic(
                id="advanced_features",
                title="Advanced Features and Tips",
                content="""Unlock the full potential of your Spanish learning:

**Keyboard Shortcuts:**
- Ctrl+N: New search
- Ctrl+G: Generate description  
- Ctrl+E: Export vocabulary
- Ctrl+T: Toggle theme
- Ctrl+Plus/Minus: Zoom image
- Ctrl+0: Reset zoom
- F1: Open help
- Ctrl+Q: Quit app

**Image Viewing Tips:**
- Use mouse wheel + Ctrl to zoom
- Scroll around zoomed images
- Look for small details that add vocabulary
- Pay attention to background elements
- Notice text in images for reading practice

**Learning Optimization:**
- Set daily vocabulary goals
- Focus on specific topics for deeper learning
- Create themed learning sessions
- Mix difficulty levels for balanced progress
- Review previous vocabulary regularly

**Customization Options:**
- Switch between light/dark themes
- Adjust font sizes for comfort
- Configure export preferences
- Set preferred GPT model for quality/cost balance
- Customize vocabulary extraction settings

**Productivity Features:**
- Batch process multiple images
- Save favorite searches for quick access
- Export vocabulary in multiple formats
- Track learning progress over time
- Share interesting finds with study partners

**Integration with Other Tools:**
- Import vocabulary to language learning apps
- Use with flashcard systems
- Combine with grammar study resources
- Supplement conversation practice
- Enhance reading comprehension skills""",
                keywords=["advanced", "features", "shortcuts", "tips", "optimization", "productivity"],
                context=HelpContext.GENERAL,
                difficulty="advanced",
                related_topics=["keyboard_shortcuts", "customization", "productivity_tips"]
            ),
            
            # Learning Methodology
            HelpTopic(
                id="learning_methodology",
                title="Effective Spanish Learning with Images",
                content="""Maximize your Spanish learning with proven visual learning techniques:

**Visual Learning Theory:**
- Images provide context that aids memory retention
- Visual associations create stronger neural pathways  
- Cultural context in images enhances understanding
- Multiple senses engaged improve learning outcomes
- Real-world imagery shows authentic language use

**Learning Progression:**
1. **Observation:** Study the image carefully before reading
2. **Prediction:** Guess what vocabulary might appear
3. **Analysis:** Read the AI description thoughtfully
4. **Extraction:** Select vocabulary that interests you
5. **Review:** Study collected words with spaced repetition
6. **Application:** Try using new words in your own sentences

**Building Vocabulary Systematically:**
- **Week 1:** Focus on concrete nouns (objects, animals, food)
- **Week 2:** Add descriptive adjectives (colors, sizes, qualities)
- **Week 3:** Include action verbs (what people are doing)
- **Week 4:** Collect useful phrases and expressions
- **Ongoing:** Mix all categories based on interests

**Cultural Learning Benefits:**
- Understand cultural context of vocabulary
- Learn regional variations and preferences
- Discover traditions and customs through images
- Build cultural competency alongside language skills
- Prepare for real-world interactions

**Memory Techniques:**
- Create mental associations between images and words
- Use the story method to link vocabulary
- Practice active recall with your exported lists
- Space your review sessions for optimal retention
- Connect new words to personal experiences

**Measuring Progress:**
- Track vocabulary acquisition over time
- Notice increasing comprehension of descriptions
- Test retention with spaced repetition
- Challenge yourself with more complex topics
- Celebrate milestones and achievements""",
                keywords=["learning", "methodology", "visual", "spanish", "techniques", "progress"],
                context=HelpContext.GENERAL,  
                difficulty="intermediate",
                related_topics=["study_methods", "vocabulary_extraction", "cultural_learning"]
            )
        ]
    
    def show_help(self, context: HelpContext = HelpContext.GENERAL, 
                  topic_id: Optional[str] = None, widget: Optional[tk.Widget] = None):
        """Show context-appropriate help"""
        if topic_id:
            # Show specific topic
            topic = self._find_topic(topic_id)
            if topic:
                self.help_browser.show_topic(topic)
            else:
                self.help_browser.show(context)
        else:
            # Show general help for context
            self.help_browser.show(context)
    
    def show_faq(self):
        """Show frequently asked questions"""
        if not self.faq_system:
            return
        self.faq_system.show()
    
    def show_troubleshooting(self):
        """Show troubleshooting wizard"""
        if not self.troubleshooting_wizard:
            return
        self.troubleshooting_wizard.show()
    
    def show_feedback(self):
        """Show feedback system"""
        if not self.feedback_system:
            return
        self.feedback_system.show()
    
    def show_tutorial(self, tutorial_id: str):
        """Show a specific tutorial"""
        if not self.tutorial_system:
            return
        self.tutorial_system.show_tutorial(tutorial_id)
    
    def get_contextual_help(self, context: HelpContext) -> List[HelpTopic]:
        """Get help topics for a specific context"""
        return [topic for topic in self.help_topics if topic.context == context]
    
    def search_help(self, query: str) -> List[HelpTopic]:
        """Search help topics by query"""
        query = query.lower()
        matching_topics = []
        
        for topic in self.help_topics:
            # Check title, content, and keywords
            if (query in topic.title.lower() or
                query in topic.content.lower() or
                any(query in keyword.lower() for keyword in topic.keywords)):
                matching_topics.append(topic)
        
        return matching_topics
    
    def get_empty_state(self, state_type: str) -> Dict[str, str]:
        """Get empty state content"""
        if not self.empty_state_manager:
            return {}
        return self.empty_state_manager.get_empty_state(state_type)
    
    def _find_topic(self, topic_id: str) -> Optional[HelpTopic]:
        """Find a help topic by ID"""
        for topic in self.help_topics:
            if topic.id == topic_id:
                return topic
        return None
    
    def _track_topic_view(self, topic_id: str):
        """Track when a help topic is viewed"""
        self.help_usage['topics_viewed'].add(topic_id)
    
    def _track_feedback(self, feedback_type: str):
        """Track feedback submission"""
        self.help_usage['feedback_submitted'] += 1
    
    def _track_tutorial(self, tutorial_id: str):
        """Track tutorial completion"""
        self.help_usage['tutorials_watched'].add(tutorial_id)
    
    def get_help_statistics(self) -> Dict[str, Any]:
        """Get help system usage statistics"""
        return {
            'topics_available': len(self.help_topics),
            'topics_viewed': len(self.help_usage['topics_viewed']),
            'searches_performed': self.help_usage['searches_performed'],
            'feedback_submitted': self.help_usage['feedback_submitted'],
            'tutorials_watched': len(self.help_usage['tutorials_watched'])
        }
    
    def add_help_topic(self, topic: HelpTopic):
        """Add a custom help topic"""
        self.help_topics.append(topic)
        if self.help_browser:
            self.help_browser.refresh_topics()
    
    def update_help_topic(self, topic_id: str, updated_topic: HelpTopic):
        """Update an existing help topic"""
        for i, topic in enumerate(self.help_topics):
            if topic.id == topic_id:
                self.help_topics[i] = updated_topic
                if self.help_browser:
                    self.help_browser.refresh_topics()
                break