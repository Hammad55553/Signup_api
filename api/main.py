from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User  # Importing User model from models.py
from schemas import UserCreate, UserResponse, UserLogin  # Importing schemas from schemas.py
from database import SessionLocal, engine, Base  # Importing DB connection
from email_service import send_confirmation_email  # Email service
from passlib.context import CryptContext
import uuid
from fastapi.middleware.cors import CORSMiddleware

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get DB session
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
        number=user.number,
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

# Login Endpoint
@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify password
    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user_id": db_user.id}

# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI !"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
