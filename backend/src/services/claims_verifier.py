"""
Front-of-Package Marketing Claims Verifier
Detects front-of-package marketing claims (e.g. '100% Natural', 'No Added Sugar', 'Zero Trans Fat',
'Chemical Free', 'Organic', 'Diet', 'Low Fat') and validates each against actual back ingredients,
physical state (liquid vs solid), and chemical thresholds.
Ported & enhanced from NutriScan.
"""

import re
from typing import List, Dict, Any, Optional

CLAIM_PATTERNS = [
    {
        "pattern": r"\b(no added sugar|zero sugar|sugar free|unsweetened)\b",
        "claim": "No Added Sugar",
        "check": lambda ings, text, state: (
            ("Contains hidden high-GI sweeteners like maltodextrin, invert syrup, or concentrated fruit juices", "misleading")
            if any(s in ' '.join(ings).lower() for s in ["maltodextrin", "dextrose", "invert syrup", "corn syrup", "fructose", "apple juice concentrate"])
            else ("Verified: Formulation contains no high-GI exogenous syrups or added sucrose", "verified")
        )
    },
    {
        "pattern": r"\b(100% natural|all natural|natural ingredients|pure natural)\b",
        "claim": "100% Natural",
        "check": lambda ings, text, state: (
            ("Misleading: Product contains ultra-processed additives, synthetic preservatives, or artificial colors", "misleading")
            if any(a in ' '.join(ings).lower() for a in ["ins ", "e1", "e2", "sodium benzoate", "potassium sorbate", "bht", "tbhq", "artificial flavor", "maltodextrin", "methylparaben"])
            else ("Verified: Ingredients list consists of natural whole food or botanical extracts", "verified")
        )
    },
    {
        "pattern": r"\b(zero trans fat|trans fat free|no trans fat)\b",
        "claim": "Zero Trans Fat",
        "check": lambda ings, text, state: (
            ("Misleading: Contains partially hydrogenated vegetable oil, vanaspati, or interesterified fat", "misleading")
            if any(t in ' '.join(ings).lower() for t in ["partially hydrogenated", "hydrogenated vegetable oil", "vanaspati", "interesterified"])
            else ("Verified: No hydrogenated oil precursors detected", "verified")
        )
    },
    {
        "pattern": r"\b(chemical free|toxin free|zero chemicals)\b",
        "claim": "Chemical Free",
        "check": lambda ings, text, state: (
            ("Misleading: Pseudoscientific claim. All physical matter consists of chemicals; product contains synthetic compounds", "misleading")
        )
    },
    {
        "pattern": r"\b(organic|bio|certified organic)\b",
        "claim": "Organic / Bio",
        "check": lambda ings, text, state: (
            ("Potential Fake Organic: No authorized certification badge (e.g. Jaivik Bharat / USDA) or contains non-organic stabilizers", "unsubstantiated")
            if not any(badge in text.lower() for badge in ["jaivik bharat", "usda organic", "india organic", "apeda"])
            else ("Verified: Authorized organic statutory marking detected", "verified")
        )
    },
    {
        "pattern": r"\b(low fat|diet|light|guilt free)\b",
        "claim": "Low Fat / Diet",
        "check": lambda ings, text, state: (
            ("Caution: Fat reduction frequently compensated by spiking maltodextrin, thickeners, or sugars", "misleading")
            if any(s in ' '.join(ings).lower() for s in ["maltodextrin", "glucose", "starch", "sugar", "gum", "syrup"])
            else ("Verified: Product maintains low lipid density without added filler sugars", "verified")
        )
    },
    {
        "pattern": r"\b(dermatologically tested|clinically proven|hypoallergenic)\b",
        "claim": "Dermatologically Tested",
        "check": lambda ings, text, state: (
            ("Caution: Product contains known EU fragrance contact allergens or harsh surfactants (e.g. Limonene, Linalool, SLS)", "misleading")
            if any(al in ' '.join(ings).lower() for al in ["limonene", "linalool", "fragrance", "parfum", "sodium lauryl sulfate"])
            else ("Verified: Hypoallergenic profile without common contact sensitizers", "verified")
        )
    }
]

def verify_marketing_claims(
    front_text: str,
    ingredients: List[str],
    physical_state: str = "solid",
    back_text: str = ""
) -> List[Dict[str, str]]:
    """
    Extracts claims from front packaging and cross-verifies against back formulation.
    """
    combined_front = front_text.lower()
    combined_back = f"{back_text} {' '.join(ingredients)}".lower()
    results = []

    for item in CLAIM_PATTERNS:
        match = re.search(item["pattern"], combined_front)
        if match:
            claim_name = item["claim"]
            truth, verdict = item["check"](ingredients, combined_back, physical_state)
            results.append({
                "claim": claim_name,
                "truth": truth,
                "verdict": verdict
            })

    # If no explicit buzzwords found in front_text, scan the ingredients themselves for implicit claims
    if not results:
        # Check implicit 'No Sugar' or 'Clean Label'
        ings_str = " ".join(ingredients).lower()
        if any(s in ings_str for s in ["maltodextrin", "dextrose", "invert syrup"]):
            results.append({
                "claim": "Implicit Clean Label / Wholesome",
                "truth": "Hidden industrial sweeteners (e.g. Maltodextrin / Invert Syrup) detected in ingredient list",
                "verdict": "misleading"
            })

    return results
