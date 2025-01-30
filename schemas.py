from pydantic import BaseModel, EmailStr
from datetime import date

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    dob: date

class UserResponse(BaseModel):
    name: str
    email: str
    dob: date
    is_active: bool