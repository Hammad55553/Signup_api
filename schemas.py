from pydantic import BaseModel, EmailStr
from typing import Optional

# User Create Schema (for registration)
class UserCreate(BaseModel):
    name: str
    email: EmailStr  # Improved validation for email
    password: str
    number: str

    class Config:
        from_attributes = True

# User Response Schema (for returning user data)
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr  # Using EmailStr for better validation
    number: str
    is_active: bool

    class Config:
        from_attributes = True

# User Login Schema (for login)
class UserLogin(BaseModel):
    email: EmailStr  # Improved validation for email
    password: str

# User Forgot Password Schema (for reset password request)
class UserForgotPassword(BaseModel):
    email: EmailStr  # Improved validation for email

    class Config:
        from_attributes = True

# User Reset Password Schema (for resetting the password)
class UserResetPassword(BaseModel):
    reset_token: str
    new_password: str

    class Config:
        from_attributes = True
