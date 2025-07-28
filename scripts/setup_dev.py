#!/usr/bin/env python3
"""
Development setup script for PACE project.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(command: List[str], cwd: Optional[Path] = None) -> bool:
    """Run a command and return success status."""
    try:
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def create_virtual_environment() -> bool:
    """Create a virtual environment."""
    if Path("venv").exists():
        print("✓ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    return run_command([sys.executable, "-m", "venv", "venv"])


def install_dependencies() -> bool:
    """Install project dependencies."""
    print("Installing dependencies...")
    
    # Determine the pip command based on the platform
    if sys.platform == "win32":
        pip_cmd = ["venv\\Scripts\\pip"]
    else:
        pip_cmd = ["venv/bin/pip"]
    
    # Install in development mode
    if not run_command(pip_cmd + ["install", "-e", ".[dev]"]):
        return False
    
    print("✓ Dependencies installed successfully")
    return True


def setup_pre_commit() -> bool:
    """Setup pre-commit hooks."""
    print("Setting up pre-commit hooks...")
    
    # Determine the pre-commit command based on the platform
    if sys.platform == "win32":
        pre_commit_cmd = ["venv\\Scripts\\pre-commit"]
    else:
        pre_commit_cmd = ["venv/bin/pre-commit"]
    
    if not run_command(pre_commit_cmd + ["install"]):
        return False
    
    print("✓ Pre-commit hooks installed")
    return True


def create_directories() -> bool:
    """Create necessary directories."""
    print("Creating directories...")
    
    directories = [
        "data",
        "data/uploads",
        "data/temp",
        "data/backups",
        "logs",
        "output",
        "output/bids",
        "output/reports",
        "output/catalogs",
        "docs",
        "tests/fixtures",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created")
    return True


def create_env_file() -> bool:
    """Create .env file from example."""
    if Path(".env").exists():
        print("✓ .env file already exists")
        return True
    
    if Path("env.example").exists():
        import shutil
        shutil.copy("env.example", ".env")
        print("✓ .env file created from env.example")
        return True
    
    print("⚠ No env.example found, skipping .env creation")
    return True


def run_initial_tests() -> bool:
    """Run initial tests to verify setup."""
    print("Running initial tests...")
    
    # Determine the pytest command based on the platform
    if sys.platform == "win32":
        pytest_cmd = ["venv\\Scripts\\pytest"]
    else:
        pytest_cmd = ["venv/bin/pytest"]
    
    if not run_command(pytest_cmd + ["tests/", "-v"]):
        print("⚠ Some tests failed, but setup continues")
        return True
    
    print("✓ All tests passed")
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up PACE development environment...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup pre-commit
    if not setup_pre_commit():
        print("❌ Failed to setup pre-commit hooks")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Run initial tests
    if not run_initial_tests():
        print("❌ Failed to run initial tests")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 PACE development environment setup complete!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Edit .env file with your configuration")
    print("3. Run 'make help' to see available commands")
    print("4. Run 'python -m pace.cli.main init' to initialize the application")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    main() 