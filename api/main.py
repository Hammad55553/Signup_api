import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from email_service import send_password_reset_email, send_confirmation_email

# Firebase Imports
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import auth as firebase_auth

# Local Imports
from models import User
from schemas import UserCreate, UserResponse, UserLogin
from database import SessionLocal, engine, Base

# Load Environment Variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Firebase Initialization
cred = credentials.Certificate("packtrack-b7c89-firebase-adminsdk-fbsvc-91ddaf6ef7.json")  # Ensure correct path
firebase_admin.initialize_app(cred)
db_firebase = firestore.client()

# Database Tables Create
Base.metadata.create_all(bind=engine)

# FastAPI App Initialize
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT Token Generation
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Middleware to Get Current User
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Create a Pydantic model for forgot-password request body
from pydantic import BaseModel

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

# OTP Generation Function
import random
import string

def generate_otp(length=6):
    """Generate a random OTP"""
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

# Signup Endpoint
@app.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db_session: Session = Depends(get_db)):
    db_user = db_session.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        password=hashed_password,
        number=user.number,
        is_active=True
    )
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    # 🔹 Firebase Authentication me user create karo (same UID)
    try:
        firebase_auth.create_user(
            uid=new_user.id,
            email=user.email,
            password=user.password,  # Plain password, not hashed
            display_name=user.name
        )
    except Exception as e:
        print("Firebase Auth error:", e)

    # 🔹 Firebase me data store karo
    firebase_data = {
        "name": user.name,
        "email": user.email,
        "number": user.number,
        "is_active": True
    }
    db_firebase.collection("users").document(new_user.id).set(firebase_data)

    send_confirmation_email(user.email, user.name)

    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        number=new_user.number,
        is_active=new_user.is_active
    )

# Login Endpoint
@app.post("/login")
async def login(user: UserLogin, db_session: Session = Depends(get_db)):
    db_user = db_session.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.id}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {"access_token": token, "token_type": "bearer", "user_id": db_user.id}

# Forgot Password Endpoint (using request body)
@app.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest, 
    background_tasks: BackgroundTasks, 
    db_session: Session = Depends(get_db)
):
    db_user = db_session.query(User).filter(User.email == request.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate and store OTP with expiration (10 minutes)
    otp = generate_otp()
    db_user.reset_token = otp
    db_user.reset_token_expires = datetime.utcnow() + timedelta(minutes=10)
    db_session.commit()

    # Send email
    background_tasks.add_task(send_password_reset_email, request.email, otp)

    return {"message": "Password reset email sent"}

# Reset Password Endpoint
@app.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest, 
    db_session: Session = Depends(get_db)
):
    # Find user with valid, non-expired token
    db_user = db_session.query(User).filter(
        User.reset_token == request.reset_token,
        User.reset_token_expires > datetime.utcnow()
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Update password and clear token
    db_user.password = pwd_context.hash(request.new_password)
    db_user.reset_token = None
    db_user.reset_token_expires = None
    db_session.commit()

    return {"message": "Password reset successfully"}

# Get Logged-In User Data (Firebase Se Fetch Karo)
@app.get("/user/me")
async def get_user_me(uid: str = Depends(get_current_user)):
    user_ref = db_firebase.collection("users").document(uid)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc.to_dict()

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Secure FastAPI App!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
