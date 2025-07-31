#!/usr/bin/env python3
"""
Electoral Roll Data Extraction Tool
Main extraction script as required by assignment

This script extracts structured voter data from multi-column PDF electoral rolls
and consolidates the information into Excel files. Supports both GUI and CLI modes.

Usage:
    python extract.py --input "C:\folder" --output "C:\folder"
    python extract.py --gui

Author: Data Scrapper Intern Applicant
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import core modules
from src.core.extractor import ElectoralRollExtractor
from src.utils.file_handler import FileHandler
from src.utils.logger import Logger


def create_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description='Extract structured voter data from PDF electoral rolls',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input "C:\\electoral_pdfs" --output "C:\\output"
  %(prog)s -i electoral_roll.pdf -o output_folder
  %(prog)s --gui
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input PDF file or directory path containing PDF files'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory path where Excel file will be saved'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch GUI mode instead of CLI'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (optional)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Electoral Roll Extractor v1.0.0'
    )
    
    return parser


def validate_arguments(args, logger):
    """Validate command line arguments"""
    if args.gui:
        return True
    
    if not args.input or not args.output:
        logger.error("Both --input and --output are required for CLI mode")
        return False
    
    # Validate input path
    if not FileHandler.validate_input_path(args.input):
        logger.error(f"Invalid input path or no PDF files found: {args.input}")
        return False
    
    # Validate output path
    if not FileHandler.validate_output_path(args.output):
        logger.error(f"Invalid output path or insufficient permissions: {args.output}")
        return False
    
    return True


def run_cli_mode(input_path, output_path, logger):
    """Run extraction in CLI mode"""
    try:
        logger.info("Starting Electoral Roll Data Extraction (CLI Mode)")
        logger.info("=" * 60)
        
        # Initialize extractor
        extractor = ElectoralRollExtractor()
        
        # Process files
        logger.info(f"Input path: {input_path}")
        logger.info(f"Output path: {output_path}")
        
        voters = extractor.process_directory(input_path)
        
        if not voters:
            logger.warning("No voter data extracted")
            return False
        
        logger.info(f"Successfully extracted {len(voters)} voter records")
        
        # Save to Excel
        logger.info("Saving data to Excel file...")
        result = FileHandler.save_to_excel(voters, output_path)
        
        if result:
            logger.info(f"Data saved successfully to: {result}")
            logger.info("Extraction completed successfully!")
            return True
        else:
            logger.error("Failed to save data to Excel")
            return False
    
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        return False


def run_gui_mode(logger):
    """Launch GUI mode"""
    try:
        from src.gui.main_window import MainWindow
        
        logger.info("Launching GUI mode...")
        app = MainWindow()
        app.run()
    
    except ImportError as e:
        logger.error(f"GUI dependencies not available: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error launching GUI: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point for the extraction script"""
    try:
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Setup logging
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logger = Logger.setup_logger(
            __name__, 
            log_level,
            args.log_file
        )
        
        # Default to GUI if no arguments provided
        if len(sys.argv) == 1:
            args.gui = True
        
        # Validate arguments
        if not validate_arguments(args, logger):
            parser.print_help()
            sys.exit(1)
        
        # Run appropriate mode
        if args.gui:
            run_gui_mode(logger)
        else:
            success = run_cli_mode(args.input, args.output, logger)
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger = Logger.setup_logger(__name__)
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
