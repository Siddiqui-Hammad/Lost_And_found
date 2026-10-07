from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IoTBox(BaseModel):
    box_id: str
    name: str
    location: str
    status: str = "ONLINE"  # ONLINE, OFFLINE, MAINTENANCE
    last_seen: str = Field(default_factory=lambda: datetime.now().isoformat())
    items_registered: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class IoTEvent(BaseModel):
    event_id: str
    box_id: str
    rfid_id: str
    location: str
    timestamp: str
    found_item_id: Optional[str] = None
    status: str = "PROCESSED"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
