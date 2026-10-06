from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
from ..database import db
from ..models import FoundItem

router = APIRouter(prefix="/found-items", tags=["Found Items"])

class CreateFoundItemRequest(BaseModel):
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    found_location: str
    found_time: Optional[str] = "Recently"
    description: str
    image_url: Optional[str] = None
    source: Optional[str] = "MANUAL"
    reported_by_name: Optional[str] = "Good Samaritan"

@router.get("", response_model=List[FoundItem])
def get_all_found_items(category: Optional[str] = None, source: Optional[str] = None):
    items = db.get_found_items()
    if category:
        items = [i for i in items if i.category.lower() == category.lower()]
    if source:
        items = [i for i in items if i.source.lower() == source.lower()]
    return items

@router.get("/{item_id}", response_model=FoundItem)
def get_found_item_by_id(item_id: str):
    item = db.get_found_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Found item not found")
    return item

@router.post("", response_model=FoundItem)
def create_found_item(req: CreateFoundItemRequest):
    new_id = f"FND-{uuid.uuid4().hex[:4].upper()}"
    item = FoundItem(
        id=new_id,
        item_name=req.item_name,
        category=req.category,
        brand=req.brand or "",
        color=req.color,
        found_location=req.found_location,
        found_time=req.found_time or "Just now",
        description=req.description,
        image_url=req.image_url or "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
        source=req.source or "MANUAL",
        reported_by_name=req.reported_by_name or "Student / Staff",
        status="FOUND"
    )
    return db.add_found_item(item)
