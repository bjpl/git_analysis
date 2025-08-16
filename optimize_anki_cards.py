import csv
import re

# Set the correct file paths
input_file_path = r"C:\Users\brand\Development\Project_Workspace\Review Cards - Sheet1.csv"
output_file_path = r"C:\Users\brand\Development\Project_Workspace\Anki_Compatible_Review_Cards.csv"

# Function to optimize formatting for Anki compatibility
def optimize_anki_format(text):
    if not text:
        return text
    
    # Replace escaped quotes with properly escaped quotes for CSV
    fixed = text.replace('\\"', '""')
    
    # 1. Make headers before colons bold
    fixed = re.sub(r'(•|\-)\s+([^:]+):', r'\1 <b>\2</b>:', fixed)
    
    # 2. Make examples (text in quotes) italic
    # This regex looks for quoted text that follows a dash
    fixed = re.sub(r'(\-\s+)(".*?")', r'\1<i>\2</i>', fixed)
    
    # Also make examples within parentheses italic if they contain quotes
    fixed = re.sub(r'(\([^)]*")([^"]+)(".*?\))', r'\1<i>\2</i>\3', fixed)
    
    # 3. Add extra spacing between main bullet points for better readability
    fixed = re.sub(r'(<br>\s*)(•)', r'<br><br>\2', fixed)
    
    # 4. Ensure proper spacing after colons for readability
    fixed = re.sub(r':</b>([^\s])', r':</b> \1', fixed)
    
    # 5. Ensure the content is left-aligned with additional styling
    fixed = f'''<div style="text-align: left; width: 100%; margin-left: 0; padding-left: 0;">
{fixed}
</div>'''
    
    return fixed

try:
    # Read the original CSV file
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file)
        headers = next(reader)  # Get the headers
        rows = list(reader)     # Get all data rows
    
    # Write to the new CSV file with explicit field separation
    with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(
            output_file,
            delimiter='\t',      # Use tab as delimiter for better compatibility
            quotechar='"',       # Use double quotes for quoting
            quoting=csv.QUOTE_MINIMAL # Only quote fields that need it
        )
        
        # Write the header row
        writer.writerow(headers)
        
        # Process and write each data row
        for row in rows:
            # Make sure we have at least 3 columns
            while len(row) < 3:
                row.append("")
                
            # Apply optimized formatting to the third column (Detalles)
            if len(row) >= 3 and row[2]:
                row[2] = optimize_anki_format(row[2])
            
            writer.writerow(row)
    
    print("✅ Anki-compatible file created successfully!")
    print(f"📝 The file '{output_file_path}' is ready to be imported into Anki.")
    print("\nFormatting improvements:")
    print("1. Section headers (before colons) are in bold")
    print("2. Examples (in quotes) are in italics")
    print("3. Added spacing between main bullet points")
    print("4. Ensured proper left alignment")
    print("5. Made sure spacing after colons is consistent")
    print("\nWhen importing to Anki:")
    print("1. Select 'Fields separated by: Tab'")
    print("2. Select 'Allow HTML in fields'")
    print("3. Verify field mapping is correct")
    
except FileNotFoundError:
    print(f"❌ Error: Could not find the input file '{input_file_path}'")
    print("Please check that the file path is correct.")
except Exception as e:
    print(f"❌ An error occurred: {e}")