from typing import Dict, Any, Optional
from datetime import datetime
from ..config import settings
from ..models.match import MatchBreakdown
from .embedding_engine import embedding_engine
from .image_matcher import image_matcher

def compute_category_score(cat1: str, cat2: str) -> float:
    if not cat1 or not cat2:
        return 0.0
    c1, c2 = cat1.strip().lower(), cat2.strip().lower()
    if c1 == c2:
        return 100.0
    # Synonyms / Related category checks
    related = {
        "wallet": ["accessories", "documents", "id card"],
        "id card": ["documents", "wallet", "accessories"],
        "electronics": ["accessories", "watch", "stationery"],
        "keys": ["accessories"],
        "bag": ["accessories", "clothing"],
        "bottle": ["accessories", "stationery"],
        "watch": ["electronics", "accessories"]
    }
    if c2 in related.get(c1, []) or c1 in related.get(c2, []):
        return 75.0
    return 0.0

def compute_color_score(col1: str, col2: str) -> float:
    if not col1 or not col2:
        return 50.0  # Neutral if unknown
    c1, c2 = col1.strip().lower(), col2.strip().lower()
    if c1 == c2:
        return 100.0
    if c1 in c2 or c2 in c1:
        return 85.0
    return 20.0

def compute_brand_score(b1: Optional[str], b2: Optional[str]) -> float:
    if not b1 or not b2 or b1.strip() == "" or b2.strip() == "":
        return 60.0  # Default neutral score
    brand1, brand2 = b1.strip().lower(), b2.strip().lower()
    if brand1 == brand2:
        return 100.0
    if brand1 in brand2 or brand2 in brand1:
        return 85.0
    return 10.0

def compute_location_score(loc1: str, loc2: str) -> float:
    if not loc1 or not loc2:
        return 50.0
    l1, l2 = loc1.strip().lower(), loc2.strip().lower()
    if l1 == l2:
        return 100.0
    # Proximity matrix for campus
    adjacent_pairs = [
        {"library", "admin block"},
        {"canteen", "sports complex"},
        {"classroom hall", "library"},
        {"main gate", "admin block"}
    ]
    for pair in adjacent_pairs:
        if l1 in pair and l2 in pair:
            return 75.0
    return 30.0

def compute_time_score(t1_str: str, t2_str: str) -> float:
    try:
        dt1 = datetime.fromisoformat(t1_str.replace("Z", ""))
        dt2 = datetime.fromisoformat(t2_str.replace("Z", ""))
        diff_hours = abs((dt1 - dt2).total_seconds()) / 3600.0
        if diff_hours <= 6.0:
            return 100.0
        elif diff_hours <= 24.0:
            return 90.0
        elif diff_hours <= 72.0:
            return 75.0
        elif diff_hours <= 168.0:
            return 50.0
        else:
            return 30.0
    except Exception:
        return 70.0  # Default temporal tolerance

def compute_composite_match(lost_item: dict, found_item: dict) -> MatchBreakdown:
    """
    Computes 6-factor configurable weighted match score:
    final_score = (
        0.40 * text_score +
        0.20 * category_score +
        0.15 * location_score +
        0.10 * color_score +
        0.10 * time_score +
        0.05 * brand_score
    )
    """
    # 1. Text description semantics
    desc1 = f"{lost_item.get('item_name', '')} {lost_item.get('description', '')}"
    desc2 = f"{found_item.get('item_name', '')} {found_item.get('description', '')}"
    text_score = embedding_engine.compute_similarity(desc1, desc2)

    # 2. Category
    cat_score = compute_category_score(lost_item.get("category", ""), found_item.get("category", ""))

    # 3. Color
    col_score = compute_color_score(lost_item.get("color", ""), found_item.get("color", ""))

    # 4. Brand
    brd_score = compute_brand_score(lost_item.get("brand", ""), found_item.get("brand", ""))

    # 5. Location
    loc_score = compute_location_score(lost_item.get("location", ""), found_item.get("location", ""))

    # 6. Time window
    time_score = compute_time_score(lost_item.get("lost_at", ""), found_item.get("found_at", ""))

    # Optional Vision / CLIP score
    img_score = image_matcher.compute_image_similarity(lost_item.get("image_url"), found_item.get("image_url"))

    # Configurable weighted summation
    raw_final = (
        settings.WEIGHT_TEXT * text_score +
        settings.WEIGHT_CATEGORY * cat_score +
        settings.WEIGHT_LOCATION * loc_score +
        settings.WEIGHT_COLOR * col_score +
        settings.WEIGHT_TIME * time_score +
        settings.WEIGHT_BRAND * brd_score
    )
    final_score = round(min(100.0, max(0.0, raw_final)), 1)

    # Match Level Classification
    if final_score >= settings.THRESHOLD_HIGH:
        match_level = "HIGH PROBABILITY"
    elif final_score >= settings.THRESHOLD_POSSIBLE:
        match_level = "POSSIBLE MATCH"
    else:
        match_level = "LOW PROBABILITY"

    return MatchBreakdown(
        text_score=round(text_score, 1),
        category_score=round(cat_score, 1),
        color_score=round(col_score, 1),
        brand_score=round(brd_score, 1),
        location_score=round(loc_score, 1),
        time_score=round(time_score, 1),
        image_score=img_score,
        final_score=final_score,
        match_level=match_level
    )
