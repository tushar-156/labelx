"""
UK FSA / WHO Front-of-Pack (FoP) Traffic Light Rating Engine for LabelX
Adapted from Food-Label-Analyzer (nutrition_analyzer.py)

Classifies food products into Green (Low), Amber (Moderate), and Red (High)
traffic light badges according to official UK Food Standards Agency (FSA),
European Commission, and WHO statutory front-of-pack nutrition guidelines.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class TrafficLightBadge(BaseModel):
    nutrient: str
    value: float
    unit: str
    rating: str  # 'LOW', 'MODERATE', 'HIGH', 'UNKNOWN'
    color: str   # 'GREEN', 'AMBER', 'RED', 'GRAY'
    reference_intake_pct: float
    threshold_explanation: str

class TrafficLightReport(BaseModel):
    badges: List[TrafficLightBadge]
    overall_healthiness: str  # 'HEALTHY', 'BALANCED', 'CAUTION', 'UNHEALTHY'
    high_count: int
    moderate_count: int
    low_count: int
    summary: str

# Statutory UK FSA / European Front-of-Pack Thresholds per 100g (Solid Food)
THRESHOLDS = {
    "sugar_g": {
        "low_max": 5.0,
        "high_min": 22.5,
        "daily_ri": 90.0,
        "unit": "g"
    },
    "salt_g": {
        "low_max": 0.3,
        "high_min": 1.5,
        "daily_ri": 6.0,
        "unit": "g"
    },
    "sodium_mg": {
        "low_max": 120.0,
        "high_min": 600.0,
        "daily_ri": 2400.0,
        "unit": "mg"
    },
    "fat_g": {
        "low_max": 3.0,
        "high_min": 17.5,
        "daily_ri": 70.0,
        "unit": "g"
    },
    "saturated_fat_g": {
        "low_max": 1.5,
        "high_min": 5.0,
        "daily_ri": 20.0,
        "unit": "g"
    },
    "calories_kcal": {
        "low_max": 200.0,
        "high_min": 400.0,
        "daily_ri": 2000.0,
        "unit": "kcal"
    }
}

def _classify_nutrient(key: str, value: Optional[float]) -> TrafficLightBadge:
    meta = THRESHOLDS.get(key, {"low_max": 0, "high_min": 0, "daily_ri": 100, "unit": ""})
    name_display = key.replace("_g", "").replace("_mg", "").replace("_kcal", "").replace("_", " ").title()

    if value is None:
        return TrafficLightBadge(
            nutrient=name_display,
            value=0.0,
            unit=meta["unit"],
            rating="UNKNOWN",
            color="GRAY",
            reference_intake_pct=0.0,
            threshold_explanation=f"{name_display} data not declared on packaging"
        )

    val = float(value)
    low_max = meta["low_max"]
    high_min = meta["high_min"]
    ri_pct = round((val / meta["daily_ri"]) * 100, 1)

    if val < low_max:
        rating = "LOW"
        color = "GREEN"
        desc = f"Low ({val}{meta['unit']} < {low_max}{meta['unit']} per 100g)"
    elif val >= high_min:
        rating = "HIGH"
        color = "RED"
        desc = f"High ({val}{meta['unit']} >= {high_min}{meta['unit']} statutory limit)"
    else:
        rating = "MODERATE"
        color = "AMBER"
        desc = f"Moderate ({low_max}{meta['unit']} - {high_min}{meta['unit']} range)"

    return TrafficLightBadge(
        nutrient=name_display,
        value=round(val, 1),
        unit=meta["unit"],
        rating=rating,
        color=color,
        reference_intake_pct=ri_pct,
        threshold_explanation=desc
    )

def evaluate_traffic_lights(nutritional_info: Optional[Dict[str, Any]] = None) -> TrafficLightReport:
    """
    Evaluates nutritional info against UK FSA / WHO Front-of-Pack standards.
    """
    info = nutritional_info or {}

    sugar_val = info.get("sugars_100g") or info.get("sugar") or info.get("sugars")
    salt_val = info.get("salt_100g") or info.get("salt")
    sodium_val = info.get("sodium_100g") or info.get("sodium")
    fat_val = info.get("fat_100g") or info.get("fat") or info.get("total_fat")
    sat_fat_val = info.get("saturated-fat_100g") or info.get("saturated_fat")
    cal_val = info.get("energy-kcal_100g") or info.get("calories") or info.get("energy")

    # If salt is missing but sodium is present: salt = sodium * 2.5 / 1000
    if salt_val is None and sodium_val is not None:
        try:
            salt_val = float(sodium_val) * 2.5 / 1000.0
        except:
            pass
    # If sodium is missing but salt is present: sodium = salt / 2.5 * 1000
    if sodium_val is None and salt_val is not None:
        try:
            sodium_val = float(salt_val) / 2.5 * 1000.0
        except:
            pass

    badges = [
        _classify_nutrient("calories_kcal", float(cal_val) if cal_val is not None else None),
        _classify_nutrient("sugar_g", float(sugar_val) if sugar_val is not None else None),
        _classify_nutrient("fat_g", float(fat_val) if fat_val is not None else None),
        _classify_nutrient("saturated_fat_g", float(sat_fat_val) if sat_fat_val is not None else None),
        _classify_nutrient("salt_g", float(salt_val) if salt_val is not None else None)
    ]

    high_count = sum(1 for b in badges if b.rating == "HIGH")
    mod_count = sum(1 for b in badges if b.rating == "MODERATE")
    low_count = sum(1 for b in badges if b.rating == "LOW")

    if high_count >= 2:
        healthiness = "UNHEALTHY"
        summary = f"Contains {high_count} HIGH (Red) indicators according to UK FSA front-of-pack guidelines. Consume infrequently."
    elif high_count == 1:
        healthiness = "CAUTION"
        summary = f"Contains 1 HIGH (Red) indicator. Moderate consumption advised."
    elif mod_count >= 2:
        healthiness = "BALANCED"
        summary = "Balanced nutritional profile with moderate levels across key nutrients."
    else:
        healthiness = "HEALTHY"
        summary = "Excellent front-of-pack rating with low sugar, saturated fat, and salt."

    return TrafficLightReport(
        badges=badges,
        overall_healthiness=healthiness,
        high_count=high_count,
        moderate_count=mod_count,
        low_count=low_count,
        summary=summary
    )

traffic_light_engine = evaluate_traffic_lights
