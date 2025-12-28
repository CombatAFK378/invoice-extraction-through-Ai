# 📊 Invoice Extraction System

**Automated invoice data extraction using OCR and LLM technology**

A complete end-to-end pipeline for extracting structured data from invoice PDFs using deep learning OCR (PaddleOCR, EasyOCR) and Large Language Models (Groq API with GPT-OSS 120B).

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

---

## 🎯 Project Overview

This system processes invoice PDFs through a 4-stage pipeline to extract, structure, and analyze invoice data with high accuracy.

### **Key Features**
- ✅ **100% PDF Success Rate**: Processed 32/32 invoices successfully
- ✅ **96.9% LLM Extraction Accuracy**: 31/32 invoices extracted correctly on first run
- ✅ **Multi-Strategy OCR**: PaddleOCR + EasyOCR with automatic fallback
- ✅ **Structured Data Export**: Normalized CSV schema with foreign keys
- ✅ **Interactive Dashboard**: Streamlit web app with analytics and visualizations
- ✅ **Zero Manual Dependencies**: Pure Python solution (no Tesseract/Poppler required)

### **Results**
- **32 invoices processed** from 2 vendors
- **186 line items extracted** across all invoices
- **4 normalized CSV tables** (invoices, line_items, vendors, customers)
- **Average processing time**: ~3-5 seconds per invoice

---

## 🏗️ Architecture

### **4-Stage Pipeline**

┌─────────────────────────────────────────────────────────────────┐
│ Stage 1: OCR Extraction │
│ PDF → Images → Text (PaddleOCR/EasyOCR) │
└─────────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────────┐
│ Stage 2: LLM-Based Field Extraction │
│ Raw Text → Structured JSON (Groq API - GPT-OSS 120B) │
└─────────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────────┐
│ Stage 3: Data Normalization │
│ JSON → Normalized CSV (4 tables with foreign keys) │
└─────────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────────┐
│ Stage 4: Analytics & Visualization │
│ CSV → Interactive Dashboard (Streamlit + Plotly) │
└─────────────────────────────────────────────────────────────────┘


---

## 🛠️ Tech Stack

### **Stage 1: OCR & PDF Processing**
- **PyMuPDF** - PDF rendering and manipulation
- **PaddleOCR** - High-accuracy deep learning OCR
- **EasyOCR** - Fallback OCR engine
- **OpenCV** - Image preprocessing
- **Pillow** - Image handling

### **Stage 2: LLM Extraction**
- **Groq API** - Ultra-fast LLM inference
- **GPT-OSS 120B Model** - Open-source large language model
- **Structured Output** - JSON schema validation

### **Stage 3: Data Processing**
- **Pandas** - Data manipulation and CSV export
- **JSON** - Intermediate data format

### **Stage 4: Dashboard**
- **Streamlit** - Web application framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data queries and filtering

---

## 📦 Installation

### **Prerequisites**
- Python 3.8 or higher
- pip package manager

### **1. Clone Repository**
git clone https://github.com/CombatAFK378/invoice-extraction-through-Ai.git
cd invoice-extraction-through-Ai


### **2. Create Virtual Environment**
Windows
python -m venv venv
venv\Scripts\activate

Linux/Mac
python3 -m venv venv
source venv/bin/activate


### **3. Install Dependencies**
pip install -r requirements.txt


### **4. Configure Environment**
Create a `.env` file in the project root:
GROQ_API_KEY=your_groq_api_key_here

Get your Groq API key from: https://console.groq.com/

---

## 🚀 Usage

### **Complete Pipeline (All Stages)**

Stage 1: OCR Extraction
python -m preprocessing.stage1_pipeline

Stage 2: LLM Field Extraction
python -m preprocessing.stage2_groq_pipeline

Stage 3: CSV Export
python -m preprocessing.stage3_csv_export

Stage 4: Launch Dashboard
streamlit run app.py

### **Individual Stage Testing**

Test Stage 1 (OCR)
python test_stage1.py

Test Stage 2 (Groq Extraction)
python test_stage2_groq.py


### **Retry Failed Extractions**
python retry_failed.py


---

## 📊 Data Schema

### **Output Structure**

<pre>
Output Structure
stage3_csv/
│
├── invoices.csv        # Invoice header data
├── line_items.csv      # Individual product line items
├── vendors.csv         # Vendor / supplier information
├── customers.csv       # Customer / buyer information
└── metadata.json       # Processing metadata
</pre>


### **Database Schema**

#### **invoices.csv**
| Field | Type | Description |
|-------|------|-------------|
| invoice_id | int | Primary key |
| invoice_number | str | Invoice number |
| invoice_date | date | Invoice date |
| vendor_id | int | Foreign key → vendors |
| customer_id | int | Foreign key → customers |
| total | float | Total amount |
| subtotal | float | Subtotal before tax |
| tax | float | Tax amount |

#### **line_items.csv**
| Field | Type | Description |
|-------|------|-------------|
| line_item_id | int | Primary key |
| invoice_id | int | Foreign key → invoices |
| product_id | str | Product code |
| description | str | Product description |
| quantity | float | Quantity ordered |
| unit_price | float | Price per unit |
| total_price | float | Line total |

#### **vendors.csv**
| Field | Type | Description |
|-------|------|-------------|
| vendor_id | int | Primary key |
| name | str | Vendor name |
| address | str | Vendor address |
| phone | str | Phone number |

#### **customers.csv**
| Field | Type | Description |
|-------|------|-------------|
| customer_id | int | Primary key |
| name | str | Customer name |
| address | str | Customer address |
| phone | str | Phone number |

---

## 📈 Dashboard Features

### **5 Interactive Pages**

1. **🏠 Dashboard** - Overview metrics, revenue trends, top products
2. **📋 Query Invoices** - Filter by vendor, date range, export results
3. **📦 Products** - Product analytics, purchase frequency, revenue
4. **🔍 Search** - Search products by name/description
5. **📄 Invoice Lookup** - Detailed invoice view with line items

### **Launch Dashboard**
streamlit run app.py


Access at: http://localhost:8501

---


---

## 🎯 Performance Metrics

### **Stage 1: OCR Extraction**
- **Success Rate**: 100% (32/32 invoices)
- **Average Confidence**: 92.5%
- **Average Time**: 2.1s per invoice
- **OCR Method**: PaddleOCR (primary), EasyOCR (fallback)

### **Stage 2: LLM Extraction**
- **Success Rate**: 96.9% (31/32 first run, 100% after retry)
- **Average Time**: 3.2s per invoice
- **Model**: Groq GPT-OSS 120B
- **Tokens Used**: ~85,000 total

### **Stage 3: Data Export**
- **Invoices**: 32
- **Line Items**: 186
- **Unique Vendors**: 2
- **Unique Customers**: 2-3
- **Export Time**: <1s

---

## 🔬 Technical Details

### **OCR Strategy**
1. **Primary**: PaddleOCR (deep learning, high accuracy)
2. **Fallback**: EasyOCR (if PaddleOCR fails)
3. **Preprocessing**: Automatic image enhancement
4. **Confidence Threshold**: 70%

### **LLM Prompt Engineering**
- Structured JSON output schema
- Field validation rules
- Error handling and retries
- Context window: 8192 tokens

### **Data Normalization**
- Automatic duplicate detection
- Foreign key relationships
- Type conversion and validation
- Metadata tracking

---

## 🚧 Known Issues & Limitations

### **Current Limitations**
1. **Vendor/Customer Duplicates**: Address variations create duplicate records (10 vendor rows → 2 actual vendors)
   - *Reason*: OCR inconsistencies + source document formatting differences
   - *Solution*: Fuzzy matching or manual deduplication (Stage 4 improvement)

2. **Two-Page Invoices**: Currently processes first page only
   - *Solution*: Multi-page processing (planned enhancement)

3. **Handwritten Text**: OCR struggles with handwriting
   - *Solution*: Use invoices with printed text

### **Data Quality Notes**
- OCR may misread similar characters (e.g., "1" vs "I", "0" vs "O")
- Address formatting inconsistencies are preserved (by design)
- Some invoices may require manual review

---

## 🔮 Future Enhancements

### **Planned Features**
- [ ] Multi-page invoice support
- [ ] Fuzzy matching for vendor/customer deduplication
- [ ] Batch upload via dashboard
- [ ] REST API for integration
- [ ] Docker containerization
- [ ] Database backend (PostgreSQL)
- [ ] Email notification system
- [ ] OCR confidence visualization
- [ ] Multi-language support
- [ ] Invoice template learning

---

## 📝 Example Output

### **Sample Invoice Processing**

**Input**: `Copy of ARPFIINVOEBTCHLASER (1).pdf`

**Stage 1 Output** (OCR):
{
"metadata": {
"filename": "Copy of ARPFIINVOEBTCHLASER (1).pdf",
"processing_time_seconds": 2.14,
"confidence": 0.925
},
"ocr_results": {
"method": "paddleocr",
"raw_text": "INVOICE 379183\nDate: 08/05/2025\n..."
}
}


**Stage 2 Output** (LLM Extraction):
{
"invoice_number": "379183",
"invoice_date": "2025-08-05",
"vendor": {
"name": "Pacific Food Importers Inc.",
"address": "18620 80th Court South, Building F, Kent, WA 98032"
},
"line_items": [
{
"product_id": "102950",
"description": "FLOUR POWER",
"quantity": 8.0,
"unit": "CS",
"unit_price": 24.063,
"total_price": 192.5
}
],
"total": 596.94
}


**Stage 3 Output**: Normalized CSV tables (see Data Schema section)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**GitHub**: [@CombatAFK378](https://github.com/CombatAFK378)

---

## 🙏 Acknowledgments

- **Groq** - Ultra-fast LLM inference
- **PaddlePaddle** - PaddleOCR framework
- **Streamlit** - Dashboard framework
- **Plotly** - Visualization library

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**⭐ If you find this project helpful, please consider giving it a star!**





