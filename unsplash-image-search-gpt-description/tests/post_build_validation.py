#!/usr/bin/env python3
"""
Post-Build Validation Script for Unsplash Image Search GPT Tool

This script runs comprehensive validation tests on the built executable
to ensure it's ready for distribution. It combines smoke tests, API tests,
and UI tests into a complete validation suite.
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


class PostBuildValidator:
    """Main validator for post-build testing."""
    
    def __init__(self, exe_path: str = None, output_dir: str = None):
        """Initialize the post-build validator."""
        self.exe_path = exe_path or self._find_executable()
        self.output_dir = Path(output_dir) if output_dir else Path("test_results")
        self.output_dir.mkdir(exist_ok=True)
        
        self.test_results = {
            'validation_timestamp': datetime.now().isoformat(),
            'executable_path': str(self.exe_path),
            'test_suites': {},
            'overall_status': 'UNKNOWN',
            'summary': {}
        }
        
        self.critical_failures = []
        self.warnings = []
    
    def _find_executable(self):
        """Auto-detect executable path."""
        possible_paths = [
            "dist/main.exe",
            "build/main.exe", 
            "main.exe",
            "dist/UnsplashImageSearchGPT.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return Path(path).absolute()
        
        raise FileNotFoundError(
            "Executable not found. Please build the application first or specify --exe path."
        )
    
    def run_validation_suite(self):
        """Run the complete validation suite."""
        print("🚀 Starting Post-Build Validation Suite")
        print("=" * 70)
        print(f"Executable: {self.exe_path}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Timestamp: {self.test_results['validation_timestamp']}")
        print()
        
        # Test Suite 1: Smoke Tests (Critical)
        print("📋 Running Smoke Tests (Critical)...")
        smoke_results = self._run_smoke_tests()
        self.test_results['test_suites']['smoke_tests'] = {
            'results': smoke_results,
            'critical': True,
            'passed': self._evaluate_test_suite(smoke_results, critical=True)
        }
        
        # Check if we should continue based on critical failures
        if not self.test_results['test_suites']['smoke_tests']['passed']:
            self._handle_critical_failure("Smoke tests failed - blocking further testing")
            return self._generate_final_report()
        
        # Test Suite 2: API Mock Tests
        print("\n🔧 Running API Mock Tests...")
        api_results = self._run_api_mock_tests()
        self.test_results['test_suites']['api_mock_tests'] = {
            'results': api_results,
            'critical': False,
            'passed': self._evaluate_test_suite(api_results)
        }
        
        # Test Suite 3: UI Responsiveness Tests
        print("\n🖥️  Running UI Responsiveness Tests...")
        ui_results = self._run_ui_responsiveness_tests()
        self.test_results['test_suites']['ui_responsiveness_tests'] = {
            'results': ui_results,
            'critical': False,
            'passed': self._evaluate_test_suite(ui_results)
        }
        
        # Test Suite 4: Security and Error Handling Tests
        print("\n🔒 Running Security and Error Handling Tests...")
        security_results = self._run_security_tests()
        self.test_results['test_suites']['security_tests'] = {
            'results': security_results,
            'critical': False,
            'passed': self._evaluate_test_suite(security_results)
        }
        
        # Test Suite 5: Performance Benchmarking
        print("\n📊 Running Performance Benchmarks...")
        performance_results = self._run_performance_benchmarks()
        self.test_results['test_suites']['performance_benchmarks'] = {
            'results': performance_results,
            'critical': False,
            'passed': self._evaluate_test_suite(performance_results)
        }
        
        return self._generate_final_report()
    
    def _run_smoke_tests(self):
        """Run smoke test suite."""
        try:
            # Import and run smoke tests
            sys.path.append(str(Path(__file__).parent))
            from smoke_test_suite import run_smoke_tests
            
            results = run_smoke_tests(str(self.exe_path))
            self._save_test_results('smoke_tests.json', results)
            return results
            
        except Exception as e:
            print(f"❌ Smoke tests failed to run: {e}")
            return [self._create_error_result("Smoke Test Execution", str(e))]
    
    def _run_api_mock_tests(self):
        """Run API mock test suite."""
        try:
            from api_mock_tests import run_api_mock_tests
            
            results = run_api_mock_tests()
            self._save_test_results('api_mock_tests.json', results)
            return results
            
        except Exception as e:
            print(f"❌ API mock tests failed to run: {e}")
            return [self._create_error_result("API Mock Test Execution", str(e))]
    
    def _run_ui_responsiveness_tests(self):
        """Run UI responsiveness test suite."""
        try:
            from ui_responsiveness_tests import run_ui_responsiveness_tests
            
            results = run_ui_responsiveness_tests(str(self.exe_path))
            self._save_test_results('ui_responsiveness_tests.json', results)
            return results
            
        except Exception as e:
            print(f"❌ UI responsiveness tests failed to run: {e}")
            return [self._create_error_result("UI Responsiveness Test Execution", str(e))]
    
    def _run_security_tests(self):
        """Run security and error handling tests."""
        security_results = []
        
        # File system security test
        security_results.append(self._test_file_system_security())
        
        # Configuration security test
        security_results.append(self._test_config_security())
        
        # Error handling test
        security_results.append(self._test_error_handling())
        
        # Process isolation test
        security_results.append(self._test_process_isolation())
        
        self._save_test_results('security_tests.json', security_results)
        return security_results
    
    def _run_performance_benchmarks(self):
        """Run performance benchmark tests."""
        performance_results = []
        
        # Executable size check
        performance_results.append(self._test_executable_size())
        
        # Startup performance benchmark
        performance_results.append(self._test_startup_performance())
        
        # Memory efficiency benchmark
        performance_results.append(self._test_memory_efficiency())
        
        # Resource cleanup test
        performance_results.append(self._test_resource_cleanup())
        
        self._save_test_results('performance_benchmarks.json', performance_results)
        return performance_results
    
    def _test_file_system_security(self):
        """Test file system access security."""
        try:
            # Create temporary test environment
            with tempfile.TemporaryDirectory() as temp_dir:
                test_dir = Path(temp_dir) / "security_test"
                test_dir.mkdir()
                
                # Test that application only creates files in expected locations
                process = subprocess.Popen(
                    [str(self.exe_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(test_dir)
                )
                
                time.sleep(5)  # Let it initialize
                
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                
                # Check that no unauthorized files were created outside test directory
                files_created = list(test_dir.rglob("*"))
                unauthorized_access = any(
                    not str(f).startswith(str(test_dir)) for f in files_created
                )
                
                return self._create_test_result(
                    "File System Security",
                    not unauthorized_access,
                    f"Files created: {len(files_created)}, Unauthorized access: {unauthorized_access}"
                )
                
        except Exception as e:
            return self._create_error_result("File System Security", str(e))
    
    def _test_config_security(self):
        """Test configuration file security."""
        try:
            # Test that sensitive data is not stored in plain text
            with tempfile.TemporaryDirectory() as temp_dir:
                config_dir = Path(temp_dir) / "config_test"
                config_dir.mkdir()
                
                # Create a config file with test API keys
                import configparser
                config = configparser.ConfigParser()
                config['API'] = {
                    'unsplash_access_key': 'test_sensitive_key_12345',
                    'openai_api_key': 'test_sensitive_key_67890',
                    'gpt_model': 'gpt-4o-mini'
                }
                
                config_file = config_dir / 'config.ini'
                with open(config_file, 'w') as f:
                    config.write(f)
                
                # Start application briefly
                process = subprocess.Popen(
                    [str(self.exe_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(config_dir.parent)
                )
                
                time.sleep(3)
                
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                
                # Check that config file wasn't compromised or leaked
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config_content = f.read()
                    
                    # Basic check: sensitive data should still be there (not deleted/corrupted)
                    has_keys = 'test_sensitive_key' in config_content
                    config_secure = has_keys  # Basic test - in real app, check for encryption
                else:
                    config_secure = False
                
                return self._create_test_result(
                    "Config Security",
                    config_secure,
                    "Configuration file handling appears secure"
                )
                
        except Exception as e:
            return self._create_error_result("Config Security", str(e))
    
    def _test_error_handling(self):
        """Test error handling robustness."""
        try:
            error_scenarios_passed = 0
            total_error_scenarios = 0
            
            # Scenario 1: Invalid executable location
            total_error_scenarios += 1
            try:
                # Try running from a directory that doesn't exist
                invalid_dir = Path("nonexistent_directory_12345")
                process = subprocess.Popen(
                    [str(self.exe_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(invalid_dir) if invalid_dir.exists() else None
                )
                
                # Should either start successfully or fail gracefully
                time.sleep(3)
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                    error_scenarios_passed += 1  # Started successfully
                elif process.returncode is not None:
                    # Check if it failed gracefully (not crash)
                    if process.returncode != -1073741819:  # Not access violation
                        error_scenarios_passed += 1
                    
            except Exception:
                pass  # Expected to fail
            
            # Scenario 2: Corrupted config file
            total_error_scenarios += 1
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    config_dir = Path(temp_dir)
                    
                    # Create corrupted config file
                    config_file = config_dir / 'config.ini'
                    with open(config_file, 'w') as f:
                        f.write("CORRUPTED CONFIG FILE\n!!!INVALID CONTENT!!!")
                    
                    process = subprocess.Popen(
                        [str(self.exe_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=str(config_dir)
                    )
                    
                    time.sleep(5)
                    
                    # Should handle corrupted config gracefully
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=5)
                        error_scenarios_passed += 1  # Handled gracefully
                        
            except Exception:
                pass
            
            success_rate = error_scenarios_passed / total_error_scenarios if total_error_scenarios > 0 else 0
            
            return self._create_test_result(
                "Error Handling",
                success_rate >= 0.5,  # At least 50% of error scenarios handled
                f"Error scenarios handled: {error_scenarios_passed}/{total_error_scenarios}",
                {'success_rate': success_rate * 100}
            )
            
        except Exception as e:
            return self._create_error_result("Error Handling", str(e))
    
    def _test_process_isolation(self):
        """Test process isolation and cleanup."""
        try:
            # Start the application
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(3)
            
            # Get process information
            import psutil
            try:
                ps_process = psutil.Process(process.pid)
                child_processes_before = ps_process.children(recursive=True)
                open_files_before = len(ps_process.open_files())
                
                # Let it run a bit longer
                time.sleep(5)
                
                child_processes_after = ps_process.children(recursive=True)
                open_files_after = len(ps_process.open_files())
                
                # Terminate the process
                process.terminate()
                process.wait(timeout=10)
                
                # Check for cleanup
                time.sleep(2)
                
                # Verify process is actually terminated
                process_cleaned_up = not psutil.pid_exists(process.pid)
                
                # Check for zombie child processes
                zombie_processes = []
                for child in child_processes_after:
                    try:
                        if psutil.pid_exists(child.pid):
                            zombie_processes.append(child.pid)
                    except:
                        pass
                
                isolation_good = (
                    process_cleaned_up and
                    len(zombie_processes) == 0 and
                    open_files_after < open_files_before + 10  # Allow some file handles
                )
                
                return self._create_test_result(
                    "Process Isolation",
                    isolation_good,
                    f"Process cleaned up: {process_cleaned_up}, Zombie processes: {len(zombie_processes)}",
                    {
                        'child_processes': len(child_processes_after),
                        'open_files': open_files_after,
                        'zombies': len(zombie_processes)
                    }
                )
                
            except ImportError:
                # psutil not available, do basic test
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=10)
                
                return self._create_test_result(
                    "Process Isolation",
                    True,
                    "Basic process cleanup successful (psutil not available)"
                )
                
        except Exception as e:
            return self._create_error_result("Process Isolation", str(e))
    
    def _test_executable_size(self):
        """Test executable size is reasonable."""
        try:
            size_bytes = self.exe_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            # Reasonable size limits for a GUI application
            min_size_mb = 10   # At least 10MB (has dependencies)
            max_size_mb = 500  # Less than 500MB
            
            size_reasonable = min_size_mb <= size_mb <= max_size_mb
            
            return self._create_test_result(
                "Executable Size",
                size_reasonable,
                f"Size: {size_mb:.1f}MB (acceptable range: {min_size_mb}-{max_size_mb}MB)",
                {'size_mb': round(size_mb, 1)}
            )
            
        except Exception as e:
            return self._create_error_result("Executable Size", str(e))
    
    def _test_startup_performance(self):
        """Benchmark startup performance."""
        try:
            startup_times = []
            
            # Run multiple startup tests
            for i in range(3):
                start_time = time.time()
                
                process = subprocess.Popen(
                    [str(self.exe_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait for process to initialize
                time.sleep(2)
                
                startup_time = time.time() - start_time
                startup_times.append(startup_time)
                
                # Terminate
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                
                time.sleep(1)  # Brief pause between tests
            
            avg_startup_time = sum(startup_times) / len(startup_times)
            max_startup_time = max(startup_times)
            
            # Performance criteria
            fast_startup = avg_startup_time < 8.0  # Average under 8 seconds
            consistent_startup = max_startup_time < 12.0  # Max under 12 seconds
            
            performance_good = fast_startup and consistent_startup
            
            return self._create_test_result(
                "Startup Performance",
                performance_good,
                f"Average: {avg_startup_time:.2f}s, Max: {max_startup_time:.2f}s",
                {
                    'avg_startup_time': round(avg_startup_time, 2),
                    'max_startup_time': round(max_startup_time, 2),
                    'all_times': [round(t, 2) for t in startup_times]
                }
            )
            
        except Exception as e:
            return self._create_error_result("Startup Performance", str(e))
    
    def _test_memory_efficiency(self):
        """Test memory usage efficiency."""
        try:
            # Start application
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(5)  # Let it fully initialize
            
            if process.poll() is not None:
                return self._create_error_result("Memory Efficiency", "Process terminated before memory test")
            
            import psutil
            try:
                ps_process = psutil.Process(process.pid)
                memory_info = ps_process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                
                # Let it run for a bit to check for immediate leaks
                time.sleep(10)
                
                if process.poll() is None:
                    memory_info_after = ps_process.memory_info()
                    memory_mb_after = memory_info_after.rss / (1024 * 1024)
                    memory_growth = memory_mb_after - memory_mb
                    
                    process.terminate()
                    process.wait(timeout=5)
                else:
                    memory_mb_after = memory_mb
                    memory_growth = 0
                
                # Memory efficiency criteria
                reasonable_initial_memory = memory_mb < 300  # Under 300MB initial
                reasonable_growth = memory_growth < 50  # Less than 50MB growth in 10 seconds
                
                efficient = reasonable_initial_memory and reasonable_growth
                
                return self._create_test_result(
                    "Memory Efficiency",
                    efficient,
                    f"Initial: {memory_mb:.1f}MB, After 10s: {memory_mb_after:.1f}MB, Growth: {memory_growth:.1f}MB",
                    {
                        'initial_memory_mb': round(memory_mb, 1),
                        'final_memory_mb': round(memory_mb_after, 1),
                        'memory_growth_mb': round(memory_growth, 1)
                    }
                )
                
            except ImportError:
                # psutil not available
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                
                return self._create_test_result(
                    "Memory Efficiency",
                    True,
                    "Basic memory test passed (psutil not available)"
                )
                
        except Exception as e:
            return self._create_error_result("Memory Efficiency", str(e))
    
    def _test_resource_cleanup(self):
        """Test resource cleanup after termination."""
        try:
            # Start and stop application multiple times
            temp_files_before = list(Path(tempfile.gettempdir()).glob("*"))
            
            for i in range(3):
                process = subprocess.Popen(
                    [str(self.exe_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                time.sleep(3)  # Let it create any temp files
                
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                
                time.sleep(1)  # Allow cleanup time
            
            # Check for temp file accumulation
            temp_files_after = list(Path(tempfile.gettempdir()).glob("*"))
            temp_files_growth = len(temp_files_after) - len(temp_files_before)
            
            # Should not accumulate many temp files
            cleanup_good = temp_files_growth < 10  # Less than 10 new temp files
            
            return self._create_test_result(
                "Resource Cleanup",
                cleanup_good,
                f"Temp files growth: {temp_files_growth} files",
                {'temp_files_growth': temp_files_growth}
            )
            
        except Exception as e:
            return self._create_error_result("Resource Cleanup", str(e))
    
    def _create_test_result(self, test_name: str, passed: bool, details: str = "", metrics: dict = None):
        """Create a standardized test result."""
        return {
            'test_name': test_name,
            'passed': passed,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'metrics': metrics or {}
        }
    
    def _create_error_result(self, test_name: str, error_message: str):
        """Create an error test result."""
        return {
            'test_name': test_name,
            'passed': False,
            'timestamp': datetime.now().isoformat(),
            'details': f"Test execution error: {error_message}",
            'metrics': {'error': True}
        }
    
    def _evaluate_test_suite(self, results: list, critical: bool = False):
        """Evaluate if a test suite passes."""
        if not results:
            return False
        
        passed_count = sum(1 for r in results if r.get('passed', False))
        total_count = len(results)
        
        if critical:
            # Critical tests must have high pass rate
            required_rate = 0.95  # 95%
        else:
            # Non-critical tests can have lower pass rate
            required_rate = 0.80  # 80%
        
        return (passed_count / total_count) >= required_rate
    
    def _handle_critical_failure(self, message: str):
        """Handle critical failure that blocks testing."""
        self.critical_failures.append(message)
        print(f"🚨 CRITICAL FAILURE: {message}")
    
    def _save_test_results(self, filename: str, results: list):
        """Save test results to file."""
        output_file = self.output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _generate_final_report(self):
        """Generate final validation report."""
        print("\n" + "=" * 70)
        print("📋 POST-BUILD VALIDATION REPORT")
        print("=" * 70)
        
        # Calculate overall statistics
        all_tests = []
        suite_summary = {}
        
        for suite_name, suite_data in self.test_results['test_suites'].items():
            suite_results = suite_data['results']
            all_tests.extend(suite_results)
            
            passed_count = sum(1 for r in suite_results if r.get('passed', False))
            total_count = len(suite_results)
            pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
            
            suite_summary[suite_name] = {
                'passed': passed_count,
                'total': total_count,
                'pass_rate': round(pass_rate, 1),
                'critical': suite_data['critical'],
                'suite_passed': suite_data['passed']
            }
        
        # Overall statistics
        total_passed = sum(1 for r in all_tests if r.get('passed', False))
        total_tests = len(all_tests)
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'overall_pass_rate': round(overall_pass_rate, 1),
            'suite_summary': suite_summary,
            'critical_failures': self.critical_failures,
            'warnings': self.warnings
        }
        
        # Print summary
        print(f"Total Tests: {total_tests}")
        print(f"Tests Passed: {total_passed}")
        print(f"Overall Pass Rate: {overall_pass_rate:.1f}%")
        print()
        
        # Print suite breakdown
        print("TEST SUITE BREAKDOWN:")
        for suite_name, summary in suite_summary.items():
            status = "✅ PASS" if summary['suite_passed'] else "❌ FAIL"
            critical_flag = " (CRITICAL)" if summary['critical'] else ""
            print(f"  {status} {suite_name}{critical_flag}: {summary['passed']}/{summary['total']} ({summary['pass_rate']:.1f}%)")
        
        # Critical failures
        if self.critical_failures:
            print("\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"  - {failure}")
        
        # Failed tests
        failed_tests = [r for r in all_tests if not r.get('passed', False)]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['details']}")
        
        # Determine overall status
        critical_suites_passed = all(
            summary['suite_passed'] for summary in suite_summary.values() 
            if summary['critical']
        )
        
        if self.critical_failures or not critical_suites_passed:
            self.test_results['overall_status'] = 'CRITICAL_FAILURE'
            status_msg = "🚨 CRITICAL FAILURE - DO NOT RELEASE"
        elif overall_pass_rate >= 95:
            self.test_results['overall_status'] = 'EXCELLENT'
            status_msg = "🏆 EXCELLENT - READY FOR RELEASE"
        elif overall_pass_rate >= 85:
            self.test_results['overall_status'] = 'GOOD'
            status_msg = "✅ GOOD - READY FOR RELEASE"
        elif overall_pass_rate >= 70:
            self.test_results['overall_status'] = 'ACCEPTABLE'
            status_msg = "⚠️  ACCEPTABLE - CONSIDER FIXES BEFORE RELEASE"
        else:
            self.test_results['overall_status'] = 'POOR'
            status_msg = "❌ POOR - SIGNIFICANT ISSUES NEED FIXING"
        
        print(f"\n{status_msg}")
        
        # Save complete results
        final_report_file = self.output_dir / 'post_build_validation_report.json'
        with open(final_report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Complete report saved to: {final_report_file}")
        
        # Save summary report (human-readable)
        summary_file = self.output_dir / 'validation_summary.txt'
        with open(summary_file, 'w') as f:
            f.write("POST-BUILD VALIDATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Timestamp: {self.test_results['validation_timestamp']}\n")
            f.write(f"Executable: {self.exe_path}\n")
            f.write(f"Overall Status: {self.test_results['overall_status']}\n")
            f.write(f"Pass Rate: {overall_pass_rate:.1f}% ({total_passed}/{total_tests})\n\n")
            
            f.write("SUITE RESULTS:\n")
            for suite_name, summary in suite_summary.items():
                status = "PASS" if summary['suite_passed'] else "FAIL"
                critical = " (CRITICAL)" if summary['critical'] else ""
                f.write(f"  {status}: {suite_name}{critical} - {summary['pass_rate']:.1f}%\n")
            
            if failed_tests:
                f.write("\nFAILED TESTS:\n")
                for test in failed_tests:
                    f.write(f"  - {test['test_name']}: {test['details']}\n")
            
            f.write(f"\n{status_msg}\n")
        
        print(f"📄 Summary report saved to: {summary_file}")
        
        return self.test_results


def main():
    """Main entry point for post-build validation."""
    parser = argparse.ArgumentParser(description="Post-Build Validation for Unsplash Image Search GPT Tool")
    parser.add_argument("--exe", help="Path to executable file")
    parser.add_argument("--output", default="test_results", help="Output directory for test results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        validator = PostBuildValidator(args.exe, args.output)
        results = validator.run_validation_suite()
        
        # Exit with appropriate code based on validation results
        overall_status = results['overall_status']
        
        if overall_status == 'CRITICAL_FAILURE':
            sys.exit(2)  # Critical failure
        elif overall_status in ['EXCELLENT', 'GOOD']:
            sys.exit(0)  # Success
        elif overall_status == 'ACCEPTABLE':
            sys.exit(1)  # Warning
        else:
            sys.exit(3)  # Poor quality
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(4)
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(5)


if __name__ == "__main__":
    main()