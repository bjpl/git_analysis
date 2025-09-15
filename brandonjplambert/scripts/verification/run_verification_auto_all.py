"""
Automatic complete verification of ALL remaining accounts - no user input needed
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent))

from complete_verification import CompleteVerificationProcessor


async def run_automatic_complete_verification():
    """
    Automatically run verification for ALL remaining accounts
    """
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    
    print("\n🚀 AUTOMATIC COMPLETE VERIFICATION - ALL ACCOUNTS")
    print("="*60)
    print("Processing ALL remaining accounts automatically")
    print("="*60)
    
    processor = CompleteVerificationProcessor(yaml_file)
    
    print(f"\n📊 Full Scope:")
    print(f"  - Unverified URLs to process: {len(processor.unverified_accounts)}")
    print(f"  - Missing YouTube URLs to find: {processor.stats['missing_youtube_count']}")
    
    total_work = len(processor.unverified_accounts) + processor.stats['missing_youtube_count']
    print(f"  - Total operations needed: {total_work}")
    
    if total_work == 0:
        print("\n✅ No work needed - all accounts are already verified!")
        return
    
    start_time = datetime.now()
    print(f"\n⏰ Started at: {start_time.strftime('%H:%M:%S')}")
    print("🔄 Processing will continue until complete...")
    
    # Phase 1: Verify ALL existing unverified URLs
    print("\n" + "="*60)
    print("📍 PHASE 1: Verifying ALL existing URLs")
    print("="*60)
    
    total_unverified = len(processor.unverified_accounts)
    if total_unverified > 0:
        print(f"Processing {total_unverified} unverified URLs in batches...")
        
        # Process ALL URLs - no max_urls limit
        await processor.verify_existing_urls(batch_size=10, max_urls=None)
        
        print(f"\n✅ Phase 1 Complete:")
        print(f"  - URLs verified: {processor.stats['urls_verified']}")
        print(f"  - Active found: {processor.stats['urls_found_active']}")
        
        if processor.stats['urls_verified'] > 0:
            success_rate = (processor.stats['urls_found_active'] / processor.stats['urls_verified']) * 100
            print(f"  - Success rate: {success_rate:.1f}%")
    else:
        print("No unverified URLs to process")
    
    # Pause between phases
    if processor.stats['missing_youtube_count'] > 0:
        print("\n⏸️  Pausing 30 seconds before Phase 2...")
        await asyncio.sleep(30)
    
    # Phase 2: Discover ALL missing YouTube URLs
    print("\n" + "="*60)
    print("📍 PHASE 2: Finding ALL missing YouTube URLs")
    print("="*60)
    
    total_missing = processor.stats['missing_youtube_count']
    if total_missing > 0:
        print(f"Searching for {total_missing} missing YouTube URLs...")
        
        # Process ALL missing YouTube URLs - no max_accounts limit
        await processor.discover_missing_youtube_urls(max_accounts=None)
        
        print(f"\n✅ Phase 2 Complete:")
        print(f"  - Accounts processed: {total_missing}")
        print(f"  - YouTube URLs discovered: {processor.stats['youtube_urls_discovered']}")
        
        if total_missing > 0:
            discovery_rate = (processor.stats['youtube_urls_discovered'] / total_missing) * 100
            print(f"  - Discovery rate: {discovery_rate:.1f}%")
    else:
        print("No missing YouTube URLs to find")
    
    # Update YAML with ALL results
    print("\n" + "="*60)
    print("💾 SAVING ALL RESULTS TO YAML")
    print("="*60)
    
    updates = processor.update_yaml_with_results()
    
    if updates > 0:
        processor.save_yaml()
        print(f"✅ Successfully updated {updates} accounts in YAML")
    else:
        print("ℹ️  No updates to save")
    
    # Generate final report
    report = processor.generate_report()
    print("\n" + report)
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(yaml_file).parent / f"complete_verification_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("COMPLETE VERIFICATION REPORT\n")
        f.write("="*70 + "\n")
        f.write(f"Processing started: {start_time}\n")
        f.write(f"Processing ended: {datetime.now()}\n")
        f.write(f"Total duration: {datetime.now() - start_time}\n")
        f.write("\n" + report)
        
        # Add detailed results
        f.write("\n\nDETAILED RESULTS:\n")
        f.write("="*70 + "\n")
        
        if processor.verification_results:
            f.write("\nVERIFIED ACCOUNTS:\n")
            for idx, platforms in processor.verification_results.items():
                account = processor.yaml_data['accounts'][idx]
                f.write(f"\n{account.get('name', 'Unknown')}:\n")
                for platform, result in platforms.items():
                    f.write(f"  - {platform}: {result['status']}")
                    if result.get('follower_count'):
                        f.write(f" ({result['follower_count']:,} followers)")
                    f.write("\n")
        
        if processor.discovered_youtube_urls:
            f.write("\n\nDISCOVERED YOUTUBE URLs:\n")
            for idx, youtube_data in processor.discovered_youtube_urls.items():
                account = processor.yaml_data['accounts'][idx]
                f.write(f"\n{account.get('name', 'Unknown')}:\n")
                f.write(f"  - URL: {youtube_data['url']}\n")
                f.write(f"  - Confidence: {youtube_data['confidence']:.2f}\n")
                if youtube_data.get('follower_count'):
                    f.write(f"  - Subscribers: {youtube_data['follower_count']:,}\n")
    
    # Final summary
    elapsed = datetime.now() - start_time
    print("\n" + "="*60)
    print("🎉 VERIFICATION COMPLETE!")
    print("="*60)
    print(f"⏱️  Total time: {elapsed}")
    print(f"\n📊 Final Results:")
    print(f"  - URLs verified: {processor.stats['urls_verified']}")
    print(f"  - Active URLs found: {processor.stats['urls_found_active']}")
    print(f"  - YouTube URLs discovered: {processor.stats['youtube_urls_discovered']}")
    print(f"  - Total accounts updated: {updates}")
    
    # Calculate final completion rates
    instagram_complete = sum(1 for acc in processor.yaml_data['accounts'] 
                            if acc and acc.get('instagram_verified'))
    youtube_complete = sum(1 for acc in processor.yaml_data['accounts'] 
                          if acc and acc.get('youtube_url'))
    total_accounts = processor.stats['total_accounts']
    
    print(f"\n📈 Final Completion Rates:")
    print(f"  - Instagram verified: {instagram_complete}/{total_accounts} ({instagram_complete/total_accounts*100:.1f}%)")
    print(f"  - YouTube URLs: {youtube_complete}/{total_accounts} ({youtube_complete/total_accounts*100:.1f}%)")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("\n✨ Your Spanish accounts dataset is now fully verified and enriched!")


if __name__ == "__main__":
    print("\n🔥 AUTOMATIC COMPLETE VERIFICATION SYSTEM")
    print("   Processing ALL remaining accounts")
    print("   No user input required - fully automatic!")
    print("   Estimated time: 30-90 minutes depending on accounts")
    
    try:
        asyncio.run(run_automatic_complete_verification())
        print("\n✅ All processing completed successfully!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("   Partial results have been saved")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\n   Check logs for details - partial results may have been saved")