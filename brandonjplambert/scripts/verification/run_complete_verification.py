"""
Automated runner for complete verification with safety limits
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from complete_verification import CompleteVerificationProcessor


async def run_safe_verification():
    """
    Run verification with safe limits to avoid rate limiting issues
    """
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    
    print("\n🔍 Safe Complete Verification & YouTube Discovery")
    print("="*60)
    print("Processing with conservative limits to avoid rate limiting")
    print("="*60)
    
    processor = CompleteVerificationProcessor(yaml_file)
    
    print(f"\n📊 Current Status:")
    print(f"  - Unverified URLs: {len(processor.unverified_accounts)}")
    print(f"  - Missing YouTube: {processor.stats['missing_youtube_count']}")
    
    print("\n🎯 Processing Plan:")
    print("  - Will verify up to 30 existing URLs")
    print("  - Will search for up to 20 missing YouTube URLs")
    print("  - Using small batches with pauses")
    print("  - Estimated time: 15-20 minutes")
    
    start_time = datetime.now()
    
    # Phase 1: Verify existing unverified URLs (conservative limit)
    print("\n📍 Phase 1: Verifying existing URLs...")
    print("  Processing first 30 unverified URLs...")
    await processor.verify_existing_urls(batch_size=5, max_urls=30)
    
    print(f"  ✓ Verified {processor.stats['urls_verified']} URLs")
    print(f"  ✓ Found {processor.stats['urls_found_active']} active")
    
    # Pause between phases
    print("\n⏸️  Pausing 20 seconds between phases...")
    await asyncio.sleep(20)
    
    # Phase 2: Discover missing YouTube URLs (conservative limit)
    print("\n📍 Phase 2: Discovering missing YouTube URLs...")
    print("  Searching for YouTube URLs for 20 accounts...")
    await processor.discover_missing_youtube_urls(max_accounts=20)
    
    print(f"  ✓ Discovered {processor.stats['youtube_urls_discovered']} YouTube URLs")
    
    # Update YAML with results
    print("\n💾 Updating YAML with results...")
    updates = processor.update_yaml_with_results()
    
    if updates > 0:
        processor.save_yaml()
        print(f"✅ Successfully updated {updates} accounts")
    else:
        print("ℹ️  No updates to save")
    
    # Generate and display report
    report = processor.generate_report()
    print("\n" + report)
    
    # Save report
    report_file = Path(yaml_file).parent / f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    elapsed = datetime.now() - start_time
    print(f"\n⏱️  Total time: {elapsed.total_seconds():.0f} seconds")
    print(f"📄 Report saved to: {report_file}")
    
    # Provide next steps
    if len(processor.unverified_accounts) > 30 or processor.stats['missing_youtube_count'] > 20:
        print("\n📌 Next Steps:")
        remaining_unverified = max(0, len(processor.unverified_accounts) - 30)
        remaining_youtube = max(0, processor.stats['missing_youtube_count'] - 20)
        
        if remaining_unverified > 0:
            print(f"  - {remaining_unverified} URLs still need verification")
        if remaining_youtube > 0:
            print(f"  - {remaining_youtube} accounts still missing YouTube URLs")
        
        print("\n  Run again later to process more accounts")
        print("  Wait at least 1 hour to avoid rate limiting")


if __name__ == "__main__":
    print("\n🚀 Starting Safe Verification Process")
    print("   This will respect rate limits and process conservatively")
    
    try:
        asyncio.run(run_safe_verification())
        print("\n✅ Verification completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()