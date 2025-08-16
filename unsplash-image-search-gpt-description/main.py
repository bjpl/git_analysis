import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
from openai import OpenAI
import os
import sys
import json
import re
import csv
import time
from pathlib import Path
from datetime import datetime
from config_manager import ConfigManager, ensure_api_keys_configured

# ─── CONFIGURATION ─────────────────────────────────────────────
# Configuration is now handled by ConfigManager
# API keys are loaded from environment variables or config.ini


class ImageSearchApp(tk.Tk):
    """
    Aplicación Tkinter que:
      - Busca imágenes en Unsplash (con paginación)
      - Muestra una vista previa de la imagen (izquierda)
      - Acepta notas del usuario y muestra una descripción generada por GPT (derecha)
      - Usa un modelo de GPT con capacidad de visión para generar descripciones en español
      - Extrae palabras/frases clave (sustantivos con artículos, verbos, adjetivos, adverbios, frases) en orden alfabético
      - Muestra esas frases como botones clicables
      - Al hacer clic en una frase, se traduce del español al inglés (EE.UU.) y se registra en un archivo CSV
      - Registra todo en un archivo de sesión y permite "Otra Imagen" y "Nueva Búsqueda"
    """

    def __init__(self):
        super().__init__()
        
        # Initialize configuration
        self.config_manager = ensure_api_keys_configured(self)
        if not self.config_manager:
            # User cancelled setup
            self.destroy()
            return
        
        # Load API keys and paths
        api_keys = self.config_manager.get_api_keys()
        paths = self.config_manager.get_paths()
        
        self.UNSPLASH_ACCESS_KEY = api_keys['unsplash']
        self.OPENAI_API_KEY = api_keys['openai']
        self.GPT_MODEL = api_keys['gpt_model']
        
        # Initialize OpenAI client with new SDK
        self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
        
        # Set up paths
        self.DATA_DIR = paths['data_dir']
        self.LOG_FILENAME = paths['log_file']
        self.CSV_TARGET_WORDS = paths['vocabulary_file']
        
        # Ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV with headers if it doesn't exist
        if not self.CSV_TARGET_WORDS.exists():
            with open(self.CSV_TARGET_WORDS, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
        
        self.title("Búsqueda de Imágenes en Unsplash & Descripción GPT")
        self.geometry("1100x800")
        self.resizable(True, True)

        self.log_entries = []
        self.extracted_phrases = {}
        self.target_phrases = []
        self.used_image_urls = set()
        self.vocabulary_cache = set()  # Cache to prevent duplicates
        self.image_cache = {}  # Simple cache for downloaded images

        # Estado de paginación
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None

        self.load_used_image_urls_from_log()
        self.load_vocabulary_cache()

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Show API status in title
        self.update_title_with_status()
        
        # Load last search if exists
        self.load_last_search()
        
        # Initialize stats
        self.update_stats()

    def update_title_with_status(self):
        """Update window title with API status."""
        model = self.GPT_MODEL
        self.title(f"Unsplash & GPT Tool - Model: {model}")
    
    def load_last_search(self):
        """Load the last search query from previous session."""
        try:
            last_search_file = self.DATA_DIR / "last_search.txt"
            if last_search_file.exists():
                with open(last_search_file, 'r', encoding='utf-8') as f:
                    last_query = f.read().strip()
                    if last_query:
                        self.search_entry.insert(0, last_query)
                        self.search_entry.selection_range(0, tk.END)  # Select all text
        except:
            pass  # Ignore errors
    
    def save_last_search(self):
        """Save the current search query for next session."""
        try:
            if self.current_query:
                last_search_file = self.DATA_DIR / "last_search.txt"
                with open(last_search_file, 'w', encoding='utf-8') as f:
                    f.write(self.current_query)
        except:
            pass  # Ignore errors

    def canonicalize_url(self, url):
        """Retorna la URL base sin parámetros de consulta."""
        return url.split('?')[0] if url else ""

    def load_vocabulary_cache(self):
        """Load existing vocabulary to prevent duplicates."""
        if self.CSV_TARGET_WORDS.exists():
            try:
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'Spanish' in row:
                            self.vocabulary_cache.add(row['Spanish'])
            except Exception as e:
                # If file is corrupted or has old format, try to read as simple CSV
                try:
                    with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader, None)  # Skip header if exists
                        for row in reader:
                            if row and len(row) > 0:
                                self.vocabulary_cache.add(row[0])
                except Exception:
                    pass  # Start fresh if all fails

    def load_used_image_urls_from_log(self):
        """Carga URLs de imagen usadas desde el archivo de sesión JSON."""
        if self.LOG_FILENAME.exists():
            try:
                with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for session in data.get('sessions', []):
                        for entry in session.get('entries', []):
                            url = entry.get('image_url', '')
                            if url:
                                self.used_image_urls.add(self.canonicalize_url(url))
            except (json.JSONDecodeError, Exception):
                # If JSON is corrupted, try to read as text (backwards compatibility)
                try:
                    with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                        for line in f:
                            if "URL de la Imagen" in line:
                                parts = line.split(":", 1)
                                if len(parts) == 2:
                                    url = parts[1].strip()
                                    if url:
                                        self.used_image_urls.add(self.canonicalize_url(url))
                except Exception:
                    pass

    def api_call_with_retry(self, func, *args, max_retries=3, **kwargs):
        """
        Execute an API call with exponential backoff retry logic.
        """
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    self.update_status(f"API error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                continue
            except Exception as e:
                last_exception = e
                if "rate_limit" in str(e).lower():
                    self.update_status("Rate limit reached. Please wait a moment...")
                    time.sleep(5)
                    continue
                break
        
        # If all retries failed
        raise last_exception

    def create_widgets(self):
        # Contenedor principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # CONTROLES DE BÚSQUEDA (arriba)
        search_frame = ttk.Frame(main_frame, padding="5")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Consulta en Unsplash:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_image())
        # Add Ctrl+G shortcut for generating description
        self.bind('<Control-g>', lambda e: self.generate_description())
        
        self.search_button = ttk.Button(search_frame, text="Buscar Imagen", command=self.search_image)
        self.search_button.grid(row=0, column=2, padx=5)
        
        # Progress bar for API calls
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            search_frame, 
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.grid(row=0, column=3, padx=5, sticky="ew")
        self.progress_bar.grid_remove()  # Hidden by default
        
        self.another_button = ttk.Button(search_frame, text="Otra Imagen", command=self.another_image)
        self.another_button.grid(row=1, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        self.newsearch_button = ttk.Button(search_frame, text="Nueva Búsqueda", command=self.change_search)
        self.newsearch_button.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=tk.W)
        
        # Export button
        self.export_button = ttk.Button(search_frame, text="📤 Export", command=self.export_vocabulary)
        self.export_button.grid(row=1, column=2, padx=5, pady=(5, 0), sticky=tk.W)

        # BARRA DE ESTADO with statistics
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Session stats
        self.stats_label = ttk.Label(status_frame, text="Images: 0 | Words: 0", relief=tk.SUNKEN, anchor=tk.E)
        self.stats_label.pack(side=tk.RIGHT, padx=(5, 0))

        # ÁREA DE CONTENIDO (Imagen a la izquierda, área de texto a la derecha)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # IZQUIERDA: Vista Previa de la Imagen
        image_frame = ttk.LabelFrame(content_frame, text="Vista Previa", padding="10")
        image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        image_frame.rowconfigure(0, weight=1)
        image_frame.columnconfigure(0, weight=1)
        self.image_label = ttk.Label(image_frame)
        self.image_label.grid(row=0, column=0, sticky="nsew")

        # DERECHA: Área de Texto (Notas, Descripción GPT, Sección Inferior)
        self.text_area_frame = ttk.Frame(content_frame)
        self.text_area_frame.grid(row=0, column=1, sticky="nsew")
        self.text_area_frame.rowconfigure(0, weight=1)  # Notas
        self.text_area_frame.rowconfigure(1, weight=1)  # Descripción GPT
        self.text_area_frame.rowconfigure(2, weight=0)  # Sección Inferior (Frases Extraídas y Frases Objetivo)
        self.text_area_frame.columnconfigure(0, weight=1)

        # 1) Notas del Usuario
        notes_frame = ttk.LabelFrame(self.text_area_frame, text="Tus Notas / Descripción", padding="10")
        notes_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 5))
        notes_frame.rowconfigure(0, weight=1)
        notes_frame.columnconfigure(0, weight=1)
        self.note_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD)
        self.note_text.grid(row=0, column=0, sticky="nsew")

        # 2) Descripción GPT
        desc_frame = ttk.LabelFrame(self.text_area_frame, text="Descripción Generada por GPT", padding="10")
        desc_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        desc_frame.rowconfigure(0, weight=1)
        desc_frame.columnconfigure(0, weight=1)
        self.description_text = scrolledtext.ScrolledText(desc_frame, wrap=tk.WORD, state=tk.DISABLED)
        # Increase the font size for the description
        self.description_text.configure(font=("TkDefaultFont", 14))
        self.description_text.grid(row=0, column=0, sticky="nsew")
        
        # Button frame for description actions
        desc_button_frame = ttk.Frame(desc_frame)
        desc_button_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        self.generate_desc_button = ttk.Button(
            desc_button_frame, 
            text="Generar Descripción", 
            command=self.generate_description
        )
        self.generate_desc_button.pack(side=tk.RIGHT)
        
        # Copy button for description
        self.copy_desc_button = ttk.Button(
            desc_button_frame,
            text="📋 Copiar",
            command=self.copy_description,
            state=tk.DISABLED
        )
        self.copy_desc_button.pack(side=tk.RIGHT, padx=(0, 5))

        # 3) Sección Inferior: Frases Extraídas y Frases Objetivo
        bottom_frame = ttk.Frame(self.text_area_frame)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(5, 5))
        bottom_frame.columnconfigure(0, weight=2)
        bottom_frame.columnconfigure(1, weight=1)

        # Frases Extraídas
        self.extracted_frame = ttk.LabelFrame(bottom_frame, text="Frases Extraídas", padding="10")
        self.extracted_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.extracted_canvas = tk.Canvas(self.extracted_frame)
        self.extracted_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll = ttk.Scrollbar(self.extracted_frame, orient="vertical", command=self.extracted_canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.extracted_canvas.configure(yscrollcommand=v_scroll.set)
        self.extracted_inner_frame = ttk.Frame(self.extracted_canvas)
        self.extracted_canvas.create_window((0, 0), window=self.extracted_inner_frame, anchor="nw")
        self.extracted_inner_frame.bind("<Configure>", lambda e: self.extracted_canvas.configure(scrollregion=self.extracted_canvas.bbox("all")))
        self.extracted_placeholder = ttk.Label(self.extracted_inner_frame, text="No hay frases extraídas todavía.")
        self.extracted_placeholder.pack(anchor="w", padx=2, pady=2)

        # Frases Objetivo (Listbox)
        self.target_frame = ttk.LabelFrame(bottom_frame, text="Frases Objetivo", padding="10")
        self.target_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.target_listbox = tk.Listbox(self.target_frame)
        # Increase font size for target word list
        self.target_listbox.configure(font=("TkDefaultFont", 14))
        self.target_listbox.pack(fill=tk.BOTH, expand=True)

    def show_progress(self):
        """Show progress bar during API calls."""
        self.progress_bar.grid()
        self.progress_bar.start(10)

    def hide_progress(self):
        """Hide progress bar after API calls."""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()

    def copy_description(self):
        """Copy the generated description to clipboard."""
        description = self.description_text.get("1.0", tk.END).strip()
        if description:
            self.clipboard_clear()
            self.clipboard_append(description)
            self.update_status("Descripción copiada al portapapeles")

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks()  # Force UI update
    
    def update_stats(self):
        """Update session statistics display."""
        image_count = len(self.used_image_urls)
        word_count = len(self.vocabulary_cache) + len(self.target_phrases)
        self.stats_label.config(text=f"Images: {image_count} | Words: {word_count}")
        self.update_idletasks()

    def disable_buttons(self):
        self.search_button.config(state=tk.DISABLED)
        self.another_button.config(state=tk.DISABLED)
        self.newsearch_button.config(state=tk.DISABLED)
        self.generate_desc_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.search_button.config(state=tk.NORMAL)
        self.another_button.config(state=tk.NORMAL)
        self.newsearch_button.config(state=tk.NORMAL)
        self.generate_desc_button.config(state=tk.NORMAL)

    # ─── LÓGICA DE BÚSQUEDA DE IMÁGENES Y PAGINACIÓN ─────────────────────────────
    def fetch_images_page(self, query, page):
        """Obtiene una página de resultados desde Unsplash para la consulta dada."""
        headers = {"Authorization": f"Client-ID {self.UNSPLASH_ACCESS_KEY}"}
        url = f"https://api.unsplash.com/search/photos?query={query}&page={page}&per_page=10"
        
        def make_request():
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        
        data = self.api_call_with_retry(make_request)
        return data.get("results", [])

    def get_next_image(self):
        """
        Retorna la siguiente imagen nueva para la consulta actual, evitando duplicados.
        Si se acaba la página actual, pasa a la siguiente.
        """
        while True:
            if self.current_index >= len(self.current_results):
                self.current_page += 1
                try:
                    new_results = self.fetch_images_page(self.current_query, self.current_page)
                except Exception as e:
                    error_msg = str(e)
                    if "403" in error_msg:
                        messagebox.showerror("API Error", "Unsplash API key may be invalid. Please check your configuration.")
                    elif "rate" in error_msg.lower() or "429" in error_msg:
                        # Calculate time until reset (Unsplash resets hourly)
                        from datetime import datetime, timedelta
                        next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0)
                        minutes_left = int((next_hour - datetime.now()).seconds / 60)
                        messagebox.showwarning("Rate Limit", f"Unsplash rate limit reached (50/hour).\n\nTry again in {minutes_left} minutes.")
                    else:
                        messagebox.showerror("Error", f"Error al buscar imágenes:\n{e}")
                    return None

                if not new_results:
                    messagebox.showinfo("Sin más imágenes", f"No se encontraron más imágenes nuevas para '{self.current_query}'.")
                    return None

                self.current_results = new_results
                self.current_index = 0

            candidate = self.current_results[self.current_index]
            self.current_index += 1
            candidate_url = candidate["urls"]["regular"]
            canonical_url = self.canonicalize_url(candidate_url)
            if canonical_url not in self.used_image_urls:
                try:
                    # Check cache first
                    if canonical_url in self.image_cache:
                        img_data = self.image_cache[canonical_url]
                    else:
                        def download_image():
                            img_response = requests.get(candidate_url, timeout=15)
                            img_response.raise_for_status()
                            return img_response.content
                        
                        img_data = self.api_call_with_retry(download_image)
                        # Cache the image (keep last 10)
                        if len(self.image_cache) > 10:
                            # Remove oldest entry
                            self.image_cache.pop(next(iter(self.image_cache)))
                        self.image_cache[canonical_url] = img_data
                    
                    image = Image.open(BytesIO(img_data))
                    image.thumbnail((600, 600))
                    photo = ImageTk.PhotoImage(image)
                    
                    self.used_image_urls.add(canonical_url)
                    self.current_image_url = candidate_url
                    self.update_stats()  # Update image count
                    self.log_entries.append({
                        "timestamp": datetime.now().isoformat(),
                        "query": self.current_query,
                        "image_url": candidate_url,
                        "user_note": "",
                        "generated_description": ""
                    })
                    return photo
                except Exception as e:
                    print(f"Error downloading image: {e}")
                    continue

    def search_image(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Por favor ingresa una consulta de búsqueda.")
            return
        self.current_query = query
        self.current_page = 1
        self.current_index = 0
        self.save_last_search()  # Remember this search
        
        self.update_status(f"Buscando '{query}' en Unsplash...")
        self.show_progress()
        self.disable_buttons()
        
        threading.Thread(target=self.thread_search_images, args=(query,), daemon=True).start()

    def thread_search_images(self, query):
        try:
            self.current_results = self.fetch_images_page(query, self.current_page)
            
            if not self.current_results:
                self.after(0, lambda: messagebox.showinfo("Sin Resultados", f"No se encontraron imágenes para '{query}'."))
                self.after(0, self.hide_progress)
                self.after(0, self.enable_buttons)
                return
            
            photo = self.get_next_image()
            if photo:
                self.after(0, lambda: self.display_image(photo))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Error al buscar imágenes:\n{e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)

    def thread_get_next_image(self):
        try:
            photo = self.get_next_image()
            if photo:
                self.after(0, lambda: self.display_image(photo))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)

    def another_image(self):
        if not self.current_query:
            messagebox.showerror("Error", "Por favor ingresa una consulta antes.")
            return
        self.update_status("Buscando otra imagen...")
        self.show_progress()
        self.disable_buttons()
        threading.Thread(target=self.thread_get_next_image, daemon=True).start()

    def display_image(self, photo):
        self.image_label.config(image=photo)
        self.image_label.image = photo
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.DISABLED)
        self.update_status("Imagen cargada.")
        self.enable_buttons()

    def change_search(self):
        self.search_entry.delete(0, tk.END)
        self.image_label.config(image="")
        self.image_label.image = None
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.DISABLED)
        self.update_status("Lista para nueva búsqueda.")
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0
        self.current_image_url = None
        
        # Clear extracted phrases
        for widget in self.extracted_inner_frame.winfo_children():
            widget.destroy()
        self.extracted_placeholder = ttk.Label(self.extracted_inner_frame, text="No hay frases extraídas todavía.")
        self.extracted_placeholder.pack(anchor="w", padx=2, pady=2)

    # ─── LÓGICA DE DESCRIPCIÓN GPT ─────────────────────────────
    def generate_description(self):
        query = self.search_entry.get().strip()
        user_note = self.note_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showerror("Error", "Por favor ingresa una consulta de búsqueda.")
            return
        if not getattr(self.image_label, "image", None):
            messagebox.showerror("Error", "No hay imagen cargada. Por favor busca una imagen primero.")
            return

        self.update_status(f"Analizando imagen con {self.GPT_MODEL}...")
        self.show_progress()
        self.disable_buttons()
        threading.Thread(target=self.thread_generate_description, args=(query, user_note), daemon=True).start()

    def thread_generate_description(self, query, user_note):
        try:
            image_url = self.current_image_url
            if not image_url:
                self.after(0, lambda: messagebox.showerror("Error", "No se encontró la URL de la imagen."))
                return
            
            # Debug: Verify we have a valid Unsplash URL
            if not image_url.startswith('https://images.unsplash.com/'):
                print(f"Warning: Unexpected image URL format: {image_url}")
            
            print(f"Sending image to GPT-4 Vision: {image_url[:50]}...")

            # Better prompt that ensures GPT analyzes the actual image
            text_prompt = """Analiza la imagen que te estoy mostrando y descríbela en español latinoamericano.
            
IMPORTANTE: Describe SOLO lo que ves en esta imagen específica:
- ¿Qué objetos, personas o animales aparecen?
- ¿Cuáles son los colores predominantes?
- ¿Qué está sucediendo en la escena?
- ¿Dónde parece estar ubicada (interior/exterior)?
- ¿Qué detalles destacan?

Escribe 1-2 párrafos descriptivos y naturales."""
            
            if user_note:
                text_prompt += f"\n\nContexto adicional del usuario: {user_note}"

            # Use new OpenAI client syntax
            def make_gpt_call():
                response = self.openai_client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": text_prompt},
                                {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
                            ]
                        }
                    ],
                    max_tokens=600,
                    temperature=0.7,
                )
                return response.choices[0].message.content.strip()
            
            generated_text = self.api_call_with_retry(make_gpt_call)
            self.after(0, lambda: self.display_description(generated_text))
            
            # Update log entry
            for entry in reversed(self.log_entries):
                if entry["image_url"] == image_url and entry["generated_description"] == "":
                    entry["user_note"] = user_note
                    entry["generated_description"] = generated_text
                    break
            
            # Extract phrases in background
            threading.Thread(target=self.extract_phrases_from_description, args=(generated_text,), daemon=True).start()
            
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                self.after(0, lambda: messagebox.showerror("API Error", "OpenAI API key may be invalid. Please check your configuration."))
            elif "rate_limit" in error_msg.lower():
                self.after(0, lambda: messagebox.showerror("Rate Limit", "OpenAI rate limit reached. Please wait a moment."))
            elif "insufficient_quota" in error_msg.lower():
                self.after(0, lambda: messagebox.showerror("Quota Error", "OpenAI API quota exceeded. Please check your account."))
            else:
                self.after(0, lambda: messagebox.showerror("Error", f"Error de la API GPT:\n{e}"))
        finally:
            self.after(0, self.hide_progress)
            self.after(0, self.enable_buttons)

    def display_description(self, text):
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, text)
        self.description_text.config(state=tk.DISABLED)
        self.copy_desc_button.config(state=tk.NORMAL)
        self.update_status("Descripción generada.")
        self.enable_buttons()

    # ─── EXTRACCIÓN DE FRASES (GPT) ─────────────────────────────
    def extract_phrases_from_description(self, description):
        def remove_trailing_commas(json_str):
            return re.sub(r",\s*([\]\}])", r"\1", json_str)

        system_msg = (
            "You are a helpful assistant that returns only valid JSON. "
            "No disclaimers, no code fences, no extra text. If you have no data, return '{}'."
        )
        user_msg = f"""Del siguiente texto en español, extrae vocabulario útil para aprender el idioma.
        
TEXTO: {description}

Devuelve un JSON con estas categorías (pueden estar vacías si no hay ejemplos):
- "Sustantivos": incluye el artículo (el/la), máximo 10
- "Verbos": forma conjugada encontrada, máximo 10
- "Adjetivos": con concordancia de género si aplica, máximo 10
- "Adverbios": solo los más relevantes, máximo 5
- "Frases clave": expresiones de 2-4 palabras que sean útiles, máximo 10

Evita palabras muy comunes como: el, la, de, que, y, a, en, es, son
Solo devuelve el JSON, sin comentarios adicionales."""
        
        try:
            def make_extraction_call():
                response = self.openai_client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ],
                    max_tokens=600,
                    temperature=0.3,
                    response_format={"type": "json_object"}  # Force JSON response
                )
                return response.choices[0].message.content.strip()
            
            raw_str = self.api_call_with_retry(make_extraction_call)
            print("DEBUG GPT OUTPUT:\n", raw_str)
            
            # Parse JSON response
            groups = json.loads(raw_str)
            
            # Ensure all expected keys exist
            expected_keys = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
            for key in expected_keys:
                if key not in groups:
                    groups[key] = []
            
            self.after(0, lambda: self.display_extracted_phrases(groups))
            
        except json.JSONDecodeError as je:
            print(f"JSON decode error: {je}")
            # Try to recover with empty groups
            self.after(0, lambda: self.display_extracted_phrases({}))
        except Exception as e:
            print(f"Error extracting phrases: {e}")
            self.after(0, lambda: self.display_extracted_phrases({}))

    def display_extracted_phrases(self, groups):
        """
        Muestra las frases extraídas, agrupadas por categoría, con cada grupo ordenado alfabéticamente
        ignorando los artículos iniciales ("el", "la", "los", "las") al ordenar.
        """
        self.extracted_phrases = groups

        # Limpia los widgets anteriores
        for widget in self.extracted_inner_frame.winfo_children():
            widget.destroy()

        if not groups or all(not phrases for phrases in groups.values()):
            placeholder = ttk.Label(self.extracted_inner_frame, text="No se pudieron extraer frases.")
            placeholder.pack(anchor="w", padx=2, pady=2)
            return

        # Función auxiliar para ordenar ignorando artículos
        def sort_ignoring_articles(phrase):
            words = phrase.lower().split()
            if words and words[0] in ["el", "la", "los", "las"]:
                return " ".join(words[1:])
            return phrase.lower()

        max_columns = 3

        for category, phrases in groups.items():
            if phrases:
                # Ordena usando la función auxiliar
                sorted_phrases = sorted(phrases, key=sort_ignoring_articles)

                cat_label = ttk.Label(
                    self.extracted_inner_frame,
                    text=f"{category}:",
                    font=('TkDefaultFont', 10, 'bold')
                )
                cat_label.pack(anchor="w", padx=2, pady=(5, 0))

                btn_frame = ttk.Frame(self.extracted_inner_frame)
                btn_frame.pack(fill="x", padx=5)

                col = 0
                row = 0
                for phrase in sorted_phrases:
                    btn = tk.Button(
                        btn_frame, text=phrase, relief=tk.FLAT, fg="blue", cursor="hand2",
                        command=lambda p=phrase: self.add_target_phrase(p)
                    )
                    btn.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                    col += 1
                    if col >= max_columns:
                        col = 0
                        row += 1

    # ─── TRADUCCIÓN Y ADICIÓN DE FRASES OBJETIVO ─────────────────────────────
    def translate_word(self, word, context=""):
        """
        Traduce la palabra (en español) al inglés de EE.UU., usando el contexto si se proporciona.
        """
        if context:
            prompt = (
                f"Translate the Latin American Spanish word '{word}' into US English "
                f"as used in the following sentence:\n\n{context}\n\nProvide only the translation."
            )
        else:
            prompt = f"Translate the Latin American Spanish word '{word}' into US English without additional text."
        
        try:
            def make_translation_call():
                response = self.openai_client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=20,
                    temperature=0.0,
                )
                return response.choices[0].message.content.strip()
            
            translation = self.api_call_with_retry(make_translation_call, max_retries=2)
            return translation
        except Exception as e:
            print(f"Error de traducción para '{word}': {e}")
            return ""

    def add_target_phrase(self, phrase):
        # Evita duplicados comparando la palabra base (antes del guión).
        if any(phrase == tp.split(" - ")[0] for tp in self.target_phrases):
            return
        
        # Check if already in vocabulary cache
        if phrase in self.vocabulary_cache:
            self.update_status(f"'{phrase}' ya está en tu vocabulario")
            return
        
        self.update_status(f"Traduciendo '{phrase}'...")
        context = self.description_text.get("1.0", tk.END).strip()
        translation = self.translate_word(phrase, context)
        combined = f"{phrase} - {translation}" if translation else phrase
        self.target_phrases.append(combined)
        self.update_target_list_display()

        # Registra en CSV with additional metadata
        if translation:
            # Include search query and image URL for better context
            self.log_target_word_csv(phrase, translation, self.current_query, self.current_image_url, context[:100])
            self.vocabulary_cache.add(phrase)
        
        self.update_status("Frase añadida al vocabulario")
        self.update_stats()  # Update word count

    def log_target_word_csv(self, spanish_phrase, english_translation, search_query, image_url, context=""):
        """Registra la palabra objetivo con contexto completo en CSV."""
        try:
            # Check if file exists and has headers
            file_exists = self.CSV_TARGET_WORDS.exists()
            
            with open(self.CSV_TARGET_WORDS, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers if file is new or empty
                if not file_exists or os.path.getsize(self.CSV_TARGET_WORDS) == 0:
                    writer.writerow(['Spanish', 'English', 'Date', 'Search Query', 'Image URL', 'Context'])
                
                # Write the data with full context
                writer.writerow([
                    spanish_phrase,
                    english_translation,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    search_query if search_query else "",
                    image_url[:100] if image_url else "",  # Truncate long URLs
                    context[:100] if context else ""
                ])
        except Exception as e:
            print(f"Error al escribir en el CSV: {e}")

    def update_target_list_display(self):
        self.target_listbox.delete(0, tk.END)
        for phrase in self.target_phrases:
            self.target_listbox.insert(tk.END, phrase)
    
    def export_vocabulary(self):
        """Export vocabulary in different formats."""
        if not self.CSV_TARGET_WORDS.exists() or os.path.getsize(self.CSV_TARGET_WORDS) == 0:
            messagebox.showinfo("No Data", "No vocabulary to export yet!")
            return
        
        # Create export dialog
        export_window = tk.Toplevel(self)
        export_window.title("Export Vocabulary")
        export_window.geometry("400x300")
        export_window.transient(self)
        export_window.grab_set()
        
        # Center window
        export_window.update_idletasks()
        x = (export_window.winfo_screenwidth() // 2) - 200
        y = (export_window.winfo_screenheight() // 2) - 150
        export_window.geometry(f"+{x}+{y}")
        
        # Export options
        frame = ttk.Frame(export_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Export Format:", font=('TkDefaultFont', 10, 'bold')).pack(pady=(0, 10))
        
        # Anki export
        def export_anki():
            try:
                anki_file = self.DATA_DIR / f"anki_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f_in:
                    reader = csv.DictReader(f_in)
                    with open(anki_file, 'w', encoding='utf-8') as f_out:
                        for row in reader:
                            if 'Spanish' in row and 'English' in row:
                                # Anki format: front[tab]back
                                spanish = row['Spanish']
                                english = row['English']
                                context = row.get('Context', '')[:50]
                                f_out.write(f"{spanish}\t{english} | {context}\n")
                
                messagebox.showinfo("Success", f"Exported to:\n{anki_file}\n\nImport this file into Anki using 'Import File'")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
        
        ttk.Button(frame, text="📚 Anki (Tab-delimited)", command=export_anki, width=30).pack(pady=5)
        
        # Simple text export
        def export_text():
            try:
                text_file = self.DATA_DIR / f"vocabulary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f_in:
                    reader = csv.DictReader(f_in)
                    with open(text_file, 'w', encoding='utf-8') as f_out:
                        f_out.write("VOCABULARY LIST\n")
                        f_out.write("=" * 50 + "\n\n")
                        for row in reader:
                            if 'Spanish' in row and 'English' in row:
                                f_out.write(f"{row['Spanish']} = {row['English']}\n")
                                if row.get('Search Query'):
                                    f_out.write(f"  (from: {row['Search Query']})\n")
                                f_out.write("\n")
                
                messagebox.showinfo("Success", f"Exported to:\n{text_file}")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
        
        ttk.Button(frame, text="📝 Plain Text", command=export_text, width=30).pack(pady=5)
        
        # Open CSV directly
        def open_csv():
            try:
                if sys.platform == "win32":
                    os.startfile(self.CSV_TARGET_WORDS)
                elif sys.platform == "darwin":
                    os.system(f"open {self.CSV_TARGET_WORDS}")
                else:
                    os.system(f"xdg-open {self.CSV_TARGET_WORDS}")
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        
        ttk.Button(frame, text="📊 Open CSV in Excel", command=open_csv, width=30).pack(pady=5)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=20)
        
        # Stats
        try:
            with open(self.CSV_TARGET_WORDS, 'r', encoding='utf-8') as f:
                word_count = sum(1 for line in csv.DictReader(f))
            ttk.Label(frame, text=f"Total vocabulary: {word_count} words").pack()
        except:
            pass
        
        ttk.Button(frame, text="Close", command=export_window.destroy).pack(pady=10)

    # ─── SALIDA Y REGISTRO ─────────────────────────────
    def save_session_to_json(self):
        """Save session data in JSON format for better structure."""
        try:
            # Load existing data or create new structure
            if self.LOG_FILENAME.exists():
                try:
                    with open(self.LOG_FILENAME, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, Exception):
                    data = {"sessions": []}
            else:
                data = {"sessions": []}
            
            # Add current session
            if self.log_entries:
                session = {
                    "session_start": self.log_entries[0].get("timestamp", datetime.now().isoformat()),
                    "session_end": datetime.now().isoformat(),
                    "entries": self.log_entries,
                    "vocabulary_learned": len(self.target_phrases),
                    "target_phrases": self.target_phrases
                }
                data["sessions"].append(session)
            
            # Save to file
            with open(self.LOG_FILENAME, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving session to JSON: {e}")
            # Fallback to text format
            self.save_session_to_text()

    def save_session_to_text(self):
        """Fallback text format for backwards compatibility."""
        try:
            with open(self.LOG_FILENAME.with_suffix('.txt'), "a", encoding="utf-8") as f:
                f.write("\n=== Informe de Sesión ===\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                for i, entry in enumerate(self.log_entries, start=1):
                    f.write(f"\nEntrada {i}:\n")
                    f.write(f"  Consulta de la Búsqueda: {entry.get('query', '')}\n")
                    f.write(f"  URL de la Imagen     : {entry.get('image_url', '')}\n")
                    f.write(f"  Notas del Usuario    : {entry.get('user_note', '')}\n")
                    f.write(f"  Descripción Generada : {entry.get('generated_description', '')}\n")
                    f.write("-" * 40 + "\n")
                if self.target_phrases:
                    f.write("Target Phrases: " + ", ".join(self.target_phrases) + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al escribir el archivo de sesión:\n{e}")

    def on_exit(self):
        """Save session data before closing."""
        self.save_session_to_json()
        self.destroy()


def main():
    """Main entry point for the application."""
    try:
        app = ImageSearchApp()
        if app.config_manager:  # Only run if configuration was successful
            app.mainloop()
    except Exception as e:
        # Show error in a message box if GUI fails to start
        import traceback
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Error",
            f"Failed to start application:\n\n{str(e)}\n\nPlease check your configuration and try again."
        )
        traceback.print_exc()
        root.destroy()


if __name__ == "__main__":
    main()