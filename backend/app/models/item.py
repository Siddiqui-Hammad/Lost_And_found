from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Valid statuses: LOST, FOUND, MATCHED, CLAIM_PENDING, VERIFIED, RETURNED, REJECTED, RESOLVED

class LostItem(BaseModel):
    item_id: str
    user_id: str
    user_name: str
    user_email: str
    student_id: Optional[str] = ""
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    description: str
    location: str
    lost_at: str
    image_url: Optional[str] = None
    detailed_specs: Optional[Dict[str, Any]] = None
    status: str = "LOST"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class FoundItem(BaseModel):
    item_id: str
    rfid_id: Optional[str] = None
    box_id: Optional[str] = None
    item_name: str = "Found Item (Pending AI Inspection)"
    category: str = "Other"
    brand: Optional[str] = ""
    color: str = "Unspecified"
    description: str
    location: str
    found_at: str
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    source: str = "STUDENT"  # "STUDENT", "ADMIN", etc.
    reported_by_id: Optional[str] = None
    reported_by_name: Optional[str] = None
    ai_analyzed: bool = False
    detailed_specs: Optional[Dict[str, Any]] = None
    status: str = "FOUND"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
