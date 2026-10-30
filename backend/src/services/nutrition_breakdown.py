"""
4-Quadrant Nutrition & Ingredient Breakdown Service
Categorizes ingredients into:
- safe_ingredients: Neutral, safe base compounds
- unsafe_ingredients: High-risk synthetic additives or banned chemicals
- positive_nutrients: Bioactive nutrients, vitamins, whole grains, antioxidants, barrier lipids
- negative_additives: Artificial colorants, synthetic preservatives, ultra-processed emulsifiers
Computes overall health_score (0-100) and actionable consumer recommendation.
Ported & enhanced from nutriscope.
"""

from typing import List, Dict, Any
from src.services.hazard_dataset import hazard_dataset

# Beneficial nutrients across Food & Cosmetics
POSITIVE_NUTRIENT_KEYWORDS = {
    # Food
    "fiber", "iron", "calcium", "vitamin", "zinc", "protein", "oats", "chia", "flaxseed",
    "whole wheat", "almond", "walnut", "antioxidant", "probiotic", "prebiotic", "folate",
    # Cosmetics
    "ceramide", "niacinamide", "hyaluronic", "centella", "madecassoside", "panthenol",
    "squalane", "tocopherol", "peptides", "green tea", "allantoin", "glycerin", "aloe"
}

# Negative additives / ultra-processed compounds
NEGATIVE_ADDITIVE_KEYWORDS = {
    # Artificial food colors
    "red 40", "yellow 5", "yellow 6", "blue 1", "tartrazine", "sunset yellow", "allura red", "caramel color",
    # Harsh preservatives
    "sodium benzoate", "potassium sorbate", "bht", "bha", "tbhq", "sodium metabisulfite",
    # Emulsifiers & thickeners
    "carrageenan", "polysorbate", "carboxymethylcellulose", "sodium lauryl sulfate",
    # Cosmetic risks
    "paraben", "methylparaben", "propylparaben", "dmdm hydantoin", "imidazolidinyl urea",
    "formaldehyde", "triclosan", "oxybenzone", "phthalate"
}

def generate_quadrant_breakdown(
    ingredients: List[str],
    category_code: str = "food",
    physical_state: str = "solid",
    sugar_flags: int = 0
) -> Dict[str, Any]:
    """
    Produces the 4-Quadrant Nutrition and Formulation Breakdown.
    """
    safe_ingredients: List[str] = []
    unsafe_ingredients: List[str] = []
    positive_nutrients: List[str] = []
    negative_additives: List[str] = []

    for ing in ingredients:
        lower = ing.lower().strip()
        hazard = hazard_dataset.lookup(ing)

        is_unsafe = False
        is_negative = False
        is_positive = False

        if hazard:
            if hazard.get("type") == "toxic":
                unsafe_ingredients.append(ing)
                is_unsafe = True
            elif hazard.get("type") == "moderate":
                negative_additives.append(ing)
                is_negative = True

        if not is_unsafe and not is_negative:
            if any(neg in lower for neg in NEGATIVE_ADDITIVE_KEYWORDS):
                negative_additives.append(ing)
                is_negative = True
            elif any(pos in lower for pos in POSITIVE_NUTRIENT_KEYWORDS):
                positive_nutrients.append(ing)
                is_positive = True
            else:
                safe_ingredients.append(ing)

    # Compute Health Score (0 - 100)
    base_score = 85
    base_score -= len(unsafe_ingredients) * 20
    base_score -= len(negative_additives) * 8
    base_score -= sugar_flags * 10
    base_score += len(positive_nutrients) * 5

    # Clamp 5 to 100
    health_score = max(10, min(100, base_score))

    if health_score >= 75:
        verdict = "Healthy / Clean Formulation"
    elif health_score >= 50:
        verdict = "Moderate"
    else:
        verdict = "Unhealthy / High Risk"

    # Actionable Recommendation
    if category_code == "food":
        if physical_state == "liquid":
            rec = "Liquid matrix accelerates glycemic absorption. Consume sparingly if flagged for sweeteners." if health_score < 60 else "Hydrating beverage profile with clean formulation."
        else:
            rec = "High-processed snack profile. Limit consumption to occasional treat." if health_score < 60 else "Nutrient-dense solid formulation suitable for regular dietary incorporation."
    else:
        rec = "Formulation contains potential sensitizers or endocrine disruptors. Patch test recommended." if health_score < 60 else "Gentle, barrier-supportive formulation with high biocompatibility."

    summary = f"Evaluated {len(ingredients)} ingredient(s). Health score: {health_score}/100 ({verdict}). Found {len(positive_nutrients)} positive nutrient(s) and {len(negative_additives) + len(unsafe_ingredients)} flagged additive(s)."

    return {
        "safe_ingredients": safe_ingredients,
        "unsafe_ingredients": unsafe_ingredients,
        "positive_nutrients": positive_nutrients,
        "negative_additives": negative_additives,
        "health_score": health_score,
        "verdict": verdict,
        "summary": summary,
        "recommendation": rec
    }
