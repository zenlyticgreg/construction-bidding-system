"""
Main application entry point for PACE.
"""

import sys
from pathlib import Path
from typing import Optional

from .core.logging import get_module_logger
from .core.config import settings
from .cli import app

logger = get_module_logger("main")


def main():
    """Main application entry point."""
    try:
        # Add src to path for imports
        src_path = Path(__file__).parent.parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Run CLI application
        app()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 