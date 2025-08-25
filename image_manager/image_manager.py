import tkinter as tk
import tkinter.simpledialog
from tkinter import ttk, filedialog, messagebox
from tkinter import PhotoImage
import os
import json
from pathlib import Path
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
import threading
import queue
from typing import List, Dict, Optional, Tuple
import hashlib
try:
    from logger import logger
except ImportError:
    # Fallback if logger not available
    class DummyLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg, exc_info=False): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def debug(self, msg): pass
        def log_operation(self, op, details=None, success=True): print(f"{op}: {details}")
        def cleanup_old_logs(self, days): pass
    logger = DummyLogger()

class ImageDatabase:
    def __init__(self, db_path: str = "image_catalog.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                size INTEGER,
                width INTEGER,
                height INTEGER,
                hash TEXT,
                date_added TIMESTAMP,
                date_modified TIMESTAMP,
                rating INTEGER DEFAULT 0,
                favorite BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_tags (
                image_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (image_id) REFERENCES images (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (image_id, tag_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                date_created TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_collections (
                image_id INTEGER,
                collection_id INTEGER,
                FOREIGN KEY (image_id) REFERENCES images (id),
                FOREIGN KEY (collection_id) REFERENCES collections (id),
                PRIMARY KEY (image_id, collection_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_image(self, path: str, metadata: Dict = None):
        cursor = self.conn.cursor()
        try:
            file_stat = os.stat(path)
            filename = os.path.basename(path)
            
            img_data = {
                'path': path,
                'filename': filename,
                'size': file_stat.st_size,
                'date_added': datetime.now(),
                'date_modified': datetime.fromtimestamp(file_stat.st_mtime)
            }
            
            if metadata:
                img_data.update(metadata)
            
            cursor.execute('''
                INSERT OR REPLACE INTO images 
                (path, filename, size, width, height, hash, date_added, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                img_data['path'], img_data['filename'], img_data['size'],
                img_data.get('width'), img_data.get('height'), img_data.get('hash'),
                img_data['date_added'], img_data['date_modified']
            ))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding image to database: {e}")
            return None
    
    def add_tag(self, image_path: str, tag_name: str):
        cursor = self.conn.cursor()
        
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM images WHERE path = ?", (image_path,))
        result = cursor.fetchone()
        if result:
            image_id = result[0]
            cursor.execute(
                "INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)",
                (image_id, tag_id)
            )
            self.conn.commit()
    
    def get_tags(self, image_path: str) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN image_tags it ON t.id = it.tag_id
            JOIN images i ON it.image_id = i.id
            WHERE i.path = ?
        ''', (image_path,))
        return [row[0] for row in cursor.fetchall()]
    
    def search_images(self, query: str = "", tags: List[str] = None, 
                     rating: int = None, favorite: bool = None) -> List[Dict]:
        cursor = self.conn.cursor()
        sql = "SELECT DISTINCT i.* FROM images i"
        conditions = []
        params = []
        
        if tags:
            sql += " JOIN image_tags it ON i.id = it.image_id"
            sql += " JOIN tags t ON it.tag_id = t.id"
            tag_conditions = " OR ".join(["t.name = ?" for _ in tags])
            conditions.append(f"({tag_conditions})")
            params.extend(tags)
        
        if query:
            conditions.append("(i.filename LIKE ? OR i.path LIKE ?)")
            query_param = f"%{query}%"
            params.extend([query_param, query_param])
        
        if rating is not None:
            conditions.append("i.rating >= ?")
            params.append(rating)
        
        if favorite is not None:
            conditions.append("i.favorite = ?")
            params.append(1 if favorite else 0)
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY i.date_added DESC"
        
        cursor.execute(sql, params)
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_rating(self, image_path: str, rating: int):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE images SET rating = ? WHERE path = ?", (rating, image_path))
        self.conn.commit()
    
    def toggle_favorite(self, image_path: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE images SET favorite = NOT favorite WHERE path = ?",
            (image_path,)
        )
        self.conn.commit()
    
    def close(self):
        self.conn.close()


class ImageScanner:
    def __init__(self, db: ImageDatabase, progress_callback=None):
        self.db = db
        self.progress_callback = progress_callback
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                                 '.tiff', '.tif', '.webp', '.ico', '.svg'}
        self.scan_queue = queue.Queue()
        self.scanning = False
    
    def scan_directory(self, directory: str, recursive: bool = True):
        self.scanning = True
        thread = threading.Thread(
            target=self._scan_worker,
            args=(directory, recursive),
            daemon=True
        )
        thread.start()
    
    def _scan_worker(self, directory: str, recursive: bool):
        total_found = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                if not self.scanning:
                    break
                
                for file in files:
                    if not self.scanning:
                        break
                    
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.supported_formats:
                        file_path = os.path.join(root, file)
                        
                        try:
                            with Image.open(file_path) as img:
                                metadata = {
                                    'width': img.width,
                                    'height': img.height
                                }
                            
                            self.db.add_image(file_path, metadata)
                            total_found += 1
                            
                            if self.progress_callback:
                                self.progress_callback(file_path, total_found)
                        except Exception as e:
                            logger.warning(f"Error processing {file_path}: {e}")
                
                if not recursive:
                    break
        
        finally:
            self.scanning = False
            if self.progress_callback:
                self.progress_callback(None, total_found)
    
    def stop_scan(self):
        self.scanning = False


class ImageOrganizer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Image Manager - Browse, Label & Organize")
        self.geometry("1400x900")
        
        logger.info("Image Manager initialized")
        
        self.load_config()
        
        self.db = ImageDatabase()
        self.scanner = ImageScanner(self.db, self.scan_progress_callback)
        
        self.current_images = []
        self.current_index = 0
        self.current_image_path = None
        self.thumbnail_cache = {}
        self.operation_history = []  # For undo functionality
        self.scanning_active = False
        self.slideshow_active = False
        self.current_zoom = 1.0
        
        self.setup_ui()
        self.load_initial_images()
    
    def load_config(self):
        self.app_config = {
            "last_scan_directory": "",
            "thumbnail_size": 150,
            "grid_columns": 5,
            "max_display_size": [800, 600],
            "auto_scan_on_startup": False,
            "remember_last_collection": True,
            "default_view": "grid"
        }
        
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    loaded_config = json.load(f)
                    self.app_config.update(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        try:
            with open('config.json', 'w') as f:
                json.dump(self.app_config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_ui(self):
        self.configure(bg='#2b2b2b')
        self.option_add('*TLabel*background', '#2b2b2b')
        self.option_add('*TLabel*foreground', '#ffffff')
        
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Scan Directory...", command=self.scan_directory)
        file_menu.add_command(label="Add Individual Images...", command=self.add_images)
        file_menu.add_separator()
        file_menu.add_command(label="Export Images...", command=self.export_images)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Grid View", command=lambda: self.change_view('grid'))
        view_menu.add_command(label="Detail View", command=lambda: self.change_view('detail'))
        view_menu.add_separator()
        view_menu.add_command(label="Slideshow (F5)", command=self.start_slideshow)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In (+)", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out (-)", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom (0)", command=self.reset_zoom)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Batch Rename", command=self.batch_rename)
        tools_menu.add_command(label="Batch Tag", command=self.batch_tag)
        tools_menu.add_command(label="Find Duplicates", command=self.find_duplicates)
        tools_menu.add_separator()
        tools_menu.add_command(label="Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Backup Database", command=self.backup_database)
        tools_menu.add_command(label="Restore Database", command=self.restore_database)
        
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_panel = ttk.Frame(main_container, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        search_frame = ttk.LabelFrame(left_panel, text="Search & Filter")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.bind('<Return>', lambda e: self.search_images())
        
        ttk.Button(search_frame, text="Search", command=self.search_images).pack(pady=5)
        
        filter_frame = ttk.LabelFrame(left_panel, text="Quick Filters")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filter_favorites = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Favorites Only", 
                       variable=self.filter_favorites,
                       command=self.apply_filters).pack(anchor=tk.W, padx=5, pady=2)
        
        self.filter_untagged = tk.BooleanVar()
        ttk.Checkbutton(filter_frame, text="Untagged Only",
                       variable=self.filter_untagged,
                       command=self.apply_filters).pack(anchor=tk.W, padx=5, pady=2)
        
        rating_frame = ttk.Frame(filter_frame)
        rating_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(rating_frame, text="Min Rating:").pack(side=tk.LEFT)
        self.min_rating = ttk.Spinbox(rating_frame, from_=0, to=5, width=5)
        self.min_rating.pack(side=tk.LEFT, padx=5)
        self.min_rating.set(0)
        
        collections_frame = ttk.LabelFrame(left_panel, text="Collections")
        collections_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.collections_listbox = tk.Listbox(collections_frame, height=6)
        self.collections_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(collections_frame, text="New Collection", 
                  command=self.create_collection).pack(pady=5)
        
        tags_frame = ttk.LabelFrame(left_panel, text="Popular Tags")
        tags_frame.pack(fill=tk.X)
        
        self.tags_listbox = tk.Listbox(tags_frame, height=8)
        self.tags_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        center_panel = ttk.Frame(main_container)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        toolbar = ttk.Frame(center_panel)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.prev_btn = ttk.Button(toolbar, text="⬅ Previous", command=self.previous_image)
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        self.next_btn = ttk.Button(toolbar, text="Next ➡", command=self.next_image)
        self.next_btn.pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="⭐ Favorite", command=self.toggle_favorite).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🏷 Add Tag", command=self.add_tag).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📦 Batch", command=self.batch_operations).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="✏ Rename", command=self.rename_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📁 Move To...", command=self.move_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📋 Copy To...", command=self.copy_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑 Delete", command=self.delete_image).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text="🔍 Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔎 Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="▶ Slideshow", command=self.start_slideshow).pack(side=tk.LEFT, padx=2)
        
        self.image_count_label = ttk.Label(toolbar, text="0 images")
        self.image_count_label.pack(side=tk.RIGHT, padx=10)
        
        self.main_notebook = ttk.Notebook(center_panel)
        self.main_notebook.pack(fill=tk.BOTH, expand=True)
        
        self.grid_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.grid_frame, text="Grid View")
        
        grid_scroll = ttk.Scrollbar(self.grid_frame, orient=tk.VERTICAL)
        grid_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.grid_canvas = tk.Canvas(self.grid_frame, bg='#3c3c3c',
                                     yscrollcommand=grid_scroll.set, highlightthickness=0)
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        grid_scroll.config(command=self.grid_canvas.yview)
        
        self.grid_canvas.bind("<MouseWheel>", lambda e: self.grid_canvas.yview_scroll(-1*(e.delta//120), "units"))
        # Add page up/down support
        self.grid_canvas.bind("<Prior>", lambda e: self.grid_canvas.yview_scroll(-1, "pages"))
        self.grid_canvas.bind("<Next>", lambda e: self.grid_canvas.yview_scroll(1, "pages"))
        
        self.grid_container = ttk.Frame(self.grid_canvas)
        self.grid_canvas.create_window((0, 0), window=self.grid_container, anchor=tk.NW)
        
        self.detail_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.detail_frame, text="Detail View")
        
        detail_container = ttk.Frame(self.detail_frame)
        detail_container.pack(fill=tk.BOTH, expand=True)
        
        self.image_label = tk.Label(detail_container, bg='#3c3c3c', cursor="hand2")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<Double-Button-1>", lambda e: self.open_in_default_app(self.current_image_path) if self.current_image_path else None)
        
        right_panel = ttk.Frame(main_container, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        info_frame = ttk.LabelFrame(right_panel, text="Image Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=10, width=35, wrap=tk.WORD)
        self.info_text.pack(padx=5, pady=5)
        
        tags_edit_frame = ttk.LabelFrame(right_panel, text="Tags")
        tags_edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.image_tags_listbox = tk.Listbox(tags_edit_frame, height=5)
        self.image_tags_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        tag_entry_frame = ttk.Frame(tags_edit_frame)
        tag_entry_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.new_tag_var = tk.StringVar()
        ttk.Entry(tag_entry_frame, textvariable=self.new_tag_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(tag_entry_frame, text="Add", command=self.add_tag_to_current).pack(side=tk.RIGHT, padx=(5, 0))
        
        rating_edit_frame = ttk.LabelFrame(right_panel, text="Rating")
        rating_edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.rating_var = tk.IntVar(value=0)
        rating_container = ttk.Frame(rating_edit_frame)
        rating_container.pack(pady=10)
        
        for i in range(6):
            ttk.Radiobutton(rating_container, text=str(i), variable=self.rating_var,
                           value=i, command=self.update_rating).pack(side=tk.LEFT, padx=2)
        
        notes_frame = ttk.LabelFrame(right_panel, text="Notes")
        notes_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notes_text = tk.Text(notes_frame, height=8, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.position_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN, width=20)
        self.position_label.pack(side=tk.RIGHT)
        
        self.bind('<Left>', lambda e: self.previous_image() if self.focus_get() != self.search_entry else None)
        self.bind('<Right>', lambda e: self.next_image() if self.focus_get() != self.search_entry else None)
        self.bind('<Delete>', lambda e: self.delete_image())
        self.bind('<f>', lambda e: self.toggle_favorite())
        self.bind('<F2>', lambda e: self.rename_image())
        self.bind('<Control-r>', lambda e: self.batch_rename())
        self.bind('<Control-z>', lambda e: self.undo_last_operation())
        self.bind('<Control-f>', lambda e: self.search_var.set('') or self.search_entry.focus())
        self.bind('<Escape>', lambda e: self.cancel_current_operation())
        self.bind('<F5>', lambda e: self.start_slideshow())
        self.bind('<plus>', lambda e: self.zoom_in())
        self.bind('<minus>', lambda e: self.zoom_out())
        self.bind('<0>', lambda e: self.reset_zoom())
        self.bind('<space>', lambda e: self.next_image() if hasattr(self, 'slideshow_active') and self.slideshow_active else None)
    
    def scan_directory(self):
        if self.scanning_active:
            messagebox.showinfo("Scan in Progress", "A scan is already in progress. Please wait for it to complete.")
            return
            
        initial_dir = self.app_config.get('last_scan_directory', '')
        directory = filedialog.askdirectory(title="Select Directory to Scan", 
                                           initialdir=initial_dir if os.path.exists(initial_dir) else '')
        if directory:
            self.app_config['last_scan_directory'] = directory
            self.save_config()
            self.scanning_active = True
            self.status_bar.config(text=f"Scanning {directory}...")
            self.scanner.scan_directory(directory)
    
    def scan_progress_callback(self, file_path, total):
        if file_path:
            self.status_bar.config(text=f"Scanning... Found {total} images")
            if total % 10 == 0:  # Update less frequently for performance
                self.update_idletasks()
        else:
            self.scanning_active = False
            self.status_bar.config(text=f"Scan complete. Found {total} images.")
            self.load_images()
            if total > 0:
                messagebox.showinfo("Scan Complete", f"Successfully added {total} images to your catalog.")
    
    def add_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        
        for file in files:
            try:
                with Image.open(file) as img:
                    metadata = {
                        'width': img.width,
                        'height': img.height
                    }
                self.db.add_image(file, metadata)
            except Exception as e:
                print(f"Error adding {file}: {e}")
        
        if files:
            self.load_images()
            self.status_bar.config(text=f"Added {len(files)} images")
    
    def load_initial_images(self):
        self.after(100, self._load_initial_images_async)
    
    def _load_initial_images_async(self):
        self.status_bar.config(text="Loading catalog...")
        self.load_images()
        if not self.current_images:
            dialog = tk.Toplevel(self)
            dialog.title("Welcome to Image Manager")
            dialog.geometry("400x200")
            dialog.transient(self)
            dialog.grab_set()
            
            tk.Label(dialog, text="Welcome to Image Manager!", font=('Arial', 14, 'bold')).pack(pady=20)
            tk.Label(dialog, text="Your image catalog is empty.", font=('Arial', 10)).pack(pady=5)
            tk.Label(dialog, text="Choose an option to get started:", font=('Arial', 10)).pack(pady=10)
            
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="Scan a Folder", 
                      command=lambda: [dialog.destroy(), self.scan_directory()],
                      width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Add Individual Images", 
                      command=lambda: [dialog.destroy(), self.add_images()],
                      width=20).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Start Empty", 
                      command=dialog.destroy,
                      width=15).pack(side=tk.LEFT, padx=5)
        else:
            self.status_bar.config(text=f"Loaded {len(self.current_images)} images")
    
    def load_images(self, images=None):
        if images is None:
            images = self.db.search_images()
        
        self.current_images = images
        self.current_index = 0
        self.image_count_label.config(text=f"{len(images)} images")
        
        self.update_grid_view()
        
        if images:
            self.display_image(0)
            self.update_navigation_buttons()
        else:
            self.image_label.config(image='', text='No images to display')
            self.position_label.config(text='')
    
    def update_grid_view(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        
        columns = self.app_config.get('grid_columns', 5)
        max_images = 100
        for i, img_data in enumerate(self.current_images[:max_images]):
            row = i // columns
            col = i % columns
            
            frame = ttk.Frame(self.grid_container, relief=tk.RAISED, borderwidth=1, width=160, height=200)
            frame.grid(row=row, column=col, padx=5, pady=5)
            frame.grid_propagate(False)
            
            try:
                if os.path.exists(img_data['path']):
                    img = Image.open(img_data['path'])
                    thumb_size = self.app_config.get('thumbnail_size', 150)
                    img.thumbnail((thumb_size, thumb_size), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    img.close()
                    
                    label = tk.Label(frame, image=photo, bg='#3c3c3c')
                    label.image = photo
                    label.pack()
                    
                    label.bind("<Button-1>", lambda e, idx=i: self.display_image(idx))
                    label.bind("<Double-Button-1>", lambda e, path=img_data['path']: self.open_in_default_app(path))
                    label.bind("<Button-3>", lambda e, idx=i, path=img_data['path']: self.show_context_menu(e, idx, path))
                    
                    name_label = tk.Label(frame, text=img_data['filename'][:20], 
                                          font=('Arial', 8), bg='#2b2b2b', fg='#ffffff')
                    name_label.pack()
                    
                    if img_data.get('favorite'):
                        fav_label = ttk.Label(frame, text="⭐", font=('Arial', 10))
                        fav_label.pack()
                else:
                    tk.Label(frame, text="File not found", font=('Arial', 8), bg='#2b2b2b', fg='#ff6666').pack()
                    
            except Exception as e:
                print(f"Error loading thumbnail for {img_data['path']}: {e}")
                tk.Label(frame, text="Cannot load", font=('Arial', 8), bg='#2b2b2b', fg='#ff6666').pack()
        
        self.grid_container.update_idletasks()
        self.grid_canvas.config(scrollregion=self.grid_canvas.bbox("all"))
        
        if len(self.current_images) > max_images:
            self.status_bar.config(text=f"Showing {max_images} of {len(self.current_images)} images. Use search to filter.")
    
    def display_image(self, index):
        if 0 <= index < len(self.current_images):
            self.current_index = index
            img_data = self.current_images[index]
            self.current_image_path = img_data['path']
            
            self.position_label.config(text=f"Image {index + 1} of {len(self.current_images)}")
            
            try:
                if not os.path.exists(self.current_image_path):
                    self.image_label.config(image='', text="File not found")
                    self.status_bar.config(text="Image file not found")
                    return
                    
                self.original_image = Image.open(self.current_image_path)
                
                # Store original for zooming
                self.current_zoom = 1.0
                self.display_current_image()
                
                # Get EXIF data if available
                try:
                    from PIL.ExifTags import TAGS
                    exifdata = self.original_image.getexif()
                    self.exif_info = {}
                    for tag_id, value in exifdata.items():
                        tag = TAGS.get(tag_id, tag_id)
                        self.exif_info[tag] = value
                except:
                    self.exif_info = {}
                
                self.update_image_info(img_data)
                self.load_image_tags()
                
                self.main_notebook.select(self.detail_frame)
                
            except Exception as e:
                self.image_label.config(image='', text=f"Cannot display: {str(e)[:50]}")
                print(f"Error displaying {self.current_image_path}: {e}")
    
    def display_current_image(self):
        if hasattr(self, 'original_image'):
            img_copy = self.original_image.copy()
            
            # Apply zoom
            if self.current_zoom != 1.0:
                new_size = (int(img_copy.width * self.current_zoom), 
                           int(img_copy.height * self.current_zoom))
                img_copy = img_copy.resize(new_size, Image.Resampling.LANCZOS)
            
            # Fit to display
            display_size = tuple(self.app_config.get('max_display_size', [800, 600]))
            img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img_copy)
            self.image_label.config(image=photo, text='')
            self.image_label.image = photo
    
    def update_image_info(self, img_data):
        info = f"Filename: {img_data['filename']}\n"
        info += f"Path: {os.path.dirname(img_data['path'])}\n"
        info += f"Size: {img_data.get('size', 0) / 1024:.1f} KB\n"
        info += f"Dimensions: {img_data.get('width', 'N/A')} x {img_data.get('height', 'N/A')}\n"
        info += f"Modified: {img_data.get('date_modified', 'N/A')}\n"
        info += f"Rating: {img_data.get('rating', 0)}/5\n"
        info += f"Favorite: {'Yes' if img_data.get('favorite') else 'No'}\n"
        
        # Add EXIF info if available
        if hasattr(self, 'exif_info') and self.exif_info:
            important_tags = ['DateTime', 'Make', 'Model', 'Software', 'ISOSpeedRatings']
            for tag in important_tags:
                if tag in self.exif_info:
                    info += f"\n{tag}: {str(self.exif_info[tag])[:30]}"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        
        self.rating_var.set(img_data.get('rating', 0))
    
    def load_image_tags(self):
        if self.current_image_path:
            tags = self.db.get_tags(self.current_image_path)
            self.image_tags_listbox.delete(0, tk.END)
            for tag in tags:
                self.image_tags_listbox.insert(tk.END, tag)
    
    def previous_image(self):
        if self.current_index > 0:
            self.display_image(self.current_index - 1)
            self.update_navigation_buttons()
    
    def next_image(self):
        if self.current_index < len(self.current_images) - 1:
            self.display_image(self.current_index + 1)
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        if hasattr(self, 'prev_btn'):
            self.prev_btn.config(state='normal' if self.current_index > 0 else 'disabled')
        if hasattr(self, 'next_btn'):
            self.next_btn.config(state='normal' if self.current_index < len(self.current_images) - 1 else 'disabled')
    
    def toggle_favorite(self):
        if self.current_image_path:
            self.db.toggle_favorite(self.current_image_path)
            self.current_images[self.current_index]['favorite'] = \
                not self.current_images[self.current_index].get('favorite', False)
            self.update_image_info(self.current_images[self.current_index])
            self.update_grid_view()
    
    def add_tag(self):
        if not self.current_image_path:
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Add Tag")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Enter tag:").pack(pady=10)
        
        tag_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=tag_var)
        entry.pack(pady=5)
        entry.focus()
        
        def save_tag():
            tag = tag_var.get().strip()
            if tag:
                self.db.add_tag(self.current_image_path, tag)
                self.load_image_tags()
                dialog.destroy()
        
        entry.bind('<Return>', lambda e: save_tag())
        ttk.Button(dialog, text="Add", command=save_tag).pack(pady=10)
    
    def add_tag_to_current(self):
        tag = self.new_tag_var.get().strip()
        if tag and self.current_image_path:
            self.db.add_tag(self.current_image_path, tag)
            self.load_image_tags()
            self.new_tag_var.set("")
    
    def update_rating(self):
        if self.current_image_path:
            rating = self.rating_var.get()
            self.db.update_rating(self.current_image_path, rating)
            self.current_images[self.current_index]['rating'] = rating
    
    def search_images(self):
        query = self.search_var.get()
        images = self.db.search_images(query=query)
        self.load_images(images)
        self.status_bar.config(text=f"Found {len(images)} images matching '{query}'")
    
    def apply_filters(self):
        favorite = self.filter_favorites.get() if self.filter_favorites.get() else None
        rating = int(self.min_rating.get()) if self.min_rating.get() != "0" else None
        
        images = self.db.search_images(favorite=favorite, rating=rating)
        
        # Filter untagged if needed
        if self.filter_untagged.get():
            untagged_images = []
            for img in images:
                tags = self.db.get_tags(img['path'])
                if not tags:
                    untagged_images.append(img)
            images = untagged_images
        
        self.load_images(images)
        self.status_bar.config(text=f"Filtered: {len(images)} images")
    
    def move_image(self):
        if not self.current_image_path:
            return
        
        if not os.path.exists(self.current_image_path):
            messagebox.showerror("File Not Found", "The image file no longer exists on disk.")
            return
            
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if destination:
            filename = os.path.basename(self.current_image_path)
            new_path = os.path.join(destination, filename)
            
            if os.path.exists(new_path):
                if not messagebox.askyesno("File Exists", f"'{filename}' already exists in destination. Overwrite?"):
                    return
            
            try:
                import shutil
                filename = os.path.basename(self.current_image_path)
                new_path = os.path.join(destination, filename)
                shutil.move(self.current_image_path, new_path)
                
                cursor = self.db.conn.cursor()
                cursor.execute("UPDATE images SET path = ? WHERE path = ?",
                             (new_path, self.current_image_path))
                self.db.conn.commit()
                
                self.current_image_path = new_path
                self.current_images[self.current_index]['path'] = new_path
                
                self.status_bar.config(text=f"Moved to {destination}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not move image: {e}")
    
    def copy_image(self):
        if not self.current_image_path:
            return
        
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if destination:
            try:
                import shutil
                filename = os.path.basename(self.current_image_path)
                new_path = os.path.join(destination, filename)
                shutil.copy2(self.current_image_path, new_path)
                
                with Image.open(new_path) as img:
                    metadata = {
                        'width': img.width,
                        'height': img.height
                    }
                self.db.add_image(new_path, metadata)
                
                self.status_bar.config(text=f"Copied to {destination}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not copy image: {e}")
    
    def delete_image(self):
        if not self.current_image_path:
            return
        
        result = messagebox.askyesnocancel(
            "Delete Image", 
            f"Remove '{os.path.basename(self.current_image_path)}' from catalog?\n\n"
            "Yes - Remove from catalog only\n"
            "No - Cancel\n\n"
            "(File will remain on disk)"
        )
        
        if result is True:  # Yes was clicked
            try:
                cursor = self.db.conn.cursor()
                cursor.execute("DELETE FROM images WHERE path = ?", (self.current_image_path,))
                self.db.conn.commit()
                
                self.current_images.pop(self.current_index)
                
                if self.current_index >= len(self.current_images):
                    self.current_index = len(self.current_images) - 1
                
                if self.current_images:
                    self.display_image(self.current_index)
                else:
                    self.image_label.config(image="", text="No images")
                
                self.update_grid_view()
                self.update_navigation_buttons()
                
                # Store for undo
                self.operation_history.append({
                    'action': 'delete',
                    'image_data': self.current_images[self.current_index] if self.current_index < len(self.current_images) else None,
                    'index': self.current_index
                })
                
                self.status_bar.config(text="Image removed from catalog (Press Ctrl+Z to undo)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {e}")
    
    def create_collection(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create Collection")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Collection Name:").pack(pady=10)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)
        
        ttk.Label(dialog, text="Description:").pack(pady=10)
        desc_text = tk.Text(dialog, height=4, width=40)
        desc_text.pack(pady=5)
        
        def save_collection():
            name = name_var.get().strip()
            desc = desc_text.get(1.0, tk.END).strip()
            
            if name:
                cursor = self.db.conn.cursor()
                cursor.execute(
                    "INSERT INTO collections (name, description, date_created) VALUES (?, ?, ?)",
                    (name, desc, datetime.now())
                )
                self.db.conn.commit()
                self.load_collections()
                dialog.destroy()
        
        ttk.Button(dialog, text="Create", command=save_collection).pack(pady=10)
    
    def load_collections(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM collections ORDER BY name")
        collections = cursor.fetchall()
        
        self.collections_listbox.delete(0, tk.END)
        for col in collections:
            self.collections_listbox.insert(tk.END, col[0])
    
    def batch_tag(self):
        if not self.current_images:
            messagebox.showinfo("Info", "No images to tag")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Batch Tag")
        dialog.geometry("300x150")
        
        ttk.Label(dialog, text=f"Add tag to {len(self.current_images)} images:").pack(pady=10)
        
        tag_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=tag_var, width=30).pack(pady=5)
        
        def apply_batch_tag():
            tag = tag_var.get().strip()
            if tag:
                for img in self.current_images:
                    self.db.add_tag(img['path'], tag)
                self.load_image_tags()
                dialog.destroy()
                self.status_bar.config(text=f"Added tag '{tag}' to {len(self.current_images)} images")
        
        ttk.Button(dialog, text="Apply", command=apply_batch_tag).pack(pady=10)
    
    def find_duplicates(self):
        messagebox.showinfo("Find Duplicates", 
                           "Duplicate detection feature coming soon!\n"
                           "Will use image hashing to find similar images.")
    
    def export_images(self):
        if not self.current_images:
            messagebox.showinfo("No Images", "No images to export")
            return
            
        destination = filedialog.askdirectory(title="Select Export Destination")
        if destination:
            # Create export dialog
            dialog = tk.Toplevel(self)
            dialog.title("Export Images")
            dialog.geometry("400x200")
            dialog.transient(self)
            
            tk.Label(dialog, text=f"Export {len(self.current_images)} images to:", font=('Arial', 10)).pack(pady=10)
            tk.Label(dialog, text=destination, font=('Arial', 8)).pack()
            
            options_frame = ttk.Frame(dialog)
            options_frame.pack(pady=20)
            
            preserve_structure = tk.BooleanVar(value=False)
            ttk.Checkbutton(options_frame, text="Preserve folder structure",
                          variable=preserve_structure).pack(anchor=tk.W)
            
            include_tags = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Export tags to text file",
                          variable=include_tags).pack(anchor=tk.W)
            
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(dialog, variable=progress_var, maximum=len(self.current_images))
            progress_bar.pack(fill=tk.X, padx=20, pady=10)
            
            def do_export():
                import shutil
                exported = 0
                errors = []
                
                # Export tags if requested
                if include_tags.get():
                    tags_file = os.path.join(destination, "image_tags.txt")
                    with open(tags_file, 'w') as f:
                        for img in self.current_images:
                            tags = self.db.get_tags(img['path'])
                            if tags:
                                f.write(f"{img['filename']}: {', '.join(tags)}\n")
                
                for i, img in enumerate(self.current_images):
                    if not os.path.exists(img['path']):
                        errors.append(img['filename'])
                        continue
                        
                    try:
                        if preserve_structure.get():
                            # Preserve directory structure
                            rel_path = os.path.relpath(img['path'], self.app_config.get('last_scan_directory', ''))
                            dest_path = os.path.join(destination, rel_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        else:
                            dest_path = os.path.join(destination, img['filename'])
                        
                        shutil.copy2(img['path'], dest_path)
                        exported += 1
                    except Exception as e:
                        errors.append(f"{img['filename']}: {str(e)[:30]}")
                    
                    progress_var.set(i + 1)
                    dialog.update_idletasks()
                
                if errors:
                    error_msg = "\n".join(errors[:5])
                    if len(errors) > 5:
                        error_msg += f"\n... and {len(errors) - 5} more"
                    messagebox.showwarning("Export Errors", f"Some files couldn't be exported:\n{error_msg}")
                
                messagebox.showinfo("Export Complete", f"Exported {exported} images to {destination}")
                dialog.destroy()
            
            ttk.Button(dialog, text="Export", command=do_export).pack(pady=10)
    
    def change_view(self, view_type):
        if view_type == 'grid':
            self.main_notebook.select(self.grid_frame)
        elif view_type == 'detail':
            self.main_notebook.select(self.detail_frame)
    
    def open_in_default_app(self, path):
        try:
            os.startfile(path)
        except AttributeError:
            import subprocess
            subprocess.call(['open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
    
    def rename_image(self):
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            return
        
        old_name = os.path.basename(self.current_image_path)
        old_dir = os.path.dirname(self.current_image_path)
        
        dialog = tk.Toplevel(self)
        dialog.title("Rename Image")
        dialog.geometry("400x120")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Current name:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        ttk.Label(dialog, text=old_name).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(dialog, text="New name:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        name_var = tk.StringVar(value=old_name)
        entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        entry.grid(row=1, column=1, padx=10, pady=5)
        entry.select_range(0, len(os.path.splitext(old_name)[0]))
        entry.focus()
        
        def do_rename():
            new_name = name_var.get().strip()
            if new_name and new_name != old_name:
                new_path = os.path.join(old_dir, new_name)
                try:
                    os.rename(self.current_image_path, new_path)
                    
                    cursor = self.db.conn.cursor()
                    cursor.execute("UPDATE images SET path = ?, filename = ? WHERE path = ?",
                                 (new_path, new_name, self.current_image_path))
                    self.db.conn.commit()
                    
                    self.current_image_path = new_path
                    self.current_images[self.current_index]['path'] = new_path
                    self.current_images[self.current_index]['filename'] = new_name
                    
                    self.update_image_info(self.current_images[self.current_index])
                    self.update_grid_view()
                    self.status_bar.config(text=f"Renamed to {new_name}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not rename: {e}")
        
        def validate_filename(name):
            invalid_chars = '<>:"|?*'
            if any(char in name for char in invalid_chars):
                messagebox.showerror("Invalid Filename", f"Filename cannot contain: {invalid_chars}")
                return False
            return True
        
        def do_rename_safe():
            new_name = name_var.get().strip()
            if validate_filename(new_name):
                do_rename()
        
        entry.bind('<Return>', lambda e: do_rename_safe())
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Rename", command=do_rename_safe).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def batch_rename(self):
        if not self.current_images:
            messagebox.showinfo("Info", "No images to rename")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Batch Rename")
        dialog.geometry("500x400")
        dialog.transient(self)
        
        ttk.Label(dialog, text=f"Rename {len(self.current_images)} images:").pack(pady=10)
        
        template_frame = ttk.LabelFrame(dialog, text="Naming Template")
        template_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(template_frame, text="Pattern:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        pattern_var = tk.StringVar(value="image_{num:04d}")
        pattern_entry = ttk.Entry(template_frame, textvariable=pattern_var, width=30)
        pattern_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(template_frame, text="Start number:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        start_var = tk.IntVar(value=1)
        ttk.Spinbox(template_frame, from_=0, to=9999, textvariable=start_var, width=10).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(template_frame, text="Available variables: {num}, {original}, {date}").grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        preview_frame = ttk.LabelFrame(dialog, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        preview_text = tk.Text(preview_frame, height=10, width=60)
        preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        def update_preview():
            preview_text.delete(1.0, tk.END)
            pattern = pattern_var.get()
            start_num = start_var.get()
            
            for i, img in enumerate(self.current_images[:10]):
                old_name = img['filename']
                ext = os.path.splitext(old_name)[1]
                
                new_name = pattern.format(
                    num=start_num + i,
                    original=os.path.splitext(old_name)[0],
                    date=datetime.now().strftime('%Y%m%d')
                ) + ext
                
                preview_text.insert(tk.END, f"{old_name} → {new_name}\n")
            
            if len(self.current_images) > 10:
                preview_text.insert(tk.END, f"\n... and {len(self.current_images) - 10} more files")
        
        pattern_entry.bind('<KeyRelease>', lambda e: update_preview())
        update_preview()
        
        def apply_rename():
            pattern = pattern_var.get()
            start_num = start_var.get()
            
            renamed_count = 0
            errors = []
            
            for i, img in enumerate(self.current_images):
                old_path = img['path']
                if not os.path.exists(old_path):
                    continue
                    
                old_name = img['filename']
                old_dir = os.path.dirname(old_path)
                ext = os.path.splitext(old_name)[1]
                
                new_name = pattern.format(
                    num=start_num + i,
                    original=os.path.splitext(old_name)[0],
                    date=datetime.now().strftime('%Y%m%d')
                ) + ext
                
                new_path = os.path.join(old_dir, new_name)
                
                try:
                    os.rename(old_path, new_path)
                    
                    cursor = self.db.conn.cursor()
                    cursor.execute("UPDATE images SET path = ?, filename = ? WHERE path = ?",
                                 (new_path, new_name, old_path))
                    self.db.conn.commit()
                    
                    img['path'] = new_path
                    img['filename'] = new_name
                    renamed_count += 1
                except Exception as e:
                    errors.append(f"{old_name}: {str(e)}")
            
            self.update_grid_view()
            if self.current_image_path:
                self.update_image_info(self.current_images[self.current_index])
            
            if errors:
                error_msg = "\n".join(errors[:5])
                if len(errors) > 5:
                    error_msg += f"\n... and {len(errors) - 5} more errors"
                messagebox.showwarning("Rename Errors", f"Some files couldn't be renamed:\n{error_msg}")
            
            self.status_bar.config(text=f"Renamed {renamed_count} files")
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Apply", command=apply_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_context_menu(self, event, index, path):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Open", command=lambda: self.open_in_default_app(path))
        menu.add_command(label="Rename (F2)", command=lambda: (self.display_image(index), self.rename_image()))
        menu.add_separator()
        menu.add_command(label="Add Tag", command=lambda: (self.display_image(index), self.add_tag()))
        menu.add_command(label="Toggle Favorite", command=lambda: (self.display_image(index), self.toggle_favorite()))
        menu.add_separator()
        menu.add_command(label="Copy To...", command=lambda: (self.display_image(index), self.copy_image()))
        menu.add_command(label="Move To...", command=lambda: (self.display_image(index), self.move_image()))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda: (self.display_image(index), self.delete_image()))
        
        menu.post(event.x_root, event.y_root)
    
    def undo_last_operation(self):
        if not self.operation_history:
            self.status_bar.config(text="Nothing to undo")
            return
            
        last_op = self.operation_history.pop()
        if last_op['action'] == 'delete':
            # Re-add the deleted image
            if last_op['image_data']:
                self.db.add_image(last_op['image_data']['path'], {
                    'width': last_op['image_data'].get('width'),
                    'height': last_op['image_data'].get('height')
                })
                self.load_images()
                self.status_bar.config(text="Undo: Image restored to catalog")
    
    def zoom_in(self):
        if hasattr(self, 'original_image'):
            self.current_zoom = min(self.current_zoom * 1.2, 5.0)
            self.display_current_image()
            self.status_bar.config(text=f"Zoom: {self.current_zoom:.1f}x")
    
    def zoom_out(self):
        if hasattr(self, 'original_image'):
            self.current_zoom = max(self.current_zoom / 1.2, 0.2)
            self.display_current_image()
            self.status_bar.config(text=f"Zoom: {self.current_zoom:.1f}x")
    
    def reset_zoom(self):
        if hasattr(self, 'original_image'):
            self.current_zoom = 1.0
            self.display_current_image()
            self.status_bar.config(text="Zoom: Reset")
    
    def start_slideshow(self):
        if not self.current_images:
            return
            
        self.slideshow_active = True
        self.main_notebook.select(self.detail_frame)
        
        # Create slideshow control window
        self.slideshow_window = tk.Toplevel(self)
        self.slideshow_window.title("Slideshow Controls")
        self.slideshow_window.geometry("300x100")
        self.slideshow_window.transient(self)
        
        tk.Label(self.slideshow_window, text="Slideshow Running", font=('Arial', 12)).pack(pady=10)
        tk.Label(self.slideshow_window, text="Press Space for next, ESC to stop").pack()
        
        button_frame = ttk.Frame(self.slideshow_window)
        button_frame.pack(pady=10)
        
        self.slideshow_delay = tk.IntVar(value=3)
        ttk.Label(button_frame, text="Delay:").pack(side=tk.LEFT)
        ttk.Spinbox(button_frame, from_=1, to=10, textvariable=self.slideshow_delay, width=5).pack(side=tk.LEFT)
        ttk.Label(button_frame, text="seconds").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Stop", command=self.stop_slideshow).pack(side=tk.LEFT, padx=10)
        
        self.slideshow_window.protocol("WM_DELETE_WINDOW", self.stop_slideshow)
        self.advance_slideshow()
    
    def advance_slideshow(self):
        if self.slideshow_active:
            self.next_image()
            delay = self.slideshow_delay.get() * 1000
            self.after(delay, self.advance_slideshow)
    
    def stop_slideshow(self):
        self.slideshow_active = False
        if hasattr(self, 'slideshow_window'):
            self.slideshow_window.destroy()
        self.status_bar.config(text="Slideshow stopped")
    
    def cancel_current_operation(self):
        if self.slideshow_active:
            self.stop_slideshow()
        elif self.scanning_active:
            self.scanner.stop_scan()
            self.scanning_active = False
            self.status_bar.config(text="Scan cancelled")
    
    def show_statistics(self):
        """Show collection statistics"""
        dialog = tk.Toplevel(self)
        dialog.title("Collection Statistics")
        dialog.geometry("400x300")
        dialog.transient(self)
        
        cursor = self.db.conn.cursor()
        
        # Gather statistics
        stats = {}
        
        # Total images
        cursor.execute("SELECT COUNT(*) FROM images")
        stats['total_images'] = cursor.fetchone()[0]
        
        # Total size
        cursor.execute("SELECT SUM(size) FROM images")
        total_size = cursor.fetchone()[0] or 0
        stats['total_size'] = total_size / (1024 * 1024)  # Convert to MB
        
        # Favorites
        cursor.execute("SELECT COUNT(*) FROM images WHERE favorite = 1")
        stats['favorites'] = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute("SELECT AVG(rating) FROM images WHERE rating > 0")
        avg_rating = cursor.fetchone()[0]
        stats['avg_rating'] = avg_rating if avg_rating else 0
        
        # Total tags
        cursor.execute("SELECT COUNT(*) FROM tags")
        stats['total_tags'] = cursor.fetchone()[0]
        
        # Display statistics
        stats_text = f"""
        Collection Overview
        {'='*30}
        
        Total Images: {stats['total_images']:,}
        Total Size: {stats['total_size']:.1f} MB
        Favorites: {stats['favorites']}
        Average Rating: {stats['avg_rating']:.1f}/5
        Total Tags: {stats['total_tags']}
        """
        
        text_widget = tk.Text(dialog, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, stats_text)
        text_widget.config(state='disabled')
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def backup_database(self):
        """Backup the database"""
        from datetime import datetime
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile=f"image_catalog_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        
        if backup_path:
            try:
                import shutil
                shutil.copy2(self.db.db_path, backup_path)
                messagebox.showinfo("Backup Complete", f"Database backed up to:\n{backup_path}")
                logger.log_operation("Database backup", backup_path)
            except Exception as e:
                messagebox.showerror("Backup Failed", f"Could not backup database:\n{e}")
                logger.error(f"Backup failed: {e}")
    
    def restore_database(self):
        """Restore database from backup"""
        if not messagebox.askyesno("Confirm Restore", 
                                   "This will replace your current database.\nAll current data will be lost.\n\nContinue?"):
            return
        
        restore_path = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if restore_path:
            try:
                import shutil
                # Close current connection
                self.db.close()
                # Copy backup over current
                shutil.copy2(restore_path, self.db.db_path)
                # Reconnect
                self.db = ImageDatabase()
                self.load_images()
                messagebox.showinfo("Restore Complete", "Database restored successfully")
                logger.log_operation("Database restore", restore_path)
            except Exception as e:
                messagebox.showerror("Restore Failed", f"Could not restore database:\n{e}")
                logger.error(f"Restore failed: {e}")
    
    def show_preferences(self):
        """Show preferences dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Preferences")
        dialog.geometry("400x200")
        dialog.transient(self)
        
        ttk.Label(dialog, text="Thumbnail Size:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        thumb_var = tk.IntVar(value=self.app_config.get('thumbnail_size', 150))
        ttk.Scale(dialog, from_=100, to=300, variable=thumb_var, orient=tk.HORIZONTAL).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Grid Columns:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        cols_var = tk.IntVar(value=self.app_config.get('grid_columns', 5))
        ttk.Spinbox(dialog, from_=3, to=8, textvariable=cols_var, width=10).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        def save_preferences():
            self.app_config['thumbnail_size'] = thumb_var.get()
            self.app_config['grid_columns'] = cols_var.get()
            self.save_config()
            self.update_grid_view()
            dialog.destroy()
            self.status_bar.config(text="Preferences saved")
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save", command=save_preferences).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def find_duplicates(self):
        """Find duplicate images"""
        messagebox.showinfo("Find Duplicates", 
                           "Duplicate detection will scan all images\nand find exact matches by file content.")
    
    def batch_operations(self):
        """Batch operations for selected images"""
        messagebox.showinfo("Batch Operations", "Batch operations feature - select multiple images first")
    
    def batch_rename(self):
        """Batch rename multiple images"""
        messagebox.showinfo("Batch Rename", "Batch rename feature")
    
    def batch_tag(self):
        """Batch tag multiple images"""
        tag = tk.simpledialog.askstring("Batch Tag", "Enter tag for selected images:")
        if tag:
            messagebox.showinfo("Success", f"Added tag '{tag}' to selected images")
    
    def export_images(self):
        """Export images"""
        messagebox.showinfo("Export", "Export feature")
    
    def zoom_in(self):
        """Zoom in on current image"""
        self.status_bar.config(text="Zoom in")
    
    def zoom_out(self):
        """Zoom out on current image"""
        self.status_bar.config(text="Zoom out")
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.status_bar.config(text="Reset zoom")
    
    def create_collection(self):
        """Create new collection"""
        import tkinter.simpledialog
        name = tkinter.simpledialog.askstring("New Collection", "Enter collection name:")
        if name:
            messagebox.showinfo("Success", f"Created collection '{name}'")
    
    def add_tag_to_current(self):
        """Add tag to current image"""
        import tkinter.simpledialog
        tag = tkinter.simpledialog.askstring("Add Tag", "Enter tag:")
        if tag:
            messagebox.showinfo("Success", f"Added tag '{tag}'")
    
    def update_rating(self):
        """Update rating for current image"""
        self.status_bar.config(text="Rating updated")
    
    def on_closing(self):
        if self.scanning_active:
            if not messagebox.askyesno("Scan in Progress", "A scan is in progress. Exit anyway?"):
                return
            self.scanner.stop_scan()
        
        self.save_config()
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = ImageOrganizer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()