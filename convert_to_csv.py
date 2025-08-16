import re
import csv

def main():
    print("Enter your content. Type 'EOF' (in a new line) to finish:")

    # Read multiline input until 'EOF' is encountered
    lines = []
    while True:
        line = input()
        if line.strip() == "EOF":
            break
        lines.append(line)
    content = "\n".join(lines)

    # Improved regex:
    pattern = re.compile(r'^[ \t]{4,}(.+?):\n((?:[ \t]{8,}.+\n?)+)', re.MULTILINE)

    # Find matches
    matches = pattern.findall(content)

    data = []
    for title, description_block in matches:
        perspective = title.strip()
        description_lines = description_block.splitlines()
        description = " ".join(line.strip() for line in description_lines)
        data.append([perspective, description])

    # Force semicolon (;) as delimiter for better Excel compatibility
    output_filename = "output.csv"
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_ALL)  # Use semicolon separator
        writer.writerow(['Perspective', 'Description'])
        writer.writerows(data)

    print(f"CSV file created as '{output_filename}'. Try opening it in Excel with semicolon-separated values.")

if __name__ == "__main__":
    main()
