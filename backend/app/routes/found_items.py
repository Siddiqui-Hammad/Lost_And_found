from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
import uuid
from ..database import db
from ..models.item import FoundItem
from ..schemas.item import FoundItemCreate, ItemStatusUpdate
from ..routes.auth import get_current_user
from ..ai.matcher import ai_matcher
from ..ai.vision_extractor import vision_extractor

router = APIRouter(prefix="/found-items", tags=["Found Items"])

@router.post("/ai-analyze-photo")
async def analyze_found_photo(
    file: UploadFile = File(...),
    note: Optional[str] = Form(""),
    location: Optional[str] = Form("")
):
    """
    Multimodal AI Vision Endpoint:
    Analyzes an uploaded image of a found item + optional note
    Extracts item_name, category, brand, color, condition, and generates an AI description.
    """
    image_bytes = await file.read()
    analysis = vision_extractor.analyze_image(
        image_bytes=image_bytes,
        user_note=note or "",
        location_hint=location or ""
    )
    return {
        "success": True,
        "extracted_data": analysis,
        "filename": file.filename
    }

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
        image_base64=req.image_base64,
        source="STUDENT",
        reported_by_id=current_user.get("user_id") if current_user else "ANONYMOUS",
        reported_by_name=current_user.get("name") if current_user else "Good Samaritan",
        ai_analyzed=False,
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

@router.post("/{item_id}/ai-verify")
def run_ai_analysis_on_found_item(item_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    """
    Runs multimodal AI analysis and updates specifications profile for an existing found item.
    Immediately recalculates cross-matching against active student lost reports.
    """
    item = db.get_found_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Found item not found")

    import base64
    import os
    img_bytes = b""
    if item.get("image_base64"):
        try:
            img_bytes = base64.b64decode(item["image_base64"])
        except Exception:
            img_bytes = b""

    if not img_bytes and item.get("image_url"):
        img_url = item["image_url"].lstrip("/")
        for p in [img_url, os.path.join("backend", "app", img_url)]:
            if os.path.exists(p) and os.path.isfile(p):
                try:
                    with open(p, "rb") as f_img:
                        img_bytes = f_img.read()
                    break
                except Exception:
                    pass

    analysis = vision_extractor.analyze_image(
        image_bytes=img_bytes,
        user_note=item.get("description", ""),
        location_hint=item.get("location", "")
    )

    update_payload = {
        "item_name": analysis.get("item_name", item.get("item_name")),
        "category": analysis.get("category", item.get("category")),
        "brand": analysis.get("brand", item.get("brand")),
        "color": analysis.get("color", item.get("color")),
        "description": f"{analysis.get('ai_description', '')} (Verified: {analysis.get('condition', 'Good condition')})",
        "ai_analyzed": True,
        "detailed_specs": analysis.get("detailed_specs")
    }
    updated = db.update_found_item(item_id, update_payload)
    matches = ai_matcher.run_matching_for_found_item(updated or item)
    top_matches = [m.model_dump() for m in matches if m.final_match_score >= 65.0]

    return {
        "success": True,
        "item": updated,
        "analysis": analysis,
        "matches_count": len(top_matches),
        "matches": top_matches
    }
