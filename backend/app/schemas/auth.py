from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    student_id: Optional[str] = None
    department: Optional[str] = "Computer Science & Engineering"
    semester: Optional[str] = "Semester 3"
    phone: Optional[str] = None
    role: Optional[str] = "STUDENT"

class UserLogin(BaseModel):
    identifier: str  # Email or Student ID
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
