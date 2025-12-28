"""
Retry failed Stage 2 extractions
"""

import os
from dotenv import load_dotenv
from preprocessing.stage2_groq_pipeline import GroqStage2Pipeline

def main():
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    print("🔄 Retrying failed extractions with increased max_tokens...")
    
    pipeline = GroqStage2Pipeline(
        api_key=api_key,
        model_name="openai/gpt-oss-120b",
        output_dir="stage2_output",
        delay_seconds=2
    )
    
    # Retry the failed file
    failed_file = "stage1_output/Copy of ARPFIINVOEBTCHLASER (6)_stage1.json"
    
    print(f"\n📄 Retrying: {failed_file}")
    result = pipeline.process_stage1_output(failed_file)
    
    if result['invoice_data'].get('error'):
        print("❌ Still failed - may need manual review")
    else:
        print("✅ Success! Now 32/32 complete!")

if __name__ == "__main__":
    main()
