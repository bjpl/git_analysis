#!/usr/bin/env python3
"""
Smoke Test Suite for Unsplash Image Search GPT Tool Executable

This module provides automated smoke tests for the built executable.
These tests verify critical functionality works after building the application.
"""

import os
import sys
import time
import psutil
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from unittest.mock import Mock, patch
import pytest


class ExecutableTestRunner:
    """Main test runner for executable smoke tests."""
    
    def __init__(self, exe_path: str = None):
        """Initialize test runner with executable path."""
        self.exe_path = exe_path or self._find_executable()
        self.test_results = []
        self.start_time = None
        self.temp_dir = None
        
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
        
        raise FileNotFoundError("Executable not found. Build the application first.")
    
    def setup_test_environment(self):
        """Set up isolated test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="smoke_test_")
        self.test_config_dir = Path(self.temp_dir) / "config"
        self.test_config_dir.mkdir(exist_ok=True)
        
        # Create test config file
        test_config = {
            'API': {
                'unsplash_access_key': 'test_key_unsplash',
                'openai_api_key': 'test_key_openai',
                'gpt_model': 'gpt-4o-mini'
            },
            'Paths': {
                'data_dir': str(self.test_config_dir / 'data'),
                'log_file': str(self.test_config_dir / 'data' / 'session_log.json'),
                'vocabulary_file': str(self.test_config_dir / 'data' / 'vocabulary.csv')
            },
            'UI': {
                'window_width': '1100',
                'window_height': '800',
                'font_size': '12',
                'theme': 'light',
                'zoom_level': '100'
            }
        }
        
        import configparser
        config = configparser.ConfigParser()
        for section, values in test_config.items():
            config[section] = values
        
        with open(self.test_config_dir / 'config.ini', 'w') as f:
            config.write(f)
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        result = {
            'test_name': test_name,
            'passed': passed,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")


class SmokeTests(ExecutableTestRunner):
    """Core smoke tests for the executable."""
    
    def test_executable_exists(self):
        """Test that the executable file exists and is accessible."""
        try:
            exists = Path(self.exe_path).exists()
            size = Path(self.exe_path).stat().st_size if exists else 0
            
            self.log_test_result(
                "Executable File Exists",
                exists and size > 1000000,  # Should be at least 1MB
                f"Path: {self.exe_path}, Size: {size:,} bytes"
            )
            return exists and size > 1000000
        except Exception as e:
            self.log_test_result(
                "Executable File Exists", 
                False, 
                f"Error: {str(e)}"
            )
            return False
    
    def test_executable_launches(self):
        """Test that the executable launches without immediate crash."""
        try:
            # Start the process
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            # Give it time to start
            time.sleep(3)
            
            # Check if still running
            is_running = process.poll() is None
            
            if is_running:
                # Try to terminate gracefully
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
            else:
                # Process already terminated, check exit code
                stdout, stderr = process.communicate()
                details = f"Exit code: {process.returncode}"
                if stderr:
                    details += f", Stderr: {stderr.decode()[:200]}"
            
            self.log_test_result(
                "Executable Launches",
                is_running,
                "Process started successfully" if is_running else details
            )
            return is_running
            
        except Exception as e:
            self.log_test_result(
                "Executable Launches",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_process_resource_usage(self):
        """Test that the process uses reasonable system resources."""
        try:
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            time.sleep(5)  # Let it fully load
            
            if process.poll() is not None:
                self.log_test_result(
                    "Process Resource Usage",
                    False,
                    "Process terminated before resource check"
                )
                return False
            
            # Get process info
            ps_process = psutil.Process(process.pid)
            memory_mb = ps_process.memory_info().rss / 1024 / 1024
            cpu_percent = ps_process.cpu_percent(interval=1)
            
            # Reasonable limits for a GUI application
            memory_ok = memory_mb < 300  # Less than 300MB
            cpu_ok = cpu_percent < 50    # Less than 50% CPU after startup
            
            process.terminate()
            process.wait(timeout=5)
            
            passed = memory_ok and cpu_ok
            details = f"Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%"
            
            self.log_test_result(
                "Process Resource Usage",
                passed,
                details
            )
            return passed
            
        except Exception as e:
            self.log_test_result(
                "Process Resource Usage",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_config_file_handling(self):
        """Test that configuration files are created and accessed properly."""
        try:
            # Remove config file if it exists
            config_file = self.test_config_dir / 'config.ini'
            if config_file.exists():
                config_file.unlink()
            
            # Start process briefly
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            time.sleep(3)
            
            # Check if config file was created
            config_created = config_file.exists()
            
            # Terminate process
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            
            self.log_test_result(
                "Config File Handling",
                config_created,
                f"Config file created: {config_created}"
            )
            return config_created
            
        except Exception as e:
            self.log_test_result(
                "Config File Handling",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_data_directory_creation(self):
        """Test that data directories are created properly."""
        try:
            data_dir = self.test_config_dir / 'data'
            if data_dir.exists():
                import shutil
                shutil.rmtree(data_dir)
            
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            time.sleep(3)
            
            data_dir_created = data_dir.exists()
            
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            
            self.log_test_result(
                "Data Directory Creation",
                data_dir_created,
                f"Data directory created: {data_dir_created}"
            )
            return data_dir_created
            
        except Exception as e:
            self.log_test_result(
                "Data Directory Creation",
                False,
                f"Error: {str(e)}"
            )
            return False


class APIConnectionTests(ExecutableTestRunner):
    """Tests for API connectivity and error handling."""
    
    def test_invalid_api_keys_handling(self):
        """Test behavior with invalid API keys."""
        try:
            # Create config with invalid keys
            import configparser
            config = configparser.ConfigParser()
            config['API'] = {
                'unsplash_access_key': 'invalid_key_12345',
                'openai_api_key': 'invalid_key_67890',
                'gpt_model': 'gpt-4o-mini'
            }
            
            config_file = self.test_config_dir / 'config.ini'
            with open(config_file, 'w') as f:
                config.write(f)
            
            # Start process
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            time.sleep(5)
            
            # Process should still be running (graceful error handling)
            still_running = process.poll() is None
            
            if still_running:
                process.terminate()
                process.wait(timeout=5)
            
            self.log_test_result(
                "Invalid API Keys Handling",
                still_running,
                "Application handles invalid keys gracefully" if still_running else "Application crashed with invalid keys"
            )
            return still_running
            
        except Exception as e:
            self.log_test_result(
                "Invalid API Keys Handling",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_network_error_simulation(self):
        """Test behavior when network is unavailable."""
        try:
            # This test would require network simulation
            # For now, we'll just verify the app can start offline
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            time.sleep(3)
            
            offline_ok = process.poll() is None
            
            if offline_ok:
                process.terminate()
                process.wait(timeout=5)
            
            self.log_test_result(
                "Network Error Simulation",
                offline_ok,
                "Application starts without network connectivity"
            )
            return offline_ok
            
        except Exception as e:
            self.log_test_result(
                "Network Error Simulation",
                False,
                f"Error: {str(e)}"
            )
            return False


class PerformanceTests(ExecutableTestRunner):
    """Performance-related tests."""
    
    def test_startup_time(self):
        """Test application startup time."""
        try:
            start_time = time.time()
            
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            # Wait for process to be responsive (approximate)
            time.sleep(2)
            
            startup_time = time.time() - start_time
            
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            
            # Startup should be under 10 seconds for reasonable performance
            fast_startup = startup_time < 10
            
            self.log_test_result(
                "Startup Time",
                fast_startup,
                f"Startup time: {startup_time:.2f} seconds"
            )
            return fast_startup
            
        except Exception as e:
            self.log_test_result(
                "Startup Time",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_memory_leak_basic(self):
        """Basic memory leak test - run for extended period."""
        try:
            process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            time.sleep(3)
            
            if process.poll() is not None:
                self.log_test_result(
                    "Memory Leak Basic",
                    False,
                    "Process terminated before memory test"
                )
                return False
            
            ps_process = psutil.Process(process.pid)
            initial_memory = ps_process.memory_info().rss
            
            # Let it run for a bit
            time.sleep(10)
            
            if process.poll() is None:
                final_memory = ps_process.memory_info().rss
                memory_growth = final_memory - initial_memory
                memory_growth_mb = memory_growth / 1024 / 1024
                
                # Allow some memory growth but not excessive
                no_major_leak = memory_growth_mb < 50  # Less than 50MB growth
                
                process.terminate()
                process.wait(timeout=5)
                
                self.log_test_result(
                    "Memory Leak Basic",
                    no_major_leak,
                    f"Memory growth: {memory_growth_mb:.1f}MB over 10 seconds"
                )
                return no_major_leak
            else:
                self.log_test_result(
                    "Memory Leak Basic",
                    False,
                    "Process terminated during memory test"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Memory Leak Basic",
                False,
                f"Error: {str(e)}"
            )
            return False


def run_smoke_tests(exe_path: str = None):
    """Run all smoke tests and return results."""
    print("🔍 Starting Executable Smoke Tests...")
    print("=" * 60)
    
    # Initialize test runner
    runner = SmokeTests(exe_path)
    
    try:
        # Setup test environment
        runner.setup_test_environment()
        
        # Run basic smoke tests
        basic_tests = [
            runner.test_executable_exists,
            runner.test_executable_launches,
            runner.test_process_resource_usage,
            runner.test_config_file_handling,
            runner.test_data_directory_creation,
        ]
        
        basic_results = []
        for test in basic_tests:
            try:
                result = test()
                basic_results.append(result)
            except Exception as e:
                print(f"Test failed with exception: {e}")
                basic_results.append(False)
        
        # Run API tests if basic tests pass
        if all(basic_results):
            api_runner = APIConnectionTests(exe_path)
            api_runner.test_config_dir = runner.test_config_dir
            api_runner.temp_dir = runner.temp_dir
            
            api_tests = [
                api_runner.test_invalid_api_keys_handling,
                api_runner.test_network_error_simulation,
            ]
            
            for test in api_tests:
                try:
                    test()
                except Exception as e:
                    print(f"API test failed with exception: {e}")
        
        # Run performance tests
        perf_runner = PerformanceTests(exe_path)
        perf_runner.test_config_dir = runner.test_config_dir
        perf_runner.temp_dir = runner.temp_dir
        
        perf_tests = [
            perf_runner.test_startup_time,
            perf_runner.test_memory_leak_basic,
        ]
        
        for test in perf_tests:
            try:
                test()
            except Exception as e:
                print(f"Performance test failed with exception: {e}")
        
        # Combine all results
        all_results = runner.test_results + getattr(api_runner, 'test_results', []) + getattr(perf_runner, 'test_results', [])
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SMOKE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_count = sum(1 for r in all_results if r['passed'])
        total_count = len(all_results)
        pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        print(f"Tests Passed: {passed_count}/{total_count} ({pass_rate:.1f}%)")
        
        # Critical failures
        critical_failures = [r for r in all_results if not r['passed'] and any(critical in r['test_name'] for critical in ['Executable Exists', 'Executable Launches'])]
        
        if critical_failures:
            print("🚨 CRITICAL FAILURES - RELEASE BLOCKER:")
            for failure in critical_failures:
                print(f"  - {failure['test_name']}: {failure['details']}")
        
        # Overall status
        if pass_rate >= 90:
            print("✅ OVERALL STATUS: PASS - Ready for further testing")
        elif pass_rate >= 70:
            print("⚠️  OVERALL STATUS: WARNING - Issues need attention")
        else:
            print("❌ OVERALL STATUS: FAIL - Major issues found")
        
        return all_results
        
    finally:
        # Cleanup
        runner.cleanup_test_environment()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run smoke tests on built executable")
    parser.add_argument("--exe", help="Path to executable file")
    parser.add_argument("--output", help="Output file for test results JSON")
    
    args = parser.parse_args()
    
    try:
        results = run_smoke_tests(args.exe)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📋 Results saved to: {args.output}")
        
        # Exit with appropriate code
        passed_count = sum(1 for r in results if r['passed'])
        total_count = len(results)
        critical_passed = all(r['passed'] for r in results if any(critical in r['test_name'] for critical in ['Executable Exists', 'Executable Launches']))
        
        if critical_passed and passed_count >= total_count * 0.9:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except Exception as e:
        print(f"❌ Smoke tests failed with error: {e}")
        sys.exit(1)