import os
import json
import time
import logging
import requests
import wptools
import wikipedia
import openai
from io import BytesIO
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui

# ------------------ Logger Setup ------------------

def setup_loggers():
    """
    Sets up two loggers:
      - technical_logger: For technical details and debugging.
      - content_logger: For logging GPT prompts/responses and user content.
    Returns:
      (technical_logger, content_logger)
    """
    technical_logger = logging.getLogger("technical")
    technical_logger.setLevel(logging.DEBUG)
    tech_handler = logging.FileHandler("technical_log.txt")
    tech_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    tech_handler.setFormatter(tech_formatter)
    if not technical_logger.handlers:
        technical_logger.addHandler(tech_handler)

    content_logger = logging.getLogger("content")
    content_logger.setLevel(logging.INFO)
    content_handler = logging.FileHandler("content_log.txt")
    content_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    content_handler.setFormatter(content_formatter)
    if not content_logger.handlers:
        content_logger.addHandler(content_handler)

    return technical_logger, content_logger

technical_logger, content_logger = setup_loggers()

# ------------------ GPT-4 Helper Functions ------------------

def query_gpt_for_celebrities(search_term, characteristics, limit=5):
    """
    Uses GPT-4 to generate a curated list of celebrity names based on the search term and characteristics.
    Returns a list of strings.
    """
    prompt = (
        f"Please provide a JSON array of {limit} celebrity names that best match the following criteria:\n"
        f"Search term: {search_term}\n"
        f"Characteristics: {characteristics}\n"
        f"Ensure that if the search term is a specific category (e.g., 'comedians'), the results reflect that category accurately."
    )
    content_logger.info(f"Query GPT-4 for celebrities with prompt:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        content_logger.info(f"GPT-4 celebrity response:\n{content}")
        celeb_names = json.loads(content)
        if not isinstance(celeb_names, list):
            raise ValueError("Response is not a list")
        cleaned_list = []
        for item in celeb_names:
            if isinstance(item, dict):
                # Potential keys: "name", "celebrityName", etc.
                if "name" in item:
                    cleaned_list.append(item["name"])
                elif "celebrityName" in item:
                    cleaned_list.append(item["celebrityName"])
                else:
                    cleaned_list.append(str(item))
            else:
                cleaned_list.append(item)
        return cleaned_list
    except Exception as e:
        technical_logger.error(f"Error in query_gpt_for_celebrities: {e}", exc_info=True)
        return []

def generate_extended_bio(basic_bio):
    """
    Enhances the given biography text with engaging details.
    """
    prompt = f"Enhance the following biography with engaging details and a captivating narrative:\n\n{basic_bio}"
    content_logger.info(f"Generate extended bio prompt:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.7,
        )
        enhanced_bio = response.choices[0].message.content.strip()
        content_logger.info("Extended biography generated successfully.")
        return enhanced_bio
    except Exception as e:
        technical_logger.error(f"Error in generate_extended_bio: {e}", exc_info=True)
        return basic_bio

def extract_key_facts(text):
    """
    Extracts key facts from the given text in bullet-point format.
    """
    prompt = (
        f"From the following biography, extract the key facts (e.g., career highlights, awards, notable works) "
        f"and present them as bullet points:\n\n{text}"
    )
    content_logger.info(f"Extract key facts prompt:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )
        facts = response.choices[0].message.content.strip()
        content_logger.info("Key facts extracted successfully.")
        return facts
    except Exception as e:
        technical_logger.error(f"Error in extract_key_facts: {e}", exc_info=True)
        return "No key facts could be extracted."

def generate_quiz(text):
    """
    Generates multiple-choice quiz questions based on the given text.
    Returns a string containing the quiz.
    """
    prompt = (
        f"Based on the following content about a celebrity, generate 3 to 5 multiple-choice quiz questions. "
        f"For each question, provide one correct answer and 3 distractors. Format your answer as follows:\n"
        f"Q: [question]\nA: [option1], [option2], [option3], [option4] (indicate the correct answer clearly)\n\n{text}"
    )
    content_logger.info(f"Generate quiz prompt:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        quiz = response.choices[0].message.content.strip()
        content_logger.info("Quiz generated successfully.")
        return quiz
    except Exception as e:
        technical_logger.error(f"Error in generate_quiz: {e}", exc_info=True)
        return "No quiz questions could be generated."

def review_content(text):
    """
    Reviews the given content for clarity, coherence, and engagement.
    Returns the refined version of the text.
    """
    prompt = (
        f"Review the following content for clarity, coherence, and engagement. Provide an improved version "
        f"of the text while preserving its key information:\n\n{text}"
    )
    content_logger.info(f"Review content prompt:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.6,
        )
        reviewed = response.choices[0].message.content.strip()
        content_logger.info("Content reviewed successfully.")
        return reviewed
    except Exception as e:
        technical_logger.error(f"Error in review_content: {e}", exc_info=True)
        return text

def generate_image_quiz(correct_name, search_term):
    """
    Generates an image-based quiz question using GPT-4.
    Given the correct celebrity name and the search term context,
    it generates a multiple-choice quiz question.
    """
    prompt = (
        f"Generate a multiple-choice quiz question based on the context of an image. "
        f"The correct celebrity is '{correct_name}', and the search term context is '{search_term}'. "
        f"Ensure that the quiz question relates to this context. Format the output as follows:\n"
        f"Q: [quiz question]\nA: [option1], [option2], [option3], [option4] (indicate the correct answer clearly).\n"
        f"Make sure the correct answer is included among the options."
    )
    content_logger.info(f"Generate image quiz prompt:\n{prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.7,
        )
        quiz_question = response.choices[0].message.content.strip()
        content_logger.info("Image quiz generated successfully.")
        return quiz_question
    except Exception as e:
        technical_logger.error(f"Error in generate_image_quiz: {e}", exc_info=True)
        return "No quiz question could be generated at this time."

# ------------------ Wikipedia & Image Functions ------------------

def fetch_profile(celebrity_name, wiki_lang="en"):
    """
    1) Fetch summary & URL from python-wikipedia library.
    2) Use wptools to fetch single 'main' image from the infobox if available.
    3) If no infobox image, fallback to the first valid .jpg or .png from python-wikipedia's page.images.
    """
    try:
        # --- 1) SUMMARY & URL from python-wikipedia
        wikipedia.set_lang(wiki_lang)
        page_wiki = wikipedia.page(celebrity_name)
        summary = page_wiki.summary or ""
        page_url = page_wiki.url or ""
        # We'll keep the official title from python-wikipedia as well
        official_title = page_wiki.title

    except Exception as e:
        technical_logger.error(f"Error in python-wikipedia fetch for {celebrity_name}: {e}", exc_info=True)
        return None

    # --- 2) Use wptools for a single main infobox image
    main_image_url = None
    try:
        wp_page = wptools.page(celebrity_name, lang=wiki_lang)
        wp_page.get_parse()
        infobox = wp_page.data.get('infobox', {})
        if 'image' in infobox:
            # Usually something like "File:SomeImage.jpg"
            image_name = infobox['image']
            # Create a basic commons link. This might need adjustments for certain files.
            main_image_url = f"https://upload.wikimedia.org/wikipedia/commons/{image_name}"
    except Exception as e:
        technical_logger.error(f"Error using wptools infobox for {celebrity_name}: {e}", exc_info=True)

    # --- 3) Fallback to the first valid .jpg or .png from the python-wikipedia library
    if not main_image_url:
        try:
            for img in page_wiki.images:
                lower_img = img.lower()
                if lower_img.endswith(".jpg") or lower_img.endswith(".jpeg") or lower_img.endswith(".png"):
                    # Skip certain icons/flags
                    if any(x in lower_img for x in ["flag", "icon", "symbol"]):
                        continue
                    main_image_url = img
                    break
        except Exception as e:
            technical_logger.error(f"Error scanning images for {celebrity_name}: {e}", exc_info=True)

    profile = {
        "name": official_title,
        "summary": summary,
        "image_url": main_image_url,
        "url": page_url
    }
    technical_logger.info(f"Fetched profile for {celebrity_name} with summary length {len(summary)} and image {main_image_url}")
    return profile

def load_image_from_url(url, max_width=400):
    """
    Downloads an image from a URL, resizes it while maintaining aspect ratio,
    and returns a QPixmap.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        ratio = max_width / float(image.width)
        new_size = (max_width, int(image.height * ratio))
        image = image.resize(new_size, Image.ANTIALIAS)
        image_qt = ImageQt(image)
        pixmap = QtGui.QPixmap.fromImage(image_qt)
        technical_logger.info(f"Image loaded and resized successfully from {url}")
        return pixmap
    except Exception as e:
        technical_logger.error(f"Error in load_image_from_url ({url}): {e}", exc_info=True)
        return None

def save_image_for_logging(url, celeb_name):
    """
    Downloads an image from the given URL and saves it to a local folder ('logged_images').
    Logs the original URL and the saved file path.
    Returns the file path of the saved image.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        folder = "logged_images"
        if not os.path.exists(folder):
            os.makedirs(folder)
        timestamp = int(time.time())
        filename = f"{celeb_name.replace(' ', '_')}_{timestamp}.jpg"
        file_path = os.path.join(folder, filename)
        image.save(file_path)
        technical_logger.info(f"Image for {celeb_name} saved at {file_path}. Original URL: {url}")
        return file_path
    except Exception as e:
        technical_logger.error(f"Error in save_image_for_logging for {celeb_name} from {url}: {e}", exc_info=True)
        return None
