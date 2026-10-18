"""
NOVA Processing Classifier, Consumer Intent Detector & Nutritional Trade-Offs Engine for LabelX
Classifies industrial food processing levels into the international NOVA taxonomy:
  - Group 1: Unprocessed / Minimally Processed
  - Group 2: Processed Culinary Ingredients
  - Group 3: Processed Foods
  - Group 4: Ultra-Processed Food (UPF)

Also performs:
  - Consumer Intent Identification (Parent for kids, Diabetic/Sugar, Fitness/Protein, Sensitive Skin/Allergies)
  - Objective Nutritional Trade-Offs Analysis
  - Uncertainty & Data Gap Audit
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import re

class ConsumerIntentProfile(BaseModel):
    intent: str
    rationale: str
    suitability: str  # 'Highly Recommended', 'Acceptable with Moderation', 'Not Recommended'
    priority_nutrients: List[str]

class NovaAnalysis(BaseModel):
    group: int  # 1 to 4
    tier_name: str  # 'Unprocessed', 'Minimally Processed', 'Processed', 'Ultra-Processed'
    color: str  # green, emerald, amber, red
    description: str
    upf_markers: List[str] = []
    processing_indicators: List[str] = []

class NutritionalTradeOff(BaseModel):
    positive_aspects: List[str]
    negative_aspects: List[str]
    consumer_tradeoff_summary: str
    verdict: str  # 'Excellent', 'Good', 'Fair', 'Poor', 'Avoid'
    frequency_recommendation: str  # 'Daily Staple', '2-3 Times a Week', 'Occasional Treat', 'Rarely / Avoid'

class UncertaintyAudit(BaseModel):
    has_gaps: bool
    confidence_score: float  # 0.0 to 1.0
    flags: List[str]
    recommendation: str

class ComprehensiveIntelligenceReport(BaseModel):
    nova: NovaAnalysis
    intent: ConsumerIntentProfile
    tradeoffs: NutritionalTradeOff
    uncertainty: UncertaintyAudit

# UPF Markers from FAO and Monteiro et al. (NOVA System)
UPF_MARKERS = [
    "maltodextrin", "high fructose corn syrup", "corn syrup", "invert sugar",
    "hydrogenated oil", "partially hydrogenated", "interesterified", "palmolein",
    "soy protein isolate", "pea protein isolate", "whey protein concentrate", "caseinate",
    "modified starch", "dextrin", "polydextrose", "xanthan gum", "guar gum",
    "carrageenan", "cellulose gum", "carboxymethyl cellulose", "mono- and diglycerides",
    "polysorbate", "datem", "sodium stearoyl lactylate", "tbhq", "bha", "bht",
    "potassium sorbate", "sodium benzoate", "aspartame", "sucralose", "acesulfame",
    "saccharin", "erythritol", "xylitol", "monosodium glutamate", "msg",
    "disodium inosinate", "disodium guanylate", "artificial flavor", "flavor enhancer",
    "caramel color", "tartrazine", "sunset yellow", "allura red", "brilliant blue"
]

def classify_nova(ingredients: List[str], additives: Optional[List[dict]] = None) -> NovaAnalysis:
    """Classifies ingredient list into 1 of 4 NOVA tiers."""
    if not ingredients:
        return NovaAnalysis(
            group=1,
            tier_name="Unprocessed",
            color="emerald",
            description="Fresh whole foods or single unrefined ingredients.",
            upf_markers=[]
        )

    ing_text = " ".join(ingredients).lower()
    found_upf: List[str] = []

    for marker in UPF_MARKERS:
        if re.search(r'\b' + re.escape(marker) + r'\b', ing_text):
            found_upf.append(marker)

    # Check for E-codes or INS markers
    ecodes = re.findall(r'\b(e\d{3,4}[a-z]?|ins\s*\d{3,4}[a-z]?)\b', ing_text)
    if ecodes:
        for ec in ecodes:
            found_upf.append(ec.upper())

    # De-duplicate
    found_upf = list(dict.fromkeys(found_upf))

    # NOVA Classification Logic
    if len(found_upf) >= 2 or len(ingredients) > 12:
        return NovaAnalysis(
            group=4,
            tier_name="Ultra-Processed",
            color="red",
            description="Industrial formulations typically with 5+ ingredients, synthetic additives, flavorings, and emulsifiers rarely found in domestic kitchens.",
            upf_markers=found_upf,
            processing_indicators=["Industrial cosmetic additives", "High refining fraction", "Deconstructed food matrices"]
        )
    elif len(found_upf) == 1 or len(ingredients) > 5:
        return NovaAnalysis(
            group=3,
            tier_name="Processed",
            color="amber",
            description="Manufactured by combining whole foods with salt, sugar, oil, or preservatives to prolong durability and enhance sensory attributes.",
            upf_markers=found_upf,
            processing_indicators=["Added culinary preservation agents", "Canned or artisan manufactured"]
        )
    elif any(term in ing_text for term in ["salt", "sugar", "oil", "butter", "vinegar"]):
        return NovaAnalysis(
            group=2,
            tier_name="Processed Culinary Ingredients",
            color="amber",
            description="Substances obtained directly from Group 1 foods by physical pressing, refining, or milling.",
            upf_markers=[]
        )
    else:
        return NovaAnalysis(
            group=1,
            tier_name="Unprocessed or Minimally Processed",
            color="emerald",
            description="Natural parts of plants or animals subjected to cleaning, roasting, boiling, or fermentation without added fats, sugars, or salts.",
            upf_markers=[]
        )

def detect_consumer_intent(
    ingredients: List[str], 
    nutritional_claims: List[str], 
    category: str = "Food & Beverage",
    user_context: Optional[dict] = None
) -> ConsumerIntentProfile:
    """Infers the probable buyer's persona and evaluates formulation match."""
    claims_lower = [c.lower() for c in nutritional_claims]
    ing_lower = [i.lower() for i in ingredients]
    full_text = " ".join(claims_lower + ing_lower)

    # Detect Fitness / Protein intent
    if any(k in full_text for k in ["protein", "whey", "bcaa", "creatine", "muscle", "workout", "peanut butter"]):
        return ConsumerIntentProfile(
            intent="Athlete / Muscle Recovery & Fitness Tracking",
            rationale="Product formulation emphasizes protein density, amino acid enrichment, and macronutrient balance for physical performance.",
            suitability="Highly Recommended" if not any("high sugar" in c for c in claims_lower) else "Acceptable with Moderation",
            priority_nutrients=["Protein per serving", "Energy (kcal)", "Sugar ratio", "Branched-Chain Amino Acids"]
        )

    # Detect Child / Parental Care
    if any(k in full_text for k in ["kid", "baby", "infant", "junior", "snack", "tiffin", "biscuit", "choc", "candy", "gummy"]):
        is_safe = not any(c in full_text for c in ["tartrazine", "sunset yellow", "caffeine", "aspartame", "ins 211"])
        return ConsumerIntentProfile(
            intent="Parent Checking Child Nutrition & Toxicity",
            rationale="Evaluating safety for pediatric metabolism, hyperactive colorant risks (Southampton 6), and sugar spikes.",
            suitability="Highly Recommended" if is_safe else "Not Recommended",
            priority_nutrients=["Added Sugar", "Synthetic Azo Dyes (E102, E110)", "Dietary Fiber", "Chemical Preservatives"]
        )

    # Detect Diabetic / Sugar Management
    if any(k in full_text for k in ["sugar free", "zero sugar", "stevia", "keto", "diabetic", "low carb"]):
        has_maltodextrin = "maltodextrin" in full_text
        return ConsumerIntentProfile(
            intent="Glycemic & Diabetic Blood Glucose Monitoring",
            rationale="Monitoring net carbohydrates, sugar alcohol load, and rapid glycemic index spike triggers.",
            suitability="Not Recommended" if has_maltodextrin else "Highly Recommended",
            priority_nutrients=["Net Carbs", "Total Sugar", "Maltodextrin / High GI fillers", "Glycemic Load"]
        )

    # Default: General Wellness & Clean Label Consumer
    return ConsumerIntentProfile(
        intent="General Wellness & Clean-Label Consumer",
        rationale="Screening for whole-food integrity, chemical preservatives, trans fats, and hidden sodium.",
        suitability="Acceptable with Moderation",
        priority_nutrients=["Trans Fats", "Sodium / Salt", "NOVA Processing Level", "Antioxidant Richness"]
    )

def analyze_tradeoffs(
    nutritional: Optional[dict], 
    nova: NovaAnalysis, 
    ingredients: List[str]
) -> NutritionalTradeOff:
    """Generates balanced, non-alarmist trade-offs."""
    positives = []
    negatives = []

    if nova.group == 1:
        positives.append("Clean, unrefined whole-food cellular matrix.")
        positives.append("Zero artificial additives or chemical preservatives.")
    elif nova.group == 4:
        negatives.append("High degree of industrial processing (UPF Group 4).")
        if nova.upf_markers:
            negatives.append(f"Contains industrial cosmetic additives: {', '.join(nova.upf_markers[:3])}.")

    if nutritional:
        protein = nutritional.get("protein_g") or 0
        sugar = nutritional.get("sugar_g") or 0
        sodium = nutritional.get("sodium_mg") or 0
        fiber = nutritional.get("fiber_g") or 0

        if protein >= 10: positives.append(f"Excellent protein density ({protein}g per serving).")
        if fiber >= 4: positives.append(f"High prebiotic fiber content ({fiber}g per serving) promoting satiety.")
        if sugar > 15: negatives.append(f"High sugar load ({sugar}g per serving); will trigger insulin peak.")
        if sodium > 400: negatives.append(f"Elevated sodium level ({sodium}mg per serving); monitor daily blood pressure threshold.")

    if not positives:
        positives.append("Convenient shelf-stable caloric energy source.")
    if not negatives:
        negatives.append("Standard balanced formulation without immediate acute concerns.")

    # Calculate verdict and frequency
    if nova.group == 1 and not negatives:
        verdict = "Excellent"
        freq = "Daily Staple"
        summary = "Highly wholesome, nutrient-dense whole food. Excellent cornerstone for a daily balanced diet."
    elif nova.group <= 3 and len(negatives) <= 1:
        verdict = "Good"
        freq = "2-3 Times a Week"
        summary = "Reasonable nutritional profile with minimal processing compromises. Enjoy regularly with balance."
    elif nova.group == 4 and len(negatives) <= 2:
        verdict = "Fair"
        freq = "Occasional Treat"
        summary = "Ultra-processed product offering sensory convenience but carries refined stabilizers and moderate sodium/sugar."
    else:
        verdict = "Avoid"
        freq = "Rarely / Avoid"
        summary = "Heavy ultra-processing footprint with multiple synthetic additives and high refined carb/sodium levels. Restrict frequency."

    return NutritionalTradeOff(
        positive_aspects=positives,
        negative_aspects=negatives,
        consumer_tradeoff_summary=summary,
        verdict=verdict,
        frequency_recommendation=freq
    )

def audit_uncertainties(label_data: dict) -> UncertaintyAudit:
    """Flags blurry, ambiguous, or incomplete label data."""
    flags = []
    confidence = 1.0

    if not label_data.get("ingredients"):
        flags.append("Ingredient list could not be fully identified or was cropped out.")
        confidence -= 0.4
    if not label_data.get("nutritional_info"):
        flags.append("Nutritional facts panel is missing from image; macro and micro calculations are estimated.")
        confidence -= 0.3
    if not label_data.get("net_weight"):
        flags.append("Net weight / serving size not declared on scan.")
        confidence -= 0.1
    if not label_data.get("fssai_license"):
        flags.append("Regulatory license number not detected.")
        confidence -= 0.1

    has_gaps = len(flags) > 0
    rec = "Image clarity is optimal. All statutory fields extracted with high fidelity." if not has_gaps else "For 100% legal audit assurance, capture a direct flat photo of the back nutritional panel."

    return UncertaintyAudit(
        has_gaps=has_gaps,
        confidence_score=round(max(0.2, confidence), 2),
        flags=flags,
        recommendation=rec
    )

def generate_intelligence_report(
    ingredients: List[str],
    additives: Optional[List[dict]] = None,
    nutritional: Optional[dict] = None,
    claims: Optional[List[str]] = None,
    category: str = "Food & Beverage",
    raw_label: Optional[dict] = None
) -> ComprehensiveIntelligenceReport:
    """Orchestrates NOVA classification, intent detection, and trade-offs."""
    nova = classify_nova(ingredients, additives)
    intent = detect_consumer_intent(ingredients, claims or [], category)
    tradeoffs = analyze_tradeoffs(nutritional, nova, ingredients)
    uncertainty = audit_uncertainties(raw_label or {"ingredients": ingredients, "nutritional_info": nutritional})

    return ComprehensiveIntelligenceReport(
        nova=nova,
        intent=intent,
        tradeoffs=tradeoffs,
        uncertainty=uncertainty
    )
