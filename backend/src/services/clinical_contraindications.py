"""
Clinical Drug-Food & Chronic Pathology Contraindication Matrix for LabelX
Inspired by IngreScan-AI and Diet-Lens-Stanford-Project-
Evaluates scanned formulations against active user medications and chronic medical conditions.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import re

class ClinicalContraindication(BaseModel):
    severity: str  # 'CRITICAL', 'HIGH', 'MODERATE', 'CAUTION'
    trigger_ingredient: str
    conflicting_condition_or_drug: str
    clinical_mechanism: str
    recommendation: str

# Evidence-based medical contraindication rules
CLINICAL_RULES = [
    {
        "target": "asthma",
        "type": "condition",
        "keywords": [
            "sodium benzoate", "e211", "ins 211", "benzoic acid", "e210",
            "sulphur dioxide", "sulfur dioxide", "e220", "sodium metabisulphite", "e223",
            "tartrazine", "e102", "sunset yellow", "e110", "aspirin", "salicylate"
        ],
        "severity": "CRITICAL",
        "mechanism": "Sulfites, synthetic benzoates, and azo dyes trigger leukotriene production and non-allergic histamine release, causing acute bronchospasms in sensitive asthmatics.",
        "recommendation": "Avoid products with sulfite (E220-E228) and benzoate (E210-E213) preservatives."
    },
    {
        "target": "hypertension",
        "type": "condition",
        "keywords": [
            "sodium", "salt", "monosodium glutamate", "msg", "e621",
            "sodium bicarbonate", "baking soda", "e500", "sodium nitrate", "e251",
            "licorice", "liquorice", "glycyrrhizin", "glycyrrhizic acid"
        ],
        "severity": "HIGH",
        "mechanism": "High sodium increases blood volume. Glycyrrhizin in licorice inhibits 11-beta-HSD2, triggering mineralocorticoid excess and rapid systolic spikes.",
        "recommendation": "Maintain daily sodium under 1500mg. Strictly avoid real licorice extracts."
    },
    {
        "target": "diabetes",
        "type": "condition",
        "keywords": [
            "maltodextrin", "dextrose", "glucose", "high fructose corn syrup", "hfcs",
            "corn syrup", "sucrose", "invert sugar", "honey", "malt syrup", "agave"
        ],
        "severity": "HIGH",
        "mechanism": "Maltodextrin has a glycemic index of 110-136 (higher than pure table sugar), provoking immediate post-prandial glucose surges and insulin resistance.",
        "recommendation": "Select snacks with a glycemic index < 55 and zero maltodextrin/refined corn syrups."
    },
    {
        "target": "ckd",
        "type": "condition",
        "keywords": [
            "potassium chloride", "e508", "potassium sorbate", "e202", "potassium citrate", "e332",
            "phosphoric acid", "e338", "diphosphate", "e450", "polyphosphate", "e452"
        ],
        "severity": "CRITICAL",
        "mechanism": "Impaired glomerular filtration cannot clear dietary potassium and bioavailable inorganic phosphorus additives, posing arrhythmia and vascular calcification risks.",
        "recommendation": "Strictly eliminate inorganic phosphate additives and potassium salt substitutes."
    },
    {
        "target": "gerd",
        "type": "condition",
        "keywords": [
            "peppermint", "spearmint", "caffeine", "coffee", "citric acid", "e330",
            "cocoa", "chocolate", "chili", "capsicum", "black pepper"
        ],
        "severity": "MODERATE",
        "mechanism": "Relaxes the lower esophageal sphincter (LES) while increasing gastric acid secretion, exacerbating mucosal irritation and reflux.",
        "recommendation": "Limit caffeinated, mint-infused, or highly acidic citrus beverages."
    },
    {
        "target": "gout",
        "type": "condition",
        "keywords": [
            "high fructose corn syrup", "hfcs", "yeast extract", "autolyzed yeast",
            "marmite", "anchovies", "sardines"
        ],
        "severity": "HIGH",
        "mechanism": "Hepatic fructolysis rapidly consumes ATP, forming AMP and degrading into uric acid. Yeast purines directly elevate serum urate.",
        "recommendation": "Avoid high-fructose corn syrups and purine-dense yeast extract flavor enhancers."
    },
    {
        "target": "statins",
        "type": "medication",
        "keywords": ["grapefruit", "grapefruit juice", "grapefruit extract", "naringin", "citrus paradisi"],
        "severity": "CRITICAL",
        "mechanism": "Naringin irreversibly inhibits intestinal CYP3A4 enzymes, increasing statin systemic bioavailability up to 5-fold, drastically elevating rhabdomyolysis and myopathy risk.",
        "recommendation": "Strictly avoid any product with natural grapefruit pulp, juice, or citrus bioflavonoid extracts."
    },
    {
        "target": "metformin",
        "type": "medication",
        "keywords": ["ethanol", "alcohol", "sorbitol", "e420", "maltitol", "e965", "xylitol", "e967"],
        "severity": "MODERATE",
        "mechanism": "Polyols accelerate intestinal transit and fermentative diarrhea, compounding metformin GI side effects. High alcohol intake potentiates lactic acidosis.",
        "recommendation": "Limit sugar alcohol sweeteners and avoid alcohol consumption with medication."
    },
    {
        "target": "ace_inhibitors",
        "type": "medication",
        "keywords": ["potassium chloride", "potassium sorbate", "potassium benzoate", "e212", "e202", "e508"],
        "severity": "HIGH",
        "mechanism": "ACE inhibitors reduce aldosterone secretion, causing renal potassium retention. Potassium additive loads induce hyperkalemia and cardiac conduction risks.",
        "recommendation": "Avoid 'low-sodium' salt substitutes formulated with potassium chloride."
    },
    {
        "target": "warfarin",
        "type": "medication",
        "keywords": ["cranberry", "cranberry extract", "vitamin k", "phylloquinone", "spinach extract", "kale extract", "green tea extract"],
        "severity": "HIGH",
        "mechanism": "Vitamin K directly antagonizes warfarin coagulation cascade inhibition. Cranberry extracts inhibit CYP2C9, unpredictably prolonging INR and hemorrhage risks.",
        "recommendation": "Avoid concentrated cranberry supplements or high vitamin K fortifications."
    },
    {
        "target": "thyroid",
        "type": "medication",
        "keywords": ["soy", "soy protein", "soy lecithin", "e322", "calcium carbonate", "iron", "ferrous"],
        "severity": "MODERATE",
        "mechanism": "Soy isoflavones, calcium carbonate, and iron bind levothyroxine in the gut, severely decreasing therapeutic thyroid hormone absorption.",
        "recommendation": "Separate levothyroxine dose by at least 4 hours from soy-fortified foods or calcium/iron enriched drinks."
    }
]

def check_clinical_contraindications(
    ingredients: List[str],
    user_conditions: Optional[List[str]] = None,
    active_medications: Optional[List[str]] = None
) -> List[ClinicalContraindication]:
    """
    Cross-references ingredients against user medications and conditions.
    """
    if not ingredients:
        return []

    conditions = [c.lower().strip() for c in (user_conditions or []) if c]
    medications = [m.lower().strip() for m in (active_medications or []) if m]
    all_targets = conditions + medications

    # Normalize aliases (e.g. "high blood pressure" -> "hypertension")
    alias_map = {
        "high blood pressure": "hypertension",
        "bp": "hypertension",
        "sugar": "diabetes",
        "diabetic": "diabetes",
        "kidney disease": "ckd",
        "renal": "ckd",
        "acid reflux": "gerd",
        "heartburn": "gerd",
        "atorvastatin": "statins",
        "rosuvastatin": "statins",
        "simvastatin": "statins",
        "enalapril": "ace_inhibitors",
        "lisinopril": "ace_inhibitors",
        "ramipril": "ace_inhibitors",
        "telmisartan": "ace_inhibitors",
        "losartan": "ace_inhibitors",
        "coumadin": "warfarin",
        "blood thinner": "warfarin",
        "levothyroxine": "thyroid",
        "thyronorm": "thyroid",
        "eltroxin": "thyroid"
    }

    normalized_targets = set()
    for t in all_targets:
        normalized_targets.add(t)
        if t in alias_map:
            normalized_targets.add(alias_map[t])

    contraindications = []

    for rule in CLINICAL_RULES:
        rule_target = rule["target"]
        if rule_target in normalized_targets:
            for ing in ingredients:
                ing_clean = ing.lower()
                matched = any(re.search(r'\b' + re.escape(kw) + r'\b', ing_clean) for kw in rule["keywords"])
                if matched:
                    contraindications.append(ClinicalContraindication(
                        severity=rule["severity"],
                        trigger_ingredient=ing,
                        conflicting_condition_or_drug=rule_target.replace("_", " ").title(),
                        clinical_mechanism=rule["mechanism"],
                        recommendation=rule["recommendation"]
                    ))

    # De-duplicate
    seen = set()
    unique_list = []
    for c in contraindications:
        key = (c.trigger_ingredient.lower(), c.conflicting_condition_or_drug.lower())
        if key not in seen:
            seen.add(key)
            unique_list.append(c)

    return unique_list
