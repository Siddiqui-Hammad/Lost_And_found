from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    user_id: str
    name: str
    email: str
    password_hash: str
    role: str = "STUDENT"  # "STUDENT" or "ADMIN"
    student_id: Optional[str] = None  # Roll number or Faculty ID
    department: Optional[str] = "Computer Science & Engineering"
    semester: Optional[str] = "Semester 3"
    phone: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
