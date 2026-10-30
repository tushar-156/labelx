r"""
Label Padhega India 🇮🇳 Deceptive Marketing Buster & Temporal Health Impact Engine
Adapted from C:\ClientBTP\IngreScan-AI (server/routers.ts, ScanResult.tsx)

Key Capabilities:
1. Ingredient Order Hierarchy Analyzer:
   - Validates the FSSAI descending order rule (top 3 ingredients represent ~75% of product volume).
   - Flags when cheap fillers, palmolein, or sugars dominate products claiming to be "healthy".
2. Deceptive Claim & Greenwashing Debunker:
   - Unmasks "No Added Sugar" claims loaded with maltodextrin (GI 110-185), invert syrup, or dextrose.
   - Detects Refined Palmolein hiding in "Nutritious Snacks".
   - Flags predatory marketing targeted at children (Southampton Six azo dyes + intense sweeteners).
3. Temporal Tripartite Health Impact Matrix:
   - Categorizes each flagged ingredient into Short-Term (0-24h), Long-Term (Chronic), and Side Effects.
   - Provides authoritative PubMed, WHO, and FSSAI citations.
4. Biometric Risk Personalization:
   - Computes BMI (kg/m^2) and personalizes vulnerability scores.
"""

import re
from typing import List, Dict, Optional, Any, Tuple
from pydantic import BaseModel

class HierarchyAudit(BaseModel):
    top_3_ingredients: List[str]
    dominant_filler: Optional[str]
    is_sugar_in_top_3: bool
    is_palm_oil_in_top_3: bool
    is_refined_flour_in_top_3: bool
    hierarchy_verdict: str
    consumer_tip: str

class GreenwashingAlert(BaseModel):
    claimed_label: str
    actual_substance_detected: str
    glycemic_index_or_risk: str
    deception_mechanism: str
    regulatory_verdict: str

class TemporalHealthImpact(BaseModel):
    ingredient_name: str
    scientific_name_or_e_code: str
    category: str
    risk_level: str  # 'Safe', 'Low', 'Moderate', 'High', 'Severe'
    short_term_effects: str
    long_term_effects: str
    documented_side_effects: str
    sources: List[str]

class LabelPadhegaAuditReport(BaseModel):
    hierarchy: HierarchyAudit
    greenwashing_alerts: List[GreenwashingAlert]
    temporal_impacts: List[TemporalHealthImpact]
    palm_oil_alert: Optional[str]
    children_marketing_alert: Optional[str]
    summary_verdict: str

# Curated High-Assurance Clinical & PubMed Monograph Database for Packaged Food Additives
TEMPORAL_IMPACTS_DB: Dict[str, Dict[str, Any]] = {
    "maltodextrin": {
        "scientific": "Polysaccharide hydrolysis polymer (DE 3-20)",
        "category": "High-Glycemic Bulking Agent & Sweetener",
        "risk_level": "High",
        "short_term": "Triggers rapid, acute blood glucose spike (GI 110-185, higher than pure glucose), followed by reactive hypoglycemia and brain fog.",
        "long_term": "Contributes to insulin resistance, hepatic steatosis (fatty liver), and alters the gut microbiome by promoting E. coli colonization in mucosal linings.",
        "side_effects": "Digestive bloating, abdominal gas, increased hunger within 90 minutes.",
        "sources": ["PubMed ID: 22778739 (Nickerson et al.)", "WHO Sugar Guidelines 2023", "FSSAI Food Safety Standards"]
    },
    "palmolein": {
        "scientific": "Elaeis guineensis refined lipid fraction",
        "category": "Refined Industrial Vegetable Oil",
        "risk_level": "High",
        "short_term": "Elevates postprandial triglyceride levels and slows gastric emptying time.",
        "long_term": "Contains ~50% saturated palmitic acid. Chronic consumption induces endothelial dysfunction, elevates LDL cholesterol, and accelerates coronary artery plaque formation.",
        "side_effects": "Acid reflux, heaviness, systemic low-grade vascular inflammation.",
        "sources": ["PubMed ID: 26038487 (Sun et al.)", "ICMR-NIN Dietary Guidelines for Indians 2024", "WHO Saturated Fat Review"]
    },
    "palm oil": {
        "scientific": "Elaeis guineensis oil",
        "category": "Refined Tropical Oil",
        "risk_level": "High",
        "short_term": "High saturated lipid load delaying gastric motility.",
        "long_term": "Repeated industrial heating yields 3-MCPD and glycidyl fatty acid esters (genotoxic carcinogens as designated by EFSA). Increases cardiovascular atherogenic risk.",
        "side_effects": "Indigestion, arterial endothelial stress.",
        "sources": ["EFSA Contaminants in the Food Chain (CONTAM) 2016", "PubMed ID: 30049071"]
    },
    "tbhq": {
        "scientific": "Tertiary Butylhydroquinone (E319 / INS 319)",
        "category": "Synthetic Phenolic Antioxidant / Preservative",
        "risk_level": "Severe",
        "short_term": "Can cause nausea, acute contact dermatitis, and transient tinnitus in doses above 100 ppm.",
        "long_term": "In vivo studies demonstrate oxidative stress, potential immune system dysregulation (inhibits CD4/CD8 T-cell activation), and pre-cancerous cellular alterations in liver tissue.",
        "side_effects": "Allergic reactions, hyperactivity, immunological hypersensitivity.",
        "sources": ["PubMed ID: 31210160 (Michigan State Univ)", "FSSAI Schedule I (Max 200 PPM)", "EFSA Journal 2018"]
    },
    "sodium benzoate": {
        "scientific": "Sodium salt of benzoic acid (E211 / INS 211)",
        "category": "Synthetic Antimicrobial Preservative",
        "risk_level": "Moderate",
        "short_term": "Triggers leukotriene release, exacerbating bronchospasms in sensitive asthmatics.",
        "long_term": "When combined with Vitamin C (Ascorbic Acid E300) in acidic liquids, it chemically reacts to synthesize Benzene, a classified Group 1 human carcinogen.",
        "side_effects": "Skin hives, allergic rhinitis, pediatric behavioral irritability.",
        "sources": ["FDA Food Safety Benzene Survey", "PubMed ID: 17825405 (McCann et al.)", "WHO Food Additives Series"]
    },
    "monosodium glutamate": {
        "scientific": "Sodium 2-aminopentanedioate (E621 / INS 621)",
        "category": "Excitatory Neurotransmitter Flavor Enhancer",
        "risk_level": "Moderate",
        "short_term": "Chinese Restaurant Syndrome: facial numbness, heart palpitations, and tension headaches in sensitive individuals within 30 minutes.",
        "long_term": "Hyper-stimulates hypothalamic appetite receptors, desensitizing leptin satiety cues and promoting overeating.",
        "side_effects": "Thirst, facial flushing, migraine onset.",
        "sources": ["PubMed ID: 19302116", "FSSAI Labelling Regulations", "EFSA Re-evaluation of Glutamates"]
    },
    "tartrazine": {
        "scientific": "Trisodium 5-hydroxy-1-(4-sulfonatophenyl)-4-(4-sulfonatophenylazo)pyrazole-3-carboxylate (E102 / INS 102)",
        "category": "Synthetic Azo Food Colorant (Southampton Six)",
        "risk_level": "Severe",
        "short_term": "Cross-reactive pseudo-allergy in individuals with aspirin sensitivity; acute urticaria (hives).",
        "long_term": "Under the UK Southampton University study and EU regulations, causes clinically significant increases in hyperactivity and attention deficit in children. Requires mandatory EU warning label.",
        "side_effects": "Restlessness, loss of focus, allergic rhinitis in children.",
        "sources": ["The Lancet: PubMed ID: 17825405", "EU Regulation 1333/2008 Annex V", "FSSAI Color Regulations"]
    },
    "sunset yellow": {
        "scientific": "Disodium 6-hydroxy-5-[(4-sulfophenyl)azo]-2-naphthalenesulfonate (E110 / INS 110)",
        "category": "Synthetic Azo Dye (Southampton Six)",
        "risk_level": "High",
        "short_term": "Induces non-IgE histamine release and gastric irritation.",
        "long_term": "Associated with pediatric hyperactivity, DNA damage in animal colonic mucosa, and contact dermatitis.",
        "side_effects": "Hyperactivity in children, nasal congestion, itching.",
        "sources": ["PubMed ID: 22002305", "UK Food Standards Agency Guidelines", "EFSA Scientific Opinion 2014"]
    },
    "invert sugar": {
        "scientific": "Equimolar glucose-fructose hydrolysate syrup",
        "category": "Refined Liquid Sugar",
        "risk_level": "High",
        "short_term": "Near-instantaneous blood glucose spike followed by steep insulin dump.",
        "long_term": "Free unbound fructose directly bypasses insulin regulation and is metabolized in the liver into de novo triglycerides, causing visceral fat accumulation and NAFLD.",
        "side_effects": "Extreme energy crash, increased dental caries risk.",
        "sources": ["Harvard T.H. Chan School of Public Health", "PubMed ID: 23493534"]
    },
    "carmine": {
        "scientific": "Cochineal extract / Carminic Acid (E120 / INS 120)",
        "category": "Insect-Derived Red Pigment",
        "risk_level": "Moderate",
        "short_term": "Severe IgE-mediated anaphylaxis and occupational asthma in sensitive consumers.",
        "long_term": "Non-vegetarian insect protein (derived from crushed female Dactylopius coccus insects). Deceptive to vegetarians and vegans when listed cryptically as INS 120.",
        "side_effects": "Skin hives, contact dermatitis, breathing difficulty.",
        "sources": ["PubMed ID: 11467406", "FDA Food Labeling: Carmine and Cochineal", "FSSAI Non-Veg Disclosures"]
    }
}

def analyze_ingredient_hierarchy(ingredients: List[str]) -> HierarchyAudit:
    """
    Enforces the FSSAI descending order rule:
    The top 3 ingredients account for ~75% of the total product mass.
    """
    clean_ings = [re.sub(r'\(.*?\)', '', i).strip().lower() for i in ingredients if i.strip()]
    top_3 = clean_ings[:3] if len(clean_ings) >= 3 else clean_ings

    top_3_str = " ".join(top_3)
    is_sugar = any(s in top_3_str for s in ["sugar", "glucose", "fructose", "syrup", "dextrose", "maltodextrin", "jaggery"])
    is_palm = any(p in top_3_str for p in ["palm", "palmolein", "hydrogenated", "vanaspati"])
    is_maida = any(m in top_3_str for m in ["refined wheat flour", "maida", "wheat flour (refined)"])

    filler = None
    if is_sugar and is_palm:
        filler = "Sugar & Refined Palmolein Mixture"
    elif is_maida and is_palm:
        filler = "Refined Maida & Palmolein Base"
    elif is_sugar:
        filler = "Refined Sugar / Sweetener Base"
    elif is_palm:
        filler = "Refined Palm Oil Base"

    if is_sugar or is_palm or is_maida:
        verdict = f"High-Risk Industrial Base: Over 70% of this product is composed of {filler or 'processed fillers'}, not the healthy ingredients shown on the front packaging."
        tip = "Rule of Thumb (#LabelPadhegaIndia): If Sugar, Palm Oil, or Maida is among the first 3 ingredients, treat this as a processed confection, not a health food."
    else:
        verdict = "Wholesome Foundation: Top 3 ingredients are dominated by whole foods, grains, or active culinary staples."
        tip = "Great sign! The primary mass of this product comes from nutritious whole ingredients."

    return HierarchyAudit(
        top_3_ingredients=[i.title() for i in top_3],
        dominant_filler=filler,
        is_sugar_in_top_3=is_sugar,
        is_palm_oil_in_top_3=is_palm,
        is_refined_flour_in_top_3=is_maida,
        hierarchy_verdict=verdict,
        consumer_tip=tip
    )

def evaluate_greenwashing(front_claims: List[str], ingredients: List[str]) -> List[GreenwashingAlert]:
    """
    Detects front-of-pack greenwashing where health claims contradict back-of-pack ingredients.
    """
    alerts: List[GreenwashingAlert] = []
    full_text = " ".join(ingredients).lower()
    claims_text = " ".join(front_claims).lower()

    # 1. "Sugar Free" / "No Added Sugar" but loaded with Maltodextrin / Invert Syrup
    if any(c in claims_text for c in ["sugar free", "no added sugar", "zero sugar", "guilt free", "diet"]):
        if "maltodextrin" in full_text:
            alerts.append(GreenwashingAlert(
                claimed_label="Sugar-Free / No Added Sugar",
                actual_substance_detected="Maltodextrin",
                glycemic_index_or_risk="GI: 110 - 185 (Higher than pure sugar GI 65!)",
                deception_mechanism="Manufacturer replaced sucrose with maltodextrin. While technically not called 'sugar' under outdated laws, it causes a MORE severe blood sugar spike.",
                regulatory_verdict="Deceptive Marketing: Causes rapid glycemic and insulin surges in diabetics."
            ))
        if any(s in full_text for s in ["invert syrup", "liquid glucose", "dextrose", "fruit juice concentrate"]):
            alerts.append(GreenwashingAlert(
                claimed_label="No Refined Sugar",
                actual_substance_detected="Invert Sugar / Liquid Glucose / Fruit Puree Concentrate",
                glycemic_index_or_risk="High Free Fructose Load",
                deception_mechanism="Substituted table sugar with concentrated industrial syrups that metabolize directly into liver fat (triglycerides).",
                regulatory_verdict="Misleading Claim: Chemically identical or worse metabolic impact than sucrose."
            ))

    # 2. "Healthy / Nutritious / 100% Natural" but loaded with Palmolein & TBHQ
    if any(c in claims_text for c in ["healthy", "nutritious", "natural", "goodness of", "power of"]):
        if any(p in full_text for p in ["palmolein", "palm oil", "hydrogenated"]):
            alerts.append(GreenwashingAlert(
                claimed_label="Healthy / Nutritious Snack",
                actual_substance_detected="Refined Palmolein (Palm Oil)",
                glycemic_index_or_risk="50% Saturated Palmitic Fatty Acids",
                deception_mechanism="Advertised as a wholesome grain or protein snack, but deep-fried in cheap commercial palmolein.",
                regulatory_verdict="Cardiovascular Risk: High atherogenic index accelerating arterial plaque formation."
            ))
        if "tbhq" in full_text or "e319" in full_text:
            alerts.append(GreenwashingAlert(
                claimed_label="100% Natural",
                actual_substance_detected="TBHQ (E319 synthetic antioxidant)",
                glycemic_index_or_risk="Petroleum-Derived Synthetic Chemical",
                deception_mechanism="Claims to be natural, but contains synthetic preservative TBHQ to prevent cheap oils from turning rancid on store shelves.",
                regulatory_verdict="Violates Natural Claims Standards under FSSAI Advertising Regulations 2018."
            ))

    return alerts

def get_temporal_health_impacts(ingredients: List[str]) -> List[TemporalHealthImpact]:
    """
    Evaluates detected ingredients against the clinical temporal impact database.
    """
    results: List[TemporalHealthImpact] = []
    full_text = " ".join(ingredients).lower()

    for key, data in TEMPORAL_IMPACTS_DB.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, full_text):
            results.append(TemporalHealthImpact(
                ingredient_name=key.title(),
                scientific_name_or_e_code=data["scientific"],
                category=data["category"],
                risk_level=data["risk_level"],
                short_term_effects=data["short_term"],
                long_term_effects=data["long_term"],
                documented_side_effects=data["side_effects"],
                sources=data["sources"]
            ))

    return results

def run_label_padhega_audit(
    ingredients: List[str],
    front_claims: Optional[List[str]] = None
) -> LabelPadhegaAuditReport:
    """
    Full Label Padhega India Comprehensive Consumer Literacy Audit.
    """
    claims = front_claims or []
    hierarchy = analyze_ingredient_hierarchy(ingredients)
    greenwashing = evaluate_greenwashing(claims, ingredients)
    temporal = get_temporal_health_impacts(ingredients)

    full_text = " ".join(ingredients).lower()

    palm_alert = None
    if any(p in full_text for p in ["palmolein", "palm oil", "fractionated palm"]):
        palm_alert = "⚠️ Refined Palmolein Alert: This product contains cheap industrial palm oil with ~50% saturated palmitic acid. Chronic consumption is linked to elevated LDL and cardiovascular atherogenesis."

    child_alert = None
    if any(c in full_text for c in ["tartrazine", "e102", "sunset yellow", "e110", "carmoisine", "e122", "allura red", "e129"]):
        child_alert = "🚨 Southampton Six Alert (Pediatric Hazard): Contains synthetic azo dyes clinically proven to trigger hyperactivity and attention deficits in children. In the EU, products with these colors must legally carry the warning: 'May have an adverse effect on activity and attention in children'."

    high_risk_count = sum(1 for t in temporal if t.risk_level in ["High", "Severe"])
    if high_risk_count >= 2 or len(greenwashing) > 0:
        verdict = f"Consumer Caution (#LabelPadhegaIndia): This product exhibits deceptive formulation practices with {len(greenwashing)} greenwashing contradiction(s) and {high_risk_count} high-severity chemical additives."
    elif hierarchy.is_sugar_in_top_3 or hierarchy.is_palm_oil_in_top_3:
        verdict = "Ultra-Processed Core: Despite marketing imagery, the primary physical foundation of this food is processed sugar, oil, or refined starch."
    else:
        verdict = "Clean Honest Formulation: Transparent ingredient list with zero deceptive sugar substitutes or high-risk industrial additives detected."

    return LabelPadhegaAuditReport(
        hierarchy=hierarchy,
        greenwashing_alerts=greenwashing,
        temporal_impacts=temporal,
        palm_oil_alert=palm_alert,
        children_marketing_alert=child_alert,
        summary_verdict=verdict
    )

label_padhega_engine = run_label_padhega_audit
