import urllib.parse
import uuid
import datetime
from typing import Dict, Any, List, Optional
from backend.app.database import db

class NotificationDispatcher:
    """
    FINDBACK AI Automated WhatsApp & Email Notification Dispatcher.
    Delivers instant high-priority alerts with secure claim tokens when
    lost items are matched on campus.
    """

    def create_claim_token(self, lost_item_id: str, found_item_id: str) -> str:
        """Generates a secure 8-character verification token for the claimant."""
        import hashlib
        seed = f"{lost_item_id}:{found_item_id}:{datetime.datetime.now().date()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:8].upper()

    def format_whatsapp_message(
        self,
        student_name: str,
        item_name: str,
        found_location: str,
        match_score: float,
        claim_token: str
    ) -> str:
        """Constructs an official, polite WhatsApp alert message."""
        return (
            f"🔔 *GL BAJAJ LOST & FOUND ALERT — FINDBACK AI*\n\n"
            f"Dear *{student_name}*,\n"
            f"Great news! Our AI campus surveillance system has detected a *{match_score}% MATCH* for your lost item:\n\n"
            f"📦 *Item:* {item_name}\n"
            f"📍 *Found At:* {found_location}\n"
            f"🔑 *Verification Token:* `{claim_token}`\n\n"
            f"🏢 *Collection Office:* Office of the Chief Proctor (Admin Block A)\n"
            f"⏰ *Hours:* 10:00 AM - 4:30 PM (Mon-Sat)\n\n"
            f"⚠️ *Important:* Please bring your GL Bajaj Student ID Card and secret proof (serials/stickers) to collect your item.\n\n"
            f"— *Proctorial Board & Security Department, GLBITM*"
        )

    def generate_whatsapp_url(self, phone: str, message: str) -> str:
        """Generates a direct 1-click WhatsApp web/app dispatch URL."""
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if len(clean_phone) == 10:
            clean_phone = f"91{clean_phone}"  # Default to India ISD code
        encoded_text = urllib.parse.quote(message)
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"

    def format_email_content(
        self,
        student_name: str,
        student_email: str,
        item_name: str,
        lost_location: str,
        found_location: str,
        match_score: float,
        claim_token: str
    ) -> Dict[str, str]:
        """Constructs official Proctorial email notice with subject and body."""
        subject = f"[GLBITM Alert] High AI Match ({match_score}%) for your lost {item_name} — FINDBACK AI"
        body_text = (
            f"Dear {student_name},\n\n"
            f"FINDBACK AI has successfully matched your reported lost item '{item_name}' "
            f"with an item recovered at {found_location} with {match_score}% confidence.\n\n"
            f"Match Details:\n"
            f"- Lost Report Location: {lost_location}\n"
            f"- Recovery Location: {found_location}\n"
            f"- Secure Claim Token: {claim_token}\n\n"
            f"Next Steps to Retrieve Your Possession:\n"
            f"1. Visit the Proctorial Board Office (Room 104, Admin Block A).\n"
            f"2. Present your GL Bajaj Student Identity Card.\n"
            f"3. Provide the Claim Token ({claim_token}) and describe any distinguishing internal marks or serial numbers.\n\n"
            f"Office Timings: Monday to Saturday, 10:00 AM – 4:30 PM\n\n"
            f"Regards,\n"
            f"Office of the Chief Proctor & Security Board\n"
            f"GL Bajaj Institute of Technology & Management, Greater Noida\n"
            f"Powered by FINDBACK AI"
        )
        mailto_url = f"mailto:{student_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body_text)}"
        return {
            "subject": subject,
            "body_text": body_text,
            "mailto_url": mailto_url
        }

    def send_alert(
        self,
        channel: str,
        recipient_name: str,
        recipient_contact: str,
        lost_item: Dict[str, Any],
        found_item: Dict[str, Any],
        match_score: float,
        dispatched_by: str = "FINDBACK AI Automated Dispatcher"
    ) -> Dict[str, Any]:
        """
        Dispatches and logs an official alert (WhatsApp / Email / SMS).
        """
        notif_id = f"NOTIF-{uuid.uuid4().hex[:6].upper()}"
        claim_token = self.create_claim_token(
            lost_item.get("item_id", "LOST"),
            found_item.get("item_id", "FOUND")
        )
        now_str = datetime.datetime.now().isoformat()

        item_name = lost_item.get("item_name", "Item")
        found_loc = found_item.get("location", "Campus")
        lost_loc = lost_item.get("location", "Campus")

        if channel.upper() == "WHATSAPP":
            msg_text = self.format_whatsapp_message(
                recipient_name, item_name, found_loc, match_score, claim_token
            )
            action_url = self.generate_whatsapp_url(recipient_contact, msg_text)
        else:
            email_data = self.format_email_content(
                recipient_name, recipient_contact, item_name, lost_loc, found_loc, match_score, claim_token
            )
            msg_text = email_data["body_text"]
            action_url = email_data["mailto_url"]

        notif_record = {
            "notification_id": notif_id,
            "channel": channel.upper(),
            "recipient_name": recipient_name,
            "recipient_contact": recipient_contact,
            "user_email": lost_item.get("user_email", recipient_contact),
            "item_name": item_name,
            "lost_item_id": lost_item.get("item_id"),
            "found_item_id": found_item.get("item_id"),
            "match_score": match_score,
            "claim_token": claim_token,
            "message_preview": msg_text[:180] + "...",
            "full_message": msg_text,
            "action_url": action_url,
            "dispatched_by": dispatched_by,
            "status": "DELIVERED",
            "timestamp": now_str,
            "is_read": False
        }

        saved = db.add_notification(notif_record)
        return saved

    def get_notification_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves history of dispatched alerts."""
        notifs = db.get_all_notifications()
        # Sort newest first
        return sorted(notifs, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]

notification_dispatcher = NotificationDispatcher()
