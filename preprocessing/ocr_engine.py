"""
Multi-Strategy OCR Engine
Two-tier: PaddleOCR + EasyOCR (No Tesseract!)
"""

from paddleocr import PaddleOCR
import easyocr
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Union
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

@dataclass
class OCRResult:
    """Store OCR results with metadata"""
    text: str
    boxes: List
    confidence: float
    method: str
    line_level_data: List[Dict]
    
    def to_dict(self):
        return asdict(self)

class MultiStrategyOCR:
    """Two-tier OCR: PaddleOCR -> EasyOCR"""
    
    def __init__(self, lang: str = 'en', use_gpu: bool = False):
        self.lang = lang
        self.use_gpu = use_gpu
        
        print("🔧 Initializing OCR engines...")
        
        # Initialize PaddleOCR
        try:
            print("   Loading PaddleOCR...")
            self.paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                show_log=False,
                use_gpu=use_gpu
            )
            print("   ✓ PaddleOCR ready")
        except Exception as e:
            print(f"   ✗ PaddleOCR failed: {e}")
            self.paddle_ocr = None
        
        # Initialize EasyOCR
        try:
            print("   Loading EasyOCR...")
            self.easy_reader = easyocr.Reader([lang], gpu=use_gpu, verbose=False)
            print("   ✓ EasyOCR ready")
        except Exception as e:
            print(f"   ✗ EasyOCR failed: {e}")
            self.easy_reader = None
        
        if not self.paddle_ocr and not self.easy_reader:
            raise RuntimeError("No OCR engines available!")
        
        print("✓ OCR ready\n")
    
    def extract_text(self, image_input: Union[Image.Image, np.ndarray, str], 
                     strategy: str = 'auto') -> OCRResult:
        """Extract text with automatic fallback"""
        img_array = self._prepare_image(image_input)
        
        if strategy == 'auto':
            result = self._paddle_extract(img_array)
            
            if result.confidence < 0.7:
                print(f"   ⚠️  Low confidence ({result.confidence:.2%}), trying EasyOCR...")
                easy_result = self._easy_extract(img_array)
                if easy_result.confidence > result.confidence:
                    result = easy_result
            
            return result
        
        elif strategy == 'paddle':
            return self._paddle_extract(img_array)
        elif strategy == 'easy':
            return self._easy_extract(img_array)
    
    def _prepare_image(self, image_input):
        """Convert input to numpy array"""
        if isinstance(image_input, str):
            img = cv2.imread(image_input)
        elif isinstance(image_input, Image.Image):
            img = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            img = image_input
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
        return img
    
    def _paddle_extract(self, img_array: np.ndarray) -> OCRResult:
        """Extract using PaddleOCR"""
        if self.paddle_ocr is None:
            return OCRResult("", [], 0.0, "paddle_unavailable", [])
        
        try:
            result = self.paddle_ocr.ocr(img_array, cls=True)
            
            if not result or not result[0]:
                return OCRResult("", [], 0.0, "paddle_no_text", [])
            
            full_text = []
            boxes = []
            confidences = []
            line_data = []
            
            for line in result[0]:
                box = line[0]
                text = line[1][0]
                conf = float(line[1][1])
                
                full_text.append(text)
                boxes.append(box)
                confidences.append(conf)
                
                line_data.append({
                    'text': text,
                    'box': [[float(p[0]), float(p[1])] for p in box],
                    'confidence': conf,
                    'bbox': self._get_bbox(box)
                })
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text="\n".join(full_text),
                boxes=boxes,
                confidence=avg_confidence,
                method="PaddleOCR",
                line_level_data=line_data
            )
            
        except Exception as e:
            print(f"   ✗ PaddleOCR error: {e}")
            return OCRResult("", [], 0.0, "paddle_error", [])
    
    def _easy_extract(self, img_array: np.ndarray) -> OCRResult:
        """Extract using EasyOCR"""
        if self.easy_reader is None:
            return OCRResult("", [], 0.0, "easy_unavailable", [])
        
        try:
            result = self.easy_reader.readtext(img_array)
            
            if not result:
                return OCRResult("", [], 0.0, "easy_no_text", [])
            
            full_text = []
            boxes = []
            confidences = []
            line_data = []
            
            for detection in result:
                box = detection[0]
                text = detection[1]
                conf = float(detection[2])
                
                full_text.append(text)
                boxes.append(box)
                confidences.append(conf)
                
                line_data.append({
                    'text': text,
                    'box': [[float(p[0]), float(p[1])] for p in box],
                    'confidence': conf,
                    'bbox': self._get_bbox(box)
                })
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text="\n".join(full_text),
                boxes=boxes,
                confidence=avg_confidence,
                method="EasyOCR",
                line_level_data=line_data
            )
            
        except Exception as e:
            print(f"   ✗ EasyOCR error: {e}")
            return OCRResult("", [], 0.0, "easy_error", [])
    
    def _get_bbox(self, box: List) -> List[int]:
        """Convert polygon to [x, y, width, height]"""
        x_coords = [p[0] for p in box]
        y_coords = [p[1] for p in box]
        
        x = int(min(x_coords))
        y = int(min(y_coords))
        w = int(max(x_coords) - x)
        h = int(max(y_coords) - y)
        
        return [x, y, w, h]
