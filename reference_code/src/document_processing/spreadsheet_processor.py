# src/document_processing/spreadsheet_processor.py
import os
from typing import List, Dict, Any
import logging
import pandas as pd
import openpyxl

from .base_processor import BaseDocumentProcessor

logger = logging.getLogger(__name__)

class SpreadsheetProcessor(BaseDocumentProcessor):
    """Processor for spreadsheet files (Excel, CSV)"""
    
    def can_process(self, file_path: str, content_type: str) -> bool:
        """
        Check if this processor can handle the given file type
        
        Args:
            file_path: Path to the file
            content_type: MIME type of the file
            
        Returns:
            True if this processor can handle the file, False otherwise
        """
        # Check file extension
        ext = os.path.splitext(file_path)[1].lower()
        valid_extensions = ['.xlsx', '.xls', '.csv', '.tsv']
        
        # Check content type
        valid_types = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/csv',
            'text/tab-separated-values'
        ]
        
        return ext in valid_extensions or any(t in content_type for t in valid_types)
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a spreadsheet file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text content as a formatted string
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                return self._process_csv(file_path)
            elif ext == '.tsv':
                return self._process_csv(file_path, delimiter='\t')
            elif ext in ['.xlsx', '.xls']:
                return self._process_excel(file_path)
            else:
                raise ValueError(f"Unsupported spreadsheet format: {ext}")
        except Exception as e:
            logger.error(f"Error extracting text from spreadsheet {file_path}: {e}")
            raise
    
    def _process_csv(self, file_path: str, delimiter: str = ',') -> str:
        """Process a CSV/TSV file and return formatted text"""
        try:
            # First try UTF-8
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8')
        except UnicodeDecodeError:
            # Fall back to latin-1 if UTF-8 fails
            logger.warning(f"UTF-8 decoding failed for {file_path}, falling back to Latin-1")
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='latin-1')
        
        return self._format_dataframe(df)
    
    def _process_excel(self, file_path: str) -> str:
        """Process an Excel file and return formatted text"""
        # Get all sheet names
        workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet_names = workbook.sheetnames
        workbook.close()
        
        # Process each sheet
        all_sheets_text = []
        
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if not df.empty:
                sheet_text = f"Sheet: {sheet_name}\n"
                sheet_text += self._format_dataframe(df)
                all_sheets_text.append(sheet_text)
        
        return "\n\n".join(all_sheets_text)
    
    def _format_dataframe(self, df: pd.DataFrame) -> str:
        """Format a DataFrame as readable text"""
        # Get column headers
        headers = df.columns.tolist()
        
        # Convert numeric columns that might be IDs to strings to preserve leading zeros
        for col in df.select_dtypes(include=['int64']).columns:
            if df[col].max() < 1000000:  # Assume small numbers might be IDs
                df[col] = df[col].astype(str)
        
        # Format as text
        rows = []
        
        # Add header
        rows.append(", ".join(str(h) for h in headers))
        
        # Add each row
        for _, row in df.iterrows():
            # Format each value, handling NaN values
            formatted_values = []
            for val in row:
                if pd.isna(val):
                    formatted_values.append("")
                else:
                    formatted_values.append(str(val))
            
            rows.append(", ".join(formatted_values))
        
        return "\n".join(rows)