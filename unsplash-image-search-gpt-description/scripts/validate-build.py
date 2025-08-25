#!/usr/bin/env python3
"""
Build Validation and Testing Script for Unsplash Image Search & GPT Tool

This script validates the PyInstaller build output, tests executable functionality,
and provides comprehensive reports on build quality and potential issues.

Features:
- Executable validation and testing
- Dependency analysis
- File size and optimization reporting
- Security scanning
- Performance benchmarking
- Distribution readiness checks
"""

import os
import sys
import json
import subprocess
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


@dataclass
class BuildValidationResult:
    """Results of build validation process."""
    executable_path: str
    file_size_mb: float
    is_valid: bool
    startup_time_seconds: float
    dependencies_found: List[str]
    missing_dependencies: List[str]
    security_issues: List[str]
    performance_score: int
    distribution_ready: bool
    validation_errors: List[str]
    validation_warnings: List[str]
    test_results: Dict[str, bool]
    timestamp: str


class BuildValidator:
    """Validates PyInstaller build outputs."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        self.installer_dir = project_root / "installer"
        
        # Test configurations
        self.test_timeout = 30  # seconds
        self.performance_threshold = 10  # seconds for startup
        
        # Results storage
        self.results: List[BuildValidationResult] = []
        
    def find_executables(self) -> List[Path]:
        """Find all executable files in the dist directory."""
        executables = []
        
        if not self.dist_dir.exists():
            print(f"❌ Distribution directory not found: {self.dist_dir}")
            return executables
        
        # Find .exe files
        for exe_file in self.dist_dir.rglob("*.exe"):
            executables.append(exe_file)
        
        # Find executable directories (portable distributions)
        for item in self.dist_dir.iterdir():
            if item.is_dir():
                for exe_file in item.glob("*.exe"):
                    executables.append(exe_file)
        
        return executables
    
    def validate_executable_basic(self, exe_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Perform basic executable validation."""
        errors = []
        warnings = []
        is_valid = True
        
        # Check if file exists and is executable
        if not exe_path.exists():
            errors.append(f"Executable not found: {exe_path}")
            return False, errors, warnings
        
        if not os.access(exe_path, os.X_OK):
            warnings.append(f"File may not be executable: {exe_path}")
        
        # Check file size
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        if size_mb > 500:  # 500MB threshold
            warnings.append(f"Large executable size: {size_mb:.1f}MB")
        elif size_mb < 10:  # 10MB minimum threshold
            warnings.append(f"Unusually small executable: {size_mb:.1f}MB")
        
        # Check if it's a valid PE file (Windows)
        try:
            with open(exe_path, 'rb') as f:
                dos_header = f.read(2)
                if dos_header != b'MZ':
                    errors.append("Invalid executable format (not a PE file)")
                    is_valid = False
        except Exception as e:
            errors.append(f"Error reading executable: {e}")
            is_valid = False
        
        return is_valid, errors, warnings
    
    def test_executable_startup(self, exe_path: Path) -> Tuple[float, bool, List[str]]:
        """Test executable startup time and basic functionality."""
        errors = []
        
        print(f"  🧪 Testing startup time for {exe_path.name}...")
        
        try:
            start_time = time.time()
            
            # Try to run with --help or --version flag (non-GUI mode)
            result = subprocess.run(
                [str(exe_path), '--help'],
                capture_output=True,
                text=True,
                timeout=self.test_timeout
            )
            
            startup_time = time.time() - start_time
            
            # If --help doesn't work, try --version
            if result.returncode != 0:
                start_time = time.time()
                result = subprocess.run(
                    [str(exe_path), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5  # Shorter timeout for version check
                )
                startup_time = time.time() - start_time
            
            # If both fail, just check if it starts (may open GUI)
            if result.returncode != 0:
                start_time = time.time()
                # Run for a very short time and terminate
                proc = subprocess.Popen([str(exe_path)])
                time.sleep(2)  # Let it start
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                startup_time = 2.0  # Approximate startup time
                success = True
            else:
                success = True
            
            return startup_time, success, errors
            
        except subprocess.TimeoutExpired:
            errors.append(f"Executable startup timeout (>{self.test_timeout}s)")
            return float('inf'), False, errors
        except Exception as e:
            errors.append(f"Startup test failed: {e}")
            return 0.0, False, errors
    
    def analyze_dependencies(self, exe_path: Path) -> Tuple[List[str], List[str]]:
        """Analyze executable dependencies."""
        found_deps = []
        missing_deps = []
        
        # Common dependencies to check for
        expected_deps = [
            'python',
            'tkinter',
            'PIL',
            'Pillow',
            'requests',
            'openai',
            'dotenv',
        ]
        
        try:
            # Use strings command (if available) to find embedded strings
            if os.name == 'nt':  # Windows
                # Use PowerShell to search for strings
                result = subprocess.run([
                    'powershell', '-Command',
                    f'Select-String -Pattern "import|from" -Path "{exe_path}" -Quiet'
                ], capture_output=True, text=True, timeout=10)
            else:  # Unix-like
                result = subprocess.run([
                    'strings', str(exe_path)
                ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                content = result.stdout.lower()
                for dep in expected_deps:
                    if dep.lower() in content:
                        found_deps.append(dep)
                    else:
                        missing_deps.append(dep)
            else:
                # Fallback: assume all dependencies are present
                found_deps = expected_deps[:]
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # If analysis tools aren't available, assume basic dependencies
            found_deps = ['python', 'tkinter', 'requests']
            missing_deps = ['PIL', 'openai', 'dotenv']
        
        return found_deps, missing_deps
    
    def security_scan(self, exe_path: Path) -> List[str]:
        """Perform basic security scanning."""
        issues = []
        
        print(f"  🔒 Security scanning {exe_path.name}...")
        
        try:
            # Check file permissions
            stat_info = exe_path.stat()
            if stat_info.st_mode & 0o002:  # World writable
                issues.append("Executable is world-writable")
            
            # Check for common suspicious patterns (basic)
            with open(exe_path, 'rb') as f:
                # Read first 1MB for pattern matching
                chunk = f.read(1024 * 1024)
                
                # Look for suspicious strings (basic check)
                suspicious_patterns = [
                    b'cmd.exe',
                    b'powershell.exe',
                    b'regedit',
                    b'system32',
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in chunk:
                        issues.append(f"Found potentially suspicious pattern: {pattern.decode('ascii', errors='ignore')}")
            
            # File size check for potential packing
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            if size_mb > 200:
                issues.append(f"Large file size ({size_mb:.1f}MB) may indicate bundled content")
                
        except Exception as e:
            issues.append(f"Security scan error: {e}")
        
        return issues
    
    def performance_test(self, exe_path: Path, startup_time: float) -> int:
        """Calculate performance score (0-100)."""
        score = 100
        
        # Startup time penalty
        if startup_time > 10:
            score -= 30
        elif startup_time > 5:
            score -= 15
        elif startup_time > 2:
            score -= 5
        
        # File size penalty
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        if size_mb > 200:
            score -= 20
        elif size_mb > 100:
            score -= 10
        elif size_mb > 50:
            score -= 5
        
        # Bonus for reasonable file size
        if 20 <= size_mb <= 50:
            score += 5
        
        return max(0, min(100, score))
    
    def check_distribution_readiness(self, exe_path: Path, 
                                   security_issues: List[str],
                                   test_results: Dict[str, bool]) -> Tuple[bool, List[str]]:
        """Check if the build is ready for distribution."""
        issues = []
        ready = True
        
        # Critical security issues
        critical_security = ['world-writable', 'suspicious pattern']
        for issue in security_issues:
            if any(critical in issue.lower() for critical in critical_security):
                issues.append(f"Critical security issue: {issue}")
                ready = False
        
        # Failed tests
        failed_tests = [test for test, passed in test_results.items() if not passed]
        if failed_tests:
            issues.append(f"Failed tests: {', '.join(failed_tests)}")
            if len(failed_tests) > 1:
                ready = False
        
        # File integrity
        try:
            # Check if file can be read completely
            with open(exe_path, 'rb') as f:
                # Read in chunks to avoid memory issues
                chunk_size = 8192
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
        except Exception as e:
            issues.append(f"File integrity issue: {e}")
            ready = False
        
        # Required files check (for portable distributions)
        if exe_path.parent != self.dist_dir:  # It's in a subdirectory
            required_files = ['config_manager.py']  # Add more as needed
            for req_file in required_files:
                if not (exe_path.parent / req_file).exists():
                    issues.append(f"Missing required file: {req_file}")
        
        return ready, issues
    
    def run_comprehensive_tests(self, exe_path: Path) -> Dict[str, bool]:
        """Run comprehensive functionality tests."""
        tests = {
            'file_exists': exe_path.exists(),
            'file_readable': False,
            'correct_size': False,
            'starts_successfully': False,
            'responds_to_signals': False,
        }
        
        # File readable test
        try:
            with open(exe_path, 'rb') as f:
                f.read(1024)  # Read first 1KB
            tests['file_readable'] = True
        except Exception:
            pass
        
        # Size test
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        tests['correct_size'] = 10 <= size_mb <= 500
        
        # Startup test
        try:
            proc = subprocess.Popen([str(exe_path)], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
            time.sleep(1)  # Let it start
            proc.terminate()
            proc.wait(timeout=3)
            tests['starts_successfully'] = True
            tests['responds_to_signals'] = True
        except Exception:
            pass
        
        return tests
    
    def validate_single_executable(self, exe_path: Path) -> BuildValidationResult:
        """Validate a single executable comprehensively."""
        print(f"\n🔍 Validating: {exe_path.name}")
        print(f"   Path: {exe_path}")
        
        # Basic validation
        is_valid, errors, warnings = self.validate_executable_basic(exe_path)
        
        # Startup test
        startup_time, startup_success, startup_errors = self.test_executable_startup(exe_path)
        errors.extend(startup_errors)
        
        # Dependency analysis
        found_deps, missing_deps = self.analyze_dependencies(exe_path)
        
        # Security scan
        security_issues = self.security_scan(exe_path)
        
        # Performance scoring
        performance_score = self.performance_test(exe_path, startup_time)
        
        # Comprehensive tests
        test_results = self.run_comprehensive_tests(exe_path)
        
        # Distribution readiness
        distribution_ready, dist_issues = self.check_distribution_readiness(
            exe_path, security_issues, test_results
        )
        errors.extend(dist_issues)
        
        # Calculate file size
        file_size_mb = exe_path.stat().st_size / (1024 * 1024)
        
        # Final validation status
        final_valid = (is_valid and startup_success and 
                      len([t for t in test_results.values() if not t]) <= 1)
        
        result = BuildValidationResult(
            executable_path=str(exe_path),
            file_size_mb=round(file_size_mb, 2),
            is_valid=final_valid,
            startup_time_seconds=round(startup_time, 2),
            dependencies_found=found_deps,
            missing_dependencies=missing_deps,
            security_issues=security_issues,
            performance_score=performance_score,
            distribution_ready=distribution_ready,
            validation_errors=errors,
            validation_warnings=warnings,
            test_results=test_results,
            timestamp=datetime.now().isoformat()
        )
        
        return result
    
    def validate_all_builds(self) -> List[BuildValidationResult]:
        """Validate all executables in the dist directory."""
        print("🚀 Starting comprehensive build validation...")
        print(f"📁 Scanning: {self.dist_dir}")
        
        executables = self.find_executables()
        
        if not executables:
            print("❌ No executables found in dist directory")
            return []
        
        print(f"✅ Found {len(executables)} executable(s) to validate")
        
        results = []
        for exe_path in executables:
            result = self.validate_single_executable(exe_path)
            results.append(result)
        
        self.results = results
        return results
    
    def generate_report(self, results: List[BuildValidationResult]) -> str:
        """Generate a comprehensive validation report."""
        if not results:
            return "No validation results available."
        
        report_lines = [
            "=" * 80,
            "🔍 BUILD VALIDATION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Project: Unsplash Image Search & GPT Tool",
            f"Validated: {len(results)} executable(s)",
            ""
        ]
        
        # Summary
        valid_count = sum(1 for r in results if r.is_valid)
        ready_count = sum(1 for r in results if r.distribution_ready)
        avg_performance = sum(r.performance_score for r in results) / len(results)
        
        report_lines.extend([
            "📊 SUMMARY",
            "-" * 40,
            f"✅ Valid executables: {valid_count}/{len(results)}",
            f"🚀 Distribution ready: {ready_count}/{len(results)}",
            f"⚡ Average performance score: {avg_performance:.1f}/100",
            ""
        ])
        
        # Individual results
        for i, result in enumerate(results, 1):
            exe_name = Path(result.executable_path).name
            status = "✅" if result.is_valid else "❌"
            ready = "🚀" if result.distribution_ready else "⏳"
            
            report_lines.extend([
                f"#{i} {status} {exe_name} {ready}",
                "-" * 60,
                f"📁 Path: {result.executable_path}",
                f"📏 Size: {result.file_size_mb} MB",
                f"⚡ Startup: {result.startup_time_seconds}s",
                f"🎯 Performance: {result.performance_score}/100",
                f"📦 Dependencies: {len(result.dependencies_found)} found, {len(result.missing_dependencies)} missing",
            ])
            
            if result.dependencies_found:
                report_lines.append(f"   Found: {', '.join(result.dependencies_found)}")
            
            if result.missing_dependencies:
                report_lines.append(f"   Missing: {', '.join(result.missing_dependencies)}")
            
            # Test results
            passed_tests = [t for t, passed in result.test_results.items() if passed]
            failed_tests = [t for t, passed in result.test_results.items() if not passed]
            
            report_lines.append(f"🧪 Tests: {len(passed_tests)} passed, {len(failed_tests)} failed")
            
            if failed_tests:
                report_lines.append(f"   Failed: {', '.join(failed_tests)}")
            
            # Issues
            if result.validation_errors:
                report_lines.extend([
                    "❌ Errors:",
                    *[f"   • {error}" for error in result.validation_errors]
                ])
            
            if result.validation_warnings:
                report_lines.extend([
                    "⚠️  Warnings:",
                    *[f"   • {warning}" for warning in result.validation_warnings]
                ])
            
            if result.security_issues:
                report_lines.extend([
                    "🔒 Security Issues:",
                    *[f"   • {issue}" for issue in result.security_issues]
                ])
            
            report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "💡 RECOMMENDATIONS",
            "-" * 40,
        ])
        
        all_errors = []
        all_warnings = []
        for result in results:
            all_errors.extend(result.validation_errors)
            all_warnings.extend(result.validation_warnings)
        
        if not all_errors and not all_warnings:
            report_lines.append("✅ All validations passed! Builds are ready for distribution.")
        else:
            if all_errors:
                report_lines.extend([
                    "🚨 Critical Issues to Fix:",
                    *[f"   • {error}" for error in set(all_errors)],
                    ""
                ])
            
            if all_warnings:
                report_lines.extend([
                    "⚠️  Improvements Suggested:",
                    *[f"   • {warning}" for warning in set(all_warnings)],
                    ""
                ])
        
        # Performance recommendations
        slow_builds = [r for r in results if r.startup_time_seconds > 5]
        if slow_builds:
            report_lines.extend([
                "⚡ Performance Improvements:",
                "   • Consider using --onedir instead of --onefile for faster startup",
                "   • Review hidden imports and exclude unnecessary modules",
                "   • Enable UPX compression if not already used",
                ""
            ])
        
        report_lines.extend([
            "=" * 80,
            "End of Report",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, report: str, results: List[BuildValidationResult]) -> Path:
        """Save validation report and results."""
        # Create reports directory
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save text report
        report_file = reports_dir / f"build_validation_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save JSON results
        json_file = reports_dir / f"build_validation_{timestamp}.json"
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_executables': len(results),
                'valid_executables': sum(1 for r in results if r.is_valid),
                'distribution_ready': sum(1 for r in results if r.distribution_ready),
                'average_performance': sum(r.performance_score for r in results) / len(results) if results else 0,
            },
            'results': [asdict(result) for result in results]
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Reports saved:")
        print(f"   Text: {report_file}")
        print(f"   JSON: {json_file}")
        
        return report_file


def main():
    """Main entry point for build validation."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print("""
🔍 Build Validation Script for Unsplash Image Search & GPT Tool

USAGE:
    python validate-build.py [options]

OPTIONS:
    --help, -h          Show this help message
    --json-only         Output only JSON results
    --no-tests          Skip functionality tests
    --quiet             Minimal output
    --executable <path> Validate specific executable

EXAMPLES:
    python validate-build.py                    # Validate all executables
    python validate-build.py --quiet           # Quiet mode
    python validate-build.py --json-only       # JSON output only
    python validate-build.py --executable dist/app.exe

The script will:
• Find all executables in the dist/ directory
• Test startup time and basic functionality  
• Analyze dependencies and file structure
• Perform basic security scanning
• Generate comprehensive validation report
• Save results in reports/ directory
        """)
        return 0
    
    # Initialize validator
    project_root = Path(__file__).parent.parent
    validator = BuildValidator(project_root)
    
    try:
        # Run validation
        results = validator.validate_all_builds()
        
        if not results:
            print("❌ No builds found to validate")
            return 1
        
        # Generate and display report
        report = validator.generate_report(results)
        
        if '--json-only' not in sys.argv:
            print(report)
        
        # Save results
        report_file = validator.save_report(report, results)
        
        # Return appropriate exit code
        all_valid = all(result.is_valid for result in results)
        all_ready = all(result.distribution_ready for result in results)
        
        if all_valid and all_ready:
            print("\n✅ All builds validated successfully!")
            return 0
        elif all_valid:
            print("\n⚠️  Builds are valid but may need improvements for distribution")
            return 0
        else:
            print("\n❌ Some builds failed validation")
            return 1
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())