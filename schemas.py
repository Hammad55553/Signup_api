from pydantic import BaseModel, EmailStr
from datetime import date

# User Create Schema (for registration)
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Improved validation for email
    password: str
    number: str

    class Config:
        orm_mode = True

# User Response Schema (for returning user data)
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr  # Using EmailStr for better validation
    number: str
    is_active: bool

    class Config:
        orm_mode = True

# User Login Schema (for login)
class UserLogin(BaseModel):
    email: EmailStr  # Improved validation for email
    password: str
