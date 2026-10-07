from pydantic import BaseModel, Field
from typing import Optional
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
    status: str = "LOST"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class FoundItem(BaseModel):
    item_id: str
    rfid_id: Optional[str] = None
    box_id: Optional[str] = None
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    description: str
    location: str
    found_at: str
    image_url: Optional[str] = None
    source: str = "MANUAL"  # "MANUAL" or "IOT"
    reported_by_id: Optional[str] = None
    reported_by_name: Optional[str] = None
    status: str = "FOUND"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
