import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database import db
from ..models.iot import IoTBox

class IoTBoxManager:
    """Manages Smart Collection Box Hardware fleet registry & telemetry"""
    
    def get_all_boxes(self) -> List[IoTBox]:
        boxes = db.get_iot_boxes()
        return [IoTBox(**b) for b in boxes]

    def get_box(self, box_id: str) -> Optional[IoTBox]:
        data = db.get_iot_box(box_id)
        return IoTBox(**data) if data else None

    def register_box(self, box_id: str, name: str, location: str) -> IoTBox:
        existing = self.get_box(box_id)
        if existing:
            return existing
        new_box = IoTBox(
            box_id=box_id,
            name=name,
            location=location,
            status="ONLINE",
            last_seen=datetime.now().isoformat(),
            items_registered=0
        )
        db.add_iot_box(new_box.model_dump())
        return new_box

    def heartbeat(self, box_id: str) -> bool:
        box = self.get_box(box_id)
        if not box:
            return False
        # Update last seen
        db.mongo_db.iot_boxes.update_one({"box_id": box_id}, {"$set": {"last_seen": datetime.now().isoformat(), "status": "ONLINE"}}) if db.is_connected else None
        if box_id in db.collections["iot_boxes"]:
            db.collections["iot_boxes"][box_id]["last_seen"] = datetime.now().isoformat()
            db.collections["iot_boxes"][box_id]["status"] = "ONLINE"
            db.save_local_store()
        return True

box_manager = IoTBoxManager()
