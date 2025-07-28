"""
Configuration management for PACE application.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(default="sqlite:///data/pace.db", env="PACE_DB_URL")
    echo: bool = Field(default=False, env="PACE_DB_ECHO")
    pool_size: int = Field(default=10, env="PACE_DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="PACE_DB_MAX_OVERFLOW")
    
    class Config:
        env_prefix = "PACE_DB_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", env="PACE_LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="PACE_LOG_FORMAT"
    )
    file_path: Optional[Path] = Field(default=None, env="PACE_LOG_FILE")
    max_size: int = Field(default=10 * 1024 * 1024, env="PACE_LOG_MAX_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="PACE_LOG_BACKUP_COUNT")
    
    class Config:
        env_prefix = "PACE_LOG_"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    host: str = Field(default="0.0.0.0", env="PACE_API_HOST")
    port: int = Field(default=8000, env="PACE_API_PORT")
    debug: bool = Field(default=False, env="PACE_API_DEBUG")
    cors_origins: list[str] = Field(default=["*"], env="PACE_API_CORS_ORIGINS")
    
    class Config:
        env_prefix = "PACE_API_"


class UISettings(BaseSettings):
    """UI configuration settings."""
    
    theme: str = Field(default="light", env="PACE_UI_THEME")
    page_title: str = Field(default="PACE - Construction Estimating", env="PACE_UI_PAGE_TITLE")
    page_icon: str = Field(default="📊", env="PACE_UI_PAGE_ICON")
    layout: str = Field(default="wide", env="PACE_UI_LAYOUT")
    
    class Config:
        env_prefix = "PACE_UI_"


class AgencySettings(BaseSettings):
    """Agency-specific configuration settings."""
    
    default_agency: str = Field(default="caltrans", env="PACE_DEFAULT_AGENCY")
    supported_agencies: list[str] = Field(
        default=["caltrans", "dot", "municipal", "federal", "commercial"],
        env="PACE_SUPPORTED_AGENCIES"
    )
    
    class Config:
        env_prefix = "PACE_AGENCY_"


class FileSettings(BaseSettings):
    """File handling configuration settings."""
    
    upload_dir: Path = Field(default=Path("data/uploads"), env="PACE_FILE_UPLOAD_DIR")
    temp_dir: Path = Field(default=Path("data/temp"), env="PACE_FILE_TEMP_DIR")
    output_dir: Path = Field(default=Path("output"), env="PACE_FILE_OUTPUT_DIR")
    max_file_size: int = Field(default=100 * 1024 * 1024, env="PACE_FILE_MAX_SIZE")  # 100MB
    allowed_extensions: list[str] = Field(
        default=[".pdf", ".xlsx", ".xls", ".csv"],
        env="PACE_FILE_ALLOWED_EXTENSIONS"
    )
    
    @validator("upload_dir", "temp_dir", "output_dir", pre=True)
    def create_directories(cls, v):
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_prefix = "PACE_FILE_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="development", env="PACE_ENVIRONMENT")
    debug: bool = Field(default=False, env="PACE_DEBUG")
    
    # Application info
    app_name: str = Field(default="PACE - Project Analysis & Construction Estimating", env="PACE_APP_NAME")
    version: str = Field(default="1.0.0", env="PACE_VERSION")
    
    # Base directories
    base_dir: Path = Field(default=Path(__file__).parent.parent.parent.parent, env="PACE_BASE_DIR")
    data_dir: Path = Field(default=Path("data"), env="PACE_DATA_DIR")
    logs_dir: Path = Field(default=Path("logs"), env="PACE_LOGS_DIR")
    
    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()
    api: APISettings = APISettings()
    ui: UISettings = UISettings()
    agency: AgencySettings = AgencySettings()
    file: FileSettings = FileSettings()
    
    @validator("base_dir", "data_dir", "logs_dir", pre=True)
    def create_directories(cls, v):
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"
    
    def get_agency_config(self, agency_name: str) -> Dict[str, Any]:
        """Get agency-specific configuration."""
        # This would load from agency-specific config files
        return {
            "name": agency_name,
            "templates": self.base_dir / "templates" / agency_name,
            "specifications": self.base_dir / "specs" / agency_name,
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 