import sys
import os
import random
import logging
import requests
import openai
import time
from io import BytesIO
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtWidgets, QtGui, QtCore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils import (
    query_gpt_for_celebrities,
    fetch_profile,
    generate_extended_bio,
    extract_key_facts,
    generate_quiz,
    generate_image_quiz,
    review_content,
    load_image_from_url,
    save_image_for_logging,
    setup_loggers,
)

# Setup loggers
technical_logger, content_logger = setup_loggers()

# Set OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY"

class CelebrityGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Celebrity Finder")
        self.setGeometry(100, 100, 1200, 800)
        self.curated_celebrities = []
        self.current_profile = None
        self.initUI()

    def initUI(self):
        # Central widget and layout
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # Mode toggle
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Learning Mode", "Quiz Mode"])
        self.mode_combo.currentIndexChanged.connect(self.switchMode)
        main_layout.addWidget(self.mode_combo)

        # Search criteria group
        search_group = QtWidgets.QGroupBox("Search Criteria")
        search_layout = QtWidgets.QGridLayout(search_group)

        self.search_term_input = QtWidgets.QLineEdit()
        self.search_term_input.setPlaceholderText("e.g., actor, comedian, singer")
        self.characteristics_input = QtWidgets.QLineEdit()
        self.characteristics_input.setPlaceholderText("e.g., British, older than 50, award-winning")
        self.language_input = QtWidgets.QLineEdit()
        self.language_input.setPlaceholderText("Wiki Language (default: en)")
        self.limit_spinner = QtWidgets.QSpinBox()
        self.limit_spinner.setRange(1, 20)
        self.limit_spinner.setValue(5)
        search_button = QtWidgets.QPushButton("Find Celebrities")
        search_button.clicked.connect(self.findCelebrities)

        search_layout.addWidget(QtWidgets.QLabel("Search Term:"), 0, 0)
        search_layout.addWidget(self.search_term_input, 0, 1)
        search_layout.addWidget(QtWidgets.QLabel("Characteristics:"), 1, 0)
        search_layout.addWidget(self.characteristics_input, 1, 1)
        search_layout.addWidget(QtWidgets.QLabel("Language:"), 2, 0)
        search_layout.addWidget(self.language_input, 2, 1)
        search_layout.addWidget(QtWidgets.QLabel("Limit:"), 3, 0)
        search_layout.addWidget(self.limit_spinner, 3, 1)
        search_layout.addWidget(search_button, 4, 0, 1, 2)
        main_layout.addWidget(search_group)

        # Stacked widget for modes
        self.stack = QtWidgets.QStackedWidget()
        main_layout.addWidget(self.stack)

        # Page 0: Learning Mode
        self.learningPage = QtWidgets.QWidget()
        learning_layout = QtWidgets.QVBoxLayout(self.learningPage)
        learning_split = QtWidgets.QHBoxLayout()

        # Curated Celebrity List
        self.celeb_list_widget = QtWidgets.QListWidget()
        self.celeb_list_widget.setFixedWidth(300)
        self.celeb_list_widget.itemClicked.connect(self.loadSelectedCelebrity)
        left_panel = QtWidgets.QVBoxLayout()
        left_panel.addWidget(QtWidgets.QLabel("Curated Celebrity List:"))
        left_panel.addWidget(self.celeb_list_widget)
        self.random_pick_button = QtWidgets.QPushButton("Random from List")
        self.random_pick_button.clicked.connect(self.loadRandomCelebrity)
        left_panel.addWidget(self.random_pick_button)
        left_container = QtWidgets.QWidget()
        left_container.setLayout(left_panel)
        learning_split.addWidget(left_container)

        # Right Panel: Profile
        self.learningProfileWidget = QtWidgets.QWidget()
        profile_layout = QtWidgets.QVBoxLayout(self.learningProfileWidget)
        self.image_label = QtWidgets.QLabel("Celebrity Image")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setFixedHeight(300)
        self.name_label = QtWidgets.QLabel("Celebrity Name")
        self.name_label.setObjectName("titleLabel")
        self.bio_text = QtWidgets.QTextEdit()
        self.bio_text.setReadOnly(True)
        profile_layout.addWidget(self.image_label)
        profile_layout.addWidget(self.name_label)
        profile_layout.addWidget(self.bio_text)
        # Buttons: content processing
        buttons_layout = QtWidgets.QHBoxLayout()
        self.review_button = QtWidgets.QPushButton("Review Content")
        self.review_button.clicked.connect(self.reviewCurrentContent)
        self.extract_button = QtWidgets.QPushButton("Extract Key Facts")
        self.extract_button.clicked.connect(self.extractKeyFacts)
        self.generateQuizButton = QtWidgets.QPushButton("Generate Text Quiz")
        self.generateQuizButton.clicked.connect(self.generateQuizContent)
        buttons_layout.addWidget(self.review_button)
        buttons_layout.addWidget(self.extract_button)
        buttons_layout.addWidget(self.generateQuizButton)
        profile_layout.addLayout(buttons_layout)
        learning_split.addWidget(self.learningProfileWidget)
        learning_layout.addLayout(learning_split)
        self.stack.addWidget(self.learningPage)

        # Page 1: Quiz Mode
        self.quizPage = QtWidgets.QWidget()
        quiz_layout = QtWidgets.QVBoxLayout(self.quizPage)
        self.quizImageLabel = QtWidgets.QLabel("Celebrity Image")
        self.quizImageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.quizImageLabel.setFixedHeight(300)
        quiz_layout.addWidget(self.quizImageLabel)
        self.quizQuestionLabel = QtWidgets.QLabel("Quiz question will appear here.")
        quiz_layout.addWidget(self.quizQuestionLabel)
        # Answer buttons
        self.answerButtons = []
        answer_layout = QtWidgets.QHBoxLayout()
        for i in range(4):
            btn = QtWidgets.QPushButton(f"Option {i+1}")
            btn.clicked.connect(self.handleQuizAnswer)
            self.answerButtons.append(btn)
            answer_layout.addWidget(btn)
        quiz_layout.addLayout(answer_layout)
        self.nextQuestionButton = QtWidgets.QPushButton("Next Question")
        self.nextQuestionButton.clicked.connect(self.generateQuizForCurrentProfile)
        quiz_layout.addWidget(self.nextQuestionButton)
        self.returnToLearningButton = QtWidgets.QPushButton("Return to Learning Mode")
        self.returnToLearningButton.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        quiz_layout.addWidget(self.returnToLearningButton)
        self.stack.addWidget(self.quizPage)

        self.statusBar().showMessage("Ready")
        self.stack.setCurrentIndex(0)

    def switchMode(self):
        mode = self.mode_combo.currentText()
        if mode == "Learning Mode":
            self.stack.setCurrentIndex(0)
        elif mode == "Quiz Mode":
            self.stack.setCurrentIndex(1)
            self.generateQuizForCurrentProfile()

    def findCelebrities(self):
        search_term = self.search_term_input.text().strip()
        characteristics = self.characteristics_input.text().strip()
        wiki_lang = self.language_input.text().strip() or "en"
        limit = self.limit_spinner.value()
        if not search_term and not characteristics:
            self.statusBar().showMessage("Please provide a search term or characteristics.")
            return
        self.statusBar().showMessage("Querying GPT-4 for matching celebrities...")
        self.celeb_list_widget.clear()
        celebrities = query_gpt_for_celebrities(search_term, characteristics, limit)
        self.curated_celebrities = celebrities
        if not celebrities:
            self.statusBar().showMessage("No celebrities found. Please adjust your search criteria.")
        else:
            for celeb in celebrities:
                self.celeb_list_widget.addItem(celeb)
            self.statusBar().showMessage(f"Found {len(celebrities)} celebrities. Select one to load profile.")

    def loadSelectedCelebrity(self, item):
        celeb_name = item.text()
        self.loadCelebrityProfile(celeb_name)

    def loadRandomCelebrity(self):
        if not self.curated_celebrities:
            self.statusBar().showMessage("No curated celebrities to choose from.")
            return
        celeb_name = random.choice(self.curated_celebrities)
        self.loadCelebrityProfile(celeb_name)

    def loadCelebrityProfile(self, celeb_name):
        wiki_lang = self.language_input.text().strip() or "en"
        self.statusBar().showMessage(f"Loading profile for {celeb_name} (lang: {wiki_lang})...")
        profile = fetch_profile(celeb_name, wiki_lang)
        self.updateProfileUI(profile)

    def updateProfileUI(self, profile):
        if not profile:
            self.statusBar().showMessage("Profile not found or error in fetching data.")
            return
        self.current_profile = profile
        name = profile.get("name", "Unknown")
        summary = profile.get("summary", "No summary available.")
        image_url = profile.get("image_url")
        # Now we have a real Wikipedia summary. Let’s enhance it with GPT-4:
        enhanced_bio = generate_extended_bio(summary)
        self.name_label.setText(name)
        self.bio_text.setPlainText(enhanced_bio)
        # Load & display image in Learning Mode
        self.image_label.clear()
        if image_url:
            pixmap = load_image_from_url(image_url)
            if pixmap:
                self.image_label.setPixmap(pixmap)
                save_image_for_logging(image_url, name)
            else:
                self.image_label.setText("Image not available")
        else:
            self.image_label.setText("Image not available")

        # Update Quiz Mode
        self.quizImageLabel.clear()
        if image_url:
            pixmap_quiz = load_image_from_url(image_url)
            if pixmap_quiz:
                self.quizImageLabel.setPixmap(pixmap_quiz)
            else:
                self.quizImageLabel.setText("Image not available")
        else:
            self.quizImageLabel.setText("Image not available")

        self.statusBar().showMessage(f"Profile loaded for {name}.")
        content_logger.info(f"Loaded profile for celebrity: {name}")

    def reviewCurrentContent(self):
        current_content = self.bio_text.toPlainText()
        if not current_content:
            self.statusBar().showMessage("No content to review.")
            return
        self.statusBar().showMessage("Reviewing content with GPT-4...")
        reviewed = review_content(current_content)
        self.bio_text.setPlainText(reviewed)
        self.statusBar().showMessage("Content reviewed and updated.")

    def extractKeyFacts(self):
        current_content = self.bio_text.toPlainText()
        if not current_content:
            self.statusBar().showMessage("No content available for extraction.")
            return
        self.statusBar().showMessage("Extracting key facts...")
        facts = extract_key_facts(current_content)
        self.bio_text.append("\n\n--- Key Facts ---\n" + facts)
        self.statusBar().showMessage("Key facts extracted.")

    def generateQuizContent(self):
        current_content = self.bio_text.toPlainText()
        if not current_content:
            self.statusBar().showMessage("No content available to generate quiz.")
            return
        self.statusBar().showMessage("Generating quiz questions...")
        quiz = generate_quiz(current_content)
        QtWidgets.QMessageBox.information(self, "Quiz Questions", quiz)
        self.statusBar().showMessage("Quiz questions generated.")

    def generateQuizForCurrentProfile(self):
        if not self.current_profile:
            self.statusBar().showMessage("No celebrity profile loaded for quiz generation.")
            return
        correct_name = self.current_profile.get("name", "")
        search_term = self.search_term_input.text().strip()
        self.statusBar().showMessage("Generating image quiz question...")
        quiz_question = generate_image_quiz(correct_name, search_term)
        self.quizQuestionLabel.setText(quiz_question)
        self.statusBar().showMessage("Image quiz question generated.")

    def handleQuizAnswer(self):
        sender = self.sender()
        selected = sender.text()
        QtWidgets.QMessageBox.information(self, "Quiz Answer", f"You selected: {selected}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = CelebrityGUI()
    gui.show()
    sys.exit(app.exec_())
