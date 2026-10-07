from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Notification(BaseModel):
    notification_id: str
    user_id: str
    user_email: str
    title: str
    message: str
    item_id: Optional[str] = None
    match_id: Optional[str] = None
    match_score: Optional[float] = None
    location: Optional[str] = None
    link: Optional[str] = None
    is_read: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
