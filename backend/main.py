from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import PasswordEntry, MasterKey, AccessLog
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv
from datetime import datetime
import os, secrets, string, hashlib
from fastapi.middleware.cors import CORSMiddleware

# ---------------- ENV ----------------

load_dotenv()
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY not found in .env")

cipher = Fernet(FERNET_KEY.encode())

# bcrypt MUST be < 4.0
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Securo Password Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ---------------- DB DEP ----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- UTILS ----------------

def hash_master(password: str) -> str:
    """
    bcrypt supports only 72 bytes.
    So we SHA-256 first, then bcrypt.
    """
    sha = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha)

def verify_master(password: str, hashed: str) -> bool:
    sha = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.verify(sha, hashed)

def check_master(password: str, db: Session):
    master = db.query(MasterKey).first()
    if not master or not verify_master(password, master.password_hash):
        raise HTTPException(status_code=401, detail="Invalid master password")

def generate_password(length=16):
    if length < 12:
        raise HTTPException(400, "Password length must be at least 12")
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

def password_strength(password: str):
    score = 0
    score += min(len(password) * 4, 40)
    score += 15 if any(c.isupper() for c in password) else 0
    score += 15 if any(c.islower() for c in password) else 0
    score += 15 if any(c.isdigit() for c in password) else 0
    score += 15 if any(c in string.punctuation for c in password) else 0
    return min(score, 100)

def decrypt_password(enc: str):
    return cipher.decrypt(enc.encode()).decode()

# ---------------- SCHEMAS ----------------

class PasswordInput(BaseModel):
    service: str
    email: EmailStr
    length: int = Field(16, gt=0)
    category: str = "General"

class MasterPasswordInput(BaseModel):
    password: str = Field(min_length=8)

class PasswordListOut(BaseModel):
    service: str
    email: EmailStr
    category: str
    updated_at: datetime | None

    class Config:
        from_attributes = True

class PasswordExportOut(BaseModel):
    service: str
    email: EmailStr
    password: str
    category: str
    strength: int

    class Config:
        from_attributes = True

# ---------------- ROUTES ----------------

@app.post("/set-master", tags=["Security"])
def set_master_password(payload: MasterPasswordInput, db: Session = Depends(get_db)):
    if db.query(MasterKey).first():
        raise HTTPException(400, "Master password already set")

    db.add(MasterKey(password_hash=hash_master(payload.password)))
    db.commit()
    return {"message": "Master password set successfully"}

@app.post("/add", tags=["Passwords"])
def add_password(payload: PasswordInput, db: Session = Depends(get_db)):
    password = generate_password(payload.length)
    strength = password_strength(password)

    entry = PasswordEntry(
        service=payload.service,
        email=payload.email,
        password_enc=cipher.encrypt(password.encode()).decode(),
        category=payload.category,
        strength=strength
    )

    db.add(entry)
    db.commit()

    return {
        "service": payload.service,
        "email": payload.email,
        "password": password,
        "strength": strength
    }

@app.get("/retrieve", tags=["Passwords"])
def retrieve_password(service: str, master_password: str, db: Session = Depends(get_db)):
    check_master(master_password, db)

    entry = db.query(PasswordEntry).filter_by(service=service).first()
    if not entry:
        raise HTTPException(404, "Service not found")

    db.add(AccessLog(service=service))
    db.commit()

    return {
        "service": entry.service,
        "email": entry.email,
        "password": decrypt_password(entry.password_enc),
        "strength": entry.strength
    }

@app.put("/rotate", tags=["Passwords"])
def rotate_password(service: str, master_password: str, db: Session = Depends(get_db)):
    check_master(master_password, db)

    entry = db.query(PasswordEntry).filter_by(service=service).first()
    if not entry:
        raise HTTPException(404, "Service not found")

    new_password = generate_password()
    entry.password_enc = cipher.encrypt(new_password.encode()).decode()
    entry.updated_at = datetime.utcnow()
    entry.strength = password_strength(new_password)

    db.commit()
    return {"new_password": new_password}

@app.delete("/delete", tags=["Passwords"])
def delete_password(service: str, master_password: str, db: Session = Depends(get_db)):
    check_master(master_password, db)

    entry = db.query(PasswordEntry).filter_by(service=service).first()
    if not entry:
        raise HTTPException(404, "Service not found")

    db.delete(entry)
    db.commit()
    return {"message": "Password deleted successfully"}

@app.get("/list", response_model=list[PasswordListOut], tags=["Utility"])
def list_services(db: Session = Depends(get_db)):
    return db.query(PasswordEntry).all()

@app.get("/search", response_model=list[PasswordListOut], tags=["Utility"])
def search_services(query: str, db: Session = Depends(get_db)):
    return db.query(PasswordEntry).filter(
        PasswordEntry.service.ilike(f"%{query}%")
    ).all()

@app.get("/export", response_model=list[PasswordExportOut], tags=["Utility"])
def export_passwords(master_password: str, db: Session = Depends(get_db)):
    check_master(master_password, db)

    entries = db.query(PasswordEntry).all()
    return [
        PasswordExportOut(
            service=e.service,
            email=e.email,
            password=decrypt_password(e.password_enc),
            category=e.category,
            strength=e.strength
        )
        for e in entries
    ]

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}
