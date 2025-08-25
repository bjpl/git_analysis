"""
Service manager for coordinating all API services.
Provides a unified interface and handles service lifecycle management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from .base_service import ServiceError
from .unsplash_service import UnsplashClient
from .openai_service import OpenAIClient
from .translation_service import TranslationService


@dataclass
class ServiceConfig:
    """Configuration for all services."""
    unsplash_access_key: str
    openai_api_key: str
    openai_organization_id: Optional[str] = None
    default_gpt_model: str = "gpt-4-vision-preview"
    data_dir: Path = Path("data")
    enable_caching: bool = True
    timeout: int = 30


class ServiceManager:
    """
    Manager for all API services with unified interface.
    
    Features:
    - Centralized service configuration
    - Unified error handling
    - Service health monitoring
    - Automatic cleanup
    - Logging coordination
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        
        # Initialize services
        self.unsplash: Optional[UnsplashClient] = None
        self.openai: Optional[OpenAIClient] = None
        self.translation: Optional[TranslationService] = None
        
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._services_started = False
        
        # Health check tracking
        self._last_health_check: Optional[datetime] = None
        self._health_status: Dict[str, bool] = {}
        
        self.logger.info("ServiceManager initialized")
    
    async def initialize(self) -> None:
        """Initialize all services."""
        if self._initialized:
            return
        
        try:
            # Create data directory
            self.config.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize OpenAI client
            self.openai = OpenAIClient(
                api_key=self.config.openai_api_key,
                organization_id=self.config.openai_organization_id,
                default_model=self.config.default_gpt_model,
                timeout=self.config.timeout,
                enable_caching=self.config.enable_caching,
            )
            
            # Initialize Unsplash client
            self.unsplash = UnsplashClient(
                access_key=self.config.unsplash_access_key,
                timeout=self.config.timeout,
                enable_caching=self.config.enable_caching,
            )
            
            # Initialize Translation service
            translation_cache_file = self.config.data_dir / "translation_cache.json"
            self.translation = TranslationService(
                openai_client=self.openai,
                cache_file=translation_cache_file,
                default_model=self.config.default_gpt_model,
                enable_caching=self.config.enable_caching,
            )
            
            self._initialized = True
            self.logger.info("All services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise ServiceError(f"Service initialization failed: {e}")
    
    async def start_services(self) -> None:
        """Start all services."""
        if not self._initialized:
            await self.initialize()
        
        if self._services_started:
            return
        
        try:
            # Services are started on-demand with async context managers
            # or when first methods are called
            self._services_started = True
            self.logger.info("All services started")
            
        except Exception as e:
            self.logger.error(f"Failed to start services: {e}")
            raise ServiceError(f"Service startup failed: {e}")
    
    async def stop_services(self) -> None:
        """Stop all services and cleanup resources."""
        if not self._services_started:
            return
        
        cleanup_tasks = []
        
        if self.unsplash:
            cleanup_tasks.append(self.unsplash.close())
        
        if self.openai:
            cleanup_tasks.append(self.openai.close())
        
        if self.translation:
            cleanup_tasks.append(self.translation.close())
        
        if cleanup_tasks:
            try:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                self.logger.info("All services stopped")
            except Exception as e:
                self.logger.error(f"Error during service cleanup: {e}")
        
        self._services_started = False
    
    async def health_check(self, force: bool = False) -> Dict[str, bool]:
        """
        Check health of all services.
        
        Args:
            force: Force health check even if recently performed
            
        Returns:
            Dictionary of service health status
        """
        # Check if we need to perform health check
        now = datetime.now()
        if (not force and self._last_health_check and 
            (now - self._last_health_check).total_seconds() < 60):
            return self._health_status.copy()
        
        self.logger.info("Performing health check on all services")
        
        health_checks = {}
        
        if self.unsplash:
            health_checks['unsplash'] = self.unsplash.health_check()
        
        if self.openai:
            health_checks['openai'] = self.openai.health_check()
        
        if self.translation:
            health_checks['translation'] = self.translation.health_check()
        
        # Execute all health checks concurrently
        if health_checks:
            results = await asyncio.gather(
                *health_checks.values(),
                return_exceptions=True
            )
            
            self._health_status = {}
            for service, result in zip(health_checks.keys(), results):
                if isinstance(result, Exception):
                    self.logger.error(f"Health check failed for {service}: {result}")
                    self._health_status[service] = False
                else:
                    self._health_status[service] = result
        
        self._last_health_check = now
        
        # Log summary
        healthy_count = sum(1 for status in self._health_status.values() if status)
        total_count = len(self._health_status)
        self.logger.info(f"Health check complete: {healthy_count}/{total_count} services healthy")
        
        return self._health_status.copy()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get detailed status of all services."""
        status = {
            'initialized': self._initialized,
            'services_started': self._services_started,
            'last_health_check': self._last_health_check.isoformat() if self._last_health_check else None,
            'health_status': self._health_status.copy(),
            'services': {},
        }
        
        if self.unsplash:
            status['services']['unsplash'] = {
                **self.unsplash.get_status(),
                'rate_limit': self.unsplash.get_rate_limit_status(),
            }
        
        if self.openai:
            status['services']['openai'] = {
                **self.openai.get_status(),
                'usage_stats': self.openai.get_usage_statistics(),
            }
        
        if self.translation:
            status['services']['translation'] = {
                **self.translation.get_status(),
                'cache_stats': self.translation.get_cache_stats(),
            }
        
        return status
    
    def clear_all_caches(self) -> None:
        """Clear caches for all services."""
        self.logger.info("Clearing all service caches")
        
        if self.unsplash:
            self.unsplash.clear_cache()
        
        if self.openai:
            self.openai.clear_cache()
        
        if self.translation:
            self.translation.clear_cache()
        
        self.logger.info("All caches cleared")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_services()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_services()


# Convenience function for creating service manager
def create_service_manager(
    unsplash_access_key: str,
    openai_api_key: str,
    openai_organization_id: Optional[str] = None,
    default_gpt_model: str = "gpt-4-vision-preview",
    data_dir: Optional[Path] = None,
    enable_caching: bool = True,
    timeout: int = 30,
) -> ServiceManager:
    """
    Create a ServiceManager with the given configuration.
    
    Args:
        unsplash_access_key: Unsplash API access key
        openai_api_key: OpenAI API key
        openai_organization_id: Optional OpenAI organization ID
        default_gpt_model: Default GPT model to use
        data_dir: Directory for data storage
        enable_caching: Enable response caching
        timeout: Request timeout in seconds
        
    Returns:
        Configured ServiceManager instance
    """
    config = ServiceConfig(
        unsplash_access_key=unsplash_access_key,
        openai_api_key=openai_api_key,
        openai_organization_id=openai_organization_id,
        default_gpt_model=default_gpt_model,
        data_dir=data_dir or Path("data"),
        enable_caching=enable_caching,
        timeout=timeout,
    )
    
    return ServiceManager(config)