"""
Verify all dependencies are installed
"""

def check_imports():
    print("="*60)
    print("VERIFYING DEPENDENCIES")
    print("="*60 + "\n")
    
    dependencies = [
        ("PyMuPDF (fitz)", "import fitz"),
        ("PaddleOCR", "from paddleocr import PaddleOCR"),
        ("EasyOCR", "import easyocr"),
        ("PIL/Pillow", "from PIL import Image"),
        ("OpenCV", "import cv2"),
        ("NumPy", "import numpy"),
    ]
    
    all_ok = True
    
    for name, import_stmt in dependencies:
        try:
            exec(import_stmt)
            print(f"✓ {name:20s} - INSTALLED")
        except ImportError:
            print(f"✗ {name:20s} - MISSING")
            all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print("✅ ALL DEPENDENCIES INSTALLED!")
        print("\n🎉 Features:")
        print("   ✓ NO Poppler needed")
        print("   ✓ NO Tesseract needed")
        print("   ✓ Pure Python solution")
        print("\n▶️  Next steps:")
        print("   1. Add invoice PDFs to 'data/' folder")
        print("   2. Run: python test_stage1.py")
    else:
        print("❌ MISSING DEPENDENCIES")
        print("\n📦 Run: pip install -r requirements.txt")
    print("="*60)

if __name__ == "__main__":
    check_imports()
