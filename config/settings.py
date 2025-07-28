"""
Application settings and configuration for PACE - Project Analysis & Construction Estimating.
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
        'sqlite_path': BASE_DIR / 'data' / 'pace_construction_dev.db',
        'backup_path': BASE_DIR / 'data' / 'backups',
        'cache_path': BASE_DIR / 'data' / 'cache',
    },
    'production': {
        'sqlite_path': BASE_DIR / 'data' / 'pace_construction_prod.db',
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
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': BASE_DIR / 'logs' / 'pace_construction.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': BASE_DIR / 'logs' / 'pace_construction_errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {  # Root logger
            'level': 'INFO',
            'handlers': ['console', 'file', 'error_file'],
            'propagate': False
        },
        'pace_construction': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'src': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    }
}

# Application settings
APP_CONFIG = {
    'name': 'PACE - Project Analysis & Construction Estimating',
    'version': '1.0.0',
    'description': 'Intelligent Construction Estimating Platform',
    'subtitle': 'Professional-grade estimating for competitive advantage',
    'company': 'Squires Lumber',
    'tagline': 'Powered by Squires Lumber',
    'author': 'PACE Development Team',
    'contact_email': 'support@pace-construction.com',
    'website': 'https://pace-construction.com',
    'page_title': 'PACE - Project Analysis & Construction Estimating',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'menu_items': {
        'Get help': 'https://docs.pace-construction.com',
        'Report a bug': 'https://github.com/your-org/pace-construction-estimating/issues',
        'About': 'PACE - Intelligent Construction Estimating Platform'
    }
}

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'smtp_username': os.getenv('EMAIL_USERNAME', ''),
    'smtp_password': os.getenv('EMAIL_PASSWORD', ''),
    'use_tls': True,
    'default_sender': 'noreply@pace-construction.com',
    'default_recipients': ['admin@pace-construction.com'],
    'email_templates': {
        'catalog_export': {
            'subject': 'PACE - Catalog Export Complete',
            'template': 'catalog_export_template.html'
        },
        'bid_generated': {
            'subject': 'PACE - Project Bid Generated',
            'template': 'bid_generated_template.html'
        },
        'analysis_complete': {
            'subject': 'PACE - Project Analysis Complete',
            'template': 'analysis_complete_template.html'
        }
    }
}

# Output paths
OUTPUT_PATHS = {
    'catalogs': BASE_DIR / 'output' / 'catalogs',
    'bids': BASE_DIR / 'output' / 'bids',
    'reports': BASE_DIR / 'output' / 'reports',
    'analyses': BASE_DIR / 'output' / 'analyses',
    'temp': BASE_DIR / 'data' / 'temp',
    'backups': BASE_DIR / 'data' / 'backups'
}

# Analysis settings
ANALYSIS_CONFIG = {
    'max_pages_per_pdf': 1000,
    'min_confidence_threshold': 0.5,
    'max_processing_time': 300,  # 5 minutes
    'batch_size': 10,
    'supported_languages': ['en'],
    'terminology_categories': [
        'formwork',
        'concrete',
        'steel',
        'electrical',
        'mechanical',
        'plumbing',
        'landscaping',
        'paving',
        'drainage',
        'signage'
    ]
}

# Bid generation settings
BID_CONFIG = {
    'default_markup_percentage': 20.0,
    'default_tax_rate': 8.25,
    'default_currency': 'USD',
    'delivery_fee_percentage': 3.0,
    'delivery_fee_minimum': 150.0,
    'waste_factors': {
        'formwork': 0.10,
        'lumber': 0.10,
        'hardware': 0.05,
        'specialty': 0.15,
        'concrete': 0.05,
        'steel': 0.03
    },
    'bid_templates': {
        'standard': 'templates/standard_bid_template.xlsx',
        'detailed': 'templates/detailed_bid_template.xlsx',
        'summary': 'templates/summary_bid_template.xlsx'
    },
    'export_formats': ['xlsx', 'pdf', 'json', 'csv']
}

# Security settings
SECURITY_CONFIG = {
    'session_timeout': 3600,  # 1 hour
    'max_login_attempts': 5,
    'password_min_length': 8,
    'require_special_chars': True,
    'enable_2fa': False,
    'allowed_file_types': ['.pdf', '.xlsx', '.xls', '.docx', '.doc'],
    'max_file_size_mb': 100
}

# Performance settings
PERFORMANCE_CONFIG = {
    'max_concurrent_uploads': 5,
    'max_concurrent_analyses': 3,
    'cache_ttl': 3600,  # 1 hour
    'database_pool_size': 10,
    'enable_caching': True,
    'enable_compression': True
}

# Feature flags
FEATURE_FLAGS = {
    'enable_batch_processing': True,
    'enable_email_notifications': True,
    'enable_advanced_analytics': True,
    'enable_multi_agency_support': True,
    'enable_caltrans_integration': True,
    'enable_whitecap_integration': True,
    'enable_custom_templates': True,
    'enable_api_access': False
}

# Agency-specific configurations
AGENCY_CONFIG = {
    'caltrans': {
        'enabled': True,
        'priority': 'high',
        'name': 'California Department of Transportation',
        'abbreviation': 'CalTrans',
        'terminology_file': 'caltrans_reference.json',
        'specification_formats': ['pdf', 'docx'],
        'bid_requirements': {
            'template_format': 'caltrans_standard',
            'required_sections': ['cover_sheet', 'bid_form', 'schedule_of_values'],
            'markup_range': (15.0, 25.0),
            'delivery_requirements': 'caltrans_approved'
        },
        'specific_requirements': ['caltrans_approved', 'california_specs', 'dbe_compliance']
    },
    'dot_agencies': {
        'enabled': True,
        'priority': 'high',
        'name': 'State DOT Agencies',
        'abbreviation': 'DOT',
        'examples': ['TxDOT', 'FDOT', 'NYSDOT', 'PennDOT'],
        'terminology_file': 'dot_reference.json',
        'specification_formats': ['pdf', 'docx'],
        'bid_requirements': {
            'template_format': 'dot_standard',
            'required_sections': ['bid_form', 'schedule_of_values', 'qualifications'],
            'markup_range': (12.0, 22.0),
            'delivery_requirements': 'state_approved'
        },
        'specific_requirements': ['state_approved', 'dot_specs', 'mbe_wbe_compliance']
    },
    'municipal': {
        'enabled': True,
        'priority': 'medium',
        'name': 'Municipal Construction',
        'description': 'City and County Infrastructure Projects',
        'terminology_file': 'municipal_reference.json',
        'specification_formats': ['pdf', 'docx'],
        'bid_requirements': {
            'template_format': 'municipal_standard',
            'required_sections': ['bid_form', 'schedule_of_values'],
            'markup_range': (10.0, 20.0),
            'delivery_requirements': 'local_approved'
        },
        'specific_requirements': ['local_approved', 'municipal_specs', 'local_preferences']
    },
    'federal': {
        'enabled': True,
        'priority': 'medium',
        'name': 'Federal Infrastructure',
        'description': 'Government Construction Projects',
        'terminology_file': 'federal_reference.json',
        'specification_formats': ['pdf', 'docx'],
        'bid_requirements': {
            'template_format': 'federal_standard',
            'required_sections': ['sf1442', 'schedule_of_values', 'certifications'],
            'markup_range': (8.0, 18.0),
            'delivery_requirements': 'federal_approved'
        },
        'specific_requirements': ['federal_approved', 'federal_specs', 'davis_bacon', 'buy_american']
    },
    'commercial': {
        'enabled': True,
        'priority': 'medium',
        'name': 'Commercial Construction',
        'description': 'Private Sector Development',
        'terminology_file': 'commercial_reference.json',
        'specification_formats': ['pdf', 'docx', 'dwg'],
        'bid_requirements': {
            'template_format': 'commercial_standard',
            'required_sections': ['proposal', 'schedule_of_values', 'qualifications'],
            'markup_range': (15.0, 30.0),
            'delivery_requirements': 'client_specified'
        },
        'specific_requirements': ['client_specs', 'commercial_standards', 'quality_requirements']
    },
    'industrial': {
        'enabled': True,
        'priority': 'low',
        'name': 'Industrial Projects',
        'description': 'Manufacturing and Processing Facilities',
        'terminology_file': 'industrial_reference.json',
        'specification_formats': ['pdf', 'docx', 'dwg'],
        'bid_requirements': {
            'template_format': 'industrial_standard',
            'required_sections': ['technical_proposal', 'schedule_of_values', 'safety_plan'],
            'markup_range': (20.0, 35.0),
            'delivery_requirements': 'industrial_standards'
        },
        'specific_requirements': ['industrial_specs', 'safety_compliance', 'quality_standards']
    }
}

# Market segments configuration
MARKET_SEGMENTS = {
    'dot_highway': {
        'name': 'DOT & Highway Projects',
        'description': 'State transportation departments and highway construction',
        'agencies': ['caltrans', 'dot_agencies'],
        'examples': ['CalTrans', 'TxDOT', 'FDOT', 'NYSDOT'],
        'priority': 'high',
        'icon': '🛣️'
    },
    'municipal': {
        'name': 'Municipal Construction',
        'description': 'City and county infrastructure projects',
        'agencies': ['municipal'],
        'examples': ['Water treatment', 'Roads', 'Public buildings'],
        'priority': 'medium',
        'icon': '🏛️'
    },
    'federal': {
        'name': 'Federal Infrastructure',
        'description': 'Government construction projects',
        'agencies': ['federal'],
        'examples': ['Courthouses', 'Military facilities', 'Federal buildings'],
        'priority': 'medium',
        'icon': '🏛️'
    },
    'commercial': {
        'name': 'Commercial Construction',
        'description': 'Private sector development projects',
        'agencies': ['commercial'],
        'examples': ['Office complexes', 'Retail centers', 'Hotels'],
        'priority': 'medium',
        'icon': '🏢'
    },
    'industrial': {
        'name': 'Industrial Projects',
        'description': 'Manufacturing and processing facilities',
        'agencies': ['industrial'],
        'examples': ['Factories', 'Warehouses', 'Refineries'],
        'priority': 'low',
        'icon': '🏭'
    }
}

# Success metrics configuration
SUCCESS_METRICS = {
    'competitive_advantage': {
        'name': 'Competitive Advantage',
        'description': 'Advanced bidding strategies for construction projects',
        'icon': '🏆',
        'color': 'success',
        'target': 'Higher win rates',
        'measurement': 'Win rate improvement'
    },
    'multi_agency_support': {
        'name': 'Multi-Agency Support',
        'description': 'DOT, municipal, federal, and commercial projects',
        'icon': '🏛️',
        'color': 'primary',
        'target': 'Broader market access',
        'measurement': 'Agencies supported'
    },
    'professional_estimating': {
        'name': 'Professional Estimating',
        'description': 'Industry-leading accuracy for all project types',
        'icon': '📊',
        'color': 'error',
        'target': 'Reduced errors',
        'measurement': 'Accuracy rate'
    }
}

# Professional language and messaging
PROFESSIONAL_MESSAGING = {
    'headlines': [
        'PACE supports all major construction project types',
        'From highway infrastructure to commercial builds',
        'Professional-grade estimating for competitive advantage'
    ],
    'benefits': [
        'Advanced bidding strategies for construction projects',
        'Multi-agency project support across all major segments',
        'Professional estimating for all project types'
    ],
    'value_propositions': [
        'Streamline infrastructure and construction project bidding',
        'Automate catalog processing and bid generation',
        'Generate accurate cost estimates with built-in calculations'
    ]
}

# Default application settings
DEFAULT_SETTINGS = {
    'markup_percentage': 20.0,
    'tax_rate': 8.25,
    'delivery_fee_percentage': 3.0,
    'delivery_fee_minimum': 150.0,
    'waste_factors': {
        'formwork': 0.10,
        'lumber': 0.10,
        'hardware': 0.05,
        'specialty': 0.15
    },
    'currency': 'USD',
    'language': 'en',
    'timezone': 'America/Los_Angeles',
    'date_format': '%Y-%m-%d',
    'time_format': '%H:%M:%S'
}

def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a setting value by key.
    
    Args:
        key: The setting key to retrieve
        default: Default value if key not found
        
    Returns:
        The setting value or default
    """
    # Check in environment variables first
    env_value = os.getenv(key.upper())
    if env_value is not None:
        return env_value
    
    # Check in default settings
    if key in DEFAULT_SETTINGS:
        return DEFAULT_SETTINGS[key]
    
    # Check in app config
    if key in APP_CONFIG:
        return APP_CONFIG[key]
    
    return default

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        BASE_DIR / 'data' / 'uploads',
        BASE_DIR / 'data' / 'temp',
        BASE_DIR / 'data' / 'backups',
        BASE_DIR / 'data' / 'cache',
        BASE_DIR / 'logs',
        BASE_DIR / 'output' / 'catalogs',
        BASE_DIR / 'output' / 'bids',
        BASE_DIR / 'output' / 'reports',
        BASE_DIR / 'output' / 'analyses'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    return directories 