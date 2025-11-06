#asks for email and service name, generates password, stores in db
#specific password retrieval: not implemented yet
#delete specific password: not implemented yet
#validation of email: not implemented yet


from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import PasswordEntry  
from cryptography.fernet import Fernet
import secrets
import string
import os
from pydantic import BaseModel, Field, EmailStr
#import validators

app = FastAPI(title="Securo Password Manager")
Base.metadata.create_all(bind=engine)

KEY_FILE = "secret.key"

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

key = load_key()
cipher = Fernet(key)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PasswordInput(BaseModel): 
    service: str
    email: EmailStr
    length: int = Field(15, gt=0, description="Length of password to generate")

def create_pass(length=15):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    specials = "!@#$%^&*()-_=+[]{};:,.<>?/"

    # Base characters
    all_chars = lowercase + uppercase + digits + specials

    # Ensure at least one of each required type
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(specials)
    ]

    # Fill the rest of the password length
    password += [secrets.choice(all_chars) for _ in range(length - len(password))]

    # Shuffle securely
    secrets.SystemRandom().shuffle(password)
    final_password = ''.join(password)

    return final_password


def decrypt_password(enc_password):
    return cipher.decrypt(enc_password.encode()).decode()

@app.post("/add",tags=["Create Password"])
def add_password(payload: PasswordInput, db: Session = Depends(get_db)):
    try:
        # Auto-generate password
        plain_password = create_pass(length=payload.length)

        # Encrypt password
        encrypted = cipher.encrypt(plain_password.encode()).decode()

        # Create DB entry
        new_entry = PasswordEntry(
            service=payload.service,
            email=payload.email,
            password_enc=encrypted
        )

        # Store in DB
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        return {
            "message": f"Password added for {payload.service}",
            "email": payload.email,
            "generated_password": plain_password
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/delete", tags=["Delete Password"])
def delete_password(service: str, db: Session = Depends(get_db)):
    entry = db.query(PasswordEntry).filter(PasswordEntry.service == service).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Service not found")

    try:
        db.delete(entry)
        db.commit()
        return {"message": f"Password entry for {service} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/retrieve", tags=["Retrieve Password"])
def retrieve_password(service: str, db: Session = Depends(get_db)):
    entry = db.query(PasswordEntry).filter(PasswordEntry.service == service).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Service not found")

    try:
        decrypted_password = decrypt_password(entry.password_enc)
        return {
            "service": entry.service,
            "email": entry.email,
            "password": decrypted_password
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update", tags=["Update Password"])
def update_password(payload: PasswordInput, db: Session = Depends(get_db)):
    entry = db.query(PasswordEntry).filter(
        PasswordEntry.service == payload.service,
        PasswordEntry.email == payload.email
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Generate new password
    new_password = create_pass(payload.length)
    entry.password_enc = cipher.encrypt(new_password.encode()).decode()
    db.commit()
    return {"message": f"Password updated for {payload.service}", "new_password": new_password}
    