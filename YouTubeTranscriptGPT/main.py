import sys
import os
import re
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# -------------------------
# Load Environment Variables
# -------------------------
load_dotenv()  # Loads .env file from the project root

# -------------------------
# Logging Setup
# -------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), mode="a")
    ]
)

# -------------------------
# Enhanced Retry Utility with Timeout
# -------------------------
def retry_operation(func, *args, max_retries=3, initial_delay=1, backoff=2, timeout=60, **kwargs):
    attempt = 0
    while attempt < max_retries:
        try:
            # Add timeout to kwargs if it's an API call (for functions that support timeouts)
            if "timeout" not in kwargs and func.__name__ in ["create", "completions", "chat"]:
                kwargs["timeout"] = timeout
            
            start_time = time.time()
            logging.info(f"Starting operation {func.__name__} (attempt {attempt+1}/{max_retries})")
            result = func(*args, **kwargs)
            end_time = time.time()
            logging.info(f"Operation {func.__name__} completed in {end_time - start_time:.2f} seconds")
            return result
        except Exception as e:
            attempt += 1
            logging.warning(f"Retry {attempt} for function {func.__name__} failed: {str(e)}")
            if attempt >= max_retries:
                logging.error(f"All {max_retries} retries failed for {func.__name__}: {str(e)}")
                raise e
            retry_delay = initial_delay * (backoff ** (attempt - 1))
            logging.info(f"Waiting {retry_delay} seconds before retry...")
            time.sleep(retry_delay)

# -------------------------
# OpenAI API Setup
# -------------------------
import openai
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("OPENAI_API_KEY environment variable not set.")

# -------------------------
# Token Counting Setup (tiktoken)
# -------------------------
try:
    import tiktoken
    try:
        encoding = tiktoken.encoding_for_model("gpt-4o")
    except Exception:
        logging.warning("Model 'gpt-4o' encoding not found, falling back to 'gpt-4'.")
        encoding = tiktoken.encoding_for_model("gpt-4")
except Exception as e:
    logging.warning(f"tiktoken not available, falling back to character-based splitting: {str(e)}")
    encoding = None

# -------------------------
# PyQt6 Imports
# -------------------------
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTextEdit, QMessageBox, QHeaderView, QPlainTextEdit, QListWidget,
    QListWidgetItem, QProgressDialog, QDialog, QDialogButtonBox,
    QFormLayout, QFileDialog, QSpinBox, QDoubleSpinBox, QCheckBox, QInputDialog
)
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, QObject, QTimer

# -------------------------
# YouTube API and Transcript Imports
# -------------------------
try:
    from googleapiclient.discovery import build
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError as e:
    logging.error(f"Failed to import required YouTube modules: {str(e)}")
    raise

# -------------------------
# Worker Classes for Threading with Timeout
# -------------------------
class WorkerSignals(QObject):
    finished = pyqtSignal(object)  # returns result
    error = pyqtSignal(tuple)
    progress = pyqtSignal(int, int)  # current, total

class Worker(QRunnable):
    """
    Worker thread that runs a function with given arguments.
    Includes timeout mechanism and progress reporting.
    """
    def __init__(self, fn, *args, timeout=300, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.timeout = timeout
        self.is_killed = False
        
    def run(self):
        try:
            logging.info(f"Worker starting function: {self.fn.__name__}")
            start_time = time.time()
            
            # Set up a timer to monitor for timeouts
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(self.handle_timeout)
            timer.start(self.timeout * 1000)  # Convert seconds to milliseconds
            
            result = self.fn(*self.args, **self.kwargs)
            
            timer.stop()
            elapsed_time = time.time() - start_time
            logging.info(f"Worker completed {self.fn.__name__} in {elapsed_time:.2f} seconds")
            
            if not self.is_killed:
                self.signals.finished.emit(result)
        except Exception as e:
            if not self.is_killed:
                logging.error(f"Worker encountered an error in {self.fn.__name__}: {str(e)}")
                self.signals.error.emit((e,))
    
    def handle_timeout(self):
        self.is_killed = True
        error_msg = f"Operation {self.fn.__name__} timed out after {self.timeout} seconds"
        logging.error(error_msg)
        self.signals.error.emit((TimeoutError(error_msg),))

# -------------------------
# Utility Functions
# -------------------------
def sanitize_filename(name):
    """Sanitize a string to be a safe filename."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    # Further limit length to avoid path length issues
    if len(sanitized) > 150:
        sanitized = sanitized[:147] + "..."
    return sanitized

def merge_transcript_annotations(transcript, annotations):
    """
    Merges annotations with the transcript.
    Returns a string with the original transcript followed by an "Annotations:" block.
    Each annotation includes its start and end indices and the annotation text.
    """
    if not annotations:
        return transcript
    merged = transcript + "\n\n=== Annotations ===\n"
    for ann in annotations:
        merged += f"At char {ann['start']} to {ann['end']}: {ann['text']}\n"
    return merged

# -------------------------
# YouTube API Helper Functions
# -------------------------
def search_channel_videos(channel_name, max_videos=500):
    """
    Searches for a YouTube channel by name and returns a list of videos with details.
    Limits to max_videos to prevent excessive API usage.
    Requires YOUTUBE_API_KEY environment variable.
    """
    logging.info(f"Starting search for channel: {channel_name}")
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        error_msg = "YOUTUBE_API_KEY environment variable not set."
        logging.error(error_msg)
        raise Exception(error_msg)
    
    youtube = build("youtube", "v3", developerKey=api_key)
    # Search for the channel
    search_response = retry_operation(
        youtube.search().list,
        q=channel_name,
        type="channel",
        part="snippet",
        maxResults=1
    ).execute()
    
    if not search_response["items"]:
        error_msg = f"No channel found for name: {channel_name}"
        logging.error(error_msg)
        raise Exception(error_msg)
    
    channel_id = search_response["items"][0]["snippet"]["channelId"]
    logging.info(f"Found channel with ID: {channel_id}")
    
    # Get the uploads playlist ID from channel details
    channel_response = retry_operation(
        youtube.channels().list,
        id=channel_id,
        part="contentDetails"
    ).execute()
    
    uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    logging.info(f"Uploads playlist ID: {uploads_playlist_id}")
    
    # Retrieve videos from the uploads playlist
    videos = []
    next_page_token = None
    
    # Limit the number of API calls to prevent excessive usage
    api_calls = 0
    max_api_calls = (max_videos + 49) // 50  # Calculate max calls needed (50 videos per call)
    
    while True and api_calls < max_api_calls:
        api_calls += 1
        playlist_response = retry_operation(
            youtube.playlistItems().list,
            playlistId=uploads_playlist_id,
            part="snippet,contentDetails",
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        for item in playlist_response.get("items", []):
            try:
                video_data = {
                    "video_id": item["contentDetails"]["videoId"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"].get("publishedAt", "N/A")
                }
                videos.append(video_data)
                
                if len(videos) >= max_videos:
                    logging.info(f"Reached maximum video limit of {max_videos}")
                    break
            except KeyError as e:
                logging.warning(f"Skipping video due to missing data: {str(e)}")
                continue
        
        # Stop if we've reached the video limit or no more pages
        if len(videos) >= max_videos or "nextPageToken" not in playlist_response:
            break
            
        next_page_token = playlist_response.get("nextPageToken")
    
    logging.info(f"Retrieved {len(videos)} videos from channel.")
    return videos

def get_transcript(video_id):
    """
    Retrieves transcript text for a given video_id.
    Enhanced with retry logic and Spanish language support.
    If fetching fails, returns a clear placeholder string.
    """
    logging.info(f"Fetching transcript for video: {video_id}")
    try:
        # Try to fetch Spanish transcript first.
        try:
            transcript_list = retry_operation(
                YouTubeTranscriptApi.get_transcript, 
                video_id, 
                languages=["es"],
                timeout=30  # 30 second timeout for transcript fetch
            )
            logging.info(f"Transcript in Spanish fetched for video: {video_id}")
        except Exception as e:
            logging.warning(f"Spanish transcript not available for {video_id}. Trying default language. ({str(e)})")
            transcript_list = retry_operation(
                YouTubeTranscriptApi.get_transcript, 
                video_id,
                timeout=30
            )
            logging.info(f"Transcript in default language fetched for video: {video_id}")
            
        # Process transcript
        transcript_text = "\n".join([t["text"] for t in transcript_list])
        transcript_length = len(transcript_text)
        logging.info(f"Transcript fetched for {video_id}: {transcript_length} characters")
        
        return transcript_text
    except Exception as e:
        err_str = str(e).lower()
        if "live event" in err_str:
            placeholder = "Transcript unavailable: Live event not started."
        elif "subtitles are disabled" in err_str:
            placeholder = "Transcript unavailable: Subtitles disabled."
        else:
            placeholder = f"Transcript unavailable: {str(e)}"
        logging.error(f"Error fetching transcript for {video_id} after retries: {str(e)}")
        return placeholder

# -------------------------
# GPT-4o Processing Helper Functions
# -------------------------
def split_text_by_tokens(text, max_tokens):
    """
    Splits text into chunks of at most max_tokens tokens.
    Uses tiktoken if available; otherwise, falls back to splitting by characters.
    """
    logging.info(f"Splitting text of length {len(text)} into chunks of max {max_tokens} tokens")
    if encoding:
        try:
            tokens = encoding.encode(text)
            logging.info(f"Text contains {len(tokens)} tokens total")
            chunks = []
            for i in range(0, len(tokens), max_tokens):
                chunk_tokens = tokens[i:i+max_tokens]
                chunk_text = encoding.decode(chunk_tokens)
                chunks.append(chunk_text)
            logging.info(f"Split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logging.error(f"Error splitting text with tiktoken: {str(e)}")
            # Fall back to character-based splitting
            max_chars = max_tokens * 4  # approximate
            chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            logging.info(f"Fell back to character-based splitting, {len(chunks)} chunks")
            return chunks
    else:
        max_chars = max_tokens * 4  # approximate
        chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
        logging.info(f"Using character-based splitting, {len(chunks)} chunks")
        return chunks

def call_gpt4_api(prompt, transcript_chunk, temperature=0.7, timeout=120):
    """
    Calls the GPT-4o API with a prompt and a chunk of transcript.
    
    --- GPT-4o API Call Section ---
    This function uses the current OpenAI API client to interact with the GPT-4o model.
    Includes timeout and detailed logging.
    
    Parameters:
        prompt (str): The base prompt to send to GPT-4o.
        transcript_chunk (str): A chunk of transcript text to be appended to the prompt.
        temperature (float): Controls the randomness of the response.
        timeout (int): Timeout in seconds for the API call
    
    Returns:
        The cleaned GPT response as a string.
    """
    logging.info(f"Preparing GPT-4o API call with prompt of length {len(prompt)} and transcript chunk of length {len(transcript_chunk)}")
    try:
        client = openai.OpenAI(api_key=openai.api_key)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}\n\nTranscript:\n{transcript_chunk}"}
        ]
        
        total_input_length = len(messages[0]["content"]) + len(messages[1]["content"])
        logging.info(f"Calling GPT-4o API with total input length of {total_input_length} characters")
        
        start_time = time.time()
        
        # --- Begin GPT-4o API call ---
        response = retry_operation(
            client.chat.completions.create,
            model="gpt-4o",  # Use your GPT-4o model identifier here (replace with "gpt-4" if needed)
            messages=messages,
            temperature=temperature,
            timeout=timeout  # Add explicit timeout for API call
        )
        # --- End GPT-4o API call ---
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        reply = response.choices[0].message.content.strip()
        reply_length = len(reply)
        
        logging.info(f"GPT-4o API call completed in {elapsed_time:.2f} seconds. Response length: {reply_length} characters")
        
        return reply
    except Exception as e:
        error_msg = f"Error in GPT-4o API call: {str(e)}"
        logging.error(error_msg)
        # Return a user-friendly error message that can be included in the output
        return f"Error processing this section with GPT-4o: {str(e)}\n\nPlease try again with a smaller chunk size or check your API key and network connection."

def process_transcript_with_prompt(video_title, transcript, prompt, max_tokens=12000, temperature=0.7, timeout=180):
    """
    Splits the transcript if needed and processes each chunk with GPT-4o.
    
    Uses the call_gpt4_api function (documented above) for each chunk.
    Includes improved error handling and logging.
    
    Returns:
        The combined GPT-4o response as a single string.
    """
    logging.info(f"Processing transcript for video '{video_title}' with prompt: {prompt[:100]}...")
    
    if not transcript or transcript.startswith("Transcript unavailable"):
        logging.warning(f"Cannot process unavailable transcript for '{video_title}'")
        return f"Unable to process: {transcript}"
    
    # Use a smaller max_tokens value for safety (12000 is a reasonable default)
    actual_max_tokens = min(max_tokens, 12000)
    chunks = split_text_by_tokens(transcript, actual_max_tokens)
    
    responses = []
    for i, chunk in enumerate(chunks):
        chunk_num = i + 1
        total_chunks = len(chunks)
        logging.info(f"Processing chunk {chunk_num}/{total_chunks} for video '{video_title}'")
        
        try:
            response = call_gpt4_api(prompt, chunk, temperature=temperature, timeout=timeout)
            responses.append(response)
            logging.info(f"Successfully processed chunk {chunk_num}/{total_chunks}")
        except Exception as e:
            error_message = f"Error processing chunk {chunk_num}/{total_chunks}: {str(e)}"
            logging.error(error_message)
            responses.append(f"Error processing chunk {chunk_num}: {str(e)}")
    
    full_response = "\n\n=== Chunk Separator ===\n\n".join(responses)
    logging.info(f"Completed processing all {len(chunks)} chunks for '{video_title}'")
    
    return full_response

def process_all_transcripts(videos, transcripts, prompts, token_limit, temperature, outputs_folder, include_annotations, annotations_dict, progress_callback=None):
    """
    For each transcript (associated with a video) and for each prompt,
    merge the transcript with annotations (if enabled), then process (splitting if necessary)
    and save the outcome.
    
    Calls progress_callback(current, total) after each processed task.
    Includes improved error handling to continue processing even if some videos fail.
    
    Returns:
        A list of tuples: (video_id, prompt, output_file, success)
    """
    os.makedirs(outputs_folder, exist_ok=True)
    results = []  # List of tuples: (video_id, prompt, output_file, success)
    
    # Filter videos to only those with transcripts
    videos_with_transcripts = [v for v in videos if v["video_id"] in transcripts]
    total_tasks = len(videos_with_transcripts) * len(prompts)
    
    if total_tasks == 0:
        logging.warning("No transcripts to process")
        return results
    
    current_task = 0
    
    for video in videos_with_transcripts:
        video_id = video["video_id"]
        video_title = video["title"]
        transcript = transcripts[video_id]
        
        # Skip videos with unavailable transcripts
        if transcript.startswith("Transcript unavailable"):
            logging.warning(f"Skipping unavailable transcript for video: {video_title}")
            if progress_callback:
                for _ in prompts:
                    current_task += 1
                    progress_callback(current_task, total_tasks)
            continue
        
        # Merge annotations with transcript if enabled.
        ann = annotations_dict.get(video_id, [])
        if include_annotations and ann:
            transcript_to_process = merge_transcript_annotations(transcript, ann)
            logging.info(f"Merged {len(ann)} annotations with transcript for '{video_title}'")
        else:
            transcript_to_process = transcript
        
        sanitized_title = sanitize_filename(video_title) or video_id
        
        for idx, prompt in enumerate(prompts):
            prompt_num = idx + 1
            prompt_preview = prompt[:50] + ("..." if len(prompt) > 50 else "")
            
            logging.info(f"Processing video '{video_title}' with prompt {prompt_num}: {prompt_preview}")
            
            try:
                outcome = process_transcript_with_prompt(
                    video_title,
                    transcript_to_process,
                    prompt,
                    max_tokens=token_limit,
                    temperature=temperature
                )
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{sanitized_title}_prompt{prompt_num}_{timestamp}.txt"
                file_path = os.path.join(outputs_folder, filename)
                
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(outcome)
                    logging.info(f"Outcome saved to: {file_path}")
                    success = True
                except Exception as e:
                    error_msg = f"Error saving outcome for video '{video_title}': {str(e)}"
                    logging.error(error_msg)
                    file_path = error_msg
                    success = False
            except Exception as e:
                error_msg = f"Error processing video '{video_title}' with prompt {prompt_num}: {str(e)}"
                logging.error(error_msg)
                file_path = "Error: " + error_msg
                success = False
            
            results.append((video_id, prompt, file_path, success))
            current_task += 1
            
            if progress_callback:
                progress_callback(current_task, total_tasks)
    
    successful_count = sum(1 for _, _, _, success in results if success)
    logging.info(f"Completed processing {successful_count}/{total_tasks} tasks successfully")
    
    return results

# -------------------------
# Settings Dialog
# -------------------------
class SettingsDialog(QDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.current_settings = current_settings
        layout = QFormLayout(self)
        
        self.token_limit_spin = QSpinBox()
        self.token_limit_spin.setRange(1000, 12000)  # Lower max to avoid API issues
        self.token_limit_spin.setValue(current_settings.get("token_limit", 8000))
        
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 1.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(current_settings.get("temperature", 0.7))
        
        self.api_timeout_spin = QSpinBox()
        self.api_timeout_spin.setRange(30, 300)
        self.api_timeout_spin.setValue(current_settings.get("api_timeout", 120))
        
        self.include_ann_checkbox = QCheckBox("Include Annotations in GPT Prompt")
        self.include_ann_checkbox.setChecked(current_settings.get("include_annotations", True))
        
        self.max_videos_spin = QSpinBox()
        self.max_videos_spin.setRange(50, 1000)
        self.max_videos_spin.setValue(current_settings.get("max_videos", 500))
        
        self.transcripts_folder_edit = QLineEdit()
        self.transcripts_folder_edit.setText(current_settings.get("transcripts_folder", os.path.join(os.getcwd(), "transcripts")))
        self.transcripts_folder_button = QPushButton("Browse")
        self.transcripts_folder_button.clicked.connect(self.browse_transcripts_folder)
        
        self.outputs_folder_edit = QLineEdit()
        self.outputs_folder_edit.setText(current_settings.get("outputs_folder", os.path.join(os.getcwd(), "outputs")))
        self.outputs_folder_button = QPushButton("Browse")
        self.outputs_folder_button.clicked.connect(self.browse_outputs_folder)
        
        transcripts_layout = QHBoxLayout()
        transcripts_layout.addWidget(self.transcripts_folder_edit)
        transcripts_layout.addWidget(self.transcripts_folder_button)
        
        outputs_layout = QHBoxLayout()
        outputs_layout.addWidget(self.outputs_folder_edit)
        outputs_layout.addWidget(self.outputs_folder_button)
        
        layout.addRow("Token Limit:", self.token_limit_spin)
        layout.addRow("Temperature:", self.temperature_spin)
        layout.addRow("API Timeout (seconds):", self.api_timeout_spin)
        layout.addRow("Max Videos to Fetch:", self.max_videos_spin)
        layout.addRow(self.include_ann_checkbox)
        layout.addRow("Transcripts Folder:", transcripts_layout)
        layout.addRow("Outputs Folder:", outputs_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def browse_transcripts_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Transcripts Folder", os.getcwd())
        if folder:
            self.transcripts_folder_edit.setText(folder)
    
    def browse_outputs_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Outputs Folder", os.getcwd())
        if folder:
            self.outputs_folder_edit.setText(folder)
    
    def get_settings(self):
        return {
            "token_limit": self.token_limit_spin.value(),
            "temperature": self.temperature_spin.value(),
            "api_timeout": self.api_timeout_spin.value(),
            "max_videos": self.max_videos_spin.value(),
            "include_annotations": self.include_ann_checkbox.isChecked(),
            "transcripts_folder": self.transcripts_folder_edit.text(),
            "outputs_folder": self.outputs_folder_edit.text()
        }

# -------------------------
# Annotation Dialog (for adding/editing an annotation)
# -------------------------
class AnnotationDialog(QDialog):
    def __init__(self, selected_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Annotation")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Selected Transcript Text:"))
        self.selected_text_display = QTextEdit()
        self.selected_text_display.setReadOnly(True)
        self.selected_text_display.setPlainText(selected_text)
        layout.addWidget(self.selected_text_display)
        layout.addWidget(QLabel("Enter Annotation:"))
        self.annotation_edit = QPlainTextEdit()
        layout.addWidget(self.annotation_edit)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_annotation(self):
        return self.annotation_edit.toPlainText().strip()

# -------------------------
# MainWindow UI Class
# -------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Transcript & GPT-4o Processor with Annotations")
        self.resize(1200, 800)
        
        self.threadpool = QThreadPool()
        logging.info(f"Application started. Maximum threads: {self.threadpool.maxThreadCount()}")
        
        self.videos = []         # list of video dicts
        self.transcripts = {}    # mapping video_id -> transcript text
        self.annotations = {}    # mapping video_id -> list of annotations
        
        # Default settings (modifiable via Settings dialog)
        self.settings = {
            "token_limit": 8000,           # Reduced from 120000 to avoid API issues
            "temperature": 0.7,
            "api_timeout": 120,            # 2 minutes timeout for API calls
            "max_videos": 500,             # Limit videos to prevent excessive API usage
            "include_annotations": True,
            "transcripts_folder": os.path.join(os.getcwd(), "transcripts"),
            "outputs_folder": os.path.join(os.getcwd(), "outputs")
        }
        
        self.setup_ui()
        
        # Progress dialog for transcript downloads
        self.progress_bar = QProgressDialog("Downloading transcripts...", "Cancel", 0, 0, self)
        self.progress_bar.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_bar.setCancelButton(None)
        self.progress_bar.close()
        
        # Status Bar for information
        self.statusBar().showMessage("Ready")
    
    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # --- Top Section: Search and Settings ---
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter YouTube channel name")
        self.search_button = QPushButton("Search Channel")
        self.search_button.clicked.connect(self.on_search_channel)
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        search_layout.addWidget(QLabel("Channel Name:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.settings_button)
        
        # --- Middle Section: Videos Table ---
        self.videos_table = QTableWidget()
        self.videos_table.setColumnCount(3)
        self.videos_table.setHorizontalHeaderLabels(["Title", "Published At", "Video ID"])
        self.videos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.videos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.videos_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.videos_table.cellClicked.connect(self.on_video_selected)
        
        self.transcript_button = QPushButton("Get Transcripts for Selected Videos")
        self.transcript_button.clicked.connect(self.on_get_transcripts)
        
        # --- Right Section: Transcript Viewer and Annotations ---
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Transcript Viewer:"))
        self.transcript_viewer = QTextEdit()
        self.transcript_viewer.setReadOnly(True)
        right_layout.addWidget(self.transcript_viewer)
        
        # Annotation controls
        annotation_buttons_layout = QHBoxLayout()
        self.add_annotation_button = QPushButton("Add Annotation")
        self.add_annotation_button.clicked.connect(self.on_add_annotation)
        self.delete_annotation_button = QPushButton("Delete Annotation")
        self.delete_annotation_button.clicked.connect(self.on_delete_annotation)
        annotation_buttons_layout.addWidget(self.add_annotation_button)
        annotation_buttons_layout.addWidget(self.delete_annotation_button)
        right_layout.addLayout(annotation_buttons_layout)
        
        # Annotation list
        right_layout.addWidget(QLabel("Annotations:"))
        self.annotation_list = QListWidget()
        right_layout.addWidget(self.annotation_list)
        
        # --- GPT-4 Prompt Section ---
        prompts_layout = QVBoxLayout()
        prompts_label = QLabel("Enter GPT-4 Prompt(s) (one per line):")
        self.prompts_input = QPlainTextEdit()
        self.process_gpt_button = QPushButton("Process Transcripts with GPT-4o")
        self.process_gpt_button.clicked.connect(self.on_process_with_gpt4)
        prompts_layout.addWidget(prompts_label)
        prompts_layout.addWidget(self.prompts_input)
        prompts_layout.addWidget(self.process_gpt_button)
        
        # --- Combine Left (Videos) and Right (Transcript + Annotations + Prompts) ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.videos_table)
        left_layout.addWidget(self.transcript_button)
        
        combined_layout = QHBoxLayout()
        combined_layout.addLayout(left_layout, 1)
        
        right_side_layout = QVBoxLayout()
        right_side_layout.addLayout(right_layout, 2)
        right_side_layout.addLayout(prompts_layout, 1)
        combined_layout.addLayout(right_side_layout, 1)
        
        main_layout.addLayout(search_layout)
        main_layout.addLayout(combined_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            logging.info(f"Settings updated: {self.settings}")
            QMessageBox.information(self, "Settings", "Settings updated successfully.")
    
    def on_search_channel(self):
        channel_name = self.search_input.text().strip()
        if not channel_name:
            QMessageBox.warning(self, "Input Error", "Please enter a channel name.")
            return
            
        max_videos = self.settings.get("max_videos", 500)
        
        self.search_button.setEnabled(False)
        self.statusBar().showMessage(f"Searching for channel: {channel_name}...")
        logging.info(f"Initiating search for channel: {channel_name} (max videos: {max_videos})")
        
        worker = Worker(search_channel_videos, channel_name, max_videos, timeout=180)  # 3 minute timeout
        worker.signals.finished.connect(self.on_search_finished)
        worker.signals.error.connect(self.on_worker_error)
        self.threadpool.start(worker)
    
    def on_search_finished(self, videos):
        self.search_button.setEnabled(True)
        self.videos = videos
        self.videos_table.setRowCount(0)
        
        for video in videos:
            row = self.videos_table.rowCount()
            self.videos_table.insertRow(row)
            self.videos_table.setItem(row, 0, QTableWidgetItem(video["title"]))
            self.videos_table.setItem(row, 1, QTableWidgetItem(video["published_at"]))
            self.videos_table.setItem(row, 2, QTableWidgetItem(video["video_id"]))
        
        logging.info(f"Videos table updated with {len(videos)} entries.")
        self.statusBar().showMessage(f"Found {len(videos)} videos. Select videos and click 'Get Transcripts'")
    
    def on_get_transcripts(self):
        selected_rows = self.videos_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select at least one video.")
            return
            
        transcripts_folder = self.settings.get("transcripts_folder", os.path.join(os.getcwd(), "transcripts"))
        os.makedirs(transcripts_folder, exist_ok=True)
        logging.info(f"Saving transcripts to folder: {transcripts_folder}")
        
        total_tasks = len(selected_rows)
        self.progress_bar.setLabelText(f"Downloading {total_tasks} transcripts...")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(total_tasks)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        for index in selected_rows:
            row = index.row()
            video = self.videos[row]
            video_id = video["video_id"]
            
            # Skip if we already have this transcript
            if video_id in self.transcripts:
                current = self.progress_bar.value() + 1
                self.progress_bar.setValue(current)
                continue
                
            worker = Worker(get_transcript, video_id, timeout=60)  # 1 minute timeout per transcript
            worker.signals.finished.connect(lambda transcript, vid=video: self.on_transcript_fetched(vid, transcript, transcripts_folder))
            worker.signals.error.connect(self.on_worker_error)
            self.threadpool.start(worker)
    
    def on_transcript_fetched(self, video, transcript, folder):
        video_id = video["video_id"]
        # Store transcript (even placeholder) and update progress
        self.transcripts[video_id] = transcript
        
        if transcript.startswith("Transcript unavailable:"):
            logging.warning(f"Transcript for video {video_id} is unavailable: {transcript}")
            self.statusBar().showMessage(f"Warning: Transcript unavailable for {video['title']}", 5000)
        else:
            self.statusBar().showMessage(f"Transcript downloaded: {video['title']}", 3000)
            
        filename = sanitize_filename(video["title"]) or video_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(folder, f"{filename}_{timestamp}.txt")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            logging.info(f"Transcript saved to: {file_path}")
        except Exception as e:
            logging.error(f"Error saving transcript for video {video_id}: {str(e)}")
        
        val = self.progress_bar.value() + 1
        self.progress_bar.setValue(val)
        
        if val >= self.progress_bar.maximum():
            self.progress_bar.hide()
            self.statusBar().showMessage(f"All {val} transcripts downloaded", 5000)
        
        self.transcript_viewer.setPlainText(transcript)
        self.load_annotations_for_video(video_id)
    
    def on_video_selected(self, row, column):
        video_id = self.videos_table.item(row, 2).text()
        if video_id in self.transcripts:
            self.transcript_viewer.setPlainText(self.transcripts[video_id])
            self.load_annotations_for_video(video_id)
        else:
            self.transcript_viewer.setPlainText("Transcript not downloaded yet. Please click 'Get Transcripts for Selected Videos'.")
            self.annotation_list.clear()
    
    def on_add_annotation(self):
        selected_items = self.videos_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Video Selected", "Please select a video first.")
            return
        
        video_id = self.videos_table.item(self.videos_table.currentRow(), 2).text()
        transcript = self.transcripts.get(video_id, "")
        
        if not transcript:
            QMessageBox.warning(self, "No Transcript", "Transcript not available for the selected video.")
            return
            
        cursor = self.transcript_viewer.textCursor()
        if cursor.hasSelection():
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            selected_text = cursor.selectedText()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a portion of the transcript to annotate.")
            return
        
        dialog = AnnotationDialog(selected_text, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            annotation_text = dialog.get_annotation()
            if annotation_text:
                annotation = {"start": sel_start, "end": sel_end, "text": annotation_text}
                if video_id not in self.annotations:
                    self.annotations[video_id] = []
                self.annotations[video_id].append(annotation)
                self.update_annotation_list(video_id)
                self.statusBar().showMessage("Annotation added", 3000)
    
    def on_delete_annotation(self):
        selected_items = self.videos_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Video Selected", "Please select a video first.")
            return
            
        video_id = self.videos_table.item(self.videos_table.currentRow(), 2).text()
        selected = self.annotation_list.currentRow()
        
        if video_id in self.annotations and selected >= 0:
            del self.annotations[video_id][selected]
            self.update_annotation_list(video_id)
            self.statusBar().showMessage("Annotation deleted", 3000)
    
    def update_annotation_list(self, video_id):
        self.annotation_list.clear()
        for ann in self.annotations.get(video_id, []):
            item_text = f"Chars {ann['start']}–{ann['end']}: {ann['text']}"
            self.annotation_list.addItem(QListWidgetItem(item_text))
    
    def load_annotations_for_video(self, video_id):
        self.annotation_list.clear()
        if video_id in self.annotations:
            self.update_annotation_list(video_id)
    
    def on_process_with_gpt4(self):
        raw_prompts = self.prompts_input.toPlainText().strip()
        if not raw_prompts:
            QMessageBox.warning(self, "Input Error", "Please enter at least one GPT-4 prompt.")
            return
            
        prompts = [p.strip() for p in raw_prompts.splitlines() if p.strip()]
        if not prompts:
            QMessageBox.warning(self, "Input Error", "No valid prompts found.")
            return
            
        if not self.transcripts:
            QMessageBox.warning(self, "No Transcripts", "Please download transcripts first.")
            return
        
        # Get selected videos only if some are selected, otherwise process all with transcripts
        selected_rows = self.videos_table.selectionModel().selectedRows()
        if selected_rows:
            selected_videos = []
            for index in selected_rows:
                row = index.row()
                video = self.videos[row]
                if video["video_id"] in self.transcripts:
                    selected_videos.append(video)
            
            if not selected_videos:
                QMessageBox.warning(self, "Selection Error", "None of the selected videos have transcripts.")
                return
                
            videos_to_process = selected_videos
            videos_count = len(videos_to_process)
        else:
            # Process all videos with transcripts
            videos_to_process = [v for v in self.videos if v["video_id"] in self.transcripts]
            videos_count = len(videos_to_process)
            
            if videos_count == 0:
                QMessageBox.warning(self, "No Transcripts", "No videos have transcripts. Please download transcripts first.")
                return
                
            # Confirm with user if processing all videos
            if videos_count > 5:  # Arbitrary threshold
                confirm = QMessageBox.question(
                    self,
                    "Confirm Processing",
                    f"No videos selected. Process all {videos_count} videos with transcripts?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm != QMessageBox.StandardButton.Yes:
                    return
        
        self.process_gpt_button.setEnabled(False)
        logging.info(f"Starting GPT-4o processing for {videos_count} video(s) with {len(prompts)} prompt(s).")
        self.statusBar().showMessage(f"Processing {videos_count} videos with GPT-4o...")
        
        total_tasks = len(videos_to_process) * len(prompts)
        progress_dialog = QProgressDialog("Processing GPT-4o...", "Cancel", 0, total_tasks, self)
        progress_dialog.setWindowTitle("GPT-4o Processing")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()
        
        def progress_callback(current, total):
            if progress_dialog.wasCanceled():
                return
            progress_dialog.setValue(current)
            progress_dialog.setLabelText(f"Processing video {current}/{total}...")
        
        # Get current settings
        token_limit = self.settings.get("token_limit", 8000)
        temperature = self.settings.get("temperature", 0.7)
        api_timeout = self.settings.get("api_timeout", 120)
        outputs_folder = self.settings.get("outputs_folder", os.path.join(os.getcwd(), "outputs"))
        include_annotations = self.settings.get("include_annotations", True)
        
        worker = Worker(
            process_all_transcripts,
            videos_to_process,
            self.transcripts,
            prompts,
            token_limit,
            temperature,
            outputs_folder,
            include_annotations,
            self.annotations,
            progress_callback,
            timeout=300  # 5 minute timeout for the entire processing
        )
        
        worker.signals.finished.connect(lambda results: self.on_gpt4_processing_finished(results, progress_dialog))
        worker.signals.error.connect(lambda error: self.on_worker_error(error, progress_dialog))
        self.threadpool.start(worker)
    
    def on_gpt4_processing_finished(self, results, progress_dialog):
        self.process_gpt_button.setEnabled(True)
        progress_dialog.setValue(progress_dialog.maximum())
        progress_dialog.close()
        
        successful_results = [(vid, prompt, filepath) for vid, prompt, filepath, success in results if success]
        failed_results = [(vid, prompt, error) for vid, prompt, error, success in results if not success]
        
        if successful_results:
            successful_msg = "GPT-4o processing completed for the following:\n\n"
            for video_id, prompt, filepath in successful_results:
                video_title = next((v["title"] for v in self.videos if v["video_id"] == video_id), video_id)
                prompt_preview = prompt[:30] + ("..." if len(prompt) > 30 else "")
                successful_msg += f"• {video_title}\n  Prompt: {prompt_preview}\n  Output: {filepath}\n\n"
            
            if failed_results:
                successful_msg += "\nHowever, some processing tasks failed. See error log for details."
            
            # Use more detailed dialog for results instead of a simple message box
            results_dialog = QDialog(self)
            results_dialog.setWindowTitle("Processing Results")
            results_dialog.resize(800, 400)
            
            layout = QVBoxLayout(results_dialog)
            
            results_text = QTextEdit()
            results_text.setReadOnly(True)
            results_text.setPlainText(successful_msg)
            
            layout.addWidget(results_text)
            
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            button_box.accepted.connect(results_dialog.accept)
            layout.addWidget(button_box)
            
            results_dialog.exec()
        else:
            QMessageBox.critical(self, "Processing Failed", "All GPT-4o processing tasks failed. Check error log for details.")
        
        if failed_results:
            error_log = "The following processing tasks failed:\n\n"
            for video_id, prompt, error in failed_results:
                video_title = next((v["title"] for v in self.videos if v["video_id"] == video_id), video_id)
                prompt_preview = prompt[:30] + ("..." if len(prompt) > 30 else "")
                error_log += f"• {video_title}\n  Prompt: {prompt_preview}\n  Error: {error}\n\n"
            
            logging.error(f"Processing failures: {error_log}")
            self.statusBar().showMessage("Processing completed with errors", 5000)
        else:
            self.statusBar().showMessage("Processing completed successfully", 5000)
        
        logging.info(f"GPT-4o processing finished: {len(successful_results)} succeeded, {len(failed_results)} failed")
    
    def on_worker_error(self, error_tuple, progress_dialog=None):
        if progress_dialog and progress_dialog.isVisible():
            progress_dialog.close()
            
        e = error_tuple[0]
        error_message = str(e)
        
        if isinstance(e, TimeoutError):
            error_title = "Operation Timed Out"
            logging.error(f"Operation timed out: {error_message}")
        else:
            error_title = "Error"
            logging.error(f"Worker error: {error_message}")
        
        self.statusBar().showMessage(f"Error: {error_message}", 5000)
        self.process_gpt_button.setEnabled(True)
        self.search_button.setEnabled(True)
        
        QMessageBox.critical(self, error_title, f"An error occurred: {error_message}")

# -------------------------
# Main Application Entry Point
# -------------------------
def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.critical(f"Fatal application error: {str(e)}")
        print(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()