import json
import os
import uuid
from typing import List, Dict, Any, Optional
from .config import settings
from .models import User, LostItem, FoundItem, Claim, MatchItem
from .ai_matcher import compute_match_score

DB_FILE = os.path.join(settings.DATA_DIR, "db.json")

class Database:
    def __init__(self):
        self.data: Dict[str, Any] = {
            "users": {},
            "lost_items": {},
            "found_items": {},
            "claims": {},
            "iot_events": []
        }
        self.load()

    def load(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"[DB] Error loading db.json: {e}")
                self.seed_defaults()
        else:
            self.seed_defaults()

    def save(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def seed_defaults(self):
        from .seed_data import DEFAULT_USERS, DEFAULT_LOST, DEFAULT_FOUND
        self.data["users"] = {u["id"]: u for u in DEFAULT_USERS}
        self.data["lost_items"] = {l["id"]: l for l in DEFAULT_LOST}
        self.data["found_items"] = {f["id"]: f for f in DEFAULT_FOUND}
        self.data["claims"] = {}
        self.data["iot_events"] = []
        self.save()
        print("[DB] Initialized database with default seed data.")

    # Users
    def get_users(self) -> List[dict]:
        return list(self.data["users"].values())

    def get_user(self, user_id: str) -> Optional[dict]:
        return self.data["users"].get(user_id)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        for u in self.data["users"].values():
            if u.get("email", "").lower() == email.lower():
                return u
        return None

    def add_user(self, user: User) -> dict:
        self.data["users"][user.id] = user.model_dump()
        self.save()
        return self.data["users"][user.id]

    # Lost Items
    def get_lost_items(self) -> List[LostItem]:
        return [LostItem(**item) for item in self.data["lost_items"].values()]

    def get_lost_item(self, item_id: str) -> Optional[LostItem]:
        data = self.data["lost_items"].get(item_id)
        return LostItem(**data) if data else None

    def add_lost_item(self, item: LostItem) -> LostItem:
        self.data["lost_items"][item.id] = item.model_dump()
        self.save()
        return item

    def update_lost_item_status(self, item_id: str, status: str):
        if item_id in self.data["lost_items"]:
            self.data["lost_items"][item_id]["status"] = status
            self.save()

    # Found Items
    def get_found_items(self) -> List[FoundItem]:
        return [FoundItem(**item) for item in self.data["found_items"].values()]

    def get_found_item(self, item_id: str) -> Optional[FoundItem]:
        data = self.data["found_items"].get(item_id)
        return FoundItem(**data) if data else None

    def add_found_item(self, item: FoundItem) -> FoundItem:
        self.data["found_items"][item.id] = item.model_dump()
        self.save()
        return item

    def update_found_item_status(self, item_id: str, status: str):
        if item_id in self.data["found_items"]:
            self.data["found_items"][item_id]["status"] = status
            self.save()

    # Claims
    def get_claims(self) -> List[Claim]:
        return [Claim(**c) for c in self.data["claims"].values()]

    def get_claim(self, claim_id: str) -> Optional[Claim]:
        data = self.data["claims"].get(claim_id)
        return Claim(**data) if data else None

    def add_claim(self, claim: Claim) -> Claim:
        self.data["claims"][claim.id] = claim.model_dump()
        self.save()
        return claim

    def update_claim(self, claim_id: str, status: str, admin_notes: str = ""):
        if claim_id in self.data["claims"]:
            self.data["claims"][claim_id]["status"] = status
            self.data["claims"][claim_id]["admin_notes"] = admin_notes
            self.save()

    # Matches Query & Computation
    def get_all_matches(self, min_score: float = 50.0) -> List[MatchItem]:
        lost_items = self.get_lost_items()
        found_items = self.get_found_items()
        matches = []
        for lost in lost_items:
            for found in found_items:
                breakdown = compute_match_score(lost, found)
                if breakdown.final_score >= min_score:
                    match_id = f"MATCH-{lost.id}-{found.id}"
                    matches.append(MatchItem(
                        id=match_id,
                        lost_item=lost,
                        found_item=found,
                        breakdown=breakdown,
                        status="CLAIMED" if (lost.status == "RETURNED" or found.status == "RETURNED") else "PENDING"
                    ))
        matches.sort(key=lambda m: m.breakdown.final_score, reverse=True)
        return matches

    def add_iot_event(self, event: dict):
        self.data["iot_events"].insert(0, event)
        if len(self.data["iot_events"]) > 50:
            self.data["iot_events"] = self.data["iot_events"][:50]
        self.save()

    def get_iot_events(self) -> List[dict]:
        return self.data.get("iot_events", [])

db = Database()
