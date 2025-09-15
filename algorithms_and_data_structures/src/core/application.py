"""
Central Application class that coordinates all components.
Single source of truth for application state and lifecycle.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from ..config import Config
from ..services.curriculum_service import CurriculumService
from ..services.progress_service import ProgressService
from ..services.notes_service import NotesService
from ..persistence.db_manager import DatabaseManager


class ApplicationState(Enum):
    """Application lifecycle states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    TERMINATED = "terminated"


@dataclass
class ApplicationContext:
    """Application-wide context and configuration"""
    config: Config
    user_id: str
    session_id: str
    debug_mode: bool = False
    test_mode: bool = False


class Application:
    """
    Central application controller that manages lifecycle and coordinates components.
    
    This class implements the Facade pattern to provide a simplified interface
    to the complex subsystem of services, managers, and persistence layers.
    """
    
    _instance: Optional['Application'] = None
    
    def __new__(cls):
        """Singleton pattern to ensure single application instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize application if not already initialized"""
        if not hasattr(self, '_initialized'):
            self._initialized = False
            self.state = ApplicationState.UNINITIALIZED
            self.context: Optional[ApplicationContext] = None
            self.services: Dict[str, Any] = {}
            self.logger = logging.getLogger(__name__)
            
    def initialize(self, config: Optional[Config] = None) -> None:
        """
        Initialize the application with all required components.
        
        Args:
            config: Optional configuration object, uses default if not provided
        """
        if self._initialized:
            self.logger.warning("Application already initialized")
            return
            
        try:
            self.state = ApplicationState.INITIALIZING
            self.logger.info("Initializing Algorithm Learning System...")
            
            # Initialize configuration
            self.config = config or Config()
            
            # Create application context
            self.context = ApplicationContext(
                config=self.config,
                user_id=self._get_or_create_user_id(),
                session_id=self._generate_session_id(),
                debug_mode=self.config.debug,
                test_mode=self.config.test_mode
            )
            
            # Initialize database
            self._initialize_database()
            
            # Initialize services
            self._initialize_services()
            
            # Validate initialization
            self._validate_initialization()
            
            self._initialized = True
            self.state = ApplicationState.READY
            self.logger.info("Application initialized successfully")
            
        except Exception as e:
            self.state = ApplicationState.UNINITIALIZED
            self.logger.error(f"Failed to initialize application: {e}")
            raise
            
    def _initialize_database(self) -> None:
        """Initialize database connection and schema"""
        self.logger.debug("Initializing database...")
        
        # Create database manager
        self.db_manager = DatabaseManager(self.config.database_path)
        
        # Initialize schema if needed
        if not self.db_manager.validate_schema():
            self.db_manager.initialize_schema()
            
        # Run migrations if needed
        self.db_manager.run_migrations()
        
        self.logger.debug("Database initialized")
        
    def _initialize_services(self) -> None:
        """Initialize all application services"""
        self.logger.debug("Initializing services...")
        
        # Initialize core services
        self.services['curriculum'] = CurriculumService(
            db_manager=self.db_manager,
            config=self.config
        )
        
        self.services['progress'] = ProgressService(
            db_manager=self.db_manager,
            user_id=self.context.user_id
        )
        
        self.services['notes'] = NotesService(
            db_manager=self.db_manager,
            user_id=self.context.user_id
        )
        
        self.logger.debug(f"Initialized {len(self.services)} services")
        
    def _validate_initialization(self) -> None:
        """Validate that all components are properly initialized"""
        required_services = ['curriculum', 'progress', 'notes']
        
        for service_name in required_services:
            if service_name not in self.services:
                raise RuntimeError(f"Required service '{service_name}' not initialized")
                
        # Validate database connection
        if not self.db_manager.is_connected():
            raise RuntimeError("Database connection not established")
            
    def _get_or_create_user_id(self) -> str:
        """Get existing user ID or create new one"""
        # For now, use a default user
        # In future, implement proper user management
        return "default_user"
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())
        
    def get_service(self, service_name: str) -> Any:
        """
        Get a service by name.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The requested service instance
            
        Raises:
            KeyError: If service doesn't exist
        """
        if not self._initialized:
            raise RuntimeError("Application not initialized")
            
        if service_name not in self.services:
            raise KeyError(f"Service '{service_name}' not found")
            
        return self.services[service_name]
        
    def run(self) -> None:
        """Start the application main loop"""
        if not self._initialized:
            self.initialize()
            
        self.state = ApplicationState.RUNNING
        self.logger.info(f"Application running (session: {self.context.session_id})")
        
    def shutdown(self) -> None:
        """Gracefully shutdown the application"""
        if self.state != ApplicationState.RUNNING:
            self.logger.warning("Application not running, skipping shutdown")
            return
            
        try:
            self.state = ApplicationState.SHUTTING_DOWN
            self.logger.info("Shutting down application...")
            
            # Close database connections
            if hasattr(self, 'db_manager'):
                self.db_manager.close()
                
            # Clean up services
            for service_name, service in self.services.items():
                if hasattr(service, 'cleanup'):
                    service.cleanup()
                    
            self.state = ApplicationState.TERMINATED
            self.logger.info("Application shut down successfully")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise
            
    def reset(self) -> None:
        """Reset application to uninitialized state"""
        self.shutdown()
        self._initialized = False
        self.state = ApplicationState.UNINITIALIZED
        self.context = None
        self.services.clear()
        
    @property
    def is_ready(self) -> bool:
        """Check if application is ready to handle requests"""
        return self.state in [ApplicationState.READY, ApplicationState.RUNNING]
        
    @property
    def curriculum_service(self) -> 'CurriculumService':
        """Convenience property for curriculum service"""
        return self.get_service('curriculum')
        
    @property
    def progress_service(self) -> 'ProgressService':
        """Convenience property for progress service"""
        return self.get_service('progress')
        
    @property
    def notes_service(self) -> 'NotesService':
        """Convenience property for notes service"""
        return self.get_service('notes')