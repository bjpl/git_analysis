"""
Auto-updater module for checking and applying application updates from GitHub releases.
"""

import os
import sys
import json
import hashlib
import shutil
import tempfile
import threading
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, Tuple
from urllib.parse import urlparse
import tkinter as tk
from tkinter import messagebox
import requests
from packaging import version


class UpdateError(Exception):
    """Custom exception for update-related errors."""
    pass


class UpdateInfo:
    """Information about an available update."""
    
    def __init__(self, version: str, release_data: Dict[str, Any]):
        self.version = version
        self.release_data = release_data
        
    @property
    def name(self) -> str:
        return self.release_data.get("name", f"Version {self.version}")
    
    @property
    def body(self) -> str:
        return self.release_data.get("body", "No release notes available.")
    
    @property
    def html_url(self) -> str:
        return self.release_data.get("html_url", "")
    
    @property
    def published_at(self) -> str:
        return self.release_data.get("published_at", "")
    
    @property
    def prerelease(self) -> bool:
        return self.release_data.get("prerelease", False)
    
    @property
    def assets(self) -> list:
        return self.release_data.get("assets", [])


class AutoUpdater:
    """Auto-updater that checks for updates from GitHub releases."""
    
    def __init__(self, config_path: Optional[Path] = None, current_version: str = "0.1.0"):
        self.current_version = current_version
        self.config_path = config_path or Path("update_config.json")
        self.config = self._load_config()
        
        # State
        self._last_check = None
        self._checking_for_updates = False
        self._downloading = False
        self._download_thread = None
        
        # Callbacks
        self.on_update_available: Optional[Callable[[UpdateInfo], None]] = None
        self.on_update_progress: Optional[Callable[[int], None]] = None
        self.on_update_complete: Optional[Callable[[str], None]] = None
        self.on_update_error: Optional[Callable[[str], None]] = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load update configuration."""
        default_config = {
            "enabled": True,
            "check_on_startup": True,
            "check_frequency_hours": 24,
            "auto_download": False,
            "auto_install": False,
            "channel": "stable",
            "github_repo": "your-username/unsplash-image-search-gpt-description",
            "proxy_settings": {
                "enabled": False,
                "host": "",
                "port": 8080,
                "username": "",
                "password": ""
            },
            "backup_enabled": True,
            "max_backups": 3,
            "download_timeout": 300,
            "verify_checksums": True
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load update config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save update config: {e}")
    
    def is_enabled(self) -> bool:
        """Check if updater is enabled."""
        return self.config.get("enabled", True)
    
    def should_check_on_startup(self) -> bool:
        """Check if updates should be checked on application startup."""
        return self.config.get("check_on_startup", True) and self.is_enabled()
    
    def should_check_now(self) -> bool:
        """Check if it's time to check for updates based on frequency settings."""
        if not self.is_enabled():
            return False
        
        frequency_hours = self.config.get("check_frequency_hours", 24)
        if frequency_hours <= 0:
            return False
        
        if self._last_check is None:
            return True
        
        time_since_check = datetime.now() - self._last_check
        return time_since_check >= timedelta(hours=frequency_hours)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the updater."""
        self.config["enabled"] = enabled
        self.save_config()
    
    def set_check_on_startup(self, enabled: bool):
        """Enable or disable startup checking."""
        self.config["check_on_startup"] = enabled
        self.save_config()
    
    def set_auto_download(self, enabled: bool):
        """Enable or disable automatic downloading."""
        self.config["auto_download"] = enabled
        self.save_config()
    
    def check_for_updates(self, force: bool = False) -> Optional[UpdateInfo]:
        """
        Check for available updates.
        
        Args:
            force: If True, check even if frequency hasn't elapsed
            
        Returns:
            UpdateInfo if update available, None otherwise
        """
        if self._checking_for_updates:
            return None
        
        if not force and not self.should_check_now():
            return None
        
        if not self.is_enabled():
            return None
        
        self._checking_for_updates = True
        
        try:
            update_info = self._fetch_latest_release()
            self._last_check = datetime.now()
            
            if update_info and self._is_newer_version(update_info.version):
                if self.on_update_available:
                    self.on_update_available(update_info)
                return update_info
            
            return None
        
        except Exception as e:
            error_msg = f"Failed to check for updates: {str(e)}"
            if self.on_update_error:
                self.on_update_error(error_msg)
            else:
                print(error_msg)
            return None
        
        finally:
            self._checking_for_updates = False
    
    def check_for_updates_async(self, force: bool = False):
        """Check for updates in a background thread."""
        if self._checking_for_updates:
            return
        
        def check_thread():
            self.check_for_updates(force)
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def _fetch_latest_release(self) -> Optional[UpdateInfo]:
        """Fetch latest release information from GitHub."""
        repo = self.config.get("github_repo", "")
        if not repo:
            raise UpdateError("GitHub repository not configured")
        
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        channel = self.config.get("channel", "stable")
        
        # Setup session with proxy if configured
        session = requests.Session()
        if self.config.get("proxy_settings", {}).get("enabled"):
            proxy_config = self.config["proxy_settings"]
            proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
            session.proxies = {"http": proxy_url, "https": proxy_url}
            
            if proxy_config.get("username") and proxy_config.get("password"):
                session.auth = (proxy_config["username"], proxy_config["password"])
        
        # If beta channel, get all releases and find latest non-prerelease or prerelease
        if channel == "beta":
            url = f"https://api.github.com/repos/{repo}/releases"
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        if channel == "beta":
            releases = response.json()
            if not releases:
                return None
            # For beta channel, include prereleases
            latest_release = releases[0]  # First release (latest)
        else:
            # For stable channel, only get stable releases (GitHub API handles this)
            latest_release = response.json()
        
        tag_name = latest_release.get("tag_name", "")
        if not tag_name:
            return None
        
        # Remove 'v' prefix if present
        version_string = tag_name.lstrip("v")
        
        return UpdateInfo(version_string, latest_release)
    
    def _is_newer_version(self, new_version: str) -> bool:
        """Compare version numbers to determine if update is available."""
        try:
            return version.parse(new_version) > version.parse(self.current_version)
        except Exception:
            # Fallback to string comparison if version parsing fails
            return new_version != self.current_version
    
    def download_update(self, update_info: UpdateInfo, 
                       progress_callback: Optional[Callable[[int], None]] = None) -> Optional[str]:
        """
        Download update file.
        
        Args:
            update_info: Information about the update
            progress_callback: Callback for download progress (0-100)
            
        Returns:
            Path to downloaded file, or None if failed
        """
        if self._downloading:
            return None
        
        # Find appropriate asset to download
        asset = self._find_download_asset(update_info.assets)
        if not asset:
            raise UpdateError("No suitable download asset found")
        
        self._downloading = True
        
        try:
            return self._download_file(
                asset["browser_download_url"],
                asset["name"],
                asset.get("size", 0),
                progress_callback
            )
        finally:
            self._downloading = False
    
    def download_update_async(self, update_info: UpdateInfo,
                            progress_callback: Optional[Callable[[int], None]] = None,
                            completion_callback: Optional[Callable[[Optional[str]], None]] = None):
        """Download update in a background thread."""
        if self._downloading:
            return
        
        def download_thread():
            try:
                file_path = self.download_update(update_info, progress_callback)
                if completion_callback:
                    completion_callback(file_path)
            except Exception as e:
                error_msg = f"Failed to download update: {str(e)}"
                if self.on_update_error:
                    self.on_update_error(error_msg)
                if completion_callback:
                    completion_callback(None)
        
        self._download_thread = threading.Thread(target=download_thread, daemon=True)
        self._download_thread.start()
    
    def _find_download_asset(self, assets: list) -> Optional[Dict[str, Any]]:
        """Find the appropriate asset to download based on platform."""
        if not assets:
            return None
        
        platform = sys.platform.lower()
        
        # Priority order for different platforms
        if platform.startswith("win"):
            priorities = [".exe", ".msi", ".zip"]
        elif platform.startswith("darwin"):
            priorities = [".dmg", ".pkg", ".zip"]
        elif platform.startswith("linux"):
            priorities = [".AppImage", ".deb", ".rpm", ".tar.gz", ".zip"]
        else:
            priorities = [".zip", ".tar.gz"]
        
        # Try to find asset matching platform
        for priority in priorities:
            for asset in assets:
                name = asset.get("name", "").lower()
                if priority in name:
                    return asset
        
        # Fallback to first asset
        return assets[0] if assets else None
    
    def _download_file(self, url: str, filename: str, total_size: int,
                      progress_callback: Optional[Callable[[int], None]]) -> str:
        """Download file with progress tracking."""
        # Create temporary directory
        temp_dir = Path(tempfile.gettempdir()) / "app_updates"
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / filename
        
        # Setup session with proxy if configured
        session = requests.Session()
        if self.config.get("proxy_settings", {}).get("enabled"):
            proxy_config = self.config["proxy_settings"]
            proxy_url = f"http://{proxy_config['host']}:{proxy_config['port']}"
            session.proxies = {"http": proxy_url, "https": proxy_url}
            
            if proxy_config.get("username") and proxy_config.get("password"):
                session.auth = (proxy_config["username"], proxy_config["password"])
        
        # Download with progress tracking
        timeout = self.config.get("download_timeout", 300)
        response = session.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        
        downloaded = 0
        chunk_size = 8192
        
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback and total_size > 0:
                        progress = min(100, int((downloaded / total_size) * 100))
                        progress_callback(progress)
        
        return str(file_path)
    
    def verify_download(self, file_path: str, expected_hash: Optional[str] = None) -> bool:
        """Verify downloaded file integrity."""
        if not self.config.get("verify_checksums", True):
            return True
        
        if not expected_hash:
            # If no hash provided, just check if file exists and has content
            try:
                return Path(file_path).stat().st_size > 0
            except OSError:
                return False
        
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest().lower() == expected_hash.lower()
        
        except Exception as e:
            print(f"Verification failed: {e}")
            return False
    
    def create_backup(self) -> Optional[str]:
        """Create backup of current application."""
        if not self.config.get("backup_enabled", True):
            return None
        
        try:
            # Determine current executable path
            if getattr(sys, "frozen", False):
                current_exe = Path(sys.executable)
            else:
                # For development, backup the entire source directory
                current_exe = Path(__file__).parent.parent.parent
            
            # Create backup directory
            backup_dir = Path.home() / ".app_backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Clean old backups
            self._clean_old_backups(backup_dir)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{self.current_version}_{timestamp}"
            
            if current_exe.is_file():
                backup_path = backup_dir / f"{backup_name}{current_exe.suffix}"
                shutil.copy2(current_exe, backup_path)
            else:
                backup_path = backup_dir / backup_name
                shutil.copytree(current_exe, backup_path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            
            return str(backup_path)
        
        except Exception as e:
            print(f"Backup creation failed: {e}")
            return None
    
    def _clean_old_backups(self, backup_dir: Path):
        """Remove old backups to save space."""
        max_backups = self.config.get("max_backups", 3)
        if max_backups <= 0:
            return
        
        try:
            backup_items = []
            for item in backup_dir.iterdir():
                if item.name.startswith("backup_"):
                    backup_items.append((item.stat().st_mtime, item))
            
            # Sort by modification time (newest first)
            backup_items.sort(reverse=True)
            
            # Remove excess backups
            for _, backup_path in backup_items[max_backups:]:
                if backup_path.is_file():
                    backup_path.unlink()
                elif backup_path.is_dir():
                    shutil.rmtree(backup_path)
        
        except Exception as e:
            print(f"Backup cleanup failed: {e}")
    
    def apply_update(self, update_file: str, restart_app: bool = True) -> bool:
        """
        Apply the downloaded update.
        
        Args:
            update_file: Path to the downloaded update file
            restart_app: Whether to restart the application after update
            
        Returns:
            True if update was applied successfully
        """
        try:
            # Create backup first
            backup_path = self.create_backup()
            
            # Determine update method based on file type
            file_path = Path(update_file)
            
            if file_path.suffix.lower() == ".exe":
                return self._apply_exe_update(update_file, restart_app)
            elif file_path.suffix.lower() in [".zip", ".tar.gz"]:
                return self._apply_archive_update(update_file, restart_app)
            else:
                # Try to run as executable installer
                return self._apply_installer_update(update_file, restart_app)
        
        except Exception as e:
            error_msg = f"Failed to apply update: {str(e)}"
            if self.on_update_error:
                self.on_update_error(error_msg)
            return False
    
    def _apply_exe_update(self, update_file: str, restart_app: bool) -> bool:
        """Apply update from executable file."""
        if getattr(sys, "frozen", False):
            # Running as executable - replace current exe
            current_exe = Path(sys.executable)
            update_path = Path(update_file)
            
            # Create update script
            script_content = f'''
import os
import sys
import time
import shutil
from pathlib import Path

# Wait for main process to exit
time.sleep(2)

try:
    # Replace executable
    shutil.move(r"{update_path}", r"{current_exe}")
    
    if {restart_app}:
        # Restart application
        os.startfile(r"{current_exe}")
    
    print("Update applied successfully")
except Exception as e:
    print(f"Update failed: {{e}}")
    sys.exit(1)
'''
            
            script_path = Path(tempfile.gettempdir()) / "update_script.py"
            with open(script_path, "w") as f:
                f.write(script_content)
            
            # Run update script and exit
            subprocess.Popen([sys.executable, str(script_path)], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            if restart_app:
                sys.exit(0)
            return True
        else:
            # Development mode - just run the new executable
            if restart_app:
                subprocess.Popen([update_file])
                sys.exit(0)
            return True
    
    def _apply_archive_update(self, update_file: str, restart_app: bool) -> bool:
        """Apply update from archive file (zip/tar.gz)."""
        # For archive updates, we would extract and replace files
        # This is more complex and depends on the application structure
        # For now, just run as installer
        return self._apply_installer_update(update_file, restart_app)
    
    def _apply_installer_update(self, update_file: str, restart_app: bool) -> bool:
        """Apply update by running installer."""
        try:
            # Run the installer
            if sys.platform.startswith("win"):
                subprocess.Popen([update_file], shell=True)
            else:
                subprocess.Popen([update_file])
            
            if restart_app:
                sys.exit(0)
            return True
        
        except Exception as e:
            print(f"Failed to run installer: {e}")
            return False
    
    def rollback_update(self, backup_path: str) -> bool:
        """Rollback to previous version from backup."""
        try:
            backup = Path(backup_path)
            if not backup.exists():
                raise UpdateError("Backup not found")
            
            if getattr(sys, "frozen", False):
                current_exe = Path(sys.executable)
                
                if backup.is_file():
                    # Replace executable
                    shutil.move(backup, current_exe)
                else:
                    # Replace directory
                    app_dir = current_exe.parent
                    temp_dir = app_dir.parent / f"temp_{int(time.time())}"
                    shutil.move(app_dir, temp_dir)
                    shutil.move(backup, app_dir)
                    shutil.rmtree(temp_dir)
                
                # Restart application
                os.startfile(str(current_exe))
                sys.exit(0)
            
            return True
        
        except Exception as e:
            error_msg = f"Rollback failed: {str(e)}"
            if self.on_update_error:
                self.on_update_error(error_msg)
            return False
    
    def get_available_backups(self) -> list:
        """Get list of available backup versions."""
        backup_dir = Path.home() / ".app_backups"
        backups = []
        
        if not backup_dir.exists():
            return backups
        
        try:
            for item in backup_dir.iterdir():
                if item.name.startswith("backup_"):
                    parts = item.name.split("_")
                    if len(parts) >= 3:
                        version_part = parts[1]
                        timestamp_part = "_".join(parts[2:])
                        backups.append({
                            "path": str(item),
                            "version": version_part,
                            "timestamp": timestamp_part,
                            "created": datetime.fromtimestamp(item.stat().st_mtime)
                        })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
        
        except Exception as e:
            print(f"Failed to list backups: {e}")
        
        return backups