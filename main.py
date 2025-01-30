from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User  # Absolute import
from schemas import UserCreate, UserResponse  # Absolute import
from database import SessionLocal, Base  # Absolute import
from email_service import send_confirmation_email  # Updated import
from passlib.context import CryptContext
import uuid

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup Endpoint
@app.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = pwd_context.hash(user.password)

    # Save user to DB
    db_user = User(
        id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        password=hashed_password,
        dob=user.dob,
        is_active=True  # Directly mark user as active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send confirmation email with user's name
    send_confirmation_email(user.email, user.name)  # Pass user's name here

    return db_user

# Get User by ID Endpoint
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Get User by Email Endpoint
@app.get("/users/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user