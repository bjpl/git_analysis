# -*- coding: utf-8 -*-
import sys
import os
import datetime
import logging
import random
import base64
from dotenv import load_dotenv

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QTextEdit, QHBoxLayout, QVBoxLayout, QStatusBar, QMessageBox, QSplitter
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import osmnx as ox
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

import openai

# Ensure Python always uses UTF-8 for I/O
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Load environment variables from .env file
if not load_dotenv():
    logging.warning("⚠️ WARNING: .env file not found. Ensure the API key is properly set.")

# Get the API key from the .env file
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("ERROR: OpenAI API key not found. Make sure it's set in the .env file.")

# Initialize OpenAI client
openai.api_key = openai_api_key

# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# Map Generation Function
# -----------------------------
def generate_map_image(search_area, variant=False):
    """
    Generates a map image for the given search area using OSMNx and Matplotlib.
    If variant=True, randomizes some styling (e.g., marker color).
    Returns the file path of the saved image, or None if an error occurs.
    """
    try:
        # Fetch the drivable street network.
        G = ox.graph_from_place(search_area, network_type="drive")
        nodes, edges = ox.graph_to_gdfs(G)

        # Define POI tags.
        tags = {
            "amenity": ["restaurant", "cafe", "bar", "fast_food"],
            "shop": True
        }
        pois = ox.geometries_from_place(search_area, tags)
        pois = pois[pois.geometry.type == "Point"]

        # For variant maps, choose a random marker color.
        poi_color = random.choice(["red", "blue", "green"]) if variant else "red"

        # Create and plot the map.
        fig, ax = plt.subplots(figsize=(10, 10))
        ox.plot_graph(
            G, ax=ax, node_size=0, edge_color="#444444",
            show=False, close=False
        )
        if not pois.empty:
            pois.plot(ax=ax, color=poi_color, markersize=30, label="POI")

        ax.legend()
        ax.set_title(f"Mapa de {search_area}", fontsize=16)
        plt.tight_layout()

        # Save the map image with a timestamp.
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"map_{timestamp}.png"
        plt.savefig(filename, dpi=300)
        plt.close(fig)

        logging.info(f"Mapa generado para '{search_area}' guardado como {filename}")
        return filename
    except Exception as e:
        logging.error(f"Error generando el mapa para '{search_area}': {e}")
        return None

# -----------------------------
# Description Generation Function with Vision
# -----------------------------
def generate_description(image_path, user_description):
    """
    Generates a detailed description of the map image using GPT-4o-mini with vision capabilities.
    The function reads the image, encodes it in Base64, and sends it along with a text prompt.
    """
    try:
        # Encode the image file in Base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Construct the messages with properly encoded text
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"El usuario proporcionó la siguiente descripción previa: \"{user_description}\". "
                            "Ahora, analiza visualmente la siguiente imagen de un mapa y proporciona "
                            "una descripción detallada en español latinoamericano, resaltando la ubicación "
                            "de negocios, calles y puntos de interés."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )

        description = response["choices"][0]["message"]["content"].strip()
        logging.info(f"Descripción generada para {os.path.basename(image_path)} usando GPT-4o-mini")
        return description

    except Exception as e:
        logging.error(f"Error generando la descripción con GPT-4o-mini: {e}")
        return "Error al generar la descripción."

# -----------------------------
# Worker Thread for Map Generation
# -----------------------------
from PyQt5.QtCore import QThread, pyqtSignal

class MapGenerationThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, search_area, variant=False):
        super().__init__()
        self.search_area = search_area
        self.variant = variant

    def run(self):
        result = generate_map_image(self.search_area, self.variant)
        if result:
            self.finished.emit(result)
        else:
            self.error.emit(f"No se pudo generar el mapa para el área: {self.search_area}")

# -----------------------------
# Worker Thread for Description Generation
# -----------------------------
class DescriptionGenerationThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, image_path, user_description):
        super().__init__()
        self.image_path = image_path
        self.user_description = user_description

    def run(self):
        result = generate_description(self.image_path, self.user_description)
        if result:
            self.finished.emit(result)
        else:
            self.error.emit("No se pudo generar la descripción.")

# -----------------------------
# Main Application Window
# -----------------------------
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QTextEdit, QHBoxLayout, QVBoxLayout, QStatusBar, QMessageBox, QSplitter
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Mapas y Descripciones")
        self.current_map_path = None

        # Set up a central widget with margins and spacing.
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #f9f9f9;")
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Top Panel: Search and Control Buttons ---
        top_panel = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ingrese área de búsqueda (ej. 'Mountain View, CA')")
        self.search_input.setMinimumHeight(30)
        self.search_input.setFont(QFont("Arial", 11))

        self.btn_new_search = QPushButton("Nueva Búsqueda")
        self.btn_new_search.setMinimumHeight(30)
        self.btn_new_search.setFont(QFont("Arial", 11))

        self.btn_new_map = QPushButton("Generar Nuevo Mapa")
        self.btn_new_map.setMinimumHeight(30)
        self.btn_new_map.setFont(QFont("Arial", 11))

        top_panel.addWidget(self.search_input)
        top_panel.addWidget(self.btn_new_search)
        top_panel.addWidget(self.btn_new_map)
        main_layout.addLayout(top_panel)

        # --- Main Area: Splitter for Map Display and Text Panels ---
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter, 1)

        # Left: Map Display
        self.map_label = QLabel("El mapa generado aparecerá aquí")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setStyleSheet("border: 1px solid #aaa; background-color: white;")
        main_splitter.addWidget(self.map_label)
        main_splitter.setStretchFactor(0, 3)

        # Right: Vertical Splitter for Text Areas
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)

        # Use a splitter for the two text areas.
        text_splitter = QSplitter(Qt.Vertical)
        right_layout.addWidget(text_splitter, 1)

        # Top Text Area: User Description
        self.user_text = QTextEdit()
        self.user_text.setPlaceholderText("Escriba su descripción aquí (en español latinoamericano)...")
        self.user_text.setFont(QFont("Arial", 11))
        text_splitter.addWidget(self.user_text)

        # Bottom Text Area: GPT-4o-mini Generated Description
        self.generated_text = QTextEdit()
        self.generated_text.setPlaceholderText("La descripción generada aparecerá aquí...")
        self.generated_text.setReadOnly(True)
        self.generated_text.setFont(QFont("Arial", 11))
        text_splitter.addWidget(self.generated_text)

        # Set initial splitter sizes for text areas.
        text_splitter.setSizes([200, 200])
        main_splitter.addWidget(right_widget)
        main_splitter.setStretchFactor(1, 2)

        # --- Description Generation Button ---
        self.btn_generate_desc = QPushButton("Generar Descripción")
        self.btn_generate_desc.setMinimumHeight(30)
        self.btn_generate_desc.setFont(QFont("Arial", 11))
        right_layout.addWidget(self.btn_generate_desc)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # --- Connect Signals ---
        self.btn_new_search.clicked.connect(self.handle_new_search)
        self.btn_new_map.clicked.connect(self.handle_new_map)
        self.btn_generate_desc.clicked.connect(self.handle_generate_description)

    # -----------------------------
    # Event Handlers
    # -----------------------------
    def handle_new_search(self):
        search_area = self.search_input.text().strip()
        if not search_area:
            QMessageBox.warning(self, "Entrada Inválida", "Por favor, ingrese un área de búsqueda.")
            return
        self.user_text.clear()
        self.generated_text.clear()
        self.status_bar.showMessage("Generando mapa...")
        self.disable_buttons()

        self.map_thread = MapGenerationThread(search_area, variant=False)
        self.map_thread.finished.connect(self.update_map)
        self.map_thread.error.connect(self.thread_error)
        self.map_thread.start()

    def handle_new_map(self):
        search_area = self.search_input.text().strip()
        if not search_area:
            QMessageBox.warning(self, "Entrada Inválida", "Por favor, ingrese un área de búsqueda.")
            return
        self.user_text.clear()
        self.generated_text.clear()
        self.status_bar.showMessage("Generando nuevo mapa...")
        self.disable_buttons()

        self.map_thread = MapGenerationThread(search_area, variant=True)
        self.map_thread.finished.connect(self.update_map)
        self.map_thread.error.connect(self.thread_error)
        self.map_thread.start()

    def handle_generate_description(self):
        if not self.current_map_path:
            QMessageBox.warning(self, "Mapa No Generado", "Primero genere un mapa para proceder.")
            return
        user_desc = self.user_text.toPlainText().strip()
        self.status_bar.showMessage("Generando descripción...")
        self.disable_buttons()

        self.desc_thread = DescriptionGenerationThread(self.current_map_path, user_desc)
        self.desc_thread.finished.connect(self.update_description)
        self.desc_thread.error.connect(self.thread_error)
        self.desc_thread.start()

    # -----------------------------
    # Slot Methods for Thread Completion
    # -----------------------------
    def update_map(self, image_path):
        self.current_map_path = image_path
        pixmap = QPixmap(image_path)
        self.map_label.setPixmap(pixmap.scaled(
            self.map_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.status_bar.showMessage("Mapa generado exitosamente.", 5000)
        self.enable_buttons()
        self.log_event("Map generated", f"Área: {self.search_input.text().strip()}, Archivo: {image_path}")

    def update_description(self, description):
        self.generated_text.setPlainText(description)
        self.status_bar.showMessage("Descripción generada exitosamente.", 5000)
        self.enable_buttons()
        self.log_event("Description generated", f"Mapa: {os.path.basename(self.current_map_path)}, "
                                               f"User Desc: {self.user_text.toPlainText().strip()}, "
                                               f"Generated Desc: {description}")

    def thread_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.status_bar.showMessage("Error: " + message, 5000)
        self.enable_buttons()

    def disable_buttons(self):
        self.btn_new_search.setEnabled(False)
        self.btn_new_map.setEnabled(False)
        self.btn_generate_desc.setEnabled(False)

    def enable_buttons(self):
        self.btn_new_search.setEnabled(True)
        self.btn_new_map.setEnabled(True)
        self.btn_generate_desc.setEnabled(True)

    def log_event(self, event_type, details):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {event_type} - {details}"
        logging.info(log_entry)

    def resizeEvent(self, event):
        if self.current_map_path:
            pixmap = QPixmap(self.current_map_path)
            self.map_label.setPixmap(pixmap.scaled(
                self.map_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        super().resizeEvent(event)

# -----------------------------
# Main Application Entry Point
# -----------------------------
def main():
    app = QApplication(sys.argv)
    window = MapApp()
    window.showMaximized()  # Start maximized but allow minimization/resizing
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
