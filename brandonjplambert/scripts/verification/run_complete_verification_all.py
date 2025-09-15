"""
Complete verification of ALL remaining accounts - persistent until done
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent))

from complete_verification import CompleteVerificationProcessor


async def run_complete_verification_all():
    """
    Run verification for ALL remaining accounts - don't stop until done
    """
    yaml_file = r"C:\Users\brand\Development\Project_Workspace\brandonjplambert\_data\spanish_accounts.yml"
    
    print("\n🚀 COMPLETE VERIFICATION - ALL ACCOUNTS")
    print("="*60)
    print("Will process ALL remaining accounts until completion")
    print("="*60)
    
    processor = CompleteVerificationProcessor(yaml_file)
    
    print(f"\n📊 Full Scope:")
    print(f"  - Unverified URLs to process: {len(processor.unverified_accounts)}")
    print(f"  - Missing YouTube URLs to find: {processor.stats['missing_youtube_count']}")
    
    total_work = len(processor.unverified_accounts) + processor.stats['missing_youtube_count']
    print(f"  - Total operations: {total_work}")
    
    print("\n⚠️  IMPORTANT:")
    print("  - This WILL take time (possibly 1-2 hours)")
    print("  - Rate limiting pauses are built in")
    print("  - The process will NOT stop until complete")
    print("  - You can interrupt with Ctrl+C if needed")
    
    response = input("\n🔥 Ready to process ALL accounts? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("Cancelled")
        return
    
    start_time = datetime.now()
    print(f"\n⏰ Started at: {start_time.strftime('%H:%M:%S')}")
    
    # Phase 1: Verify ALL existing unverified URLs
    print("\n" + "="*60)
    print("📍 PHASE 1: Verifying ALL existing URLs")
    print("="*60)
    
    total_unverified = len(processor.unverified_accounts)
    if total_unverified > 0:
        print(f"Processing {total_unverified} unverified URLs...")
        
        # Process in batches of 20, but process ALL
        batch_size = 20
        for i in range(0, total_unverified, batch_size):
            batch_end = min(i + batch_size, total_unverified)
            print(f"\n🔄 Processing URLs {i+1}-{batch_end} of {total_unverified}")
            
            await processor.verify_existing_urls(
                batch_size=5,  # Small internal batches
                max_urls=batch_size if i == 0 else None  # Process next batch
            )
            
            print(f"  Progress: {processor.stats['urls_verified']}/{total_unverified} verified")
            print(f"  Active found: {processor.stats['urls_found_active']}")
            
            # Longer pause between batches to respect rate limits
            if i + batch_size < total_unverified:
                pause_time = 30  # 30 seconds between batches
                print(f"  ⏸️  Pausing {pause_time} seconds before next batch...")
                await asyncio.sleep(pause_time)
    else:
        print("No unverified URLs to process")
    
    print(f"\n✅ Phase 1 Complete: {processor.stats['urls_verified']} URLs verified")
    
    # Pause between phases
    print("\n⏸️  Pausing 60 seconds before Phase 2...")
    await asyncio.sleep(60)
    
    # Phase 2: Discover ALL missing YouTube URLs
    print("\n" + "="*60)
    print("📍 PHASE 2: Finding ALL missing YouTube URLs")
    print("="*60)
    
    total_missing = processor.stats['missing_youtube_count']
    if total_missing > 0:
        print(f"Searching for {total_missing} missing YouTube URLs...")
        
        # Process in batches of 10 accounts
        batch_size = 10
        processed = 0
        
        while processed < total_missing:
            batch_end = min(processed + batch_size, total_missing)
            print(f"\n🔄 Processing accounts {processed+1}-{batch_end} of {total_missing}")
            
            # Reset the accounts list for next batch
            if processed > 0:
                processor.accounts_missing_youtube = processor.accounts_missing_youtube[batch_size:]
            
            await processor.discover_missing_youtube_urls(max_accounts=batch_size)
            
            processed = batch_end
            print(f"  Progress: {processed}/{total_missing} accounts processed")
            print(f"  YouTube URLs found: {processor.stats['youtube_urls_discovered']}")
            
            # Pause between batches
            if processed < total_missing:
                pause_time = 45  # 45 seconds between YouTube batches
                print(f"  ⏸️  Pausing {pause_time} seconds before next batch...")
                await asyncio.sleep(pause_time)
    else:
        print("No missing YouTube URLs to find")
    
    print(f"\n✅ Phase 2 Complete: {processor.stats['youtube_urls_discovered']} YouTube URLs discovered")
    
    # Update YAML with ALL results
    print("\n" + "="*60)
    print("💾 SAVING ALL RESULTS")
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
    
    # Save report
    report_file = Path(yaml_file).parent / f"complete_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
        f.write(f"\n\nProcessing started: {start_time}")
        f.write(f"\nProcessing ended: {datetime.now()}")
        f.write(f"\nTotal duration: {datetime.now() - start_time}")
    
    # Final summary
    elapsed = datetime.now() - start_time
    print("\n" + "="*60)
    print("🎉 VERIFICATION COMPLETE!")
    print("="*60)
    print(f"⏱️  Total time: {elapsed}")
    print(f"📊 Final Results:")
    print(f"  - URLs verified: {processor.stats['urls_verified']}")
    print(f"  - Active URLs found: {processor.stats['urls_found_active']}")
    print(f"  - YouTube URLs discovered: {processor.stats['youtube_urls_discovered']}")
    print(f"  - Total updates made: {updates}")
    print(f"\n📄 Full report saved to: {report_file}")
    print("\n✨ Your Spanish accounts dataset is now fully verified and enriched!")


if __name__ == "__main__":
    print("\n🔥 COMPLETE VERIFICATION SYSTEM")
    print("   Will process ALL remaining accounts")
    print("   This is the FULL run - no limits!")
    
    try:
        asyncio.run(run_complete_verification_all())
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("   Partial results have been saved")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n   Partial results may have been saved")