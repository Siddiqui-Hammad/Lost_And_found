from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from ..database import db
from ..models.item import FoundItem
from ..schemas.item import FoundItemCreate, ItemStatusUpdate
from ..routes.auth import get_current_user
from ..ai.matcher import ai_matcher

router = APIRouter(prefix="/found-items", tags=["Found Items"])

@router.get("", response_model=List[dict])
def list_found_items(category: Optional[str] = None, status: Optional[str] = None, source: Optional[str] = None):
    items = db.get_found_items()
    if category:
        items = [i for i in items if i.get("category", "").lower() == category.lower()]
    if status:
        items = [i for i in items if i.get("status", "").upper() == status.upper()]
    if source:
        items = [i for i in items if i.get("source", "").upper() == source.upper()]
    return items

@router.get("/{item_id}")
def get_found_item_detail(item_id: str):
    item = db.get_found_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Found item not found")
    return item

@router.post("", response_model=dict)
def report_found_item(req: FoundItemCreate, current_user: Optional[dict] = Depends(get_current_user)):
    existing_count = len(db.get_found_items()) + 1
    item_id = f"FOUND-{existing_count:04d}"
    
    new_found = FoundItem(
        item_id=item_id,
        item_name=req.item_name,
        category=req.category,
        brand=req.brand or "",
        color=req.color,
        description=req.description,
        location=req.location,
        found_at=req.found_at,
        image_url=req.image_url,
        source="MANUAL",
        reported_by_id=current_user.get("user_id") if current_user else "ANONYMOUS",
        reported_by_name=current_user.get("name") if current_user else "Good Samaritan",
        status="FOUND"
    )
    saved = db.add_found_item(new_found.model_dump())
    
    # Trigger AI matching
    matches = ai_matcher.run_matching_for_found_item(saved)
    top_matches = [m.model_dump() for m in matches if m.final_match_score >= 70.0]
    
    return {
        "success": True,
        "item_id": item_id,
        "message": "Found item registered successfully.",
        "item": saved,
        "matches_count": len(top_matches),
        "matches": top_matches
    }

@router.patch("/{item_id}/status")
def update_found_status(item_id: str, req: ItemStatusUpdate, current_user: dict = Depends(get_current_user)):
    updated = db.update_found_item_status(item_id, req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Found item not found")
    return {"success": True, "item": updated}
