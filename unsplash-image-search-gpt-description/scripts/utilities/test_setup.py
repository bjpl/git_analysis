#!/usr/bin/env python3
"""
Test script to verify API keys and configuration.
Run this before building the executable to ensure everything works.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
import requests
from openai import OpenAI


def test_configuration():
    """Test that configuration loads correctly."""
    print("Testing configuration...")
    try:
        config = ConfigManager()
        keys = config.get_api_keys()
        
        if not keys['unsplash']:
            print("❌ Unsplash API key not found")
            return False
        else:
            print("✅ Unsplash API key found")
        
        if not keys['openai']:
            print("❌ OpenAI API key not found")
            return False
        else:
            print("✅ OpenAI API key found")
        
        print(f"✅ GPT Model: {keys['gpt_model']}")
        
        paths = config.get_paths()
        print(f"✅ Data directory: {paths['data_dir']}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_unsplash_api(api_key):
    """Test Unsplash API connection."""
    print("\nTesting Unsplash API...")
    try:
        headers = {"Authorization": f"Client-ID {api_key}"}
        url = "https://api.unsplash.com/search/photos?query=test&page=1&per_page=1"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Unsplash API working")
            data = response.json()
            if data.get('results'):
                print(f"   Found {data['total']} results for 'test'")
            return True
        elif response.status_code == 401:
            print("❌ Unsplash API key is invalid")
            return False
        elif response.status_code == 403:
            print("❌ Unsplash API rate limit exceeded")
            return False
        else:
            print(f"❌ Unsplash API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unsplash connection error: {e}")
        return False


def test_openai_api(api_key, model):
    """Test OpenAI API connection."""
    print("\nTesting OpenAI API...")
    try:
        client = OpenAI(api_key=api_key)
        
        # Simple test message
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'API test successful' in Spanish"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API working")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        error_str = str(e)
        if "api_key" in error_str.lower() or "unauthorized" in error_str.lower():
            print("❌ OpenAI API key is invalid")
        elif "insufficient_quota" in error_str.lower():
            print("❌ OpenAI API quota exceeded - please add credits to your account")
        elif "rate_limit" in error_str.lower():
            print("❌ OpenAI API rate limit exceeded")
        else:
            print(f"❌ OpenAI API error: {e}")
        return False


def main():
    print("=" * 50)
    print("UNSPLASH-GPT TOOL CONFIGURATION TEST")
    print("=" * 50)
    
    # Test configuration
    if not test_configuration():
        print("\n⚠️  Please set up your API keys first!")
        print("Run: python main_updated.py")
        print("Or create a .env file based on .env.example")
        return 1
    
    # Load config for API tests
    config = ConfigManager()
    keys = config.get_api_keys()
    
    # Test APIs
    unsplash_ok = test_unsplash_api(keys['unsplash'])
    openai_ok = test_openai_api(keys['openai'], keys['gpt_model'])
    
    print("\n" + "=" * 50)
    if unsplash_ok and openai_ok:
        print("✅ ALL TESTS PASSED - Ready to use!")
        print("\nYou can now:")
        print("1. Run the app: python main_updated.py")
        print("2. Build executable: build.bat (Windows) or ./build.sh (Mac/Linux)")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please check your configuration")
        print("\nTroubleshooting:")
        if not unsplash_ok:
            print("- Check your Unsplash API key at https://unsplash.com/developers")
        if not openai_ok:
            print("- Check your OpenAI API key at https://platform.openai.com/api-keys")
            print("- Ensure you have credits in your OpenAI account")
        return 1


if __name__ == "__main__":
    sys.exit(main())