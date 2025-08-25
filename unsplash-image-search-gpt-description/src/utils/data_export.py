"""
Data export utilities for vocabulary and session data.
"""

import csv
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.vocabulary import VocabularyManager


class ExportDialog:
    """Dialog for exporting vocabulary in different formats."""
    
    def __init__(self, parent: tk.Widget, vocabulary_manager: VocabularyManager, data_dir: Path):
        self.parent = parent
        self.vocabulary_manager = vocabulary_manager
        self.data_dir = data_dir
    
    def show_export_dialog(self):
        """Show the export options dialog."""
        if not self.vocabulary_manager.csv_file.exists() or os.path.getsize(self.vocabulary_manager.csv_file) == 0:
            messagebox.showinfo("No Data", "No vocabulary to export yet!")
            return
        
        # Create export dialog
        export_window = tk.Toplevel(self.parent)
        export_window.title("Export Vocabulary")
        export_window.geometry("400x300")
        export_window.transient(self.parent)
        export_window.grab_set()
        
        # Center window
        export_window.update_idletasks()
        x = (export_window.winfo_screenwidth() // 2) - 200
        y = (export_window.winfo_screenheight() // 2) - 150
        export_window.geometry(f"+{x}+{y}")
        
        self._create_export_widgets(export_window)
    
    def _create_export_widgets(self, window: tk.Toplevel):
        """Create the export dialog widgets."""
        # Export options
        frame = ttk.Frame(window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Export Format:", font=('TkDefaultFont', 10, 'bold')).pack(pady=(0, 10))
        
        # Anki export button
        ttk.Button(
            frame, 
            text="📚 Anki (Tab-delimited)", 
            command=lambda: self._export_anki(window), 
            width=30
        ).pack(pady=5)
        
        # Simple text export button
        ttk.Button(
            frame, 
            text="📝 Plain Text", 
            command=lambda: self._export_text(window), 
            width=30
        ).pack(pady=5)
        
        # Open CSV directly button
        ttk.Button(
            frame, 
            text="📊 Open CSV in Excel", 
            command=lambda: self._open_csv(window), 
            width=30
        ).pack(pady=5)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Stats
        self._show_vocabulary_stats(frame)
        
        # Close button
        ttk.Button(frame, text="Close", command=window.destroy).pack(pady=10)
    
    def _show_vocabulary_stats(self, frame: ttk.Frame):
        """Show vocabulary statistics."""
        try:
            word_count = self.vocabulary_manager.get_vocabulary_count()
            ttk.Label(frame, text=f"Total vocabulary: {word_count} words").pack()
        except Exception:
            pass  # Ignore errors in stats display
    
    def _export_anki(self, window: tk.Toplevel):
        """Export vocabulary to Anki format."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            anki_file = self.data_dir / f"anki_export_{timestamp}.txt"
            
            if self.vocabulary_manager.export_to_anki(anki_file):
                messagebox.showinfo(
                    "Success", 
                    f"Exported to:\n{anki_file}\n\nImport this file into Anki using 'Import File'"
                )
                window.destroy()
            else:
                messagebox.showerror("Error", "Export failed")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def _export_text(self, window: tk.Toplevel):
        """Export vocabulary to plain text format."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            text_file = self.data_dir / f"vocabulary_{timestamp}.txt"
            
            if self.vocabulary_manager.export_to_text(text_file):
                messagebox.showinfo("Success", f"Exported to:\n{text_file}")
                window.destroy()
            else:
                messagebox.showerror("Error", "Export failed")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def _open_csv(self, window: tk.Toplevel):
        """Open the CSV file in the default application."""
        try:
            csv_file = self.vocabulary_manager.csv_file
            if sys.platform == "win32":
                os.startfile(csv_file)
            elif sys.platform == "darwin":
                os.system(f"open {csv_file}")
            else:
                os.system(f"xdg-open {csv_file}")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")


class DataExporter:
    """Utility class for various data export operations."""
    
    @staticmethod
    def export_vocabulary_anki(vocabulary_manager: VocabularyManager, output_file: Path) -> bool:
        """Export vocabulary to Anki-compatible format."""
        return vocabulary_manager.export_to_anki(output_file)
    
    @staticmethod
    def export_vocabulary_text(vocabulary_manager: VocabularyManager, output_file: Path) -> bool:
        """Export vocabulary to plain text format."""
        return vocabulary_manager.export_to_text(output_file)
    
    @staticmethod
    def export_session_json(session_data: dict, output_file: Path) -> bool:
        """Export session data to JSON format."""
        try:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting session JSON: {e}")
            return False
    
    @staticmethod
    def export_session_csv(session_data: dict, output_file: Path) -> bool:
        """Export session data to CSV format."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Query', 'Image URL', 'User Note', 'Generated Description'])
                
                for session in session_data.get('sessions', []):
                    for entry in session.get('entries', []):
                        writer.writerow([
                            entry.get('timestamp', ''),
                            entry.get('query', ''),
                            entry.get('image_url', ''),
                            entry.get('user_note', ''),
                            entry.get('generated_description', '')
                        ])
            return True
        except Exception as e:
            print(f"Error exporting session CSV: {e}")
            return False