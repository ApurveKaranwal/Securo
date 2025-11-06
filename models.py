from sqlalchemy import Column, Integer, String
from database import Base

class PasswordEntry(Base):
    __tablename__ = "passwords"
    id = Column(Integer, primary_key=True, index=True)
    service = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=False)
    password_enc = Column(String, nullable=False)

if __name__ == "__main__":
    print("Creating database...")
    Base.metadata.create_all(bind=engine)
    print("Database created successfully")
