from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from ..database import db
from ..config import settings
from ..models import FoundItem, IoTDepositRequest

router = APIRouter(prefix="/iot", tags=["IoT Smart Collection Boxes"])

@router.get("/boxes")
def get_collection_boxes():
    return list(settings.COLLECTION_BOXES.values())

@router.get("/events")
def get_iot_event_stream():
    return db.get_iot_events()

@router.post("/deposit")
def process_iot_deposit(deposit: IoTDepositRequest):
    box_info = settings.COLLECTION_BOXES.get(deposit.box_id)
    if not box_info:
        # Auto-create or fallback
        box_location = deposit.found_location or "Campus Smart Box"
        box_name = f"Box {deposit.box_id}"
    else:
        box_location = box_info["location"]
        box_name = box_info["name"]

    new_id = f"FND-IOT-{uuid.uuid4().hex[:4].upper()}"
    found_item = FoundItem(
        id=new_id,
        item_name=deposit.item_name,
        category=deposit.category,
        brand=deposit.brand or "",
        color=deposit.color,
        found_location=box_location,
        found_time=datetime.now().strftime("%I:%M %p"),
        description=deposit.description,
        image_url=deposit.image_url or "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400",
        source="IOT_BOX",
        box_id=deposit.box_id,
        rfid_tag=deposit.rfid_tag,
        reported_by_name=f"{box_name} (ESP32 Smart Box)",
        status="FOUND"
    )
    
    saved_item = db.add_found_item(found_item)
    
    # Record event in IoT event stream
    event = {
        "event_id": f"EVT-{uuid.uuid4().hex[:6].upper()}",
        "box_id": deposit.box_id,
        "box_name": box_name,
        "location": box_location,
        "rfid_tag": deposit.rfid_tag,
        "item_id": saved_item.id,
        "item_name": saved_item.item_name,
        "category": saved_item.category,
        "timestamp": datetime.now().isoformat(),
        "oled_message": "ITEM REGISTERED",
        "servo_status": "OPEN -> LOCKED (5s)"
    }
    db.add_iot_event(event)

    # Calculate matches for response feedback
    matches = [m for m in db.get_all_matches(min_score=60.0) if m.found_item.id == saved_item.id]
    best_match = matches[0] if matches else None

    return {
        "status": "SUCCESS",
        "message": f"Item deposited and registered successfully into {box_name}",
        "rfid_tag": deposit.rfid_tag,
        "item": saved_item,
        "best_match_score": best_match.breakdown.final_score if best_match else None,
        "matched_lost_item": best_match.lost_item.item_name if best_match else None,
        "oled_display": {
            "line1": "ITEM REGISTERED",
            "line2": f"ID: {saved_item.id}",
            "line3": f"RFID: {deposit.rfid_tag}",
            "line4": f"Match: {best_match.breakdown.final_score if best_match else 'Searching'}%"
        }
    }
