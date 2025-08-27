"""
Version information and metadata for the Unsplash Image Search & GPT Description Tool.
This file is used by PyInstaller to generate Windows version info and by the build script.
"""

import os
from datetime import datetime

# Application Information
APP_NAME = "Unsplash Image Search & GPT Tool"
APP_DESCRIPTION = "AI-powered image search and Spanish vocabulary learning tool"
APP_COPYRIGHT = "© 2024 Unsplash GPT Tool. All rights reserved."
COMPANY_NAME = "Language Learning Tools"
PRODUCT_NAME = APP_NAME

# Version Configuration
MAJOR_VERSION = 2
MINOR_VERSION = 0
PATCH_VERSION = 0
BUILD_NUMBER = int(datetime.now().strftime("%y%m%d"))  # YYMMDD format

# Version Strings
APP_VERSION = f"{MAJOR_VERSION}.{MINOR_VERSION}.{PATCH_VERSION}"
FULL_VERSION = f"{APP_VERSION}.{BUILD_NUMBER}"
VERSION_TUPLE = (MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, BUILD_NUMBER)

# Build Information
BUILD_DATE = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
BUILD_TYPE = "Release"
BUILD_BRANCH = "main"

# Update Information (for future update checking)
UPDATE_CHECK_URL = "https://api.github.com/repos/yourusername/unsplash-image-search-gpt/releases/latest"
DOWNLOAD_URL = "https://github.com/yourusername/unsplash-image-search-gpt/releases"

# File Paths and Names
EXECUTABLE_NAME = f"{APP_NAME.replace(' ', '_')}_v{APP_VERSION}.exe"
INSTALLER_NAME = f"{APP_NAME.replace(' ', '_')}_Setup_v{APP_VERSION}.exe"
PORTABLE_NAME = f"{APP_NAME.replace(' ', '_')}_Portable_v{APP_VERSION}.exe"

# Windows Version Info Resource
VERSION_INFO = f"""
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={VERSION_TUPLE},
    prodvers={VERSION_TUPLE},
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{COMPANY_NAME}'),
        StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
        StringStruct(u'FileVersion', u'{FULL_VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'{APP_COPYRIGHT}'),
        StringStruct(u'OriginalFilename', u'{EXECUTABLE_NAME}'),
        StringStruct(u'ProductName', u'{PRODUCT_NAME}'),
        StringStruct(u'ProductVersion', u'{FULL_VERSION}'),
        StringStruct(u'Comments', u'Built on {BUILD_DATE}'),
        StringStruct(u'LegalTrademarks', u''),
        StringStruct(u'PrivateBuild', u'{BUILD_TYPE}'),
        StringStruct(u'SpecialBuild', u'Branch: {BUILD_BRANCH}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""

# Create version info file for PyInstaller
def create_version_file():
    """Create a version info file for PyInstaller to use."""
    version_content = VERSION_INFO.format(
        COMPANY_NAME=COMPANY_NAME,
        APP_DESCRIPTION=APP_DESCRIPTION,
        FULL_VERSION=FULL_VERSION,
        APP_NAME=APP_NAME,
        APP_COPYRIGHT=APP_COPYRIGHT,
        EXECUTABLE_NAME=EXECUTABLE_NAME,
        PRODUCT_NAME=PRODUCT_NAME,
        BUILD_DATE=BUILD_DATE,
        BUILD_TYPE=BUILD_TYPE,
        BUILD_BRANCH=BUILD_BRANCH,
        VERSION_TUPLE=VERSION_TUPLE
    )
    
    version_file_path = os.path.join(os.path.dirname(__file__), "version_file.txt")
    with open(version_file_path, "w", encoding="utf-8") as f:
        f.write(version_content)
    
    return version_file_path

# Feature flags for different build configurations
FEATURES = {
    "auto_update": True,
    "crash_reporting": True,
    "analytics": False,  # Disabled for privacy
    "debug_mode": False,
    "beta_features": False,
}

# Minimum system requirements
SYSTEM_REQUIREMENTS = {
    "min_python_version": "3.8",
    "min_ram_mb": 512,
    "min_disk_space_mb": 100,
    "supported_os": ["Windows 10", "Windows 11"],
    "required_apis": ["OpenAI", "Unsplash"],
}

# Security and privacy settings
SECURITY = {
    "encrypt_config": False,
    "secure_api_storage": True,
    "check_certificates": True,
    "allow_http": False,  # Only HTTPS
}

if __name__ == "__main__":
    print(f"Application: {APP_NAME}")
    print(f"Version: {FULL_VERSION}")
    print(f"Build Date: {BUILD_DATE}")
    print(f"Build Type: {BUILD_TYPE}")
    print(f"Executable: {EXECUTABLE_NAME}")
    
    # Create version file
    version_file = create_version_file()
    print(f"Version file created: {version_file}")