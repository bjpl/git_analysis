"""
Simple test runner for image collection functionality validation.
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    """Run image collection tests and provide summary."""
    print("🚀 Running Image Collection Tests")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # Test suites to run
    test_files = [
        "tests/test_basic_validation.py",
        "tests/unit/test_image_collection.py",
        "tests/integration/test_image_collection_integration.py"
    ]
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    
    for test_file in test_files:
        test_path = project_root / test_file
        
        if not test_path.exists():
            print(f"⚠️  Skipping {test_file} - file not found")
            continue
            
        print(f"\n📋 Running: {test_file}")
        print("-" * 30)
        
        # Run the test
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "-x"  # Stop on first failure for easier debugging
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout per file
            )
            
            # Parse output
            output = result.stdout + result.stderr
            passed = output.count("PASSED")
            failed = output.count("FAILED") 
            skipped = output.count("SKIPPED")
            
            total_tests += passed + failed + skipped
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
            
            # Print results
            if result.returncode == 0:
                print(f"✅ {test_file}: {passed} passed, {skipped} skipped")
            else:
                print(f"❌ {test_file}: {passed} passed, {failed} failed, {skipped} skipped")
                if failed > 0:
                    # Show failure details
                    print("\nFailure details:")
                    lines = output.split('\n')
                    for line in lines:
                        if "FAILED" in line or "ERROR" in line:
                            print(f"  - {line}")
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file}: Test timed out")
            total_failed += 1
            total_tests += 1
            
        except Exception as e:
            print(f"💥 {test_file}: Error running test - {e}")
            total_failed += 1
            total_tests += 1
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"⏭️  Skipped: {total_skipped}")
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    # Recommendations
    print("\n💡 FINDINGS:")
    if total_failed == 0:
        print("✨ All tests passed! Image collection functionality validated.")
    else:
        print(f"⚠️  {total_failed} tests failed. Review and fix issues.")
    
    if total_skipped > 0:
        print(f"ℹ️  {total_skipped} tests were skipped (likely due to missing dependencies).")
    
    # Exit with appropriate code
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())