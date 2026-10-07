from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from .item import LostItem, FoundItem

class MatchBreakdown(BaseModel):
    text_score: float
    category_score: float
    color_score: float
    brand_score: float
    location_score: float
    time_score: float
    image_score: Optional[float] = None
    final_score: float
    match_level: str  # "HIGH PROBABILITY", "POSSIBLE MATCH", "LOW PROBABILITY"

class MatchRecord(BaseModel):
    match_id: str
    lost_item_id: str
    found_item_id: str
    text_score: float
    category_score: float
    color_score: float
    brand_score: float
    location_score: float
    time_score: float
    image_score: Optional[float] = None
    final_match_score: float
    match_level: str
    lost_item: Optional[LostItem] = None
    found_item: Optional[FoundItem] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
