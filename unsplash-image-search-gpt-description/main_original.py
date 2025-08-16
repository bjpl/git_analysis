import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
from io import BytesIO
import threading
import openai
import os
import sys
import json
import re
import csv

# ─── CONFIGURATION ─────────────────────────────────────────────
UNSPLASH_ACCESS_KEY = "DPM5yTFbvoZW0imPQWe5pAXAxbEMhhBZE1GllByUPzY"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

CSV_TARGET_WORDS = r"C:\Users\brand\Development\Project_Workspace\unsplash-image-search-gpt-description\target_word_list.csv"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILENAME = os.path.join(BASE_DIR, "session_log.txt")


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
        self.title("Búsqueda de Imágenes en Unsplash & Descripción GPT")
        self.geometry("1100x800")
        self.resizable(True, True)

        self.log_entries = []
        self.extracted_phrases = {}
        self.target_phrases = []
        self.used_image_urls = set()

        # Estado de paginación
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0

        self.load_used_image_urls_from_log()

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def canonicalize_url(self, url):
        """Retorna la URL base sin parámetros de consulta."""
        return url.split('?')[0]

    def load_used_image_urls_from_log(self):
        """Carga URLs de imagen usadas (en forma canónica) desde el archivo de sesión."""
        if os.path.exists(LOG_FILENAME):
            try:
                with open(LOG_FILENAME, "r", encoding="utf-8") as f:
                    for line in f:
                        if "URL de la Imagen" in line:
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                url = parts[1].strip()
                                if url:
                                    self.used_image_urls.add(self.canonicalize_url(url))
            except Exception as e:
                messagebox.showerror("Error", f"Error al leer el archivo de sesión:\n{e}")

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
        self.search_button = ttk.Button(search_frame, text="Buscar Imagen", command=self.search_image)
        self.search_button.grid(row=0, column=2, padx=5)
        self.another_button = ttk.Button(search_frame, text="Otra Imagen", command=self.another_image)
        self.another_button.grid(row=1, column=0, padx=5, pady=(5, 0), sticky=tk.W)
        self.newsearch_button = ttk.Button(search_frame, text="Nueva Búsqueda", command=self.change_search)
        self.newsearch_button.grid(row=1, column=1, padx=5, pady=(5, 0), sticky=tk.W)

        # BARRA DE ESTADO
        self.status_label = ttk.Label(main_frame, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(5, 10))

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
        self.generate_desc_button = ttk.Button(desc_frame, text="Generar Descripción", command=self.generate_description)
        self.generate_desc_button.grid(row=1, column=0, sticky="e", pady=(5, 0))

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

    def update_status(self, message):
        self.status_label.config(text=message)

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
        headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
        url = f"https://api.unsplash.com/search/photos?query={query}&page={page}&per_page=10"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
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
                    img_response = requests.get(candidate_url)
                    img_response.raise_for_status()
                    img_data = img_response.content
                    image = Image.open(BytesIO(img_data))
                    image.thumbnail((600, 600))
                    photo = ImageTk.PhotoImage(image)
                    self.used_image_urls.add(canonical_url)
                    self.log_entries.append({
                        "query": self.current_query,
                        "image_url": candidate_url,
                        "user_note": "",
                        "generated_description": ""
                    })
                    return photo
                except Exception as e:
                    messagebox.showerror("Error", f"Error al descargar la imagen:\n{e}")
                    continue

    def search_image(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Por favor ingresa una consulta de búsqueda.")
            return
        self.current_query = query
        self.current_page = 1
        self.current_index = 0
        try:
            self.current_results = self.fetch_images_page(query, self.current_page)
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar imágenes:\n{e}")
            return

        if not self.current_results:
            messagebox.showinfo("Sin Resultados", f"No se encontraron imágenes para '{query}'.")
            return

        self.update_status("Buscando imagen...")
        self.disable_buttons()
        threading.Thread(target=self.thread_get_next_image, daemon=True).start()

    def thread_get_next_image(self):
        photo = self.get_next_image()
        if photo:
            self.after(0, lambda: self.display_image(photo))
        else:
            self.after(0, self.enable_buttons)

    def another_image(self):
        if not self.current_query:
            messagebox.showerror("Error", "Por favor ingresa una consulta antes.")
            return
        self.update_status("Buscando otra imagen...")
        self.disable_buttons()
        threading.Thread(target=self.thread_get_next_image, daemon=True).start()

    def display_image(self, photo):
        self.image_label.config(image=photo)
        self.image_label.image = photo
        self.note_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)
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
        self.update_status("Lista para nueva búsqueda.")
        self.current_query = ""
        self.current_page = 0
        self.current_results = []
        self.current_index = 0

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

        self.update_status("Generando descripción...")
        self.disable_buttons()
        threading.Thread(target=self.thread_generate_description, args=(query, user_note), daemon=True).start()

    def thread_generate_description(self, query, user_note):
        image_url = None
        for entry in reversed(self.log_entries):
            if entry["query"] == query and entry["generated_description"] == "":
                image_url = entry["image_url"]
                break
        if not image_url:
            self.after(0, lambda: messagebox.showerror("Error", "No se encontró la URL de la imagen."))
            return

        text_prompt = "Por favor, describe en detalle la imagen en español latinoamericano natural y clara en 1 o 2 párrafos."
        if user_note:
            text_prompt += f" Nota del usuario: {user_note}."

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
                ]
            }
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.7,
            )
            generated_text = response.choices[0].message.content.strip()
            self.after(0, lambda: self.display_description(generated_text))
            for entry in reversed(self.log_entries):
                if entry["query"] == query and entry["generated_description"] == "":
                    entry["user_note"] = user_note
                    entry["generated_description"] = generated_text
                    break
            threading.Thread(target=self.extract_phrases_from_description, args=(generated_text,), daemon=True).start()
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Error de la API GPT:\n{e}"))
            self.after(0, self.enable_buttons)

    def display_description(self, text):
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, text)
        self.description_text.config(state=tk.DISABLED)
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
        user_msg = (
            "Extrae todos los sustantivos, asegurándote de incluir el artículo definido ('el' o 'la') para cada sustantivo, "
            "así como todos los verbos (conjugados e infinitivo), adjetivos (con género), adverbios y frases clave de la siguiente descripción. "
            "Devuelve un objeto JSON con las claves 'Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios' y 'Frases clave'. "
            "Cada lista debe estar ordenada alfabéticamente, sin duplicados. "
            "Devuelve únicamente el JSON. Sin comentarios.\n\n" + description
        )
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.3,
            )
            raw_str = response.choices[0].message.content.strip()
            print("DEBUG GPT OUTPUT:\n", raw_str)
            start_idx = raw_str.find('{')
            end_idx = raw_str.rfind('}')
            if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
                raise ValueError("No valid JSON object found en la respuesta de GPT.")
            json_str = raw_str[start_idx:end_idx+1]
            json_str = remove_trailing_commas(json_str)
            groups = json.loads(json_str)
            self.after(0, lambda: self.display_extracted_phrases(groups))
        except json.JSONDecodeError as je:
            self.after(0, lambda: messagebox.showerror("Error", f"Error de JSON:\n{je}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Error al extraer frases:\n{e}"))

    def display_extracted_phrases(self, groups):
        """
        Muestra las frases extraídas, agrupadas por categoría, con cada grupo ordenado alfabéticamente
        ignorando los artículos iniciales ("el", "la", "los", "las") al ordenar.
        """
        self.extracted_phrases = groups

        # Limpia los widgets anteriores
        for widget in self.extracted_inner_frame.winfo_children():
            widget.destroy()

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
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.0,
            )
            translation = response.choices[0].message.content.strip()
            return translation
        except Exception as e:
            print(f"Error de traducción para '{word}': {e}")
            return ""

    def add_target_phrase(self, phrase):
        # Evita duplicados comparando la palabra base (antes del guión).
        if any(phrase == tp.split(" - ")[0] for tp in self.target_phrases):
            return
        context = self.description_text.get("1.0", tk.END).strip()
        translation = self.translate_word(phrase, context)
        combined = f"{phrase} - {translation}" if translation else phrase
        self.target_phrases.append(combined)
        self.update_target_list_display()

        # Registra en CSV
        if translation:
            self.log_target_word_csv(phrase, translation)

    def log_target_word_csv(self, spanish_phrase, english_translation):
        """Registra la palabra objetivo (ES, EN) en un archivo CSV."""
        try:
            with open(CSV_TARGET_WORDS, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([spanish_phrase, english_translation])
        except Exception as e:
            print(f"Error al escribir en el CSV: {e}")

    def update_target_list_display(self):
        self.target_listbox.delete(0, tk.END)
        for phrase in self.target_phrases:
            self.target_listbox.insert(tk.END, phrase)

    # ─── SALIDA Y REGISTRO ─────────────────────────────
    def on_exit(self):
        try:
            with open(LOG_FILENAME, "a", encoding="utf-8") as f:
                f.write("\n=== Informe de Sesión ===\n")
                for i, entry in enumerate(self.log_entries, start=1):
                    f.write(f"\nEntrada {i}:\n")
                    f.write(f"  Consulta de la Búsqueda: {entry['query']}\n")
                    f.write(f"  URL de la Imagen     : {entry['image_url']}\n")
                    f.write(f"  Notas del Usuario    : {entry['user_note']}\n")
                    f.write(f"  Descripción Generada : {entry['generated_description']}\n")
                    f.write("-" * 40 + "\n")
                if self.target_phrases:
                    f.write("Target Phrases: " + ", ".join(self.target_phrases) + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al escribir el archivo de sesión:\n{e}")
        self.destroy()


if __name__ == "__main__":
    app = ImageSearchApp()
    app.mainloop()
