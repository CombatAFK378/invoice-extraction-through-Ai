"""
PDF to Image Converter using PyMuPDF
No Poppler installation required!
"""

import fitz  # PyMuPDF
from PIL import Image
from typing import List
import os
import io

class PDFProcessor:
    """Convert PDF documents to images using PyMuPDF"""
    
    def __init__(self, dpi: int = 300):
        """
        Args:
            dpi: Resolution for image conversion (300 recommended for OCR)
        """
        self.dpi = dpi
        self.zoom = dpi / 72  # PDF default DPI is 72
    
    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert PDF to list of PIL Images
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PIL Image objects (one per page)
        """
        try:
            doc = fitz.open(pdf_path)
            images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Create transformation matrix for DPI
                mat = fitz.Matrix(self.zoom, self.zoom)
                
                # Render page to pixmap
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                images.append(img)
            
            doc.close()
            return images
            
        except Exception as e:
            print(f"✗ Error converting PDF {pdf_path}: {e}")
            raise
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """Get PDF metadata"""
        doc = fitz.open(pdf_path)
        info = {
            'pages': len(doc),
            'metadata': doc.metadata,
            'is_encrypted': doc.is_encrypted
        }
        doc.close()
        return info
