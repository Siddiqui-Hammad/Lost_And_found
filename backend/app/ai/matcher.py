import uuid
from typing import List, Dict, Any, Optional
from ..database import db
from ..models.match import MatchRecord
from ..models.item import LostItem, FoundItem
from ..models.notification import Notification
from .scoring import compute_composite_match

class AIMatcherService:
    """
    TRACE AI Cross-Matching Service.
    Automatically executes when new items are reported or IoT events arrive.
    """
    def evaluate_pair(self, lost_item: dict, found_item: dict) -> MatchRecord:
        breakdown = compute_composite_match(lost_item, found_item)
        match_id = f"MATCH-{lost_item['item_id']}-{found_item['item_id']}"
        
        return MatchRecord(
            match_id=match_id,
            lost_item_id=lost_item["item_id"],
            found_item_id=found_item["item_id"],
            text_score=breakdown.text_score,
            category_score=breakdown.category_score,
            color_score=breakdown.color_score,
            brand_score=breakdown.brand_score,
            location_score=breakdown.location_score,
            time_score=breakdown.time_score,
            image_score=breakdown.image_score,
            final_match_score=breakdown.final_score,
            match_level=breakdown.match_level,
            lost_item=LostItem(**lost_item),
            found_item=FoundItem(**found_item)
        )

    def run_matching_for_found_item(self, found_item: dict) -> List[MatchRecord]:
        """Triggered automatically when a new found item is reported or scanned via IoT"""
        lost_items = db.get_lost_items()
        matches: List[MatchRecord] = []
        
        for lost in lost_items:
            if lost.get("status") in ["RETURNED", "RESOLVED"]:
                continue
            record = self.evaluate_pair(lost, found_item)
            if record.final_match_score >= 50.0:
                matches.append(record)
                # Create in-app notification if match is notable (>=70%)
                if record.final_match_score >= 70.0 and lost.get("user_email"):
                    notif = Notification(
                        notification_id=f"NOTIF-{uuid.uuid4().hex[:6].upper()}",
                        user_id=lost.get("user_id", ""),
                        user_email=lost.get("user_email", ""),
                        title="🎯 Possible Match Found!",
                        message=f"A found item '{found_item.get('item_name')}' deposited at {found_item.get('location')} matches your lost report with {record.final_match_score}% confidence.",
                        item_id=lost.get("item_id"),
                        match_id=record.match_id,
                        match_score=record.final_match_score,
                        location=found_item.get("location"),
                        link=f"/matches?match_id={record.match_id}"
                    )
                    db.add_notification(notif.model_dump())
                    
        # Cache matches
        if matches:
            db.save_matches([m.model_dump() for m in matches])
        return matches

    def run_matching_for_lost_item(self, lost_item: dict) -> List[MatchRecord]:
        """Triggered when a student reports a new lost item"""
        found_items = db.get_found_items()
        matches: List[MatchRecord] = []
        
        for found in found_items:
            if found.get("status") in ["RETURNED", "RESOLVED"]:
                continue
            record = self.evaluate_pair(lost_item, found)
            if record.final_match_score >= 50.0:
                matches.append(record)
                if record.final_match_score >= 70.0 and lost_item.get("user_email"):
                    notif = Notification(
                        notification_id=f"NOTIF-{uuid.uuid4().hex[:6].upper()}",
                        user_id=lost_item.get("user_id", ""),
                        user_email=lost_item.get("user_email", ""),
                        title="🎯 Immediate Match Detected!",
                        message=f"An existing found item '{found.get('item_name')}' at {found.get('location')} matches your lost report with {record.final_match_score}% confidence.",
                        item_id=lost_item.get("item_id"),
                        match_id=record.match_id,
                        match_score=record.final_match_score,
                        location=found.get("location"),
                        link=f"/matches?match_id={record.match_id}"
                    )
                    db.add_notification(notif.model_dump())

        if matches:
            db.save_matches([m.model_dump() for m in matches])
        return matches

    def get_all_matches(self, min_score: float = 50.0) -> List[MatchRecord]:
        lost_items = db.get_lost_items()
        found_items = db.get_found_items()
        all_matches: List[MatchRecord] = []
        
        for l in lost_items:
            for f in found_items:
                record = self.evaluate_pair(l, f)
                if record.final_match_score >= min_score:
                    all_matches.append(record)
                    
        all_matches.sort(key=lambda x: x.final_match_score, reverse=True)
        return all_matches

ai_matcher = AIMatcherService()
