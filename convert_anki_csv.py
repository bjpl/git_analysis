import csv
import re

# Set the correct file paths
input_file_path = r"C:\Users\brand\Development\Project_Workspace\Review Cards - Sheet1.csv"
output_file_path = r"C:\Users\brand\Development\Project_Workspace\Anki_Cards.csv"

def format_anki_content(text):
    if not text:
        return text
    
    # Replace escaped quotes with properly escaped quotes
    fixed = text.replace('\\"', '"')
    
    # Make section headers before colons bold
    fixed = re.sub(r'(•|\-)\s+([^:]+):', r'\1 <b>\2</b>:', fixed)
    
    # Make examples (text in quotes) italic but NOT section headers
    fixed = re.sub(r'(\-\s+)(".*?")', r'\1<i>\2</i>', fixed)
    
    # Add spacing between main bullet points
    fixed = re.sub(r'(<br>\s*)(•)', r'<br><br>\2', fixed)
    
    # Ensure proper spacing after colons
    fixed = re.sub(r':</b>([^\s])', r':</b> \1', fixed)
    
    # Left-align content with styling that works in Anki
    fixed = f'<div style="text-align: left;">{fixed}</div>'
    
    return fixed

try:
    # Read the original CSV file
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        headers = next(reader)
        rows = list(reader)
    
    # Create a new file with tab-delimited format (better for Anki)
    with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
        # Process each row
        for row in rows:
            # Ensure we have three columns
            while len(row) < 3:
                row.append("")
            
            # Format the third column with improved styling
            if len(row) >= 3:
                row[2] = format_anki_content(row[2])
            
            # Remove any tab characters from the content
            row = [field.replace('\t', ' ') for field in row]
            
            # Write the tab-separated line
            output_file.write('\t'.join(row) + '\n')
    
    print("✅ Anki-compatible CSV file created successfully!")
    print(f"📝 File saved as: {output_file_path}")
    print("\nImport instructions for Anki:")
    print("1. In Anki, go to File → Import")
    print("2. Select the file: Anki_Cards.csv")
    print("3. Make sure to select:")
    print("   • Fields separated by: Tab")
    print("   • Allow HTML in fields: CHECKED")
    print("   • Ensure Field mapping shows three separate columns")
    print("4. Click Import")

except Exception as e:
    print(f"❌ Error: {e}")