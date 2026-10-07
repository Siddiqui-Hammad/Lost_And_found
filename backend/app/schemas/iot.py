from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IoTScanRequest(BaseModel):
    box_id: str = Field(..., description="Unique hardware box identifier, e.g., BOX-001")
    rfid_id: str = Field(..., description="Scanned RFID UID hex string, e.g., A37B219C")
    location: Optional[str] = "Library"
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    item_name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

class IoTScanResponse(BaseModel):
    success: bool
    item_id: str
    message: str
    match_found: bool = False
    top_match_score: Optional[float] = None

class IoTBoxCreate(BaseModel):
    box_id: str
    name: str
    location: str
    status: Optional[str] = "ONLINE"
