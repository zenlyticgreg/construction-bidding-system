#!/usr/bin/env python3
"""
Test Runner for CalTrans Bidding System

This script provides easy commands to run different types of tests
with various options and configurations.
"""

import subprocess
import sys
import argparse
from pathlib import Path
import os


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def run_unit_tests():
    """Run unit tests only"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-m", "unit", "-v"]
    return run_command(cmd, "Unit Tests")


def run_integration_tests():
    """Run integration tests only"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-m", "integration", "-v"]
    return run_command(cmd, "Integration Tests")


def run_performance_tests():
    """Run performance tests only"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-m", "performance", "-v"]
    return run_command(cmd, "Performance Tests")


def run_all_tests():
    """Run all tests"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    return run_command(cmd, "All Tests")


def run_specific_test_file(test_file):
    """Run a specific test file"""
    if not Path(test_file).exists():
        print(f"❌ Test file {test_file} not found!")
        return False
    
    cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    return run_command(cmd, f"Test File: {test_file}")


def run_tests_with_coverage():
    """Run tests with coverage report"""
    cmd = [
        sys.executable, "-m", "pytest", "tests/", 
        "--cov=src", 
        "--cov-report=html", 
        "--cov-report=term-missing",
        "-v"
    ]
    return run_command(cmd, "Tests with Coverage")


def run_tests_with_parallel():
    """Run tests in parallel"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-n", "auto", "-v"]
    return run_command(cmd, "Tests in Parallel")


def run_tests_except_slow():
    """Run tests excluding slow tests"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-m", "not slow", "-v"]
    return run_command(cmd, "Tests (excluding slow tests)")


def run_extractor_tests():
    """Run extractor tests specifically"""
    return run_specific_test_file("tests/test_extractor.py")


def run_analyzer_tests():
    """Run analyzer tests specifically"""
    return run_specific_test_file("tests/test_analyzer.py")


def run_bidding_tests():
    """Run bidding tests specifically"""
    return run_specific_test_file("tests/test_bidding.py")


def install_test_dependencies():
    """Install test dependencies"""
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    return run_command(cmd, "Installing Test Dependencies")


def check_test_environment():
    """Check if test environment is properly set up"""
    print("🔍 Checking test environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is installed")
    except ImportError:
        print("❌ pytest is not installed")
        return False
    
    # Check if test files exist
    test_files = [
        "tests/test_extractor.py",
        "tests/test_analyzer.py", 
        "tests/test_bidding.py",
        "tests/conftest.py"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file} exists")
        else:
            print(f"❌ {test_file} not found")
            return False
    
    # Check if src directory exists
    if Path("src").exists():
        print("✅ src directory exists")
    else:
        print("❌ src directory not found")
        return False
    
    print("✅ Test environment is ready!")
    return True


def generate_test_report():
    """Generate a comprehensive test report"""
    print("📊 Generating test report...")
    
    # Run tests with coverage and generate report
    cmd = [
        sys.executable, "-m", "pytest", "tests/", 
        "--cov=src", 
        "--cov-report=html:htmlcov", 
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing",
        "--junitxml=test-results.xml",
        "-v"
    ]
    
    success = run_command(cmd, "Test Report Generation")
    
    if success:
        print("\n📈 Test Report Generated:")
        print("  - HTML Coverage Report: htmlcov/index.html")
        print("  - XML Coverage Report: coverage.xml")
        print("  - JUnit XML Report: test-results.xml")
    
    return success


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Test Runner for CalTrans Bidding System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --unit                   # Run unit tests only
  python run_tests.py --integration            # Run integration tests only
  python run_tests.py --performance            # Run performance tests only
  python run_tests.py --coverage               # Run tests with coverage
  python run_tests.py --parallel               # Run tests in parallel
  python run_tests.py --extractor              # Run extractor tests
  python run_tests.py --analyzer               # Run analyzer tests
  python run_tests.py --bidding                # Run bidding tests
  python run_tests.py --check-env              # Check test environment
  python run_tests.py --install-deps           # Install dependencies
  python run_tests.py --report                 # Generate test report
        """
    )
    
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Run all tests"
    )
    parser.add_argument(
        "--unit", 
        action="store_true", 
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration", 
        action="store_true", 
        help="Run integration tests only"
    )
    parser.add_argument(
        "--performance", 
        action="store_true", 
        help="Run performance tests only"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--no-slow", 
        action="store_true", 
        help="Run tests excluding slow tests"
    )
    parser.add_argument(
        "--extractor", 
        action="store_true", 
        help="Run extractor tests specifically"
    )
    parser.add_argument(
        "--analyzer", 
        action="store_true", 
        help="Run analyzer tests specifically"
    )
    parser.add_argument(
        "--bidding", 
        action="store_true", 
        help="Run bidding tests specifically"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Run a specific test file"
    )
    parser.add_argument(
        "--check-env", 
        action="store_true", 
        help="Check test environment"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true", 
        help="Install test dependencies"
    )
    parser.add_argument(
        "--report", 
        action="store_true", 
        help="Generate comprehensive test report"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("🏗️  CalTrans Bidding System - Test Runner")
    print("=" * 50)
    
    # Handle different test options
    success = True
    
    if args.check_env:
        success = check_test_environment()
    
    elif args.install_deps:
        success = install_test_dependencies()
    
    elif args.report:
        success = generate_test_report()
    
    elif args.all:
        success = run_all_tests()
    
    elif args.unit:
        success = run_unit_tests()
    
    elif args.integration:
        success = run_integration_tests()
    
    elif args.performance:
        success = run_performance_tests()
    
    elif args.coverage:
        success = run_tests_with_coverage()
    
    elif args.parallel:
        success = run_tests_with_parallel()
    
    elif args.no_slow:
        success = run_tests_except_slow()
    
    elif args.extractor:
        success = run_extractor_tests()
    
    elif args.analyzer:
        success = run_analyzer_tests()
    
    elif args.bidding:
        success = run_bidding_tests()
    
    elif args.file:
        success = run_specific_test_file(args.file)
    
    else:
        # Default: run all tests
        print("No specific test type specified. Running all tests...")
        success = run_all_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 