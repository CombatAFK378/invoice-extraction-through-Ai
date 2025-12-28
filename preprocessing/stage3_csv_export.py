"""
Stage 3: Export extracted invoice data to CSV files
Creates normalized CSV files for invoices, line items, vendors, and customers
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class CSVExporter:
    """Export Stage 2 JSON outputs to normalized CSV files"""
    
    def __init__(self, stage2_dir: str = "stage2_output", output_dir: str = "stage3_csv"):
        self.stage2_dir = Path(stage2_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Data containers
        self.vendors = []
        self.customers = []
        self.invoices = []
        self.line_items = []
        
        # ID tracking for normalization
        self.vendor_map = {}
        self.customer_map = {}
        self.invoice_counter = 1
        self.line_item_counter = 1
    
    def process_all_invoices(self):
        """Process all Stage 2 JSON files"""
        json_files = list(self.stage2_dir.glob("*.json"))
        
        print(f"\n🚀 Stage 3: CSV Export")
        print(f"   Found {len(json_files)} invoice files")
        print(f"   Output directory: {self.output_dir}")
        
        successful = 0
        failed = 0
        
        for json_file in json_files:
            try:
                self._process_invoice_file(json_file)
                successful += 1
            except Exception as e:
                print(f"   ❌ Error processing {json_file.name}: {e}")
                failed += 1
        
        print(f"\n📊 Processing complete:")
        print(f"   Successful: {successful}")
        print(f"   Failed: {failed}")
        
        # Export to CSV
        self._export_to_csv()
        
        return {
            "successful": successful,
            "failed": failed,
            "vendors": len(self.vendors),
            "customers": len(self.customers),
            "invoices": len(self.invoices),
            "line_items": len(self.line_items)
        }
    
    def _process_invoice_file(self, json_file: Path):
        """Process a single invoice JSON file"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Skip if extraction failed
        if data['invoice_data'].get('error'):
            print(f"   ⏭️  Skipping failed: {json_file.name}")
            return
        
        invoice_data = data['invoice_data']
        metadata = data['metadata']
        
        # Process vendor
        vendor_id = self._add_vendor(invoice_data['vendor'])
        
        # Process customer
        customer_id = self._add_customer(invoice_data['customer'])
        
        # Process invoice
        invoice_id = self._add_invoice(
            invoice_data, 
            metadata['source_file'],
            vendor_id, 
            customer_id
        )
        
        # Process line items
        for item in invoice_data.get('line_items', []):
            self._add_line_item(invoice_id, item)
    
    def _add_vendor(self, vendor: Dict[str, Any]) -> int:
        """Add vendor and return vendor_id"""
        vendor_key = f"{vendor.get('name', '')}|{vendor.get('address', '')}"
        
        if vendor_key in self.vendor_map:
            return self.vendor_map[vendor_key]
        
        vendor_id = len(self.vendors) + 1
        self.vendor_map[vendor_key] = vendor_id
        
        self.vendors.append({
            'vendor_id': vendor_id,
            'name': vendor.get('name'),
            'address': vendor.get('address'),
            'phone': vendor.get('phone'),
            'email': vendor.get('email')
        })
        
        return vendor_id
    
    def _add_customer(self, customer: Dict[str, Any]) -> int:
        """Add customer and return customer_id"""
        customer_key = f"{customer.get('name', '')}|{customer.get('address', '')}"
        
        if customer_key in self.customer_map:
            return self.customer_map[customer_key]
        
        customer_id = len(self.customers) + 1
        self.customer_map[customer_key] = customer_id
        
        self.customers.append({
            'customer_id': customer_id,
            'name': customer.get('name'),
            'address': customer.get('address'),
            'phone': customer.get('phone'),
            'customer_code': customer.get('customer_id')
        })
        
        return customer_id
    
    def _add_invoice(self, invoice_data: Dict[str, Any], source_file: str, 
                     vendor_id: int, customer_id: int) -> int:
        """Add invoice and return invoice_id"""
        invoice_id = self.invoice_counter
        self.invoice_counter += 1
        
        amounts = invoice_data.get('amounts', {})
        
        self.invoices.append({
            'invoice_id': invoice_id,
            'invoice_number': invoice_data.get('invoice_number'),
            'order_number': invoice_data.get('order_number'),
            'invoice_date': invoice_data.get('invoice_date'),
            'order_date': invoice_data.get('order_date'),
            'due_date': invoice_data.get('due_date'),
            'vendor_id': vendor_id,
            'customer_id': customer_id,
            'subtotal': amounts.get('subtotal'),
            'tax': amounts.get('tax'),
            'discount': amounts.get('discount'),
            'freight': amounts.get('freight'),
            'total': amounts.get('total'),
            'payment_terms': invoice_data.get('payment_terms'),
            'currency': invoice_data.get('currency', 'USD'),
            'source_file': source_file
        })
        
        return invoice_id
    
    def _add_line_item(self, invoice_id: int, item: Dict[str, Any]):
        """Add line item"""
        line_item_id = self.line_item_counter
        self.line_item_counter += 1
        
        self.line_items.append({
            'line_item_id': line_item_id,
            'invoice_id': invoice_id,
            'product_id': item.get('product_id'),
            'description': item.get('description'),
            'quantity': item.get('quantity'),
            'unit': item.get('unit'),
            'unit_price': item.get('unit_price'),
            'total_price': item.get('total_price')
        })
    
    def _export_to_csv(self):
        """Export all data to CSV files"""
        print(f"\n💾 Exporting to CSV files...")
        
        # Create DataFrames
        df_vendors = pd.DataFrame(self.vendors)
        df_customers = pd.DataFrame(self.customers)
        df_invoices = pd.DataFrame(self.invoices)
        df_line_items = pd.DataFrame(self.line_items)
        
        # Save to CSV
        csv_files = {
            'vendors.csv': df_vendors,
            'customers.csv': df_customers,
            'invoices.csv': df_invoices,
            'line_items.csv': df_line_items
        }
        
        for filename, df in csv_files.items():
            filepath = self.output_dir / filename
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"   ✅ {filename}: {len(df)} rows")
        
        # Print summary
        print(f"\n📊 Export Summary:")
        print(f"   Vendors: {len(self.vendors)}")
        print(f"   Customers: {len(self.customers)}")
        print(f"   Invoices: {len(self.invoices)}")
        print(f"   Line Items: {len(self.line_items)}")
        
        # Create metadata file
        self._create_metadata()
    
    def _create_metadata(self):
        """Create metadata file describing the CSVs"""
        metadata = {
            "export_date": datetime.now().isoformat(),
            "total_vendors": len(self.vendors),
            "total_customers": len(self.customers),
            "total_invoices": len(self.invoices),
            "total_line_items": len(self.line_items),
            "files": {
                "vendors.csv": "Unique vendors with contact information",
                "customers.csv": "Unique customers with contact information",
                "invoices.csv": "Invoice headers with totals and references",
                "line_items.csv": "Individual line items for each invoice"
            },
            "relationships": {
                "invoices.vendor_id": "→ vendors.vendor_id",
                "invoices.customer_id": "→ customers.customer_id",
                "line_items.invoice_id": "→ invoices.invoice_id"
            }
        }
        
        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   ✅ metadata.json")


def main():
    """Main execution"""
    print("=" * 60)
    print("STAGE 3: CSV EXPORT")
    print("=" * 60)
    
    exporter = CSVExporter()
    results = exporter.process_all_invoices()
    
    print("\n" + "=" * 60)
    print("CSV EXPORT COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Output location: stage3_csv/")
    print(f"   ✅ vendors.csv")
    print(f"   ✅ customers.csv")
    print(f"   ✅ invoices.csv")
    print(f"   ✅ line_items.csv")
    print(f"   ✅ metadata.json")


if __name__ == "__main__":
    main()
