from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import logging
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import csv
import io
from pydantic import BaseModel, ValidationError
from typing import Optional

load_dotenv()

# ── Logging (stdout only — Railway captures it) ───────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError(
        "JWT_SECRET not set. Add it in Railway → Settings → Variables."
    )

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "aum_creations")

app = FastAPI(title="Aum Creations API", version="1.0.0")

# ── Static files ──────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── MongoDB ───────────────────────────────────────────────────────────────────
mongo_client = AsyncIOMotorClient(MONGODB_URI)
db: AsyncIOMotorDatabase = mongo_client[DB_NAME]

@app.on_event("startup")
async def startup_event():
    try:
        await db.command("ping")
        logger.info("✅ MongoDB connected")
    except Exception as e:
        logger.critical(f"❌ MongoDB failed: {e}")
        raise RuntimeError(f"Cannot connect to MongoDB: {e}")
    try:
        await db.users.create_index("email", unique=True)
        await db.products.create_index("category")
        await db.products.create_index([("category", 1), ("price", 1)])
    except Exception as e:
        logger.warning(f"Index warning: {e}")

# ── Password helpers ──────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

# ── JWT ───────────────────────────────────────────────────────────────────────
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Models ────────────────────────────────────────────────────────────────────
class User(BaseModel):
    email: str
    password: str

class Product(BaseModel):
    name: str
    category: str
    price: float
    description: str
    specifications: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    specifications: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: Optional[bool] = None

class ServiceModel(BaseModel):
    name: str
    category: str
    price: Optional[float] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    active: bool = True

class FeedbackModel(BaseModel):
    name: str
    role: Optional[str] = None
    message: str
    rating: Optional[int] = 5
    active: bool = True

# ── HTML page routes ──────────────────────────────────────────────────────────
@app.get("/")
async def home():
    return FileResponse("templates/index.html")

@app.get("/about")
async def about():
    return FileResponse("templates/about.html")

@app.get("/services")
async def services_page():
    return FileResponse("templates/services.html")

@app.get("/contact")
async def contact():
    return FileResponse("templates/contact.html")

@app.get("/portfolio")
async def portfolio():
    return FileResponse("templates/portfolio.html")

@app.get("/admin-login")
async def admin_login():
    return FileResponse("templates/admin-login.html")

@app.get("/admin-dashboard")
async def admin_dashboard():
    return FileResponse("templates/admin-dashboard.html")

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    try:
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}

# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/api/auth/register")
async def register(user: User):
    try:
        if await db.users.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already registered")
        await db.users.insert_one({
            "email": user.email,
            "password_hash": hash_password(user.password),
            "created_at": datetime.utcnow()
        })
        return {"message": "User registered successfully", "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login(user: User):
    try:
        user_doc = await db.users.find_one({"email": user.email})
        if not user_doc or not verify_password(user.password, user_doc.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = jwt.encode(
            {"sub": user.email, "exp": datetime.utcnow() + timedelta(hours=24)},
            JWT_SECRET, algorithm="HS256"
        )
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Products ──────────────────────────────────────────────────────────────────
@app.get("/api/products")
async def get_products(skip: int = 0, limit: int = 50):
    skip = max(0, skip)
    limit = max(1, min(limit, 100))
    products = await db.products.find().skip(skip).limit(limit).to_list(length=limit)
    total = await db.products.count_documents({})
    for p in products:
        p["_id"] = str(p["_id"])
    return {"success": True, "total": total, "data": products}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    from bson.objectid import ObjectId
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product["_id"] = str(product["_id"])
    return {"success": True, "data": product}

@app.post("/api/products")
async def create_product(product: Product, user=Depends(verify_token)):
    d = product.dict()
    d["created_at"] = d["updated_at"] = datetime.utcnow()
    result = await db.products.insert_one(d)
    d["_id"] = str(result.inserted_id)
    return {"success": True, "message": "Product created", "data": d}

@app.put("/api/products/{product_id}")
async def update_product(product_id: str, product: ProductUpdate, user=Depends(verify_token)):
    from bson.objectid import ObjectId
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    update_data = product.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    result = await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "message": "Product updated"}

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, user=Depends(verify_token)):
    from bson.objectid import ObjectId
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "message": "Product deleted"}

@app.post("/api/products/bulk-import")
async def bulk_import(payload: dict, user=Depends(verify_token)):
    products = payload.get("products", [])
    if not isinstance(products, list):
        raise HTTPException(status_code=400, detail="Products must be an array")
    valid, errors = [], []
    for idx, item in enumerate(products):
        try:
            d = Product(**item).dict()
            d["created_at"] = d["updated_at"] = datetime.utcnow()
            valid.append(d)
        except ValidationError as ve:
            errors.append({"index": idx, "error": str(ve)})
    if errors:
        raise HTTPException(status_code=400, detail=f"Validation errors: {errors}")
    result = await db.products.insert_many(valid)
    ids = [str(i) for i in result.inserted_ids]
    return {"success": True, "imported_count": len(ids), "ids": ids}

@app.post("/api/products/import-csv")
async def import_csv(file: UploadFile = File(...), user=Depends(verify_token)):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    ids = []
    for row in reader:
        try:
            price = float(row.get("price", 0))
        except (ValueError, TypeError):
            price = 0.0
        d = {
            "name": row.get("name", ""), "category": row.get("category", ""),
            "price": price, "description": row.get("description", ""),
            "specifications": row.get("specifications", ""),
            "image_url": row.get("image_url", ""),
            "in_stock": row.get("in_stock", "true").lower() in ["true", "1"],
            "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
        }
        result = await db.products.insert_one(d)
        ids.append(str(result.inserted_id))
    return {"success": True, "imported_count": len(ids), "ids": ids}

# ── Categories ────────────────────────────────────────────────────────────────
@app.get("/api/categories")
async def get_categories():
    return {"success": True, "categories": [
        "Bridal Wear", "Casual Wear", "Ethnic Wear", "Party Wear",
        "Formal Wear", "Sarees", "Kurtis", "Suits", "Alterations", "Consultation"
    ]}

# ── Services ──────────────────────────────────────────────────────────────────
DEFAULT_SERVICES = [
    {"name": "Bridal Lehenga Stitching", "category": "bridal", "price": 3000, "icon": "fas fa-gem", "description": "Exquisite custom bridal lehengas crafted with premium fabrics and intricate detailing.", "active": True},
    {"name": "Custom Suit Tailoring", "category": "custom", "price": 800, "icon": "fas fa-paint-brush", "description": "Bespoke salwar suits and Punjabi suits stitched to perfection.", "active": True},
    {"name": "Blouse Stitching", "category": "custom", "price": 300, "icon": "fas fa-shirt", "description": "Designer blouse stitching with precision fit and hand embroidery.", "active": True},
    {"name": "Saree Fall & Pico", "category": "alterations", "price": 150, "icon": "fas fa-scissors", "description": "Expert saree fall stitching and pico border.", "active": True},
    {"name": "Embroidery & Hand Work", "category": "custom", "price": 500, "icon": "fas fa-star", "description": "Traditional zari, gota, mirror work and thread embroidery.", "active": True},
    {"name": "Alteration & Fitting", "category": "alterations", "price": 150, "icon": "fas fa-wrench", "description": "Professional alterations for perfect fit.", "active": True},
    {"name": "Designer Kurti Stitching", "category": "custom", "price": 400, "icon": "fas fa-palette", "description": "Trendy kurtis in your fabric — anarkali, A-line, straight or asymmetric.", "active": True},
    {"name": "Party Wear Gown", "category": "custom", "price": 1500, "icon": "fas fa-crown", "description": "Glamorous gowns for receptions, sangeets and special occasions.", "active": True},
    {"name": "Design Consultation", "category": "custom", "price": 0, "icon": "fas fa-comments", "description": "Free one-on-one consultation with our expert designers.", "active": True},
]

@app.get("/api/services")
async def get_services():
    docs = await db.services.find({"active": True}).to_list(100)
    if not docs:
        await db.services.insert_many([{**s, "created_at": datetime.utcnow()} for s in DEFAULT_SERVICES])
        docs = await db.services.find({"active": True}).to_list(100)
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"success": True, "data": docs}

@app.post("/api/services")
async def create_service(service: ServiceModel, user=Depends(verify_token)):
    result = await db.services.insert_one({**service.dict(), "created_at": datetime.utcnow()})
    return {"success": True, "id": str(result.inserted_id)}

@app.put("/api/services/{service_id}")
async def update_service(service_id: str, service: ServiceModel, user=Depends(verify_token)):
    from bson import ObjectId
    await db.services.update_one({"_id": ObjectId(service_id)}, {"$set": {**service.dict(), "updated_at": datetime.utcnow()}})
    return {"success": True}

@app.delete("/api/services/{service_id}")
async def delete_service(service_id: str, user=Depends(verify_token)):
    from bson import ObjectId
    await db.services.delete_one({"_id": ObjectId(service_id)})
    return {"success": True}

# ── Feedback ──────────────────────────────────────────────────────────────────
@app.get("/api/feedback")
async def get_feedback(all: bool = False):
    query = {} if all else {"active": True}
    docs = await db.feedback.find(query).sort("created_at", -1).to_list(50)
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"success": True, "data": docs}

@app.post("/api/feedback")
async def create_feedback(feedback: FeedbackModel, user=Depends(verify_token)):
    result = await db.feedback.insert_one({**feedback.dict(), "created_at": datetime.utcnow()})
    return {"success": True, "id": str(result.inserted_id)}

@app.put("/api/feedback/{feedback_id}")
async def update_feedback(feedback_id: str, feedback: FeedbackModel, user=Depends(verify_token)):
    from bson import ObjectId
    await db.feedback.update_one({"_id": ObjectId(feedback_id)}, {"$set": {**feedback.dict(), "updated_at": datetime.utcnow()}})
    return {"success": True}

@app.delete("/api/feedback/{feedback_id}")
async def delete_feedback(feedback_id: str, user=Depends(verify_token)):
    from bson import ObjectId
    await db.feedback.delete_one({"_id": ObjectId(feedback_id)})
    return {"success": True}

# ── Railway entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
