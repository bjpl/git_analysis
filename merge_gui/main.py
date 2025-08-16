import csv
import datetime
import logging
import os
import textwrap
import PySimpleGUI as sg

# -----------------------------------------------------------------------------
# Logging Setup using Python's built-in logging module.
# -----------------------------------------------------------------------------
LOG_FILENAME = "revision_log.txt"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_action(message: str) -> None:
    """Log an action to the log file with a timestamp."""
    logging.info(message)

# -----------------------------------------------------------------------------
# CSV Handling Functions
# -----------------------------------------------------------------------------
def read_csv(filename: str) -> list:
    """Read the CSV file and return a list of rows, skipping the header."""
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        return list(reader)

def parse_csv_row(row: list) -> dict:
    """
    Parse a CSV row (a list of strings) into a dictionary with keys:
    'spanish', 'english', 'definition', 'collocations', 'tags'.
    Missing fields are replaced with empty strings.
    """
    fields = [field.strip() for field in row]
    return {
        "spanish": fields[0] if len(fields) > 0 else "",
        "english": fields[1] if len(fields) > 1 else "",
        "definition": fields[2] if len(fields) > 2 else "",
        "collocations": fields[3] if len(fields) > 3 else "",
        "tags": fields[4] if len(fields) > 4 else ""
    }

def write_csv(filename: str, rows: list) -> None:
    """
    Write the in-memory list of rows back to a CSV file.
    The CSV file is written with a header row.
    """
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["spanish", "english", "definition", "collocations", "tags"])
            for row in rows:
                writer.writerow([
                    row.get("spanish", ""),
                    row.get("english", ""),
                    row.get("definition", ""),
                    row.get("collocations", ""),
                    row.get("tags", "")
                ])
        log_action(f"Updated CSV file successfully written: {filename}")
    except Exception as e:
        log_action(f"Error writing updated CSV file: {e}")
        sg.popup_error("Error saving updated CSV.", str(e), font=("Helvetica", 12))

# -----------------------------------------------------------------------------
# Helper Function for Multiline Sizing
# -----------------------------------------------------------------------------
def compute_multiline_size(text: str, width: int = 60) -> tuple:
    """
    Given a text string and a desired width (in characters), return a tuple (width, height)
    where height is the number of lines needed to display the text fully.
    A minimum of 3 lines is used.
    """
    if not text:
        return (width, 3)
    # Wrap the text using textwrap.wrap; this returns a list of lines.
    lines = textwrap.wrap(text, width=width)
    height = max(len(lines), 3)
    return (width, height)

# -----------------------------------------------------------------------------
# GUI Helper Functions
# -----------------------------------------------------------------------------
def create_comparison_row(field: str, existing_value: str, duplicate_value: str) -> list:
    """
    Create a layout row for comparing a single field side-by-side.
    Uses sg.Multiline elements whose height is computed from the text content so that
    all of the content is visible at once.
    """
    default_width = 60  # in characters
    # Compute required size for each text value.
    w_ex, h_ex = compute_multiline_size(existing_value, width=default_width)
    w_du, h_du = compute_multiline_size(duplicate_value, width=default_width)
    # Use the maximum of the two heights so both boxes are equal in height.
    height = max(h_ex, h_du)
    
    return [
        sg.Text(f"{field}:", font=("Helvetica", 12, "bold"), size=(12, 1)),
        sg.Multiline(default_text=existing_value, key=f"EX_{field.upper()}",
                     font=("Helvetica", 12), size=(default_width, height),
                     autoscroll=False, no_scrollbar=True),
        sg.Multiline(default_text=duplicate_value, key=f"DU_{field.upper()}",
                     font=("Helvetica", 12), size=(default_width, height),
                     autoscroll=False, no_scrollbar=True)
    ]

def duplicate_resolution_window(existing: dict, duplicate: dict, row_idx: int) -> tuple:
    """
    Display a window for resolving a duplicate.
    Returns a tuple: (action, updated_existing, updated_duplicate, merge_options).
    If the user chooses to exit, returns "exit" as the action.
    """
    fields = ["Spanish", "English", "Definition", "Collocations", "Tags"]
    comparison_rows = [
        create_comparison_row(field, existing.get(field.lower(), ""), duplicate.get(field.lower(), ""))
        for field in fields
    ]
    
    layout = [
        [sg.Text(f"Row #{row_idx+1}: Duplicate Detected!", font=("Helvetica", 16, "bold"),
                 justification="center", expand_x=True)],
        [sg.Text("Compare each field side-by-side:", font=("Helvetica", 12), pad=((0,0),(10,10)))],
        # Do not set the column as scrollable so that the entire content is shown.
        [sg.Column(comparison_rows, expand_x=True)],
        [sg.HorizontalSeparator(pad=(10,10))],
        [sg.Text("Select Action:", font=("Helvetica", 14, "bold"))],
        [sg.Radio("Merge fields into existing row", "ACTION", key="ACTION_MERGE", default=True, font=("Helvetica", 12))],
        [sg.Radio("Add as separate row", "ACTION", key="ACTION_ADD", default=False, font=("Helvetica", 12))],
        [sg.Radio("Delete duplicate row", "ACTION", key="ACTION_DELETE", default=False, font=("Helvetica", 12))],
        [sg.Text("If merging, select fields to merge:", font=("Helvetica", 12))],
        [sg.Checkbox("Definition", key="MERGE_DEF", font=("Helvetica", 12)),
         sg.Checkbox("Collocations", key="MERGE_COL", font=("Helvetica", 12)),
         sg.Checkbox("Tags", key="MERGE_TAG", font=("Helvetica", 12))],
        [sg.Button("Confirm", font=("Helvetica", 12)),
         sg.Button("Cancel", font=("Helvetica", 12)),
         sg.Button("Exit", font=("Helvetica", 12))]
    ]
    
    window = sg.Window("Duplicate Resolution", layout, modal=True, resizable=True)
    action = None
    updated_existing = existing.copy()
    updated_duplicate = duplicate.copy()
    merge_options = {}
    
    while True:
        event, values = window.read()
        if event in (None, "Cancel"):
            action = None
            break
        if event == "Exit":
            window.close()
            return "exit", None, None, None
        if event == "Confirm":
            for field in fields:
                key_ex = f"EX_{field.upper()}"
                key_du = f"DU_{field.upper()}"
                updated_existing[field.lower()] = values[key_ex]
                updated_duplicate[field.lower()] = values[key_du]
            
            if values["ACTION_ADD"]:
                action = "add"
            elif values["ACTION_DELETE"]:
                action = "delete"
            elif values["ACTION_MERGE"]:
                action = "merge"
            merge_options = {
                "definition": values.get("MERGE_DEF", False),
                "collocations": values.get("MERGE_COL", False),
                "tags": values.get("MERGE_TAG", False)
            }
            break
    window.close()
    return action, updated_existing, updated_duplicate, merge_options

def merge_fields(existing: dict, duplicate: dict, merge_options: dict) -> dict:
    """
    Merge selected fields from the duplicate into the existing row.
    """
    for field, should_merge in merge_options.items():
        if should_merge:
            existing[field] = duplicate.get(field, "").strip()
    return existing

def show_summary(counters: dict, duration: datetime.timedelta) -> None:
    """
    Display a final session summary.
    """
    layout = [
        [sg.Text("Session Summary", font=("Helvetica", 16, "bold"))],
        [sg.Text(f"Rows Processed: {counters['rows_processed']}", font=("Helvetica", 12))],
        [sg.Text(f"Rows Added: {counters['rows_added']}", font=("Helvetica", 12))],
        [sg.Text(f"Duplicates Found: {counters['duplicates_found']}", font=("Helvetica", 12))],
        [sg.Text(f"Edits Made: {counters['edits_made']}", font=("Helvetica", 12))],
        [sg.Text(f"Merges Made: {counters['merges_made']}", font=("Helvetica", 12))],
        [sg.Text(f"Session Duration: {duration}", font=("Helvetica", 12))],
        [sg.Button("Close", font=("Helvetica", 12))]
    ]
    window = sg.Window("Session Summary", layout, resizable=True)
    while True:
        event, _ = window.read()
        if event in (None, "Close"):
            break
    window.close()

# -----------------------------------------------------------------------------
# Main Application
# -----------------------------------------------------------------------------
def main() -> None:
    sg.theme("LightBlue")
    counters = {
        "rows_processed": 0,
        "rows_added": 0,
        "duplicates_found": 0,
        "edits_made": 0,
        "merges_made": 0
    }
    memory = []  # This list will hold all processed rows.
    session_start = datetime.datetime.now()
    log_action("Session started.")

    layout_main = [
        [sg.Text("CSV Processor", font=("Helvetica", 16, "bold"), justification="center", expand_x=True)],
        [sg.Text("Select CSV file:", font=("Helvetica", 12)), sg.Input(key="-FILE-"), sg.FileBrowse(file_types=(("CSV Files", "*.csv"),))],
        [sg.Text("Starting Row (1-based):", font=("Helvetica", 12)), sg.Input(default_text="1", key="-START_ROW-", size=(5, 1))],
        [sg.Button("Load CSV", font=("Helvetica", 12)), sg.Button("Exit", font=("Helvetica", 12))]
    ]
    window_main = sg.Window("CSV Processor - Main", layout_main, size=(600,200))
    while True:
        event, values = window_main.read()
        if event in (None, "Exit"):
            window_main.close()
            return
        if event == "Load CSV":
            filename = values["-FILE-"]
            try:
                start_row = int(values["-START_ROW-"])
            except ValueError:
                sg.popup_error("Invalid starting row number.", font=("Helvetica", 12))
                continue
            if not os.path.exists(filename):
                sg.popup_error("File not found.", font=("Helvetica", 12))
                continue
            break
    window_main.close()
    log_action(f"CSV file selected: {filename}. Starting row: {start_row}.")

    try:
        csv_rows = read_csv(filename)
    except Exception as e:
        sg.popup_error("Error reading CSV file.", str(e), font=("Helvetica", 12))
        log_action(f"Error reading CSV file: {e}")
        return
    total_rows = len(csv_rows)
    sg.popup("CSV Loaded", f"Total rows in CSV: {total_rows}", font=("Helvetica", 12))
    log_action(f"CSV file loaded with {total_rows} rows.")

    exit_requested = False
    current_index = start_row - 1  # Keep track of the current row index.
    for idx in range(start_row - 1, total_rows):
        current_index = idx  # Update our pointer.
        counters["rows_processed"] += 1
        current_row = csv_rows[idx]
        entry = parse_csv_row(current_row)
        if not entry["spanish"]:
            log_action(f"Row {idx+1} skipped: empty Spanish word.")
            continue

        # Check for duplicates based on the Spanish word (case-insensitive)
        duplicate = None
        for mem in memory:
            if mem["spanish"].lower() == entry["spanish"].lower():
                duplicate = mem
                break

        if duplicate is None:
            memory.append(entry)
            counters["rows_added"] += 1
            log_action(f"Row {idx+1} added: {entry}")
        else:
            counters["duplicates_found"] += 1
            log_action(f"Duplicate found at row {idx+1}: {entry}")
            action, updated_existing, updated_duplicate, merge_options = duplicate_resolution_window(duplicate, entry, idx)
            if action == "exit":
                log_action(f"Exit requested at row {idx+1}.")
                exit_requested = True
                break
            if action is None:
                continue
            if action == "add":
                memory.append(updated_duplicate)
                counters["rows_added"] += 1
                log_action(f"Action 'Add' for row {idx+1}: duplicate added as separate row.")
            elif action == "delete":
                log_action(f"Action 'Delete' for row {idx+1}: duplicate row discarded.")
            elif action == "merge":
                mem_index = memory.index(duplicate)
                merged = merge_fields(updated_existing, updated_duplicate, merge_options)
                memory[mem_index] = merged
                counters["merges_made"] += 1
                log_action(f"Action 'Merge' for row {idx+1}: merged fields {merge_options}.")

        sg.OneLineProgressMeter("Processing CSV", idx+1, total_rows, "CSV_PROCESS")

    sg.OneLineProgressMeterCancel("CSV_PROCESS")

    # If we exited early, append the remaining unrevised rows unchanged.
    if exit_requested:
        for j in range(current_index, total_rows):
            entry = parse_csv_row(csv_rows[j])
            memory.append(entry)
            counters["rows_added"] += 1
            counters["rows_processed"] += 1
            log_action(f"Row {j+1} (unrevised) added: {entry}")

    updated_filename = os.path.join(os.path.dirname(filename), "updated_" + os.path.basename(filename))
    log_action(f"Writing updated CSV file to: {updated_filename}")
    write_csv(updated_filename, memory)
    sg.popup(f"Updated CSV saved: {updated_filename}", font=("Helvetica", 12))

    session_duration = datetime.datetime.now() - session_start
    log_action("Session complete.")
    log_action(f"Rows Processed: {counters['rows_processed']}, Rows Added: {counters['rows_added']}, "
              f"Duplicates Found: {counters['duplicates_found']}, Merges Made: {counters['merges_made']}")

    show_summary(counters, session_duration)
    exit(0)

if __name__ == "__main__":
    main()
