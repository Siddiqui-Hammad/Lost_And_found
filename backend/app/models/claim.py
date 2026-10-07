from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Claim(BaseModel):
    claim_id: str
    user_id: str
    student_name: str
    student_email: str
    student_id: Optional[str] = ""
    lost_item_id: str
    found_item_id: str
    item_name: str
    answers: str  # Secret verification details (e.g. inside contents, unique scratch)
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    admin_notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    reviewed_at: Optional[str] = None
