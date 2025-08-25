"""
API Timeout Fixes - Patches for main.py to resolve timeout and cancellation issues.

This module provides drop-in replacements for the timeout-prone API methods in main.py.
Apply these patches to fix:
1. Proper timeout configurations for different API calls
2. Exponential backoff with jitter
3. Cancellation token support for long-running operations
4. Better error handling with specific error types
5. Rate limiting awareness
"""

import time
import threading
from typing import Optional, Callable, Dict, Any
import logging

# Import enhanced services
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    
    from services.enhanced_unsplash_service import (
        EnhancedUnsplashService,
        UnsplashError,
        UnsplashAuthError,
        UnsplashRateLimitError,
        UnsplashNetworkError
    )
    from services.enhanced_openai_service import (
        EnhancedOpenAIService,
        OpenAIError,
        OpenAIAuthError,
        OpenAIRateLimitError,
        OpenAITimeoutError,
        OpenAINetworkError,
        OpenAIQuotaError
    )
    from services.api_timeout_manager import api_timeout_manager, CancellationError
except ImportError as e:
    print(f"Warning: Could not import enhanced services: {e}")
    print("Enhanced timeout features will not be available.")
    EnhancedUnsplashService = None
    EnhancedOpenAIService = None


class ApiTimeoutPatches:
    """
    Collection of patches to fix API timeout issues in the main application.
    """
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = logging.getLogger(f"{__name__}.ApiTimeoutPatches")
        
        # Enhanced services (if available)
        self.enhanced_unsplash = None
        self.enhanced_openai = None
        
        # Operation tracking
        self.active_operations: Dict[str, str] = {}
        self.operation_counter = 0
        
    def initialize_enhanced_services(self) -> bool:
        """
        Initialize enhanced services if available.
        Returns True if successfully initialized.
        """
        if not (EnhancedUnsplashService and EnhancedOpenAIService):
            self.logger.warning("Enhanced services not available, using fallback methods")
            return False
        
        try:
            # Initialize enhanced Unsplash service
            self.enhanced_unsplash = EnhancedUnsplashService(self.app.UNSPLASH_ACCESS_KEY)
            
            # Load existing used image URLs
            if hasattr(self.app, 'used_image_urls'):
                self.enhanced_unsplash.load_used_image_urls(self.app.used_image_urls)
            
            # Initialize enhanced OpenAI service
            self.enhanced_openai = EnhancedOpenAIService(
                api_key=self.app.OPENAI_API_KEY,
                model=self.app.GPT_MODEL
            )
            
            self.logger.info("Enhanced API services initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced services: {e}")
            return False
    
    def _get_operation_id(self, operation_type: str) -> str:
        """Generate unique operation ID."""
        self.operation_counter += 1
        return f"{operation_type}_{self.operation_counter}_{int(time.time())}"
    
    def _update_app_status(self, message: str) -> None:
        """Update application status safely."""
        try:
            if hasattr(self.app, 'update_status'):
                self.app.after(0, lambda: self.app.update_status(message))
        except Exception:
            pass
    
    def patched_fetch_images_page(self, query: str, page: int) -> list:
        """
        Enhanced replacement for fetch_images_page with proper timeout handling.
        """
        operation_id = self._get_operation_id("search")
        self.active_operations[operation_id] = f"Searching '{query}' page {page}"
        
        def progress_callback(message: str):
            self._update_app_status(message)
        
        try:
            if self.enhanced_unsplash:
                # Use enhanced service
                result = self.enhanced_unsplash.search_photos(
                    query=query,
                    page=page,
                    per_page=10,
                    operation_id=operation_id,
                    progress_callback=progress_callback
                )
                return result.get("results", [])
            else:
                # Fallback to improved original method
                return self._fallback_fetch_images_page(query, page, operation_id, progress_callback)
                
        except UnsplashAuthError as e:
            self._update_app_status("API key error")
            raise Exception("Unsplash API key may be invalid. Please check your configuration.")
        except UnsplashRateLimitError as e:
            self._update_app_status("Rate limit reached")
            raise Exception(str(e))
        except UnsplashNetworkError as e:
            self._update_app_status("Network error")
            raise Exception(f"Network error: {str(e)}")
        except CancellationError:
            self._update_app_status("Search cancelled")
            raise Exception("Search was cancelled")
        except Exception as e:
            self._update_app_status("Search failed")
            raise e
        finally:
            self.active_operations.pop(operation_id, None)
    
    def _fallback_fetch_images_page(self, query: str, page: int, operation_id: str, progress_callback: Callable) -> list:
        """Fallback method with improved timeout handling."""
        import requests
        from datetime import datetime, timedelta
        
        headers = {"Authorization": f"Client-ID {self.app.UNSPLASH_ACCESS_KEY}"}
        url = f"https://api.unsplash.com/search/photos?query={query}&page={page}&per_page=10"
        
        progress_callback(f"Searching Unsplash for '{query}' (page {page})...")
        
        # Use timeout manager if available
        if api_timeout_manager:
            try:
                response = api_timeout_manager.make_request_with_timeout(
                    service='unsplash',
                    method='GET',
                    url=url,
                    operation_id=operation_id,
                    progress_callback=progress_callback,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                raise Exception(f"Unsplash API error: {str(e)}")
        else:
            # Basic fallback with timeout
            try:
                response = requests.get(url, headers=headers, timeout=(10, 20))
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.Timeout:
                raise Exception("Unsplash search timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                if "403" in str(e):
                    raise Exception("Unsplash API key may be invalid. Please check your configuration.")
                elif "429" in str(e):
                    next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0)
                    minutes_left = int((next_hour - datetime.now()).seconds / 60)
                    raise Exception(f"Unsplash rate limit reached. Try again in {minutes_left} minutes.")
                else:
                    raise Exception(f"Network error: {str(e)}")
        
        progress_callback(f"Found {data.get('total', 0)} results for '{query}'")
        return data.get("results", [])
    
    def patched_download_image(self, image_url: str, operation_id: Optional[str] = None) -> bytes:
        """
        Enhanced replacement for image download with progress and cancellation.
        """
        if not operation_id:
            operation_id = self._get_operation_id("download")
        
        self.active_operations[operation_id] = f"Downloading image"
        
        def progress_callback(message: str):
            self._update_app_status(message)
        
        try:
            if self.enhanced_unsplash:
                # Use enhanced service
                return self.enhanced_unsplash.download_image(
                    image_url=image_url,
                    operation_id=operation_id,
                    progress_callback=progress_callback
                )
            else:
                # Fallback method
                return self._fallback_download_image(image_url, operation_id, progress_callback)
                
        except CancellationError:
            self._update_app_status("Download cancelled")
            raise Exception("Download was cancelled")
        except Exception as e:
            self._update_app_status("Download failed")
            raise e
        finally:
            self.active_operations.pop(operation_id, None)
    
    def _fallback_download_image(self, image_url: str, operation_id: str, progress_callback: Callable) -> bytes:
        """Fallback download method with timeout."""
        import requests
        
        progress_callback("Starting image download...")
        
        if api_timeout_manager:
            return api_timeout_manager.download_with_progress(
                url=image_url,
                operation_id=operation_id,
                progress_callback=progress_callback
            )
        else:
            # Basic fallback
            try:
                response = requests.get(image_url, timeout=(10, 30), stream=True)
                response.raise_for_status()
                
                content_length = response.headers.get('content-length')
                if content_length:
                    total_size = int(content_length)
                    downloaded = 0
                    chunks = []
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        chunks.append(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            progress_callback(f"Downloading... {progress}%")
                    
                    return b''.join(chunks)
                else:
                    return response.content
                    
            except requests.exceptions.Timeout:
                raise Exception("Image download timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                raise Exception(f"Download failed: {str(e)}")
    
    def patched_generate_description(self, image_url: str, user_note: str = "") -> str:
        """
        Enhanced replacement for GPT description generation with timeout handling.
        """
        operation_id = self._get_operation_id("description")
        self.active_operations[operation_id] = "Generating image description"
        
        def progress_callback(message: str):
            self._update_app_status(message)
        
        try:
            if self.enhanced_openai:
                # Use enhanced service
                return self.enhanced_openai.generate_image_description(
                    image_url=image_url,
                    user_note=user_note,
                    operation_id=operation_id,
                    progress_callback=progress_callback
                )
            else:
                # Fallback method
                return self._fallback_generate_description(image_url, user_note, operation_id, progress_callback)
                
        except OpenAIAuthError:
            self._update_app_status("API key error")
            raise Exception("OpenAI API key may be invalid. Please check your configuration.")
        except OpenAIRateLimitError:
            self._update_app_status("Rate limit reached")
            raise Exception("OpenAI rate limit reached. Please wait a moment.")
        except OpenAIQuotaError:
            self._update_app_status("Quota exceeded")
            raise Exception("OpenAI API quota exceeded. Please check your account.")
        except OpenAITimeoutError:
            self._update_app_status("Request timed out")
            raise Exception("Description generation timed out. Please try again.")
        except CancellationError:
            self._update_app_status("Generation cancelled")
            raise Exception("Description generation was cancelled")
        except Exception as e:
            self._update_app_status("Generation failed")
            raise e
        finally:
            self.active_operations.pop(operation_id, None)
    
    def _fallback_generate_description(self, image_url: str, user_note: str, operation_id: str, progress_callback: Callable) -> str:
        """Fallback description generation with timeout."""
        progress_callback(f"Analyzing image with {self.app.GPT_MODEL}...")
        
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
        
        def make_request():
            return self.app.openai_client.chat.completions.create(
                model=self.app.GPT_MODEL,
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
        
        if api_timeout_manager:
            response = api_timeout_manager.execute_with_timeout(
                func=make_request,
                timeout=120.0,
                operation_id=operation_id
            )
        else:
            response = make_request()
        
        progress_callback("Description generated successfully")
        return response.choices[0].message.content.strip()
    
    def patched_extract_phrases(self, description: str) -> Dict[str, list]:
        """
        Enhanced replacement for phrase extraction with timeout handling.
        """
        operation_id = self._get_operation_id("extract")
        self.active_operations[operation_id] = "Extracting vocabulary"
        
        def progress_callback(message: str):
            self._update_app_status(message)
        
        try:
            if self.enhanced_openai:
                # Use enhanced service
                return self.enhanced_openai.extract_vocabulary(
                    description=description,
                    operation_id=operation_id,
                    progress_callback=progress_callback
                )
            else:
                # Fallback method
                return self._fallback_extract_phrases(description, operation_id, progress_callback)
                
        except Exception as e:
            self._update_app_status("Extraction failed")
            self.logger.error(f"Phrase extraction error: {e}")
            return {}
        finally:
            self.active_operations.pop(operation_id, None)
    
    def _fallback_extract_phrases(self, description: str, operation_id: str, progress_callback: Callable) -> Dict[str, list]:
        """Fallback phrase extraction with timeout."""
        import json
        
        progress_callback("Extracting vocabulary with AI...")
        
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
        
        def make_request():
            return self.app.openai_client.chat.completions.create(
                model=self.app.GPT_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=600,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
        
        try:
            if api_timeout_manager:
                response = api_timeout_manager.execute_with_timeout(
                    func=make_request,
                    timeout=60.0,
                    operation_id=operation_id
                )
            else:
                response = make_request()
            
            raw_str = response.choices[0].message.content.strip()
            groups = json.loads(raw_str)
            
            # Ensure expected keys
            expected_keys = ['Sustantivos', 'Verbos', 'Adjetivos', 'Adverbios', 'Frases clave']
            for key in expected_keys:
                if key not in groups:
                    groups[key] = []
            
            vocab_count = sum(len(v) for v in groups.values() if isinstance(v, list))
            progress_callback(f"Extracted {vocab_count} vocabulary items")
            
            return groups
            
        except json.JSONDecodeError:
            self.logger.error("Failed to parse vocabulary JSON")
            return {}
        except Exception as e:
            self.logger.error(f"Vocabulary extraction error: {e}")
            return {}
    
    def patched_translate_word(self, word: str, context: str = "") -> str:
        """
        Enhanced replacement for word translation with timeout handling.
        """
        operation_id = self._get_operation_id("translate")
        self.active_operations[operation_id] = f"Translating '{word}'"
        
        def progress_callback(message: str):
            self._update_app_status(message)
        
        try:
            if self.enhanced_openai:
                # Use enhanced service
                return self.enhanced_openai.translate_word(
                    word=word,
                    context=context,
                    operation_id=operation_id,
                    progress_callback=progress_callback
                )
            else:
                # Fallback method
                return self._fallback_translate_word(word, context, operation_id, progress_callback)
                
        except Exception as e:
            self._update_app_status("Translation failed")
            self.logger.error(f"Translation error for '{word}': {e}")
            return ""
        finally:
            self.active_operations.pop(operation_id, None)
    
    def _fallback_translate_word(self, word: str, context: str, operation_id: str, progress_callback: Callable) -> str:
        """Fallback translation with timeout."""
        progress_callback(f"Translating '{word}'...")
        
        if context:
            prompt = (
                f"Translate the Latin American Spanish word '{word}' into US English "
                f"as used in the following sentence:\n\n{context}\n\nProvide only the translation."
            )
        else:
            prompt = f"Translate the Latin American Spanish word '{word}' into US English without additional text."
        
        def make_request():
            return self.app.openai_client.chat.completions.create(
                model=self.app.GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.0,
            )
        
        try:
            if api_timeout_manager:
                response = api_timeout_manager.execute_with_timeout(
                    func=make_request,
                    timeout=30.0,
                    operation_id=operation_id
                )
            else:
                response = make_request()
            
            translation = response.choices[0].message.content.strip()
            progress_callback(f"Translated: {word} → {translation}")
            return translation
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return ""
    
    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel specific operation."""
        if operation_id in self.active_operations:
            if api_timeout_manager:
                return api_timeout_manager.cancel_operation(operation_id)
            else:
                # Basic cancellation tracking
                self.active_operations.pop(operation_id, None)
                return True
        return False
    
    def cancel_all_operations(self) -> int:
        """Cancel all active operations."""
        count = 0
        if api_timeout_manager:
            count = api_timeout_manager.cancel_all_operations()
        
        # Clear local tracking
        self.active_operations.clear()
        return count
    
    def get_status(self) -> Dict[str, Any]:
        """Get patch status information."""
        status = {
            'active_operations': len(self.active_operations),
            'operations': dict(self.active_operations),
            'enhanced_services_available': bool(self.enhanced_unsplash and self.enhanced_openai)
        }
        
        if api_timeout_manager:
            status['timeout_manager'] = api_timeout_manager.get_status()
        
        if self.enhanced_unsplash:
            status['unsplash_rate_limit'] = self.enhanced_unsplash.get_rate_limit_status()
        
        if self.enhanced_openai:
            status['openai_usage'] = self.enhanced_openai.get_usage_stats()
        
        return status
    
    def apply_patches_to_app(self) -> bool:
        """
        Apply patches to the application instance.
        Returns True if patches were successfully applied.
        """
        try:
            # Initialize enhanced services
            enhanced_available = self.initialize_enhanced_services()
            
            # Store original methods for potential restoration
            self.app._original_fetch_images_page = getattr(self.app, 'fetch_images_page', None)
            self.app._original_api_call_with_retry = getattr(self.app, 'api_call_with_retry', None)
            
            # Apply patches
            self.app.fetch_images_page = self.patched_fetch_images_page
            
            # Enhanced api_call_with_retry replacement
            def patched_api_call_with_retry(func, *args, max_retries=3, **kwargs):
                """Enhanced API call with retry and better error handling."""
                operation_id = self._get_operation_id("api_call")
                
                if api_timeout_manager:
                    try:
                        return api_timeout_manager.execute_with_timeout(
                            func=func,
                            timeout=60.0,  # Default timeout
                            operation_id=operation_id,
                            *args,
                            **kwargs
                        )
                    except Exception as e:
                        # Fallback to original retry logic if timeout manager fails
                        pass
                
                # Original retry logic with improvements
                import time
                import requests
                last_exception = None
                
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except requests.exceptions.RequestException as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) * 0.5  # Exponential backoff with smaller base
                            self._update_app_status(f"API error, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)
                        continue
                    except Exception as e:
                        last_exception = e
                        if "rate_limit" in str(e).lower():
                            self._update_app_status("Rate limit reached. Waiting...")
                            time.sleep(5)
                            continue
                        break
                
                raise last_exception
            
            self.app.api_call_with_retry = patched_api_call_with_retry
            
            # Add cancellation methods to app
            self.app.cancel_operation = self.cancel_operation
            self.app.cancel_all_operations = self.cancel_all_operations
            self.app.get_api_status = self.get_status
            
            self.logger.info(f"API timeout patches applied successfully (enhanced services: {enhanced_available})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply patches: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources when app closes."""
        try:
            # Cancel all operations
            self.cancel_all_operations()
            
            # Cleanup enhanced services
            if self.enhanced_unsplash:
                self.enhanced_unsplash.cancel_all_operations()
            if self.enhanced_openai:
                self.enhanced_openai.cancel_all_operations()
            
            # Shutdown timeout manager
            if api_timeout_manager:
                api_timeout_manager.shutdown(wait=False)
            
            self.logger.info("API timeout patches cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def apply_timeout_patches(app_instance) -> Optional[ApiTimeoutPatches]:
    """
    Convenience function to apply timeout patches to an application instance.
    
    Usage:
        patches = apply_timeout_patches(app)
        if patches:
            print("Timeout patches applied successfully")
    """
    try:
        patches = ApiTimeoutPatches(app_instance)
        if patches.apply_patches_to_app():
            return patches
        else:
            return None
    except Exception as e:
        logging.error(f"Failed to apply timeout patches: {e}")
        return None
