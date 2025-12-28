"""
Invoice Extraction System - Interactive Dashboard
Streamlit web application for querying and analyzing invoices
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis.queries import InvoiceAnalyzer
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Invoice Extraction System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize analyzer
@st.cache_resource
def load_data():
    """Load invoice data (cached)"""
    return InvoiceAnalyzer()

analyzer = load_data()

# Helper function for JSON serialization
def convert_to_json_serializable(obj):
    """Convert pandas/numpy types to native Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif hasattr(obj, 'item'):  # numpy/pandas scalar types
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy arrays
        return obj.tolist()
    elif pd.isna(obj):  # Handle NaN values
        return None
    else:
        return obj

# Header
st.markdown('<div class="main-header">📊 Invoice Extraction System</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/invoice.png", width=100)
    st.title("Navigation")
    
    page = st.radio(
        "Select Page:",
        ["🏠 Dashboard", "📋 Query Invoices", "📦 Products", "🔍 Search", "📄 Invoice Lookup"]
    )
    
    st.markdown("---")
    st.info(f"""
    **Data Summary**
    - 📄 Invoices: {len(analyzer.invoices)}
    - 📦 Line Items: {len(analyzer.line_items)}
    - 🏢 Vendors: {len(analyzer.vendors)}
    - 👥 Customers: {len(analyzer.customers)}
    """)

# ============================================================
# PAGE 1: DASHBOARD
# ============================================================
if page == "🏠 Dashboard":
    st.header("📊 Overview Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"${analyzer.invoices['total'].sum():,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📄 Total Invoices",
            value=len(analyzer.invoices),
            delta=None
        )
    
    with col3:
        st.metric(
            label="📦 Total Line Items",
            value=len(analyzer.line_items),
            delta=None
        )
    
    with col4:
        st.metric(
            label="💵 Avg Invoice Value",
            value=f"${analyzer.invoices['total'].mean():,.2f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Spend by Vendor")
        vendor_spend = analyzer.get_total_spend_by_vendor()
        
        fig = px.bar(
            vendor_spend,
            x='vendor_name',
            y='total_spend',
            color='total_spend',
            color_continuous_scale='Blues',
            labels={'total_spend': 'Total Spend ($)', 'vendor_name': 'Vendor'}
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show table
        st.dataframe(vendor_spend, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📈 Monthly Revenue Trend")
        monthly = analyzer.get_monthly_revenue()
        
        fig = px.line(
            monthly,
            x='month',
            y='revenue',
            markers=True,
            labels={'revenue': 'Revenue ($)', 'month': 'Month'}
        )
        fig.update_traces(line_color='#1f77b4', line_width=3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show table
        st.dataframe(monthly, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Top Products
    st.subheader("🏆 Top 10 Products")
    top_products = analyzer.get_top_products(10)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            top_products,
            y='description',
            x='purchase_count',
            orientation='h',
            color='total_revenue',
            color_continuous_scale='Greens',
            labels={'purchase_count': 'Purchase Count', 'description': 'Product'}
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            top_products[['description', 'purchase_count', 'total_quantity']],
            use_container_width=True,
            hide_index=True,
            height=500
        )

# ============================================================
# PAGE 2: QUERY INVOICES
# ============================================================
elif page == "📋 Query Invoices":
    st.header("📋 Query Invoices by Vendor and Date")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get unique vendor names
        unique_vendors = analyzer.vendors['name'].unique()
        vendor_search = st.selectbox(
            "Select Vendor:",
            ["All"] + list(unique_vendors)
        )
    
    with col2:
        start_date = st.date_input(
            "Start Date:",
            value=analyzer.invoices['invoice_date'].min()
        )
    
    with col3:
        end_date = st.date_input(
            "End Date:",
            value=analyzer.invoices['invoice_date'].max()
        )
    
    # Query button
    if st.button("🔍 Search", type="primary"):
        if vendor_search == "All":
            # Filter by date only
            mask = (analyzer.invoices['invoice_date'] >= pd.to_datetime(start_date)) & \
                   (analyzer.invoices['invoice_date'] <= pd.to_datetime(end_date))
            results = analyzer.invoices[mask].copy()
            results = results.merge(
                analyzer.vendors[['vendor_id', 'name']], 
                on='vendor_id', 
                how='left'
            ).rename(columns={'name': 'vendor_name'})
        else:
            results = analyzer.get_invoices_by_vendor(
                vendor_search,
                start_date=str(start_date),
                end_date=str(end_date)
            )
        
        st.success(f"✅ Found {len(results)} invoices")
        
        if len(results) > 0:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue", f"${results['total'].sum():,.2f}")
            with col2:
                st.metric("Average Invoice", f"${results['total'].mean():,.2f}")
            with col3:
                st.metric("Invoice Count", len(results))
            
            # Display results
            st.dataframe(
                results[['invoice_number', 'invoice_date', 'vendor_name', 'order_number', 'total', 'payment_terms']],
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv = results.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"invoices_{vendor_search}_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No invoices found for the selected criteria.")

# ============================================================
# PAGE 3: PRODUCTS
# ============================================================
elif page == "📦 Products":
    st.header("📦 Product Analysis")
    
    # Top N selector
    top_n = st.slider("Show Top N Products:", min_value=5, max_value=50, value=15, step=5)
    
    top_products = analyzer.get_top_products(top_n)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Unique Products", analyzer.line_items['product_id'].nunique())
    with col2:
        st.metric("Total Quantity Sold", f"{analyzer.line_items['quantity'].sum():,.0f}")
    with col3:
        st.metric("Total Revenue", f"${analyzer.line_items['total_price'].sum():,.2f}")
    with col4:
        st.metric("Avg Items/Invoice", f"{len(analyzer.line_items) / len(analyzer.invoices):.1f}")
    
    st.markdown("---")
    
    # Visualization tabs
    tab1, tab2 = st.tabs(["📊 Chart View", "📋 Table View"])
    
    with tab1:
        # Purchase frequency
        fig = px.bar(
            top_products,
            x='description',
            y='purchase_count',
            color='total_revenue',
            color_continuous_scale='Viridis',
            labels={'purchase_count': 'Purchase Count', 'description': 'Product', 'total_revenue': 'Revenue ($)'}
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.dataframe(
            top_products,
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# PAGE 4: SEARCH
# ============================================================
elif page == "🔍 Search":
    st.header("🔍 Search Products")
    
    search_term = st.text_input(
        "Enter search term (e.g., 'FLOUR', 'TOMATO', 'MILK'):",
        placeholder="Type product name..."
    )
    
    if search_term:
        results = analyzer.search_products(search_term)
        
        if len(results) > 0:
            st.success(f"✅ Found {len(results)} matching line items")
            
            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Quantity", f"{results['quantity'].sum():,.1f}")
            with col2:
                st.metric("Total Value", f"${results['total_price'].sum():,.2f}")
            with col3:
                st.metric("Unique Products", results['description'].nunique())
            
            # Results table
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )
            
            # Download
            csv = results.to_csv(index=False)
            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name=f"search_{search_term}.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No products found matching '{search_term}'")

# ============================================================
# PAGE 5: INVOICE LOOKUP
# ============================================================
elif page == "📄 Invoice Lookup":
    st.header("📄 Invoice Details Lookup")
    
    # Get all invoice numbers
    invoice_numbers = analyzer.invoices['invoice_number'].tolist()
    
    selected_invoice = st.selectbox(
        "Select Invoice Number:",
        invoice_numbers
    )
    
    if st.button("🔍 Load Invoice", type="primary"):
        details = analyzer.get_invoice_details(selected_invoice)
        
        if "error" not in details:
            # Header
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 Invoice Information")
                st.write(f"**Invoice Number:** {details['invoice_number']}")
                st.write(f"**Invoice Date:** {details['invoice_date']}")
                st.write(f"**Total Amount:** ${details['total']:,.2f}")
                st.write(f"**Line Items:** {details['line_item_count']}")
            
            with col2:
                st.subheader("🏢 Vendor")
                st.write(f"**Name:** {details['vendor']['name']}")
                st.write(f"**Address:** {details['vendor']['address']}")
                st.write(f"**Phone:** {details['vendor']['phone']}")
            
            st.markdown("---")
            
            st.subheader("👥 Customer")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {details['customer']['name']}")
                st.write(f"**Phone:** {details['customer']['phone']}")
            with col2:
                st.write(f"**Address:** {details['customer']['address']}")
            
            st.markdown("---")
            
            # Line items
            st.subheader("📦 Line Items")
            line_items_df = pd.DataFrame(details['line_items'])
            st.dataframe(
                line_items_df[['product_id', 'description', 'quantity', 'unit', 'unit_price', 'total_price']],
                use_container_width=True,
                hide_index=True
            )
            
            # Download invoice as JSON (FIXED)
            json_ready_details = convert_to_json_serializable(details)
            json_str = json.dumps(json_ready_details, indent=2)
            
            st.download_button(
                label="📥 Download Invoice JSON",
                data=json_str,
                file_name=f"invoice_{selected_invoice}.json",
                mime="application/json"
            )
        else:
            st.error(details['error'])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 Invoice Extraction System | Built with Streamlit, Tesseract, and Groq API</p>
    <p>Stage 1: OCR | Stage 2: LLM Extraction | Stage 3: CSV Export | Stage 4: Analytics</p>
</div>
""", unsafe_allow_html=True)
