#!/usr/bin/env python3
"""
Apply Claude Enhancements to Existing CLI
This script patches the existing curriculum_cli_enhanced.py with Claude integration
Run this to upgrade your existing CLI with all the new features!
"""

import os
import sys
from pathlib import Path

def apply_enhancements():
    """Apply Claude enhancements to the existing CLI"""
    
    print("🚀 Applying Claude Enhancements to your CLI...")
    print("="*60)
    
    # Check if files exist
    base_dir = Path(__file__).parent.parent
    cli_path = base_dir / "curriculum_cli_enhanced.py"
    
    if not cli_path.exists():
        print("❌ Error: curriculum_cli_enhanced.py not found!")
        print(f"   Looking in: {cli_path}")
        return False
    
    # Check if enhancement files exist
    enhancement_path = Path(__file__).parent / "enhanced_learning_system.py"
    claude_helper_path = Path(__file__).parent / "claude_helper.py"
    
    if not enhancement_path.exists():
        print("❌ Error: enhanced_learning_system.py not found!")
        return False
    
    # Create the integration code
    integration_code = '''
# ============================================================================
# CLAUDE AI INTEGRATION - Added by apply_claude_enhancements.py
# ============================================================================

try:
    from src.enhanced_learning_system import CLIClaudeIntegration, ComprehensiveLearningEnhancer
    CLAUDE_INTEGRATION_AVAILABLE = True
    claude_integration = CLIClaudeIntegration()
    learning_enhancer = ComprehensiveLearningEnhancer()
    print("✅ Claude AI Integration loaded successfully!")
except ImportError:
    CLAUDE_INTEGRATION_AVAILABLE = False
    print("ℹ️  Claude integration not available - continuing with base features")

def display_claude_help(lesson):
    """Display Claude assistance for a lesson"""
    if not CLAUDE_INTEGRATION_AVAILABLE:
        return ""
    
    return claude_integration.enhance_lesson_display(lesson)

def format_question_for_claude(lesson, question):
    """Format a question with context for Claude"""
    if not CLAUDE_INTEGRATION_AVAILABLE:
        return f"Question about {lesson.get('title', 'this topic')}: {question}"
    
    return claude_integration.format_question_for_claude(lesson, question)

def save_claude_discussion_as_note(question, response, lesson):
    """Save Claude discussion as a structured note"""
    if not CLAUDE_INTEGRATION_AVAILABLE:
        return f"Q: {question}\\nA: {response[:200]}..."
    
    return claude_integration.save_claude_discussion(question, response, lesson)

# Monkey-patch the existing methods to add Claude features
original_display_lesson = CurriculumCLI.display_lesson
original_interactive_menu = CurriculumCLI.interactive_learning_menu if hasattr(CurriculumCLI, 'interactive_learning_menu') else None

def enhanced_display_lesson(self, lesson):
    """Enhanced lesson display with Claude assistance"""
    # Show Claude help before the lesson
    if CLAUDE_INTEGRATION_AVAILABLE:
        claude_help = display_claude_help(lesson)
        if claude_help:
            console.print(claude_help)
    
    # Call original method
    return original_display_lesson(self, lesson)

def enhanced_interactive_menu(self, lesson):
    """Enhanced interactive menu with Claude features"""
    console.print("\\n" + "="*80)
    console.print("[bold cyan]Interactive Learning Menu[/bold cyan]")
    console.print("="*80)
    console.print()
    console.print("[bold]Choose an option:[/bold]")
    console.print("1. 📝 Add a note about this lesson")
    console.print("2. ❓ Prepare a question for Claude")
    console.print("3. 🔍 View suggested questions for this topic")
    console.print("4. 📚 Review your notes")
    
    if CLAUDE_INTEGRATION_AVAILABLE:
        console.print("5. 🤖 Get Claude-formatted context")
        console.print("6. 🎯 View practice problems")
        console.print("7. ✅ Continue to comprehension check")
    else:
        console.print("5. ✅ Continue to comprehension check")
    
    console.print()
    
    all_notes = []
    
    while True:
        max_choice = "7" if CLAUDE_INTEGRATION_AVAILABLE else "5"
        choice = Prompt.ask("Your choice", choices=["1","2","3","4","5","6","7"][:int(max_choice)], default=max_choice)
        
        if choice == "1":
            note = Prompt.ask("\\n[bold]Enter your note[/bold]")
            if note:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                all_notes.append(f"[{timestamp}] {note}")
                console.print("[green]✓ Note saved![/green]")
        
        elif choice == "2":
            question = Prompt.ask("\\n[bold]What would you like to ask about this lesson?[/bold]")
            if question:
                if CLAUDE_INTEGRATION_AVAILABLE:
                    formatted = format_question_for_claude(lesson, question)
                    console.print("\\n[bold green]Question formatted for Claude:[/bold green]")
                    console.print(Panel(formatted[:500] + "..." if len(formatted) > 500 else formatted))
                    console.print("[dim]Copy this to Claude Code for a detailed answer![/dim]")
                    all_notes.append(f"Question: {question}")
                else:
                    all_notes.append(f"Question: {question}")
                    console.print("[yellow]Save this question to ask Claude later![/yellow]")
        
        elif choice == "3":
            if CLAUDE_INTEGRATION_AVAILABLE and hasattr(learning_enhancer, 'analyze_lesson_for_questions'):
                questions = learning_enhancer.analyze_lesson_for_questions(lesson)
                console.print("\\n[bold]Suggested Questions:[/bold]")
                for category, q_list in list(questions.items())[:3]:
                    if q_list:
                        console.print(f"\\n[cyan]{category.upper()}:[/cyan]")
                        for q in q_list[:2]:
                            console.print(f"  • {q}")
            else:
                console.print("\\n[bold]Consider asking:[/bold]")
                console.print(f"  • Why does {lesson.get('title', 'this')} work this way?")
                console.print(f"  • What are real-world applications?")
                console.print(f"  • How does this compare to alternatives?")
        
        elif choice == "4":
            if all_notes:
                console.print("\\n[bold]Your notes:[/bold]")
                for note in all_notes:
                    console.print(f"  • {note}")
            else:
                console.print("[yellow]No notes yet[/yellow]")
        
        elif choice == "5" and CLAUDE_INTEGRATION_AVAILABLE:
            context = format_question_for_claude(lesson, "Explain this concept in detail")
            console.print("\\n[bold]Full context for Claude:[/bold]")
            console.print(Panel(context[:800] + "..." if len(context) > 800 else context))
            input("\\nPress Enter to continue...")
        
        elif choice == "6" and CLAUDE_INTEGRATION_AVAILABLE:
            if hasattr(learning_enhancer, 'create_practice_problems'):
                problems = learning_enhancer.create_practice_problems(lesson)
                console.print("\\n[bold]Practice Problems:[/bold]")
                for i, p in enumerate(problems[:3], 1):
                    console.print(f"\\n{i}. {p['description']}")
                    console.print(f"   [dim]Hint: {p['hint']}[/dim]")
            input("\\nPress Enter to continue...")
        
        elif (choice == "7" and CLAUDE_INTEGRATION_AVAILABLE) or (choice == "5" and not CLAUDE_INTEGRATION_AVAILABLE):
            break
    
    return "\\n---\\n".join(all_notes) if all_notes else ""

# Apply the patches
CurriculumCLI.display_lesson = enhanced_display_lesson
CurriculumCLI.interactive_learning_menu = enhanced_interactive_menu

print("✅ Claude enhancements applied successfully!")
print("🤖 Claude AI features are now integrated into your CLI!")

# ============================================================================
# END CLAUDE AI INTEGRATION
# ============================================================================
'''
    
    # Read the existing CLI file
    print("📖 Reading existing CLI file...")
    with open(cli_path, 'r', encoding='utf-8') as f:
        cli_content = f.read()
    
    # Check if already patched
    if "CLAUDE AI INTEGRATION" in cli_content:
        print("ℹ️  CLI already has Claude enhancements applied!")
        return True
    
    # Find where to insert the code (after imports but before main class)
    lines = cli_content.split('\n')
    insert_index = -1
    
    # Find the last import statement
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_index = i + 1
        elif line.startswith('class CurriculumCLI'):
            if insert_index == -1:
                insert_index = i - 1
            break
    
    if insert_index == -1:
        print("❌ Could not find appropriate place to insert enhancements")
        return False
    
    # Insert the integration code
    print("🔧 Applying enhancements...")
    lines.insert(insert_index, integration_code)
    
    # Write back the enhanced file
    enhanced_content = '\n'.join(lines)
    
    # Create backup
    backup_path = cli_path.with_suffix('.py.backup')
    print(f"💾 Creating backup at {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(cli_content)
    
    # Write enhanced version
    with open(cli_path, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print("✅ Enhancements applied successfully!")
    print("\n" + "="*60)
    print("🎉 SUCCESS! Your CLI now has Claude AI integration!")
    print("\nNew features added:")
    print("  • Smart question suggestions")
    print("  • Claude-formatted context generation")
    print("  • Practice problems")
    print("  • Enhanced note-taking")
    print("  • Learning pattern tracking")
    print("\n To use:")
    print("  1. Run your CLI: python curriculum_cli_enhanced.py")
    print("  2. Keep Claude Code open alongside")
    print("  3. Copy suggested questions to Claude for detailed explanations!")
    print("="*60)
    
    return True

def main():
    """Main entry point"""
    success = apply_enhancements()
    
    if not success:
        print("\n❌ Enhancement failed. Please check the errors above.")
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()