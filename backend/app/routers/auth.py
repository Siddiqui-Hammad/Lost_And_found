from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from ..database import db
from ..models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class StudentLoginRequest(BaseModel):
    identifier: str  # Email or Student Roll No
    password: str

class StudentRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    student_id: str  # Roll Number / Enrollment ID
    department: str = "Computer Science & Engineering"
    semester: str = "Semester 3"
    phone: Optional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = "password"

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: Optional[str] = "student123"
    role: str = "student"
    student_id: Optional[str] = ""
    department: Optional[str] = "Computer Science"
    semester: Optional[str] = "Semester 3"
    phone: Optional[str] = ""

@router.post("/admin/login")
def admin_login(req: AdminLoginRequest):
    # Search for admin user
    user = db.get_user_by_email(req.email)
    if user:
        if user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access Denied: Not an administrator account.")
        if req.password and user.get("password") and user.get("password") != req.password:
            raise HTTPException(status_code=401, detail="Invalid administrator password.")
        return {"status": "success", "user": user, "token": f"bearer_{user['id']}"}
    
    # Allow default admin login fallback if fresh db
    if req.email.lower() == "admin@campus.edu" and req.password == "admin123":
        admin_user = User(
            id="USR-ADMIN",
            name="Campus Administrator",
            email=req.email,
            password=req.password,
            role="admin",
            student_id="ADMIN-001",
            department="Dean Student Welfare",
            semester="Staff"
        )
        user_dict = db.add_user(admin_user)
        return {"status": "success", "user": user_dict, "token": f"bearer_{user_dict['id']}"}
    
    raise HTTPException(status_code=401, detail="Invalid administrator email or password.")

@router.post("/student/register")
def student_register(req: StudentRegisterRequest):
    # Check if email already registered
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="A student with this email address already exists.")
    
    # Check if student ID already registered
    for u in db.get_users():
        if u.get("student_id") and u.get("student_id").strip().lower() == req.student_id.strip().lower():
            raise HTTPException(status_code=400, detail="This Roll Number / Student ID is already registered.")

    new_user = User(
        id=f"USR-{uuid.uuid4().hex[:6].upper()}",
        name=req.name,
        email=req.email,
        password=req.password,
        role="student",
        student_id=req.student_id,
        department=req.department,
        semester=req.semester,
        phone=req.phone
    )
    user = db.add_user(new_user)
    return {"status": "success", "message": "Student registration successful!", "user": user, "token": f"bearer_{user['id']}"}

@router.post("/student/login")
def student_login(req: StudentLoginRequest):
    target = req.identifier.strip().lower()
    matched_user = None
    for u in db.get_users():
        if u.get("email", "").lower() == target or (u.get("student_id") and u.get("student_id").lower() == target):
            matched_user = u
            break
            
    if not matched_user:
        raise HTTPException(status_code=404, detail="Student account not found. Please sign up first.")
        
    if req.password and matched_user.get("password") and matched_user.get("password") != req.password:
        raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
        
    return {"status": "success", "user": matched_user, "token": f"bearer_{matched_user['id']}"}

@router.post("/login")
def login(req: LoginRequest):
    user = db.get_user_by_email(req.email)
    if not user:
        is_admin = "admin" in req.email.lower()
        new_user = User(
            id=f"USR-{uuid.uuid4().hex[:6].upper()}",
            name=req.email.split("@")[0].title(),
            email=req.email,
            password=req.password or "password123",
            role="admin" if is_admin else "student",
            student_id="2300970100099" if not is_admin else "ADMIN-001"
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
        password=req.password or "student123",
        role=req.role,
        student_id=req.student_id,
        department=req.department or "Computer Science",
        semester=req.semester or "Semester 3",
        phone=req.phone
    )
    user = db.add_user(new_user)
    return {"status": "success", "user": user, "token": f"bearer_{user['id']}"}

@router.get("/users")
def list_users():
    return db.get_users()
