"""
Security module for Git Tracker
================================
Handles secure token storage, input validation, and command sanitization.
"""

import os
import re
import json
import shlex
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64


class SecureConfigManager:
    """Manages secure storage and retrieval of sensitive configuration data."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize secure config manager with encrypted storage."""
        self.config_dir = config_dir or Path.home() / '.git_tracker'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / 'secure_config.enc'
        self.key_file = self.config_dir / '.key'
        self.cipher = self._get_or_create_cipher()

    def _get_or_create_cipher(self) -> Fernet:
        """Get existing cipher or create new one with secure key derivation."""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate key from machine-specific seed
            machine_id = self._get_machine_id()
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=machine_id.encode()[:16].ljust(16, b'0'),
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))

            # Store key with restricted permissions
            with open(self.key_file, 'wb') as f:
                f.write(key)

            # Set file permissions (Unix-like systems)
            try:
                os.chmod(self.key_file, 0o600)
            except:
                pass  # Windows doesn't support chmod

        return Fernet(key)

    def _get_machine_id(self) -> str:
        """Generate unique machine identifier for key derivation."""
        # Combine multiple system attributes for uniqueness
        factors = [
            os.environ.get('COMPUTERNAME', ''),
            os.environ.get('USERNAME', ''),
            str(Path.home()),
        ]
        combined = '|'.join(factors)
        return hashlib.sha256(combined.encode()).hexdigest()

    def store_token(self, service: str, token: str) -> None:
        """Securely store an API token."""
        config = self._load_config()
        config['tokens'] = config.get('tokens', {})
        config['tokens'][service] = token
        self._save_config(config)

    def get_token(self, service: str) -> Optional[str]:
        """Retrieve a stored API token."""
        config = self._load_config()
        return config.get('tokens', {}).get(service)

    def remove_token(self, service: str) -> bool:
        """Remove a stored token."""
        config = self._load_config()
        if 'tokens' in config and service in config['tokens']:
            del config['tokens'][service]
            self._save_config(config)
            return True
        return False

    def _load_config(self) -> Dict[str, Any]:
        """Load and decrypt configuration."""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Encrypt and save configuration."""
        json_data = json.dumps(config)
        encrypted_data = self.cipher.encrypt(json_data.encode())

        with open(self.config_file, 'wb') as f:
            f.write(encrypted_data)

        # Set restricted permissions
        try:
            os.chmod(self.config_file, 0o600)
        except:
            pass


class CommandSanitizer:
    """Validates and sanitizes shell commands to prevent injection attacks."""

    # Whitelist of allowed git commands
    ALLOWED_GIT_COMMANDS = {
        'log', 'show', 'diff', 'status', 'branch', 'tag',
        'ls-files', 'ls-tree', 'rev-list', 'rev-parse',
        'shortlog', 'describe', 'remote', 'config'
    }

    # Regex patterns for validation
    PATTERNS = {
        'sha': re.compile(r'^[a-f0-9]{40}$'),
        'branch': re.compile(r'^[a-zA-Z0-9/_.-]+$'),
        'file_path': re.compile(r'^[a-zA-Z0-9/_.-]+$'),
        'author': re.compile(r'^[a-zA-Z0-9\s.-]+$'),
    }

    @classmethod
    def validate_git_command(cls, command: str, args: List[str]) -> bool:
        """Validate git command and arguments."""
        if command not in cls.ALLOWED_GIT_COMMANDS:
            raise ValueError(f"Git command '{command}' not allowed")

        # Additional validation based on command
        if command == 'log' and '--format' in args:
            # Ensure format string doesn't contain dangerous characters
            format_idx = args.index('--format') + 1
            if format_idx < len(args):
                format_str = args[format_idx]
                if any(char in format_str for char in ['$', '`', ';', '|', '&']):
                    raise ValueError("Invalid format string")

        return True

    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """Sanitize file path to prevent directory traversal."""
        # Remove any directory traversal attempts
        path = os.path.normpath(path)
        path = path.replace('..', '')

        # Ensure path doesn't start with system directories
        forbidden_prefixes = ['/etc', '/sys', '/proc', 'C:\\Windows', 'C:\\System']
        for prefix in forbidden_prefixes:
            if path.startswith(prefix):
                raise ValueError(f"Access to {prefix} is forbidden")

        return path

    @classmethod
    def quote_argument(cls, arg: str) -> str:
        """Safely quote shell argument."""
        return shlex.quote(arg)

    @classmethod
    def build_safe_command(cls, base_command: List[str], user_args: List[str] = None) -> List[str]:
        """Build safe command list with validated arguments."""
        safe_command = base_command.copy()

        if user_args:
            for arg in user_args:
                # Skip empty arguments
                if not arg:
                    continue

                # Quote arguments that might contain spaces or special chars
                if ' ' in arg or any(c in arg for c in ['*', '?', '[', ']']):
                    arg = cls.quote_argument(arg)

                safe_command.append(arg)

        return safe_command


class InputValidator:
    """Validates user inputs to prevent various attacks."""

    @staticmethod
    def validate_username(username: str) -> str:
        """Validate GitHub username."""
        pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$')
        if not pattern.match(username):
            raise ValueError(f"Invalid GitHub username: {username}")
        return username

    @staticmethod
    def validate_repo_name(repo_name: str) -> str:
        """Validate repository name."""
        pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        if not pattern.match(repo_name):
            raise ValueError(f"Invalid repository name: {repo_name}")
        return repo_name

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate GitHub URL."""
        pattern = re.compile(
            r'^https?://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9._-]+(?:\.git)?$'
        )
        if not pattern.match(url):
            raise ValueError(f"Invalid GitHub URL: {url}")
        return url

    @staticmethod
    def validate_sha(sha: str) -> str:
        """Validate git SHA."""
        pattern = re.compile(r'^[a-f0-9]{40}$')
        if not pattern.match(sha):
            raise ValueError(f"Invalid git SHA: {sha}")
        return sha

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize text for HTML output."""
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '&': '&amp;'
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text


class RateLimiter:
    """Implements rate limiting for API calls."""

    def __init__(self, max_calls: int = 60, window_seconds: int = 3600):
        """Initialize rate limiter."""
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = []

    def can_make_request(self) -> bool:
        """Check if request can be made within rate limits."""
        import time
        now = time.time()

        # Remove old calls outside the window
        self.calls = [t for t in self.calls if now - t < self.window_seconds]

        # Check if we can make a new call
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True

        return False

    def time_until_reset(self) -> float:
        """Get seconds until rate limit resets."""
        if not self.calls:
            return 0

        import time
        oldest_call = min(self.calls)
        reset_time = oldest_call + self.window_seconds
        return max(0, reset_time - time.time())


# Example usage and testing
if __name__ == "__main__":
    # Test secure config manager
    config_mgr = SecureConfigManager()

    # Store a token securely
    config_mgr.store_token('github', 'ghp_test_token_12345')

    # Retrieve the token
    token = config_mgr.get_token('github')
    print(f"Retrieved token: {token[:10]}..." if token else "No token found")

    # Test command sanitizer
    sanitizer = CommandSanitizer()

    # Validate git command
    try:
        sanitizer.validate_git_command('log', ['--oneline', '-n', '10'])
        print("Git command validated successfully")
    except ValueError as e:
        print(f"Validation error: {e}")

    # Test input validator
    validator = InputValidator()

    try:
        username = validator.validate_username("bjpl")
        print(f"Valid username: {username}")
    except ValueError as e:
        print(f"Invalid username: {e}")