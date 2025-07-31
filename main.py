#!/usr/bin/env python3
"""
Electoral Roll Data Extraction Tool
Main entry point for the application

Author: Data Scrapper Intern Applicant
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli.command_line import CommandLineInterface
from src.utils.logger import Logger


def main():
    """Main entry point for the application"""
    try:
        # Initialize CLI
        cli = CommandLineInterface()
        
        # Check if no arguments provided - default to GUI
        if len(sys.argv) == 1:
            cli.run(['--gui'])
        else:
            cli.run()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger = Logger.get_logger(__name__)
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()