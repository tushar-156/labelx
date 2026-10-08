from typing import List, Dict, Any

# A mocked list of regulatory databases. In production, this might be loaded from a DB or JSON
BANNED_INGREDIENTS = {
    "fda": ["bithionol", "chlorofluorocarbon propellants", "chloroform", "halogenated salicylanilides", "hexachlorophene", "mercury compounds", "methylene chloride", "prohibited cattle materials", "zirconium-containing complexes"],
    "eu_annex_ii": ["hydroquinone", "methyldibromo glutaronitrile", "lyral", "atranol", "chloroatranol"]
}

# Known conflicting pairs of active ingredients that may cause irritation when used together
CONFLICTING_PAIRS = [
    ({"retinol", "vitamin c"}, "Using Retinol and Vitamin C together can cause significant skin irritation. Consider using Vitamin C in the morning and Retinol at night."),
    ({"retinol", "aha"}, "Combining Retinol with AHAs (like Glycolic Acid) increases the risk of peeling and severe redness."),
    ({"retinol", "bha"}, "Combining Retinol with BHAs (like Salicylic Acid) can excessively dry out the skin."),
    ({"benzoyl peroxide", "retinol"}, "Benzoyl Peroxide can deactivate Retinol and cause severe dryness. Do not layer these ingredients."),
    ({"niacinamide", "vitamin c"}, "While not as dangerous as previously thought, layering high concentrations of both can cause flushing in sensitive skin.")
]

# Normalizing aliases
INGREDIENT_ALIASES = {
    "ascorbic acid": "vitamin c",
    "l-ascorbic acid": "vitamin c",
    "salicylic acid": "bha",
    "glycolic acid": "aha",
    "lactic acid": "aha"
}

def _normalize(ingredient: str) -> str:
    """Normalize ingredient name for matching."""
    norm = ingredient.lower().strip()
    return INGREDIENT_ALIASES.get(norm, norm)

def check_regulatory_compliance(ingredients: List[str]) -> List[Dict[str, str]]:
    """Check if any of the ingredients are banned in major regulatory markets."""
    violations = []
    for raw_ing in ingredients:
        ing = _normalize(raw_ing)
        # Check FDA
        if any(banned in ing for banned in BANNED_INGREDIENTS["fda"]):
            violations.append({"ingredient": raw_ing, "regulation": "FDA", "reason": "Banned or restricted by the FDA."})
        # Check EU
        if any(banned in ing for banned in BANNED_INGREDIENTS["eu_annex_ii"]):
            violations.append({"ingredient": raw_ing, "regulation": "EU Annex II", "reason": "Prohibited in cosmetic products in the EU."})
    return violations

def check_conflicts(ingredients: List[str]) -> List[Dict[str, Any]]:
    """Check for known ingredient conflicts in a formulation or routine."""
    conflicts = []
    normalized_ingredients = {_normalize(i) for i in ingredients}
    
    for pair, warning in CONFLICTING_PAIRS:
        # If both items in the conflict pair are present in the provided ingredients
        if pair.issubset(normalized_ingredients):
            conflicts.append({
                "conflict_pair": list(pair),
                "warning": warning
            })
            
    return conflicts

def analyze_formulation(ingredients: List[str]) -> Dict[str, Any]:
    """Run all rules on a list of ingredients and return a structured report."""
    regulatory_violations = check_regulatory_compliance(ingredients)
    ingredient_conflicts = check_conflicts(ingredients)
    
    is_compliant = len(regulatory_violations) == 0
    
    return {
        "is_compliant": is_compliant,
        "regulatory_violations": regulatory_violations,
        "ingredient_conflicts": ingredient_conflicts,
        "risk_level": "High" if not is_compliant else ("Caution" if ingredient_conflicts else "Low")
    }


def analyze_routine_stacking(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates multi-product routine layering and cross-product chemical interference.
    Accepts a list of products: [{'name': 'Product 1', 'ingredients': ['retinol', ...]}]
    """
    cross_conflicts = []
    all_actives = {}
    total_violations = []

    # Map each ingredient to the product it came from
    for p_idx, prod in enumerate(products):
        p_name = prod.get("name") or f"Product #{p_idx + 1}"
        p_ings = prod.get("ingredients") or []
        
        # Check regulatory compliance per product
        prod_violations = check_regulatory_compliance(p_ings)
        if prod_violations:
            total_violations.extend([{**v, "product": p_name} for v in prod_violations])
            
        for raw_ing in p_ings:
            norm = _normalize(raw_ing)
            if norm not in all_actives:
                all_actives[norm] = []
            all_actives[norm].append({"product": p_name, "raw": raw_ing})

    # Detect cross-product pairwise clashes
    present_normalized = set(all_actives.keys())
    for pair, warning in CONFLICTING_PAIRS:
        if pair.issubset(present_normalized):
            pair_list = list(pair)
            prod_a = all_actives[pair_list[0]][0]["product"]
            prod_b = all_actives[pair_list[1]][0]["product"]
            
            # If from different products, it is a cross-product layering risk!
            is_cross = prod_a != prod_b
            cross_conflicts.append({
                "conflict_pair": pair_list,
                "product_a": prod_a,
                "product_b": prod_b,
                "is_cross_product": is_cross,
                "warning": warning,
                "severity": "CRITICAL" if "deactivate" in warning.lower() or "severe" in warning.lower() else "MODERATE"
            })

    # Active Concentration Stacking alerts
    stacking_alerts = []
    for active_key, instances in all_actives.items():
        if len(instances) > 1 and active_key in ["aha", "bha", "vitamin c", "retinol", "niacinamide", "glycolic acid", "salicylic acid"]:
            product_list = [inst["product"] for inst in instances]
            stacking_alerts.append({
                "active": active_key.title(),
                "products_involved": product_list,
                "warning": f"Cumulative dose of {active_key.upper()} repeated across {len(instances)} products ({', '.join(product_list)}). High risk of barrier compromise and transepidermal water loss (TEWL)."
            })

    # Routine Safety Score calculation
    base_score = 100
    base_score -= len(total_violations) * 30
    base_score -= len(cross_conflicts) * 15
    base_score -= len(stacking_alerts) * 10
    routine_score = max(10, min(100, base_score))

    return {
        "products_evaluated": len(products),
        "routine_safety_score": routine_score,
        "is_safe_to_layer": len(cross_conflicts) == 0 and len(total_violations) == 0,
        "cross_product_conflicts": cross_conflicts,
        "stacking_overdose_alerts": stacking_alerts,
        "regulatory_violations": total_violations
    }
