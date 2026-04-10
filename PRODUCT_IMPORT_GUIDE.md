# 🛍️ Aum Creations - Product Import System

## Quick Start

This system allows you to add products to your website in **3 ways**:

1. **Single Product Form** - Add one product at a time through the admin dashboard
2. **CSV Upload** - Upload a spreadsheet with multiple products
3. **JSON Paste** - Paste product data as JSON

---

## 📋 Installation & Setup

### Step 1: Update Your Backend (server.py)

Replace your current `server.py` with the updated version that includes:
- ✅ `/api/products` - Get all products
- ✅ `/api/products/{id}` - Get single product
- ✅ `/api/products/bulk-import` - Import products from JSON
- ✅ `/api/products/import-csv` - Import products from CSV file

**Installation:**
```bash
pip install fastapi uvicorn python-jose passlib bcrypt python-dotenv motor pymongo cloudinary python-multipart slowapi
```

### Step 2: Update Your Admin Dashboard

Replace your `admin-dashboard.html` with the new version that includes:
- ✅ Single product form
- ✅ CSV file upload with drag-and-drop
- ✅ JSON data pasting
- ✅ Import progress tracking
- ✅ CSV template download

### Step 3: Start Your Servers

**Terminal 1 - Backend API:**
```bash
cd your-website-folder
uvicorn server:app --reload --port 5000
```

**Terminal 2 - Frontend:**
```bash
cd your-website-folder
python -m http.server 3000
```

Then open: `http://localhost:3000/admin-dashboard.html`

---

## 📁 Method 1: CSV Upload (Recommended)

### CSV Format

Create a spreadsheet (Excel or Google Sheets) with these columns:

| name | category | price | description | specifications | image_url | in_stock |
|------|----------|-------|-------------|-----------------|-----------|----------|
| Bridal Lehenga | Bridal Wear | 12000 | Elegant bridal lehenga | Material: Silk \| Length: 48 inches | https://... | true |
| Salwar Kameez | Casual Wear | 1500 | Cotton suit | Material: Cotton | https://... | true |

### Valid Categories

- Bridal Wear
- Casual Wear
- Ethnic Wear
- Party Wear
- Formal Wear
- Sarees
- Kurtis
- Suits
- Alterations
- Consultation

### Steps

1. Go to **Admin Dashboard** → **Bulk Import** tab
2. Click **CSV File Upload** section
3. Click the upload zone or drag-drop your CSV file
4. Click **Upload & Import**
5. ✅ Success! Products are now in your database

### Download Template

Click the **"📥 Download CSV Template"** button in the admin dashboard to get a pre-formatted CSV file.

---

## 🔗 Method 2: JSON Paste

### JSON Format

```json
[
  {
    "name": "Bridal Lehenga",
    "category": "Bridal Wear",
    "price": 12000,
    "description": "Elegant bridal lehenga with heavy embroidery",
    "specifications": "Material: Silk | Length: 48 inches | Color: Red Gold",
    "image_url": "https://example.com/image.jpg",
    "in_stock": true
  },
  {
    "name": "Salwar Kameez",
    "category": "Casual Wear",
    "price": 1500,
    "description": "Cotton suit with prints",
    "specifications": "Material: Cotton",
    "image_url": "https://example.com/image2.jpg",
    "in_stock": true
  }
]
```

### Steps

1. Go to **Admin Dashboard** → **Bulk Import** tab
2. Click **JSON Paste** section
3. Paste your JSON array in the textarea
4. Click **🚀 Import from JSON**
5. ✅ Success!

---

## ✏️ Method 3: Single Product Form

### Steps

1. Go to **Admin Dashboard** → **Add Single Product** tab
2. Fill in all fields:
   - **Product Name** (required)
   - **Category** (required) - choose from dropdown
   - **Price** (required) - in rupees
   - **Description** (required) - brief details
   - **Specifications** (optional) - e.g., "Material: Silk | Length: 48 inches"
   - **Image URL** (optional) - link to product image
   - **In Stock** - checkbox
3. Click **✅ Save Product**
4. ✅ Product saved!

---

## 🐍 Python Script Method (Advanced)

If you want to import products using Python:

```bash
python product_importer.py
```

This will:
- Load sample products
- Export to CSV and JSON
- Print summary statistics

### Use the Script

```python
from product_importer import ProductImporter

# Create importer
importer = ProductImporter()

# Add products
importer.add_product(
    name="Bridal Lehenga",
    category="Bridal Wear",
    price=12000,
    description="Elegant bridal lehenga",
    specifications="Material: Silk",
    image_url="https://...",
    in_stock=True
)

# Export to CSV
importer.export_to_csv("products.csv")

# Export to JSON
importer.export_to_json("products.json")

# Get API JSON format
print(importer.get_products_json())
```

---

## 🖼️ Product Images

### Option 1: Use Cloudinary (Recommended)

Your system already supports Cloudinary. When you upload images through the admin dashboard's file upload feature:

1. Image is sent to Cloudinary
2. You get a hosted URL automatically
3. That URL is saved in the database

### Option 2: External URLs

Paste direct URLs in the `image_url` field:
- Imgur: `https://i.imgur.com/xxxxx.jpg`
- Cloudinary: `https://res.cloudinary.com/...`
- Any hosted image URL

### Option 3: Add Image URLs Later

Leave `image_url` blank when importing. Add images later through the admin dashboard.

---

## 📊 Product Data Structure

Each product has:

```python
{
    "_id": "ObjectId",  # Auto-generated by MongoDB
    "name": "Product Name",
    "category": "Category",
    "price": 1000,
    "description": "Product description",
    "specifications": "Material, Size, etc",
    "image_url": "https://...",
    "in_stock": true,
    "created_at": "2024-04-09T...",
    "updated_at": "2024-04-09T..."
}
```

---

## 🔍 Verify Imports

After importing, verify products were added:

### Via API (Terminal)

```bash
curl http://localhost:5000/api/products
```

Response:
```json
{
  "success": true,
  "total": 5,
  "data": [
    {
      "_id": "...",
      "name": "Bridal Lehenga",
      ...
    }
  ]
}
```

### Via Admin Dashboard

Go to your main website to see products displayed (once you update your product display pages).

---

## ⚠️ Troubleshooting

### "API not accessible"
- Make sure both servers are running (port 5000 and 3000)
- Check `API_BASE` in admin dashboard matches your server address

### "CSV file not uploading"
- File must be `.csv` format
- Columns must match exactly: `name, category, price, description, specifications, image_url, in_stock`
- No special characters in file name

### "JSON import fails"
- Make sure it's valid JSON (use `jsonlint.com` to validate)
- Must be an array `[{...}, {...}]` not a single object
- All required fields: `name, category, price, description`

### "Images not showing"
- Image URLs must be complete (start with `http://` or `https://`)
- URL must point to a valid image file
- Check image still exists at that URL

---

## 📝 Next Steps

1. ✅ Download the template CSV
2. ✅ Fill in your products
3. ✅ Upload via admin dashboard
4. ✅ Verify products appear on your website
5. ✅ Update product display pages to show new items

---

## 💡 Tips

- **Bulk import is faster** for adding 10+ products
- **Test with 2-3 products first** to make sure format is correct
- **Keep product names unique** for easier management
- **Use clear descriptions** - customers read these!
- **Add good images** - they make a big difference in conversions
- **Update specifications** - sizes, materials, colors matter

---

## 🆘 Need Help?

Common issues and fixes:

| Issue | Solution |
|-------|----------|
| Products not appearing | Check `in_stock` is true, refresh browser cache |
| API returns 500 error | Check MongoDB is running or Atlas connection string is correct |
| Images show as broken | Verify image URL is correct and publicly accessible |
| CSV import fails | Download template and use exact format |
| Authentication required | Make sure JWT_SECRET is set in .env |

---

## 📞 Contact

For Aum Creations:
- **Email:** masterssanwal@gmail.com
- **Phone:** +91 92172 97800

---

**Last Updated:** April 2024
