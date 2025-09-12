#!/usr/bin/env python3
"""
Plugin System Architecture - Extensible plugin management

This module provides:
- Dynamic plugin loading and management
- Plugin lifecycle management
- Dependency resolution
- Security and sandboxing
- Plugin registry and discovery
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Any, Set, Type, Union
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
import json
import hashlib
from enum import Enum

from ..commands.base import BaseCommand


class PluginState(Enum):
    """Plugin states"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginInfo:
    """Plugin information and metadata"""
    name: str
    version: str
    description: str
    author: str = ""
    email: str = ""
    website: str = ""
    license: str = ""
    dependencies: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    min_cli_version: str = "1.0.0"
    max_cli_version: str = "*"
    python_requires: str = ">=3.8"
    platforms: List[str] = field(default_factory=lambda: ["linux", "darwin", "win32"])
    

@dataclass
class PluginManifest:
    """Plugin manifest with file information"""
    info: PluginInfo
    file_path: Path
    module_name: str
    checksum: str
    state: PluginState = PluginState.DISCOVERED
    error_message: Optional[str] = None
    load_time: Optional[float] = None
    

class PluginInterface(ABC):
    """Abstract base class for all plugins"""
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Get plugin information
        
        Returns:
            Plugin information object
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin
        
        Args:
            config: Plugin configuration
            
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup plugin resources
        
        Returns:
            True if cleanup successful
        """
        pass
    
    def get_commands(self) -> List[BaseCommand]:
        """Get commands provided by this plugin
        
        Returns:
            List of command instances
        """
        return []
    
    def get_hooks(self) -> Dict[str, callable]:
        """Get hooks provided by this plugin
        
        Returns:
            Dictionary mapping hook names to callable functions
        """
        return {}
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation error messages
        """
        return []


class PluginManager:
    """Plugin manager for loading and managing plugins"""
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """Initialize plugin manager
        
        Args:
            plugin_dirs: List of plugin directories to search
        """
        self.logger = logging.getLogger(__name__)
        
        # Plugin directories
        default_dirs = [
            "~/.curriculum-cli/plugins",
            "./plugins",
            "/usr/local/share/curriculum-cli/plugins",
            "/usr/share/curriculum-cli/plugins"
        ]
        self.plugin_dirs = [Path(d).expanduser() for d in (plugin_dirs or default_dirs)]
        
        # Plugin registry
        self.manifests: Dict[str, PluginManifest] = {}
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        
        # Dependency graph
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        # Security settings
        self.sandbox_enabled = True
        self.allowed_imports: Set[str] = {
            'os', 'sys', 'json', 'yaml', 'csv', 'sqlite3',
            'requests', 'urllib', 'pathlib', 'datetime',
            'logging', 'argparse', 'typing', 'dataclasses'
        }
        
        # Create plugin directories
        for plugin_dir in self.plugin_dirs:
            plugin_dir.mkdir(parents=True, exist_ok=True)
    
    def discover_plugins(self) -> List[PluginManifest]:
        """Discover plugins in configured directories
        
        Returns:
            List of discovered plugin manifests
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            # Look for Python files
            for plugin_file in plugin_dir.rglob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                
                try:
                    manifest = self._create_manifest_from_file(plugin_file)
                    if manifest:
                        discovered.append(manifest)
                        self.manifests[manifest.info.name] = manifest
                except Exception as e:
                    self.logger.warning(f"Failed to discover plugin {plugin_file}: {e}")
            
            # Look for plugin packages
            for plugin_package in plugin_dir.iterdir():
                if not plugin_package.is_dir() or plugin_package.name.startswith("_"):
                    continue
                
                init_file = plugin_package / "__init__.py"
                if init_file.exists():
                    try:
                        manifest = self._create_manifest_from_package(plugin_package)
                        if manifest:
                            discovered.append(manifest)
                            self.manifests[manifest.info.name] = manifest
                    except Exception as e:
                        self.logger.warning(f"Failed to discover plugin package {plugin_package}: {e}")
        
        self.logger.info(f"Discovered {len(discovered)} plugins")
        return discovered
    
    def _create_manifest_from_file(self, plugin_file: Path) -> Optional[PluginManifest]:
        """Create plugin manifest from a Python file
        
        Args:
            plugin_file: Path to plugin file
            
        Returns:
            Plugin manifest or None if invalid
        """
        # Calculate file checksum
        with open(plugin_file, 'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest()
        
        # Try to load module spec
        module_name = f"plugin_{plugin_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        
        if not spec or not spec.loader:
            return None
        
        # Load module to extract plugin info
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for plugin class
            plugin_class = None
            for name, obj in module.__dict__.items():
                if (isinstance(obj, type) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                return None
            
            # Get plugin info
            plugin_instance = plugin_class()
            plugin_info = plugin_instance.get_info()
            
            return PluginManifest(
                info=plugin_info,
                file_path=plugin_file,
                module_name=module_name,
                checksum=checksum
            )
            
        except Exception as e:
            self.logger.debug(f"Failed to load plugin info from {plugin_file}: {e}")
            return None
    
    def _create_manifest_from_package(self, package_dir: Path) -> Optional[PluginManifest]:
        """Create plugin manifest from a package directory
        
        Args:
            package_dir: Path to plugin package
            
        Returns:
            Plugin manifest or None if invalid
        """
        # Look for plugin.json manifest file
        manifest_file = package_dir / "plugin.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r') as f:
                    manifest_data = json.load(f)
                
                plugin_info = PluginInfo(**manifest_data)
                
                # Calculate package checksum (simplified)
                init_file = package_dir / "__init__.py"
                with open(init_file, 'rb') as f:
                    checksum = hashlib.md5(f.read()).hexdigest()
                
                return PluginManifest(
                    info=plugin_info,
                    file_path=init_file,
                    module_name=package_dir.name,
                    checksum=checksum
                )
                
            except Exception as e:
                self.logger.debug(f"Failed to load package manifest from {package_dir}: {e}")
        
        # Fallback to loading from __init__.py
        return self._create_manifest_from_file(package_dir / "__init__.py")
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin
        
        Args:
            plugin_name: Name of plugin to load
            
        Returns:
            True if loaded successfully
        """
        if plugin_name in self.loaded_plugins:
            return True
        
        manifest = self.manifests.get(plugin_name)
        if not manifest:
            self.logger.error(f"Plugin {plugin_name} not found")
            return False
        
        try:
            # Load dependencies first
            for dep in manifest.info.dependencies:
                if not self.load_plugin(dep):
                    self.logger.error(f"Failed to load dependency {dep} for plugin {plugin_name}")
                    return False
            
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(
                manifest.module_name, 
                manifest.file_path
            )
            
            if not spec or not spec.loader:
                raise ImportError(f"Cannot load module spec for {plugin_name}")
            
            module = importlib.util.module_from_spec(spec)
            
            # Security check: validate imports
            if self.sandbox_enabled:
                self._validate_plugin_security(manifest.file_path)
            
            spec.loader.exec_module(module)
            
            # Find and instantiate plugin class
            plugin_class = None
            for name, obj in module.__dict__.items():
                if (isinstance(obj, type) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise ValueError(f"No plugin class found in {plugin_name}")
            
            # Create plugin instance
            plugin_instance = plugin_class()
            
            # Initialize plugin
            config = self.plugin_configs.get(plugin_name, {})
            if not plugin_instance.initialize(config):
                raise RuntimeError(f"Plugin {plugin_name} initialization failed")
            
            # Store loaded plugin
            self.loaded_plugins[plugin_name] = plugin_instance
            manifest.state = PluginState.LOADED
            
            self.logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            manifest.state = PluginState.ERROR
            manifest.error_message = str(e)
            return False
    
    def _validate_plugin_security(self, plugin_file: Path):
        """Validate plugin security constraints
        
        Args:
            plugin_file: Path to plugin file
            
        Raises:
            SecurityError: If plugin violates security constraints
        """
        with open(plugin_file, 'r') as f:
            content = f.read()
        
        # Simple security checks
        dangerous_patterns = [
            'exec(', 'eval(', '__import__(',
            'subprocess.', 'os.system(',
            'open(', 'file(', 'input(',
            'raw_input('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content:
                raise SecurityError(f"Potentially dangerous pattern found: {pattern}")
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            True if unloaded successfully
        """
        if plugin_name not in self.loaded_plugins:
            return True
        
        try:
            plugin = self.loaded_plugins[plugin_name]
            plugin.cleanup()
            
            del self.loaded_plugins[plugin_name]
            
            if plugin_name in self.manifests:
                self.manifests[plugin_name].state = PluginState.DISCOVERED
            
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> List[PluginInterface]:
        """Load all discovered plugins
        
        Returns:
            List of successfully loaded plugin instances
        """
        # First, discover plugins
        self.discover_plugins()
        
        # Build dependency graph
        self._build_dependency_graph()
        
        # Load plugins in dependency order
        load_order = self._resolve_dependency_order()
        
        loaded_plugins = []
        for plugin_name in load_order:
            if self.load_plugin(plugin_name):
                loaded_plugins.append(self.loaded_plugins[plugin_name])
        
        return loaded_plugins
    
    def _build_dependency_graph(self):
        """Build plugin dependency graph"""
        self.dependency_graph.clear()
        
        for manifest in self.manifests.values():
            deps = set(manifest.info.dependencies)
            self.dependency_graph[manifest.info.name] = deps
    
    def _resolve_dependency_order(self) -> List[str]:
        """Resolve plugin load order based on dependencies
        
        Returns:
            List of plugin names in load order
            
        Raises:
            ValueError: If circular dependencies detected
        """
        # Topological sort using Kahn's algorithm
        in_degree = {}
        for plugin in self.dependency_graph:
            in_degree[plugin] = 0
        
        for plugin, deps in self.dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [plugin for plugin, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            plugin = queue.pop(0)
            result.append(plugin)
            
            for dep in self.dependency_graph[plugin]:
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)
        
        if len(result) != len(self.dependency_graph):
            raise ValueError("Circular dependency detected in plugins")
        
        return result
    
    def get_plugin_commands(self) -> List[BaseCommand]:
        """Get all commands from loaded plugins
        
        Returns:
            List of command instances
        """
        commands = []
        for plugin in self.loaded_plugins.values():
            commands.extend(plugin.get_commands())
        return commands
    
    def get_plugin_hooks(self) -> Dict[str, List[callable]]:
        """Get all hooks from loaded plugins
        
        Returns:
            Dictionary mapping hook names to list of callable functions
        """
        hooks = {}
        for plugin in self.loaded_plugins.values():
            plugin_hooks = plugin.get_hooks()
            for hook_name, hook_func in plugin_hooks.items():
                if hook_name not in hooks:
                    hooks[hook_name] = []
                hooks[hook_name].append(hook_func)
        return hooks
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """Set configuration for a plugin
        
        Args:
            plugin_name: Name of plugin
            config: Configuration dictionary
        """
        self.plugin_configs[plugin_name] = config
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a plugin
        
        Args:
            plugin_name: Name of plugin
            
        Returns:
            Plugin information or None if not found
        """
        manifest = self.manifests.get(plugin_name)
        return manifest.info if manifest else None
    
    def list_plugins(self) -> List[PluginManifest]:
        """Get list of all plugin manifests
        
        Returns:
            List of plugin manifests
        """
        return list(self.manifests.values())
    
    def install_plugin(self, plugin_source: Union[str, Path]) -> bool:
        """Install a plugin from source
        
        Args:
            plugin_source: Path to plugin file or URL
            
        Returns:
            True if installed successfully
        """
        # TODO: Implement plugin installation from various sources
        # - Local file/directory
        # - Git repository
        # - Package registry
        # - URL download
        pass
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin
        
        Args:
            plugin_name: Name of plugin to uninstall
            
        Returns:
            True if uninstalled successfully
        """
        # First unload the plugin
        self.unload_plugin(plugin_name)
        
        # Remove plugin files
        manifest = self.manifests.get(plugin_name)
        if manifest:
            try:
                if manifest.file_path.is_file():
                    manifest.file_path.unlink()
                elif manifest.file_path.parent.name == plugin_name:
                    # Remove entire plugin directory
                    import shutil
                    shutil.rmtree(manifest.file_path.parent)
                
                del self.manifests[plugin_name]
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
        
        return False


class SecurityError(Exception):
    """Raised when plugin violates security constraints"""
    pass
