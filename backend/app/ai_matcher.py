import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .config import settings
from .models import LostItem, FoundItem, MatchScoreBreakdown

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return " ".join(text.split())

def calculate_text_similarity(text1: str, text2: str) -> float:
    t1 = normalize_text(text1)
    t2 = normalize_text(text2)
    if not t1 or not t2:
        return 0.0
    if t1 == t2:
        return 100.0
    
    # 1. Cosine similarity via TF-IDF
    cos_sim = 0.0
    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([t1, t2])
        cos_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]) * 100.0
    except Exception:
        cos_sim = 0.0
    
    # 2. Token overlap & substring check
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'with', 'for', 'of', 'and', 'is', 'to', 'near', 'lost', 'found', 'on', 'the'}
    words1 = {w for w in t1.split() if w not in stop_words and len(w) > 2}
    words2 = {w for w in t2.split() if w not in stop_words and len(w) > 2}
    
    overlap_sim = 0.0
    if words1 and words2:
        intersection = len(words1.intersection(words2))
        min_len = min(len(words1), len(words2))
        overlap_sim = (intersection / min_len) * 100.0 if min_len > 0 else 0.0
        union = len(words1.union(words2))
        jaccard = (intersection / union) * 100.0 if union > 0 else 0.0
        overlap_sim = max(overlap_sim * 0.8 + jaccard * 0.2, overlap_sim)

    text_score = max(cos_sim, overlap_sim)
    return round(float(min(100.0, max(0.0, text_score))), 1)

def calculate_category_similarity(cat1: str, cat2: str) -> float:
    c1 = (cat1 or "").strip().lower()
    c2 = (cat2 or "").strip().lower()
    if not c1 or not c2:
        return 50.0
    if c1 == c2:
        return 100.0
    synonyms = {
        "electronics": ["earbuds", "headphones", "charger", "laptop", "calculator", "phone", "pendrive"],
        "documents": ["id card", "college id", "aadhar", "library card", "pass", "admit card"],
        "accessories": ["watch", "wallet", "keys", "belt", "glasses", "spectacles", "ring", "chain", "bottle"],
        "bags": ["backpack", "handbag", "pouch", "trolley", "bag"],
        "stationery": ["book", "notebook", "calculator", "pen", "pencil box", "file", "folder"]
    }
    for main_cat, sub_cats in synonyms.items():
        if (c1 == main_cat and c2 in sub_cats) or (c2 == main_cat and c1 in sub_cats):
            return 95.0
        if c1 in sub_cats and c2 in sub_cats:
            return 90.0
    return 20.0

def calculate_color_similarity(color1: str, color2: str) -> float:
    c1 = (color1 or "").strip().lower()
    c2 = (color2 or "").strip().lower()
    if not c1 or not c2:
        return 50.0
    if c1 == c2 or c1 in c2 or c2 in c1:
        return 100.0
    groups = [
        {"black", "dark grey", "grey", "charcoal", "gray", "matte black"},
        {"white", "silver", "off-white", "cream", "pearl"},
        {"blue", "navy", "cyan", "sky blue", "royal blue"},
        {"red", "maroon", "burgundy", "crimson"},
        {"brown", "tan", "beige", "khaki", "camel"}
    ]
    for g in groups:
        if any(w in c1 for w in g) and any(w in c2 for w in g):
            return 90.0
    return 15.0

def calculate_brand_similarity(brand1: str, brand2: str) -> float:
    b1 = (brand1 or "").strip().lower()
    b2 = (brand2 or "").strip().lower()
    if not b1 or not b2 or b1 in ["unknown", "other", "na", "n/a", "none"]:
        return 70.0
    if b1 == b2 or b1 in b2 or b2 in b1:
        return 100.0
    return 20.0

def calculate_location_similarity(loc1: str, loc2: str) -> float:
    l1 = (loc1 or "").strip().lower()
    l2 = (loc2 or "").strip().lower()
    if not l1 or not l2:
        return 50.0
    if l1 == l2 or l1 in l2 or l2 in l1:
        return 100.0
    zones = [
        {"library", "reading room", "study area", "librarian desk", "digital library"},
        {"canteen", "cafeteria", "food court", "juice shop", "nescafe", "mess"},
        {"main gate", "parking", "security gate", "bus stand", "auto stand", "guard room"},
        {"admin block", "academic block", "dean office", "accounts", "reception", "director office"},
        {"sports complex", "gym", "ground", "badminton court", "stadium", "cricket ground"}
    ]
    for z in zones:
        if any(w in l1 for w in z) and any(w in l2 for w in z):
            return 95.0
    return 40.0

def calculate_time_similarity(time1_str: str, time2_str: str) -> float:
    if not time1_str or not time2_str:
        return 80.0
    t1 = time1_str.lower()
    t2 = time2_str.lower()
    if t1 == t2:
        return 100.0
    return 85.0

def compute_match_score(lost: LostItem, found: FoundItem) -> MatchScoreBreakdown:
    # 1. Text score: Blend item name match (50%) + description match (50%)
    name_score = calculate_text_similarity(lost.item_name, found.item_name)
    desc_score = calculate_text_similarity(f"{lost.item_name} {lost.description}", f"{found.item_name} {found.description}")
    text_score = round(max(name_score, (name_score * 0.5 + desc_score * 0.5)), 1)
    
    cat_score = calculate_category_similarity(lost.category, found.category)
    color_score = calculate_color_similarity(lost.color, found.color)
    brand_score = calculate_brand_similarity(lost.brand or "", found.brand or "")
    loc_score = calculate_location_similarity(lost.last_seen_location, found.found_location)
    time_score = calculate_time_similarity(lost.lost_time, found.found_time)
    
    final_score = (
        (text_score * settings.WEIGHT_TEXT) +
        (cat_score * settings.WEIGHT_CATEGORY) +
        (color_score * settings.WEIGHT_COLOR) +
        (brand_score * settings.WEIGHT_BRAND) +
        (loc_score * settings.WEIGHT_LOCATION) +
        (time_score * settings.WEIGHT_TIME)
    )
    
    final_score = round(min(100.0, max(0.0, final_score)), 1)
    
    if final_score >= settings.HIGH_MATCH_THRESHOLD:
        tier = "HIGH"
    elif final_score >= settings.POSSIBLE_MATCH_THRESHOLD:
        tier = "POSSIBLE"
    else:
        tier = "LOW"
        
    return MatchScoreBreakdown(
        text_score=text_score,
        category_score=cat_score,
        color_score=color_score,
        brand_score=brand_score,
        location_score=loc_score,
        time_score=time_score,
        final_score=final_score,
        tier=tier
    )
