# Adaptive Learning System - Integration Guide

## Overview

This document provides comprehensive guidance for integrating and extending the Adaptive Learning System CLI application. The system is designed with a modular architecture that allows for easy customization and extension.

## Architecture Overview

```
src/
├── main.py                     # CLI entry point
├── app.py                      # Main application coordinator
├── models/                     # Data models and schemas
├── services/                   # Business logic services
│   ├── curriculum_service.py   # Learning path management
│   └── content_service.py      # Content delivery and management
├── data/                       # Database and data management
├── utils/                      # Utility modules
│   ├── logging_config.py       # Centralized logging
│   ├── config_manager.py       # Configuration management
│   └── cli_completion.py       # Auto-completion support
└── INTEGRATION_GUIDE.md        # This file
```

## Key Integration Points

### 1. Main Application Entry Point (`main.py`)

**Purpose**: CLI interface and command routing
**Key Features**:
- Click-based command line interface
- Rich terminal output with colors and formatting
- Interactive and non-interactive modes
- Auto-completion support
- Comprehensive error handling

**Integration Patterns**:
```python
# Adding new CLI commands
@cli.command()
@click.argument('param')
@click.option('--option', help='Description')
@click.pass_context
def new_command(ctx, param, option):
    app: AdaptiveLearningApp = ctx.obj['app']
    app.handle_new_command(param, option)
```

### 2. Application Coordinator (`app.py`)

**Purpose**: Orchestrates all services and manages application lifecycle
**Key Features**:
- Service initialization and coordination
- Session management
- Progress tracking
- Rich UI components

**Integration Patterns**:
```python
# Adding new service integrations
def __init__(self, ...):
    # Initialize new service
    self.new_service = NewService(
        db_manager=self.db_manager,
        config=self.config
    )
    
# Adding new functionality
def new_feature(self, parameters):
    try:
        result = self.new_service.process(parameters)
        self._display_results(result)
    except Exception as e:
        self.logger.error(f"Feature error: {str(e)}")
        self.console.print(f"[red]Error: {str(e)}[/red]")
```

### 3. Service Layer Integration

#### Curriculum Service (`curriculum_service.py`)
**Purpose**: Manages learning paths, topics, and educational structure
**Key Integration Points**:

```python
# Extending curriculum functionality
class CustomCurriculumService(CurriculumService):
    def add_custom_feature(self, params):
        # Custom curriculum logic
        pass
        
# Service dependencies
def __init__(self, db_manager, config):
    self.db_manager = db_manager  # Database access
    self.config = config          # Configuration
    self.logger = get_logger(__name__)  # Logging
```

#### Content Service (`content_service.py`)
**Purpose**: Manages problems, concepts, and content delivery
**Key Integration Points**:

```python
# Content customization
def get_personalized_content(self, user_profile, criteria):
    # Custom content selection logic
    content = self._base_content_selection(criteria)
    return self._personalize_for_user(content, user_profile)

# New content types
def handle_new_content_type(self, content_type, parameters):
    handlers = {
        'interactive': self._handle_interactive_content,
        'video': self._handle_video_content,
        'simulation': self._handle_simulation_content
    }
    return handlers.get(content_type, self._handle_default)(parameters)
```

### 4. Configuration Integration (`config_manager.py`)

**Adding New Configuration Sections**:
```python
@dataclass
class NewFeatureConfig:
    enabled: bool = True
    setting1: str = "default"
    setting2: int = 42

# In ConfigManager._load_default_config():
self.config['new_feature'] = asdict(NewFeatureConfig())

# Usage in services:
config_manager = ConfigManager()
feature_config = config_manager.get('new_feature')
```

**Environment Variable Integration**:
```python
# Add to ConfigManager._load_environment_config():
f'{env_prefix}NEW_FEATURE_ENABLED': ('new_feature', 'enabled'),
f'{env_prefix}NEW_SETTING': ('new_feature', 'setting1'),
```

### 5. Logging Integration (`logging_config.py`)

**Adding Custom Loggers**:
```python
# Specialized logger for new feature
class NewFeatureLogger:
    def __init__(self):
        self.logger = get_logger("new_feature")
        # Custom handler setup if needed
        
    def log_custom_event(self, event_data):
        self.logger.info(f"Custom event: {event_data}")

# Performance logging
from utils.logging_config import perf_logger

def expensive_operation():
    perf_logger.start_timer("expensive_op")
    # ... operation logic ...
    duration = perf_logger.end_timer("expensive_op")
    return duration
```

## Database Integration Patterns

### Model Integration
```python
# In models/
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class NewModel:
    id: Optional[str] = None
    name: str = ""
    created_at: Optional[datetime] = None
    data: Dict[str, Any] = None
```

### Service Database Access
```python
# In services/
def get_new_model_data(self, model_id: str):
    try:
        return self.db_manager.get_new_model(model_id)
    except Exception as e:
        self.logger.error(f"Database error: {str(e)}")
        raise
```

## CLI Extension Patterns

### Adding New Commands
```python
# In main.py, add to cli group:
@cli.command()
@click.argument('required_param')
@click.option('--optional', default='default', help='Optional parameter')
@click.pass_context
def new_command(ctx, required_param, optional):
    """New command description."""
    app = ctx.obj['app']
    try:
        result = app.handle_new_command(required_param, optional)
        console.print(f"[green]Success: {result}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
```

### Auto-completion Integration
```python
# In utils/cli_completion.py:
COMMANDS['new_command'] = {
    'options': ['--optional'],
    'choices': {
        '--optional': ['choice1', 'choice2', 'choice3']
    }
}

# Update completion functions:
def complete_new_param(ctx, param, incomplete):
    return [item for item in NEW_PARAM_OPTIONS if item.startswith(incomplete)]
```

## Rich UI Integration

### Creating Custom Display Components
```python
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

def create_custom_display(self, data):
    """Create rich display for custom data."""
    table = Table(title="Custom Data Display")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in data.items():
        table.add_row(key, str(value))
    
    panel = Panel(table, title="Results", border_style="bright_blue")
    self.console.print(panel)
```

### Interactive Components
```python
def interactive_feature(self):
    """Interactive feature with user input."""
    while True:
        try:
            user_input = self.console.input("[bold cyan]Enter command>[/bold cyan] ")
            
            if user_input.lower() == 'quit':
                break
                
            result = self._process_interactive_input(user_input)
            self.console.print(f"[green]Result: {result}[/green]")
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted[/yellow]")
            break
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")
```

## Testing Integration

### Service Testing Pattern
```python
import pytest
from unittest.mock import Mock, patch

class TestNewService:
    @pytest.fixture
    def mock_db_manager(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db_manager):
        config = {'test_setting': 'test_value'}
        return NewService(mock_db_manager, config)
    
    def test_new_functionality(self, service):
        # Test implementation
        result = service.new_method('test_input')
        assert result == 'expected_output'
```

### CLI Testing Pattern
```python
from click.testing import CliRunner
from main import cli

def test_new_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['new-command', 'test-param'])
    
    assert result.exit_code == 0
    assert 'expected output' in result.output
```

## Error Handling Patterns

### Service-Level Error Handling
```python
def service_method(self, params):
    try:
        # Main logic
        result = self._core_processing(params)
        return result
        
    except ValidationError as e:
        self.logger.warning(f"Validation error: {str(e)}")
        raise ServiceError(f"Invalid input: {str(e)}")
        
    except DatabaseError as e:
        self.logger.error(f"Database error: {str(e)}")
        raise ServiceError("Data access failed")
        
    except Exception as e:
        self.logger.error(f"Unexpected error in {self.__class__.__name__}: {str(e)}")
        raise ServiceError("Internal service error")
```

### CLI Error Handling
```python
@cli.command()
@click.pass_context
def command_with_error_handling(ctx):
    app = ctx.obj['app']
    
    try:
        result = app.risky_operation()
        console.print(f"[green]Success: {result}[/green]")
        
    except ServiceError as e:
        console.print(f"[red]Service Error: {str(e)}[/red]")
        if ctx.obj['debug']:
            console.print_exception()
            
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        if ctx.obj['debug']:
            console.print_exception()
        sys.exit(1)
```

## Performance Optimization

### Caching Integration
```python
from functools import lru_cache
from datetime import datetime, timedelta

class ServiceWithCaching:
    def __init__(self):
        self.cache_ttl = timedelta(minutes=30)
        self._cache_timestamps = {}
    
    @lru_cache(maxsize=100)
    def cached_expensive_operation(self, key):
        # Expensive operation
        return self._expensive_computation(key)
    
    def get_with_ttl_cache(self, key):
        cache_key = f"ttl_{key}"
        if (cache_key in self._cache_timestamps and 
            datetime.now() - self._cache_timestamps[cache_key] < self.cache_ttl):
            return self.cached_expensive_operation(key)
        
        # Refresh cache
        result = self.cached_expensive_operation(key)
        self._cache_timestamps[cache_key] = datetime.now()
        return result
```

## Deployment Integration

### Packaging Extensions
```python
# In setup.py, add entry points for plugins:
entry_points={
    "console_scripts": [
        "adaptive-learning=main:main",
    ],
    "adaptive_learning.plugins": [
        "new_plugin = my_package.plugin:PluginClass",
    ],
}
```

### Configuration for Deployment
```python
# Environment-specific configuration
def get_deployment_config(environment):
    base_config = get_base_config()
    
    if environment == 'production':
        base_config.update({
            'logging': {'level': 'WARNING'},
            'debug': False,
            'performance': {'enable_caching': True}
        })
    elif environment == 'development':
        base_config.update({
            'logging': {'level': 'DEBUG'},
            'debug': True
        })
    
    return base_config
```

## Extension Points Summary

1. **CLI Commands**: Add new commands in `main.py`
2. **Services**: Create new services following the pattern in `services/`
3. **Models**: Add data models in `models/`
4. **Configuration**: Extend `config_manager.py` for new settings
5. **Logging**: Add specialized loggers in `logging_config.py`
6. **UI Components**: Create rich displays using established patterns
7. **Database**: Extend database operations in `database_manager.py`
8. **Auto-completion**: Update `cli_completion.py` for new commands

## Best Practices

1. **Error Handling**: Always wrap operations in try-catch blocks
2. **Logging**: Use structured logging with appropriate levels
3. **Configuration**: Make features configurable through config files
4. **Testing**: Write tests for all new functionality
5. **Documentation**: Update this guide when adding new integration points
6. **Performance**: Consider caching for expensive operations
7. **User Experience**: Provide clear feedback and progress indicators

## Memory Integration Points

All integration work is coordinated through the Claude Flow memory system:

- Pre-task hooks: Initialize work context
- Post-edit hooks: Document changes and decisions  
- Post-task hooks: Finalize and export integration points
- Memory storage: `.swarm/memory.db` contains all coordination data

The system is designed to be both powerful and extensible while maintaining clean separation of concerns and excellent user experience.