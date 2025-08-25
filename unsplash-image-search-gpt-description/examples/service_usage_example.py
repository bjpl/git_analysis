"""
Example usage of the professional service layer.
Demonstrates how to use the async services for image search, analysis, and translation.
"""

import asyncio
import logging
from pathlib import Path

from src.services import (
    UnsplashClient,
    OpenAIClient,
    TranslationService,
    ServiceManager,
    create_service_manager
)
from src.services.openai_service import ImageAnalysisRequest
from src.services.translation_service import TranslationRequest


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def basic_service_usage():
    """Example of basic service usage."""
    print("=== Basic Service Usage ===")
    
    # Initialize individual services
    async with UnsplashClient(access_key="your-unsplash-key") as unsplash:
        # Search for images
        results = await unsplash.search_photos("nature landscape", per_page=5)
        print(f"Found {len(results.results)} images")
        
        for i, image in enumerate(results.results):
            print(f"  {i+1}. {image.description or 'No description'}")
            print(f"     By: {image.photographer}")
            print(f"     URL: {image.urls['small']}")
    
    # OpenAI client usage
    openai_client = OpenAIClient(
        api_key="your-openai-key",
        default_model="gpt-4-vision-preview"
    )
    
    async with openai_client:
        # Analyze an image
        request = ImageAnalysisRequest(
            image_url="https://images.unsplash.com/photo-example",
            prompt="Describe this image in Spanish for language learning."
        )
        
        try:
            result = await openai_client.analyze_image(request)
            print(f"Analysis: {result.content}")
            print(f"Tokens used: {result.token_usage.total_tokens}")
            print(f"Cost: ${result.cost_estimate.total_cost:.4f}")
        except Exception as e:
            print(f"Analysis failed: {e}")


async def advanced_workflow_example():
    """Example of advanced workflow with all services."""
    print("\n=== Advanced Workflow Example ===")
    
    # Use ServiceManager for coordinated services
    manager = create_service_manager(
        unsplash_access_key="your-unsplash-key",
        openai_api_key="your-openai-key",
        data_dir=Path("data"),
    )
    
    async with manager:
        # 1. Search for images
        print("1. Searching for images...")
        search_results = await manager.unsplash.search_photos(
            query="Spanish architecture",
            per_page=3,
            orientation="landscape"
        )
        
        if not search_results.results:
            print("No images found!")
            return
        
        # 2. Analyze first image
        print("2. Analyzing image with GPT-4 Vision...")
        first_image = search_results.results[0]
        
        analysis_request = ImageAnalysisRequest(
            image_url=first_image.urls['regular'],
            prompt="""Analiza esta imagen y descríbela en español latinoamericano.
            
            IMPORTANTE: Describe SOLO lo que ves en esta imagen específica:
            - ¿Qué objetos, personas o animales aparecen?
            - ¿Cuáles son los colores predominantes?
            - ¿Qué está sucediendo en la escena?
            - ¿Dónde parece estar ubicada (interior/exterior)?
            - ¿Qué detalles destacan?
            
            Escribe 1-2 párrafos descriptivos y naturales.""",
            max_tokens=600,
            temperature=0.7
        )
        
        analysis_result = await manager.openai.analyze_image(analysis_request)
        description = analysis_result.content
        print(f"Description: {description}")
        
        # 3. Extract vocabulary
        print("3. Extracting vocabulary...")
        vocabulary = await manager.openai.extract_vocabulary(
            text=description,
            language="Spanish",
            max_items=8,
            categories=['Sustantivos', 'Verbos', 'Adjetivos', 'Frases clave']
        )
        
        print("Extracted vocabulary:")
        for category, words in vocabulary.items():
            if words:
                print(f"  {category}: {', '.join(words[:5])}")
        
        # 4. Translate vocabulary
        print("4. Translating vocabulary...")
        translated_vocab = await manager.translation.translate_vocabulary(
            vocabulary_dict=vocabulary,
            context=description[:200],  # Use description as context
            source_lang="Spanish",
            target_lang="English"
        )
        
        print("Translations:")
        for category, translations in translated_vocab.items():
            if translations:
                print(f"  {category}:")
                for trans in translations[:3]:  # Show first 3
                    confidence_indicator = "✓" if trans.confidence > 0.8 else "~"
                    cache_indicator = "(cached)" if trans.from_cache else "(new)"
                    print(f"    {confidence_indicator} {trans.original} → {trans.translated} {cache_indicator}")
        
        # 5. Show service statistics
        print("5. Service statistics:")
        status = manager.get_service_status()
        
        if 'unsplash' in status['services']:
            rate_limit = status['services']['unsplash']['rate_limit']
            print(f"  Unsplash: {rate_limit['requests_remaining']}/{rate_limit['requests_per_hour']} requests remaining")
        
        if 'openai' in status['services']:
            usage = status['services']['openai']['usage_stats']
            print(f"  OpenAI: {usage['total_tokens_used']} tokens used, ${usage['total_cost']:.4f} spent")
        
        if 'translation' in status['services']:
            cache_stats = status['services']['translation']['cache_stats']
            print(f"  Translation: {cache_stats['size']} cached translations")


async def batch_translation_example():
    """Example of batch translation functionality."""
    print("\n=== Batch Translation Example ===")
    
    # Sample Spanish phrases
    spanish_phrases = [
        "la casa blanca",
        "el gato negro",
        "correr rápidamente",
        "muy bonito",
        "en la cocina",
        "hablar español",
        "tiempo nublado",
        "flores coloridas"
    ]
    
    openai_client = OpenAIClient(api_key="your-openai-key")
    translation_service = TranslationService(openai_client=openai_client)
    
    async with openai_client:
        # Create translation requests
        requests = [
            TranslationRequest(
                text=phrase,
                source_lang="Spanish",
                target_lang="English",
                context="Spanish language learning vocabulary"
            )
            for phrase in spanish_phrases
        ]
        
        # Perform batch translation
        print("Translating batch of phrases...")
        batch_result = await translation_service.batch_translate(
            requests=requests,
            batch_size=5,
            max_concurrent=2
        )
        
        print(f"Batch translation completed:")
        print(f"  Total: {batch_result.total_count}")
        print(f"  Cached: {batch_result.cached_count}")
        print(f"  Translated: {batch_result.translated_count}")
        print(f"  Processing time: {batch_result.processing_time:.2f}s")
        
        print("\nResults:")
        for result in batch_result.results:
            confidence_icon = "✓" if result.confidence > 0.8 else "~" if result.confidence > 0.5 else "✗"
            cache_icon = "💾" if result.from_cache else "🔄"
            print(f"  {confidence_icon} {cache_icon} {result.original} → {result.translated}")


async def error_handling_example():
    """Example of error handling and resilience."""
    print("\n=== Error Handling Example ===")
    
    # Create client with invalid key to demonstrate error handling
    client = UnsplashClient(access_key="invalid-key")
    
    try:
        # This should fail gracefully
        results = await client.search_photos("test")
        print("Unexpected success!")
    except Exception as e:
        print(f"Expected error handled: {type(e).__name__}: {e}")
    
    # Demonstrate circuit breaker
    print("\nCircuit breaker status:", client.get_status()['circuit_state'])
    
    # Show rate limiting
    client_limited = UnsplashClient(access_key="test-key", requests_per_hour=1)
    rate_status = client_limited.get_rate_limit_status()
    print(f"Rate limit status: {rate_status}")


async def health_check_example():
    """Example of health checking."""
    print("\n=== Health Check Example ===")
    
    manager = create_service_manager(
        unsplash_access_key="your-unsplash-key",
        openai_api_key="your-openai-key",
    )
    
    async with manager:
        # Perform health check
        health = await manager.health_check()
        
        print("Service health status:")
        for service, is_healthy in health.items():
            status = "✓ Healthy" if is_healthy else "✗ Unhealthy"
            print(f"  {service}: {status}")
        
        # Get detailed status
        detailed_status = manager.get_service_status()
        print(f"\nDetailed status available for {len(detailed_status['services'])} services")


async def main():
    """Run all examples."""
    print("🚀 Service Layer Examples")
    print("=" * 50)
    
    # Note: Replace with actual API keys for real usage
    if "your-unsplash-key" in ["your-unsplash-key", "your-openai-key"]:
        print("⚠️  Please replace 'your-unsplash-key' and 'your-openai-key' with actual API keys")
        print("📚 This example shows the structure and usage patterns")
        print()
    
    try:
        # Run examples (some will fail without real API keys)
        # await basic_service_usage()
        # await advanced_workflow_example()
        # await batch_translation_example()
        await error_handling_example()
        # await health_check_example()
        
        print("\n✅ Examples completed!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("This is expected without valid API keys.")


if __name__ == "__main__":
    asyncio.run(main())