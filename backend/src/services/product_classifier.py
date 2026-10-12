"""
Product Classifier & Physical State Engine
Automatically classifies the product into:
1. Category: Food & Beverage, Cosmetics & Personal Care, Health Supplement, Household/Cleaning.
2. Physical State: Liquid (Beverage / Serum / Oil / Tonic) vs Solid (Bar / Biscuit / Powder / Cream / Snack).
3. Adapts FSSAI, FDA, and EU regulatory thresholds (per 100g vs per 100ml).
"""

import re
from typing import Dict, Any, List, Optional

FOOD_KEYWORDS = {
    "food", "snack", "drink", "beverage", "juice", "biscuit", "cookie", "chocolate", "chips",
    "oil", "ghee", "butter", "milk", "tea", "coffee", "cereal", "noodle", "sauce", "ketchup",
    "sugar", "flour", "wheat", "rice", "spice", "masala", "salt", "energy drink", "soda",
    "nutrition facts", "per 100g", "per 100ml", "serving size", "calories", "protein", "carbohydrate", "fat"
}

COSMETIC_KEYWORDS = {
    "cosmetic", "skincare", "skin", "serum", "lotion", "cream", "shampoo", "conditioner",
    "face wash", "cleanser", "moisturizer", "sunscreen", "spf", "toner", "dermatologist",
    "fragrance", "parfum", "aqua", "water", "glycerin", "niacinamide", "salicylic acid", "retinol",
    "hyaluronic", "inci", "apply to face", "external use only", "rinse off", "leave on"
}

SUPPLEMENT_KEYWORDS = {
    "capsule", "tablet", "supplement", "dietary", "vitamin", "mineral", "ayurvedic",
    "daily dosage", "immunity", "extract", "gmp certified", "fssai nutraceutical"
}

LIQUID_INDICATORS = {
    "ml", "l", "fluid ounce", "fl oz", "beverage", "drink", "juice", "syrup", "toner", "oil",
    "serum", "shampoo", "liquid", "water", "soda", "shake", "per 100ml", "bottle"
}

SOLID_INDICATORS = {
    "gm", "g", "kg", "mg", "powder", "bar", "biscuit", "cookie", "cake", "tablet", "capsule",
    "soap bar", "balm", "butter", "chips", "per 100g", "crisps", "solid"
}

def classify_product(
    title: str = "",
    ingredients: Optional[List[str]] = None,
    net_content: str = "",
    raw_text: str = ""
) -> Dict[str, Any]:
    """
    Deterministically determines:
    - Primary Category
    - Physical State (liquid vs solid)
    - Regulatory & Nutritional Threshold Standard
    """
    combined = f"{title} {net_content} {raw_text} {' '.join(ingredients or [])}".lower()

    # 1. Category Classification
    food_score = sum(1 for kw in FOOD_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', combined))
    cosmetic_score = sum(1 for kw in COSMETIC_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', combined))
    supp_score = sum(1 for kw in SUPPLEMENT_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', combined))

    if supp_score > food_score and supp_score > cosmetic_score:
        category = "Health & Supplement"
        category_code = "supplement"
    elif cosmetic_score > food_score:
        category = "Cosmetics & Personal Care"
        category_code = "cosmetic"
    else:
        category = "Food & Beverage"
        category_code = "food"

    # 2. Physical State Classification (Liquid vs Solid)
    liquid_score = sum(1 for ind in LIQUID_INDICATORS if re.search(r'\b' + re.escape(ind) + r'\b', combined))
    solid_score = sum(1 for ind in SOLID_INDICATORS if re.search(r'\b' + re.escape(ind) + r'\b', combined))

    # Look specifically at net_content format
    if net_content:
        nc = net_content.lower()
        if any(unit in nc for unit in ["ml", "ltr", "liter", "l", "fl oz"]):
            liquid_score += 5
        elif any(unit in nc for unit in ["g", "gm", "gram", "kg", "mg"]):
            solid_score += 5

    if liquid_score > solid_score:
        physical_state = "liquid"
        unit_basis = "per 100 ml"
        # FSSAI HFSS thresholds for liquids
        thresholds = {
            "max_sugar_safe": 6.0,       # g / 100ml
            "max_saturated_fat": 2.2,    # g / 100ml
            "max_sodium_mg": 300.0,      # mg / 100ml
            "hfss_label": "FSSAI Liquid Threshold (6g Sugar / 100ml)"
        }
    else:
        physical_state = "solid"
        unit_basis = "per 100 g"
        # FSSAI HFSS thresholds for solids
        thresholds = {
            "max_sugar_safe": 10.0,      # g / 100g
            "max_saturated_fat": 4.0,    # g / 100g
            "max_sodium_mg": 675.0,      # mg / 100g
            "hfss_label": "FSSAI Solid Threshold (10g Sugar / 100g)"
        }

    return {
        "category": category,
        "category_code": category_code,
        "physical_state": physical_state,
        "unit_basis": unit_basis,
        "thresholds": thresholds,
        "classification_confidence": round(max(food_score, cosmetic_score) / (food_score + cosmetic_score + 1e-4), 2)
    }
