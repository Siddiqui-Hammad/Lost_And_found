from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..database import db
from ..routes.auth import require_admin
from ..ai.matcher import ai_matcher

router = APIRouter(prefix="/admin", tags=["Administrator Dashboard"])

@router.get("/dashboard")
def get_admin_dashboard(current_user: dict = Depends(require_admin)):
    lost_items = db.get_lost_items()
    found_items = db.get_found_items()
    claims = db.get_claims()
    matches = ai_matcher.get_all_matches(min_score=70.0)
    
    returned_count = len([l for l in lost_items if l.get("status") in ["RETURNED", "RESOLVED"]])
    total_lost = len(lost_items)
    recovery_rate = round((returned_count / total_lost * 100) if total_lost > 0 else 0.0, 1)
    
    return {
        "metrics": {
            "total_lost": total_lost,
            "total_found": len(found_items),
            "ai_matches": len(matches),
            "pending_claims": len([c for c in claims if c.get("status") == "PENDING"]),
            "returned_items": returned_count,
            "recovery_rate": recovery_rate
        },
        "recent_lost": lost_items[:5],
        "recent_found": found_items[:5],
        "pending_claims": [c for c in claims if c.get("status") == "PENDING"],
        "iot_boxes": db.get_iot_boxes()
    }

@router.post("/items/{item_id}/mark-returned")
def mark_item_returned(item_id: str, current_user: dict = Depends(require_admin)):
    # Check in lost items
    lost = db.get_lost_item(item_id)
    if lost:
        db.update_lost_item_status(item_id, "RETURNED")
        return {"success": True, "message": f"Lost item {item_id} marked as RETURNED."}
        
    found = db.get_found_item(item_id)
    if found:
        db.update_found_item_status(item_id, "RETURNED")
        return {"success": True, "message": f"Found item {item_id} marked as RETURNED."}
        
    raise HTTPException(status_code=404, detail="Item ID not found")

@router.post("/reset-demo-data")
def reset_demo_data(current_user: dict = Depends(require_admin)):
    result = db.reset_database()
    return result
