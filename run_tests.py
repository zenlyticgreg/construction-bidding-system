#!/usr/bin/env python3
"""
Test Runner for PACE - Project Analysis & Construction Estimating

This script provides a comprehensive test suite for the PACE construction bidding automation platform.
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Import test modules
try:
    import pytest
    from pytest import Session
except ImportError:
    print("❌ pytest not installed. Please install with: pip install pytest")
    sys.exit(1)

# Test configuration
TEST_CONFIG = {
    'test_directories': [
        'tests/',
        'src/',
    ],
    'test_patterns': [
        'test_*.py',
        '*_test.py',
    ],
    'exclude_patterns': [
        '__pycache__',
        '.pytest_cache',
        'venv',
        '.git',
    ],
    'coverage_target': 80.0,
    'timeout_seconds': 300,  # 5 minutes
}

# Test categories
TEST_CATEGORIES = {
    'unit': {
        'description': 'Unit tests for individual components',
        'pattern': 'test_*.py',
        'directories': ['tests/'],
    },
    'integration': {
        'description': 'Integration tests for component interactions',
        'pattern': 'test_*.py',
        'directories': ['tests/'],
    },
    'functional': {
        'description': 'Functional tests for complete workflows',
        'pattern': 'test_*.py',
        'directories': ['tests/'],
    },
    'performance': {
        'description': 'Performance and load tests',
        'pattern': 'test_performance_*.py',
        'directories': ['tests/'],
    },
    'all': {
        'description': 'All tests',
        'pattern': 'test_*.py',
        'directories': ['tests/', 'src/'],
    }
}

class TestRunner:
    """Comprehensive test runner for PACE."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or TEST_CONFIG
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'duration': 0,
            'coverage': 0,
        }
        self.start_time = None
        self.end_time = None
    
    def run_tests(self, category: str = 'all', verbose: bool = False, 
                  coverage: bool = False, parallel: bool = False) -> Dict[str, Any]:
        """
        Run tests for the specified category.
        
        Args:
            category: Test category to run
            verbose: Enable verbose output
            coverage: Enable coverage reporting
            parallel: Run tests in parallel
            
        Returns:
            Test results dictionary
        """
        print(f"📊 PACE - Project Analysis & Construction Estimating - Test Runner")
        print(f"🔍 Running {category} tests...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Build pytest arguments
        args = self._build_pytest_args(category, verbose, coverage, parallel)
        
        try:
            # Run pytest
            result = pytest.main(args)
            
            # Parse results
            self._parse_results(result)
            
        except Exception as e:
            print(f"❌ Error running tests: {str(e)}")
            self.results['errors'] += 1
        
        self.end_time = time.time()
        self.results['duration'] = self.end_time - self.start_time
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _build_pytest_args(self, category: str, verbose: bool, 
                          coverage: bool, parallel: bool) -> List[str]:
        """Build pytest command line arguments."""
        args = []
        
        # Test directories and patterns
        if category in TEST_CATEGORIES:
            cat_config = TEST_CATEGORIES[category]
            for directory in cat_config['directories']:
                if Path(directory).exists():
                    args.append(directory)
        else:
            # Default to all tests
            args.extend(['tests/', 'src/'])
        
        # Verbose output
        if verbose:
            args.append('-v')
        
        # Coverage
        if coverage:
            args.extend([
                '--cov=src',
                '--cov=tests',
                '--cov-report=html:htmlcov',
                '--cov-report=term-missing',
                f'--cov-fail-under={self.config["coverage_target"]}'
            ])
        
        # Parallel execution
        if parallel:
            args.extend(['-n', 'auto'])
        
        # Additional options
        args.extend([
            '--tb=short',
            '--strict-markers',
            '--disable-warnings',
            '--color=yes'
        ])
        
        return args
    
    def _parse_results(self, result: int):
        """Parse pytest results."""
        # This is a simplified parser - in practice, you'd use pytest hooks
        # to capture detailed results
        if result == 0:
            self.results['passed'] += 1
        elif result == 1:
            self.results['failed'] += 1
        elif result == 2:
            self.results['errors'] += 1
        elif result == 5:
            self.results['skipped'] += 1
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        duration = self.results['duration']
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏭️  Skipped: {self.results['skipped']}")
        print(f"💥 Errors: {self.results['errors']}")
        
        if self.results['coverage'] > 0:
            print(f"📊 Coverage: {self.results['coverage']:.1f}%")
        
        # Overall status
        if self.results['failed'] == 0 and self.results['errors'] == 0:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Please review the output above.")
        
        print("=" * 60)

def run_unit_tests(verbose: bool = False) -> Dict[str, Any]:
    """Run unit tests."""
    runner = TestRunner()
    return runner.run_tests('unit', verbose=verbose)

def run_integration_tests(verbose: bool = False) -> Dict[str, Any]:
    """Run integration tests."""
    runner = TestRunner()
    return runner.run_tests('integration', verbose=verbose)

def run_functional_tests(verbose: bool = False) -> Dict[str, Any]:
    """Run functional tests."""
    runner = TestRunner()
    return runner.run_tests('functional', verbose=verbose)

def run_performance_tests(verbose: bool = False) -> Dict[str, Any]:
    """Run performance tests."""
    runner = TestRunner()
    return runner.run_tests('performance', verbose=verbose)

def run_all_tests(verbose: bool = False, coverage: bool = False, 
                  parallel: bool = False) -> Dict[str, Any]:
    """Run all tests."""
    runner = TestRunner()
    return runner.run_tests('all', verbose=verbose, coverage=coverage, parallel=parallel)

def check_test_environment() -> bool:
    """Check if test environment is properly set up."""
    print("🔍 Checking test environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python {python_version.major}.{python_version.minor} not supported. Need 3.8+")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required packages
    required_packages = [
        'pytest',
        'pytest-cov',
        'pytest-xdist',
        'pytest-html',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # Check test directories
    test_dirs = ['tests/', 'src/']
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print(f"✅ {test_dir}")
        else:
            print(f"❌ {test_dir} not found")
    
    print("✅ Test environment check complete")
    return True

def generate_test_report(results: Dict[str, Any], output_file: str = None):
    """Generate a test report."""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'application': 'PACE - Project Analysis & Construction Estimating',
        'version': '1.0.0',
        'results': results,
        'summary': {
            'status': 'PASS' if results['failed'] == 0 and results['errors'] == 0 else 'FAIL',
            'total_tests': results['total_tests'],
            'success_rate': (results['passed'] / max(results['total_tests'], 1)) * 100,
        }
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Test report saved to: {output_file}")
    
    return report

def main():
    """Main function for command line interface."""
    parser = argparse.ArgumentParser(
        description="Test Runner for PACE - Project Analysis & Construction Estimating",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --verbose          # Run with verbose output
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --parallel         # Run tests in parallel
  python run_tests.py --check            # Check test environment
        """
    )
    
    # Test category options
    parser.add_argument('--unit', action='store_true', 
                       help='Run unit tests only')
    parser.add_argument('--integration', action='store_true',
                       help='Run integration tests only')
    parser.add_argument('--functional', action='store_true',
                       help='Run functional tests only')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    
    # Test execution options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Enable coverage reporting')
    parser.add_argument('--parallel', '-p', action='store_true',
                       help='Run tests in parallel')
    parser.add_argument('--check', action='store_true',
                       help='Check test environment')
    
    # Output options
    parser.add_argument('--report', '-r', type=str,
                       help='Generate test report file')
    parser.add_argument('--output', '-o', type=str,
                       help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Check environment if requested
    if args.check:
        if check_test_environment():
            print("✅ Test environment is ready")
            return 0
        else:
            print("❌ Test environment needs setup")
            return 1
    
    # Determine test category
    if args.unit:
        category = 'unit'
        test_func = run_unit_tests
    elif args.integration:
        category = 'integration'
        test_func = run_integration_tests
    elif args.functional:
        category = 'functional'
        test_func = run_functional_tests
    elif args.performance:
        category = 'performance'
        test_func = run_performance_tests
    else:
        category = 'all'
        test_func = run_all_tests
    
    # Run tests
    try:
        results = test_func(verbose=args.verbose)
        
        # Generate report if requested
        if args.report:
            generate_test_report(results, args.report)
        
        # Return appropriate exit code
        if results['failed'] == 0 and results['errors'] == 0:
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error during test execution: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 