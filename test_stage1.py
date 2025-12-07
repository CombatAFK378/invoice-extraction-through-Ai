"""
Test Stage 1 Pipeline
Processes ALL invoices in data/ folder
"""

from preprocessing.stage1_pipeline import Stage1Pipeline
import os

def main():
    print("\n" + "="*70)
    print("STAGE 1: INVOICE OCR PROCESSING")
    print("="*70 + "\n")
    
    # Check if data folder exists
    if not os.path.exists("data"):
        print("⚠️  'data/' folder not found. Creating it...")
        os.makedirs("data")
        print("\n📁 INSTRUCTIONS:")
        print("   1. Place ALL your invoice PDFs in the 'data/' folder")
        print("   2. Run this script again: python test_stage1.py")
        return
    
    # Count PDFs
    pdf_files = [f for f in os.listdir("data") if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("⚠️  No PDF files found in 'data/' folder")
        print("\n📁 INSTRUCTIONS:")
        print("   1. Copy ALL your invoice PDFs to the 'data/' folder")
        print("   2. Run this script again: python test_stage1.py")
        return
    
    print(f"✓ Found {len(pdf_files)} invoice PDF(s) in 'data/' folder")
    print("\nStarting processing...\n")
    
    # Initialize pipeline
    pipeline = Stage1Pipeline(use_gpu=False)  # Set True if GPU available
    
    # Process ALL invoices
    results = pipeline.process_all_invoices(data_folder="data", output_dir="stage1_output")
    
    # Show sample output
    successful = [r for r in results if 'ocr_results' in r]
    
    if successful:
        print("\n" + "="*70)
        print("SAMPLE OUTPUT (First Successful Invoice)")
        print("="*70)
        first = successful[0]
        
        print(f"\nFilename: {first['metadata']['filename']}")
        print(f"OCR Method: {first['ocr_results']['method']}")
        print(f"Confidence: {first['ocr_results']['confidence']:.2%}")
        print(f"Lines: {first['ocr_results']['num_lines']}")
        print(f"Time: {first['metadata']['processing_time_seconds']}s")
        
        print(f"\nText Preview (first 300 chars):")
        print("-" * 70)
        print(first['ocr_results']['raw_text'][:300])
        print("-" * 70)
    
    print("\n✅ STAGE 1 COMPLETE!")
    print(f"📁 Check 'stage1_output/' folder for all results")
    print(f"📄 See 'batch_summary.json' for complete overview\n")

if __name__ == "__main__":
    main()
