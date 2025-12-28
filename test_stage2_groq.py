"""
Test Stage 2 using Groq API (Fast and Accurate!)
"""

import os
from dotenv import load_dotenv
from preprocessing.stage2_groq_pipeline import GroqStage2Pipeline


def main():
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in .env file")
        print("   Add to .env: GROQ_API_KEY=gsk_your_key_here")
        return
    
    print("=" * 60)
    print("STAGE 2: GROQ API EXTRACTION (GPT-OSS 120B)")
    print("=" * 60)
    
    # Initialize pipeline with GPT-OSS 120B model
    pipeline = GroqStage2Pipeline(
        api_key=api_key,
        model_name="openai/gpt-oss-120b",
        output_dir="stage2_output",
        delay_seconds=2
    )
    
    # Process all Stage 1 outputs
    results = pipeline.process_batch("stage1_output")
    
    print("\n" + "=" * 60)
    print(f"PROCESSING COMPLETE: {results['successful']}/{results['total']} successful")
    print("=" * 60)


if __name__ == "__main__":
    main()
