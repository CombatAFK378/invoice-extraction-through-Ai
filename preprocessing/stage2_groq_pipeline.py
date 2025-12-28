"""
Stage 2 Pipeline using Groq API
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
from .groq_extractor import GroqExtractor, validate_extracted_data


class GroqStage2Pipeline:
    """Complete Stage 2 pipeline using Groq API"""
    
    def __init__(self, api_key: str, model_name: str = "openai/gpt-oss-120b", 
                 output_dir: str = "stage2_output", delay_seconds: int = 2):
        """
        Initialize Groq pipeline
        
        Args:
            api_key: Groq API key
            model_name: Groq model to use
            output_dir: Directory to save Stage 2 results
            delay_seconds: Seconds to wait between API calls
        """
        self.extractor = GroqExtractor(api_key, model_name)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.delay_seconds = delay_seconds
        
    def process_stage1_output(self, stage1_json_path: str) -> Dict[str, Any]:
        """Process a single Stage 1 JSON file"""
        print(f"\n📄 Processing: {Path(stage1_json_path).name}")
        
        with open(stage1_json_path, 'r', encoding='utf-8') as f:
            stage1_data = json.load(f)
        
        ocr_text = stage1_data['ocr_results']['raw_text']
        
        print(f"   🤖 Extracting with Groq...")
        extracted_data = self.extractor.extract_invoice_data(ocr_text)
        
        if validate_extracted_data(extracted_data):
            print(f"   ✅ Extraction successful!")
        else:
            print(f"   ⚠️  Extraction completed with warnings")
        
        result = {
            "metadata": {
                "source_file": stage1_data['metadata']['filename'],
                "stage1_confidence": stage1_data['ocr_results']['confidence'],
                "processed_at": stage1_data['metadata']['processing_date']
            },
            "invoice_data": extracted_data
        }
        
        output_path = self._save_result(result, stage1_json_path)
        print(f"   💾 Saved to: {output_path.name}")
        
        return result
    
    def process_batch(self, stage1_output_dir: str) -> Dict[str, Any]:
        """Process all Stage 1 JSON files with rate limiting"""
        stage1_dir = Path(stage1_output_dir)
        json_files = list(stage1_dir.glob("*.json"))
        
        print(f"\n🚀 Stage 2: LLM-Based Field Extraction (GROQ)")
        print(f"   Found {len(json_files)} Stage 1 outputs")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Rate limiting: {self.delay_seconds} seconds between requests")
        
        total_files = len([f for f in json_files if f.name != "batch_summary.json"])
        estimated_minutes = (total_files * self.delay_seconds) // 60
        print(f"   Estimated time: ~{estimated_minutes} minutes")
        
        results = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "files": []
        }
        
        for idx, json_file in enumerate(json_files, 1):
            if json_file.name == "batch_summary.json":
                print(f"   ⏭️  Skipping: {json_file.name}")
                continue
            
            results['total'] += 1
            
            try:
                result = self.process_stage1_output(str(json_file))
                
                if result['invoice_data'].get('error'):
                    results['failed'] += 1
                else:
                    results['successful'] += 1
                    
                results['files'].append({
                    "file": json_file.name,
                    "status": "success" if not result['invoice_data'].get('error') else "failed"
                })
                
                # Rate limiting
                remaining = total_files - results['total']
                if remaining > 0:
                    print(f"   ⏸️  Waiting {self.delay_seconds}s... ({results['successful']} successful, {results['failed']} failed)")
                    time.sleep(self.delay_seconds)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results['failed'] += 1
                results['files'].append({
                    "file": json_file.name,
                    "status": "error",
                    "error": str(e)
                })
                time.sleep(self.delay_seconds + 3)
        
        print(f"\n✅ Stage 2 Complete:")
        print(f"   Successful: {results['successful']}/{results['total']}")
        print(f"   Failed: {results['failed']}/{results['total']}")
        
        return results
    
    def _save_result(self, result: Dict[str, Any], stage1_path: str) -> Path:
        """Save Stage 2 result to JSON file"""
        stage1_name = Path(stage1_path).stem
        output_name = stage1_name.replace("_stage1", "_stage2") + ".json"
        output_path = self.output_dir / output_name
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return output_path
