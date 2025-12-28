"""
Stage 2: LLM-Based Field Extraction using Groq API
Fast and accurate extraction with GPT-OSS 120B
"""

from groq import Groq
import json
import re
from typing import Dict, Any
from datetime import datetime


class GroqExtractor:
    """Extract structured invoice data using Groq API"""
    
    def __init__(self, api_key: str, model_name: str = "openai/gpt-oss-120b"):
        """
        Initialize Groq extractor
        
        Args:
            api_key: Groq API key
            model_name: Model to use (openai/gpt-oss-120b recommended)
        """
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        print(f"   ⚡ Using Groq model: {model_name}")
        
    def extract_invoice_data(self, ocr_text: str, max_retries: int = 3) -> Dict[str, Any]:
        """Extract structured invoice data from OCR text"""
        prompt = self._create_extraction_prompt(ocr_text)
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert invoice data extraction system. You MUST return ONLY a valid JSON object with no additional text before or after."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.0,
                    max_tokens=4096,
                    top_p=1
                )
                
                raw_response = response.choices[0].message.content
                
                # Debug: Print first 200 chars of response
                if attempt == 0:
                    preview = raw_response[:200].replace('\n', ' ')
                    print(f"   📝 Response preview: {preview}...")
                
                result = self._parse_response(raw_response)
                
                if not result.get('error'):
                    return result
                
                if attempt < max_retries - 1:
                    print(f"   🔄 Retry {attempt + 1}/{max_retries}...")
                    continue
                    
                return result
                
            except Exception as e:
                print(f"   ❌ Groq API error: {e}")
                if attempt < max_retries - 1:
                    print(f"   🔄 Retry {attempt + 1}/{max_retries}...")
                    continue
                return self._create_error_result(str(e))
        
        return self._create_error_result("Max retries exceeded")
    
    def _create_extraction_prompt(self, ocr_text: str) -> str:
        """Create extraction prompt"""
        ocr_snippet = ocr_text[:4000] if len(ocr_text) > 4000 else ocr_text
        
        prompt = f"""Extract ALL invoice data from the OCR text and return ONLY a JSON object.

OCR TEXT:
{ocr_snippet}

Return this EXACT JSON structure (no text before or after):
{{
  "invoice_number": "string",
  "order_number": "string or null",
  "invoice_date": "YYYY-MM-DD",
  "order_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "vendor": {{
    "name": "full company name",
    "address": "complete address",
    "phone": "phone or null",
    "email": "email or null"
  }},
  "customer": {{
    "name": "full customer name",
    "address": "complete address",
    "phone": "phone or null",
    "customer_id": "id or null"
  }},
  "amounts": {{
    "subtotal": 0.0,
    "tax": 0.0,
    "discount": 0.0,
    "freight": 0.0,
    "total": 0.0
  }},
  "line_items": [
    {{
      "product_id": "id or null",
      "description": "full product name",
      "quantity": 0.0,
      "unit": "CS/EA/LB",
      "unit_price": 0.0,
      "total_price": 0.0
    }}
  ],
  "payment_terms": "terms",
  "currency": "USD"
}}

RULES:
- Return ONLY the JSON object
- No explanations or markdown
- Use null for missing values (not "null" string)
- All prices as numbers not strings
- Extract ALL line items"""
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Groq response with aggressive cleanup"""
        if not response_text or not response_text.strip():
            return self._create_error_result("Empty response")
        
        original_text = response_text
        response_text = response_text.strip()
        
        # Remove markdown code blocks
        backtick = '`'
        markers = [
            backtick * 3 + 'json',
            backtick * 3 + 'JSON',
            backtick * 3
        ]
        for marker in markers:
            response_text = response_text.replace(marker, '')
        
        response_text = response_text.strip()
        
        # Try to extract JSON object with regex
        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
        json_matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        if json_matches:
            # Try largest match first (most likely to be complete)
            json_matches.sort(key=len, reverse=True)
            
            for json_str in json_matches:
                try:
                    # Clean up common issues
                    json_str = json_str.strip()
                    
                    # Fix trailing commas
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    
                    # Try to parse
                    data = json.loads(json_str)
                    
                    # Validate it has key fields
                    if 'invoice_number' in data or 'vendor' in data:
                        return data
                        
                except json.JSONDecodeError:
                    continue
        
        # If no valid JSON found, try the whole text
        try:
            # Remove any text before first {
            start_idx = response_text.find('{')
            if start_idx > 0:
                response_text = response_text[start_idx:]
            
            # Remove any text after last }
            end_idx = response_text.rfind('}')
            if end_idx > 0:
                response_text = response_text[:end_idx + 1]
            
            # Fix trailing commas
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
            
            data = json.loads(response_text)
            return data
            
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parse failed: {e}")
            print(f"   📄 Response length: {len(original_text)} chars")
            
            # Save problematic response for debugging
            debug_file = "debug_failed_response.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(original_text)
            print(f"   💾 Saved response to: {debug_file}")
            
            return self._create_error_result(f"JSON parse error: {e}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            "error": error_message,
            "extracted": False,
            "timestamp": datetime.now().isoformat()
        }


def validate_extracted_data(data: Dict[str, Any]) -> bool:
    """Validate extracted invoice data"""
    if data.get('error'):
        return False
        
    required_fields = ['invoice_number', 'vendor', 'customer', 'amounts', 'line_items']
    
    for field in required_fields:
        if field not in data:
            print(f"   ⚠️  Missing required field: {field}")
            return False
    
    if not isinstance(data.get('amounts', {}).get('total'), (int, float)):
        print(f"   ⚠️  Invalid total amount")
        return False
    
    if not isinstance(data.get('line_items'), list) or len(data.get('line_items', [])) == 0:
        print(f"   ⚠️  No line items found")
        return False
    
    return True
