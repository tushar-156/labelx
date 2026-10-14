"""
Hidden Ingredient & Adulteration Detection Service
Detects hidden sugars, hidden MSG (glutamates), hidden trans fats,
and category-specific food fraud / adulteration (e.g., olive oil, honey, saffron).
Ported & enhanced from LabelSpy-AI.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional

# High glycemic index hidden sugars & ultra-processed syrups
HIDDEN_SUGAR_DICTIONARY = {
    "maltodextrin": "Ultra-processed corn/wheat derivative with a glycemic index of 110 (higher than table sugar). Spikes insulin rapidly.",
    "dextrose": "Purified glucose monomer that rapidly elevates blood sugar levels.",
    "high fructose corn syrup": "Enzymatically processed sweetener linked to non-alcoholic fatty liver disease (NAFLD) and insulin resistance.",
    "hfcs": "Concentrated industrial fructose sweetener heavily processed in the liver.",
    "invert syrup": "Sucrose split into glucose and fructose, commonly used to conceal total added sugar content.",
    "corn syrup solids": "Dehydrated industrial corn sweetener used to add bulk and sweetness.",
    "malt extract": "Concentrated malted grain sugars used as a coloring and hidden sweetener.",
    "agave nectar": "Marketed as natural but contains up to 85% free fructose, burdening liver metabolism.",
    "isoglucose": "European synonym for high-fructose corn syrup.",
    "rice syrup": "Concentrated starch sweetener often used as a cheap filler to adulterate pure honey."
}

# Hidden glutamate flavor enhancers
HIDDEN_MSG_DICTIONARY = {
    "yeast extract": "Concentrated autolyzed yeast containing high concentrations of free glutamic acid (natural MSG analogue).",
    "autolyzed yeast": "Hydrolyzed yeast cells releasing high amounts of free glutamates.",
    "hydrolyzed vegetable protein": "Chemically broken down plant protein creating concentrated free monosodium glutamates.",
    "hvp": "Short abbreviation for Hydrolyzed Vegetable Protein; intense glutamate flavor enhancer.",
    "hydrolyzed soy protein": "Acid-hydrolyzed soy meal packed with free glutamic acid.",
    "disodium inosinate": "Purine-based flavor enhancer acting synergistically with free glutamates to amplify MSG effects.",
    "disodium guanylate": "Nucleotide additive designed to multiply savory umami signals by up to 8x when paired with glutamates.",
    "textured vegetable protein": "Extruded soy/grain byproduct containing residual processing salts and free glutamates."
}

# Hidden or disguised industrial trans fats
HIDDEN_TRANS_FAT_DICTIONARY = {
    "hydrogenated vegetable oil": "Partially or fully hydrogenated industrial fat containing trans fatty acids detrimental to cardiovascular health.",
    "partially hydrogenated oil": "Primary dietary source of artificial trans fats that lower HDL and raise LDL cholesterol.",
    "vanaspati": "Hydrogenated vegetable ghee high in trans-fatty isomers, strictly limited under FSSAI (<2%).",
    "interesterified fat": "Chemically or enzymatically rearranged triacylglycerols used as trans-fat replacements with emerging metabolic concerns.",
    "shortening": "Solidified industrial vegetable fat blend often containing undetected trans isomers."
}

# Adulteration & Food Fraud Rules
ADULTERATION_RULES = [
    {
        "target_category": "olive oil",
        "adulterants": ["sunflower oil", "soybean oil", "canola oil", "palm oil", "pomace"],
        "message": "Potential Olive Oil Adulteration: Product labeled as premium olive oil contains cheaper refined seed oils."
    },
    {
        "target_category": "honey",
        "adulterants": ["rice syrup", "corn syrup", "invert sugar", "cane sugar", "jaggery syrup", "maltodextrin"],
        "message": "Potential Honey Adulteration: Pure honey must not contain exogenous sugar syrups (FSSAI NMR testing standard)."
    },
    {
        "target_category": "ghee",
        "adulterants": ["palm oil", "vanaspati", "animal fat", "refined vegetable oil", "starch"],
        "message": "Potential Ghee Adulteration: Product claims pure desi cow/buffalo ghee but lists vegetable fats or neutralizers."
    },
    {
        "target_category": "saffron",
        "adulterants": ["tartrazine", "sunset yellow", "synthetic dye", "safflower"],
        "message": "Potential Saffron Adulteration: High-cost saffron adulterated with synthetic petroleum food colorings."
    }
]

def detect_hidden_ingredients(
    raw_text: str,
    scanned_items: List[str],
    product_title: str = ""
) -> List[Dict[str, Any]]:
    """
    Deterministic rule-based detection for hidden additives and food fraud.
    Under NO circumstances flags natural spices, herbs, fruits, garlic, onion, or salt.
    """
    alerts = []
    normalized_items = [re.sub(r'[^a-zA-Z0-9\s]', ' ', i).lower().strip() for i in scanned_items]
    combined_text = f"{product_title} {raw_text} {' '.join(normalized_items)}".lower()

    # 1. Hidden Sugars
    for item in scanned_items:
        clean_item = re.sub(r'[^a-zA-Z0-9\s]', ' ', item).lower().strip()
        for sugar_key, profile in HIDDEN_SUGAR_DICTIONARY.items():
            if re.search(r'\b' + re.escape(sugar_key) + r'\b', clean_item):
                alerts.append({
                    "type": "hidden_sugar",
                    "title": f"Sugar Alias: {sugar_key.title()}",
                    "ingredient": item,
                    "message": profile,
                    "severity": "medium"
                })
                break

    # 2. Hidden Glutamates / MSG
    for item in scanned_items:
        clean_item = re.sub(r'[^a-zA-Z0-9\s]', ' ', item).lower().strip()
        for msg_key, profile in HIDDEN_MSG_DICTIONARY.items():
            if re.search(r'\b' + re.escape(msg_key) + r'\b', clean_item):
                alerts.append({
                    "type": "hidden_msg",
                    "title": f"Glutamate Enhancer: {msg_key.title()}",
                    "ingredient": item,
                    "message": profile,
                    "severity": "medium"
                })
                break

    # 3. Hidden Trans Fats
    for item in scanned_items:
        clean_item = re.sub(r'[^a-zA-Z0-9\s]', ' ', item).lower().strip()
        for tf_key, profile in HIDDEN_TRANS_FAT_DICTIONARY.items():
            if re.search(r'\b' + re.escape(tf_key) + r'\b', clean_item):
                alerts.append({
                    "type": "hidden_trans_fat",
                    "title": f"Trans Fat Precursor: {tf_key.title()}",
                    "ingredient": item,
                    "message": profile,
                    "severity": "high"
                })
                break

    # 4. Economic Adulteration & Food Fraud
    for rule in ADULTERATION_RULES:
        target = rule["target_category"]
        if target in product_title.lower() or target in raw_text.lower():
            for ad in rule["adulterants"]:
                for item in scanned_items:
                    clean_item = re.sub(r'[^a-zA-Z0-9\s]', ' ', item).lower().strip()
                    if re.search(r'\b' + re.escape(ad) + r'\b', clean_item):
                        alerts.append({
                            "type": "adulteration",
                            "title": f"Economic Adulteration ({target.title()})",
                            "ingredient": item,
                            "message": rule["message"],
                            "severity": "high"
                        })
                        break

    return alerts
