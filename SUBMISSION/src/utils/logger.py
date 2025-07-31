"""
Logging configuration for the electoral roll extractor
"""

import logging
import sys
from typing import Optional


class Logger:
    """Centralized logging configuration"""
    
    @staticmethod
    def setup_logger(name: str = __name__, level: int = logging.INFO, 
                    log_file: Optional[str] = None) -> logging.Logger:
        """Setup and configure logger"""
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not create file handler: {e}")
        
        return logger
    
    @staticmethod
    def get_logger(name: str = __name__) -> logging.Logger:
        """Get existing logger or create new one"""
        return logging.getLogger(name)