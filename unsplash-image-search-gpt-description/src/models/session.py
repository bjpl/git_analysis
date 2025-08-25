"""
Session data model for tracking application state and logging.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class SessionEntry:
    """Individual session entry with image and description data."""
    
    def __init__(self, query: str, image_url: str, user_note: str = "", generated_description: str = ""):
        self.timestamp = datetime.now().isoformat()
        self.query = query
        self.image_url = image_url
        self.user_note = user_note
        self.generated_description = generated_description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "query": self.query,
            "image_url": self.image_url,
            "user_note": self.user_note,
            "generated_description": self.generated_description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionEntry':
        """Create from dictionary."""
        entry = cls(data["query"], data["image_url"], data.get("user_note", ""), data.get("generated_description", ""))
        entry.timestamp = data.get("timestamp", datetime.now().isoformat())
        return entry


class Session:
    """Application session with multiple entries and vocabulary tracking."""
    
    def __init__(self):
        self.session_start = datetime.now().isoformat()
        self.entries: List[SessionEntry] = []
        self.target_phrases: List[str] = []
        self.used_image_urls = set()
    
    def add_entry(self, entry: SessionEntry):
        """Add a new session entry."""
        self.entries.append(entry)
        canonical_url = self._canonicalize_url(entry.image_url)
        self.used_image_urls.add(canonical_url)
    
    def add_target_phrase(self, phrase: str):
        """Add a target phrase to the vocabulary list."""
        if phrase not in self.target_phrases:
            self.target_phrases.append(phrase)
    
    def get_image_count(self) -> int:
        """Get the number of unique images used."""
        return len(self.used_image_urls)
    
    def get_vocabulary_count(self) -> int:
        """Get the number of vocabulary phrases learned."""
        return len(self.target_phrases)
    
    def update_entry_description(self, image_url: str, user_note: str, description: str):
        """Update the most recent entry with matching image URL."""
        for entry in reversed(self.entries):
            if entry.image_url == image_url and entry.generated_description == "":
                entry.user_note = user_note
                entry.generated_description = description
                break
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_start": self.session_start,
            "session_end": datetime.now().isoformat(),
            "entries": [entry.to_dict() for entry in self.entries],
            "vocabulary_learned": len(self.target_phrases),
            "target_phrases": self.target_phrases
        }
    
    @staticmethod
    def _canonicalize_url(url: str) -> str:
        """Return the base URL without query parameters."""
        return url.split('?')[0] if url else ""


class SessionManager:
    """Manager for handling session persistence and loading."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.current_session = Session()
        self._load_used_urls()
    
    def _load_used_urls(self):
        """Load previously used image URLs from log file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for session in data.get('sessions', []):
                        for entry in session.get('entries', []):
                            url = entry.get('image_url', '')
                            if url:
                                canonical_url = Session._canonicalize_url(url)
                                self.current_session.used_image_urls.add(canonical_url)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading session data: {e}")
                # Try to read as text (backwards compatibility)
                self._load_text_format()
    
    def _load_text_format(self):
        """Load from old text format for backwards compatibility."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "URL de la Imagen" in line:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            url = parts[1].strip()
                            if url:
                                canonical_url = Session._canonicalize_url(url)
                                self.current_session.used_image_urls.add(canonical_url)
        except Exception as e:
            print(f"Error loading text format: {e}")
    
    def save_session(self):
        """Save current session to JSON log file."""
        try:
            # Load existing data or create new structure
            if self.log_file.exists():
                try:
                    with open(self.log_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, Exception):
                    data = {"sessions": []}
            else:
                data = {"sessions": []}
            
            # Add current session if it has entries
            if self.current_session.entries:
                data["sessions"].append(self.current_session.to_dict())
            
            # Save to file
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving session to JSON: {e}")
            self._save_text_fallback()
    
    def _save_text_fallback(self):
        """Fallback text format for backwards compatibility."""
        try:
            text_file = self.log_file.with_suffix('.txt')
            with open(text_file, "a", encoding="utf-8") as f:
                f.write("\n=== Informe de Sesión ===\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                for i, entry in enumerate(self.current_session.entries, start=1):
                    f.write(f"\nEntrada {i}:\n")
                    f.write(f"  Consulta de la Búsqueda: {entry.query}\n")
                    f.write(f"  URL de la Imagen     : {entry.image_url}\n")
                    f.write(f"  Notas del Usuario    : {entry.user_note}\n")
                    f.write(f"  Descripción Generada : {entry.generated_description}\n")
                    f.write("-" * 40 + "\n")
                if self.current_session.target_phrases:
                    f.write("Target Phrases: " + ", ".join(self.current_session.target_phrases) + "\n")
        except Exception as e:
            print(f"Error saving text fallback: {e}")
    
    def is_url_used(self, url: str) -> bool:
        """Check if an image URL has been used before."""
        canonical_url = Session._canonicalize_url(url)
        return canonical_url in self.current_session.used_image_urls
    
    def get_session_stats(self) -> Dict[str, int]:
        """Get current session statistics."""
        return {
            "images": self.current_session.get_image_count(),
            "vocabulary": self.current_session.get_vocabulary_count()
        }