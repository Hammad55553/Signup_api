from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from send_email import send_reset_password_email

# Secret Key and JWT Algorithm for Token Generation
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
RESET_TOKEN_EXPIRE_MINUTES = 15  # Token expiration time for reset requests

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to generate reset token
def create_reset_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to verify reset token
def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Forget Password Logic
def forget_password(email: str, db_session: Session):
    db_user = db_session.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a reset token
    reset_token = create_reset_token(data={"sub": db_user.id})

    # Send Reset Email
    reset_url = f"http://yourapp.com/reset-password?token={reset_token}"
    send_reset_password_email(email, reset_url)

    return {"message": "Password reset email sent."}

# Reset Password Logic
def reset_password(token: str, new_password: str, db_session: Session):
    user_id = verify_reset_token(token)

    db_user = db_session.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash the new password
    hashed_password = pwd_context.hash(new_password)

    # Update the user's password in the database
    db_user.password = hashed_password
    db_session.commit()

    return {"message": "Password has been reset successfully."}
