from sqlalchemy import Column, String, Boolean, DateTime
from database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "newusers"  # Changed from "again" to be more descriptive
    
    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    number = Column(String)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)  # Add this for OTP storage
    reset_token_expires = Column(DateTime, nullable=True)  # Add expiration time