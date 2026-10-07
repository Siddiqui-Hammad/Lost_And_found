from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..ai.matcher import ai_matcher
from ..database import db
from ..routes.auth import get_current_user

router = APIRouter(prefix="/matches", tags=["AI Semantic Matching"])

@router.get("")
def get_all_matches(min_score: float = 50.0, category: Optional[str] = None):
    matches = ai_matcher.get_all_matches(min_score=min_score)
    result = [m.model_dump() for m in matches]
    if category:
        result = [r for r in result if r["lost_item"]["category"].lower() == category.lower()]
    return result

@router.get("/my-matches")
def get_my_matches(min_score: float = 50.0, current_user: dict = Depends(get_current_user)):
    matches = ai_matcher.get_all_matches(min_score=min_score)
    user_email = current_user.get("email", "").lower()
    my_matches = [
        m.model_dump() for m in matches 
        if m.lost_item.user_email.lower() == user_email or m.lost_item.user_id == current_user.get("user_id")
    ]
    return my_matches

@router.get("/compare/{lost_id}/{found_id}")
def compare_specific_items(lost_id: str, found_id: str):
    lost = db.get_lost_item(lost_id)
    found = db.get_found_item(found_id)
    if not lost or not found:
        raise HTTPException(status_code=404, detail="One or both item records not found")
    record = ai_matcher.evaluate_pair(lost, found)
    return record.model_dump()
