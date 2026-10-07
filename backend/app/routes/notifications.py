from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import db
from ..routes.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["In-App Notifications"])

@router.get("", response_model=List[dict])
def get_my_notifications(current_user: dict = Depends(get_current_user)):
    user_email = current_user.get("email", "")
    notifs = db.get_user_notifications(user_email)
    return sorted(notifs, key=lambda x: x.get("created_at", ""), reverse=True)

@router.patch("/{notification_id}/read")
def mark_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    db.mark_notification_read(notification_id)
    return {"success": True}
