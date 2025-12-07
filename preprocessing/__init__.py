"""
Stage 1: Document Ingestion & OCR Pipeline
Pure Python - No external dependencies
"""

from .pdf_processor import PDFProcessor
from .ocr_engine import MultiStrategyOCR, OCRResult
from .stage1_pipeline import Stage1Pipeline

__all__ = ['PDFProcessor', 'MultiStrategyOCR', 'OCRResult', 'Stage1Pipeline']
