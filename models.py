from sqlalchemy import Column, String, Boolean, Date
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    dob = Column(Date)
    is_active = Column(Boolean, default=True)  # Directly set as active