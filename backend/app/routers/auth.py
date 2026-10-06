from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from ..database import db
from ..models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = "password"

class RegisterRequest(BaseModel):
    name: str
    email: str
    role: str = "student"
    student_id: Optional[str] = ""
    phone: Optional[str] = ""

@router.post("/login")
def login(req: LoginRequest):
    user = db.get_user_by_email(req.email)
    if not user:
        # If demo user not in list, auto-create for quick evaluation
        is_admin = "admin" in req.email.lower()
        new_user = User(
            id=f"USR-{uuid.uuid4().hex[:6].upper()}",
            name=req.email.split("@")[0].title(),
            email=req.email,
            role="admin" if is_admin else "student",
            student_id="230097010" + str(uuid.uuid4().int)[:4] if not is_admin else "FACULTY-001"
        )
        user = db.add_user(new_user)
    return {"status": "success", "user": user, "token": f"bearer_{user['id']}"}

@router.post("/register")
def register(req: RegisterRequest):
    existing = db.get_user_by_email(req.email)
    if existing:
        return {"status": "success", "user": existing, "token": f"bearer_{existing['id']}"}
    
    new_user = User(
        id=f"USR-{uuid.uuid4().hex[:6].upper()}",
        name=req.name,
        email=req.email,
        role=req.role,
        student_id=req.student_id,
        phone=req.phone
    )
    user = db.add_user(new_user)
    return {"status": "success", "user": user, "token": f"bearer_{user['id']}"}

@router.get("/users")
def list_users():
    return db.get_users()
