"""
Automated runner script for Spanish accounts verification
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Add parent directories to path for cross-directory imports
sys.path.append(str(Path(__file__).parent.parent / "data-processing"))

from process_yaml_accounts import YAMLAccountsProcessor


async def run():
    """Run the verification process automatically"""
    
    # Configuration - using your specific file path
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    output_dir = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\verification_results"
    
    print("="*70)
    print("SPANISH ACCOUNTS VERIFICATION SYSTEM")
    print("="*70)
    print(f"\n📁 Input file: {yaml_file}")
    print(f"📂 Output directory: {output_dir}")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*70)
    
    try:
        # Create processor
        processor = YAMLAccountsProcessor(yaml_file, output_dir)
        
        # Load YAML data
        print("\n⏳ Loading YAML data...")
        yaml_data = processor.load_yaml()
        processor.accounts_data = processor.extract_accounts(yaml_data)
        
        # Show what we're about to process
        print(f"\n✅ Successfully loaded data:")
        print(f"   - Total accounts: {len(processor.accounts_data)}")
        print(f"   - URLs to verify: {len(processor.urls_to_verify)}")
        print(f"   - Categories: {len(processor.category_stats)}")
        print(f"   - Platforms: {list(processor.platform_stats.keys())}")
        
        print("\n" + "="*70)
        print("🚀 Starting automatic verification process...")
        print("   ⚠️  This will take 10-30 minutes depending on the number of URLs")
        print("   ℹ️  Respecting rate limits to avoid being blocked")
        print("="*70 + "\n")
        
        # Start verification
        await processor.verify_all_urls()
        
        # Generate reports
        print("\n📝 Generating reports...")
        report_files = processor.generate_reports()
        
        # Print summary
        processor.print_summary()
        
        # Show where reports were saved
        print("\n✅ SUCCESS! All reports have been generated:")
        print("\n📊 Report files created:")
        for report_type, file_path in report_files.items():
            file_name = Path(file_path).name
            print(f"   - {report_type.replace('_', ' ').title()}: {file_name}")
        
        print(f"\n📁 All reports saved to: {output_dir}")
        print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎉 Verification complete!")
        
        return report_files
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("   Partial results may have been saved")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Could not find file - {e}")
        print("   Please check that the YAML file exists at the specified path")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("   Check the verification.log file for details")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔧 Spanish Accounts Verification Tool v1.0 (Automated)")
    print("   Processing spanish_accounts.yml")
    
    # Check if required modules are available
    try:
        import yaml
        import aiohttp
        import pandas
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"\n❌ Missing required package: {e}")
        print("\n📦 Please install required packages:")
        print("   pip install pyyaml aiohttp pandas openpyxl")
        sys.exit(1)
    
    # Run the async function
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)