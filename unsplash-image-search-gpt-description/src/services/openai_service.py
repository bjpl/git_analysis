"""
OpenAI API service for generating descriptions and translations.
"""

import json
import re
from openai import OpenAI


class OpenAIService:
    """Service for interacting with OpenAI's API."""
    
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_image_description(self, image_url, user_note=""):
        """Generate a Spanish description of the image using GPT Vision."""
        # Debug: Verify we have a valid Unsplash URL
        if not image_url.startswith('https://images.unsplash.com/'):
            print(f"Warning: Unexpected image URL format: {image_url}")
        
        print(f"Sending image to GPT-4 Vision: {image_url[:50]}...")
        
        # Create the prompt for image description
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
        
        response = self.client.chat.completions.create(
            model=self.model,
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
    
    def extract_vocabulary(self, description):
        """Extract vocabulary from Spanish description."""
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=600,
                temperature=0.3,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            raw_str = response.choices[0].message.content.strip()
            print("DEBUG GPT OUTPUT:\n", raw_str)
            
            # Parse JSON response
            groups = json.loads(raw_str)
            
            # Ensure all expected keys exist
            expected_keys = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
            for key in expected_keys:
                if key not in groups:
                    groups[key] = []
            
            return groups
            
        except json.JSONDecodeError as je:
            print(f"JSON decode error: {je}")
            return {}
        except Exception as e:
            print(f"Error extracting phrases: {e}")
            return {}
    
    def translate_word(self, word, context=""):
        """Translate Spanish word to US English."""
        if context:
            prompt = (
                f"Translate the Latin American Spanish word '{word}' into US English "
                f"as used in the following sentence:\n\n{context}\n\nProvide only the translation."
            )
        else:
            prompt = f"Translate the Latin American Spanish word '{word}' into US English without additional text."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error de traducción para '{word}': {e}")
            return ""
    
    def handle_api_error(self, error):
        """Handle OpenAI API errors with helpful messages."""
        error_msg = str(error)
        
        if "api_key" in error_msg.lower():
            return "OpenAI API key may be invalid. Please check your configuration."
        elif "rate_limit" in error_msg.lower():
            return "OpenAI rate limit reached. Please wait a moment."
        elif "insufficient_quota" in error_msg.lower():
            return "OpenAI API quota exceeded. Please check your account."
        else:
            return f"Error de la API GPT:\n{error}"