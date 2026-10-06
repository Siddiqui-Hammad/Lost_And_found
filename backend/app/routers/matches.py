from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..database import db
from ..models import MatchItem, LostItem, FoundItem, MatchScoreBreakdown
from ..ai_matcher import compute_match_score

router = APIRouter(prefix="/matches", tags=["AI Matching Engine"])

class LiveCompareRequest(BaseModel):
    lost_name: str
    lost_category: str
    lost_brand: Optional[str] = ""
    lost_color: str
    lost_location: str
    lost_time: str
    lost_description: str
    
    found_name: str
    found_category: str
    found_brand: Optional[str] = ""
    found_color: str
    found_location: str
    found_time: str
    found_description: str

@router.get("", response_model=List[MatchItem])
def get_all_matches(min_score: float = 50.0, tier: Optional[str] = None):
    matches = db.get_all_matches(min_score=min_score)
    if tier:
        matches = [m for m in matches if m.breakdown.tier.upper() == tier.upper()]
    return matches

@router.get("/lost/{lost_id}", response_model=List[MatchItem])
def get_matches_for_lost_item(lost_id: str, min_score: float = 40.0):
    all_matches = db.get_all_matches(min_score=min_score)
    return [m for m in all_matches if m.lost_item.id == lost_id]

@router.get("/found/{found_id}", response_model=List[MatchItem])
def get_matches_for_found_item(found_id: str, min_score: float = 40.0):
    all_matches = db.get_all_matches(min_score=min_score)
    return [m for m in all_matches if m.found_item.id == found_id]

@router.post("/compare", response_model=MatchScoreBreakdown)
def live_compare(req: LiveCompareRequest):
    temp_lost = LostItem(
        id="TEMP-LOST",
        user_id="USR-TEMP",
        user_name="Demo User",
        user_email="demo@aktu.ac.in",
        item_name=req.lost_name,
        category=req.lost_category,
        brand=req.lost_brand or "",
        color=req.lost_color,
        last_seen_location=req.lost_location,
        lost_time=req.lost_time,
        description=req.lost_description,
        status="LOST"
    )
    temp_found = FoundItem(
        id="TEMP-FOUND",
        item_name=req.found_name,
        category=req.found_category,
        brand=req.found_brand or "",
        color=req.found_color,
        found_location=req.found_location,
        found_time=req.found_time,
        description=req.found_description,
        status="FOUND"
    )
    return compute_match_score(temp_lost, temp_found)
