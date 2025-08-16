import sys
import os
import csv
from dotenv import load_dotenv
load_dotenv()

import openai
# You can change the model name as needed; here we use the "gpt-4o" placeholder
GPT_MODEL = "gpt-4o"

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QLineEdit, QDialog, QDialogButtonBox, QPushButton,
    QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt

# ----------------------------
# LOGGING CONFIGURATION
# ----------------------------
import logging
from logging.handlers import RotatingFileHandler
import uuid

# Create a unique session ID (if desired)
SESSION_ID = str(uuid.uuid4())[:8]

# Create 'logs' directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# System log: logs general events (navigation, searches, warnings, etc.)
SYSTEM_LOG_FILE = os.path.join(LOG_DIR, "system.log")
system_logger = logging.getLogger("system_logger")
system_logger.setLevel(logging.INFO)
system_handler = RotatingFileHandler(SYSTEM_LOG_FILE, maxBytes=1_000_000, backupCount=5)
system_formatter = logging.Formatter("%(asctime)s | %(levelname)s | SYSTEM | %(message)s")
system_handler.setFormatter(system_formatter)
system_logger.addHandler(system_handler)
system_logger.propagate = False

# Session / Learning log: logs GPT-4 prompts, responses, and other learning-related content
SESSION_LOG_FILE = os.path.join(LOG_DIR, "session.log")
session_logger = logging.getLogger("session_logger")
session_logger.setLevel(logging.INFO)
session_handler = RotatingFileHandler(SESSION_LOG_FILE, maxBytes=1_000_000, backupCount=5)
session_formatter = logging.Formatter("%(asctime)s | %(levelname)s | SESSION | %(message)s")
session_handler.setFormatter(session_formatter)
session_logger.addHandler(session_handler)
session_logger.propagate = False

# Log the start of a session
system_logger.info(f"--- Application session started (ID={SESSION_ID}) ---")
session_logger.info(f"--- Learning/Session log started (ID={SESSION_ID}) ---")

# ----------------------------
# OPENAI CONFIG
# ----------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------------------
# DATA LOADER
# ----------------------------
def load_csv(file_path):
    """Load CSV file into a list of dictionaries, trying multiple encodings."""
    encodings = ["utf-8", "latin1", "cp1252"]
    for enc in encodings:
        try:
            data = []
            with open(file_path, newline="", encoding=enc) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append(row)
            return data
        except UnicodeDecodeError:
            continue
    system_logger.warning(f"File {file_path} could not be decoded with tried encodings.")
    return []

# Define the data folder path and Netflix dataset file.
DATA_PATH = os.path.join(os.path.expanduser("~"), "Development", "Shared", "Datasets", "tabular")
NETFLIX_FILE = os.path.join(DATA_PATH, "netflix_titles.csv")

# ----------------------------
# REUSABLE SEARCH BAR WIDGET
# ----------------------------
class SearchBar(QWidget):
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setClearButtonEnabled(True)
        layout.addWidget(self.line_edit)
        self.search_button = QPushButton("Search")
        layout.addWidget(self.search_button)
        self.setLayout(layout)

# ----------------------------
# MOVIE DETAIL DIALOG
# ----------------------------
class MovieDetailDialog(QDialog):
    def __init__(self, movie, parent=None):
        super().__init__(parent)
        self.movie = movie
        self.setWindowTitle(movie.get("title", "Movie Details"))
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        for key, value in self.movie.items():
            label = QLabel(f"<b>{key}:</b> {value}")
            label.setTextFormat(Qt.RichText)
            layout.addWidget(label)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        self.setLayout(layout)

# ----------------------------
# GPT-4 ACTOR INSIGHTS DIALOG
# ----------------------------
class GPT4ActorInsightsDialog(QDialog):
    """
    This dialog calls GPT-4 (using GPT_MODEL) with details about a specific actor’s filmography
    and displays GPT-4's summary and practice questions.
    """
    def __init__(self, actor_name, relevant_rows, parent=None):
        super().__init__(parent)
        self.actor_name = actor_name
        self.relevant_rows = relevant_rows
        self.setWindowTitle(f"GPT-4 Insights: {actor_name}")
        self.setup_ui()
        # Automatically call GPT-4 to get insights.
        self.call_gpt4_for_actor_insights()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.info_label = QLabel(f"<b>Exploring actor:</b> {self.actor_name}")
        self.info_label.setTextFormat(Qt.RichText)
        layout.addWidget(self.info_label)
        # Read-only text area for GPT-4's answer
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)
        # Ok/Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.resize(600, 500)

    def build_actor_prompt(self):
        """
        Build a prompt for GPT-4, summarizing the rows that reference this actor.
        """
        prompt_intro = (
            f"You are an expert film tutor. The user wants to learn about the actor '{self.actor_name}' "
            "based on the following Netflix titles. Provide interesting insights across different time "
            "periods, genres, and highlight unique aspects. Also provide a few practice or reflection "
            "questions for learning. Here are the details:\n"
        )
        prompt_body = ""
        for row in self.relevant_rows:
            prompt_body += (
                f"- Title: {row.get('title', 'N/A')}\n"
                f"  Year: {row.get('release_year', 'N/A')}\n"
                f"  Rating: {row.get('rating', 'N/A')}\n"
                f"  Genres: {row.get('listed_in', 'N/A')}\n\n"
            )
        prompt_outro = (
            "\nPlease summarize the actor’s filmography, highlight interesting patterns, "
            "and propose at least three short practice questions or reflection prompts about this data.\n"
        )
        return prompt_intro + prompt_body + prompt_outro

    def call_gpt4_for_actor_insights(self):
        """
        Calls GPT-4 using the latest API method.
        """
        prompt = self.build_actor_prompt()
        messages = [
            {"role": "system", "content": "You are a helpful film tutor."},
            {"role": "user", "content": prompt}
        ]

        # Log the GPT-4 prompt in the session logger
        session_logger.info(f"[Actor Insights] Prompt for '{self.actor_name}':\n{prompt}")

        try:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            gpt_answer = response.choices[0].message.content.strip()
            # Display answer in text area
            self.text_area.setPlainText(gpt_answer)
            # Log the response
            session_logger.info(f"[Actor Insights] GPT-4 Response for '{self.actor_name}':\n{gpt_answer}")

        except openai.RateLimitError as e:
            QMessageBox.warning(self, "GPT-4 Error", f"Rate limit exceeded: {e}")
            system_logger.error(f"GPT-4 RateLimitError: {e}")
        except openai.APIConnectionError as e:
            QMessageBox.warning(self, "GPT-4 Error", f"Connection error: {e}")
            system_logger.error(f"GPT-4 APIConnectionError: {e}")
        except openai.APIError as e:
            QMessageBox.warning(self, "GPT-4 Error", f"OpenAI API error: {e}")
            system_logger.error(f"GPT-4 APIError: {e}")
        except Exception as ex:
            QMessageBox.warning(self, "GPT-4 Error", f"Unexpected error: {ex}")
            system_logger.error(f"GPT-4 Unexpected error: {ex}")

# ----------------------------
# MOVIES PAGE
# ----------------------------
class MoviesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.all_movies = []
        self.filtered_movies = []
        self.setup_ui()
        self.load_movies()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.title_label = QLabel("Movies")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.search_bar = SearchBar("Search movies...")
        self.search_bar.search_button.clicked.connect(
            lambda: self.filter_movies(self.search_bar.line_edit.text())
        )
        self.search_bar.line_edit.returnPressed.connect(
            lambda: self.filter_movies(self.search_bar.line_edit.text())
        )
        layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.open_movie_detail)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_movies(self):
        all_data = load_csv(NETFLIX_FILE)
        if not all_data:
            self.title_label.setText("No movies data loaded.")
            system_logger.warning("No data loaded or CSV is empty for MoviesPage.")
            return
        self.all_movies = [row for row in all_data if row.get("type", "").lower() == "movie"]
        self.filtered_movies = self.all_movies
        self.populate_table(self.filtered_movies)

    def populate_table(self, movies):
        if not movies:
            self.table.setRowCount(0)
            return
        headers = list(movies[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(movies))
        for row_index, movie in enumerate(movies):
            for col_index, header in enumerate(headers):
                item = QTableWidgetItem(str(movie.get(header, "")))
                self.table.setItem(row_index, col_index, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filter_movies(self, text):
        text_lower = text.lower()
        system_logger.info(f"[MoviesPage] Filtering movies with text: '{text}'")
        self.filtered_movies = [
            movie for movie in self.all_movies
            if any(text_lower in str(value).lower() for value in movie.values())
        ]
        self.populate_table(self.filtered_movies)

    def open_movie_detail(self, row, column):
        if row < 0 or row >= len(self.filtered_movies):
            return
        movie = self.filtered_movies[row]
        system_logger.info(f"[MoviesPage] Opening detail for movie: {movie.get('title','N/A')}")
        dialog = MovieDetailDialog(movie, parent=self)
        dialog.exec()

# ----------------------------
# TV SHOWS PAGE
# ----------------------------
class TVShowsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.all_tv_shows = []
        self.filtered_tv_shows = []
        self.setup_ui()
        self.load_tv_shows()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.title_label = QLabel("TV Shows")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.search_bar = SearchBar("Search TV shows...")
        self.search_bar.search_button.clicked.connect(
            lambda: self.filter_tv_shows(self.search_bar.line_edit.text())
        )
        self.search_bar.line_edit.returnPressed.connect(
            lambda: self.filter_tv_shows(self.search_bar.line_edit.text())
        )
        layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_tv_shows(self):
        all_data = load_csv(NETFLIX_FILE)
        if not all_data:
            self.title_label.setText("No TV shows data loaded.")
            system_logger.warning("No data loaded or CSV is empty for TVShowsPage.")
            return
        self.all_tv_shows = [row for row in all_data if row.get("type", "").lower() == "tv show"]
        self.filtered_tv_shows = self.all_tv_shows
        self.populate_table(self.filtered_tv_shows)

    def populate_table(self, tv_shows):
        if not tv_shows:
            self.table.setRowCount(0)
            return
        headers = list(tv_shows[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(tv_shows))
        for row_index, tv_show in enumerate(tv_shows):
            for col_index, header in enumerate(headers):
                item = QTableWidgetItem(str(tv_show.get(header, "")))
                self.table.setItem(row_index, col_index, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filter_tv_shows(self, text):
        text_lower = text.lower()
        system_logger.info(f"[TVShowsPage] Filtering TV shows with text: '{text}'")
        self.filtered_tv_shows = [
            tv_show for tv_show in self.all_tv_shows
            if any(text_lower in str(value).lower() for value in tv_show.values())
        ]
        self.populate_table(self.filtered_tv_shows)

# ----------------------------
# ACTORS PAGE
# ----------------------------
class ActorsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.all_actors = []
        self.filtered_actors = []
        self.all_data = []  # Full dataset for GPT-4 usage
        self.setup_ui()
        self.load_actors()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.title_label = QLabel("Actors")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.search_bar = SearchBar("Search actors...")
        self.search_bar.search_button.clicked.connect(
            lambda: self.filter_actors(self.search_bar.line_edit.text())
        )
        self.search_bar.line_edit.returnPressed.connect(
            lambda: self.filter_actors(self.search_bar.line_edit.text())
        )
        layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        # Double-click to open GPT-4 insights
        self.table.cellDoubleClicked.connect(self.explore_actor)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_actors(self):
        self.all_data = load_csv(NETFLIX_FILE)
        if not self.all_data:
            self.title_label.setText("No actor data loaded.")
            system_logger.warning("No data loaded or CSV is empty for ActorsPage.")
            return
        actors_set = set()
        for row in self.all_data:
            cast_str = row.get("cast", "")
            if cast_str:
                for actor in cast_str.split(","):
                    actors_set.add(actor.strip())
        self.all_actors = [{"actor": actor} for actor in sorted(actors_set) if actor]
        self.filtered_actors = self.all_actors
        self.populate_table(self.filtered_actors)

    def populate_table(self, actors):
        if not actors:
            self.table.setRowCount(0)
            return
        headers = list(actors[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(actors))
        for row_index, actor in enumerate(actors):
            for col_index, header in enumerate(headers):
                item = QTableWidgetItem(str(actor.get(header, "")))
                self.table.setItem(row_index, col_index, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filter_actors(self, text):
        text_lower = text.lower()
        system_logger.info(f"[ActorsPage] Filtering actors with text: '{text}'")
        self.filtered_actors = [
            actor for actor in self.all_actors
            if text_lower in str(actor.get("actor", "")).lower()
        ]
        self.populate_table(self.filtered_actors)

    def explore_actor(self, row, column):
        """
        On double-click, gather all Netflix rows for the selected actor,
        then open a GPT-4–powered insights dialog.
        """
        if row < 0 or row >= len(self.filtered_actors):
            return
        actor_name = self.filtered_actors[row]["actor"]
        system_logger.info(f"[ActorsPage] Exploring actor: {actor_name}")
        relevant_rows = [item for item in self.all_data if actor_name in (item.get("cast", "") or "")]
        dialog = GPT4ActorInsightsDialog(actor_name, relevant_rows, self)
        dialog.exec()

# ----------------------------
# DIRECTORS PAGE
# ----------------------------
class DirectorsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.all_directors = []
        self.filtered_directors = []
        self.setup_ui()
        self.load_directors()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.title_label = QLabel("Directors")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.search_bar = SearchBar("Search directors...")
        self.search_bar.search_button.clicked.connect(
            lambda: self.filter_directors(self.search_bar.line_edit.text())
        )
        self.search_bar.line_edit.returnPressed.connect(
            lambda: self.filter_directors(self.search_bar.line_edit.text())
        )
        layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_directors(self):
        all_data = load_csv(NETFLIX_FILE)
        if not all_data:
            self.title_label.setText("No directors data loaded.")
            system_logger.warning("No data loaded or CSV is empty for DirectorsPage.")
            return
        directors_set = set()
        for row in all_data:
            director_str = row.get("director", "")
            if director_str:
                for director in director_str.split(","):
                    directors_set.add(director.strip())
        self.all_directors = [{"director": director} for director in sorted(directors_set) if director]
        self.filtered_directors = self.all_directors
        self.populate_table(self.filtered_directors)

    def populate_table(self, directors):
        if not directors:
            self.table.setRowCount(0)
            return
        headers = list(directors[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(directors))
        for row_index, director in enumerate(directors):
            for col_index, header in enumerate(headers):
                item = QTableWidgetItem(str(director.get(header, "")))
                self.table.setItem(row_index, col_index, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filter_directors(self, text):
        text_lower = text.lower()
        system_logger.info(f"[DirectorsPage] Filtering directors with text: '{text}'")
        self.filtered_directors = [
            director for director in self.all_directors
            if text_lower in str(director.get("director", "")).lower()
        ]
        self.populate_table(self.filtered_directors)

# ----------------------------
# INSIGHTS PAGE
# ----------------------------
class InsightsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.title_label = QLabel("Insights")
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.insights_label = QLabel("Visualizations and analytics will appear here.")
        layout.addWidget(self.insights_label)

        self.setLayout(layout)

# ----------------------------
# MAIN WINDOW
# ----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie Explorer")
        self.setMinimumSize(800, 600)
        self._setup_ui()

    def _setup_ui(self):
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        self.nav_list = QListWidget()
        self.nav_list.addItem("Movies")
        self.nav_list.addItem("TV Shows")
        self.nav_list.addItem("Actors")
        self.nav_list.addItem("Directors")
        self.nav_list.addItem("Insights")
        self.nav_list.setMaximumWidth(200)
        self.nav_list.currentRowChanged.connect(self.display_page)
        main_layout.addWidget(self.nav_list)

        self.pages = QStackedWidget()
        self.movies_page = MoviesPage()
        self.tv_shows_page = TVShowsPage()
        self.actors_page = ActorsPage()
        self.directors_page = DirectorsPage()
        self.insights_page = InsightsPage()

        self.pages.addWidget(self.movies_page)
        self.pages.addWidget(self.tv_shows_page)
        self.pages.addWidget(self.actors_page)
        self.pages.addWidget(self.directors_page)
        self.pages.addWidget(self.insights_page)

        main_layout.addWidget(self.pages)

        # Automatically select the first item (Movies) on start
        self.nav_list.setCurrentRow(0)

    def display_page(self, index):
        page_names = ["Movies", "TV Shows", "Actors", "Directors", "Insights"]
        if 0 <= index < len(page_names):
            system_logger.info(f"Navigating to page: {page_names[index]}")
        self.pages.setCurrentIndex(index)

# ----------------------------
# APPLICATION ENTRY POINT
# ----------------------------
def main():
    # Log that application is launching
    system_logger.info("Launching Movie Explorer Application.")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = app.exec()
    system_logger.info(f"Application closed with exit code {exit_code}.")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
