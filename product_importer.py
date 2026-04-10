#!/usr/bin/env python3
"""
Aum Creations - Product Import Helper
Extracts products from sources and converts them to import format
"""

import json
import csv
from datetime import datetime
from typing import List, Dict

class ProductImporter:
    """Helper class for managing product imports"""
    
    CATEGORIES = [
        "Bridal Wear",
        "Casual Wear",
        "Ethnic Wear",
        "Party Wear",
        "Formal Wear",
        "Sarees",
        "Kurtis",
        "Suits",
        "Alterations",
        "Consultation"
    ]
    
    def __init__(self):
        self.products: List[Dict] = []
    
    def add_product(self, name: str, category: str, price: float, 
                   description: str, specifications: str = "", 
                   image_url: str = "", in_stock: bool = True) -> None:
        """Add a product to the import list"""
        
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Valid options: {self.CATEGORIES}")
        
        product = {
            "name": name,
            "category": category,
            "price": float(price),
            "description": description,
            "specifications": specifications,
            "image_url": image_url,
            "in_stock": in_stock,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.products.append(product)
        print(f"✅ Added: {name}")
    
    def add_products_from_csv(self, csv_file: str) -> None:
        """Import products from CSV file"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.add_product(
                        name=row.get('name', ''),
                        category=row.get('category', ''),
                        price=float(row.get('price', 0)),
                        description=row.get('description', ''),
                        specifications=row.get('specifications', ''),
                        image_url=row.get('image_url', ''),
                        in_stock=row.get('in_stock', 'true').lower() == 'true'
                    )
            print(f"✅ Loaded {len(self.products)} products from CSV")
        except FileNotFoundError:
            print(f"❌ File not found: {csv_file}")
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
    
    def add_products_from_json(self, json_file: str) -> None:
        """Import products from JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for product in data:
                        self.add_product(
                            name=product.get('name', ''),
                            category=product.get('category', ''),
                            price=float(product.get('price', 0)),
                            description=product.get('description', ''),
                            specifications=product.get('specifications', ''),
                            image_url=product.get('image_url', ''),
                            in_stock=product.get('in_stock', True)
                        )
            print(f"✅ Loaded {len(self.products)} products from JSON")
        except FileNotFoundError:
            print(f"❌ File not found: {json_file}")
        except Exception as e:
            print(f"❌ Error reading JSON: {e}")
    
    def export_to_csv(self, output_file: str) -> None:
        """Export products to CSV"""
        if not self.products:
            print("❌ No products to export")
            return
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'category', 'price', 'description', 'specifications', 'image_url', 'in_stock']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.products:
                    writer.writerow({
                        'name': product['name'],
                        'category': product['category'],
                        'price': product['price'],
                        'description': product['description'],
                        'specifications': product['specifications'],
                        'image_url': product['image_url'],
                        'in_stock': product['in_stock']
                    })
            
            print(f"✅ Exported {len(self.products)} products to {output_file}")
        except Exception as e:
            print(f"❌ Error exporting CSV: {e}")
    
    def export_to_json(self, output_file: str) -> None:
        """Export products to JSON"""
        if not self.products:
            print("❌ No products to export")
            return
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported {len(self.products)} products to {output_file}")
        except Exception as e:
            print(f"❌ Error exporting JSON: {e}")
    
    def get_products_json(self) -> str:
        """Get products as JSON string for API"""
        return json.dumps({"products": self.products}, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get import statistics"""
        if not self.products:
            return {"total": 0, "by_category": {}}
        
        stats = {
            "total": len(self.products),
            "by_category": {},
            "total_value": sum(p['price'] for p in self.products),
            "in_stock": sum(1 for p in self.products if p['in_stock'])
        }
        
        for product in self.products:
            category = product['category']
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1
        
        return stats
    
    def print_summary(self) -> None:
        """Print summary of loaded products"""
        stats = self.get_statistics()
        
        if stats['total'] == 0:
            print("No products loaded")
            return
        
        print("\n" + "="*50)
        print(f"📦 PRODUCT IMPORT SUMMARY")
        print("="*50)
        print(f"Total Products: {stats['total']}")
        print(f"In Stock: {stats['in_stock']}")
        print(f"Total Value: ₹{stats['total_value']:,.2f}")
        print(f"\nBy Category:")
        for category, count in stats['by_category'].items():
            print(f"  - {category}: {count}")
        print("="*50 + "\n")


# Example usage
if __name__ == "__main__":
    # Create importer
    importer = ProductImporter()
    
    # Add sample products manually
    print("Adding sample products...\n")
    
    importer.add_product(
        name="Bridal Lehenga - Red Gold",
        category="Bridal Wear",
        price=12000,
        description="Elegant bridal lehenga with heavy embroidery and beadwork",
        specifications="Material: Silk and Net | Length: 48 inches | Color: Red Gold",
        image_url="https://example.com/bridal-lehenga-1.jpg",
        in_stock=True
    )
    
    importer.add_product(
        name="Salwar Kameez - Cotton Print",
        category="Casual Wear",
        price=1500,
        description="Comfortable cotton salwar kameez with traditional prints",
        specifications="Material: Cotton | Fit: Comfortable | Pattern: Printed",
        image_url="https://example.com/salwar-1.jpg",
        in_stock=True
    )
    
    importer.add_product(
        name="Pure Silk Saree",
        category="Ethnic Wear",
        price=3500,
        description="Beautiful pure silk saree with zari border",
        specifications="Material: Silk | Length: 6 yards | Blouse: Included",
        image_url="https://example.com/saree-1.jpg",
        in_stock=True
    )
    
    importer.add_product(
        name="Rayon Kurti with Embroidery",
        category="Casual Wear",
        price=800,
        description="Trendy rayon kurti with beautiful embroidery",
        specifications="Material: Rayon | Length: 44 inches | Pattern: Embroidered",
        image_url="https://example.com/kurti-1.jpg",
        in_stock=True
    )
    
    importer.add_product(
        name="Palazzo Suit - Navy Blue",
        category="Party Wear",
        price=2500,
        description="Elegant palazzo suit with matching dupatta",
        specifications="Material: Georgette | Fit: Straight | Color: Navy Blue",
        image_url="https://example.com/palazzo-1.jpg",
        in_stock=True
    )
    
    # Print summary
    importer.print_summary()
    
    # Export to formats
    print("Exporting products...\n")
    importer.export_to_csv("products_import.csv")
    importer.export_to_json("products_import.json")
    
    # Print JSON for API
    print("\nJSON format for API bulk-import:")
    print(importer.get_products_json())
