from fastapi import APIRouter
from collections import Counter
from ..database import db

router = APIRouter(prefix="/analytics", tags=["Campus Analytics"])

@router.get("")
def get_analytics():
    lost_items = db.get_lost_items()
    found_items = db.get_found_items()
    claims = db.get_claims()
    
    # 1. Category Distribution
    all_categories = [l.get("category", "Other") for l in lost_items] + [f.get("category", "Other") for f in found_items]
    category_counts = dict(Counter(all_categories))
    
    # 2. Location Hotspots
    lost_locations = dict(Counter([l.get("location", "Unknown") for l in lost_items]))
    found_locations = dict(Counter([f.get("location", "Unknown") for f in found_items]))
    
    # 3. Monthly Recovery & Incident Trends
    monthly_trend = [
        {"month": "Jul", "lost": 14, "found": 10, "recovered": 8},
        {"month": "Aug", "lost": 22, "found": 18, "recovered": 15},
        {"month": "Sep", "lost": 35, "found": 28, "recovered": 24},
        {"month": "Oct", "lost": len(lost_items), "found": len(found_items), "recovered": len([l for l in lost_items if l.get("status") in ["RETURNED", "RESOLVED"]])}
    ]
    
    # 4. Claim Status Breakdown
    claim_statuses = dict(Counter([c.get("status", "PENDING") for c in claims]))
    
    return {
        "category_distribution": [{"category": k, "count": v} for k, v in category_counts.items()],
        "lost_by_location": [{"location": k, "count": v} for k, v in lost_locations.items()],
        "found_by_location": [{"location": k, "count": v} for k, v in found_locations.items()],
        "monthly_trend": monthly_trend,
        "claim_status_breakdown": [{"status": k, "count": v} for k, v in claim_statuses.items()]
    }
