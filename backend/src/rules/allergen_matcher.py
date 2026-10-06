"""
Deterministic Word-Boundary Allergen Matcher
Prevents false-positive substring matches (e.g. 'coconut' triggering 'nut', 'almond' in 'tourmaline')
by compiling strict regex word boundaries tolerant of plural forms: \\bkeyword(s)?\\b.
Ported from high-assurance patterns in Smart-Ingredient-Analyzer.
"""

import re
from typing import List, Dict, Any, Tuple

# Standard EU 26 fragrance allergens & cosmetic triggers
COSMETIC_ALLERGEN_TAXONOMY: Dict[str, List[str]] = {
    "Fragrance / Perfume": [
        "fragrance", "parfum", "aroma", "flavor", "flavour"
    ],
    "Linalool": ["linalool"],
    "Limonene": ["limonene", "d-limonene"],
    "Geraniol": ["geraniol"],
    "Citronellol": ["citronellol"],
    "Eugenol": ["eugenol", "isoeugenol"],
    "Coumarin": ["coumarin"],
    "Benzyl Alcohol": ["benzyl alcohol"],
    "Benzyl Salicylate": ["benzyl salicylate"],
    "Cinnamal": ["cinnamal", "cinnamaldehyde", "amyl cinnamal", "hexyl cinnamal"],
    "Citral": ["citral"],
    "Oakmoss / Treemoss": ["evernia prunastri", "evernia furfuracea", "oakmoss", "treemoss"],
    "Farnesol": ["farnesol"],
    "Anise Alcohol": ["anise alcohol", "anisyl alcohol"],
    "Methylisothiazolinone (MIT / CMIT)": [
        "methylisothiazolinone", "methylchloroisothiazolinone", "kathon"
    ],
    "Formaldehyde Releaser": [
        "dmdm hydantoin", "imidazolidinyl urea", "diazolidinyl urea", "quaternium-15", "bronopol"
    ],
    "Parabens": [
        "methylparaben", "propylparaben", "butylparaben", "ethylparaben", "isobutylparaben"
    ],
    "Sulfates (SLS / SLES)": [
        "sodium lauryl sulfate", "sodium laureth sulfate", "ammonium lauryl sulfate"
    ],
    "Nut Oil / Almond / Peanut": [
        "prunus amygdalus", "almond oil", "peanut oil", "arachis hypogaea", "macadamia", "walnut"
    ],
    "Soy / Wheat / Gluten": [
        "hydrolyzed wheat protein", "glycine max", "soy protein", "gluten", "triticum vulgare"
    ]
}

def escape_regex(text: str) -> str:
    """Escapes special regex characters."""
    return re.escape(text.strip())

class AllergenDetector:
    def __init__(self):
        # Precompile standard cosmetic allergen matchers on word boundaries
        self.compiled_taxonomy: List[Tuple[str, List[re.Pattern]]] = []
        for category, keywords in COSMETIC_ALLERGEN_TAXONOMY.items():
            patterns = [
                re.compile(rf"\b{escape_regex(kw)}s?\b", re.IGNORECASE)
                for kw in keywords if kw.strip()
            ]
            self.compiled_taxonomy.append((category, patterns))

    def detect_allergens(
        self,
        ingredient_list: List[str],
        user_allergies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Scans ingredient names using strict word boundaries.
        Checks both the EU cosmetic taxonomy and the user's custom allergy profile.
        """
        user_allergies = user_allergies or []
        user_patterns = []
        for ua in user_allergies:
            ua_clean = ua.strip()
            if ua_clean:
                user_patterns.append((
                    ua_clean,
                    re.compile(rf"\b{escape_regex(ua_clean)}s?\b", re.IGNORECASE)
                ))

        detected_alerts = []
        user_matches = []

        for ing in ingredient_list:
            ing_clean = ing.strip()
            if not ing_clean:
                continue

            # 1. Match against user's personal allergies
            for allergy_name, pat in user_patterns:
                if pat.search(ing_clean):
                    user_matches.append({
                        "ingredient": ing_clean,
                        "matched_allergy": allergy_name,
                        "type": "USER_SPECIFIED_ALLERGEN",
                        "severity": "HIGH_AVOID"
                    })

            # 2. Match against authoritative cosmetic taxonomy
            for cat, patterns in self.compiled_taxonomy:
                for p in patterns:
                    if p.search(ing_clean):
                        detected_alerts.append({
                            "ingredient": ing_clean,
                            "category": cat,
                            "type": "REGULATORY_FRAGRANCE_ALLERGEN",
                            "severity": "MODERATE_CAUTION"
                        })
                        break

        return {
            "has_critical_allergens": len(user_matches) > 0,
            "user_allergen_violations": user_matches,
            "general_allergen_alerts": detected_alerts,
            "total_flagged": len(user_matches) + len(detected_alerts)
        }

# Global singleton detector
allergen_detector = AllergenDetector()
