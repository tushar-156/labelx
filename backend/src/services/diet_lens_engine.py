r"""
Diet-Lens Stanford Project Deterministic Verdict Engine for LabelX
Adapted from C:\ClientBTP\Diet-Lens-Stanford-Project-\verdict_checker.py

Key Principles:
1. 100% Deterministic Python Rule Engine - ZERO AI randomness or hallucination in the final verdict.
2. Checks user-selected dietary conditions against strict forbidden ingredient keyword matrices.
3. Special FDA 21 CFR § 101.61 regex parser for Low-Sodium verification (<= 140mg/serving).
4. Strict vegetarian egg & non-veg derivative unmasker (albumen, ovalbumin, lysozyme, carmine E120, shellac E904, rennet).
"""

import re
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

# ── FORBIDDEN INGREDIENT LISTS (From Diet-Lens Stanford Project) ───────

CONDITION_RULES = {
    "Diabetic": {
        "label": "Diabetic",
        "description": "Excludes added sugars, high-GI syrups, and refined glycemic sweeteners.",
        "forbidden": [
            "sugar", "added sugar", "total sugar", "cane sugar",
            "brown sugar", "raw sugar", "powdered sugar",
            "corn syrup", "high fructose corn syrup", "hfcs",
            "maltodextrin", "dextrose", "fructose", "glucose",
            "sucrose", "barley malt", "malt syrup",
            "honey", "agave", "molasses", "maple syrup",
            "fruit juice concentrate", "invert sugar",
            "turbinado", "treacle", "golden syrup",
            "rice syrup", "coconut sugar", "date sugar"
        ]
    },

    "Gluten Free": {
        "label": "Gluten Free",
        "description": "Excludes wheat, barley, rye, and cross-reactive gluten grains.",
        "forbidden": [
            "wheat", "wheat flour", "wheat starch",
            "whole wheat", "wheat bran", "wheat germ",
            "barley", "barley malt", "barley flour",
            "rye", "rye flour",
            "malt", "malt extract", "malt vinegar", "malt flavoring",
            "brewer's yeast", "brewers yeast",
            "semolina", "spelt", "kamut", "triticale",
            "durum", "einkorn", "emmer", "farro"
        ]
    },

    "Nut Allergy": {
        "label": "Nut Allergy",
        "description": "Excludes peanuts, groundnuts, and all botanical tree nuts.",
        "forbidden": [
            "peanut", "peanuts", "peanut oil", "peanut butter",
            "peanut flour", "groundnut", "groundnuts",
            "almond", "almonds", "almond flour", "almond oil",
            "almond extract", "almond milk",
            "cashew", "cashews", "cashew oil",
            "walnut", "chopped walnuts", "walnuts", "walnut oil",
            "pecan", "pecans",
            "pistachio", "pistachios",
            "macadamia", "macadamia nut",
            "hazelnut", "hazelnuts", "hazelnut oil",
            "brazil nut", "brazil nuts",
            "pine nut", "pine nuts", "pinon",
            "nut oil", "nut extract", "mixed nuts",
            "tree nut", "tree nuts", "nut butter"
        ]
    },

    "Dairy Free": {
        "label": "Dairy Free",
        "description": "Excludes mammalian milk, whey, caseins, lactose, and butterfat.",
        "forbidden": [
            "milk", "whole milk", "skim milk", "low fat milk",
            "milk solids", "milk powder", "dried milk",
            "butter", "butter oil", "butterfat",
            "cream", "heavy cream", "sour cream",
            "half and half", "buttermilk",
            "cheese", "cheddar", "mozzarella", "parmesan",
            "whey", "whey protein", "whey powder",
            "casein", "caseinate", "sodium caseinate",
            "lactose", "lactalbumin", "lactoglobulin",
            "ghee", "curd", "lassi", "yogurt",
            "ice cream", "milk fat", "dairy"
        ]
    },

    "Vegan": {
        "label": "Vegan",
        "description": "Zero animal products, slaughter byproducts, insects, dairy, or eggs.",
        "forbidden": [
            # Dairy
            "milk", "butter", "cream", "cheese",
            "whey", "casein", "lactose", "ghee", "dairy",
            # Eggs - NOT vegan
            "egg", "eggs", "whole egg", "egg white",
            "egg yolk", "egg powder", "dried egg",
            "egg solids", "albumen", "ovalbumin", "lysozyme",
            # Honey and bee products
            "honey", "beeswax", "royal jelly", "propolis",
            # Gelatin and collagen
            "gelatin", "gelatine", "collagen",
            # Dyes and shellac
            "carmine", "cochineal", "e120", "shellac", "e904",
            # Animal fats & enzymes
            "lard", "tallow", "suet", "lanolin", "isinglass", "rennet",
            # Meat and seafood
            "chicken", "beef", "pork", "lamb", "turkey",
            "fish", "salmon", "tuna", "anchovies",
            "shrimp", "oyster", "meat", "bone broth"
        ]
    },

    "Vegetarian": {
        "label": "Vegetarian",
        "description": "Strict vegetarian standard: zero meat, seafood, gelatin, or egg derivatives.",
        "forbidden": [
            # Eggs & derivatives
            "egg", "eggs", "whole egg", "egg white",
            "egg yolk", "egg powder", "dried egg",
            "egg solids", "albumen", "ovalbumin",
            "lysozyme", "mayonnaise",
            # Meat and poultry
            "beef", "chicken", "pork", "lamb",
            "turkey", "duck", "goose", "veal",
            "meat", "meat extract", "meat powder",
            "chicken broth", "beef broth", "bone broth",
            "bacon", "ham", "sausage",
            "lard", "tallow", "suet",
            "chicken fat", "beef fat", "pork fat",
            # Seafood
            "fish", "salmon", "tuna", "cod", "tilapia",
            "shrimp", "prawn", "crab", "lobster",
            "oyster", "squid", "octopus", "clam",
            "anchovies", "sardine", "mackerel",
            "fish sauce", "fish oil", "fish extract",
            "oyster sauce", "shrimp paste", "scallop", "mussel",
            "fillet", "fillets", "haddock", "pollock",
            # Animal slaughter derivatives
            "gelatin", "gelatine", "collagen",
            "carmine", "cochineal", "e120",
            "shellac", "isinglass", "rennet",
            "animal fat", "animal shortening"
        ]
    },

    "No HFCS": {
        "label": "No HFCS",
        "description": "Excludes high-fructose corn syrup and modified fructose corn sweeteners.",
        "forbidden": [
            "high fructose corn syrup", "hfcs",
            "corn syrup high fructose",
            "fructose corn syrup",
            "high-fructose corn syrup"
        ]
    },

    "Low Sodium": {
        "label": "Low Sodium",
        "description": "Enforces FDA 21 CFR § 101.61 threshold (<= 140mg sodium per serving).",
        "forbidden": [],
        "special": "sodium_check"
    }
}

class ConditionCheckResult(BaseModel):
    condition: str
    status: str  # 'PASS', 'FAIL', 'UNKNOWN'
    found: List[str]
    message: str

class DietLensVerdictReport(BaseModel):
    overall_safe: bool
    status_label: str  # 'SAFE FOR YOU' or 'NOT SAFE FOR YOU'
    conditions_checked: List[ConditionCheckResult]
    failed_conditions: List[str]
    passed_conditions: List[str]
    reasons: List[str]
    verdict_text: str

def check_sodium(text_lower: str, sodium_amount: Optional[float] = None) -> ConditionCheckResult:
    """Evaluates sodium against the FDA 21 CFR § 101.61 Low Sodium threshold (<= 140mg/serving)."""
    limit = 140.0

    if sodium_amount is not None:
        if sodium_amount > limit:
            return ConditionCheckResult(
                condition="Low Sodium",
                status="FAIL",
                found=[f"Sodium {sodium_amount}mg"],
                message=f"Sodium is {sodium_amount}mg (exceeds FDA 140mg low-sodium limit per serving)"
            )
        else:
            return ConditionCheckResult(
                condition="Low Sodium",
                status="PASS",
                found=[],
                message=f"Sodium is {sodium_amount}mg (satisfies FDA low-sodium threshold <= 140mg)"
            )

    # Regex extraction from raw label text
    patterns = [
        r'sodium[:\s]+(\d+(?:\.\d+)?)\s*mg',
        r'sodium content[:\s]+(\d+(?:\.\d+)?)\s*mg',
        r'(\d+(?:\.\d+)?)\s*mg\s*sodium',
        r'salt[:\s]+(\d+(?:\.\d+)?)\s*g'
    ]

    for p in patterns:
        m = re.search(p, text_lower)
        if m:
            val = float(m.group(1))
            if "salt" in p:
                val = val * 400.0  # Approx 400mg sodium per 1g table salt
            if val > limit:
                return ConditionCheckResult(
                    condition="Low Sodium",
                    status="FAIL",
                    found=[f"Sodium {val:.0f}mg"],
                    message=f"Sodium is {val:.0f}mg (exceeds FDA low-sodium limit of {limit:.0f}mg/serving)"
                )
            else:
                return ConditionCheckResult(
                    condition="Low Sodium",
                    status="PASS",
                    found=[],
                    message=f"Sodium is {val:.0f}mg (meets FDA low-sodium limit <= {limit:.0f}mg/serving)"
                )

    return ConditionCheckResult(
        condition="Low Sodium",
        status="UNKNOWN",
        found=[],
        message="Sodium amount not explicitly declared on label text"
    )

def check_diet_lens_verdict(
    ingredients: List[str],
    raw_text: str = "",
    user_conditions: Optional[List[str]] = None,
    sodium_amount: Optional[float] = None
) -> DietLensVerdictReport:
    """
    100% Deterministic Python Verdict Gatekeeper (Diet-Lens Stanford architecture).
    """
    if not user_conditions:
        # Default baseline conditions if none provided
        user_conditions = ["Vegetarian", "Diabetic", "Low Sodium"]

    # Normalize ingredient tokens and full text
    normalized_text = (raw_text + " " + " ".join(ingredients)).lower()
    clean_tokens = [i.strip().lower() for i in ingredients if i.strip()]

    conditions_checked: List[ConditionCheckResult] = []
    failed_conditions: List[str] = []
    passed_conditions: List[str] = []
    reasons: List[str] = []

    for cond_name in user_conditions:
        # Normalize condition names (e.g., 'diabetes' -> 'Diabetic', 'gluten' -> 'Gluten Free')
        canonical_name = cond_name.title()
        if canonical_name.lower() in ["diabetes", "diabetic"]:
            canonical_name = "Diabetic"
        elif canonical_name.lower() in ["gluten", "gluten free", "gluten-free"]:
            canonical_name = "Gluten Free"
        elif canonical_name.lower() in ["nuts", "nut", "nut allergy"]:
            canonical_name = "Nut Allergy"
        elif canonical_name.lower() in ["dairy", "dairy free", "lactose"]:
            canonical_name = "Dairy Free"
        elif canonical_name.lower() in ["veg", "vegetarian"]:
            canonical_name = "Vegetarian"
        elif canonical_name.lower() in ["vegan"]:
            canonical_name = "Vegan"
        elif canonical_name.lower() in ["no hfcs", "hfcs"]:
            canonical_name = "No HFCS"
        elif canonical_name.lower() in ["low sodium", "sodium"]:
            canonical_name = "Low Sodium"

        if canonical_name not in CONDITION_RULES:
            continue

        rule = CONDITION_RULES[canonical_name]

        # 1. Special Sodium Check
        if rule.get("special") == "sodium_check":
            res = check_sodium(normalized_text, sodium_amount)
            conditions_checked.append(res)
            if res.status == "FAIL":
                failed_conditions.append(canonical_name)
                reasons.append(f"Sodium content violates {canonical_name} threshold ({res.message})")
            elif res.status == "PASS":
                passed_conditions.append(canonical_name)
            continue

        # 2. Strict Deterministic Keyword Matching
        found_matches = []
        forbidden_list = rule.get("forbidden", [])

        # Check in whole text as well as individual tokens
        for kw in forbidden_list:
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            # Look in normalized full text
            if re.search(pattern, normalized_text):
                found_matches.append(kw)

        if found_matches:
            # Deduplicate matches
            unique_found = list(dict.fromkeys(found_matches))
            msg = f"Forbidden ingredient detected: {', '.join(unique_found[:4])}"
            conditions_checked.append(ConditionCheckResult(
                condition=canonical_name,
                status="FAIL",
                found=unique_found,
                message=msg
            ))
            failed_conditions.append(canonical_name)
            for f in unique_found[:3]:
                reasons.append(f"Contains '{f}' which violates {canonical_name} requirements")
        else:
            conditions_checked.append(ConditionCheckResult(
                condition=canonical_name,
                status="PASS",
                found=[],
                message=f"No {canonical_name} forbidden ingredients detected"
            ))
            passed_conditions.append(canonical_name)

    is_overall_safe = len(failed_conditions) == 0

    # Build Stanford Verdict Text
    verdict_lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "        DIET-LENS PERSONAL VERDICT",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"OVERALL STATUS: {'SAFE FOR YOU' if is_overall_safe else 'NOT SAFE FOR YOU'}",
        "─" * 40,
        "CONDITIONS CHECKED:"
    ]
    for c in conditions_checked:
        symbol = "✅" if c.status == "PASS" else "❌" if c.status == "FAIL" else "⚠️"
        verdict_lines.append(f"  {symbol} {c.condition}: {c.status} ({c.message})")

    verdict_lines.append("─" * 40)
    verdict_lines.append("REASONS:")
    if reasons:
        for r in reasons:
            verdict_lines.append(f"  • {r}")
    else:
        verdict_lines.append("  All your evaluated dietary conditions passed with zero violations.")

    verdict_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return DietLensVerdictReport(
        overall_safe=is_overall_safe,
        status_label="SAFE FOR YOU" if is_overall_safe else "NOT SAFE FOR YOU",
        conditions_checked=conditions_checked,
        failed_conditions=failed_conditions,
        passed_conditions=passed_conditions,
        reasons=reasons,
        verdict_text="\n".join(verdict_lines)
    )

diet_lens_engine = check_diet_lens_verdict
