#!/usr/bin/env python3
"""
Test Coverage Report Generator for Notes System
Generates comprehensive coverage reports and identifies testing gaps
"""

import pytest
import coverage
import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add src to path for imports
sys_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(sys_path))


class TestCoverageReporter:
    """Generate and analyze test coverage reports"""
    
    def __init__(self, source_dir="src", test_dir="tests"):
        self.source_dir = Path(source_dir)
        self.test_dir = Path(test_dir)
        self.cov = None
        self.report_data = {}
    
    def setup_coverage(self):
        """Setup coverage measurement"""
        self.cov = coverage.Coverage(
            source=[str(self.source_dir)],
            omit=[
                "*/test_*",
                "*/tests/*",
                "*/__pycache__/*",
                "*/venv/*",
                "*/env/*"
            ]
        )
        self.cov.start()
    
    def stop_coverage(self):
        """Stop coverage measurement"""
        if self.cov:
            self.cov.stop()
            self.cov.save()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report"""
        if not self.cov:
            raise RuntimeError("Coverage not initialized")
        
        # Generate coverage data
        coverage_data = self.cov.get_data()
        
        # Analyze coverage by file
        file_coverage = {}
        total_statements = 0
        total_missing = 0
        
        for filename in coverage_data.measured_files():
            if str(self.source_dir) in filename:
                analysis = self.cov._analyze(filename)
                statements = len(analysis.statements)
                missing = len(analysis.missing)
                covered = statements - missing
                
                if statements > 0:
                    percentage = (covered / statements) * 100
                else:
                    percentage = 100.0
                
                rel_filename = Path(filename).relative_to(Path.cwd())
                file_coverage[str(rel_filename)] = {
                    'statements': statements,
                    'missing': missing,
                    'covered': covered,
                    'percentage': round(percentage, 2),
                    'missing_lines': list(analysis.missing)
                }
                
                total_statements += statements
                total_missing += missing
        
        # Calculate overall coverage
        if total_statements > 0:
            overall_percentage = ((total_statements - total_missing) / total_statements) * 100
        else:
            overall_percentage = 100.0
        
        # Generate detailed report
        self.report_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_coverage': {
                'percentage': round(overall_percentage, 2),
                'statements': total_statements,
                'covered': total_statements - total_missing,
                'missing': total_missing
            },
            'file_coverage': file_coverage,
            'test_summary': self._analyze_test_structure(),
            'coverage_gaps': self._identify_coverage_gaps(file_coverage),
            'recommendations': self._generate_recommendations(file_coverage)
        }
        
        return self.report_data
    
    def _analyze_test_structure(self) -> Dict[str, Any]:
        """Analyze test file structure and organization"""
        test_files = list(self.test_dir.rglob("test_*.py"))
        
        test_categories = {
            'unit': [],
            'integration': [],
            'e2e': [],
            'performance': [],
            'regression': [],
            'accessibility': [],
            'compatibility': [],
            'fixtures': []
        }
        
        for test_file in test_files:
            relative_path = test_file.relative_to(self.test_dir)
            category = str(relative_path.parts[0]) if len(relative_path.parts) > 1 else 'unit'
            
            if category in test_categories:
                test_categories[category].append(str(relative_path))
            else:
                test_categories['unit'].append(str(relative_path))
        
        return {
            'total_test_files': len(test_files),
            'by_category': {k: len(v) for k, v in test_categories.items()},
            'test_files': test_categories
        }
    
    def _identify_coverage_gaps(self, file_coverage: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify areas with low or missing coverage"""
        gaps = {
            'uncovered_files': [],
            'low_coverage_files': [],  # < 80%
            'missing_critical_paths': [],
            'untested_functions': []
        }
        
        for filename, coverage_info in file_coverage.items():
            percentage = coverage_info['percentage']
            
            if percentage == 0:
                gaps['uncovered_files'].append(filename)
            elif percentage < 80:
                gaps['low_coverage_files'].append({
                    'file': filename,
                    'coverage': percentage,
                    'missing_lines': coverage_info['missing_lines']
                })
            
            # Check for critical paths
            if 'notes_manager' in filename.lower() and percentage < 90:
                gaps['missing_critical_paths'].append({
                    'file': filename,
                    'coverage': percentage,
                    'reason': 'Core notes functionality'
                })
            
            if 'ui/notes' in filename.lower() and percentage < 85:
                gaps['missing_critical_paths'].append({
                    'file': filename,
                    'coverage': percentage,
                    'reason': 'UI notes functionality'
                })
        
        return gaps
    
    def _generate_recommendations(self, file_coverage: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving test coverage"""
        recommendations = []
        
        # Overall coverage recommendations
        overall_coverage = sum(info['covered'] for info in file_coverage.values())
        overall_statements = sum(info['statements'] for info in file_coverage.values())
        
        if overall_statements > 0:
            overall_percentage = (overall_coverage / overall_statements) * 100
        else:
            overall_percentage = 100
        
        if overall_percentage < 80:
            recommendations.append("Overall coverage is below 80%. Focus on adding unit tests for core functionality.")
        elif overall_percentage < 90:
            recommendations.append("Good coverage overall. Focus on edge cases and error handling paths.")
        else:
            recommendations.append("Excellent coverage! Consider adding more integration and E2E tests.")
        
        # File-specific recommendations
        for filename, info in file_coverage.items():
            if info['percentage'] < 70:
                recommendations.append(f"High priority: Add tests for {filename} ({info['percentage']:.1f}% coverage)")
            elif info['percentage'] < 85 and 'notes' in filename.lower():
                recommendations.append(f"Medium priority: Improve coverage for {filename} ({info['percentage']:.1f}% coverage)")
        
        # Test type recommendations
        if not any('integration' in rec for rec in recommendations):
            recommendations.append("Consider adding more integration tests to verify component interactions.")
        
        if not any('e2e' in rec for rec in recommendations):
            recommendations.append("Consider adding end-to-end tests for complete user workflows.")
        
        if not any('performance' in rec for rec in recommendations):
            recommendations.append("Add performance tests to ensure scalability with large datasets.")
        
        return recommendations
    
    def save_report(self, filename: str = "coverage_report.json"):
        """Save coverage report to file"""
        if not self.report_data:
            raise RuntimeError("No report data available. Generate report first.")
        
        with open(filename, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        print(f"Coverage report saved to {filename}")
    
    def print_summary(self):
        """Print coverage summary to console"""
        if not self.report_data:
            raise RuntimeError("No report data available. Generate report first.")
        
        overall = self.report_data['overall_coverage']
        
        print("\n" + "="*60)
        print("NOTES SYSTEM TEST COVERAGE REPORT")
        print("="*60)
        print(f"Generated: {self.report_data['timestamp']}")
        print(f"\nOVERALL COVERAGE: {overall['percentage']:.1f}%")
        print(f"Statements: {overall['statements']}")
        print(f"Covered: {overall['covered']}")
        print(f"Missing: {overall['missing']}")
        
        print("\nFILE COVERAGE BREAKDOWN:")
        print("-" * 60)
        
        for filename, info in self.report_data['file_coverage'].items():
            status = "✓" if info['percentage'] >= 80 else "⚠" if info['percentage'] >= 60 else "✗"
            print(f"{status} {filename:<40} {info['percentage']:>6.1f}% ({info['covered']}/{info['statements']})")
        
        print("\nTEST STRUCTURE:")
        print("-" * 60)
        test_summary = self.report_data['test_summary']
        print(f"Total test files: {test_summary['total_test_files']}")
        
        for category, count in test_summary['by_category'].items():
            if count > 0:
                print(f"  {category.title()}: {count} files")
        
        print("\nCOVERAGE GAPS:")
        print("-" * 60)
        gaps = self.report_data['coverage_gaps']
        
        if gaps['uncovered_files']:
            print(f"⚠ {len(gaps['uncovered_files'])} files with no coverage:")
            for file in gaps['uncovered_files']:
                print(f"  - {file}")
        
        if gaps['low_coverage_files']:
            print(f"⚠ {len(gaps['low_coverage_files'])} files with low coverage (<80%):")
            for item in gaps['low_coverage_files']:
                print(f"  - {item['file']}: {item['coverage']:.1f}%")
        
        if gaps['missing_critical_paths']:
            print(f"✗ {len(gaps['missing_critical_paths'])} critical paths need attention:")
            for item in gaps['missing_critical_paths']:
                print(f"  - {item['file']}: {item['coverage']:.1f}% ({item['reason']})")
        
        print("\nRECOMMENDATIONS:")
        print("-" * 60)
        for i, recommendation in enumerate(self.report_data['recommendations'], 1):
            print(f"{i}. {recommendation}")
        
        print("\n" + "="*60)


def run_coverage_analysis():
    """Run comprehensive coverage analysis"""
    reporter = TestCoverageReporter()
    
    # Setup and run coverage
    reporter.setup_coverage()
    
    try:
        # Import and run tests to measure coverage
        # This would typically be done by running pytest with coverage
        print("Running coverage analysis...")
        
        # Import all source modules to measure potential coverage
        try:
            from notes_manager import NotesManager
            from ui.notes import NotesManager as UINotesManager, RichNote, NoteType, Priority
            from ui.formatter import TerminalFormatter
        except ImportError as e:
            print(f"Warning: Could not import some modules: {e}")
        
        # Generate report
        report_data = reporter.generate_report()
        
        # Print summary
        reporter.print_summary()
        
        # Save detailed report
        reporter.save_report()
        
        return report_data
    
    finally:
        reporter.stop_coverage()


class TestCoverageMetrics:
    """Test coverage metrics and thresholds"""
    
    def test_minimum_coverage_threshold(self):
        """Test that minimum coverage thresholds are met"""
        reporter = TestCoverageReporter()
        reporter.setup_coverage()
        
        try:
            # Import modules to measure
            from notes_manager import NotesManager
            from ui.notes import NotesManager as UINotesManager
            
            report = reporter.generate_report()
            overall_coverage = report['overall_coverage']['percentage']
            
            # Assert minimum coverage thresholds
            assert overall_coverage >= 70, f"Overall coverage {overall_coverage:.1f}% is below minimum threshold of 70%"
            
            # Check critical files
            critical_files = [
                'notes_manager.py',
                'ui/notes.py'
            ]
            
            for critical_file in critical_files:
                matching_files = [f for f in report['file_coverage'].keys() if critical_file in f]
                if matching_files:
                    for file_path in matching_files:
                        file_coverage = report['file_coverage'][file_path]['percentage']
                        assert file_coverage >= 80, f"Critical file {file_path} coverage {file_coverage:.1f}% is below 80%"
        
        finally:
            reporter.stop_coverage()
    
    def test_test_file_organization(self):
        """Test that test files are properly organized"""
        reporter = TestCoverageReporter()
        test_summary = reporter._analyze_test_structure()
        
        # Should have multiple test categories
        categories_with_tests = [cat for cat, count in test_summary['by_category'].items() if count > 0]
        assert len(categories_with_tests) >= 4, f"Expected at least 4 test categories, found {len(categories_with_tests)}"
        
        # Should have unit tests
        assert test_summary['by_category']['unit'] > 0, "No unit tests found"
        
        # Should have integration tests
        assert test_summary['by_category']['integration'] > 0, "No integration tests found"
        
        # Total test files should be reasonable
        assert test_summary['total_test_files'] >= 5, f"Expected at least 5 test files, found {test_summary['total_test_files']}"
    
    def test_coverage_gap_detection(self):
        """Test coverage gap detection"""
        # Mock coverage data for testing
        mock_coverage = {
            'src/notes_manager.py': {
                'statements': 100,
                'missing': 10,
                'covered': 90,
                'percentage': 90.0,
                'missing_lines': [45, 67, 89]
            },
            'src/ui/notes.py': {
                'statements': 200,
                'missing': 50,
                'covered': 150,
                'percentage': 75.0,
                'missing_lines': list(range(100, 150))
            },
            'src/utils.py': {
                'statements': 50,
                'missing': 50,
                'covered': 0,
                'percentage': 0.0,
                'missing_lines': list(range(1, 51))
            }
        }
        
        reporter = TestCoverageReporter()
        gaps = reporter._identify_coverage_gaps(mock_coverage)
        
        # Should identify uncovered files
        assert 'src/utils.py' in gaps['uncovered_files']
        
        # Should identify low coverage files
        low_coverage_files = [item['file'] for item in gaps['low_coverage_files']]
        assert 'src/ui/notes.py' in low_coverage_files
        
        # Should identify critical paths
        critical_paths = [item['file'] for item in gaps['missing_critical_paths']]
        assert 'src/ui/notes.py' in critical_paths  # UI functionality with <85% coverage
    
    def test_recommendation_generation(self):
        """Test recommendation generation"""
        # Mock coverage data
        mock_coverage = {
            'src/notes_manager.py': {
                'statements': 100,
                'missing': 30,
                'covered': 70,
                'percentage': 70.0,
                'missing_lines': []
            },
            'src/ui/notes.py': {
                'statements': 200,
                'missing': 20,
                'covered': 180,
                'percentage': 90.0,
                'missing_lines': []
            }
        }
        
        reporter = TestCoverageReporter()
        recommendations = reporter._generate_recommendations(mock_coverage)
        
        # Should have recommendations
        assert len(recommendations) > 0
        
        # Should recommend improving low coverage files
        high_priority_rec = any('High priority' in rec and 'notes_manager.py' in rec for rec in recommendations)
        assert high_priority_rec, "Should recommend improving notes_manager.py coverage"


def main():
    """Main function to run coverage analysis"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Run coverage tests
        pytest.main([__file__ + '::TestCoverageMetrics', '-v'])
    else:
        # Run coverage analysis
        run_coverage_analysis()


if __name__ == '__main__':
    main()
