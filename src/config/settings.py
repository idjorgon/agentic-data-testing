"""
Configuration settings for the agentic data testing framework
"""

import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the testing framework"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Project Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "examples" / "sample_datasets"
    SCHEMA_DIR = PROJECT_ROOT / "examples" / "sample_schemas"
    REPORTS_DIR = PROJECT_ROOT / "reports"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # Test Generation Settings
    DEFAULT_TEST_COUNT = 10
    MAX_SYNTHETIC_RECORDS = 100
    EDGE_CASE_COVERAGE = True
    
    # Validation Settings
    STRICT_MODE = False
    ENABLE_AI_VALIDATION = True
    VALIDATION_TIMEOUT = 30  # seconds
    
    # Logging Settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "agentic_testing.log"
    
    # Report Settings
    DEFAULT_REPORT_FORMAT = "html"  # Options: html, markdown, json
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for dir_path in [cls.DATA_DIR, cls.SCHEMA_DIR, cls.REPORTS_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "openai_model": cls.OPENAI_MODEL,
            "openai_temperature": cls.OPENAI_TEMPERATURE,
            "default_test_count": cls.DEFAULT_TEST_COUNT,
            "strict_mode": cls.STRICT_MODE,
            "log_level": cls.LOG_LEVEL,
            "default_report_format": cls.DEFAULT_REPORT_FORMAT
        }


# Create directories on import
Config.ensure_directories()
