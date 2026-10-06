from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
from ..database import db
from ..models import Claim

router = APIRouter(prefix="/claims", tags=["Ownership Claims & Verification"])

class CreateClaimRequest(BaseModel):
    lost_item_id: str
    found_item_id: str
    match_id: Optional[str] = None
    student_id: Optional[str] = "2300970100045"
    student_name: Optional[str] = "Rahul Sharma"
    student_email: Optional[str] = "rahul.sharma@aktu.ac.in"
    secret_details: str  # Proof info: unique marks, wallpaper, lock pin, contents

class VerifyClaimRequest(BaseModel):
    status: str  # APPROVED or REJECTED
    admin_notes: Optional[str] = ""

@router.get("", response_model=List[Claim])
def get_all_claims(status: Optional[str] = None):
    claims = db.get_claims()
    if status:
        claims = [c for c in claims if c.status.upper() == status.upper()]
    return claims

@router.post("", response_model=Claim)
def submit_claim(req: CreateClaimRequest):
    lost_item = db.get_lost_item(req.lost_item_id)
    found_item = db.get_found_item(req.found_item_id)
    
    if not lost_item or not found_item:
        raise HTTPException(status_code=404, detail="Lost or Found item not found")

    claim_id = f"CLM-{uuid.uuid4().hex[:5].upper()}"
    claim = Claim(
        id=claim_id,
        lost_item_id=req.lost_item_id,
        found_item_id=req.found_item_id,
        match_id=req.match_id or f"MATCH-{req.lost_item_id}-{req.found_item_id}",
        student_id=req.student_id or lost_item.student_id or "STUDENT",
        student_name=req.student_name or lost_item.user_name,
        student_email=req.student_email or lost_item.user_email,
        item_name=lost_item.item_name,
        secret_details=req.secret_details,
        status="PENDING",
        created_at=datetime.now().isoformat()
    )
    
    saved_claim = db.add_claim(claim)
    db.update_lost_item_status(req.lost_item_id, "CLAIM_PENDING")
    db.update_found_item_status(req.found_item_id, "CLAIM_PENDING")
    
    return saved_claim

@router.put("/{claim_id}/verify")
def verify_claim(claim_id: str, req: VerifyClaimRequest):
    claim = db.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    new_status = req.status.upper()
    if new_status not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Status must be APPROVED or REJECTED")

    db.update_claim(claim_id, new_status, req.admin_notes or "")

    if new_status == "APPROVED":
        db.update_lost_item_status(claim.lost_item_id, "RETURNED")
        db.update_found_item_status(claim.found_item_id, "RETURNED")
    else:
        db.update_lost_item_status(claim.lost_item_id, "LOST")
        db.update_found_item_status(claim.found_item_id, "FOUND")

    return {
        "status": "SUCCESS",
        "claim_id": claim_id,
        "new_status": new_status,
        "message": f"Claim {new_status.lower()} successfully by Proctor/Admin. Item marked as {'RETURNED' if new_status == 'APPROVED' else 'AVAILABLE'}."
    }
