"""
Complete Stage 1 Pipeline
Processes ALL PDFs in data/ folder
"""

from .pdf_processor import PDFProcessor
from .ocr_engine import MultiStrategyOCR, OCRResult
from typing import List, Dict
import json
import os
from datetime import datetime

class Stage1Pipeline:
    """Complete Stage 1: PDF -> Images -> OCR"""
    
    def __init__(self, use_gpu: bool = False):
        print("="*70)
        print("🚀 STAGE 1: Document Ingestion & OCR Pipeline")
        print("="*70)
        print("✓ Pure Python - No Poppler")
        print("✓ Pure Python - No Tesseract")
        print("="*70 + "\n")
        
        self.pdf_processor = PDFProcessor(dpi=300)
        self.ocr_engine = MultiStrategyOCR(lang='en', use_gpu=use_gpu)
    
    def process_single_invoice(self, pdf_path: str, output_dir: str = "stage1_output") -> Dict:
        """Process one invoice"""
        
        filename = os.path.basename(pdf_path)
        print(f"📄 {filename}... ", end='', flush=True)
        
        start_time = datetime.now()
        
        try:
            # Convert PDF to images
            images = self.pdf_processor.pdf_to_images(pdf_path)
            
            if not images:
                raise ValueError("No images extracted")
            
            # Run OCR
            ocr_result = self.ocr_engine.extract_text(images[0], strategy='auto')
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare output
            output_data = {
                'metadata': {
                    'filename': filename,
                    'file_path': pdf_path,
                    'processing_date': datetime.now().isoformat(),
                    'processing_time_seconds': round(processing_time, 2),
                    'num_pages': len(images),
                    'image_size': list(images[0].size)
                },
                'ocr_results': {
                    'method': ocr_result.method,
                    'confidence': round(ocr_result.confidence, 4),
                    'num_lines': len(ocr_result.line_level_data),
                    'raw_text': ocr_result.text,
                    'line_level_data': ocr_result.line_level_data
                }
            }
            
            # Save to JSON
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(
                output_dir,
                f"{os.path.splitext(filename)[0]}_stage1.json"
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ ({ocr_result.method}, {ocr_result.confidence:.2%}, {processing_time:.1f}s)")
            
            return output_data
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            return {
                'metadata': {
                    'filename': filename,
                    'error': str(e),
                    'processing_date': datetime.now().isoformat()
                }
            }
    
    def process_all_invoices(self, data_folder: str = "data", output_dir: str = "stage1_output") -> List[Dict]:
        """
        Process ALL PDFs in data folder
        """
        print(f"\n{'='*70}")
        print(f"📁 BATCH PROCESSING - ALL INVOICES IN '{data_folder}/'")
        print(f"{'='*70}\n")
        
        # Check if data folder exists
        if not os.path.exists(data_folder):
            print(f"✗ Folder '{data_folder}/' not found!")
            print(f"📁 Please create it and add your invoice PDFs")
            return []
        
        # Find all PDF files
        pdf_files = [f for f in os.listdir(data_folder) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in '{data_folder}/'")
            print(f"📁 Please add your invoice PDFs to this folder")
            return []
        
        print(f"Found {len(pdf_files)} PDF file(s) to process\n")
        print("Processing invoices:\n")
        
        results = []
        success_count = 0
        start_time = datetime.now()
        
        # Process each PDF
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"[{i:3d}/{len(pdf_files)}] ", end='')
            
            pdf_path = os.path.join(data_folder, pdf_file)
            
            try:
                result = self.process_single_invoice(pdf_path, output_dir)
                
                if 'error' not in result.get('metadata', {}):
                    success_count += 1
                
                results.append(result)
                
            except Exception as e:
                print(f"✗ FAILED: {e}")
                results.append({
                    'metadata': {
                        'filename': pdf_file,
                        'error': str(e)
                    }
                })
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Save batch summary
        summary = {
            'batch_info': {
                'data_folder': data_folder,
                'output_folder': output_dir,
                'total_files': len(pdf_files),
                'successful': success_count,
                'failed': len(pdf_files) - success_count,
                'total_processing_time_seconds': round(total_time, 2),
                'avg_time_per_invoice': round(total_time / len(pdf_files), 2) if pdf_files else 0,
                'processing_date': datetime.now().isoformat()
            },
            'results': results
        }
        
        summary_file = os.path.join(output_dir, "batch_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"📊 BATCH PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"✓ Successful: {success_count}/{len(pdf_files)}")
        print(f"✗ Failed: {len(pdf_files) - success_count}/{len(pdf_files)}")
        print(f"⏱️  Total time: {total_time:.1f}s")
        print(f"⏱️  Avg per invoice: {total_time/len(pdf_files):.1f}s")
        print(f"📄 Summary: {summary_file}")
        print(f"📁 Results: {output_dir}/")
        print(f"{'='*70}\n")
        
        return results
