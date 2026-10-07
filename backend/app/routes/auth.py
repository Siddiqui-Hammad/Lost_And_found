from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import uuid
from ..database import db
from ..models.user import User
from ..schemas.auth import UserRegister, UserLogin, Token
from ..utils.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication token required")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    user = db.get_user_by_email(payload.get("email", ""))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Access forbidden: Administrator privilege required")
    return current_user

@router.post("/register", response_model=Token)
def register(req: UserRegister):
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")
        
    user_id = f"USR-{uuid.uuid4().hex[:6].upper()}"
    new_user = User(
        user_id=user_id,
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role or "STUDENT",
        student_id=req.student_id,
        department=req.department,
        semester=req.semester,
        phone=req.phone
    )
    saved = db.add_user(new_user.model_dump())
    
    token = create_access_token({"sub": saved["user_id"], "email": saved["email"], "role": saved["role"]})
    return Token(access_token=token, token_type="bearer", user=saved)

@router.post("/login", response_model=Token)
def login(req: UserLogin):
    user = db.get_user_by_identifier(req.identifier)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email/roll number or password.")
        
    if not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email/roll number or password.")
        
    token = create_access_token({"sub": user["user_id"], "email": user["email"], "role": user["role"]})
    return Token(access_token=token, token_type="bearer", user=user)

@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return current_user
