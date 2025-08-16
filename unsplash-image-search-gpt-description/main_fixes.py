# Key fixes to implement in main.py

# FIX 1: Better prompt for actual image analysis
def get_image_description_prompt(user_note=""):
    """Generate a better prompt that ensures GPT analyzes the actual image."""
    base_prompt = """Analiza la imagen que te estoy mostrando y descríbela en español latinoamericano.
    
    IMPORTANTE: Describe SOLO lo que ves en esta imagen específica:
    - ¿Qué objetos, personas o animales aparecen?
    - ¿Cuáles son los colores predominantes?
    - ¿Qué está sucediendo en la escena?
    - ¿Dónde parece estar ubicada (interior/exterior)?
    - ¿Qué detalles destacan?
    
    Escribe 1-2 párrafos descriptivos y naturales."""
    
    if user_note:
        base_prompt += f"\n\nContexto adicional del usuario: {user_note}"
    
    return base_prompt


# FIX 2: Verify image is being sent correctly
def verify_image_url_accessible(url):
    """Quick check that image URL is accessible before sending to GPT."""
    try:
        import requests
        response = requests.head(url, timeout=3)
        return response.status_code == 200
    except:
        return False


# FIX 3: Add simple image cache to avoid re-downloading
class SimpleImageCache:
    """Minimal cache to store last 10 images in memory."""
    def __init__(self, max_size=10):
        self.cache = {}
        self.order = []
        self.max_size = max_size
    
    def get(self, url):
        if url in self.cache:
            return self.cache[url]
        return None
    
    def put(self, url, image_data):
        if url in self.cache:
            return
        
        if len(self.order) >= self.max_size:
            # Remove oldest
            old_url = self.order.pop(0)
            del self.cache[old_url]
        
        self.cache[url] = image_data
        self.order.append(url)


# FIX 4: Better status messages
STATUS_MESSAGES = {
    'searching': 'Buscando imágenes en Unsplash...',
    'downloading': 'Descargando imagen...',
    'generating': 'Analizando imagen con GPT-4 Vision...',
    'extracting': 'Extrayendo vocabulario...',
    'translating': 'Traduciendo al inglés...',
    'ready': 'Listo para buscar',
    'error_quota': '⚠️ Cuota API agotada - revisa tu cuenta',
    'error_network': '⚠️ Error de conexión - verifica internet',
    'error_key': '⚠️ API key inválida - revisa configuración'
}


# FIX 5: Smarter phrase extraction prompt
def get_extraction_prompt(description):
    """Better prompt for extracting meaningful phrases."""
    return f"""Del siguiente texto en español, extrae vocabulario útil para aprender el idioma.
    
    TEXTO: {description}
    
    Devuelve un JSON con estas categorías (pueden estar vacías si no hay ejemplos):
    - "Sustantivos": incluye el artículo (el/la)
    - "Verbos": forma conjugada encontrada
    - "Adjetivos": con concordancia de género si aplica  
    - "Adverbios": solo los más relevantes
    - "Frases clave": expresiones de 2-4 palabras que sean útiles
    
    Evita palabras muy comunes como: el, la, de, que, y, a, en
    Máximo 10 items por categoría.
    """