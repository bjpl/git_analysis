import re
import random
import os
import sys

def parse_all_stories(text):
    """
    Parse the document and extract all individual stories.
    Each story starts with a number and a quoted title.
    Filters out section headers.
    
    Args:
        text (str): The full text containing all stories
        
    Returns:
        list: A list of all stories, each as a string
    """
    # First, split the text by main section headers (numbered followed by text without quotes)
    sections = re.split(r'\d+\.\s+[^"\n]+\n', text)
    
    # Initialize a list to store all stories
    all_stories = []
    
    # For each section, extract the individual stories
    for section in sections:
        if not section.strip():  # Skip empty sections
            continue
            
        # This pattern matches individual stories that start with a number followed by a quoted title
        story_pattern = r'(\d+\.\s+\".*?\"\n.*?(?=\d+\.\s+\"|\Z))'
        stories = re.findall(story_pattern, section, re.DOTALL)
        
        # Add the found stories to our list
        all_stories.extend([story.strip() for story in stories])
    
    return all_stories

def extract_story_info(story):
    """
    Extract the original number, title, and content from a story.
    
    Args:
        story (str): The full story text
        
    Returns:
        tuple: (original_number, title, content)
    """
    # Extract the original number
    number_match = re.match(r'(\d+)\.', story)
    original_number = number_match.group(1) if number_match else "Unknown"
    
    # Extract the title
    title_match = re.search(r'\"(.*?)\"', story)
    title = title_match.group(1) if title_match else "Untitled"
    
    # Extract just the content (after the title)
    content_parts = story.split('"' + title + '"\n', 1)
    content = content_parts[1] if len(content_parts) > 1 else story
    
    return original_number, title, content

def shuffle_stories(stories):
    """
    Randomly shuffles all stories across all sections.
    
    Args:
        stories (list): The list of all stories to shuffle
        
    Returns:
        list: Shuffled stories
    """
    shuffled = stories.copy()  # Make a copy to avoid modifying the original
    random.shuffle(shuffled)
    return shuffled

def create_output_text(shuffled_stories):
    """
    Create the output text with shuffled stories.
    
    Args:
        shuffled_stories (list): The shuffled stories
        
    Returns:
        str: Formatted output text
    """
    output_text = "# Randomly Shuffled Subjunctive Scenes\n\n"
    
    # Add each shuffled story to the output with new numbering
    for i, story in enumerate(shuffled_stories, 1):
        original_number, title, content = extract_story_info(story)
        
        # Add the story with new numbering but preserve its title and content
        output_text += f"{i}. **\"{title}\"**\n\n{content}\n\n"
    
    return output_text

def process_file(input_filename, output_filename):
    """
    Process the input file and write shuffled content to the output file.
    
    Args:
        input_filename (str): Path to the input file
        output_filename (str): Path to the output file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_filename):
            print(f"Error: Input file '{input_filename}' does not exist")
            return False
        
        # Read the input file
        with open(input_filename, 'r', encoding='utf-8') as file:
            input_text = file.read()
        
        # Parse all stories from all sections in the input text
        stories = parse_all_stories(input_text)
        
        # Count stories found for verification
        num_stories = len(stories)
        if num_stories == 0:
            print("Error: No stories found in the input file")
            return False
        
        print(f"Found {num_stories} stories to shuffle")
        
        # Shuffle all stories
        shuffled_stories = shuffle_stories(stories)
        
        # Create the output text with shuffled stories
        output_text = create_output_text(shuffled_stories)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write to the output file
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(output_text)
        
        print(f"Successfully wrote {num_stories} shuffled stories to '{output_filename}'")
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def main():
    """
    Main function to handle command line arguments or use default values.
    """
    # Use command line arguments if provided, otherwise use defaults
    if len(sys.argv) > 2:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    else:
        input_filename = "subjunctive_scenes.txt"  # Default input filename
        output_filename = "shuffled_scenes.txt"    # Default output filename
        print(f"Using default filenames: {input_filename} -> {output_filename}")
        print("(You can specify custom filenames: python script.py input.txt output.txt)")
    
    # Process the file
    success = process_file(input_filename, output_filename)
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

# Execute the script if run directly
if __name__ == "__main__":
    main()