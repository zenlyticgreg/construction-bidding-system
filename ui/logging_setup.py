"""
Logging Setup for UI Components

Configures logging for the PACE UI components to write to the logs directory.
"""

import logging
import logging.config
import os
from datetime import datetime


def setup_ui_logging():
    """Setup logging configuration for UI components."""
    
    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',  # Only show warnings and errors in console
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': os.path.join(logs_dir, 'ui_app.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': os.path.join(logs_dir, 'ui_errors.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'ui': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'ui.components': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'ui.demo_app': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',  # Only show warnings and errors in console
            'handlers': ['console', 'file']
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Create logger for UI (silent setup)
    logger = logging.getLogger('ui')
    
    return logger


def get_ui_logger(name=None):
    """Get a logger for UI components."""
    if name:
        return logging.getLogger(f'ui.{name}')
    return logging.getLogger('ui')


def log_app_start():
    """Log application startup."""
    logger = get_ui_logger('demo_app')
    logger.info("PACE UI Application Starting")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def log_app_stop():
    """Log application shutdown."""
    logger = get_ui_logger('demo_app')
    logger.info("PACE UI Application Stopping")
    logger.info(f"Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def log_page_navigation(from_page, to_page):
    """Log page navigation."""
    logger = get_ui_logger('demo_app')
    logger.info(f"Navigation: {from_page} -> {to_page}")


def log_button_click(button_name, page=None):
    """Log button clicks."""
    logger = get_ui_logger('demo_app')
    if page:
        logger.info(f"Button Click: {button_name} on page {page}")
    else:
        logger.info(f"Button Click: {button_name}")


def log_file_upload(filename, file_size, success=True):
    """Log file upload events."""
    logger = get_ui_logger('file_upload')
    if success:
        logger.info(f"File Upload Success: {filename} ({file_size} bytes)")
    else:
        logger.error(f"File Upload Failed: {filename} ({file_size} bytes)")


def log_error(error_msg, error_type="Error", component="unknown"):
    """Log errors with component context."""
    logger = get_ui_logger(component)
    logger.error(f"{error_type}: {error_msg}") 