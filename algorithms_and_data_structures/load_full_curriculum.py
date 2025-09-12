#!/usr/bin/env python3
"""
Load Full Curriculum Content into the CLI Database
This script loads all the curriculum content from the JSON files into the database.
"""

import json
import sqlite3
from pathlib import Path
import sys

def load_json_file(filepath):
    """Load and parse a JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_curriculum_content(db_path="curriculum.db"):
    """Load all curriculum content from JSON files"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Path to examples directory
    base_path = Path(__file__).parent
    curriculum_path = base_path / "examples" / "curriculum"
    content_path = base_path / "examples" / "content"
    
    print("🔄 Loading curriculum content...")
    
    lesson_count = 0
    
    # Load algorithms fundamentals curriculum
    algo_fund_file = curriculum_path / "algorithms_fundamentals.json"
    if algo_fund_file.exists():
        print(f"📚 Loading: {algo_fund_file.name}")
        data = load_json_file(algo_fund_file)
        curriculum = data.get("curriculum", {})
        
        for module in curriculum.get("modules", []):
            module_title = module.get("title", "")
            module_desc = module.get("description", "")
            
            for lesson in module.get("lessons", []):
                lesson_id = lesson.get("id", "")
                title = f"{module_title}: {lesson.get('title', '')}"
                description = lesson.get("description", "")
                difficulty = lesson.get("difficulty", "beginner")
                estimated_time = lesson.get("estimatedMinutes", 30)
                
                # Extract content
                content_obj = lesson.get("content", {})
                theory = content_obj.get("theory", {})
                
                # Build content text
                content_text = f"# {lesson.get('title', '')}\n\n"
                content_text += f"{description}\n\n"
                
                if isinstance(theory, dict):
                    if "definition" in theory:
                        content_text += f"## Definition\n{theory['definition']}\n\n"
                    if "properties" in theory:
                        content_text += f"## Properties\n"
                        for prop in theory.get("properties", []):
                            content_text += f"- {prop}\n"
                        content_text += "\n"
                
                # Extract code examples
                code_examples = []
                for example in content_obj.get("codeExamples", []):
                    code_examples.append({
                        "language": example.get("language", "python"),
                        "title": example.get("title", ""),
                        "code": example.get("code", "")
                    })
                
                # Extract exercises
                exercises = lesson.get("exercises", [])
                
                # Extract learning objectives
                learning_objectives = lesson.get("learningObjectives", [])
                
                # Insert into database
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO lessons 
                        (id, title, description, content, code_examples, difficulty,
                         estimated_time, prerequisites, learning_objectives, 
                         exercises, quiz_questions, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        lesson_id,
                        title,
                        description,
                        content_text,
                        json.dumps(code_examples),
                        difficulty,
                        estimated_time,
                        json.dumps([]),
                        json.dumps(learning_objectives),
                        json.dumps(exercises),
                        json.dumps([]),
                        json.dumps([module_title.lower(), "algorithms"])
                    ))
                    lesson_count += 1
                    print(f"  ✓ Loaded: {title}")
                except Exception as e:
                    print(f"  ✗ Error loading {title}: {e}")
    
    # Load data structures curriculum
    ds_file = curriculum_path / "data_structures.json"
    if ds_file.exists():
        print(f"📚 Loading: {ds_file.name}")
        data = load_json_file(ds_file)
        curriculum = data.get("curriculum", {})
        
        for module in curriculum.get("modules", []):
            module_title = module.get("title", "")
            
            for lesson in module.get("lessons", []):
                lesson_id = lesson.get("id", "")
                title = f"{module_title}: {lesson.get('title', '')}"
                description = lesson.get("description", "")
                difficulty = lesson.get("difficulty", "beginner")
                estimated_time = lesson.get("estimatedMinutes", 30)
                
                # Extract content
                content_obj = lesson.get("content", {})
                theory = content_obj.get("theory", {})
                
                # Build content text
                content_text = f"# {lesson.get('title', '')}\n\n"
                content_text += f"{description}\n\n"
                
                if isinstance(theory, dict):
                    for key, value in theory.items():
                        if isinstance(value, str):
                            content_text += f"## {key.title()}\n{value}\n\n"
                        elif isinstance(value, list):
                            content_text += f"## {key.title()}\n"
                            for item in value:
                                content_text += f"- {item}\n"
                            content_text += "\n"
                
                # Extract code examples
                code_examples = []
                for example in content_obj.get("codeExamples", []):
                    code_examples.append({
                        "language": example.get("language", "python"),
                        "title": example.get("title", ""),
                        "code": example.get("code", "")
                    })
                
                # Insert into database
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO lessons 
                        (id, title, description, content, code_examples, difficulty,
                         estimated_time, prerequisites, learning_objectives, 
                         exercises, quiz_questions, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        lesson_id,
                        title,
                        description,
                        content_text,
                        json.dumps(code_examples),
                        difficulty,
                        estimated_time,
                        json.dumps([]),
                        json.dumps(lesson.get("learningObjectives", [])),
                        json.dumps(lesson.get("exercises", [])),
                        json.dumps([]),
                        json.dumps([module_title.lower(), "data-structures"])
                    ))
                    lesson_count += 1
                    print(f"  ✓ Loaded: {title}")
                except Exception as e:
                    print(f"  ✗ Error loading {title}: {e}")
    
    # Load content files (sorting, graphs, dynamic programming)
    content_files = [
        "sorting_algorithms.json",
        "graph_algorithms.json", 
        "dynamic_programming.json"
    ]
    
    for filename in content_files:
        filepath = content_path / filename
        if filepath.exists():
            print(f"📚 Loading: {filename}")
            data = load_json_file(filepath)
            
            # Process lessons from content files
            lessons = data.get("lessons", [])
            for lesson in lessons:
                lesson_id = lesson.get("id", "")
                title = lesson.get("title", "")
                description = lesson.get("description", "")
                difficulty = lesson.get("difficulty", "intermediate")
                estimated_time = lesson.get("estimatedTime", 45)
                
                # Build content
                content_text = f"# {title}\n\n{description}\n\n"
                
                theory = lesson.get("theory", {})
                if theory:
                    content_text += f"## Overview\n{theory.get('overview', '')}\n\n"
                    content_text += f"## Time Complexity\n{theory.get('timeComplexity', '')}\n\n"
                    content_text += f"## Space Complexity\n{theory.get('spaceComplexity', '')}\n\n"
                
                # Code implementations
                code_examples = []
                implementations = lesson.get("implementations", [])
                for impl in implementations:
                    code_examples.append({
                        "language": impl.get("language", "python"),
                        "title": impl.get("title", "Implementation"),
                        "code": impl.get("code", "")
                    })
                
                # Exercises
                exercises = []
                for exercise in lesson.get("exercises", []):
                    exercises.append({
                        "title": exercise.get("title", ""),
                        "description": exercise.get("description", ""),
                        "difficulty": exercise.get("difficulty", "medium"),
                        "hints": exercise.get("hints", [])
                    })
                
                # Insert into database
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO lessons 
                        (id, title, description, content, code_examples, difficulty,
                         estimated_time, prerequisites, learning_objectives, 
                         exercises, quiz_questions, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        lesson_id,
                        title,
                        description,
                        content_text,
                        json.dumps(code_examples),
                        difficulty,
                        estimated_time,
                        json.dumps(lesson.get("prerequisites", [])),
                        json.dumps(lesson.get("learningObjectives", [])),
                        json.dumps(exercises),
                        json.dumps(lesson.get("assessment", {}).get("questions", [])),
                        json.dumps(lesson.get("tags", []))
                    ))
                    lesson_count += 1
                    print(f"  ✓ Loaded: {title}")
                except Exception as e:
                    print(f"  ✗ Error loading {title}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully loaded {lesson_count} lessons!")
    print("🎉 Full curriculum content is now available in the CLI!")
    print("\nRun 'python curriculum_cli.py' to access all content.")

if __name__ == "__main__":
    # Check if examples directory exists
    examples_dir = Path(__file__).parent / "examples"
    if not examples_dir.exists():
        print("❌ Error: examples directory not found!")
        print("Make sure you have the examples folder with curriculum JSON files.")
        sys.exit(1)
    
    # Load the content
    load_curriculum_content()
    
    # Show what's available
    conn = sqlite3.connect("curriculum.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM lessons")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT title FROM lessons ORDER BY title")
    lessons = cursor.fetchall()
    
    print("\n📚 Available Lessons:")
    for i, (title,) in enumerate(lessons, 1):
        print(f"  {i}. {title}")
    
    conn.close()