"""
Vocabulary management model for tracking learned words and phrases.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Set, List, Dict, Optional


class VocabularyEntry:
    """Individual vocabulary entry with metadata."""
    
    def __init__(self, spanish: str, english: str, search_query: str = "", 
                 image_url: str = "", context: str = ""):
        self.spanish = spanish
        self.english = english
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.search_query = search_query
        self.image_url = image_url[:100] if image_url else ""  # Truncate long URLs
        self.context = context[:100] if context else ""  # Truncate long context
    
    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format."""
        return [
            self.spanish,
            self.english,
            self.date,
            self.search_query,
            self.image_url,
            self.context
        ]
    
    @classmethod
    def from_csv_row(cls, row: List[str]) -> 'VocabularyEntry':
        """Create from CSV row."""
        if len(row) >= 2:
            entry = cls(row[0], row[1])
            if len(row) > 2:
                entry.date = row[2] if row[2] else entry.date
            if len(row) > 3:
                entry.search_query = row[3]
            if len(row) > 4:
                entry.image_url = row[4]
            if len(row) > 5:
                entry.context = row[5]
            return entry
        raise ValueError("Invalid CSV row format")


class VocabularyManager:
    """Manager for vocabulary storage and retrieval."""
    
    def __init__(self, csv_file: Path):
        self.csv_file = csv_file
        self.vocabulary_cache: Set[str] = set()
        self._initialize_csv_file()
        self._load_vocabulary_cache()
    
    def _initialize_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
    
    def _load_vocabulary_cache(self):
        """Load existing vocabulary to prevent duplicates."""
        if self.csv_file.exists():
            try:
                with open(self.csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'Spanish' in row and row['Spanish']:
                            self.vocabulary_cache.add(row['Spanish'])
            except Exception as e:
                print(f"Error loading vocabulary cache: {e}")
                # Try to read as simple CSV for backwards compatibility
                self._load_simple_csv_format()
    
    def _load_simple_csv_format(self):
        """Load from simple CSV format for backwards compatibility."""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header if exists
                for row in reader:
                    if row and len(row) > 0 and row[0]:
                        self.vocabulary_cache.add(row[0])
        except Exception as e:
            print(f"Error loading simple CSV format: {e}")
    
    def add_vocabulary_entry(self, entry: VocabularyEntry) -> bool:
        """Add a vocabulary entry if it doesn't already exist."""
        if entry.spanish in self.vocabulary_cache:
            return False  # Already exists
        
        try:
            # Check if file exists and has headers
            file_exists = self.csv_file.exists()
            needs_header = not file_exists or os.path.getsize(self.csv_file) == 0
            
            with open(self.csv_file, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers if needed
                if needs_header:
                    writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
                
                # Write the data
                writer.writerow(entry.to_csv_row())
            
            # Add to cache
            self.vocabulary_cache.add(entry.spanish)
            return True
            
        except Exception as e:
            print(f"Error adding vocabulary entry: {e}")
            return False
    
    def is_duplicate(self, spanish_word: str) -> bool:
        """Check if a Spanish word already exists in vocabulary."""
        return spanish_word in self.vocabulary_cache
    
    def get_vocabulary_count(self) -> int:
        """Get the total number of vocabulary entries."""
        return len(self.vocabulary_cache)
    
    def get_all_entries(self) -> List[VocabularyEntry]:
        """Get all vocabulary entries from the CSV file."""
        entries = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if row and len(row) >= 2:
                        try:
                            entry = VocabularyEntry.from_csv_row(row)
                            entries.append(entry)
                        except ValueError:
                            continue  # Skip invalid rows
        except Exception as e:
            print(f"Error reading vocabulary entries: {e}")
        
        return entries
    
    def export_to_anki(self, output_file: Path) -> bool:
        """Export vocabulary to Anki-compatible format."""
        try:
            entries = self.get_all_entries()
            with open(output_file, 'w', encoding='utf-8') as f:
                for entry in entries:
                    # Anki format: front[tab]back
                    context_snippet = entry.context[:50] if entry.context else ""
                    f.write(f"{entry.spanish}\t{entry.english} | {context_snippet}\n")
            return True
        except Exception as e:
            print(f"Error exporting to Anki: {e}")
            return False
    
    def export_to_text(self, output_file: Path) -> bool:
        """Export vocabulary to plain text format."""
        try:
            entries = self.get_all_entries()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("VOCABULARY LIST\n")
                f.write("=" * 50 + "\n\n")
                for entry in entries:
                    f.write(f"{entry.spanish} = {entry.english}\n")
                    if entry.search_query:
                        f.write(f"  (from: {entry.search_query})\n")
                    f.write("\n")
            return True
        except Exception as e:
            print(f"Error exporting to text: {e}")
            return False