#!/usr/bin/env python3
"""
Content Processor - Handles proper rendering of lesson content

This module ensures that lesson content is properly formatted and displayed
without raw escape sequences or formatting issues.
"""

import re
from typing import Dict, List, Any, Optional


class ContentProcessor:
    """Process and clean lesson content for proper display"""
    
    @staticmethod
    def clean_content(content: str) -> str:
        """Remove or process escape sequences and format content properly"""
        # Remove ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        content = ansi_escape.sub('', content)
        
        # Clean up common formatting issues
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '    ')
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
        
        # Remove excessive whitespace while preserving structure
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Preserve indentation but remove trailing whitespace
            cleaned_lines.append(line.rstrip())
        
        return '\n'.join(cleaned_lines)
    
    @staticmethod
    def format_big_o_content() -> Dict[str, Any]:
        """Generate properly formatted Big O complexity content"""
        return {
            "title": "Big O Notation - Real-World Impact",
            "sections": [
                {
                    "header": "🌟 Why This Matters",
                    "content": """Think about searching for a specific friend's phone number in your contacts.
If you have 100 contacts and scroll through them one by one, that's O(n) - linear time.
But if your phone sorts them alphabetically and you jump to the right letter, that's 
O(log n) - logarithmic time. The difference? Finding 1 contact among 1,000,000 takes:

• O(n): Up to 1,000,000 checks (could take minutes!)
• O(log n): Only ~20 checks (instant!)

That's the power of choosing the right algorithm!"""
                },
                {
                    "header": "📊 Real-World Impact with 1 Million Items",
                    "content": """Here's what these complexities mean for actual running time:

• O(1): 1 operation - instant (like accessing an array element by index)
• O(log n): ~20 operations - instant (like binary search in a sorted list)
• O(n): 1 million operations - ~1 second (like finding max in unsorted list)
• O(n log n): 20 million operations - ~20 seconds (like efficient sorting)
• O(n²): 1 trillion operations - ~11 days! (like comparing every pair)"""
                },
                {
                    "header": "💡 The Key Insight",
                    "content": """Big O isn't about precise timing - it's about understanding how algorithms scale.
An O(n²) algorithm might be faster than O(n) for small inputs, but will always 
lose as data grows. Choose your algorithms based on your expected data size!"""
                },
                {
                    "header": "🎯 Practice Exercises",
                    "content": """1. What's the time complexity of searching for a name in an unsorted list?
   Answer: O(n) - you might need to check every element

2. If an algorithm takes 1 second for 1000 items and 4 seconds for 2000 items, 
   what's likely its complexity?
   Answer: O(n²) - time quadruples when input doubles

3. Why might you choose an O(n²) algorithm over an O(n log n) algorithm?
   Answer: For small datasets (n < 10), the simpler O(n²) might be faster 
   due to lower overhead and better cache performance."""
                }
            ],
            "key_takeaway": """Remember: The best algorithm depends on your specific use case. 
A simple O(n²) sort might be perfect for sorting 10 items, while you'd need 
O(n log n) for a million items. Always consider your data size and constraints!"""
        }
    
    @staticmethod
    def format_lesson_content(raw_content: str) -> str:
        """Format raw lesson content for display"""
        # Clean the content first
        content = ContentProcessor.clean_content(raw_content)
        
        # Add proper spacing and formatting
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Handle headers (lines starting with > or #)
            if line.startswith('>'):
                line = line[1:].strip()
                formatted_lines.append(f"\n{line}\n")
            elif line.startswith('#'):
                # Convert markdown headers
                level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('#').strip()
                formatted_lines.append(f"\n{'=' * (40 - level * 5)}\n{header_text}\n{'=' * (40 - level * 5)}")
            elif line.startswith('*') or line.startswith('-'):
                # Format bullet points
                formatted_lines.append(f"  {line}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def wrap_text(text: str, width: int = 80) -> str:
        """Wrap text to specified width while preserving formatting"""
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            # Don't wrap headers or bullet points
            if line.startswith('#') or line.startswith('*') or line.startswith('-') or line.startswith('  '):
                wrapped_lines.append(line)
                continue
            
            # Simple word wrapping for regular paragraphs
            if len(line) <= width:
                wrapped_lines.append(line)
            else:
                words = line.split()
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 <= width:
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        if current_line:
                            wrapped_lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                
                if current_line:
                    wrapped_lines.append(' '.join(current_line))
        
        return '\n'.join(wrapped_lines)