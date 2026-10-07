from pydantic import BaseModel
from typing import Optional

class ClaimCreate(BaseModel):
    lost_item_id: str
    found_item_id: str
    answers: str  # Secret verification questions answer

class ClaimReview(BaseModel):
    status: str  # "APPROVED" or "REJECTED"
    admin_notes: Optional[str] = None
