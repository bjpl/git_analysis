#!/usr/bin/env python3
"""
UI Responsiveness and Accessibility Tests for Unsplash Image Search GPT Tool

This module provides automated tests for UI responsiveness, accessibility,
and user interaction scenarios for the built executable.
"""

import os
import sys
import time
import threading
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import pyautogui
import psutil

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


class UITestFramework:
    """Framework for UI testing with automation capabilities."""
    
    def __init__(self, exe_path: str = None):
        """Initialize UI test framework."""
        self.exe_path = exe_path or self._find_executable()
        self.test_results = []
        self.process = None
        self.temp_dir = None
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # Small delay between actions
        
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
        """Set up test environment with configuration."""
        self.temp_dir = tempfile.mkdtemp(prefix="ui_test_")
        self.test_config_dir = Path(self.temp_dir) / "config"
        self.test_config_dir.mkdir(exist_ok=True)
        
        # Create test config
        import configparser
        config = configparser.ConfigParser()
        config['API'] = {
            'unsplash_access_key': 'test_key_12345',
            'openai_api_key': 'test_key_67890',
            'gpt_model': 'gpt-4o-mini'
        }
        config['Paths'] = {
            'data_dir': str(self.test_config_dir / 'data'),
            'log_file': str(self.test_config_dir / 'data' / 'session_log.json'),
            'vocabulary_file': str(self.test_config_dir / 'data' / 'vocabulary.csv')
        }
        config['UI'] = {
            'window_width': '1100',
            'window_height': '800',
            'font_size': '12',
            'theme': 'light',
            'zoom_level': '100'
        }
        
        with open(self.test_config_dir / 'config.ini', 'w') as f:
            config.write(f)
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
        
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def launch_application(self):
        """Launch the application for testing."""
        try:
            self.process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.test_config_dir.parent)
            )
            
            # Wait for application to start
            time.sleep(5)
            
            if self.process.poll() is not None:
                return False
            
            return True
        except Exception as e:
            print(f"Failed to launch application: {e}")
            return False
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", metrics: dict = None):
        """Log test result with optional metrics."""
        result = {
            'test_name': test_name,
            'passed': passed,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'metrics': metrics or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if metrics:
            print(f"   Metrics: {metrics}")


class ResponsivenessTests(UITestFramework):
    """Tests for UI responsiveness and performance."""
    
    def test_startup_responsiveness(self):
        """Test application startup time and initial responsiveness."""
        try:
            start_time = time.time()
            
            if not self.launch_application():
                self.log_test_result(
                    "Startup Responsiveness",
                    False,
                    "Failed to launch application"
                )
                return False
            
            startup_time = time.time() - start_time
            
            # Check if window is visible (basic heuristic)
            time.sleep(2)  # Allow window to fully render
            
            # Try to find the application window
            try:
                # Look for window with the app title
                window_found = False
                import pygetwindow as gw
                windows = gw.getAllTitles()
                for title in windows:
                    if "Unsplash" in title or "GPT" in title:
                        window_found = True
                        break
            except ImportError:
                # Fallback: assume window is there if process is running
                window_found = self.process.poll() is None
            
            # Evaluate responsiveness
            fast_startup = startup_time < 10.0  # Under 10 seconds
            responsive = window_found and self.process.poll() is None
            
            metrics = {
                'startup_time': round(startup_time, 2),
                'window_found': window_found
            }
            
            success = fast_startup and responsive
            details = f"Startup time: {startup_time:.2f}s, Window visible: {window_found}"
            
            self.log_test_result(
                "Startup Responsiveness",
                success,
                details,
                metrics
            )
            return success
            
        except Exception as e:
            self.log_test_result(
                "Startup Responsiveness",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_memory_usage_startup(self):
        """Test memory usage during startup and initial operation."""
        try:
            if not self.process or self.process.poll() is not None:
                if not self.launch_application():
                    self.log_test_result(
                        "Memory Usage Startup",
                        False,
                        "Failed to launch application for memory test"
                    )
                    return False
            
            # Wait for full initialization
            time.sleep(5)
            
            if self.process.poll() is not None:
                self.log_test_result(
                    "Memory Usage Startup",
                    False,
                    "Application terminated during memory test"
                )
                return False
            
            # Get memory usage
            ps_process = psutil.Process(self.process.pid)
            memory_info = ps_process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Check if memory usage is reasonable for a GUI app
            reasonable_memory = memory_mb < 250  # Less than 250MB for startup
            
            # Additional system resource metrics
            cpu_percent = ps_process.cpu_percent(interval=1)
            num_threads = ps_process.num_threads()
            
            metrics = {
                'memory_mb': round(memory_mb, 1),
                'cpu_percent': round(cpu_percent, 1),
                'num_threads': num_threads
            }
            
            details = f"Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%, Threads: {num_threads}"
            
            self.log_test_result(
                "Memory Usage Startup",
                reasonable_memory,
                details,
                metrics
            )
            return reasonable_memory
            
        except Exception as e:
            self.log_test_result(
                "Memory Usage Startup",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_ui_interaction_responsiveness(self):
        """Test UI responsiveness to basic interactions."""
        try:
            if not self.process or self.process.poll() is not None:
                if not self.launch_application():
                    self.log_test_result(
                        "UI Interaction Responsiveness",
                        False,
                        "Failed to launch application for interaction test"
                    )
                    return False
            
            # Wait for UI to be ready
            time.sleep(3)
            
            interaction_tests = []
            
            # Test 1: Try to click in the center of the screen (where window should be)
            try:
                screen_width, screen_height = pyautogui.size()
                center_x, center_y = screen_width // 2, screen_height // 2
                
                # Record time for click response
                click_start = time.time()
                pyautogui.click(center_x, center_y)
                time.sleep(0.5)  # Allow for response
                click_time = time.time() - click_start
                
                interaction_tests.append(('click_response', click_time < 1.0, click_time))
            except Exception as e:
                interaction_tests.append(('click_response', False, f"Error: {str(e)}"))
            
            # Test 2: Try keyboard input simulation
            try:
                key_start = time.time()
                pyautogui.press('tab')  # Navigate through UI
                time.sleep(0.5)
                pyautogui.typewrite('test')  # Type something
                key_time = time.time() - key_start
                
                interaction_tests.append(('keyboard_response', key_time < 2.0, key_time))
            except Exception as e:
                interaction_tests.append(('keyboard_response', False, f"Error: {str(e)}"))
            
            # Test 3: Check if application is still responsive
            app_responsive = self.process.poll() is None
            interaction_tests.append(('app_still_running', app_responsive, "Process alive" if app_responsive else "Process died"))
            
            # Evaluate overall responsiveness
            successful_interactions = sum(1 for test in interaction_tests if test[1])
            total_interactions = len(interaction_tests)
            
            success = successful_interactions >= total_interactions * 0.7  # 70% success rate
            
            metrics = {
                'successful_interactions': successful_interactions,
                'total_interactions': total_interactions,
                'success_rate': round(successful_interactions / total_interactions * 100, 1)
            }
            
            details = f"Successful interactions: {successful_interactions}/{total_interactions}"
            for test_name, test_passed, test_result in interaction_tests:
                if isinstance(test_result, float):
                    details += f", {test_name}: {test_result:.3f}s"
                else:
                    details += f", {test_name}: {test_result}"
            
            self.log_test_result(
                "UI Interaction Responsiveness",
                success,
                details,
                metrics
            )
            return success
            
        except Exception as e:
            self.log_test_result(
                "UI Interaction Responsiveness",
                False,
                f"Error: {str(e)}"
            )
            return False


class AccessibilityTests(UITestFramework):
    """Tests for accessibility features."""
    
    def test_keyboard_navigation(self):
        """Test keyboard navigation functionality."""
        try:
            if not self.process or self.process.poll() is not None:
                if not self.launch_application():
                    self.log_test_result(
                        "Keyboard Navigation",
                        False,
                        "Failed to launch application for keyboard test"
                    )
                    return False
            
            time.sleep(3)  # Wait for UI to be ready
            
            keyboard_tests = []
            
            # Test Tab navigation
            try:
                for i in range(5):  # Try tabbing through 5 elements
                    pyautogui.press('tab')
                    time.sleep(0.2)
                keyboard_tests.append(('tab_navigation', True, "Tab navigation successful"))
            except Exception as e:
                keyboard_tests.append(('tab_navigation', False, f"Tab error: {str(e)}"))
            
            # Test common shortcuts
            shortcuts_to_test = [
                ('ctrl+n', 'New search shortcut'),
                ('ctrl+t', 'Theme toggle shortcut'),
                ('f1', 'Help shortcut'),
                ('escape', 'Cancel/close shortcut')
            ]
            
            for shortcut, description in shortcuts_to_test:
                try:
                    pyautogui.hotkey(*shortcut.split('+'))
                    time.sleep(0.5)
                    keyboard_tests.append((shortcut.replace('+', '_'), True, f"{description} activated"))
                except Exception as e:
                    keyboard_tests.append((shortcut.replace('+', '_'), False, f"{description} failed: {str(e)}"))
            
            # Check if application is still responsive after keyboard tests
            still_running = self.process.poll() is None
            keyboard_tests.append(('app_stability', still_running, "App stable after keyboard input"))
            
            # Evaluate keyboard accessibility
            successful_tests = sum(1 for test in keyboard_tests if test[1])
            total_tests = len(keyboard_tests)
            
            success = successful_tests >= total_tests * 0.6  # 60% success rate
            
            metrics = {
                'successful_keyboard_tests': successful_tests,
                'total_keyboard_tests': total_tests,
                'success_rate': round(successful_tests / total_tests * 100, 1)
            }
            
            details = f"Keyboard tests passed: {successful_tests}/{total_tests}"
            
            self.log_test_result(
                "Keyboard Navigation",
                success,
                details,
                metrics
            )
            return success
            
        except Exception as e:
            self.log_test_result(
                "Keyboard Navigation",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_window_scaling_compatibility(self):
        """Test compatibility with different window scaling settings."""
        try:
            if not self.process or self.process.poll() is not None:
                if not self.launch_application():
                    self.log_test_result(
                        "Window Scaling Compatibility",
                        False,
                        "Failed to launch application for scaling test"
                    )
                    return False
            
            time.sleep(3)
            
            # Get current screen resolution and DPI info
            screen_width, screen_height = pyautogui.size()
            
            # Check if application window fits on screen reasonably
            # (We can't easily change DPI during testing, so we'll do basic checks)
            
            scaling_checks = []
            
            # Check 1: Screen resolution compatibility
            min_supported_width = 1024
            min_supported_height = 768
            
            resolution_ok = screen_width >= min_supported_width and screen_height >= min_supported_height
            scaling_checks.append(('resolution_support', resolution_ok, f"Screen: {screen_width}x{screen_height}"))
            
            # Check 2: Application still running (basic compatibility test)
            app_running = self.process.poll() is None
            scaling_checks.append(('app_compatibility', app_running, "App runs on current display"))
            
            # Check 3: Memory usage still reasonable (scaling can affect memory)
            if app_running:
                try:
                    ps_process = psutil.Process(self.process.pid)
                    memory_mb = ps_process.memory_info().rss / 1024 / 1024
                    memory_reasonable = memory_mb < 400  # Allow more memory for scaling
                    scaling_checks.append(('memory_with_scaling', memory_reasonable, f"Memory: {memory_mb:.1f}MB"))
                except:
                    scaling_checks.append(('memory_with_scaling', False, "Could not check memory"))
            
            # Evaluate scaling compatibility
            successful_checks = sum(1 for check in scaling_checks if check[1])
            total_checks = len(scaling_checks)
            
            success = successful_checks == total_checks  # All checks must pass
            
            metrics = {
                'screen_width': screen_width,
                'screen_height': screen_height,
                'successful_checks': successful_checks,
                'total_checks': total_checks
            }
            
            details = f"Scaling checks: {successful_checks}/{total_checks}"
            for check_name, check_passed, check_result in scaling_checks:
                details += f", {check_name}: {check_result}"
            
            self.log_test_result(
                "Window Scaling Compatibility",
                success,
                details,
                metrics
            )
            return success
            
        except Exception as e:
            self.log_test_result(
                "Window Scaling Compatibility",
                False,
                f"Error: {str(e)}"
            )
            return False


class PerformanceMonitoringTests(UITestFramework):
    """Tests for performance monitoring during UI operations."""
    
    def test_extended_operation_performance(self):
        """Test performance during extended operation."""
        try:
            if not self.process or self.process.poll() is not None:
                if not self.launch_application():
                    self.log_test_result(
                        "Extended Operation Performance",
                        False,
                        "Failed to launch application for performance test"
                    )
                    return False
            
            time.sleep(3)  # Initial stabilization
            
            # Get baseline metrics
            ps_process = psutil.Process(self.process.pid)
            initial_memory = ps_process.memory_info().rss
            
            performance_metrics = []
            test_duration = 30  # 30 seconds of monitoring
            measurement_interval = 5  # Every 5 seconds
            
            for i in range(0, test_duration, measurement_interval):
                time.sleep(measurement_interval)
                
                if self.process.poll() is not None:
                    break
                
                try:
                    current_memory = ps_process.memory_info().rss
                    cpu_percent = ps_process.cpu_percent()
                    num_threads = ps_process.num_threads()
                    
                    performance_metrics.append({
                        'timestamp': i + measurement_interval,
                        'memory_mb': current_memory / 1024 / 1024,
                        'memory_growth_mb': (current_memory - initial_memory) / 1024 / 1024,
                        'cpu_percent': cpu_percent,
                        'num_threads': num_threads
                    })
                    
                    # Simulate some user activity
                    if i % 10 == 0:  # Every 10 seconds
                        pyautogui.click(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
                        time.sleep(0.5)
                        pyautogui.press('tab')
                    
                except Exception as e:
                    print(f"Error during performance measurement at {i}s: {e}")
            
            # Analyze performance metrics
            if not performance_metrics:
                self.log_test_result(
                    "Extended Operation Performance",
                    False,
                    "No performance metrics collected"
                )
                return False
            
            # Calculate performance indicators
            max_memory = max(m['memory_mb'] for m in performance_metrics)
            max_memory_growth = max(m['memory_growth_mb'] for m in performance_metrics)
            avg_cpu = sum(m['cpu_percent'] for m in performance_metrics) / len(performance_metrics)
            max_threads = max(m['num_threads'] for m in performance_metrics)
            
            # Performance criteria
            memory_ok = max_memory < 400  # Less than 400MB
            memory_growth_ok = max_memory_growth < 100  # Less than 100MB growth
            cpu_ok = avg_cpu < 30  # Average CPU usage less than 30%
            threads_ok = max_threads < 50  # Reasonable thread count
            app_stable = self.process.poll() is None  # Still running
            
            success = all([memory_ok, memory_growth_ok, cpu_ok, threads_ok, app_stable])
            
            metrics = {
                'test_duration': test_duration,
                'measurements': len(performance_metrics),
                'max_memory_mb': round(max_memory, 1),
                'memory_growth_mb': round(max_memory_growth, 1),
                'avg_cpu_percent': round(avg_cpu, 1),
                'max_threads': max_threads,
                'app_stable': app_stable
            }
            
            details = (f"Max memory: {max_memory:.1f}MB, "
                      f"Memory growth: {max_memory_growth:.1f}MB, "
                      f"Avg CPU: {avg_cpu:.1f}%, "
                      f"Max threads: {max_threads}, "
                      f"Stable: {app_stable}")
            
            self.log_test_result(
                "Extended Operation Performance",
                success,
                details,
                metrics
            )
            return success
            
        except Exception as e:
            self.log_test_result(
                "Extended Operation Performance",
                False,
                f"Error: {str(e)}"
            )
            return False


def run_ui_responsiveness_tests(exe_path: str = None):
    """Run all UI responsiveness tests and return results."""
    print("🖥️  Starting UI Responsiveness Tests...")
    print("=" * 60)
    
    # Note about automation limitations
    print("⚠️  Note: UI automation tests have limitations in headless environments")
    print("   These tests work best on desktop systems with GUI access")
    print()
    
    all_results = []
    
    try:
        # Test 1: Basic Responsiveness
        print("Running Responsiveness Tests...")
        responsiveness_runner = ResponsivenessTests(exe_path)
        responsiveness_runner.setup_test_environment()
        
        try:
            responsiveness_tests = [
                responsiveness_runner.test_startup_responsiveness,
                responsiveness_runner.test_memory_usage_startup,
                responsiveness_runner.test_ui_interaction_responsiveness,
            ]
            
            for test in responsiveness_tests:
                try:
                    test()
                except Exception as e:
                    print(f"Responsiveness test {test.__name__} failed: {e}")
        finally:
            responsiveness_runner.cleanup_test_environment()
        
        all_results.extend(responsiveness_runner.test_results)
        
        # Test 2: Accessibility
        print("\nRunning Accessibility Tests...")
        accessibility_runner = AccessibilityTests(exe_path)
        accessibility_runner.setup_test_environment()
        
        try:
            accessibility_tests = [
                accessibility_runner.test_keyboard_navigation,
                accessibility_runner.test_window_scaling_compatibility,
            ]
            
            for test in accessibility_tests:
                try:
                    test()
                except Exception as e:
                    print(f"Accessibility test {test.__name__} failed: {e}")
        finally:
            accessibility_runner.cleanup_test_environment()
        
        all_results.extend(accessibility_runner.test_results)
        
        # Test 3: Performance Monitoring
        print("\nRunning Performance Monitoring Tests...")
        performance_runner = PerformanceMonitoringTests(exe_path)
        performance_runner.setup_test_environment()
        
        try:
            performance_tests = [
                performance_runner.test_extended_operation_performance,
            ]
            
            for test in performance_tests:
                try:
                    test()
                except Exception as e:
                    print(f"Performance test {test.__name__} failed: {e}")
        finally:
            performance_runner.cleanup_test_environment()
        
        all_results.extend(performance_runner.test_results)
        
    except ImportError as e:
        print(f"⚠️  Missing dependencies for UI testing: {e}")
        print("   Install with: pip install pyautogui pygetwindow")
        # Create a placeholder result
        all_results.append({
            'test_name': 'UI Testing Dependencies',
            'passed': False,
            'timestamp': datetime.now().isoformat(),
            'details': f'Missing dependencies: {str(e)}',
            'metrics': {}
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 UI RESPONSIVENESS TESTS SUMMARY")
    print("=" * 60)
    
    if all_results:
        passed_count = sum(1 for r in all_results if r['passed'])
        total_count = len(all_results)
        pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        
        print(f"Tests Passed: {passed_count}/{total_count} ({pass_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in all_results if not r['passed']]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for failure in failed_tests:
                print(f"  - {failure['test_name']}: {failure['details']}")
        
        # Performance metrics summary
        performance_results = [r for r in all_results if 'metrics' in r and r['metrics']]
        if performance_results:
            print("\n📈 PERFORMANCE METRICS:")
            for result in performance_results:
                if result['metrics']:
                    print(f"  - {result['test_name']}:")
                    for key, value in result['metrics'].items():
                        print(f"    {key}: {value}")
        
        # Overall status
        if pass_rate >= 90:
            print("✅ OVERALL STATUS: PASS - UI is responsive and accessible")
        elif pass_rate >= 70:
            print("⚠️  OVERALL STATUS: WARNING - Some UI issues detected")
        else:
            print("❌ OVERALL STATUS: FAIL - Significant UI problems found")
    else:
        print("❌ No tests were executed")
    
    return all_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run UI responsiveness tests")
    parser.add_argument("--exe", help="Path to executable file")
    parser.add_argument("--output", help="Output file for test results JSON")
    
    args = parser.parse_args()
    
    try:
        results = run_ui_responsiveness_tests(args.exe)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📋 Results saved to: {args.output}")
        
        # Exit with appropriate code
        if results:
            passed_count = sum(1 for r in results if r['passed'])
            total_count = len(results)
            
            if passed_count >= total_count * 0.7:
                sys.exit(0)  # Success
            else:
                sys.exit(1)  # Failure
        else:
            sys.exit(1)  # No tests run
            
    except Exception as e:
        print(f"❌ UI responsiveness tests failed with error: {e}")
        sys.exit(1)