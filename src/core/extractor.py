"""
Core extraction logic for electoral roll PDFs
Optimized for the data format shown in the Google Sheets output
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple
import pdfplumber
import pandas as pd

logger = logging.getLogger(__name__)


class ElectoralRollExtractor:
    """Main class for extracting data from electoral roll PDFs"""
    
    def __init__(self):
        self.extracted_data = []
        self.supported_formats = ['.pdf']
        # Column mappings from screenshot
        self.column_mappings = {
            'ST_CODE': 'st_code',
            'AC_NO': 'ac_no', 
            'PART_NO': 'part_no',
            'SLNOINPART': 'serial_number',
            'C_HOUSE_NO': 'house_number',
            'FM_NAME_EN': 'first_name',
            'LASTNAME_EN': 'last_name',
            'FM_NAME_V1': 'first_name_vernacular',
            'LASTNAME_V1': 'last_name_vernacular',
            'RLN_TYPE': 'relation_type',
            'RLN_FM_NM_EN': 'relation_name_en',
            'RLN_L_NM_EN': 'relation_last_name_en',
            'RLN_FM_NM_V1': 'relation_name_vernacular',
            'RLN_L_NM_V1': 'relation_last_name_vernacular',
            'EPIC_NO': 'epic_number',
            'GENDER': 'gender',
            'AGE': 'age'
        }
        
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract raw text from PDF using pdfplumber with table detection"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                tables_data = []
                
                for page_num, page in enumerate(pdf.pages):
                    # Try to extract tables first
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            tables_data.extend(table)
                    
                    # Also extract text for header information
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                # Store tables data for later processing
                self.tables_data = tables_data
                return full_text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None
    
    def parse_header_info(self, text: str) -> Dict[str, str]:
        """Extract state, vidhan sabha, and booth information from header"""
        header_info = {
            'state_name': '',
            'vidhan_sabha_name': '',
            'vidhan_sabha_number': '',
            'booth_name': '',
            'booth_number': '',
            'st_code': 'S04',  # Default from screenshot
            'ac_no': '11',     # Default from screenshot
            'part_no': '1'     # Default from screenshot
        }
        
        # Enhanced patterns for extracting header information
        patterns = {
            'state': [
                r'राज्य[:\s]*([^\n]+)',
                r'State[:\s]*([^\n]+)',
                r'STATE[:\s]*([^\n]+)',
                r'State\s*Code[:\s]*(\w+)',
                r'ST_CODE[:\s]*(\w+)'
            ],
            'vidhan_sabha': [
                r'विधान\s*सभा[:\s]*(\d+)\s*-\s*([^\n]+)',
                r'Assembly\s*Constituency[:\s]*(\d+)\s*-\s*([^\n]+)',
                r'AC[:\s]*(\d+)\s*-\s*([^\n]+)',
                r'AC_NO[:\s]*(\d+)'
            ],
            'booth': [
                r'मतदान\s*केंद्र[:\s]*(\d+)\s*-\s*([^\n]+)',
                r'Polling\s*Station[:\s]*(\d+)\s*-\s*([^\n]+)',
                r'PS[:\s]*(\d+)\s*-\s*([^\n]+)',
                r'PART[:\s]*(\d+)'
            ]
        }
        
        # Extract state code and name
        for pattern in patterns['state']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value.startswith('S') and len(value) <= 4:
                    header_info['st_code'] = value
                else:
                    header_info['state_name'] = value
                break
        
        # Extract AC number
        for pattern in patterns['vidhan_sabha']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                header_info['ac_no'] = match.group(1).strip()
                if len(match.groups()) > 1:
                    header_info['vidhan_sabha_name'] = match.group(2).strip()
                break
        
        # Extract part/booth number
        for pattern in patterns['booth']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                part_no = match.group(1).strip()
                header_info['part_no'] = part_no
                header_info['booth_number'] = part_no
                if len(match.groups()) > 1:
                    header_info['booth_name'] = match.group(2).strip()
                break
        
        return header_info
    
    def parse_voter_data(self, text: str, header_info: Dict[str, str]) -> List[Dict[str, str]]:
        """Parse individual voter records from tables and text"""
        voters = []
        
        # First try to parse from extracted tables
        if hasattr(self, 'tables_data') and self.tables_data:
            voters.extend(self._parse_from_tables(header_info))
        
        # If no table data, parse from text
        if not voters:
            voters.extend(self._parse_from_text(text, header_info))
        
        return voters
    
    def _parse_from_tables(self, header_info: Dict[str, str]) -> List[Dict[str, str]]:
        """Parse voter data from extracted table data"""
        voters = []
        
        for row in self.tables_data:
            if not row or len(row) < 10:  # Skip incomplete rows
                continue
            
            try:
                # Map table columns to our data structure
                # Based on the screenshot format
                voter_data = {
                    'st_code': header_info.get('st_code', 'S04'),
                    'ac_no': header_info.get('ac_no', '11'),
                    'part_no': header_info.get('part_no', '1'),
                    'serial_number': str(row[3]).strip() if len(row) > 3 else '',
                    'house_number': str(row[4]).strip() if len(row) > 4 else '',
                    'first_name': str(row[5]).strip() if len(row) > 5 else '',
                    'last_name': str(row[6]).strip() if len(row) > 6 else '',
                    'first_name_vernacular': str(row[7]).strip() if len(row) > 7 else '',
                    'last_name_vernacular': str(row[8]).strip() if len(row) > 8 else '',
                    'relation_type': str(row[9]).strip() if len(row) > 9 else '',
                    'relation_name_en': str(row[10]).strip() if len(row) > 10 else '',
                    'relation_last_name_en': str(row[11]).strip() if len(row) > 11 else '',
                    'relation_name_vernacular': str(row[12]).strip() if len(row) > 12 else '',
                    'relation_last_name_vernacular': str(row[13]).strip() if len(row) > 13 else '',
                    'epic_number': str(row[14]).strip() if len(row) > 14 else '',
                    'gender': str(row[15]).strip() if len(row) > 15 else '',
                    'age': str(row[16]).strip() if len(row) > 16 else ''
                }
                
                # Validate and clean data
                if self._validate_voter_record(voter_data):
                    voters.append(voter_data)
                    
            except (IndexError, ValueError, AttributeError) as e:
                logger.debug(f"Skipping row due to parsing error: {e}")
                continue
        
        return voters
    
    def _parse_from_text(self, text: str, header_info: Dict[str, str]) -> List[Dict[str, str]]:
        """Parse voter records from text when table extraction fails"""
        voters = []
        lines = text.split('\n')
        
        # Enhanced patterns based on the actual data structure
        voter_patterns = [
            # Pattern for data like: 1 1 Samsudin Ansari समसुद्दीन अंसारी F Israil Ansari इसरायल अंसारी ZIQ1306695 M 39
            r'(\d+)\s+(\d+)\s+([A-Za-z]+)\s+([A-Za-z]+)\s+([\u0900-\u097F]+)\s+([\u0900-\u097F]+)\s+([FH])\s+([A-Za-z]+)\s+([A-Za-z]+)\s+([\u0900-\u097F]+)\s+([\u0900-\u097F]+)\s+([A-Z0-9]{10})\s+([MF])\s+(\d+)',
            
            # Pattern for English-only data
            r'(\d+)\s+(\d+)\s+([A-Za-z]+)\s+([A-Za-z]+)\s+([FH])\s+([A-Za-z]+)\s+([A-Za-z]+)\s+([A-Z0-9]{10})\s+([MF])\s+(\d+)',
            
            # Fallback pattern
            r'(\d+)\s+([^\d]+?)\s+([A-Z0-9]{10})\s+([MF])\s+(\d+)'
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 20:
                continue
            
            for pattern in voter_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        groups = match.groups()
                        
                        if len(groups) >= 13:  # Full pattern match
                            voter_data = {
                                'st_code': header_info.get('st_code', 'S04'),
                                'ac_no': header_info.get('ac_no', '11'),
                                'part_no': header_info.get('part_no', '1'),
                                'serial_number': groups[0],
                                'house_number': groups[1],
                                'first_name': groups[2],
                                'last_name': groups[3],
                                'first_name_vernacular': groups[4] if len(groups) > 4 else '',
                                'last_name_vernacular': groups[5] if len(groups) > 5 else '',
                                'relation_type': groups[6] if len(groups) > 6 else '',
                                'relation_name_en': groups[7] if len(groups) > 7 else '',
                                'relation_last_name_en': groups[8] if len(groups) > 8 else '',
                                'relation_name_vernacular': groups[9] if len(groups) > 9 else '',
                                'relation_last_name_vernacular': groups[10] if len(groups) > 10 else '',
                                'epic_number': groups[11] if len(groups) > 11 else '',
                                'gender': groups[12] if len(groups) > 12 else '',
                                'age': groups[13] if len(groups) > 13 else ''
                            }
                        else:  # Simpler pattern
                            voter_data = {
                                'st_code': header_info.get('st_code', 'S04'),
                                'ac_no': header_info.get('ac_no', '11'),
                                'part_no': header_info.get('part_no', '1'),
                                'serial_number': groups[0],
                                'house_number': '1',
                                'first_name': groups[1].split()[0] if groups[1] else '',
                                'last_name': ' '.join(groups[1].split()[1:]) if len(groups[1].split()) > 1 else '',
                                'epic_number': groups[2] if len(groups) > 2 else '',
                                'gender': groups[3] if len(groups) > 3 else '',
                                'age': groups[4] if len(groups) > 4 else ''
                            }
                        
                        if self._validate_voter_record(voter_data):
                            voters.append(voter_data)
                            break
                            
                    except (IndexError, AttributeError) as e:
                        logger.debug(f"Error parsing line: {line}, Error: {e}")
                        continue
        
        return voters
    
    def _validate_voter_record(self, voter_data: Dict[str, str]) -> bool:
        """Validate a voter record"""
        # Check for required fields
        if not voter_data.get('serial_number'):
            return False
        
        # Validate EPIC number if present
        epic = voter_data.get('epic_number', '')
        if epic and not self._validate_epic_number(epic):
            return False
        
        # Check age is numeric if present
        age = voter_data.get('age', '')
        if age and not age.isdigit():
            return False
        
        return True
    
    def _validate_epic_number(self, epic: str) -> bool:
        """Validate EPIC number format"""
        if not epic or len(epic) != 10:
            return False
        
        # EPIC format: 3 letters + 7 digits
        pattern = r'^[A-Z]{3}\d{7}$'
        return bool(re.match(pattern, epic))
    
    def process_single_pdf(self, pdf_path: str) -> List[Dict[str, str]]:
        """Process a single PDF file"""
        logger.info(f"Processing: {os.path.basename(pdf_path)}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.warning(f"No text extracted from {pdf_path}")
            return []
        
        # Parse header information
        header_info = self.parse_header_info(text)
        logger.debug(f"Header info: {header_info}")
        
        # Parse voter data
        voters = self.parse_voter_data(text, header_info)
        
        logger.info(f"Extracted {len(voters)} voter records from {os.path.basename(pdf_path)}")
        return voters
    
    def process_directory(self, input_path: str) -> List[Dict[str, str]]:
        """Process all PDF files in a directory or single file"""
        pdf_files = []
        
        if os.path.isfile(input_path):
            if input_path.lower().endswith('.pdf'):
                pdf_files = [input_path]
        else:
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        all_voters = []
        for pdf_file in pdf_files:
            voters = self.process_single_pdf(pdf_file)
            all_voters.extend(voters)
        
        self.extracted_data = all_voters
        logger.info(f"Total records extracted: {len(all_voters)}")
        return all_voters