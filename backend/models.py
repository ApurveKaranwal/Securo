from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class PasswordEntry(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    password_enc = Column(String, nullable=False)
    category = Column(String, default="General")
    strength = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class MasterKey(Base):
    __tablename__ = "master_key"

    id = Column(Integer, primary_key=True)
    password_hash = Column(String, nullable=False)

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True)
    service = Column(String)
    accessed_at = Column(DateTime, default=datetime.utcnow)
