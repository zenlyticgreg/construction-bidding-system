"""
PACE - Project Analysis & Construction Estimating

Intelligent Construction Estimating Platform
Powered by Squires Lumber
"""

__version__ = "1.0.0"
__author__ = "PACE Development Team"
__email__ = "support@pace-construction.com"
__description__ = "Intelligent Construction Estimating Platform"

# Core imports
from .core.config import Settings
from .core.logging import setup_logging

# Initialize logging
setup_logging()

# Version info
__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__description__",
    "Settings",
    "setup_logging",
] 