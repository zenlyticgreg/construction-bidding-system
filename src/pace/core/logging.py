"""
Logging configuration for PACE application.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from .config import settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    rotation: str = "10 MB",
    retention: str = "30 days",
    format: Optional[str] = None,
) -> None:
    """
    Setup logging configuration for the PACE application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        rotation: Log rotation size/time
        retention: Log retention period
        format: Log message format
    """
    # Remove default logger
    logger.remove()
    
    # Use settings if not provided
    level = level or settings.logging.level
    log_file = log_file or settings.logging.file_path
    format = format or settings.logging.format
    
    # Console handler
    logger.add(
        sys.stdout,
        level=level,
        format=format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # File handler (if specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            level=level,
            format=format,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True,
        )
    
    # Error file handler
    error_log_file = settings.logs_dir / "pace_errors.log"
    logger.add(
        error_log_file,
        level="ERROR",
        format=format,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        filter=lambda record: record["level"].name == "ERROR",
    )
    
    # Intercept standard library logging
    logger.add(
        lambda msg: print(msg, end=""),
        level=level,
        format=format,
        filter=lambda record: record["extra"].get("name") == "stdlib",
    )


def get_logger(name: str):
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Create module-specific loggers
def get_module_logger(module_name: str):
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Logger instance for the module
    """
    return get_logger(f"pace.{module_name}")


# Initialize logging when module is imported
setup_logging() 