from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class User(BaseModel):
    id: str
    name: str
    email: str
    role: str = "student"  # student or admin
    student_id: Optional[str] = None
    phone: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class LostItem(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_email: str
    student_id: Optional[str] = ""
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    last_seen_location: str
    lost_time: str
    description: str
    image_url: Optional[str] = None
    status: str = "LOST"  # LOST, MATCH_FOUND, CLAIMED, RETURNED
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class FoundItem(BaseModel):
    id: str
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    found_location: str
    found_time: str
    description: str
    image_url: Optional[str] = None
    source: str = "MANUAL"  # MANUAL or IOT_BOX
    box_id: Optional[str] = None
    rfid_tag: Optional[str] = None
    reported_by_id: Optional[str] = None
    reported_by_name: Optional[str] = None
    status: str = "FOUND"  # FOUND, CLAIM_PENDING, RETURNED
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class MatchScoreBreakdown(BaseModel):
    text_score: float
    category_score: float
    color_score: float
    brand_score: float
    location_score: float
    time_score: float
    final_score: float
    tier: str  # HIGH, POSSIBLE, LOW

class MatchItem(BaseModel):
    id: str
    lost_item: LostItem
    found_item: FoundItem
    breakdown: MatchScoreBreakdown
    status: str = "PENDING"  # PENDING, CLAIM_SUBMITTED, VERIFIED, RETURNED
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Claim(BaseModel):
    id: str
    lost_item_id: str
    found_item_id: str
    match_id: Optional[str] = None
    student_id: str
    student_name: str
    student_email: str
    item_name: str
    secret_details: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    admin_notes: Optional[str] = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None

class IoTDepositRequest(BaseModel):
    box_id: str
    rfid_tag: str
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    description: str
    found_location: Optional[str] = None
    image_url: Optional[str] = None
