#!/usr/bin/env python3
"""
Electoral Roll Data Extraction Tool - Streamlit Web App
Web interface for the Electoral Roll Data Extraction Tool

This Streamlit app provides a web-based interface for extracting
structured voter data from PDF electoral rolls.

Author: Data Scrapper Intern Applicant
"""

import streamlit as st
import sys
import os
import tempfile
import io
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.extractor import ElectoralRollExtractor
    from src.utils.file_handler import FileHandler
    from src.utils.logger import Logger
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Electoral Roll Data Extraction Tool",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main Streamlit application"""
    
    # Title and description
    st.title("🗳️ Electoral Roll Data Extraction Tool")
    st.markdown("""
    This tool extracts structured voter data from multi-column PDF electoral rolls 
    and consolidates the information into Excel files.
    """)
    
    # Sidebar
    st.sidebar.header("📋 Instructions")
    st.sidebar.markdown("""
    1. Upload one or more PDF files
    2. Click 'Extract Data' to process
    3. Download the generated Excel file
    
    **Supported formats:**
    - Multi-column PDF electoral rolls
    - Standard electoral roll formats
    """)
    
    # File uploader
    st.header("📁 Upload PDF Files")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more PDF electoral roll files"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Display file information
        with st.expander("📄 Uploaded Files"):
            for file in uploaded_files:
                st.write(f"- **{file.name}** ({file.size:,} bytes)")
        
        # Extract button
        if st.button("🚀 Extract Data", type="primary"):
            extract_data(uploaded_files)
    else:
        st.info("👆 Please upload PDF files to get started")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>Developed by Data Scrapper Intern Applicant | Version 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)

def extract_data(uploaded_files):
    """Extract data from uploaded PDF files"""
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize extractor
        status_text.text("Initializing extractor...")
        extractor = ElectoralRollExtractor()
        
        all_voters = []
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Processing {uploaded_file.name}... ({i+1}/{total_files})")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Extract data from the PDF
                voters = extractor.process_pdf(tmp_file_path)
                if voters:
                    all_voters.extend(voters)
                    st.success(f"✅ Extracted {len(voters)} records from {uploaded_file.name}")
                else:
                    st.warning(f"⚠️ No data extracted from {uploaded_file.name}")
            
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
        
        # Final results
        progress_bar.progress(1.0)
        status_text.text("Processing complete!")
        
        if all_voters:
            st.success(f"🎉 Successfully extracted {len(all_voters)} total voter records!")
            
            # Create Excel file in memory
            status_text.text("Generating Excel file...")
            excel_buffer = create_excel_file(all_voters)
            
            if excel_buffer:
                # Download button
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_buffer,
                    file_name="electoral_roll_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Display sample data
                display_sample_data(all_voters)
            else:
                st.error("❌ Failed to generate Excel file")
        else:
            st.error("❌ No data was extracted from any of the uploaded files")
    
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.exception(e)

def create_excel_file(voters):
    """Create Excel file in memory"""
    try:
        import pandas as pd
        from io import BytesIO
        
        # Convert to DataFrame
        df = pd.DataFrame(voters)
        
        # Create Excel file in memory
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Electoral_Data', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    except Exception as e:
        st.error(f"Error creating Excel file: {str(e)}")
        return None

def display_sample_data(voters):
    """Display sample of extracted data"""
    if not voters:
        return
    
    st.header("📊 Sample Data Preview")
    
    # Convert to DataFrame for display
    import pandas as pd
    df = pd.DataFrame(voters)
    
    # Display basic statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        unique_booths = df['PART_NO'].nunique() if 'PART_NO' in df.columns else 0
        st.metric("Unique Booths", unique_booths)
    
    # Display sample rows
    st.subheader("📋 First 10 Records")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Display column information
    with st.expander("ℹ️ Column Information"):
        st.write("**Extracted Columns:**")
        for col in df.columns:
            st.write(f"- {col}")

if __name__ == "__main__":
    main()
