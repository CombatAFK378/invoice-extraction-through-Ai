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
