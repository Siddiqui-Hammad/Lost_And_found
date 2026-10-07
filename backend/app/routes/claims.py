from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import uuid
from datetime import datetime
from ..database import db
from ..models.claim import Claim
from ..schemas.claim import ClaimCreate, ClaimReview
from ..routes.auth import get_current_user, require_admin

router = APIRouter(prefix="/claims", tags=["Ownership Claims"])

@router.get("", response_model=List[dict])
def list_claims(status: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    all_claims = db.get_claims()
    if current_user.get("role") != "ADMIN":
        # Students see only their claims
        user_email = current_user.get("email", "").lower()
        user_id = current_user.get("user_id")
        all_claims = [c for c in all_claims if c.get("student_email", "").lower() == user_email or c.get("user_id") == user_id]
    
    if status:
        all_claims = [c for c in all_claims if c.get("status", "").upper() == status.upper()]
    return all_claims

@router.post("", response_model=dict)
def submit_claim(req: ClaimCreate, current_user: dict = Depends(get_current_user)):
    lost = db.get_lost_item(req.lost_item_id)
    found = db.get_found_item(req.found_item_id)
    if not lost or not found:
        raise HTTPException(status_code=404, detail="Invalid lost or found item reference")
        
    claim_id = f"CLM-{uuid.uuid4().hex[:6].upper()}"
    new_claim = Claim(
        claim_id=claim_id,
        user_id=current_user.get("user_id"),
        student_name=current_user.get("name"),
        student_email=current_user.get("email"),
        student_id=current_user.get("student_id", ""),
        lost_item_id=req.lost_item_id,
        found_item_id=req.found_item_id,
        item_name=lost.get("item_name", "Unknown Item"),
        answers=req.answers,
        status="PENDING"
    )
    saved = db.add_claim(new_claim.model_dump())
    
    # Update item statuses to indicate claim is pending
    db.update_lost_item_status(req.lost_item_id, "CLAIM_PENDING")
    db.update_found_item_status(req.found_item_id, "CLAIM_PENDING")
    
    return {
        "success": True,
        "message": "Claim submitted to Campus Proctorial Board for verification.",
        "claim": saved
    }

@router.post("/{claim_id}/review")
def review_claim(claim_id: str, req: ClaimReview, current_user: dict = Depends(require_admin)):
    claim = db.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    updated = db.update_claim_status(claim_id, req.status, req.admin_notes)
    
    if req.status == "APPROVED":
        # Verification passed -> mark items verified/returned
        db.update_lost_item_status(claim["lost_item_id"], "VERIFIED")
        db.update_found_item_status(claim["found_item_id"], "VERIFIED")
    elif req.status == "REJECTED":
        db.update_lost_item_status(claim["lost_item_id"], "LOST")
        db.update_found_item_status(claim["found_item_id"], "FOUND")
        
    return {"success": True, "claim": updated}
