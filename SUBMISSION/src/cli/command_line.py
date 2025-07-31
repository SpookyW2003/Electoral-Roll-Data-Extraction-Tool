"""
Command line interface for the electoral roll extractor
"""

import argparse
import sys
import os
from typing import Optional

from ..core.extractor import ElectoralRollExtractor
from ..utils.file_handler import FileHandler
from ..utils.logger import Logger


class CommandLineInterface:
    """Command line interface for the electoral roll extractor"""
    
    def __init__(self):
        self.extractor = ElectoralRollExtractor()
        self.logger = Logger.setup_logger(__name__)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description='Extract structured voter data from PDF electoral rolls',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --input "C:\\pdfs" --output "C:\\output"
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
    
    def validate_arguments(self, args) -> bool:
        """Validate command line arguments"""
        if args.gui:
            return True
        
        if not args.input or not args.output:
            self.logger.error("Both --input and --output are required for CLI mode")
            return False
        
        # Validate input path
        if not FileHandler.validate_input_path(args.input):
            self.logger.error(f"Invalid input path or no PDF files found: {args.input}")
            return False
        
        # Validate output path
        if not FileHandler.validate_output_path(args.output):
            self.logger.error(f"Invalid output path or insufficient permissions: {args.output}")
            return False
        
        return True
    
    def run_cli_mode(self, input_path: str, output_path: str) -> bool:
        """Run extraction in CLI mode"""
        try:
            self.logger.info("Starting Electoral Roll Data Extraction (CLI Mode)")
            self.logger.info("=" * 60)
            
            # Process files
            self.logger.info(f"Input path: {input_path}")
            self.logger.info(f"Output path: {output_path}")
            
            voters = self.extractor.process_directory(input_path)
            
            if not voters:
                self.logger.warning("No voter data extracted")
                return False
            
            self.logger.info(f"Successfully extracted {len(voters)} voter records")
            
            # Save to Excel
            self.logger.info("Saving data to Excel file...")
            result = FileHandler.save_to_excel(voters, output_path)
            
            if result:
                self.logger.info(f"Data saved successfully to: {result}")
                self.logger.info("Extraction completed successfully!")
                return True
            else:
                self.logger.error("Failed to save data to Excel")
                return False
        
        except Exception as e:
            self.logger.error(f"Error during extraction: {str(e)}")
            return False
    
    def run_gui_mode(self):
        """Launch GUI mode"""
        try:
            from ..gui.main_window import MainWindow
            
            self.logger.info("Launching GUI mode...")
            app = MainWindow()
            app.run()
        
        except ImportError as e:
            self.logger.error(f"GUI dependencies not available: {str(e)}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error launching GUI: {str(e)}")
            sys.exit(1)
    
    def run(self, args=None):
        """Main entry point for CLI"""
        parser = self.create_parser()
        args = parser.parse_args(args)
        
        # Setup logging
        log_level = 'DEBUG' if args.verbose else 'INFO'
        self.logger = Logger.setup_logger(
            __name__, 
            getattr(__import__('logging'), log_level),
            args.log_file
        )
        
        # Validate arguments
        if not self.validate_arguments(args):
            parser.print_help()
            sys.exit(1)
        
        # Run appropriate mode
        if args.gui:
            self.run_gui_mode()
        else:
            success = self.run_cli_mode(args.input, args.output)
            sys.exit(0 if success else 1)


def main():
    """Entry point for the CLI"""
    cli = CommandLineInterface()
    cli.run()


if __name__ == "__main__":
    main()