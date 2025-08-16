# CSV Processor

**CSV Processor** is a lightweight Windows-based GUI application built with [PySimpleGUI](https://pypi.org/project/PySimpleGUI/). It processes CSV files row by row and provides interactive options to resolve duplicates based on the Spanish word. With an easy-to-use interface, you can edit, merge, or discard duplicate rows while all actions are logged for reference.

## Features

- **CSV Ingestion:**  
  Load a CSV file containing columns for Spanish word, English word, Spanish definition, collocations, and optional tags.

- **Interactive Duplicate Resolution:**  
  When a duplicate (based on the Spanish word) is detected:
  - Display both the existing and duplicate rows side by side.
  - Edit the fields of either or both rows.
  - Choose one of three actions:
    - **Add as Separate Row:** Keep the duplicate as an additional entry.
    - **Delete Duplicate:** Discard the duplicate row.
    - **Merge Fields:** Merge selected fields from the duplicate into the existing row using thoughtful formatting.

- **Progress Feedback:**  
  A progress meter shows the current row being processed.

- **Session Summary & Logging:**  
  At the end of the session, a summary is displayed with details such as rows processed, duplicates found, edits made, merges performed, and session duration. All actions are logged in a file named `revision_log.txt`.

- **Exit Option:**  
  You can exit the session gracefully at any time from any window.