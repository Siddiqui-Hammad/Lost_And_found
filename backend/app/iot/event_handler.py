import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from ..database import db
from ..models.item import FoundItem
from ..models.iot import IoTEvent
from ..schemas.iot import IoTScanRequest, IoTScanResponse
from ..ai.matcher import ai_matcher
from .box_manager import box_manager

class IoTEventHandler:
    """
    Core Hardware Event Processor.
    Serves both Simulated Hardware and Future Physical ESP32 Systems identically.
    """
    
    def process_scan(self, req: IoTScanRequest) -> IoTScanResponse:
        # 1. Validate / Auto-register Box
        box = box_manager.get_box(req.box_id)
        location = req.location or (box.location if box else "Campus Collection Box")
        if not box:
            box = box_manager.register_box(req.box_id, f"Smart Drop Box {req.box_id}", location)

        # 2. Derive/Assign Item Metadata
        # Tag dictionary for known demo RFID tags if item details not explicitly supplied
        tag_lookup = {
            "RFID-1024": {"name": "Black Leather Wallet", "cat": "Wallet", "color": "Black", "brand": "Wildhorn", "desc": "Black leather wallet containing college identity card."},
            "A37B219C": {"name": "Black Leather Wallet", "cat": "Wallet", "color": "Black", "brand": "Wildhorn", "desc": "Black leather wallet with student ID inside."},
            "RFID-E204A1": {"name": "Boat Wireless Earbuds", "cat": "Electronics", "color": "White", "brand": "Boat", "desc": "White wireless earbuds inside black silicone case."},
            "RFID-KEY-88": {"name": "Bike Keys with Keychain", "cat": "Keys", "color": "Silver", "brand": "Royal Enfield", "desc": "Set of 3 motorcycle keys with leather strap."},
            "RFID-CALC-09": {"name": "Casio Scientific Calculator", "cat": "Electronics", "color": "Black", "brand": "Casio", "desc": "Casio FX-991EX ClassWiz calculator."}
        }
        
        default_meta = tag_lookup.get(req.rfid_id, {
            "name": f"Item with Tag #{req.rfid_id}",
            "cat": "Other",
            "color": "Standard",
            "brand": "Generic",
            "desc": f"Deposited item scanned via RFID tag {req.rfid_id} in {req.box_id}."
        })

        item_name = req.item_name or default_meta["name"]
        category = req.category or default_meta["cat"]
        brand = req.brand or default_meta.get("brand", "")
        color = req.color or default_meta.get("color", "Unknown")
        description = req.description or default_meta["desc"]
        
        # 3. Generate sequential/unique Found Item ID
        existing_count = len(db.get_found_items()) + 1
        item_id = f"FOUND-{existing_count:04d}"

        # 4. Create FoundItem in database
        timestamp = req.timestamp or datetime.now().isoformat()
        found_item = FoundItem(
            item_id=item_id,
            rfid_id=req.rfid_id,
            box_id=req.box_id,
            item_name=item_name,
            category=category,
            brand=brand,
            color=color,
            description=description,
            location=location,
            found_at=timestamp,
            source="IOT",
            reported_by_name=f"Smart Box {req.box_id}",
            status="FOUND"
        )
        saved_found = db.add_found_item(found_item.model_dump())

        # 5. Record IoT Event & update Box counters
        event = IoTEvent(
            event_id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
            box_id=req.box_id,
            rfid_id=req.rfid_id,
            location=location,
            timestamp=timestamp,
            found_item_id=item_id,
            status="PROCESSED"
        )
        db.record_iot_event(event.model_dump())

        # 6. Trigger AI Semantic Matching
        matches = ai_matcher.run_matching_for_found_item(saved_found)
        top_score = matches[0].final_match_score if matches else None
        match_found = (top_score is not None and top_score >= 70.0)

        # 7. Return standard response
        return IoTScanResponse(
            success=True,
            item_id=item_id,
            message="Item registered successfully via Smart Box.",
            match_found=match_found,
            top_match_score=top_score
        )

iot_event_handler = IoTEventHandler()
