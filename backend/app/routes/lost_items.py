from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from ..database import db
from ..models.item import LostItem
from ..schemas.item import LostItemCreate, ItemStatusUpdate
from ..routes.auth import get_current_user
from ..ai.matcher import ai_matcher

router = APIRouter(prefix="/lost-items", tags=["Lost Items"])

@router.get("", response_model=List[dict])
def list_lost_items(category: Optional[str] = None, status: Optional[str] = None):
    items = db.get_lost_items()
    if category:
        items = [i for i in items if i.get("category", "").lower() == category.lower()]
    if status:
        items = [i for i in items if i.get("status", "").upper() == status.upper()]
    return items

@router.get("/{item_id}")
def get_lost_item_detail(item_id: str):
    item = db.get_lost_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Lost item report not found")
    return item

@router.post("", response_model=dict)
def report_lost_item(req: LostItemCreate, current_user: dict = Depends(get_current_user)):
    existing_count = len(db.get_lost_items()) + 1
    item_id = f"LOST-{existing_count:04d}"
    
    new_lost = LostItem(
        item_id=item_id,
        user_id=current_user.get("user_id"),
        user_name=current_user.get("name"),
        user_email=current_user.get("email"),
        student_id=current_user.get("student_id", ""),
        item_name=req.item_name,
        category=req.category,
        brand=req.brand or "",
        color=req.color,
        description=req.description,
        location=req.location,
        lost_at=req.lost_at,
        image_url=req.image_url,
        status="LOST"
    )
    saved = db.add_lost_item(new_lost.model_dump())
    
    # Trigger AI matching against found items
    matches = ai_matcher.run_matching_for_lost_item(saved)
    top_matches = [m.model_dump() for m in matches if m.final_match_score >= 70.0]
    
    return {
        "success": True,
        "message": "Lost item reported successfully and queued in AI matcher.",
        "item": saved,
        "matches_count": len(top_matches),
        "matches": top_matches
    }

@router.patch("/{item_id}/status")
def update_status(item_id: str, req: ItemStatusUpdate, current_user: dict = Depends(get_current_user)):
    updated = db.update_lost_item_status(item_id, req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Lost item report not found")
    return {"success": True, "item": updated}
