#!/usr/bin/env python3
"""
Version update script for semantic release
Updates version in various project files
"""

import sys
import json
import re
from pathlib import Path


def update_version(new_version):
    """Update version in all relevant project files"""
    project_root = Path(__file__).parent.parent
    
    files_to_update = [
        {
            'file': 'package.json',
            'pattern': r'"version":\s*"[^"]*"',
            'replacement': f'"version": "{new_version}"'
        },
        {
            'file': 'version_file.txt',
            'pattern': r'.*',
            'replacement': new_version
        },
        {
            'file': 'src/config/config_template.json',
            'pattern': r'"version":\s*"[^"]*"',
            'replacement': f'"version": "{new_version}"'
        },
        {
            'file': 'installer/version_info_windows.py',
            'pattern': r"filevers=\([^)]*\)",
            'replacement': f"filevers={version_to_tuple(new_version)}"
        },
        {
            'file': 'installer/version_info_windows.py',
            'pattern': r"prodvers=\([^)]*\)",
            'replacement': f"prodvers={version_to_tuple(new_version)}"
        }
    ]
    
    for file_info in files_to_update:
        file_path = project_root / file_info['file']
        
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                updated_content = re.sub(
                    file_info['pattern'],
                    file_info['replacement'],
                    content
                )
                
                file_path.write_text(updated_content, encoding='utf-8')
                print(f"✅ Updated {file_info['file']}")
                
            except Exception as e:
                print(f"❌ Error updating {file_info['file']}: {e}")
        else:
            print(f"⚠️  File not found: {file_info['file']}")


def version_to_tuple(version_string):
    """Convert version string to tuple for Windows version info"""
    # Remove any pre-release suffixes
    version_clean = re.sub(r'[-+].*$', '', version_string)
    parts = version_clean.split('.')
    
    # Ensure we have at least 4 parts for Windows version
    while len(parts) < 4:
        parts.append('0')
    
    return f"({', '.join(parts[:4])})"


def update_package_json_version(new_version):
    """Update package.json version using JSON parsing"""
    project_root = Path(__file__).parent.parent
    package_json = project_root / 'package.json'
    
    if package_json.exists():
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['version'] = new_version
            
            with open(package_json, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')
            
            print(f"✅ Updated package.json version to {new_version}")
            
        except Exception as e:
            print(f"❌ Error updating package.json: {e}")


def validate_version(version_string):
    """Validate version string format"""
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9]+(?:\.\d+)?))?(?:\+([a-zA-Z0-9]+))?$'
    return re.match(pattern, version_string) is not None


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    if not validate_version(new_version):
        print(f"❌ Invalid version format: {new_version}")
        print("Expected format: X.Y.Z[-prerelease][+build]")
        sys.exit(1)
    
    print(f"🔄 Updating version to {new_version}")
    
    # Update all files
    update_version(new_version)
    update_package_json_version(new_version)
    
    print(f"✅ Version update complete: {new_version}")


if __name__ == '__main__':
    main()