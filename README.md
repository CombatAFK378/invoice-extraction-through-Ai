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


