"""
Unit tests for the electoral roll extractor
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.extractor import ElectoralRollExtractor
from src.utils.file_handler import FileHandler


class TestElectoralRollExtractor(unittest.TestCase):
    """Test cases for ElectoralRollExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = ElectoralRollExtractor()
    
    def test_init(self):
        """Test extractor initialization"""
        self.assertEqual(self.extractor.extracted_data, [])
        self.assertEqual(self.extractor.supported_formats, ['.pdf'])
    
    def test_validate_epic_number_valid(self):
        """Test EPIC number validation with valid numbers"""
        valid_epics = ['ABC1234567', 'XYZ9876543', 'DEF0000001']
        
        for epic in valid_epics:
            with self.subTest(epic=epic):
                self.assertTrue(self.extractor._validate_epic_number(epic))
    
    def test_validate_epic_number_invalid(self):
        """Test EPIC number validation with invalid numbers"""
        invalid_epics = [
            'ABC123456',    # Too short
            'ABC12345678',  # Too long
            '1234567890',   # All digits
            'ABCDEFGHIJ',   # All letters
            'abc1234567',   # Lowercase
            '',             # Empty
            None            # None
        ]
        
        for epic in invalid_epics:
            with self.subTest(epic=epic):
                self.assertFalse(self.extractor._validate_epic_number(epic))
    
    def test_parse_header_info(self):
        """Test header information parsing"""
        sample_text = """
        राज्य: उत्तर प्रदेश
        विधान सभा: 123 - सरोजिनी नगर
        मतदान केंद्र: 456 - प्राथमिक विद्यालय
        """
        
        header_info = self.extractor.parse_header_info(sample_text)
        
        self.assertEqual(header_info['state_name'], 'उत्तर प्रदेश')
        self.assertEqual(header_info['vidhan_sabha_number'], '123')
        self.assertEqual(header_info['vidhan_sabha_name'], 'सरोजिनी नगर')
        self.assertEqual(header_info['booth_number'], '456')
        self.assertEqual(header_info['booth_name'], 'प्राथमिक विद्यालय')
    
    @patch('pdfplumber.open')
    def test_extract_text_from_pdf_success(self, mock_pdf_open):
        """Test successful PDF text extraction"""
        # Mock PDF structure
        mock_page = Mock()
        mock_page.extract_text.return_value = "Sample text from page"
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        
        mock_pdf_open.return_value = mock_pdf
        
        result = self.extractor.extract_text_from_pdf("dummy.pdf")
        
        self.assertEqual(result, "Sample text from page\n")
        mock_pdf_open.assert_called_once_with("dummy.pdf")
    
    @patch('pdfplumber.open')
    def test_extract_text_from_pdf_failure(self, mock_pdf_open):
        """Test PDF text extraction failure"""
        mock_pdf_open.side_effect = Exception("PDF read error")
        
        result = self.extractor.extract_text_from_pdf("dummy.pdf")
        
        self.assertIsNone(result)


class TestFileHandler(unittest.TestCase):
    """Test cases for FileHandler class"""
    
    def test_validate_input_path_file_exists(self):
        """Test input path validation with existing PDF file"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            self.assertTrue(FileHandler.validate_input_path(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_validate_input_path_file_not_exists(self):
        """Test input path validation with non-existing file"""
        self.assertFalse(FileHandler.validate_input_path("nonexistent.pdf"))
    
    def test_validate_input_path_wrong_extension(self):
        """Test input path validation with wrong file extension"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            self.assertFalse(FileHandler.validate_input_path(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_generate_output_filename(self):
        """Test output filename generation"""
        sample_data = [{
            'booth_number': '123',
            'booth_name': 'Primary School',
            'vidhan_sabha_name': 'Sarojini Nagar',
            'state_name': 'Uttar Pradesh'
        }]
        
        filename = FileHandler.generate_output_filename(sample_data)
        expected = "123_Primary_School_Sarojini_Nagar_Uttar_Pradesh.xlsx"
        
        self.assertEqual(filename, expected)
    
    def test_generate_output_filename_empty_data(self):
        """Test output filename generation with empty data"""
        filename = FileHandler.generate_output_filename([])
        self.assertEqual(filename, 'electoral_data.xlsx')
    
    def test_get_pdf_files_single_file(self):
        """Test getting PDF files from single file path"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            pdf_files = FileHandler.get_pdf_files(temp_path)
            self.assertEqual(pdf_files, [temp_path])
        finally:
            os.unlink(temp_path)
    
    def test_get_pdf_files_directory(self):
        """Test getting PDF files from directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test PDF files
            pdf1 = os.path.join(temp_dir, 'file1.pdf')
            pdf2 = os.path.join(temp_dir, 'file2.pdf')
            txt_file = os.path.join(temp_dir, 'file3.txt')
            
            for file_path in [pdf1, pdf2, txt_file]:
                with open(file_path, 'w') as f:
                    f.write("dummy content")
            
            pdf_files = FileHandler.get_pdf_files(temp_dir)
            
            # Should only return PDF files, sorted
            expected = sorted([pdf1, pdf2])
            self.assertEqual(pdf_files, expected)


if __name__ == '__main__':
    unittest.main()