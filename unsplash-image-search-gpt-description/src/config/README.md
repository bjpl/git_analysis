# Secure Configuration Management System

## 🔐 Overview

This package provides enterprise-grade secure API key management for distributed executables with the following features:

- **Zero Hardcoded Secrets**: No API keys are ever embedded in the executable
- **Windows DPAPI Encryption**: Uses Windows Data Protection API for secure key storage
- **Real-time Key Validation**: Validates API keys before storing them
- **First-run Setup Wizard**: User-friendly configuration interface
- **Automatic Migration**: Seamlessly migrates from legacy configuration
- **Secure Storage**: Keys stored in user's AppData directory with proper permissions
- **Environment Variable Fallback**: Supports development workflows

## 🚀 Quick Start

```python
from src.config import ensure_secure_configuration

# This will show the setup wizard if needed
config_manager = ensure_secure_configuration()

if config_manager:
    api_keys = config_manager.get_api_keys()
    print(f"Unsplash Key: {api_keys['unsplash'][:10]}...")
    print(f"OpenAI Key: {api_keys['openai'][:10]}...")
```

## 📁 File Structure

```
src/config/
├── __init__.py                 # Package exports
├── secure_config_manager.py    # Main configuration manager
├── encryption_manager.py       # DPAPI encryption handling
├── key_validator.py           # Real-time API key validation
├── setup_wizard.py            # First-run setup wizard
├── migration_helper.py        # Legacy config migration
├── config_template.json       # Distribution template
└── README.md                  # This file
```

## 🛡️ Security Features

### Windows DPAPI Encryption

On Windows systems, API keys are encrypted using the Windows Data Protection API (DPAPI):

```python
from src.config import EncryptionManager

encryptor = EncryptionManager()
encrypted_key = encryptor.encrypt_data("your_api_key", "API Key")
decrypted_key = encryptor.decrypt_data(encrypted_key)
```

### Secure Storage Locations

Configuration is stored in platform-specific secure directories:

- **Windows**: `%LOCALAPPDATA%\UnsplashImageSearch\config.enc`
- **macOS**: `~/Library/Application Support/UnsplashImageSearch/config.enc`
- **Linux**: `~/.config/UnsplashImageSearch/config.enc`

### Permission Management

The configuration system automatically sets secure file permissions:
- Windows: Owner-only access using `icacls`
- Unix-like: 700 directory, 600 file permissions

## 🔑 API Key Validation

Real-time validation ensures keys work before storage:

```python
from src.config import APIKeyValidator
import asyncio

validator = APIKeyValidator()

# Validate individual keys
unsplash_result = await validator.validate_unsplash_key("your_key")
openai_result = await validator.validate_openai_key("your_key", "gpt-4o-mini")

# Validate all keys concurrently
results = await validator.validate_all_keys("unsplash_key", "openai_key")

print(f"Unsplash valid: {results['unsplash'].is_valid}")
print(f"OpenAI valid: {results['openai'].is_valid}")
```

## 🎮 Setup Wizard

The setup wizard provides a user-friendly configuration experience:

```python
from src.config import SecureSetupWizard, SecureConfigManager
import tkinter as tk

root = tk.Tk()
config_manager = SecureConfigManager()

def on_setup_success():
    print("Configuration saved successfully!")

wizard = SecureSetupWizard(root, config_manager, on_setup_success)
root.mainloop()
```

Features:
- Real-time key validation with visual feedback
- Secure key entry with show/hide toggles
- Model selection with cost estimates
- Help system with API key acquisition guides
- Progress indicators for async operations

## 🔄 Migration System

Automatically migrates from legacy configuration files:

```python
from src.config import migrate_legacy_configuration, SecureConfigManager

config_manager = SecureConfigManager()
migration_result = await migrate_legacy_configuration(config_manager)

if migration_result is True:
    print("Migration completed successfully")
elif migration_result is False:
    print("Migration failed")
else:
    print("No migration needed")
```

Supports migration from:
- `config.ini` files
- `.env` files  
- Environment variables
- Legacy session logs

## 📋 Configuration Template

For distribution, use the configuration template system:

```python
from src.config import SecureConfigManager

config_manager = SecureConfigManager()
template_path = config_manager.create_config_template()
print(f"Template created: {template_path}")
```

The template contains:
- Placeholder values (never real keys)
- Setup instructions
- Security warnings
- Platform-specific storage paths

## 🔧 Environment Variables

The system supports environment variable fallbacks for development:

```bash
# Development setup
export UNSPLASH_ACCESS_KEY="your_unsplash_key"
export OPENAI_API_KEY="your_openai_key"
export GPT_MODEL="gpt-4o-mini"
```

Environment variables take precedence over stored configuration.

## 📊 Configuration Info

Get information about the current configuration:

```python
config_info = config_manager.get_config_info()
print(f"Config exists: {config_info['config_exists']}")
print(f"Encryption available: {config_info['encryption_available']}")
print(f"Valid keys: {config_info['has_valid_keys']}")
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

## 🚨 Security Best Practices

1. **Never store API keys in code**: Always use the secure configuration system
2. **Validate keys before storage**: Use the built-in validation system
3. **Use environment variables for development**: Keep production keys out of code
4. **Regular key rotation**: Update keys periodically for security
5. **Secure backups**: Use the built-in backup system for key recovery

## 🐛 Troubleshooting

### Windows DPAPI Issues
If DPAPI is unavailable:
1. Install `pywin32`: `pip install pywin32`
2. The system will automatically fall back to base64 encoding (less secure)

### Permission Errors
If you encounter permission errors:
1. Run the application as administrator once to set initial permissions
2. Check that the config directory exists and is writable

### Network Validation Issues
If key validation fails:
1. Check internet connectivity
2. Verify firewall settings allow HTTPS requests
3. Check if corporate proxy is blocking requests

### Migration Issues
If migration from legacy config fails:
1. Check that legacy files are readable
2. Ensure target directory is writable
3. Review logs for specific error messages

## 📞 Support

For issues with the secure configuration system:

1. Check the application logs for detailed error messages
2. Verify your API keys work independently (test in browser/curl)
3. Ensure you have the required dependencies installed
4. Review the troubleshooting section above

## 🔒 Security Disclosure

If you discover a security vulnerability in the configuration system, please report it privately to the maintainers. Do not create public issues for security vulnerabilities.