"""
Claude Conversation Handler - SPARC Implementation

SPECIFICATION:
- Input: User text + conversation context
- Output: Intelligent response with follow-up questions
- Constraints: < 900ms response time, < 3 sentences
- Intelligence: Ask clarifying questions, connect ideas

PSEUDOCODE:
1. Get last 5 exchanges from context
2. Format system + user prompt
3. Call Claude Haiku API
4. Post-process response (add fallback if needed)
5. Return response

ARCHITECTURE:
- Single responsibility: Only handles Claude interaction
- Dependency injection: Pass in state manager
- Error boundaries: Graceful fallback responses

REFINEMENT:
- Cache frequently used prompts
- Batch API calls when possible
- Use streaming for lower latency perception

CODE:
"""
from typing import List, Dict, Optional
import anthropic
from app.config import settings
import re

class ConversationHandler:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.system_prompt = self._create_system_prompt()
        
    def _create_system_prompt(self) -> str:
        """
        CONCEPT: Carefully crafted system prompt
        WHY: The prompt IS the intelligence - no complex logic needed
        PATTERN: Behavioral specification through examples
        """
        return """You are a personal learning companion helping capture and develop ideas. 

Your role:
- Ask ONE clarifying question when responses are vague or under 10 words
- Connect new ideas to previously mentioned topics in the conversation
- When user lists items, ask "What else?" once, then summarize
- Keep responses under 3 sentences
- Never lecture or provide long explanations unless explicitly asked

Response style:
- Be curious and encouraging
- Use natural, conversational language
- Mirror the user's energy level
- Focus on helping them articulate their thoughts

Special behaviors:
- If user says something profound, acknowledge it briefly
- If they're stuck, offer a gentle prompt like "What made you think of that?"
- If they say goodbye or want to end, confirm and summarize key points"""

    def _format_context(self, exchanges: List[Dict]) -> str:
        """
        PATTERN: Context window formatting
        WHY: Claude needs structured context for coherence
        """
        if not exchanges:
            return "This is the start of our conversation."
        
        context_lines = []
        for exchange in exchanges:
            context_lines.append(f"User: {exchange.get('user', '')}")
            context_lines.append(f"You: {exchange.get('agent', '')}")
        
        return "Previous conversation:\n" + "\n".join(context_lines)
    
    def _should_add_followup(self, user_text: str, response: str) -> bool:
        """
        CONCEPT: Intelligent fallback detection
        WHY: Ensure conversation continues even with short responses
        """
        # Check if response already contains a question
        has_question = "?" in response
        
        # Check if user input is very short
        is_short_input = len(user_text.split()) <= 3
        
        # Check if response is conversational ender
        enders = ["goodbye", "bye", "see you", "thank you", "thanks"]
        is_ending = any(end in response.lower() for end in enders)
        
        return is_short_input and not has_question and not is_ending
    
    async def generate_response(
        self,
        user_text: str,
        context: List[Dict],
        session_metadata: Optional[Dict] = None
    ) -> str:
        """
        PATTERN: Main conversation logic with error handling
        WHY: Centralized intelligence with graceful degradation
        """
        try:
            # Format the context
            context_str = self._format_context(context)
            
            # Build the user message
            user_message = f"{context_str}\n\nUser just said: {user_text}\n\nRespond naturally and help them capture their learning effectively."
            
            # Call Claude API
            message = await self.client.messages.create(
                model=settings.claude_model,
                max_tokens=settings.claude_max_tokens,
                temperature=settings.claude_temperature,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            response = message.content[0].text.strip()
            
            # Add follow-up if needed
            if self._should_add_followup(user_text, response):
                followups = [
                    "Tell me more about that.",
                    "What made you think of that?",
                    "Can you elaborate?",
                    "What's the connection there?",
                    "How does that relate to what you're learning?"
                ]
                import random
                response += f" {random.choice(followups)}"
            
            return response
            
        except anthropic.RateLimitError:
            return "I need a moment to catch up. Could you repeat that?"
        except anthropic.APIError as e:
            print(f"Claude API error: {e}")
            return "I'm having trouble connecting right now. Let's try again - what were you saying?"
        except Exception as e:
            print(f"Unexpected error in conversation handler: {e}")
            return "Something went wrong on my end. Could you say that again?"
    
    def detect_intent(self, text: str) -> str:
        """
        CONCEPT: Simple intent detection without ML
        WHY: Fast, deterministic, good enough for our needs
        """
        text_lower = text.lower().strip()
        
        # Ending intents
        if any(word in text_lower for word in ["goodbye", "bye", "see you later", "talk to you later"]):
            return "end_conversation"
        
        # Question intents
        if text_lower.startswith(("what", "why", "how", "when", "where", "who")):
            return "question"
        
        # List intents  
        if any(word in text_lower for word in ["first", "second", "next", "then", "also"]):
            return "listing"
        
        # Reflection intents
        if any(word in text_lower for word in ["realize", "think", "feel", "believe", "understand"]):
            return "reflection"
        
        return "statement"
    
    def create_summary(self, exchanges: List[Dict]) -> str:
        """
        PATTERN: Context-aware summarization
        WHY: Help users see patterns in their learning
        """
        if not exchanges:
            return "We didn't get to explore any topics today."
        
        # Extract key topics (simple noun phrase extraction)
        all_text = " ".join([e.get("user", "") for e in exchanges])
        
        # Simple topic extraction (could be enhanced with NLP)
        words = all_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Focus on substantial words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if top_topics:
            topics_str = ", ".join([topic[0] for topic in top_topics])
            return f"We explored: {topics_str}. Great conversation!"
        else:
            return "Thanks for sharing your thoughts today!"

# Global conversation handler instance
conversation_handler = ConversationHandler()