# Claude Code Notes - Algorithm Learning Sessions

## Overview
This directory contains comprehensive Q&A-style notes from algorithm learning sessions with Claude Code. Each note set includes both markdown and HTML versions for different viewing preferences.

## File Naming Convention
- **Markdown**: `{topic_name}_{date}.md`
- **HTML**: `{topic_name}_{date}.html`
- **Date Format**: `YYYY-MM-DD`

Example: `binary_search_deep_dive_2025-01-12.md`

## Document Structure

### Markdown Format (.md)

#### Header Template
```markdown
# [Topic Title]: Q&A Session

**Date Created:** [Month DD, YYYY]  
**Last Updated:** [Month DD, YYYY]

## Table of Contents
1. [Section Title](#section-link)
2. [Section Title](#section-link)
...
```

#### Section Template
```markdown
## [Number]. [Section Title]

### Question
"[Exact question from conversation]"

### Answer

**[Key insight in bold]**

#### [Subsection if needed]

[Content with examples]
```

#### Code Examples Format
- Always include multiple languages (Pseudocode, Python, Rust minimum)
- Use descriptive comments
- Show both problem and solution
- Include visual traces where helpful

```markdown
**Pseudocode:**
\`\`\`
[Pseudocode here]
\`\`\`

**Python:**
\`\`\`python
[Python code here]
\`\`\`

**Rust:**
\`\`\`rust
[Rust code here]
\`\`\`
```

### HTML Format (.html)

#### Key Features
- **Self-contained**: All content embedded in JavaScript
- **File selector dropdown**: Switch between multiple note documents
- **GitHub-style CSS**: Clean, professional formatting
- **Syntax highlighting**: Code blocks with proper formatting
- **Responsive design**: Works on all screen sizes

#### HTML Template Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Topic] - Algorithm Notes</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        /* GitHub-style CSS - see existing files for full styles */
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-links">
            <label for="file-selector">Select Notes: </label>
            <select id="file-selector">
                <option value="file1.md">Document 1</option>
                <option value="file2.md">Document 2</option>
            </select>
        </div>
        <div id="content" class="loading">Loading notes...</div>
    </div>
    <script>
        // Embedded markdown content
        const documents = {
            'file1.md': `[markdown content]`,
            'file2.md': `[markdown content]`
        };
        // Rendering logic - see existing files
    </script>
</body>
</html>
```

## Content Guidelines

### 1. Teaching Style
- **Warm and Patient**: Like a favorite professor
- **Real-world Analogies First**: Connect to everyday situations before technical terms
- **Progressive Complexity**: Start simple, build gradually
- **Practical Focus**: Always explain "why this matters"

### 2. Analogy Patterns
Common analogies used throughout notes:
- Arrays = Parking spaces/Apartment buildings
- Hash maps = Library card catalog
- Linked lists = Scavenger hunt
- Trees = Family trees/Organizational charts
- Binary search = Dictionary/Phone book lookup

### 3. Code Example Requirements
Each code example should include:
- **Clear purpose statement**
- **Input/output examples**
- **Step-by-step trace for complex algorithms**
- **Edge cases highlighted**
- **Performance analysis**

### 4. Visual Representations
Use ASCII art for diagrams:
```
Array: [A] [B] [C] [D]
       ^              ^
     start           end

Tree:      10
         /    \
        5      15
       / \    /  \
      3   7  12   20
```

## Q&A Format Best Practices

### Question Selection
- Use exact questions from learning session
- Include follow-up questions that clarify confusion
- Progress from simple to complex

### Answer Structure
1. **Bold key insight** at the start
2. **Analogy or real-world connection**
3. **Technical explanation with examples**
4. **Code demonstrations**
5. **Common pitfalls or edge cases**
6. **Summary of key points**

## Adding New Notes

### Step 1: Create Markdown File
1. Copy the template structure
2. Fill in Q&A content from session
3. Add code examples in multiple languages
4. Include visual diagrams where helpful

### Step 2: Create HTML File
1. Copy existing HTML template
2. Embed markdown content in JavaScript
3. Add to documents object for dropdown
4. Test switching between documents

### Step 3: Update Documentation
1. Add entry to this README if new topic area
2. Ensure consistent formatting
3. Verify all code examples work

## Current Topics Covered

### Big O and Search Algorithms (2025-01-11)
- O(n) vs O(1) complexity
- Pronunciation of Big O notation
- Linear search advantages
- Binary search mechanics

### Binary Search Deep Dive (2025-01-12)
- Prerequisites and data structures
- Dynamic arrays and database indexes
- Integer overflow pitfall
- Search variations (first/last/insertion)
- Rotated array search

## Future Topics Template

When adding new algorithm topics, consider including:
- **Complexity Analysis**: Time and space
- **Common Use Cases**: Real-world applications
- **Implementation Variations**: Different approaches
- **Optimization Techniques**: Performance improvements
- **Common Mistakes**: What to avoid
- **Practice Problems**: Hands-on exercises

## Style Consistency Checklist

- [ ] Date format consistent (YYYY-MM-DD in filename, Month DD, YYYY in header)
- [ ] Table of contents with working anchor links
- [ ] Code examples in at least 3 languages
- [ ] Real-world analogies for complex concepts
- [ ] Visual diagrams where applicable
- [ ] Key takeaways section at end
- [ ] HTML file includes dropdown for all documents
- [ ] Markdown properly escaped in HTML JavaScript strings

## Resources

- **Marked.js**: For markdown rendering in HTML
- **GitHub Markdown CSS**: For consistent styling
- **Algorithm Visualizers**: For understanding complex operations
- **Practice Platforms**: LeetCode, HackerRank, CodeSignal

---

*This README serves as the style guide and template for all Claude Code algorithm learning notes. Maintain consistency across all documents for the best learning experience.*