"""
Stage 4: Query and Analysis Functions
Provides functions to query and analyze invoice data from CSVs
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class InvoiceAnalyzer:
    """Query and analyze invoice data from CSV files"""
    
    def __init__(self, csv_dir: str = "stage3_csv"):
        """Load all CSV files"""
        self.csv_dir = Path(csv_dir)
        
        print("📊 Loading CSV data...")
        self.vendors = pd.read_csv(self.csv_dir / "vendors.csv")
        self.customers = pd.read_csv(self.csv_dir / "customers.csv")
        self.invoices = pd.read_csv(self.csv_dir / "invoices.csv")
        self.line_items = pd.read_csv(self.csv_dir / "line_items.csv")
        
        # Convert dates
        self.invoices['invoice_date'] = pd.to_datetime(self.invoices['invoice_date'])
        self.invoices['order_date'] = pd.to_datetime(self.invoices['order_date'], errors='coerce')
        self.invoices['due_date'] = pd.to_datetime(self.invoices['due_date'], errors='coerce')
        
        print(f"   ✅ Loaded {len(self.invoices)} invoices")
        print(f"   ✅ Loaded {len(self.line_items)} line items")
        print(f"   ✅ Loaded {len(self.vendors)} vendors")
        print(f"   ✅ Loaded {len(self.customers)} customers")
    
    def get_invoices_by_vendor(self, vendor_name: str, 
                                start_date: Optional[str] = None, 
                                end_date: Optional[str] = None) -> pd.DataFrame:
        """
        List all invoices from a specific vendor with optional date range
        
        Args:
            vendor_name: Vendor name (partial match supported)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with invoice details
        """
        # Find vendor IDs matching the name
        vendor_mask = self.vendors['name'].str.contains(vendor_name, case=False, na=False)
        vendor_ids = self.vendors[vendor_mask]['vendor_id'].tolist()
        
        if not vendor_ids:
            print(f"⚠️  No vendors found matching: {vendor_name}")
            return pd.DataFrame()
        
        # Filter invoices by vendor
        result = self.invoices[self.invoices['vendor_id'].isin(vendor_ids)].copy()
        
        # Apply date filters
        if start_date:
            result = result[result['invoice_date'] >= pd.to_datetime(start_date)]
        if end_date:
            result = result[result['invoice_date'] <= pd.to_datetime(end_date)]
        
        # Join with vendor names
        result = result.merge(
            self.vendors[['vendor_id', 'name']], 
            on='vendor_id', 
            how='left'
        ).rename(columns={'name': 'vendor_name'})
        
        return result
    
    def get_total_spend_by_vendor(self) -> pd.DataFrame:
        """
        Calculate total spend by vendor
        
        Returns:
            DataFrame with vendor names and total spend
        """
        # Join invoices with vendors
        vendor_spend = self.invoices.merge(
            self.vendors[['vendor_id', 'name']], 
            on='vendor_id', 
            how='left'
        )
        
        # Group by vendor and sum
        summary = vendor_spend.groupby('name').agg({
            'total': 'sum',
            'invoice_id': 'count'
        }).reset_index()
        
        summary.columns = ['vendor_name', 'total_spend', 'invoice_count']
        summary = summary.sort_values('total_spend', ascending=False)
        
        return summary
    
    def get_total_spend_by_customer(self) -> pd.DataFrame:
        """Calculate total spend by customer"""
        customer_spend = self.invoices.merge(
            self.customers[['customer_id', 'name']], 
            on='customer_id', 
            how='left'
        )
        
        summary = customer_spend.groupby('name').agg({
            'total': 'sum',
            'invoice_id': 'count'
        }).reset_index()
        
        summary.columns = ['customer_name', 'total_spend', 'invoice_count']
        summary = summary.sort_values('total_spend', ascending=False)
        
        return summary
    
    def get_top_products(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get most frequently purchased products
        
        Args:
            top_n: Number of top products to return
        
        Returns:
            DataFrame with product details
        """
        # Group by product and aggregate
        product_summary = self.line_items.groupby(['product_id', 'description']).agg({
            'quantity': 'sum',
            'total_price': 'sum',
            'line_item_id': 'count'
        }).reset_index()
        
        product_summary.columns = ['product_id', 'description', 'total_quantity', 
                                   'total_revenue', 'purchase_count']
        
        # Sort by purchase frequency
        product_summary = product_summary.sort_values('purchase_count', ascending=False)
        
        return product_summary.head(top_n)
    
    def get_invoice_details(self, invoice_number: str) -> Dict[str, Any]:
        """
        Get complete details for a specific invoice
        
        Args:
            invoice_number: Invoice number to lookup
        
        Returns:
            Dictionary with invoice header and line items
        """
        # Find invoice
        invoice = self.invoices[self.invoices['invoice_number'] == invoice_number]
        
        if invoice.empty:
            return {"error": f"Invoice {invoice_number} not found"}
        
        invoice = invoice.iloc[0]
        invoice_id = invoice['invoice_id']
        
        # Get vendor and customer
        vendor = self.vendors[self.vendors['vendor_id'] == invoice['vendor_id']].iloc[0]
        customer = self.customers[self.customers['customer_id'] == invoice['customer_id']].iloc[0]
        
        # Get line items
        items = self.line_items[self.line_items['invoice_id'] == invoice_id]
        
        return {
            "invoice_number": invoice['invoice_number'],
            "invoice_date": invoice['invoice_date'].strftime('%Y-%m-%d'),
            "total": float(invoice['total']),
            "vendor": {
                "name": vendor['name'],
                "address": vendor['address'],
                "phone": vendor['phone']
            },
            "customer": {
                "name": customer['name'],
                "address": customer['address'],
                "phone": customer['phone']
            },
            "line_items": items.to_dict('records'),
            "line_item_count": len(items)
        }
    
    def get_date_range_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get summary statistics for a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Dictionary with summary statistics
        """
        mask = (self.invoices['invoice_date'] >= pd.to_datetime(start_date)) & \
               (self.invoices['invoice_date'] <= pd.to_datetime(end_date))
        
        filtered = self.invoices[mask]
        
        return {
            "date_range": f"{start_date} to {end_date}",
            "invoice_count": len(filtered),
            "total_revenue": float(filtered['total'].sum()),
            "average_invoice_value": float(filtered['total'].mean()),
            "min_invoice": float(filtered['total'].min()),
            "max_invoice": float(filtered['total'].max())
        }
    
    def search_products(self, search_term: str) -> pd.DataFrame:
        """
        Search for products by description
        
        Args:
            search_term: Term to search in product descriptions
        
        Returns:
            DataFrame with matching products
        """
        mask = self.line_items['description'].str.contains(
            search_term, case=False, na=False
        )
        
        results = self.line_items[mask].copy()
        
        # Add invoice information
        results = results.merge(
            self.invoices[['invoice_id', 'invoice_number', 'invoice_date']], 
            on='invoice_id', 
            how='left'
        )
        
        return results[['invoice_number', 'invoice_date', 'product_id', 
                       'description', 'quantity', 'unit', 'unit_price', 'total_price']]
    
    def get_monthly_revenue(self) -> pd.DataFrame:
        """Get revenue by month"""
        monthly = self.invoices.copy()
        monthly['month'] = monthly['invoice_date'].dt.to_period('M')
        
        summary = monthly.groupby('month').agg({
            'total': 'sum',
            'invoice_id': 'count'
        }).reset_index()
        
        summary.columns = ['month', 'revenue', 'invoice_count']
        summary['month'] = summary['month'].astype(str)
        
        return summary
    
    def print_summary(self):
        """Print overall data summary"""
        print("\n" + "=" * 60)
        print("📊 INVOICE DATA SUMMARY")
        print("=" * 60)
        
        print(f"\n📅 Date Range:")
        print(f"   From: {self.invoices['invoice_date'].min().strftime('%Y-%m-%d')}")
        print(f"   To:   {self.invoices['invoice_date'].max().strftime('%Y-%m-%d')}")
        
        print(f"\n💰 Financial Summary:")
        print(f"   Total Revenue: ${self.invoices['total'].sum():,.2f}")
        print(f"   Average Invoice: ${self.invoices['total'].mean():,.2f}")
        print(f"   Total Invoices: {len(self.invoices)}")
        
        print(f"\n📦 Line Items:")
        print(f"   Total Items: {len(self.line_items)}")
        print(f"   Unique Products: {self.line_items['product_id'].nunique()}")
        print(f"   Avg Items per Invoice: {len(self.line_items) / len(self.invoices):.1f}")
        
        print(f"\n🏢 Vendors & Customers:")
        print(f"   Vendors: {len(self.vendors)}")
        print(f"   Customers: {len(self.customers)}")


def main():
    """Demo queries"""
    analyzer = InvoiceAnalyzer()
    
    # Print summary
    analyzer.print_summary()
    
    print("\n" + "=" * 60)
    print("📋 EXAMPLE QUERIES")
    print("=" * 60)
    
    # Query 1: Invoices from Pacific Food Importers
    print("\n1️⃣ Invoices from Pacific Food Importers (June-July 2025):")
    pacific_invoices = analyzer.get_invoices_by_vendor(
        "Pacific Food", 
        start_date="2025-06-01", 
        end_date="2025-07-31"
    )
    print(f"   Found {len(pacific_invoices)} invoices")
    print(pacific_invoices[['invoice_number', 'invoice_date', 'total']].head())
    
    # Query 2: Total spend by vendor
    print("\n2️⃣ Total Spend by Vendor:")
    vendor_spend = analyzer.get_total_spend_by_vendor()
    print(vendor_spend.head(10))
    
    # Query 3: Top products
    print("\n3️⃣ Top 10 Most Purchased Products:")
    top_products = analyzer.get_top_products(10)
    print(top_products[['description', 'purchase_count', 'total_quantity']])


if __name__ == "__main__":
    main()
