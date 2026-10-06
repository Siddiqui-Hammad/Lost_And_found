from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
from ..database import db
from ..models import LostItem

router = APIRouter(prefix="/lost-items", tags=["Lost Items"])

class CreateLostItemRequest(BaseModel):
    user_id: Optional[str] = "USR-101"
    user_name: Optional[str] = "Rahul Sharma"
    user_email: Optional[str] = "rahul.sharma@aktu.ac.in"
    student_id: Optional[str] = "2300970100045"
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    last_seen_location: str
    lost_time: Optional[str] = "Recently"
    description: str
    image_url: Optional[str] = None

@router.get("", response_model=List[LostItem])
def get_all_lost_items(category: Optional[str] = None, status: Optional[str] = None):
    items = db.get_lost_items()
    if category:
        items = [i for i in items if i.category.lower() == category.lower()]
    if status:
        items = [i for i in items if i.status.lower() == status.lower()]
    return items

@router.get("/{item_id}", response_model=LostItem)
def get_lost_item_by_id(item_id: str):
    item = db.get_lost_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Lost item not found")
    return item

@router.post("", response_model=LostItem)
def create_lost_item(req: CreateLostItemRequest):
    new_id = f"LOST-{uuid.uuid4().hex[:4].upper()}"
    item = LostItem(
        id=new_id,
        user_id=req.user_id or "USR-101",
        user_name=req.user_name or "Student",
        user_email=req.user_email or "student@aktu.ac.in",
        student_id=req.student_id or "",
        item_name=req.item_name,
        category=req.category,
        brand=req.brand or "",
        color=req.color,
        last_seen_location=req.last_seen_location,
        lost_time=req.lost_time or "Just now",
        description=req.description,
        image_url=req.image_url or "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
        status="LOST"
    )
    return db.add_lost_item(item)
