#!/usr/bin/env python3
"""
Simple demonstration of the extracted questionnaire functionality
Shows how to use the core components without the GUI
"""

import os
import sys
import time

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from questionnaire_core import SessionManager, ProgressTracker


def simple_questionnaire_demo():
    """Simple command-line questionnaire demo"""
    print("=" * 50)
    print("Simple Questionnaire Demo")
    print("=" * 50)
    
    # Create session manager
    session_mgr = SessionManager("demo_sessions")
    
    # Questions to ask
    questions = [
        "What is your name?",
        "What is your favorite programming language?",
        "What project are you most proud of?",
        "What do you want to learn next?",
        "Any final thoughts?"
    ]
    
    # Start session
    session_id = session_mgr.start_session(len(questions))
    print(f"Starting session: {session_id}")
    print(f"Total questions: {len(questions)}\n")
    
    # Setup progress tracking
    progress = ProgressTracker()
    progress.set_total_questions(len(questions))
    
    def show_progress(current, total):
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * current // total)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"Progress: [{bar}] {current}/{total} ({percentage:.1f}%)")
    
    progress.add_progress_callback(show_progress)
    
    # Ask questions
    for i, question in enumerate(questions):
        print(f"\nQuestion {i + 1}/{len(questions)}:")
        print(f"{question}")
        
        # Get user input
        start_time = time.time()
        answer = input("Your answer: ").strip()
        processing_time = int((time.time() - start_time) * 1000)
        
        # Handle empty answers
        if not answer:
            answer = "[No answer provided]"
        
        # Add response to session
        session_mgr.add_response(
            question_id=i,
            question_text=question,
            answer=answer,
            processing_time_ms=processing_time,
            additional_data={"input_method": "keyboard"}
        )
        
        # Update progress
        progress.advance_question()
        print()
    
    # End session
    csv_path = session_mgr.end_session()
    
    print("\n" + "=" * 50)
    print("Questionnaire Complete!")
    print(f"Your responses have been saved to: {csv_path}")
    print("=" * 50)
    
    # Show CSV content preview
    if os.path.exists(csv_path):
        print("\nYour session data (first 10 lines):")
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
            for i, line in enumerate(lines):
                print(f"{i+1:2}: {line.strip()}")
        
        if len(lines) >= 10:
            print("    ... (more data in file)")
    
    return csv_path


if __name__ == "__main__":
    try:
        csv_path = simple_questionnaire_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()