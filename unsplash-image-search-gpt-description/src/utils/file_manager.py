"""
File management utilities for handling application data and configuration.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class FileManager:
    """Utility class for common file operations."""
    
    @staticmethod
    def ensure_directory_exists(directory: Path) -> None:
        """Ensure directory exists, create if it doesn't."""
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def read_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
        """Read JSON file and return data, None if error."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"Error reading JSON file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_json_file(file_path: Path, data: Dict[str, Any]) -> bool:
        """Write data to JSON file, return success status."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error writing JSON file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_text_file(file_path: Path) -> Optional[str]:
        """Read text file and return content, None if error."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (FileNotFoundError, Exception) as e:
            print(f"Error reading text file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_text_file(file_path: Path, content: str) -> bool:
        """Write content to text file, return success status."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing text file {file_path}: {e}")
            return False
    
    @staticmethod
    def append_text_file(file_path: Path, content: str) -> bool:
        """Append content to text file, return success status."""
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error appending to text file {file_path}: {e}")
            return False
    
    @staticmethod
    def file_exists(file_path: Path) -> bool:
        """Check if file exists."""
        return file_path.exists() and file_path.is_file()
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes, return 0 if error."""
        try:
            return file_path.stat().st_size
        except Exception:
            return 0
    
    @staticmethod
    def backup_file(file_path: Path, backup_suffix: str = ".bak") -> bool:
        """Create a backup of the file, return success status."""
        if not FileManager.file_exists(file_path):
            return False
        
        try:
            backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
            backup_path.write_bytes(file_path.read_bytes())
            return True
        except Exception as e:
            print(f"Error creating backup for {file_path}: {e}")
            return False
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename by removing invalid characters."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()


class LastSearchManager:
    """Manager for saving and loading the last search query."""
    
    def __init__(self, data_dir: Path):
        self.last_search_file = data_dir / "last_search.txt"
    
    def save_last_search(self, query: str) -> None:
        """Save the current search query for next session."""
        try:
            if query:
                FileManager.write_text_file(self.last_search_file, query)
        except Exception:
            pass  # Ignore errors
    
    def load_last_search(self) -> Optional[str]:
        """Load the last search query from previous session."""
        try:
            if self.last_search_file.exists():
                content = FileManager.read_text_file(self.last_search_file)
                if content:
                    return content.strip()
        except Exception:
            pass  # Ignore errors
        return None
    
    def clear_last_search(self) -> None:
        """Clear the saved last search."""
        try:
            if self.last_search_file.exists():
                self.last_search_file.unlink()
        except Exception:
            pass  # Ignore errors