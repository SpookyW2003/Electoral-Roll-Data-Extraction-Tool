#!/usr/bin/env python3
"""
Test script for Electoral Roll Data Extraction Tool
This script creates sample data to demonstrate the output format
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.file_handler import FileHandler

def create_sample_data():
    """Create sample data matching the Google Sheets format"""
    sample_data = [
        {
            'st_code': 'S04',
            'ac_no': '11',
            'part_no': '1',
            'serial_number': '1',
            'house_number': '1',
            'first_name': 'Samsudin',
            'last_name': 'Ansari',
            'first_name_vernacular': 'समसुद्दीन',
            'last_name_vernacular': 'अंसारी',
            'relation_type': 'F',
            'relation_name_en': 'Israil',
            'relation_last_name_en': 'Ansari',
            'relation_name_vernacular': 'इसरायल',
            'relation_last_name_vernacular': 'अंसारी',
            'epic_number': 'ZIQ1306695',
            'gender': 'M',
            'age': '39'
        },
        {
            'st_code': 'S04',
            'ac_no': '11',
            'part_no': '1',
            'serial_number': '2',
            'house_number': '1',
            'first_name': 'Jahrbano',
            'last_name': 'Khatoon',
            'first_name_vernacular': 'जहरबानो',
            'last_name_vernacular': 'खातून',
            'relation_type': 'H',
            'relation_name_en': 'Shamsuddin',
            'relation_last_name_en': 'Ansari',
            'relation_name_vernacular': 'शमसुद्दीन',
            'relation_last_name_vernacular': 'अंसारी',
            'epic_number': 'ZIQ1306737',
            'gender': 'F',
            'age': '31'
        },
        {
            'st_code': 'S04',
            'ac_no': '11',
            'part_no': '1',
            'serial_number': '3',
            'house_number': '1',
            'first_name': 'Sahadbano',
            'last_name': 'Khatoon',
            'first_name_vernacular': 'सहदबानो',
            'last_name_vernacular': 'खातून',
            'relation_type': 'H',
            'relation_name_en': 'Geyasuddin',
            'relation_last_name_en': 'Ansari',
            'relation_name_vernacular': 'गयासुद्दीन',
            'relation_last_name_vernacular': 'अंसारी',
            'epic_number': 'ZIQ1306786',
            'gender': 'F',
            'age': '31'
        },
        {
            'st_code': 'S04',
            'ac_no': '11',
            'part_no': '1',
            'serial_number': '4',
            'house_number': '1',
            'first_name': 'Manager',
            'last_name': 'Sha',
            'first_name_vernacular': 'मैनेजर',
            'last_name_vernacular': 'शाह',
            'relation_type': 'F',
            'relation_name_en': 'Dhanni',
            'relation_last_name_en': 'Sha',
            'relation_name_vernacular': 'धन्नी',
            'relation_last_name_vernacular': 'शाह',
            'epic_number': 'ZIQ1306729',
            'gender': 'M',
            'age': '29'
        },
        {
            'st_code': 'S04',
            'ac_no': '11',
            'part_no': '1',
            'serial_number': '5',
            'house_number': '1',
            'first_name': 'MAHMAD',
            'last_name': 'SOUKAT ALI',
            'first_name_vernacular': 'महमद्द',
            'last_name_vernacular': 'शौकत अली',
            'relation_type': 'F',
            'relation_name_en': 'mohammad ANUAL',
            'relation_last_name_en': 'HAQUE SOH',
            'relation_name_vernacular': 'महमद्द एजुल',  
            'relation_last_name_vernacular': 'हक शेह',
            'epic_number': 'ZIQ1213651',
            'gender': 'M',
            'age': '29'
        }
    ]
    
    return sample_data

def main():
    """Main function to create sample output"""
    print("Creating sample output file...")
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Create output directory
    output_dir = os.path.join(os.getcwd(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to Excel
    output_file = FileHandler.save_to_excel(sample_data, output_dir)
    
    if output_file:
        print(f"Sample output created successfully: {output_file}")
        print(f"Total sample records: {len(sample_data)}")
        
        # Also create a final_output.xlsx as required
        final_output_path = os.path.join(os.getcwd(), 'final_output.xlsx')
        
        df = pd.DataFrame(sample_data)
        
        # Define column order matching the screenshot
        column_order = [
            'st_code', 'ac_no', 'part_no', 'serial_number', 'house_number',
            'first_name', 'last_name', 'first_name_vernacular', 'last_name_vernacular',
            'relation_type', 'relation_name_en', 'relation_last_name_en',
            'relation_name_vernacular', 'relation_last_name_vernacular',
            'epic_number', 'gender', 'age'
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
        
        # Reorder and rename columns
        df = df.reindex(columns=column_order)
        df = df.rename(columns=column_headers)
        
        # Save final output
        with pd.ExcelWriter(final_output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Electoral_Data')
            
            # Format the worksheet
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
        
        print(f"Final output file created: {final_output_path}")
        
    else:
        print("Failed to create sample output")

if __name__ == "__main__":
    main()
