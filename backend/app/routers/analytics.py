from fastapi import APIRouter
from collections import Counter
from typing import Dict, Any
from ..database import db

router = APIRouter(prefix="/analytics", tags=["Campus Analytics"])

@router.get("")
def get_campus_analytics() -> Dict[str, Any]:
    lost_items = db.get_lost_items()
    found_items = db.get_found_items()
    claims = db.get_claims()
    matches = db.get_all_matches(min_score=65.0)

    total_lost = len(lost_items)
    total_found = len(found_items)
    ai_matches_count = len(matches)
    pending_claims = len([c for c in claims if c.status == "PENDING"])
    returned_items = len([l for l in lost_items if l.status == "RETURNED"])

    recovery_rate = round((returned_items / total_lost * 100) if total_lost > 0 else 0.0, 1)

    # Categories Breakdown
    categories = [l.category for l in lost_items] + [f.category for f in found_items]
    cat_counts = dict(Counter(categories).most_common(6))
    if not cat_counts:
        cat_counts = {"Electronics": 4, "Accessories": 3, "Stationery": 2, "Documents": 1}

    # Location Hotspots
    locations = [l.last_seen_location for l in lost_items] + [f.found_location for f in found_items]
    loc_counts = dict(Counter(locations).most_common(6))
    if not loc_counts:
        loc_counts = {"Library": 5, "Canteen": 3, "Main Gate": 2, "Admin Block": 2, "Sports Complex": 1}

    # IoT vs Manual collection breakdown
    iot_count = len([f for f in found_items if f.source == "IOT_BOX"])
    manual_count = len([f for f in found_items if f.source != "IOT_BOX"])

    return {
        "summary": {
            "total_lost": total_lost,
            "total_found": total_found,
            "ai_matches": ai_matches_count,
            "pending_claims": pending_claims,
            "returned_items": returned_items,
            "recovery_rate": recovery_rate,
            "iot_registered_items": iot_count,
            "manual_reported_items": manual_count
        },
        "category_distribution": cat_counts,
        "location_hotspots": loc_counts,
        "recent_iot_activity": db.get_iot_events()[:5]
    }
