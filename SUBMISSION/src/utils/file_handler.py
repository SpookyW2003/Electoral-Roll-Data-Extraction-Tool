"""
File handling utilities for the electoral roll extractor
"""

import os
import re
import pandas as pd
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file operations for the electoral roll extractor"""
    
    @staticmethod
    def validate_input_path(path: str) -> bool:
        """Validate if input path exists and contains PDF files"""
        if not os.path.exists(path):
            return False
        
        if os.path.isfile(path):
            return path.lower().endswith('.pdf')
        
        # Check if directory contains PDF files
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    return True
        
        return False
    
    @staticmethod
    def validate_output_path(path: str) -> bool:
        """Validate if output path is writable"""
        if os.path.isfile(path):
            # Check if file is writable
            return os.access(path, os.W_OK)
        
        # Check if directory exists and is writable
        directory = os.path.dirname(path) if os.path.dirname(path) else path
        return os.path.exists(directory) and os.access(directory, os.W_OK)
    
    @staticmethod
    def generate_output_filename(data: List[Dict[str, str]]) -> str:
        """Generate output filename based on extracted data"""
        if not data:
            return 'electoral_data.xlsx'
        
        first_record = data[0]
        
        # Extract components for filename (updated for new structure)
        part_no = first_record.get('part_no', first_record.get('booth_number', 'Unknown'))
        booth_name = first_record.get('booth_name', 'Part' + str(part_no))
        ac_no = first_record.get('ac_no', first_record.get('vidhan_sabha_number', 'Unknown'))
        st_code = first_record.get('st_code', first_record.get('state_name', 'Unknown'))
        
        # Create filename: PartNumber_BoothName_ACNumber_StateCode.xlsx
        filename = f"{part_no}_{booth_name}_{ac_no}_{st_code}.xlsx"
        
        # Clean filename - remove special characters and normalize spaces
        filename = re.sub(r'[^\w\s.-]', '', filename)  # Keep dots for extension
        filename = re.sub(r'[\s]+', '_', filename)
        filename = filename.replace('__', '_').strip('_')
        
        # Ensure it ends with .xlsx
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        return filename
    
    @staticmethod
    def save_to_excel(data: List[Dict[str, str]], output_path: str) -> Optional[str]:
        """Save extracted data to Excel file matching the Google Sheets format"""
        if not data:
            logger.warning("No data to save")
            return None
        
        try:
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Define column order matching the screenshot
            column_order = [
                'st_code',           # ST_CODE
                'ac_no',             # AC_NO
                'part_no',           # PART_NO
                'serial_number',     # SLNOINPART
                'house_number',      # C_HOUSE_NO
                'first_name',        # FM_NAME_EN
                'last_name',         # LASTNAME_EN
                'first_name_vernacular',      # FM_NAME_V1
                'last_name_vernacular',       # LASTNAME_V1
                'relation_type',     # RLN_TYPE
                'relation_name_en',  # RLN_FM_NM_EN
                'relation_last_name_en',      # RLN_L_NM_EN
                'relation_name_vernacular',   # RLN_FM_NM_V1
                'relation_last_name_vernacular', # RLN_L_NM_V1
                'epic_number',       # EPIC_NO
                'gender',            # GENDER
                'age'                # AGE
            ]
            
            # Define column headers matching the screenshot
            column_headers = {
                'st_code': 'ST_CODE',
                'ac_no': 'AC_NO',
                'part_no': 'PART_NO',
                'serial_number': 'SLNOINPART',
                'house_number': 'C_HOUSE_NO',
                'first_name': 'FM_NAME_EN',
                'last_name': 'LASTNAME_EN',
                'first_name_vernacular': 'FM_NAME_V1',
                'last_name_vernacular': 'LASTNAME_V1',
                'relation_type': 'RLN_TYPE',
                'relation_name_en': 'RLN_FM_NM_EN',
                'relation_last_name_en': 'RLN_L_NM_EN',
                'relation_name_vernacular': 'RLN_FM_NM_V1',
                'relation_last_name_vernacular': 'RLN_L_NM_V1',
                'epic_number': 'EPIC_NO',
                'gender': 'GENDER',
                'age': 'AGE'
            }
            
            # Ensure all columns exist, fill missing with empty strings
            for col in column_order:
                if col not in df.columns:
                    df[col] = ''
            
            # Reorder columns
            df = df.reindex(columns=column_order)
            
            # Rename columns to match header format
            df = df.rename(columns=column_headers)
            
            # Generate filename
            filename = FileHandler.generate_output_filename(data)
            
            # Determine full output path
            if output_path.endswith('.xlsx'):
                full_path = output_path
            else:
                full_path = os.path.join(output_path, filename)
            
            # Ensure directory exists
            directory = os.path.dirname(full_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # Save to Excel with formatting
            with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Electoral_Data')
                
                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Electoral_Data']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Data saved successfully to: {full_path}")
            return full_path
            
        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
            return None
    
    @staticmethod
    def get_pdf_files(input_path: str) -> List[str]:
        """Get list of PDF files from input path"""
        pdf_files = []
        
        if os.path.isfile(input_path):
            if input_path.lower().endswith('.pdf'):
                pdf_files = [input_path]
        else:
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
        
        return sorted(pdf_files)