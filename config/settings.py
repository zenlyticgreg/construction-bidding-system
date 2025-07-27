"""
Application settings and configuration for Caltrans Bidding System.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Environment settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # development, staging, production
DEBUG = ENVIRONMENT == 'development'

# Database paths
DATABASE_CONFIG = {
    'development': {
        'sqlite_path': BASE_DIR / 'data' / 'caltrans_bidding_dev.db',
        'backup_path': BASE_DIR / 'data' / 'backups',
        'cache_path': BASE_DIR / 'data' / 'cache',
    },
    'production': {
        'sqlite_path': BASE_DIR / 'data' / 'caltrans_bidding_prod.db',
        'backup_path': BASE_DIR / 'data' / 'backups',
        'cache_path': BASE_DIR / 'data' / 'cache',
    }
}

# Get current environment database config
DB_CONFIG = DATABASE_CONFIG.get(ENVIRONMENT, DATABASE_CONFIG['development'])

# Default markup percentages for different project types
MARKUP_PERCENTAGES = {
    'highway_construction': {
        'materials': 20.0,      # 20% markup on materials
        'labor': 25.0,          # 25% markup on labor
        'equipment': 20.0,      # 20% markup on equipment
        'overhead': 12.0,       # 12% overhead
        'profit': 8.0,          # 8% profit margin
    },
    'bridge_construction': {
        'materials': 20.0,      # 20% markup on materials
        'labor': 28.0,          # 28% markup on labor
        'equipment': 22.0,      # 22% markup on equipment
        'overhead': 15.0,       # 15% overhead
        'profit': 10.0,         # 10% profit margin
    },
    'maintenance': {
        'materials': 20.0,      # 20% markup on materials
        'labor': 20.0,          # 20% markup on labor
        'equipment': 15.0,      # 15% markup on equipment
        'overhead': 10.0,       # 10% overhead
        'profit': 6.0,          # 6% profit margin
    },
    'default': {
        'materials': 20.0,      # 20% default markup
        'labor': 25.0,
        'equipment': 20.0,
        'overhead': 12.0,
        'profit': 8.0,
    }
}

# Delivery fee settings
DELIVERY_FEE_CONFIG = {
    'percentage': 3.0,          # 3% delivery fee
    'minimum_amount': 150.0,    # $150 minimum delivery fee
    'maximum_amount': 5000.0,   # $5000 maximum delivery fee
    'free_delivery_threshold': 10000.0,  # Free delivery for orders over $10,000
    'rush_delivery_multiplier': 1.5,     # 50% additional for rush delivery
}

# File upload limits and configurations
FILE_UPLOAD_CONFIG = {
    'max_file_size': 100 * 1024 * 1024,  # 100MB max file size
    'allowed_extensions': [
        '.pdf', '.PDF',
        '.xlsx', '.xls',
        '.docx', '.doc',
        '.txt', '.csv'
    ],
    'upload_directory': BASE_DIR / 'data' / 'uploads',
    'temp_directory': BASE_DIR / 'data' / 'temp',
    'max_files_per_upload': 10,
    'auto_cleanup_temp_files': True,
    'cleanup_after_hours': 24,
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG' if DEBUG else 'INFO',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'caltrans_bidding.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'level': 'INFO',
            'formatter': 'detailed',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'level': 'ERROR',
            'formatter': 'detailed',
        }
    },
    'loggers': {
        'caltrans_bidding': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'src.extractors': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'src.analyzers': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'src.bidding': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    }
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': 'Caltrans Bidding System',
    'page_icon': '🏗️',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'theme': {
        'primaryColor': '#1f77b4',
        'backgroundColor': '#ffffff',
        'secondaryBackgroundColor': '#f0f2f6',
        'textColor': '#262730',
    }
}

# PDF processing configuration
PDF_CONFIG = {
    'extraction_timeout': 300,  # 5 minutes
    'max_pages_per_document': 1000,
    'ocr_enabled': True,
    'ocr_language': 'eng',
    'table_extraction': True,
    'image_extraction': False,
    'text_cleaning': True,
}

# Bidding analysis configuration
BIDDING_CONFIG = {
    'historical_data_years': 5,  # Years of historical data to analyze
    'competitor_analysis': True,
    'market_trend_analysis': True,
    'risk_assessment': True,
    'confidence_threshold': 0.75,  # Minimum confidence for recommendations
    'max_competitors_analyzed': 10,
}

# Output configuration
OUTPUT_CONFIG = {
    'reports_directory': BASE_DIR / 'output' / 'reports',
    'bids_directory': BASE_DIR / 'output' / 'bids',
    'catalogs_directory': BASE_DIR / 'output' / 'catalogs',
    'export_formats': ['xlsx', 'pdf', 'csv'],
    'default_export_format': 'xlsx',
    'include_charts': True,
    'include_summary': True,
}

# Security configuration
SECURITY_CONFIG = {
    'session_timeout': 3600,  # 1 hour
    'max_login_attempts': 5,
    'password_min_length': 8,
    'require_special_chars': True,
    'data_encryption': ENVIRONMENT == 'production',
}

# Performance configuration
PERFORMANCE_CONFIG = {
    'max_concurrent_extractions': 3,
    'cache_enabled': True,
    'cache_ttl': 3600,  # 1 hour
    'batch_size': 100,
    'memory_limit': 1024 * 1024 * 1024,  # 1GB
}

# Waste factors for different materials
WASTE_FACTORS = {
    'concrete': {
        'structural_concrete': 0.05,      # 5% waste factor
        'lightweight_concrete': 0.08,     # 8% waste factor
        'high_performance_concrete': 0.06, # 6% waste factor
        'fiber_reinforced_concrete': 0.07, # 7% waste factor
    },
    'reinforcement': {
        'rebar': 0.10,                    # 10% waste factor
        'wire_mesh': 0.05,                # 5% waste factor
        'post_tensioning': 0.08,          # 8% waste factor
        'fiber_reinforcement': 0.03,      # 3% waste factor
    },
    'formwork': {
        'plywood': 0.15,                  # 15% waste factor
        'steel_forms': 0.02,              # 2% waste factor
        'aluminum_forms': 0.01,           # 1% waste factor
        'shoring': 0.05,                  # 5% waste factor
    },
    'aggregate': {
        'fine_aggregate': 0.08,           # 8% waste factor
        'coarse_aggregate': 0.10,         # 10% waste factor
        'lightweight_aggregate': 0.12,    # 12% waste factor
    },
    'cement': {
        'type_i': 0.03,                   # 3% waste factor
        'type_ii': 0.03,                  # 3% waste factor
        'type_iii': 0.04,                 # 4% waste factor
        'blended': 0.03,                  # 3% waste factor
    }
}

# Productivity factors for estimating
PRODUCTIVITY_FACTORS = {
    'concrete_placement': {
        'bridge_deck': {
            'base_rate': 20.0,            # cubic yards per hour
            'crew_size': 8,
            'weather_factor': 0.8,        # 20% reduction in bad weather
            'access_factor': 0.9,         # 10% reduction for difficult access
            'quality_factor': 0.95,       # 5% reduction for high quality requirements
        },
        'bridge_abutment': {
            'base_rate': 15.0,            # cubic yards per hour
            'crew_size': 6,
            'weather_factor': 0.8,
            'access_factor': 0.85,
            'quality_factor': 0.95,
        },
        'bridge_pier': {
            'base_rate': 12.0,            # cubic yards per hour
            'crew_size': 5,
            'weather_factor': 0.8,
            'access_factor': 0.9,
            'quality_factor': 0.95,
        }
    },
    'formwork_installation': {
        'wall_forms': {
            'base_rate': 100.0,           # square feet per hour
            'crew_size': 4,
            'complexity_factor': 0.8,     # 20% reduction for complex forms
            'height_factor': 0.9,         # 10% reduction for heights over 12ft
        },
        'deck_forms': {
            'base_rate': 80.0,            # square feet per hour
            'crew_size': 6,
            'complexity_factor': 0.85,
            'access_factor': 0.9,
        },
        'column_forms': {
            'base_rate': 20.0,            # linear feet per hour
            'crew_size': 3,
            'diameter_factor': 0.9,       # 10% reduction for large diameters
            'height_factor': 0.85,
        }
    },
    'reinforcement_installation': {
        'bridge_deck': {
            'base_rate': 500.0,           # pounds per hour
            'crew_size': 4,
            'spacing_factor': 0.9,        # 10% reduction for tight spacing
            'complexity_factor': 0.85,
        },
        'bridge_abutment': {
            'base_rate': 300.0,           # pounds per hour
            'crew_size': 3,
            'spacing_factor': 0.9,
            'access_factor': 0.85,
        },
        'bridge_pier': {
            'base_rate': 200.0,           # pounds per hour
            'crew_size': 2,
            'spacing_factor': 0.9,
            'access_factor': 0.8,
        }
    },
    'general_factors': {
        'overtime_multiplier': 1.5,       # 50% additional for overtime
        'night_work_multiplier': 1.3,     # 30% additional for night work
        'weekend_multiplier': 1.4,        # 40% additional for weekend work
        'holiday_multiplier': 2.0,        # 100% additional for holidays
        'learning_curve_factor': 0.9,     # 10% improvement after first week
        'experience_factor': 1.1,         # 10% improvement for experienced crews
    }
}

# Development-specific settings
if DEBUG:
    # Override settings for development
    PDF_CONFIG['extraction_timeout'] = 600  # 10 minutes for development
    PERFORMANCE_CONFIG['max_concurrent_extractions'] = 1  # Single extraction for development

# Production-specific settings
if ENVIRONMENT == 'production':
    # Stricter settings for production
    SECURITY_CONFIG['session_timeout'] = 1800  # 30 minutes
    SECURITY_CONFIG['max_login_attempts'] = 3
    PERFORMANCE_CONFIG['cache_ttl'] = 7200  # 2 hours

def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value with fallback to default."""
    # Flatten all config dictionaries for easy access
    all_settings = {
        **globals(),
        **DB_CONFIG,
        **MARKUP_PERCENTAGES,
        **DELIVERY_FEE_CONFIG,
        **FILE_UPLOAD_CONFIG,
        **STREAMLIT_CONFIG,
        **PDF_CONFIG,
        **BIDDING_CONFIG,
        **OUTPUT_CONFIG,
        **SECURITY_CONFIG,
        **PERFORMANCE_CONFIG,
        **WASTE_FACTORS,
        **PRODUCTIVITY_FACTORS,
    }
    return all_settings.get(key, default)

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        BASE_DIR / 'data',
        BASE_DIR / 'data' / 'uploads',
        BASE_DIR / 'data' / 'temp',
        BASE_DIR / 'data' / 'backups',
        BASE_DIR / 'data' / 'cache',
        BASE_DIR / 'logs',
        BASE_DIR / 'output' / 'reports',
        BASE_DIR / 'output' / 'bids',
        BASE_DIR / 'output' / 'catalogs',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Ensure directories exist when module is imported
ensure_directories() 