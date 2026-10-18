"""
Plain-English Chemical Translation Service for LabelX
Translates cryptic chemical additives (e.g. INS 211, maltodextrin, TBHQ, BHA, carrageenan, parabens)
into simple, transparent layman explanations for consumers, categorizing ingredients into:
- Harmful / High-Risk
- Beneficial / Nutritious
- Neutral / Functional
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
import re

class TranslatedIngredient(BaseModel):
    name: str
    original_code: Optional[str] = None
    category: str  # 'harmful', 'beneficial', 'neutral'
    common_name: str
    simple_explanation: str
    potential_risks: Optional[str] = None
    health_benefits: Optional[str] = None

# Known chemical dictionary for instant deterministic translation
CHEMICAL_LEXICON: Dict[str, dict] = {
    "ins 211": {
        "common_name": "Sodium Benzoate (Synthetic Preservative)",
        "category": "harmful",
        "simple_explanation": "A chemical preservative used to stop mold and bacteria growth in acidic foods and drinks.",
        "risks": "Can react with Vitamin C (Ascorbic Acid) to form benzene, a known carcinogen. May trigger hyperactivity in children."
    },
    "e211": {
        "common_name": "Sodium Benzoate (Synthetic Preservative)",
        "category": "harmful",
        "simple_explanation": "A chemical preservative used to prevent mold and yeast in beverages, sauces, and pickles.",
        "risks": "May form trace benzene when combined with Vitamin C; linked to hyperactivity in children."
    },
    "ins 319": {
        "common_name": "TBHQ (Tertiary Butylhydroquinone)",
        "category": "harmful",
        "simple_explanation": "A synthetic antioxidant petroleum derivative added to vegetable oils to prevent them from turning rancid.",
        "risks": "High doses have been associated with immune system changes and biochemical cellular stress."
    },
    "tbhq": {
        "common_name": "TBHQ (Petroleum-Derived Preservative)",
        "category": "harmful",
        "simple_explanation": "A petroleum byproduct used to extend shelf-life of processed chips, instant noodles, and fried foods.",
        "risks": "Associated with potential cellular stress and immune system disruptions if consumed frequently."
    },
    "e320": {
        "common_name": "BHA (Butylated Hydroxyanisole)",
        "category": "harmful",
        "simple_explanation": "A synthetic preservative added to fats and oils to delay oxidation.",
        "risks": "Classified by IARC as a possible human carcinogen and known endocrine disruptor in animal studies."
    },
    "bha": {
        "common_name": "BHA (Synthetic Antioxidant)",
        "category": "harmful",
        "simple_explanation": "A chemical antioxidant used to keep chips, cereals, and oils fresh.",
        "risks": "Antioxidant with suspected hormonal interference and carcinogenicity concerns."
    },
    "e321": {
        "common_name": "BHT (Butylated Hydroxytoluene)",
        "category": "harmful",
        "simple_explanation": "A synthetic preservative related to BHA used in snacks and cosmetic packaging.",
        "risks": "Potential liver and kidney strain with chronic high intake; endocrine disruption warnings."
    },
    "bht": {
        "common_name": "BHT (Chemical Preservative)",
        "category": "harmful",
        "simple_explanation": "Petroleum-derived preservative preventing oils from spoiling.",
        "risks": "Endocrine disruptor alert; banned or restricted in several European countries."
    },
    "e102": {
        "common_name": "Tartrazine (Yellow #5 Dye)",
        "category": "harmful",
        "simple_explanation": "A synthetic petroleum-derived azo dye producing bright yellow/orange colors.",
        "risks": "Known to trigger allergic hives, asthma, and attention disorders/hyperactivity in sensitive children."
    },
    "e110": {
        "common_name": "Sunset Yellow FCF (Orange #6 Dye)",
        "category": "harmful",
        "simple_explanation": "A synthetic coal-tar dye providing intense orange hues.",
        "risks": "Part of the 'Southampton Six' colors linked to hyperactivity in kids; potential allergen."
    },
    "e171": {
        "common_name": "Titanium Dioxide (White Color Pigment)",
        "category": "harmful",
        "simple_explanation": "An inorganic metal pigment used to make icings, creams, and sunscreens intensely white.",
        "risks": "Banned by EFSA in Europe and restricted by FSSAI due to genotoxicity concerns of nanoparticles."
    },
    "maltodextrin": {
        "common_name": "Maltodextrin (Refined Starch Thickener)",
        "category": "harmful",
        "simple_explanation": "A heavily processed white powder derived from corn, rice, or potato starch.",
        "risks": "Has a glycemic index (105-136) higher than table sugar, causing rapid blood glucose spikes and insulin surges."
    },
    "high fructose corn syrup": {
        "common_name": "HFCS (Liquid Sugar Derivative)",
        "category": "harmful",
        "simple_explanation": "Liquid sweetener made from corn starch through enzymatic processing.",
        "risks": "Strongly linked to non-alcoholic fatty liver disease, visceral fat buildup, and insulin resistance."
    },
    "palm oil": {
        "common_name": "Fractionated Palm Oil / Palmolein",
        "category": "neutral",
        "simple_explanation": "High-melting vegetable oil widely used for cheap industrial frying and texture.",
        "risks": "High in palmitic saturated fat; linked to atherogenic LDL cholesterol increases if consumed daily."
    },
    "carrageenan": {
        "common_name": "Carrageenan (Seaweed Extract Thickener, E407)",
        "category": "harmful",
        "simple_explanation": "An additive extracted from red edible seaweeds used to thicken dairy, milk substitutes, and yogurt.",
        "risks": "Frequently linked to gastrointestinal inflammation, bloating, and leaky gut symptoms in clinical trials."
    },
    "aspartame": {
        "common_name": "Aspartame (Synthetic Sweetener, E951)",
        "category": "harmful",
        "simple_explanation": "Artificial intense sweetener 200 times sweeter than sucrose.",
        "risks": "Classified as possibly carcinogenic (Group 2B) by WHO/IARC; dangerous for individuals with PKU (phenylketonuria)."
    },
    "curcumin": {
        "common_name": "Curcumin (Turmeric Extract, E100)",
        "category": "beneficial",
        "simple_explanation": "The active polyphenol naturally extracted from turmeric root.",
        "benefits": "Potent anti-inflammatory and antioxidant properties supporting cellular resilience."
    },
    "e100": {
        "common_name": "Curcumin (Natural Yellow, E100)",
        "category": "beneficial",
        "simple_explanation": "Natural turmeric pigment.",
        "benefits": "Natural cellular antioxidant and digestive aid."
    },
    "ascorbic acid": {
        "common_name": "Vitamin C (Natural Antioxidant, E300)",
        "category": "beneficial",
        "simple_explanation": "Pure Vitamin C, an essential micronutrient and natural antioxidant.",
        "benefits": "Neutralizes free radicals, boosts collagen synthesis, and protects nutrients from oxidation."
    },
    "e300": {
        "common_name": "Ascorbic Acid (Vitamin C, E300)",
        "category": "beneficial",
        "simple_explanation": "Vitamin C.",
        "benefits": "Essential water-soluble antioxidant protecting against cell damage."
    },
    "tocopherol": {
        "common_name": "Vitamin E (Natural Lipid Antioxidant, E306)",
        "category": "beneficial",
        "simple_explanation": "Natural Vitamin E oil extracted from plant seeds.",
        "benefits": "Protects cell membranes and fatty acids from rancidity; nourishes skin and vascular tissues."
    },
    "e306": {
        "common_name": "Natural Tocopherols (Vitamin E, E306)",
        "category": "beneficial",
        "simple_explanation": "Plant-derived Vitamin E.",
        "benefits": "High physiological antioxidant value."
    },
    "guar gum": {
        "common_name": "Guar Gum (Natural Bean Fiber, E412)",
        "category": "neutral",
        "simple_explanation": "Soluble dietary fiber extracted from Indian guar beans used for thickening sauces and ice creams.",
        "benefits": "Acts as a prebiotic fiber supporting healthy gut microbiome."
    },
    "xanthan gum": {
        "common_name": "Xanthan Gum (Fermented Corn Sugar, E415)",
        "category": "neutral",
        "simple_explanation": "A natural polysaccharide produced by fermenting glucose with Xanthomonas campestris bacteria.",
        "benefits": "Gluten-free stabilizer that provides smooth texture with zero caloric absorption."
    },
    "soy lecithin": {
        "common_name": "Soy Lecithin (Natural Emulsifier, E322)",
        "category": "neutral",
        "simple_explanation": "A natural fatty substance extracted from soybeans that prevents oil and water from separating in chocolate and bakery goods.",
        "risks": "Allergen warning for people allergic to soy."
    },
    "citric acid": {
        "common_name": "Citric Acid (Acidity Regulator, E330)",
        "category": "neutral",
        "simple_explanation": "Natural organic acid found in citrus fruits, used to give tartness and prevent spoilage.",
        "benefits": "Non-toxic food acid safe for general consumption."
    }
}

class ChemicalTranslator:
    """Service that transforms cryptic ingredients into plain-English cards."""

    @staticmethod
    def translate_ingredient(raw_name: str) -> TranslatedIngredient:
        name_clean = raw_name.lower().strip()
        name_no_punct = re.sub(r'[\(\)\d\.\%]', '', name_clean).strip()

        # Check direct or code match
        match_key = None
        for key in CHEMICAL_LEXICON:
            if key in name_clean or key in name_no_punct:
                match_key = key
                break

        # Check E/INS code regex match
        e_match = re.search(r'\b(e\d{3,4}[a-z]?|ins\s*\d{3,4}[a-z]?)\b', name_clean)
        if not match_key and e_match:
            code = e_match.group(1).replace(" ", "").lower()
            code_e = code.replace("ins", "e")
            code_ins = code.replace("e", "ins ")
            if code in CHEMICAL_LEXICON: match_key = code
            elif code_e in CHEMICAL_LEXICON: match_key = code_e
            elif code_ins in CHEMICAL_LEXICON: match_key = code_ins

        if match_key:
            data = CHEMICAL_LEXICON[match_key]
            return TranslatedIngredient(
                name=raw_name,
                original_code=e_match.group(1).upper() if e_match else None,
                category=data["category"],
                common_name=data["common_name"],
                simple_explanation=data["simple_explanation"],
                potential_risks=data.get("risks"),
                health_benefits=data.get("benefits")
            )

        # Heuristic fallback for uncataloged chemicals
        is_chemical = bool(re.search(r'(benzoate|sorbate|propionate|bha|bht|paraben|sulfate|glycol|acetate|fcf|tartrazine|artificial|synthetic)', name_clean))
        is_natural = bool(re.search(r'(extract|oil|pure|juice|leaf|seed|fruit|honey|aloe|water|aqua|flower)', name_clean))

        if is_chemical:
            cat = "harmful"
            common = f"{raw_name} (Synthetic Chemical Compound)"
            exp = "A manufactured chemical compound used as a preservative, colorant, or synthetic stabilizer."
            risk = "Synthetic additive; monitor cumulative daily intake to avoid digestive or allergenic irritation."
            bene = None
        elif is_natural:
            cat = "beneficial"
            common = f"{raw_name} (Plant / Natural Extract)"
            exp = "A natural whole-food or plant-derived ingredient."
            risk = None
            bene = "Provides natural phytochemicals and nutritional cofactors."
        else:
            cat = "neutral"
            common = f"{raw_name} (Standard Food Constituent)"
            exp = "A common bulk food ingredient or structural base."
            risk = None
            bene = None

        return TranslatedIngredient(
            name=raw_name,
            original_code=e_match.group(1).upper() if e_match else None,
            category=cat,
            common_name=common,
            simple_explanation=exp,
            potential_risks=risk,
            health_benefits=bene
        )

    @classmethod
    def translate_all(cls, ingredients: List[str]) -> Dict[str, List[TranslatedIngredient]]:
        results = {"harmful": [], "beneficial": [], "neutral": []}
        for ing in ingredients:
            t = cls.translate_ingredient(ing)
            results[t.category].append(t)
        return results

chemical_translator = ChemicalTranslator()
