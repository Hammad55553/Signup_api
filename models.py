from sqlalchemy import Column, String, Boolean, Date
from database import Base

class User(Base):
    __tablename__ = "Test"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    number = Column(String)
    is_active = Column(Boolean, default=True)