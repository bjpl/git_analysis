"""
Windows DPAPI Encryption Manager

Provides secure encryption/decryption of API keys using Windows Data Protection API.
Falls back to base64 encoding on non-Windows systems for portability.
"""

import os
import sys
import base64
import json
import logging
from typing import Dict, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Manages secure encryption and decryption of sensitive configuration data."""
    
    def __init__(self):
        self.is_windows = sys.platform.startswith('win')
        self.dpapi_available = False
        
        if self.is_windows:
            try:
                import win32crypt
                self.dpapi_available = True
                self.win32crypt = win32crypt
                logger.info("Windows DPAPI encryption available")
            except ImportError:
                logger.warning("Windows DPAPI not available, falling back to base64 encoding")
        
    def encrypt_data(self, data: Union[str, Dict], description: str = "API Key") -> str:
        """
        Encrypt sensitive data using Windows DPAPI or fallback encoding.
        
        Args:
            data: String or dictionary to encrypt
            description: Description for DPAPI blob
            
        Returns:
            Encrypted data as base64 string
        """
        try:
            # Convert dict to JSON string if needed
            if isinstance(data, dict):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
            
            data_bytes = data_str.encode('utf-8')
            
            if self.dpapi_available:
                # Use Windows DPAPI for secure encryption
                encrypted_data = self.win32crypt.CryptProtectData(
                    data_bytes,
                    description,
                    None,  # Optional entropy
                    None,  # Reserved
                    None,  # Prompt struct
                    0      # Flags
                )
                return base64.b64encode(encrypted_data).decode('utf-8')
            else:
                # Fallback: Base64 encoding (not secure, but functional)
                logger.warning("Using base64 encoding - data is NOT securely encrypted!")
                return base64.b64encode(data_bytes).decode('utf-8')
                
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt data: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> Union[str, Dict]:
        """
        Decrypt data that was encrypted with encrypt_data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted data as string or dictionary
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            if self.dpapi_available:
                # Use Windows DPAPI for decryption
                decrypted_data, description = self.win32crypt.CryptUnprotectData(
                    encrypted_bytes,
                    None,  # Optional entropy
                    None,  # Reserved
                    None,  # Prompt struct
                    0      # Flags
                )
                decrypted_str = decrypted_data.decode('utf-8')
            else:
                # Fallback: Base64 decoding
                decrypted_str = encrypted_bytes.decode('utf-8')
            
            # Try to parse as JSON first
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
                
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Failed to decrypt data: {e}")
    
    def is_encrypted_data(self, data: str) -> bool:
        """
        Check if a string appears to be encrypted data.
        
        Args:
            data: String to check
            
        Returns:
            True if data appears to be encrypted
        """
        try:
            # Check if it's valid base64
            decoded = base64.b64decode(data.encode('utf-8'))
            
            if self.dpapi_available:
                # Try to decrypt with DPAPI
                try:
                    self.win32crypt.CryptUnprotectData(
                        decoded, None, None, None, 0
                    )
                    return True
                except:
                    return False
            else:
                # For non-Windows, assume base64-encoded data is encrypted
                return len(decoded) > 10 and all(32 <= b <= 126 for b in decoded[:10])
                
        except:
            return False
    
    def create_secure_backup(self, data: Dict, backup_path: Path) -> bool:
        """
        Create an encrypted backup of configuration data.
        
        Args:
            data: Configuration dictionary to backup
            backup_path: Path where backup will be saved
            
        Returns:
            True if backup was created successfully
        """
        try:
            encrypted_data = self.encrypt_data(data, "Config Backup")
            backup_content = {
                "version": "1.0",
                "created_at": str(Path(__file__).stat().st_mtime),
                "encrypted_config": encrypted_data,
                "encryption_method": "DPAPI" if self.dpapi_available else "Base64"
            }
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_content, f, indent=2)
            
            logger.info(f"Secure backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create secure backup: {e}")
            return False
    
    def restore_from_backup(self, backup_path: Path) -> Optional[Dict]:
        """
        Restore configuration from an encrypted backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Restored configuration dictionary or None if failed
        """
        try:
            if not backup_path.exists():
                logger.warning(f"Backup file not found: {backup_path}")
                return None
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = json.load(f)
            
            encrypted_data = backup_content.get("encrypted_config")
            if not encrypted_data:
                logger.error("Invalid backup file format")
                return None
            
            restored_data = self.decrypt_data(encrypted_data)
            logger.info(f"Configuration restored from backup: {backup_path}")
            return restored_data
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return None


class EncryptionError(Exception):
    """Custom exception for encryption-related errors."""
    pass