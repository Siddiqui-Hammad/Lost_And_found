from pydantic import BaseModel
from typing import Optional

class LostItemCreate(BaseModel):
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    description: str
    location: str
    lost_at: str
    image_url: Optional[str] = None

class FoundItemCreate(BaseModel):
    item_name: str
    category: str
    brand: Optional[str] = ""
    color: str
    description: str
    location: str
    found_at: str
    image_url: Optional[str] = None

class ItemStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
