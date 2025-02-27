from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt

# --- Database Setup ---
DATABASE_URL = "mssql+pyodbc://admin:admin@DESKTOP-18K402V/master?driver=ODBC+Driver+17+for+SQL+Server&timeout=180"

# Create Engine, Session, and Base
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# --- FastAPI App ---
app = FastAPI()

# --- Models ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))  # Store hashed password


# Create Tables on Startup
Base.metadata.create_all(bind=engine)

# --- Utility / Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# --- Routes ---
@app.post("/users/")
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_pwd = hash_password(password)
    new_user = User(username=username, email=email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email}

@app.get("/")
def main():
    return 'Deployed'

# --- Optional: Local Development Entry Point ---
# If you want to run locally with uvicorn:
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
