from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..schemas.iot import IoTScanRequest, IoTScanResponse, IoTBoxCreate
from ..iot.event_handler import iot_event_handler
from ..iot.box_manager import box_manager
from ..database import db

router = APIRouter(prefix="/iot", tags=["IoT Smart Box Integration"])

@router.post("/items", response_model=IoTScanResponse)
def handle_iot_item_scan(req: IoTScanRequest):
    """
    Standardized Hardware & Simulator Endpoint:
    Called whenever an RFID tag is placed inside a Smart Drop Box.
    This API contract is 100% compatible with ESP32 Wi-Fi HTTP client requests.
    """
    try:
        response = iot_event_handler.process_scan(req)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IoT event processing error: {str(e)}")

@router.get("/boxes")
def list_iot_boxes():
    return box_manager.get_all_boxes()

@router.post("/boxes")
def register_iot_box(req: IoTBoxCreate):
    box = box_manager.register_box(req.box_id, req.name, req.location)
    return {"success": True, "box": box}

@router.post("/boxes/{box_id}/heartbeat")
def box_heartbeat(box_id: str):
    success = box_manager.heartbeat(box_id)
    if not success:
        raise HTTPException(status_code=404, detail="Box ID not recognized")
    return {"success": True, "status": "ONLINE"}

@router.get("/events")
def list_iot_events():
    return db.get_iot_events()
