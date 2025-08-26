"""
Vocabulary Import/Export Utilities
==================================

Comprehensive import/export functionality for vocabulary data with support for:
- Multiple file formats (CSV, JSON, Anki, Excel, XML)
- Data validation and error handling
- Batch operations and progress tracking
- Format detection and conversion
- Custom mapping and field configuration
- Backup and recovery operations
"""

import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import gzip
import zipfile
from datetime import datetime
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportFormat(Enum):
    """Supported import formats."""
    CSV = "csv"
    JSON = "json"
    ANKI = "anki"
    EXCEL = "excel"
    XML = "xml"
    TSV = "tsv"
    MEMRISE = "memrise"
    QUIZLET = "quizlet"
    AUTO_DETECT = "auto"


class ExportFormat(Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    ANKI = "anki"
    EXCEL = "excel"
    XML = "xml"
    TSV = "tsv"
    PDF = "pdf"
    HTML = "html"


@dataclass
class ImportOptions:
    """Configuration options for import operations."""
    # File options
    encoding: str = "utf-8"
    delimiter: str = ","
    quote_char: str = '"'
    skip_header: bool = True
    
    # Field mapping
    field_mapping: Dict[str, str] = field(default_factory=dict)
    required_fields: List[str] = field(default_factory=lambda: ["spanish", "english"])
    
    # Data processing
    auto_detect_difficulty: bool = True
    auto_categorize_themes: bool = True
    validate_translations: bool = False
    
    # Merge options
    merge_strategy: str = "skip_duplicates"  # skip_duplicates, update_existing, create_duplicates
    duplicate_threshold: float = 0.9  # similarity threshold for duplicate detection
    
    # Progress tracking
    progress_callback: Optional[Callable[[int, int], None]] = None
    batch_size: int = 100


@dataclass
class ExportOptions:
    """Configuration options for export operations."""
    # File options
    encoding: str = "utf-8"
    delimiter: str = ","
    quote_char: str = '"'
    include_header: bool = True
    
    # Content filtering
    status_filter: Optional[List[str]] = None
    theme_filter: Optional[List[str]] = None
    difficulty_filter: Optional[List[int]] = None
    date_range: Optional[Tuple[str, str]] = None
    
    # Field selection
    include_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
    custom_fields: Dict[str, str] = field(default_factory=dict)
    
    # Formatting options
    include_statistics: bool = False
    include_metadata: bool = True
    compress_output: bool = False
    
    # Progress tracking
    progress_callback: Optional[Callable[[int, int], None]] = None


@dataclass
class ImportResult:
    """Result of an import operation."""
    success: bool
    total_processed: int
    imported: int
    updated: int
    skipped: int
    errors: int
    error_messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the import."""
        if not self.success:
            return f"Import failed: {'; '.join(self.error_messages)}"
        
        return (
            f"Import completed: {self.imported} imported, {self.updated} updated, "
            f"{self.skipped} skipped, {self.errors} errors in {self.processing_time_seconds:.2f}s"
        )


class VocabularyImportExport:
    """Main class for vocabulary import/export operations."""
    
    def __init__(self, vocabulary_manager):
        self.vocabulary_manager = vocabulary_manager
        self.format_handlers = {
            ImportFormat.CSV: self._import_csv,
            ImportFormat.JSON: self._import_json,
            ImportFormat.ANKI: self._import_anki,
            ImportFormat.XML: self._import_xml,
            ImportFormat.TSV: self._import_tsv,
            ImportFormat.MEMRISE: self._import_memrise,
            ImportFormat.QUIZLET: self._import_quizlet,
        }
        
        self.export_handlers = {
            ExportFormat.CSV: self._export_csv,
            ExportFormat.JSON: self._export_json,
            ExportFormat.ANKI: self._export_anki,
            ExportFormat.XML: self._export_xml,
            ExportFormat.TSV: self._export_tsv,
            ExportFormat.HTML: self._export_html,
        }
    
    def auto_detect_format(self, file_path: Path) -> ImportFormat:
        """Auto-detect file format based on extension and content."""
        extension = file_path.suffix.lower()
        
        # Extension-based detection
        extension_map = {
            '.csv': ImportFormat.CSV,
            '.json': ImportFormat.JSON,
            '.txt': ImportFormat.ANKI,
            '.tsv': ImportFormat.TSV,
            '.xml': ImportFormat.XML,
            '.xlsx': ImportFormat.EXCEL,
            '.xls': ImportFormat.EXCEL,
        }
        
        if extension in extension_map:
            detected_format = extension_map[extension]
            
            # Content verification for ambiguous cases
            if extension == '.txt':
                # Check if it's actually Anki format
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                        if '\t' in first_line and not first_line.startswith('"'):
                            return ImportFormat.ANKI
                        elif ',' in first_line:
                            return ImportFormat.CSV
                except:
                    pass
            
            return detected_format
        
        # Default fallback
        return ImportFormat.CSV
    
    def import_vocabulary(self, file_path: Path, format_type: ImportFormat = ImportFormat.AUTO_DETECT,
                         options: Optional[ImportOptions] = None) -> ImportResult:
        """Import vocabulary from file."""
        if options is None:
            options = ImportOptions()
        
        start_time = datetime.now()
        
        try:
            # Auto-detect format if requested
            if format_type == ImportFormat.AUTO_DETECT:
                format_type = self.auto_detect_format(file_path)
            
            logger.info(f"Importing vocabulary from {file_path} using format {format_type.value}")
            
            # Get appropriate handler
            handler = self.format_handlers.get(format_type)
            if not handler:
                return ImportResult(
                    success=False,
                    total_processed=0,
                    imported=0,
                    updated=0,
                    skipped=0,
                    errors=1,
                    error_messages=[f"Unsupported import format: {format_type.value}"]
                )
            
            # Perform import
            result = handler(file_path, options)
            
            # Calculate processing time
            end_time = datetime.now()
            result.processing_time_seconds = (end_time - start_time).total_seconds()
            
            logger.info(f"Import completed: {result.get_summary()}")
            return result
            
        except Exception as e:
            logger.error(f"Import failed with exception: {e}")
            return ImportResult(
                success=False,
                total_processed=0,
                imported=0,
                updated=0,
                skipped=0,
                errors=1,
                error_messages=[f"Import failed: {str(e)}"],
                processing_time_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _import_csv(self, file_path: Path, options: ImportOptions) -> ImportResult:
        """Import from CSV format."""
        result = ImportResult(success=True, total_processed=0, imported=0, updated=0, skipped=0, errors=0)
        
        try:
            with open(file_path, 'r', encoding=options.encoding, newline='') as f:
                # Detect delimiter if not specified
                if not options.delimiter:
                    sample = f.read(1024)
                    f.seek(0)
                    sniffer = csv.Sniffer()
                    options.delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=options.delimiter, quotechar=options.quote_char)
                
                # Skip header if requested
                if options.skip_header:
                    next(reader, None)
                
                rows = list(reader)
                result.total_processed = len(rows)
                
                # Process rows in batches
                for i in range(0, len(rows), options.batch_size):
                    batch = rows[i:i + options.batch_size]
                    batch_result = self._process_import_batch(batch, options)
                    
                    result.imported += batch_result['imported']
                    result.updated += batch_result['updated']
                    result.skipped += batch_result['skipped']
                    result.errors += batch_result['errors']
                    result.error_messages.extend(batch_result['error_messages'])
                    result.warnings.extend(batch_result['warnings'])
                    
                    # Progress callback
                    if options.progress_callback:
                        options.progress_callback(i + len(batch), len(rows))
        
        except Exception as e:
            result.success = False
            result.error_messages.append(f"CSV import error: {str(e)}")
            result.errors += 1
        
        return result
    
    def _import_json(self, file_path: Path, options: ImportOptions) -> ImportResult:
        """Import from JSON format."""
        result = ImportResult(success=True, total_processed=0, imported=0, updated=0, skipped=0, errors=0)
        
        try:
            with open(file_path, 'r', encoding=options.encoding) as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                if 'vocabulary' in data:
                    entries = data['vocabulary']
                elif 'entries' in data:
                    entries = data['entries']
                else:
                    entries = [data]  # Single entry
            elif isinstance(data, list):
                entries = data
            else:
                raise ValueError("Invalid JSON structure")
            
            result.total_processed = len(entries)
            
            # Process entries in batches
            for i in range(0, len(entries), options.batch_size):
                batch = entries[i:i + options.batch_size]
                batch_result = self._process_import_batch(batch, options)
                
                result.imported += batch_result['imported']
                result.updated += batch_result['updated']
                result.skipped += batch_result['skipped']
                result.errors += batch_result['errors']
                result.error_messages.extend(batch_result['error_messages'])
                result.warnings.extend(batch_result['warnings'])
                
                # Progress callback
                if options.progress_callback:
                    options.progress_callback(i + len(batch), len(entries))
        
        except Exception as e:
            result.success = False
            result.error_messages.append(f"JSON import error: {str(e)}")
            result.errors += 1
        
        return result
    
    def _import_anki(self, file_path: Path, options: ImportOptions) -> ImportResult:
        """Import from Anki format (tab-separated)."""
        result = ImportResult(success=True, total_processed=0, imported=0, updated=0, skipped=0, errors=0)
        
        try:
            with open(file_path, 'r', encoding=options.encoding) as f:
                lines = f.readlines()
            
            result.total_processed = len(lines)
            entries = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    entry = {
                        'spanish': parts[0].strip(),
                        'english': parts[1].strip()
                    }
                    
                    # Parse additional fields if present
                    if len(parts) > 2:
                        # Tags or additional info
                        tags = parts[2].strip()
                        if tags:
                            entry['tags'] = tags.split()
                    
                    entries.append(entry)
                else:
                    result.warnings.append(f"Line {line_num}: Invalid format, skipping")
            
            # Process entries
            batch_result = self._process_import_batch(entries, options)
            result.imported = batch_result['imported']
            result.updated = batch_result['updated']
            result.skipped = batch_result['skipped']
            result.errors = batch_result['errors']
            result.error_messages = batch_result['error_messages']
            result.warnings.extend(batch_result['warnings'])
        
        except Exception as e:
            result.success = False
            result.error_messages.append(f"Anki import error: {str(e)}")
            result.errors += 1
        
        return result
    
    def _import_xml(self, file_path: Path, options: ImportOptions) -> ImportResult:
        """Import from XML format."""
        result = ImportResult(success=True, total_processed=0, imported=0, updated=0, skipped=0, errors=0)
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            entries = []
            
            # Handle different XML structures
            if root.tag == 'vocabulary':
                entry_elements = root.findall('entry')
            elif root.tag == 'entries':
                entry_elements = root.findall('entry')
            else:
                entry_elements = [root]  # Single entry
            
            result.total_processed = len(entry_elements)
            
            for elem in entry_elements:
                entry = {}
                
                # Extract fields from XML
                for child in elem:
                    entry[child.tag] = child.text or ""
                
                # Map required fields
                if 'spanish' not in entry and 'front' in entry:
                    entry['spanish'] = entry['front']
                if 'english' not in entry and 'back' in entry:
                    entry['english'] = entry['back']
                
                entries.append(entry)
            
            # Process entries
            batch_result = self._process_import_batch(entries, options)
            result.imported = batch_result['imported']
            result.updated = batch_result['updated']
            result.skipped = batch_result['skipped']
            result.errors = batch_result['errors']
            result.error_messages = batch_result['error_messages']
            result.warnings = batch_result['warnings']
        
        except Exception as e:
            result.success = False
            result.error_messages.append(f"XML import error: {str(e)}")
            result.errors += 1
        
        return result
    
    def _import_tsv(self, file_path: Path, options: ImportOptions) -> ImportResult:
        """Import from TSV format."""
        # TSV is just CSV with tab delimiter
        options.delimiter = '\t'
        return self._import_csv(file_path, options)
    
    def _import_memrise(self, file_path: Path, options: ImportOptions) -> ImportResult:
        """Import from Memrise CSV format."""
        # Memrise typically uses specific column names
        options.field_mapping = {
            'Spanish': 'spanish',
            'English': 'english',
            'Part of Speech': 'part_of_speech',
            'Level': 'difficulty'
        }
        return self._import_csv(file_path, options)
    
    def _import_quizlet(self, file_path: Path, options: ImportOptions) -> ImportResult:
        """Import from Quizlet format."""
        # Quizlet uses tab-separated format similar to Anki
        return self._import_anki(file_path, options)
    
    def _process_import_batch(self, entries: List[Dict[str, Any]], 
                            options: ImportOptions) -> Dict[str, Any]:
        """Process a batch of entries for import."""
        from ..models.enhanced_vocabulary import EnhancedVocabularyEntry, DifficultyLevel, WordStatus, SourceType
        
        batch_result = {
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'error_messages': [],
            'warnings': []
        }
        
        for entry_data in entries:
            try:
                # Apply field mapping
                mapped_data = self._apply_field_mapping(entry_data, options.field_mapping)
                
                # Validate required fields
                missing_fields = []
                for field in options.required_fields:
                    if field not in mapped_data or not mapped_data[field].strip():
                        missing_fields.append(field)
                
                if missing_fields:
                    batch_result['errors'] += 1
                    batch_result['error_messages'].append(
                        f"Missing required fields: {', '.join(missing_fields)}"
                    )
                    continue
                
                # Create vocabulary entry
                spanish = mapped_data['spanish'].strip()
                english = mapped_data['english'].strip()
                
                # Check for existing entry
                existing_entry = self.vocabulary_manager.get_entry_by_word(spanish)
                
                if existing_entry:
                    if options.merge_strategy == 'skip_duplicates':
                        batch_result['skipped'] += 1
                        continue
                    elif options.merge_strategy == 'update_existing':
                        # Update existing entry
                        self._update_existing_entry(existing_entry, mapped_data, options)
                        batch_result['updated'] += 1
                        continue
                
                # Create new entry
                entry = EnhancedVocabularyEntry(
                    spanish=spanish,
                    english=english,
                    source=SourceType.IMPORT_CSV
                )
                
                # Apply additional fields
                self._apply_entry_fields(entry, mapped_data, options)
                
                # Add to vocabulary manager
                if self.vocabulary_manager.add_vocabulary_entry(entry):
                    batch_result['imported'] += 1
                else:
                    batch_result['errors'] += 1
                    batch_result['error_messages'].append(f"Failed to add entry: {spanish}")
            
            except Exception as e:
                batch_result['errors'] += 1
                batch_result['error_messages'].append(f"Error processing entry: {str(e)}")
        
        return batch_result
    
    def _apply_field_mapping(self, entry_data: Dict[str, Any], 
                           field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Apply field mapping to entry data."""
        mapped_data = {}
        
        for source_field, target_field in field_mapping.items():
            if source_field in entry_data:
                mapped_data[target_field] = entry_data[source_field]
        
        # Copy unmapped fields as-is
        for key, value in entry_data.items():
            if key not in field_mapping and key not in mapped_data:
                mapped_data[key] = value
        
        return mapped_data
    
    def _apply_entry_fields(self, entry: 'EnhancedVocabularyEntry', 
                          data: Dict[str, Any], options: ImportOptions):
        """Apply additional fields to vocabulary entry."""
        from ..models.enhanced_vocabulary import DifficultyLevel, WordStatus
        
        # Phonetic
        if 'phonetic' in data and data['phonetic']:
            entry.phonetic = data['phonetic']
        
        # Part of speech
        if 'part_of_speech' in data and data['part_of_speech']:
            entry.part_of_speech = data['part_of_speech']
        
        # Difficulty
        if 'difficulty' in data:
            try:
                if isinstance(data['difficulty'], str):
                    # Try to parse difficulty level
                    difficulty_map = {
                        'beginner': DifficultyLevel.BEGINNER,
                        'elementary': DifficultyLevel.ELEMENTARY,
                        'intermediate': DifficultyLevel.INTERMEDIATE,
                        'advanced': DifficultyLevel.ADVANCED,
                        'expert': DifficultyLevel.EXPERT,
                        '1': DifficultyLevel.BEGINNER,
                        '2': DifficultyLevel.ELEMENTARY,
                        '3': DifficultyLevel.INTERMEDIATE,
                        '4': DifficultyLevel.ADVANCED,
                        '5': DifficultyLevel.EXPERT,
                    }
                    difficulty_str = data['difficulty'].lower().strip()
                    if difficulty_str in difficulty_map:
                        entry.difficulty = difficulty_map[difficulty_str]
                elif isinstance(data['difficulty'], int):
                    if 1 <= data['difficulty'] <= 5:
                        entry.difficulty = DifficultyLevel(data['difficulty'])
            except (ValueError, KeyError):
                pass  # Keep default difficulty
        
        # Themes
        if 'themes' in data and data['themes']:
            if isinstance(data['themes'], str):
                entry.themes = set(data['themes'].split(';'))
            elif isinstance(data['themes'], list):
                entry.themes = set(data['themes'])
        
        # Tags
        if 'tags' in data and data['tags']:
            if isinstance(data['tags'], str):
                entry.custom_tags = set(data['tags'].split(';'))
            elif isinstance(data['tags'], list):
                entry.custom_tags = set(data['tags'])
        
        # Priority
        if 'priority' in data:
            try:
                priority = int(data['priority'])
                if 1 <= priority <= 5:
                    entry.priority = priority
            except (ValueError, TypeError):
                pass
        
        # Notes
        if 'notes' in data and data['notes']:
            entry.personal_notes = data['notes']
        
        # Auto-detect difficulty if enabled
        if options.auto_detect_difficulty and entry.difficulty == DifficultyLevel.UNKNOWN:
            entry.difficulty = self._auto_detect_difficulty(entry.spanish, entry.english)
        
        # Auto-categorize themes if enabled
        if options.auto_categorize_themes and not entry.themes:
            entry.themes = self._auto_detect_themes(entry.spanish, entry.english)
    
    def _auto_detect_difficulty(self, spanish: str, english: str) -> 'DifficultyLevel':
        """Auto-detect difficulty level based on word characteristics."""
        from ..models.enhanced_vocabulary import DifficultyLevel
        
        # Simple heuristics for difficulty detection
        word_length = len(spanish)
        
        # Common word patterns
        common_endings = ['ar', 'er', 'ir', 'ión', 'dad', 'mente']
        complex_patterns = ['cc', 'ñ', 'rr', 'll', 'x']
        
        difficulty_score = 0
        
        # Length-based scoring
        if word_length <= 4:
            difficulty_score += 1
        elif word_length <= 7:
            difficulty_score += 2
        elif word_length <= 10:
            difficulty_score += 3
        else:
            difficulty_score += 4
        
        # Pattern-based scoring
        if any(pattern in spanish for pattern in complex_patterns):
            difficulty_score += 1
        
        if any(spanish.endswith(ending) for ending in common_endings):
            difficulty_score -= 1  # Common endings are easier
        
        # Map score to difficulty level
        if difficulty_score <= 1:
            return DifficultyLevel.BEGINNER
        elif difficulty_score <= 2:
            return DifficultyLevel.ELEMENTARY
        elif difficulty_score <= 3:
            return DifficultyLevel.INTERMEDIATE
        elif difficulty_score <= 4:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT
    
    def _auto_detect_themes(self, spanish: str, english: str) -> set:
        """Auto-detect themes based on word content."""
        themes = set()
        
        # Theme keywords
        theme_keywords = {
            'food': ['comida', 'comer', 'beber', 'cocina', 'restaurante', 'food', 'eat', 'drink', 'kitchen'],
            'travel': ['viaje', 'viajar', 'hotel', 'avión', 'aeropuerto', 'travel', 'trip', 'plane', 'airport'],
            'family': ['familia', 'padre', 'madre', 'hijo', 'hija', 'family', 'father', 'mother', 'son', 'daughter'],
            'animals': ['animal', 'perro', 'gato', 'pájaro', 'animal', 'dog', 'cat', 'bird'],
            'colors': ['color', 'rojo', 'azul', 'verde', 'color', 'red', 'blue', 'green'],
            'numbers': ['número', 'uno', 'dos', 'tres', 'number', 'one', 'two', 'three'],
            'time': ['tiempo', 'hora', 'día', 'semana', 'time', 'hour', 'day', 'week'],
            'body': ['cuerpo', 'cabeza', 'mano', 'pie', 'body', 'head', 'hand', 'foot'],
            'home': ['casa', 'hogar', 'cocina', 'dormitorio', 'home', 'house', 'bedroom', 'kitchen'],
            'work': ['trabajo', 'oficina', 'jefe', 'work', 'office', 'boss', 'job']
        }
        
        text_to_check = f"{spanish} {english}".lower()
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_to_check for keyword in keywords):
                themes.add(theme)
        
        return themes
    
    def _update_existing_entry(self, existing_entry: 'EnhancedVocabularyEntry',
                             data: Dict[str, Any], options: ImportOptions):
        """Update an existing vocabulary entry with new data."""
        # Update English translation if different
        if 'english' in data and data['english'] != existing_entry.english:
            existing_entry.english = data['english']
        
        # Merge themes and tags
        if 'themes' in data and data['themes']:
            if isinstance(data['themes'], str):
                new_themes = set(data['themes'].split(';'))
            else:
                new_themes = set(data['themes'])
            existing_entry.themes.update(new_themes)
        
        if 'tags' in data and data['tags']:
            if isinstance(data['tags'], str):
                new_tags = set(data['tags'].split(';'))
            else:
                new_tags = set(data['tags'])
            existing_entry.custom_tags.update(new_tags)
        
        # Update notes
        if 'notes' in data and data['notes']:
            if existing_entry.personal_notes:
                existing_entry.personal_notes += f"\n\n{data['notes']}"
            else:
                existing_entry.personal_notes = data['notes']
        
        # Save updated entry
        self.vocabulary_manager.update_entry(existing_entry)
    
    # Export methods
    
    def export_vocabulary(self, file_path: Path, format_type: ExportFormat,
                         options: Optional[ExportOptions] = None) -> bool:
        """Export vocabulary to file."""
        if options is None:
            options = ExportOptions()
        
        try:
            logger.info(f"Exporting vocabulary to {file_path} using format {format_type.value}")
            
            # Get appropriate handler
            handler = self.export_handlers.get(format_type)
            if not handler:
                logger.error(f"Unsupported export format: {format_type.value}")
                return False
            
            # Perform export
            success = handler(file_path, options)
            
            if success:
                logger.info(f"Export completed successfully")
                
                # Compress if requested
                if options.compress_output:
                    self._compress_file(file_path)
            else:
                logger.error("Export failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Export failed with exception: {e}")
            return False
    
    def _export_csv(self, file_path: Path, options: ExportOptions) -> bool:
        """Export to CSV format."""
        try:
            entries = self._get_filtered_entries(options)
            
            with open(file_path, 'w', newline='', encoding=options.encoding) as f:
                writer = csv.writer(f, delimiter=options.delimiter, quotechar=options.quote_char)
                
                # Write header
                if options.include_header:
                    headers = self._get_export_headers(options)
                    writer.writerow(headers)
                
                # Write entries
                for i, entry in enumerate(entries):
                    row = self._entry_to_row(entry, options)
                    writer.writerow(row)
                    
                    # Progress callback
                    if options.progress_callback:
                        options.progress_callback(i + 1, len(entries))
            
            return True
            
        except Exception as e:
            logger.error(f"CSV export error: {e}")
            return False
    
    def _export_json(self, file_path: Path, options: ExportOptions) -> bool:
        """Export to JSON format."""
        try:
            entries = self._get_filtered_entries(options)
            
            export_data = {
                'vocabulary': [entry.to_dict() for entry in entries],
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_entries': len(entries),
                    'export_options': {
                        'status_filter': options.status_filter,
                        'theme_filter': options.theme_filter,
                        'difficulty_filter': options.difficulty_filter
                    }
                }
            }
            
            if options.include_statistics:
                from ..models.enhanced_vocabulary import VocabularyAnalytics
                analytics = VocabularyAnalytics(entries)
                export_data['statistics'] = analytics.get_learning_statistics()
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            return False
    
    def _export_anki(self, file_path: Path, options: ExportOptions) -> bool:
        """Export to Anki format."""
        try:
            entries = self._get_filtered_entries(options)
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                for entry in entries:
                    # Front: Spanish
                    front = entry.spanish
                    
                    # Back: English + additional info
                    back = entry.english
                    
                    if entry.phonetic:
                        back += f" [{entry.phonetic}]"
                    
                    if entry.personal_notes:
                        back += f"<br><br><small>{entry.personal_notes}</small>"
                    
                    # Tags
                    tags = []
                    tags.extend(entry.themes)
                    tags.extend(entry.custom_tags)
                    tags_str = " ".join(f"#{tag}" for tag in tags)
                    
                    if tags_str:
                        back += f"<br><br>{tags_str}"
                    
                    # Write tab-separated line
                    f.write(f"{front}\t{back}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Anki export error: {e}")
            return False
    
    def _export_xml(self, file_path: Path, options: ExportOptions) -> bool:
        """Export to XML format."""
        try:
            entries = self._get_filtered_entries(options)
            
            # Create XML structure
            root = ET.Element("vocabulary")
            root.set("export_date", datetime.now().isoformat())
            root.set("total_entries", str(len(entries)))
            
            for entry in entries:
                entry_elem = ET.SubElement(root, "entry")
                entry_elem.set("id", entry.id)
                
                # Add fields as subelements
                fields_to_export = {
                    'spanish': entry.spanish,
                    'english': entry.english,
                    'phonetic': entry.phonetic,
                    'part_of_speech': entry.part_of_speech,
                    'difficulty': entry.difficulty.name,
                    'status': entry.status.value,
                    'priority': str(entry.priority),
                    'created_date': entry.created_date,
                    'themes': ';'.join(entry.themes),
                    'tags': ';'.join(entry.custom_tags),
                    'notes': entry.personal_notes
                }
                
                for field_name, field_value in fields_to_export.items():
                    if field_value:  # Only include non-empty fields
                        field_elem = ET.SubElement(entry_elem, field_name)
                        field_elem.text = str(field_value)
            
            # Write XML file
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding=options.encoding, xml_declaration=True)
            
            return True
            
        except Exception as e:
            logger.error(f"XML export error: {e}")
            return False
    
    def _export_tsv(self, file_path: Path, options: ExportOptions) -> bool:
        """Export to TSV format."""
        options.delimiter = '\t'
        return self._export_csv(file_path, options)
    
    def _export_html(self, file_path: Path, options: ExportOptions) -> bool:
        """Export to HTML format."""
        try:
            entries = self._get_filtered_entries(options)
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Vocabulary Export</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .themes {{ color: #666; font-size: 0.9em; }}
        .notes {{ font-style: italic; color: #888; max-width: 200px; }}
        .difficulty {{ font-weight: bold; }}
        .beginner {{ color: #4CAF50; }}
        .elementary {{ color: #8BC34A; }}
        .intermediate {{ color: #FF9800; }}
        .advanced {{ color: #FF5722; }}
        .expert {{ color: #F44336; }}
    </style>
</head>
<body>
    <h1>Vocabulary Export</h1>
    <p>Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total entries: {len(entries)}</p>
    
    <table>
        <thead>
            <tr>
                <th>Spanish</th>
                <th>English</th>
                <th>Phonetic</th>
                <th>Difficulty</th>
                <th>Themes</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
"""
            
            for entry in entries:
                difficulty_class = entry.difficulty.name.lower()
                themes_str = ", ".join(entry.themes)
                
                html_content += f"""
            <tr>
                <td><strong>{entry.spanish}</strong></td>
                <td>{entry.english}</td>
                <td>{entry.phonetic}</td>
                <td class="difficulty {difficulty_class}">{entry.difficulty.name}</td>
                <td class="themes">{themes_str}</td>
                <td class="notes">{entry.personal_notes}</td>
            </tr>
"""
            
            html_content += """
        </tbody>
    </table>
</body>
</html>
"""
            
            with open(file_path, 'w', encoding=options.encoding) as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            logger.error(f"HTML export error: {e}")
            return False
    
    def _get_filtered_entries(self, options: ExportOptions) -> List['EnhancedVocabularyEntry']:
        """Get vocabulary entries filtered by export options."""
        all_entries = list(self.vocabulary_manager.vocabulary_cache.values())
        filtered_entries = []
        
        for entry in all_entries:
            # Status filter
            if options.status_filter and entry.status.value not in options.status_filter:
                continue
            
            # Theme filter
            if options.theme_filter and not entry.themes.intersection(set(options.theme_filter)):
                continue
            
            # Difficulty filter
            if options.difficulty_filter and entry.difficulty.value not in options.difficulty_filter:
                continue
            
            # Date range filter
            if options.date_range:
                start_date, end_date = options.date_range
                entry_date = entry.created_date[:10]  # YYYY-MM-DD
                if entry_date < start_date or entry_date > end_date:
                    continue
            
            filtered_entries.append(entry)
        
        return filtered_entries
    
    def _get_export_headers(self, options: ExportOptions) -> List[str]:
        """Get headers for CSV/TSV export."""
        default_headers = [
            'ID', 'Spanish', 'English', 'Phonetic', 'Part of Speech',
            'Difficulty', 'Status', 'Priority', 'Themes', 'Tags',
            'Created Date', 'Notes'
        ]
        
        if options.include_fields:
            return options.include_fields
        elif options.exclude_fields:
            return [h for h in default_headers if h not in options.exclude_fields]
        else:
            headers = default_headers.copy()
            
            # Add custom fields
            if options.custom_fields:
                headers.extend(options.custom_fields.keys())
            
            # Add statistics if requested
            if options.include_statistics:
                headers.extend(['Study Sessions', 'Accuracy', 'Learning Score'])
            
            return headers
    
    def _entry_to_row(self, entry: 'EnhancedVocabularyEntry', 
                     options: ExportOptions) -> List[str]:
        """Convert vocabulary entry to CSV row."""
        row = [
            entry.id,
            entry.spanish,
            entry.english,
            entry.phonetic,
            entry.part_of_speech,
            entry.difficulty.name,
            entry.status.value,
            str(entry.priority),
            ';'.join(entry.themes),
            ';'.join(entry.custom_tags),
            entry.created_date,
            entry.personal_notes
        ]
        
        # Add custom fields
        if options.custom_fields:
            for field_name, field_expression in options.custom_fields.items():
                try:
                    # Simple field expressions (could be expanded)
                    if field_expression == 'word_length':
                        row.append(str(len(entry.spanish)))
                    elif field_expression == 'theme_count':
                        row.append(str(len(entry.themes)))
                    else:
                        row.append('')  # Unknown expression
                except:
                    row.append('')
        
        # Add statistics if requested
        if options.include_statistics:
            row.extend([
                str(entry.frequency_data.study_sessions),
                f"{entry.frequency_data.calculate_accuracy():.1f}%",
                f"{entry.get_learning_score():.1f}"
            ])
        
        return row
    
    def _compress_file(self, file_path: Path):
        """Compress exported file using gzip."""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            # Remove original file
            file_path.unlink()
            
            logger.info(f"File compressed to {compressed_path}")
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
    
    def create_backup(self, backup_dir: Path, include_metadata: bool = True) -> Path:
        """Create a complete backup of vocabulary data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"vocabulary_backup_{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Export vocabulary data
                temp_json = backup_dir / "vocabulary.json"
                if self._export_json(temp_json, ExportOptions(include_metadata=include_metadata)):
                    zipf.write(temp_json, "vocabulary.json")
                    temp_json.unlink()
                
                # Export as CSV for compatibility
                temp_csv = backup_dir / "vocabulary.csv"
                if self._export_csv(temp_csv, ExportOptions()):
                    zipf.write(temp_csv, "vocabulary.csv")
                    temp_csv.unlink()
                
                # Include database file if exists
                if self.vocabulary_manager.db_path.exists():
                    zipf.write(self.vocabulary_manager.db_path, "vocabulary.db")
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise