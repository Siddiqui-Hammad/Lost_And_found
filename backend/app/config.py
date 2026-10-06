import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI + IoT Smart Lost & Found System"
    TAGLINE: str = "Find what you lost. Return what you found."
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    COLLECTION_BOXES: dict = {
        "BOX-001": {"id": "BOX-001", "name": "Library Smart Box", "location": "Library", "zone": "Library 1st Floor Entry", "status": "ONLINE", "last_ping": "Live"},
        "BOX-002": {"id": "BOX-002", "name": "Canteen Smart Box", "location": "Canteen", "zone": "Central Food Court", "status": "ONLINE", "last_ping": "Live"},
        "BOX-003": {"id": "BOX-003", "name": "Main Gate Smart Box", "location": "Main Gate", "zone": "Security Desk Entry", "status": "ONLINE", "last_ping": "Live"},
        "BOX-004": {"id": "BOX-004", "name": "Admin Block Smart Box", "location": "Admin Block", "zone": "Reception Ground Floor", "status": "ONLINE", "last_ping": "Live"},
        "BOX-005": {"id": "BOX-005", "name": "Sports Complex Smart Box", "location": "Sports Complex", "zone": "Indoor Arena Desk", "status": "ONLINE", "last_ping": "Live"}
    }
    
    # Composite AI Scoring Weights (Sum = 1.0)
    WEIGHT_TEXT: float = 0.35
    WEIGHT_CATEGORY: float = 0.20
    WEIGHT_COLOR: float = 0.15
    WEIGHT_BRAND: float = 0.10
    WEIGHT_LOCATION: float = 0.10
    WEIGHT_TIME: float = 0.10
    
    # Thresholds
    HIGH_MATCH_THRESHOLD: float = 80.0
    POSSIBLE_MATCH_THRESHOLD: float = 60.0
    
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    UPLOADS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
