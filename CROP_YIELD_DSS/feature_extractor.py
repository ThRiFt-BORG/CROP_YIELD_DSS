# feature_extractor.py
import re
import difflib
from typing import Dict, Optional

COUNTY_GEO = {
    "nakuru": {"lat": -0.3031, "lon": 36.0800, "elevation": 1850, "soil_texture": 2},
    "nyandarua": {"lat": -0.1800, "lon": 36.5220, "elevation": 2500, "soil_texture": 2},
    "trans nzoia": {"lat": 1.0567, "lon": 34.9500, "elevation": 1900, "soil_texture": 2},
}

def normalize_text(text: str) -> str:
    return text.lower().replace("-", " ").replace("_", " ").strip()

def extract_county(user_input: str) -> Optional[str]:
    """Improved county extraction"""
    text = normalize_text(user_input)
    
    # Direct matching
    for county in COUNTY_GEO.keys():
        if county in text or county.replace(" ", "") in text.replace(" ", ""):
            return county
    
    # Fuzzy matching (better for typos)
    words = text.split()
    for word in words:
        matches = difflib.get_close_matches(word, COUNTY_GEO.keys(), n=1, cutoff=0.75)
        if matches:
            return matches[0]
    
    # Full text fuzzy as fallback
    matches = difflib.get_close_matches(text, COUNTY_GEO.keys(), n=1, cutoff=0.65)
    if matches:
        return matches[0]
    
    return None

def extract_features(user_input: str) -> Dict:
    """Clean, focused feature extractor"""
    text = user_input.lower()
    
    features = {
        "county": None,
        "precip_total": None,
        "fertilizer": None,
        "temp_mean": None,
    }

    # County
    features["county"] = extract_county(user_input)

    # Rainfall (mm) - improved patterns
    rain_match = re.search(r'(\d{3,4})\s*(?:mm)?\s*(?:rain|rainfall|precip|precipitation)', text)
    if rain_match:
        val = int(rain_match.group(1))
        if 300 <= val <= 2000:
            features["precip_total"] = val

    # Fertilizer (kg/ha)
    fert_match = re.search(r'(\d{2,4})\s*(?:kg/ha|kg n/ha|fertilizer|n|nitrogen)', text)
    if not fert_match:
        fert_match = re.search(r'(?:fertilizer|n|nitrogen)\s*(?:rate|of|around)?\s*(\d{2,4})', text)
    if fert_match:
        val = int(fert_match.group(1))
        if 0 <= val <= 300:
            features["fertilizer"] = val

    # Temperature (°C) - significantly improved
    temp_match = re.search(r'(\d{1,2})\s*(?:°?c|degrees?|deg|°)', text)
    if temp_match:
        val = int(temp_match.group(1))
        if 15 <= val <= 32:
            features["temp_mean"] = val

    return features