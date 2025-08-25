#!/usr/bin/env python3
"""
Windows Version Information Generator for PyInstaller

This module generates proper Windows version information resources for the
executable, including:
- File version information
- Company and product details
- Copyright information
- Build metadata
- Digital signature preparation
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple


class WindowsVersionInfo:
    """Generates Windows version information for PyInstaller executables."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.installer_dir = project_root / "installer"
        
        # Load version information from project
        self._load_version_data()
    
    def _load_version_data(self):
        """Load version data from version_info.py or use defaults."""
        try:
            sys.path.insert(0, str(self.project_root))
            import version_info
            
            self.app_name = version_info.APP_NAME
            self.app_description = getattr(version_info, 'APP_DESCRIPTION', 
                                          'AI-powered image search and vocabulary learning tool')
            self.version = version_info.APP_VERSION
            self.full_version = getattr(version_info, 'FULL_VERSION', self.version + ".0")
            self.company_name = getattr(version_info, 'COMPANY_NAME', 'Language Learning Tools')
            self.copyright_text = getattr(version_info, 'APP_COPYRIGHT', 
                                        f'© {datetime.now().year} {self.company_name}. All rights reserved.')
            self.executable_name = version_info.EXECUTABLE_NAME
            
            # Parse version components
            version_parts = self.version.split('.')
            self.major_version = int(version_parts[0]) if len(version_parts) > 0 else 2
            self.minor_version = int(version_parts[1]) if len(version_parts) > 1 else 0
            self.patch_version = int(version_parts[2]) if len(version_parts) > 2 else 0
            self.build_number = getattr(version_info, 'BUILD_NUMBER', 
                                       int(datetime.now().strftime("%y%m%d")))
            
        except ImportError:
            # Fallback values
            self.app_name = "Unsplash Image Search GPT Tool"
            self.app_description = "AI-powered image search and vocabulary learning tool"
            self.version = "2.0.0"
            self.full_version = "2.0.0.0"
            self.company_name = "Language Learning Tools"
            self.copyright_text = f"© {datetime.now().year} Language Learning Tools. All rights reserved."
            self.executable_name = "Unsplash_Image_Search_GPT_Tool_v2.0.0.exe"
            self.major_version = 2
            self.minor_version = 0
            self.patch_version = 0
            self.build_number = int(datetime.now().strftime("%y%m%d"))
    
    def get_version_tuple(self) -> Tuple[int, int, int, int]:
        """Get version as tuple for Windows version info."""
        return (self.major_version, self.minor_version, self.patch_version, self.build_number)
    
    def generate_version_file(self, output_path: Optional[Path] = None) -> Path:
        """Generate Windows version information file for PyInstaller."""
        if output_path is None:
            output_path = self.installer_dir / "version_info.txt"
        
        version_tuple = self.get_version_tuple()
        build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        version_content = f'''# UTF-8
#
# Windows Version Information Resource
# Generated on {build_date}
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx

VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={version_tuple},
    prodvers={version_tuple},
    # Contains a bitmask that specifies the valid bits 'flags'
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x40004 - VOS_NT_WINDOWS32
    OS=0x40004,
    # The general type of file.
    # 0x1 - VFT_APP (the file is an application)
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
        u'040904B0',  # US English, Unicode
        [StringStruct(u'CompanyName', u'{self.company_name}'),
        StringStruct(u'FileDescription', u'{self.app_description}'),
        StringStruct(u'FileVersion', u'{self.full_version}'),
        StringStruct(u'InternalName', u'{self.app_name}'),
        StringStruct(u'LegalCopyright', u'{self.copyright_text}'),
        StringStruct(u'OriginalFilename', u'{self.executable_name}'),
        StringStruct(u'ProductName', u'{self.app_name}'),
        StringStruct(u'ProductVersion', u'{self.full_version}'),
        StringStruct(u'Comments', u'Built with PyInstaller on {build_date}'),
        StringStruct(u'LegalTrademarks', u''),
        StringStruct(u'PrivateBuild', u''),
        StringStruct(u'SpecialBuild', u'')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])]) # US English, Unicode
  ]
)'''
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(version_content)
        
        print(f"Windows version info generated: {output_path}")
        return output_path
    
    def create_dpi_aware_manifest(self, output_path: Optional[Path] = None) -> Path:
        """Create Windows application manifest with DPI awareness."""
        if output_path is None:
            output_path = self.installer_dir / "app.manifest"
        
        manifest_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="{self.full_version}"
    processorArchitecture="amd64"
    name="{self.company_name}.{self.app_name.replace(' ', '')}"
    type="win32"
  />
  
  <!-- Application Description -->
  <description>{self.app_description}</description>
  
  <!-- Windows Compatibility -->
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <!-- Windows 11 -->
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
      <!-- Windows 10 -->
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
      <!-- Windows 8.1 -->
      <supportedOS Id="{{1f676c76-80e1-4239-95bb-83d0f6d0da78}}"/>
      <!-- Windows 8 -->
      <supportedOS Id="{{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}}"/>
      <!-- Windows 7 -->
      <supportedOS Id="{{35138b9a-5d96-4fbd-8e2d-a2440225f93a}}"/>
    </application>
  </compatibility>
  
  <!-- High DPI Awareness -->
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <!-- Windows 10, version 1607 and later -->
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
      <!-- Windows 10, version 1507 and later -->
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <!-- Enable long path support -->
      <longPathAware xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">true</longPathAware>
      <!-- Heap type -->
      <heapType xmlns="http://schemas.microsoft.com/SMI/2020/WindowsSettings">SegmentHeap</heapType>
    </windowsSettings>
  </application>
  
  <!-- Security Settings -->
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
    <security>
      <requestedPrivileges xmlns="urn:schemas-microsoft-com:asm.v3">
        <!-- Request standard user privileges -->
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  
  <!-- Enable Common Controls 6.0 -->
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
  
  <!-- Enable Visual Styles -->
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="amd64"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
</assembly>'''
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        print(f"Windows manifest created: {output_path}")
        return output_path
    
    def create_code_signing_config(self, output_path: Optional[Path] = None) -> Path:
        """Create configuration file for code signing."""
        if output_path is None:
            output_path = self.installer_dir / "code_signing.json"
        
        signing_config = {
            "certificate_path": "path/to/certificate.p12",
            "certificate_password_env": "CODE_SIGN_PASSWORD",
            "timestamp_server": "http://timestamp.digicert.com",
            "description": self.app_description,
            "product_name": self.app_name,
            "product_version": self.version,
            "company_name": self.company_name,
            "file_description": self.app_description,
            "signing_algorithm": "SHA256",
            "cross_certificate": "path/to/cross_certificate.crt",
            "instructions": [
                "1. Install Windows SDK or Visual Studio with signing tools",
                "2. Set CODE_SIGN_PASSWORD environment variable",
                "3. Update certificate_path to your certificate file",
                "4. Run: signtool sign /f certificate.p12 /p %CODE_SIGN_PASSWORD% /t http://timestamp.digicert.com /fd SHA256 executable.exe",
                "5. Verify: signtool verify /pa /v executable.exe"
            ]
        }
        
        import json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(signing_config, f, indent=2, ensure_ascii=False)
        
        print(f"Code signing configuration created: {output_path}")
        return output_path
    
    def generate_all_windows_resources(self) -> Dict[str, Path]:
        """Generate all Windows-specific resources."""
        resources = {}
        
        # Version information
        resources['version_info'] = self.generate_version_file()
        
        # Application manifest
        resources['manifest'] = self.create_dpi_aware_manifest()
        
        # Code signing configuration
        resources['code_signing'] = self.create_code_signing_config()
        
        return resources
    
    def validate_resources(self) -> bool:
        """Validate that all generated resources are correct."""
        try:
            # Check version info file
            version_file = self.installer_dir / "version_info.txt"
            if not version_file.exists():
                print("Error: Version info file not found")
                return False
            
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'VSVersionInfo' not in content:
                    print("Error: Invalid version info format")
                    return False
            
            # Check manifest file
            manifest_file = self.installer_dir / "app.manifest"
            if not manifest_file.exists():
                print("Error: Manifest file not found")
                return False
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'dpiAwareness' not in content:
                    print("Warning: Manifest may not have DPI awareness")
                    return False
            
            print("All Windows resources validated successfully")
            return True
            
        except Exception as e:
            print(f"Validation error: {e}")
            return False


def main():
    """Main entry point for Windows version info generation."""
    project_root = Path(__file__).parent.parent
    
    # Create version info generator
    version_info = WindowsVersionInfo(project_root)
    
    # Generate all Windows resources
    print("Generating Windows resources...")
    resources = version_info.generate_all_windows_resources()
    
    # Validate resources
    if version_info.validate_resources():
        print("\nWindows resources generated successfully:")
        for resource_type, path in resources.items():
            print(f"  {resource_type}: {path}")
        
        print("\nNext steps:")
        print("1. Replace placeholder icon with actual .ico file")
        print("2. Configure code signing certificate if needed")
        print("3. Build with PyInstaller using generated resources")
        
        return 0
    else:
        print("Error: Resource validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
