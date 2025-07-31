"""
Configuration settings for the electoral roll extractor
"""

import os
from typing import Dict, List


class Settings:
    """Application settings and configuration"""
    
    # Application metadata
    APP_NAME = "Electoral Roll Data Extractor"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "Data Scrapper Intern Applicant"
    
    # File settings
    SUPPORTED_FORMATS = ['.pdf']
    OUTPUT_FORMAT = '.xlsx'
    
    # Excel column order
    EXCEL_COLUMNS = [
        'state_name',
        'vidhan_sabha_name', 
        'vidhan_sabha_number',
        'booth_name',
        'booth_number',
        'serial_number',
        'voter_name',
        'epic_number',
        'relation_name',
        'relation_type',
        'house_number',
        'age',
        'gender'
    ]
    
    # Excel column headers (display names)
    EXCEL_HEADERS = {
        'state_name': 'State Name',
        'vidhan_sabha_name': 'Vidhan Sabha Name',
        'vidhan_sabha_number': 'Vidhan Sabha Number',
        'booth_name': 'Booth Name',
        'booth_number': 'Booth Number',
        'serial_number': 'Serial Number',
        'voter_name': 'Voter Name',
        'epic_number': 'EPIC Number',
        'relation_name': 'Relation Name',
        'relation_type': 'Relation Type',
        'house_number': 'House Number',
        'age': 'Age',
        'gender': 'Gender'
    }
    
    # Regex patterns for data extraction
    PATTERNS = {
        'state': [
            r'राज्य[:\s]*([^\n]+)',
            r'State[:\s]*([^\n]+)',
            r'STATE[:\s]*([^\n]+)'
        ],
        'vidhan_sabha': [
            r'विधान\s*सभा[:\s]*(\d+)\s*-\s*([^\n]+)',
            r'Assembly\s*Constituency[:\s]*(\d+)\s*-\s*([^\n]+)',
            r'AC[:\s]*(\d+)\s*-\s*([^\n]+)'
        ],
        'booth': [
            r'मतदान\s*केंद्र[:\s]*(\d+)\s*-\s*([^\n]+)',
            r'Polling\s*Station[:\s]*(\d+)\s*-\s*([^\n]+)',
            r'PS[:\s]*(\d+)\s*-\s*([^\n]+)'
        ],
        'voter': [
            r'(\d+)\s+([A-Za-z\s]+?)\s+([A-Z]{10})\s+([A-Za-z\s]+?)\s+(Father|Husband|पिता|पति)\s+(\d+)\s+(\d+)\s+([MF])',
            r'(\d+)\s+([^\d]+?)\s+([A-Z]{10})\s+([^\d]+?)\s+(Father|Husband)\s+(\d+)\s+(\d+)\s+([MF])',
            r'(\d+)\s+([^\d]+?)\s+([A-Z]{10})\s+([^\d]+?)\s+(पिता|पति)\s+(\d+)\s+(\d+)\s+([MF])'
        ],
        'epic': r'^[A-Z]{3}\d{7}$'
    }
    
    # GUI settings
    GUI_SETTINGS = {
        'window_size': '800x600',
        'min_window_size': (600, 400),
        'title': APP_NAME,
        'icon': None,  # Path to icon file if available
        'theme': 'default'
    }
    
    # Logging settings
    LOG_SETTINGS = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S',
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    # Processing settings
    PROCESSING_SETTINGS = {
        'min_line_length': 20,
        'max_column_width': 50,
        'batch_size': 100,
        'timeout': 300  # 5 minutes
    }
    
    @classmethod
    def get_log_file_path(cls) -> str:
        """Get default log file path"""
        return os.path.join(os.getcwd(), 'logs', 'electoral_extractor.log')
    
    @classmethod
    def get_output_directory(cls) -> str:
        """Get default output directory"""
        return os.path.join(os.getcwd(), 'output')
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        directories = [
            os.path.dirname(cls.get_log_file_path()),
            cls.get_output_directory()
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)