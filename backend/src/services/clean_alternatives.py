"""
Smart Cleaner Alternatives Recommender ("Swap This Junk") for LabelX
Inspired by AI-Product-Analyzer and IngreScan-AI
Suggests healthier, minimally processed (NOVA 1-2) alternatives within the same product category.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel

class CleanAlternative(BaseModel):
    name: str
    brand: str
    category: str
    nova_group: int
    health_score: int
    why_cleaner: str
    swapped_out_additives: List[str]

CLEAN_ALTERNATIVES_CATALOG: Dict[str, List[dict]] = {
    "snack": [
        {
            "name": "Roasted Salt & Pepper Makhana (Fox Nuts)",
            "brand": "Farmley",
            "category": "snack",
            "nova_group": 1,
            "health_score": 94,
            "why_cleaner": "Non-fried popped water lily seeds roasted in cold-pressed olive oil. Zero palmolein, TBHQ, or artificial colorants.",
            "swapped_out_additives": ["TBHQ", "Maltodextrin", "Palmolein", "Monosodium Glutamate (E621)", "Tartrazine (E102)"]
        },
        {
            "name": "Wood-Pressed Multigrain Ragi & Quinoa Crisps",
            "brand": "True Elements",
            "category": "snack",
            "nova_group": 2,
            "health_score": 88,
            "why_cleaner": "100% whole grain millets seasoned with Himalayan pink salt. Free from refined maida flour and synthetic preservatives.",
            "swapped_out_additives": ["Sodium Benzoate (E211)", "Refined Palmolein", "Hydrolyzed Vegetable Protein"]
        },
        {
            "name": "Slow-Roasted Almonds with Rosemary & Sea Salt",
            "brand": "Open Secret",
            "category": "snack",
            "nova_group": 1,
            "health_score": 92,
            "why_cleaner": "Whole California almonds high in natural Vitamin E and dietary fiber with zero trans fats or chemical anti-caking agents.",
            "swapped_out_additives": ["Silicon Dioxide", "Tertiary Butylhydroquinone", "Azo Dyes"]
        }
    ],
    "beverage": [
        {
            "name": "Cold-Pressed Raw Tender Coconut Water",
            "brand": "Raw Pressery",
            "category": "beverage",
            "nova_group": 1,
            "health_score": 96,
            "why_cleaner": "100% pure tender coconut water providing natural potassium electrolytes with zero added sugar, caramel color, or sodium benzoate.",
            "swapped_out_additives": ["High Fructose Corn Syrup", "Sodium Benzoate (E211)", "Caramel Color (E150d)", "Phosphoric Acid (E338)"]
        },
        {
            "name": "Artisanal Sparkling Lemon & Ginger Infusion (Zero Sugar)",
            "brand": "Gunsberg",
            "category": "beverage",
            "nova_group": 2,
            "health_score": 90,
            "why_cleaner": "Naturally brewed with real Himachal ginger root and fresh lime juice without synthetic sweeteners like aspartame or acesulfame-K.",
            "swapped_out_additives": ["Aspartame (E951)", "Acesulfame Potassium (E950)", "Sunset Yellow (E110)"]
        },
        {
            "name": "Organic Cold-Brew Green Tea with Spearmint",
            "brand": "Vahdam",
            "category": "beverage",
            "nova_group": 1,
            "health_score": 95,
            "why_cleaner": "Directly sourced single-estate Darjeeling green tea leaves rich in EGCG catechins and natural antioxidants.",
            "swapped_out_additives": ["Synthetic Caffeine", "Sodium Metabisulphite", "Artificial Flavoring"]
        }
    ],
    "confectionery": [
        {
            "name": "85% Single-Origin Dark Chocolate (Bean-to-Bar)",
            "brand": "Soklet",
            "category": "confectionery",
            "nova_group": 2,
            "health_score": 89,
            "why_cleaner": "Crafted exclusively from unrefined cocoa beans, organic cocoa butter, and unrefined raw cane sugar. Free from palm oil substitutes and PGPR emulsifiers.",
            "swapped_out_additives": ["Polyglycerol Polyricinoleate (E476)", "Hydrogenated Vegetable Fats", "Vanillin (Synthetic)", "Soy Lecithin"]
        },
        {
            "name": "Organic Medjool Date & Walnut Energy Bites",
            "brand": "The Whole Truth",
            "category": "confectionery",
            "nova_group": 1,
            "health_score": 91,
            "why_cleaner": "Naturally sweetened strictly with whole dates and crushed walnuts. Zero liquid glucose, maltodextrin, or preservative chemicals.",
            "swapped_out_additives": ["Liquid Glucose", "Invert Sugar Syrup", "Potassium Sorbate (E202)"]
        }
    ],
    "cosmetic": [
        {
            "name": "100% Plant-Derived Squalane Serum",
            "brand": "Minimalist",
            "category": "cosmetic",
            "nova_group": 1,
            "health_score": 95,
            "why_cleaner": "Single-ingredient pure olive-derived squalane mimicking natural skin sebum. Non-comedogenic, fragrance-free, and paraben-free.",
            "swapped_out_additives": ["Fragrance (Parfum)", "Phenoxyethanol", "Parabens", "BHT", "Silicones (Dimethicone)"]
        },
        {
            "name": "Ceramide & Centella Asiatica Barrier Repair Cream",
            "brand": "Dr. Sheth's",
            "category": "cosmetic",
            "nova_group": 2,
            "health_score": 92,
            "why_cleaner": "Physiological 3:1:1 lipid barrier ratio with Centella soothing triterpenes. Formulated without synthetic fragrance or endocrine-disrupting phthalates.",
            "swapped_out_additives": ["Linalool", "Limonene", "Propylene Glycol", "Mineral Oil"]
        }
    ]
}

def recommend_clean_alternatives(
    category: str,
    harmful_additives: Optional[List[str]] = None
) -> List[CleanAlternative]:
    """Suggests cleaner alternatives matching the product category."""
    cat_lower = category.lower()
    additives = harmful_additives or []

    if any(k in cat_lower for k in ["cosmetic", "skincare", "cream", "lotion", "serum", "haircare"]):
        target_key = "cosmetic"
    elif any(k in cat_lower for k in ["beverage", "drink", "juice", "soda", "cola", "tea"]):
        target_key = "beverage"
    elif any(k in cat_lower for k in ["chocolate", "candy", "sweet", "bar", "confectionery"]):
        target_key = "confectionery"
    else:
        target_key = "snack"

    candidates = CLEAN_ALTERNATIVES_CATALOG.get(target_key, CLEAN_ALTERNATIVES_CATALOG["snack"])

    results = []
    for c in candidates:
        # Match swapped additives
        relevant_swapped = [a for a in additives if any(a.lower() in sw.lower() for sw in c["swapped_out_additives"])]
        if not relevant_swapped:
            relevant_swapped = c["swapped_out_additives"][:3]

        results.append(CleanAlternative(
            name=c["name"],
            brand=c["brand"],
            category=c["category"],
            nova_group=c["nova_group"],
            health_score=c["health_score"],
            why_cleaner=c["why_cleaner"],
            swapped_out_additives=relevant_swapped
        ))

    return results
