import json
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from .config import settings
from .utils.seed import SEED_USERS, SEED_IOT_BOXES, SEED_LOST_ITEMS, SEED_FOUND_ITEMS, SEED_CLAIMS

DB_JSON_PATH = os.path.join(settings.DATA_DIR, "mongodb_store.json")

class Database:
    """
    TRACE AI MongoDB Engine
    Provides high-performance collection abstractions with automatic
    JSON persistence fallback ensuring zero setup dependencies.
    """
    def __init__(self):
        self.is_connected = False
        self.mongo_client = None
        self.mongo_db = None
        
        # In-memory document storage backing collections
        self.collections: Dict[str, Dict[str, Any]] = {
            "users": {},
            "lost_items": {},
            "found_items": {},
            "claims": {},
            "iot_boxes": {},
            "iot_events": {},
            "notifications": {},
            "matches": {}
        }
        
        self.init_connection()

    def init_connection(self):
        # Attempt MongoDB connection if pymongo is installed
        try:
            import pymongo
            client = pymongo.MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=1500)
            client.server_info()  # Test connection
            self.mongo_client = client
            self.mongo_db = client[settings.DATABASE_NAME]
            self.is_connected = True
            print(f"[DB] Connected successfully to native MongoDB at {settings.MONGODB_URI}")
            self.sync_mongo_initial_data()
            return
        except Exception as e:
            print(f"[DB] Native MongoDB not available ({e}). Using embedded DocumentDB engine.")
            self.is_connected = False

        self.load_local_store()

    def load_local_store(self):
        if os.path.exists(DB_JSON_PATH):
            try:
                with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
                    self.collections = json.load(f)
                print(f"[DB] Loaded existing data store from {DB_JSON_PATH}")
                return
            except Exception as e:
                print(f"[DB] Error loading store: {e}. Re-seeding defaults.")
        self.seed_defaults()

    def save_local_store(self):
        try:
            with open(DB_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.collections, f, indent=2)
        except Exception as e:
            print(f"[DB] Failed to save store: {e}")

    def sync_mongo_initial_data(self):
        if not self.is_connected:
            return
        # If collections empty, seed
        if self.mongo_db.users.count_documents({}) == 0:
            self.mongo_db.users.insert_many(SEED_USERS)
            self.mongo_db.iot_boxes.insert_many(SEED_IOT_BOXES)
            self.mongo_db.lost_items.insert_many(SEED_LOST_ITEMS)
            self.mongo_db.found_items.insert_many(SEED_FOUND_ITEMS)
            self.mongo_db.claims.insert_many(SEED_CLAIMS)
            print("[DB] Seeded MongoDB collections with initial realistic records.")

    def seed_defaults(self):
        self.collections["users"] = {u["user_id"]: u for u in SEED_USERS}
        self.collections["iot_boxes"] = {b["box_id"]: b for b in SEED_IOT_BOXES}
        self.collections["lost_items"] = {l["item_id"]: l for l in SEED_LOST_ITEMS}
        self.collections["found_items"] = {f["item_id"]: f for f in SEED_FOUND_ITEMS}
        self.collections["claims"] = {c["claim_id"]: c for c in SEED_CLAIMS}
        self.collections["iot_events"] = {}
        self.collections["notifications"] = {}
        self.collections["matches"] = {}
        self.save_local_store()
        print("[DB] Initialized local DocumentDB with realistic campus seed records.")

    def reset_database(self):
        """Allows Admin to reset demo scenario"""
        self.seed_defaults()
        if self.is_connected:
            for col_name in ["users", "iot_boxes", "lost_items", "found_items", "claims", "iot_events", "notifications", "matches"]:
                self.mongo_db[col_name].delete_many({})
            self.sync_mongo_initial_data()
        return {"status": "success", "message": "Database reset to initial demo state."}

    # ==========================================
    # USER OPERATIONS
    # ==========================================
    def get_users(self) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.users.find({}, {"_id": 0}))
        return list(self.collections["users"].values())

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        if self.is_connected:
            return self.mongo_db.users.find_one({"user_id": user_id}, {"_id": 0})
        return self.collections["users"].get(user_id)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        if self.is_connected:
            return self.mongo_db.users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}}, {"_id": 0})
        for u in self.collections["users"].values():
            if u.get("email", "").lower() == email.strip().lower():
                return u
        return None

    def get_user_by_identifier(self, identifier: str) -> Optional[dict]:
        target = identifier.strip().lower()
        if self.is_connected:
            return self.mongo_db.users.find_one({
                "$or": [
                    {"email": {"$regex": f"^{target}$", "$options": "i"}},
                    {"student_id": {"$regex": f"^{target}$", "$options": "i"}}
                ]
            }, {"_id": 0})
        for u in self.collections["users"].values():
            if u.get("email", "").lower() == target or (u.get("student_id") and u.get("student_id").lower() == target):
                return u
        return None

    def add_user(self, user_dict: dict) -> dict:
        if self.is_connected:
            self.mongo_db.users.insert_one(user_dict.copy())
        self.collections["users"][user_dict["user_id"]] = user_dict
        self.save_local_store()
        return user_dict

    # ==========================================
    # LOST ITEMS OPERATIONS
    # ==========================================
    def get_lost_items(self) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.lost_items.find({}, {"_id": 0}))
        return list(self.collections["lost_items"].values())

    def get_lost_item(self, item_id: str) -> Optional[dict]:
        if self.is_connected:
            return self.mongo_db.lost_items.find_one({"item_id": item_id}, {"_id": 0})
        return self.collections["lost_items"].get(item_id)

    def add_lost_item(self, item_dict: dict) -> dict:
        if self.is_connected:
            self.mongo_db.lost_items.insert_one(item_dict.copy())
        self.collections["lost_items"][item_dict["item_id"]] = item_dict
        self.save_local_store()
        return item_dict

    def update_lost_item_status(self, item_id: str, status: str) -> Optional[dict]:
        if self.is_connected:
            self.mongo_db.lost_items.update_one({"item_id": item_id}, {"$set": {"status": status}})
        if item_id in self.collections["lost_items"]:
            self.collections["lost_items"][item_id]["status"] = status
            self.save_local_store()
            return self.collections["lost_items"][item_id]
        return None

    # ==========================================
    # FOUND ITEMS OPERATIONS
    # ==========================================
    def get_found_items(self) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.found_items.find({}, {"_id": 0}))
        return list(self.collections["found_items"].values())

    def get_found_item(self, item_id: str) -> Optional[dict]:
        if self.is_connected:
            return self.mongo_db.found_items.find_one({"item_id": item_id}, {"_id": 0})
        return self.collections["found_items"].get(item_id)

    def add_found_item(self, item_dict: dict) -> dict:
        if self.is_connected:
            self.mongo_db.found_items.insert_one(item_dict.copy())
        self.collections["found_items"][item_dict["item_id"]] = item_dict
        self.save_local_store()
        return item_dict

    def update_found_item_status(self, item_id: str, status: str) -> Optional[dict]:
        if self.is_connected:
            self.mongo_db.found_items.update_one({"item_id": item_id}, {"$set": {"status": status}})
        if item_id in self.collections["found_items"]:
            self.collections["found_items"][item_id]["status"] = status
            self.save_local_store()
            return self.collections["found_items"][item_id]
        return None

    # ==========================================
    # IOT BOXES & EVENTS
    # ==========================================
    def get_iot_boxes(self) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.iot_boxes.find({}, {"_id": 0}))
        return list(self.collections["iot_boxes"].values())

    def get_iot_box(self, box_id: str) -> Optional[dict]:
        if self.is_connected:
            return self.mongo_db.iot_boxes.find_one({"box_id": box_id}, {"_id": 0})
        return self.collections["iot_boxes"].get(box_id)

    def add_iot_box(self, box_dict: dict) -> dict:
        if self.is_connected:
            self.mongo_db.iot_boxes.insert_one(box_dict.copy())
        self.collections["iot_boxes"][box_dict["box_id"]] = box_dict
        self.save_local_store()
        return box_dict

    def record_iot_event(self, event_dict: dict) -> dict:
        if self.is_connected:
            self.mongo_db.iot_events.insert_one(event_dict.copy())
            self.mongo_db.iot_boxes.update_one(
                {"box_id": event_dict["box_id"]},
                {"$inc": {"items_registered": 1}, "$set": {"last_seen": event_dict["timestamp"]}}
            )
        self.collections["iot_events"][event_dict["event_id"]] = event_dict
        if event_dict["box_id"] in self.collections["iot_boxes"]:
            self.collections["iot_boxes"][event_dict["box_id"]]["items_registered"] += 1
            self.collections["iot_boxes"][event_dict["box_id"]]["last_seen"] = event_dict["timestamp"]
        self.save_local_store()
        return event_dict

    def get_iot_events(self) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.iot_events.find({}, {"_id": 0}))
        return list(self.collections["iot_events"].values())

    # ==========================================
    # CLAIMS
    # ==========================================
    def get_claims(self) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.claims.find({}, {"_id": 0}))
        return list(self.collections["claims"].values())

    def get_claim(self, claim_id: str) -> Optional[dict]:
        if self.is_connected:
            return self.mongo_db.claims.find_one({"claim_id": claim_id}, {"_id": 0})
        return self.collections["claims"].get(claim_id)

    def add_claim(self, claim_dict: dict) -> dict:
        if self.is_connected:
            self.mongo_db.claims.insert_one(claim_dict.copy())
        self.collections["claims"][claim_dict["claim_id"]] = claim_dict
        self.save_local_store()
        return claim_dict

    def update_claim_status(self, claim_id: str, status: str, admin_notes: Optional[str] = None) -> Optional[dict]:
        reviewed_at = datetime.now().isoformat()
        update_fields = {"status": status, "reviewed_at": reviewed_at}
        if admin_notes:
            update_fields["admin_notes"] = admin_notes
            
        if self.is_connected:
            self.mongo_db.claims.update_one({"claim_id": claim_id}, {"$set": update_fields})
        if claim_id in self.collections["claims"]:
            self.collections["claims"][claim_id].update(update_fields)
            self.save_local_store()
            return self.collections["claims"][claim_id]
        return None

    # ==========================================
    # NOTIFICATIONS
    # ==========================================
    def add_notification(self, notif_dict: dict) -> dict:
        if self.is_connected:
            self.mongo_db.notifications.insert_one(notif_dict.copy())
        self.collections["notifications"][notif_dict["notification_id"]] = notif_dict
        self.save_local_store()
        return notif_dict

    def get_user_notifications(self, user_email: str) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.notifications.find({"user_email": user_email}, {"_id": 0}))
        return [n for n in self.collections["notifications"].values() if n.get("user_email", "").lower() == user_email.lower()]

    def mark_notification_read(self, notif_id: str):
        if self.is_connected:
            self.mongo_db.notifications.update_one({"notification_id": notif_id}, {"$set": {"is_read": True}})
        if notif_id in self.collections["notifications"]:
            self.collections["notifications"][notif_id]["is_read"] = True
            self.save_local_store()

    # ==========================================
    # MATCHES CACHE / STORE
    # ==========================================
    def save_matches(self, matches_list: List[dict]):
        if self.is_connected:
            for m in matches_list:
                self.mongo_db.matches.replace_one({"match_id": m["match_id"]}, m, upsert=True)
        for m in matches_list:
            self.collections["matches"][m["match_id"]] = m
        self.save_local_store()

    def get_saved_matches(self) -> List[dict]:
        if self.is_connected:
            return list(self.mongo_db.matches.find({}, {"_id": 0}))
        return list(self.collections["matches"].values())

db = Database()
