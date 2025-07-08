import os
import io
from pathlib import Path
from typing import List, Optional

import PyPDF2
from docx import Document
import openpyxl
from PIL import Image
import pytesseract
import pandas as pd

class FileProcessor:
    """Service for processing different file types and extracting text content"""
    
    def __init__(self):
        self.supported_extensions = {
            '.pdf': self._extract_from_pdf,
            '.docx': self._extract_from_docx,
            '.doc': self._extract_from_docx,  # Basic support
            '.xlsx': self._extract_from_xlsx,
            '.xls': self._extract_from_xlsx,  # Basic support
            '.jpg': self._extract_from_image,
            '.jpeg': self._extract_from_image,
            '.png': self._extract_from_image,
            '.tiff': self._extract_from_image,
            '.tif': self._extract_from_image,
            '.bmp': self._extract_from_image,
        }
    
    async def extract_text(self, file_path: str, filename: str) -> str:
        """
        Extract text content from uploaded file based on file type
        """
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        try:
            extraction_method = self.supported_extensions[file_extension]
            text_content = extraction_method(file_path)
            
            if not text_content or len(text_content.strip()) == 0:
                raise ValueError("No text content could be extracted from the file")
            
            return text_content
        except Exception as e:
            raise Exception(f"Error extracting text from {filename}: {str(e)}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text_content = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return '\n\n'.join(text_content)
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from Word documents"""
        text_content = []
        
        try:
            doc = Document(file_path)
            
            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_content.append(' | '.join(row_text))
            
            return '\n\n'.join(text_content)
        except Exception as e:
            raise Exception(f"Error reading Word document: {str(e)}")
    
    def _extract_from_xlsx(self, file_path: str) -> str:
        """Extract text from Excel files"""
        text_content = []
        
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                sheet_content = []
                
                for row in sheet.iter_rows(values_only=True):
                    row_values = []
                    for cell in row:
                        if cell is not None and str(cell).strip():
                            row_values.append(str(cell).strip())
                    
                    if row_values:
                        sheet_content.append(' | '.join(row_values))
                
                if sheet_content:
                    text_content.append(f"Sheet: {sheet_name}\n" + '\n'.join(sheet_content))
            
            return '\n\n'.join(text_content)
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from images using OCR"""
        try:
            # Open and preprocess image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            if not text.strip():
                raise ValueError("No text could be detected in the image")
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def get_file_info(self, file_path: str) -> dict:
        """Get basic information about the file"""
        try:
            stat = os.stat(file_path)
            return {
                'size_bytes': stat.st_size,
                'extension': Path(file_path).suffix.lower(),
                'is_supported': Path(file_path).suffix.lower() in self.supported_extensions
            }
        except Exception as e:
            return {
                'size_bytes': 0,
                'extension': 'unknown',
                'is_supported': False,
                'error': str(e)
            }