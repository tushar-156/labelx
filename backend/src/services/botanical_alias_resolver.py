"""
Scientific Latin & Botanical Allergen Alias Resolver for LabelX
Inspired by Ingredient_Check_AI (rag_pipeline.py)
Normalizes obscure scientific, botanical, and cosmetic INCI names into statutory allergen categories.
"""

from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
import re

class ResolvedAllergen(BaseModel):
    raw_ingredient: str
    scientific_or_inci_name: str
    allergen_category: str
    common_name: str
    confidence: float

# Botanical & Chemical Allergen Taxonomy Dictionary
BOTANICAL_ALLERGEN_TAXONOMY: List[Dict[str, Any]] = [
    # ── PEANUTS ──
    {"scientific": "arachis hypogaea", "common": "Peanut", "category": "Peanuts", "aliases": ["arachis oil", "groundnut", "monkey nut", "goober nut", "arachides", "cacahuètes", "erdnüsse"]},
    
    # ── TREE NUTS ──
    {"scientific": "prunus amygdalus dulcis", "common": "Sweet Almond", "category": "Tree Nuts", "aliases": ["almond oil", "prunus dulcis", "mandel", "fruits à coque", "mandeln", "almendras"]},
    {"scientific": "anacardium occidentale", "common": "Cashew Nut", "category": "Tree Nuts", "aliases": ["cashew butter", "maranon", "noix de cajou", "kaschunüsse"]},
    {"scientific": "juglans regia", "common": "English Walnut", "category": "Tree Nuts", "aliases": ["walnut seed oil", "juglans nigra", "black walnut", "walnüsse", "noix"]},
    {"scientific": "corylus avellana", "common": "Hazelnut", "category": "Tree Nuts", "aliases": ["filbert", "hazelnut oil", "cobnut", "noisettes", "haselnüsse", "avellanas"]},
    {"scientific": "pistacia vera", "common": "Pistachio Nut", "category": "Tree Nuts", "aliases": ["pistacia oil", "pistaches", "pistazien"]},
    {"scientific": "macadamia ternifolia", "common": "Macadamia Nut", "category": "Tree Nuts", "aliases": ["macadamia integrifolia", "queensland nut"]},
    {"scientific": "carya illinoinensis", "common": "Pecan Nut", "category": "Tree Nuts", "aliases": ["pecan oil", "noix de pécan", "pekannüsse"]},
    {"scientific": "bertholletia excelsa", "common": "Brazil Nut", "category": "Tree Nuts", "aliases": ["brazil nut oil", "paranüsse"]},

    # ── WHEAT & GLUTEN ──
    {"scientific": "triticum aestivum", "common": "Wheat", "category": "Wheat", "aliases": ["triticum vulgare", "wheat germ oil", "hydrolyzed wheat protein", "spelt", "triticum spelta", "kamut", "semolina", "durum", "blé", "weizen", "trigo", "gluten"]},
    {"scientific": "hordeum vulgare", "common": "Barley / Malt", "category": "Wheat", "aliases": ["barley malt extract", "malt extract", "hordeum distichon", "brewer's yeast", "orge", "gerste"]},
    {"scientific": "secale cereale", "common": "Rye", "category": "Wheat", "aliases": ["rye flour", "rye extract", "seigle", "roggen"]},

    # ── SOYBEANS ──
    {"scientific": "glycine max", "common": "Soybean", "category": "Soy", "aliases": ["glycine soja", "soja oil", "hydrolyzed soy protein", "edamame", "textured vegetable protein", "tvp", "soja", "sojabohnen"]},

    # ── MILK & DAIRY ──
    {"scientific": "bos taurus", "common": "Bovine Milk", "category": "Milk", "aliases": ["casein", "caseinate", "sodium caseinate", "calcium caseinate", "whey", "whey protein", "lactalbumin", "lactoglobulin", "colostrum", "lactose", "ghee", "lait", "milch", "leche"]},

    # ── EGGS ──
    {"scientific": "gallus domesticus", "common": "Egg", "category": "Eggs", "aliases": ["albumen", "ovalbumin", "lysozyme", "œufs", "oeufs", "eier", "huevos", "egg powder", "egg white"]},

    # ── SESAME ──
    {"scientific": "sesamum indicum", "common": "Sesame Seed", "category": "Sesame", "aliases": ["sesame oil", "benne", "tahini", "gingelly", "til", "sésame", "sesamsamen"]},

    # ── MUSTARD & CELERY ──
    {"scientific": "brassica nigra", "common": "Black Mustard", "category": "Mustard", "aliases": ["sinapis alba", "white mustard", "brassica juncea", "mustard seed extract", "moutarde", "senf", "mostaza"]},
    {"scientific": "apium graveolens", "common": "Celery", "category": "Celery", "aliases": ["celery seed oil", "celery root", "celeriac", "céleri", "sellerie", "apio"]},

    # ── FISH & SHELLFISH ──
    {"scientific": "gadus morhua", "common": "Codfish", "category": "Fish", "aliases": ["isinglass", "fish collagen", "fish gelatin", "anchovy extract", "poissons", "fisch", "pescado"]},
    {"scientific": "crangon crangon", "common": "Brown Shrimp", "category": "Crustaceans", "aliases": ["glucosamine", "chitosan", "krill oil", "prawn extract", "crustacés", "krebstiere", "mariscos"]},

    # ── SULPHITES & LUPIN ──
    {"scientific": "sulphur dioxide", "common": "Sulphites", "category": "Sulphites", "aliases": ["sulfites", "sulphites", "schwefeldioxid", "sodium metabisulphite", "e220", "e221", "e222", "e223"]},
    {"scientific": "lupinus albus", "common": "Lupin", "category": "Lupin", "aliases": ["lupin", "lupine", "lupinen", "altramuces", "lupin flour"]}
]

class BotanicalAliasResolver:
    """Detects disguised or Latin allergen synonyms in ingredient lists."""

    @staticmethod
    def resolve_botanical_allergens(ingredients: List[str]) -> List[ResolvedAllergen]:
        detected = []

        for ing in ingredients:
            ing_lower = ing.lower().strip()
            # Clean punctuation for exact word boundary match
            clean_text = re.sub(r'[\(\)\,\.\:]', ' ', ing_lower)

            for entry in BOTANICAL_ALLERGEN_TAXONOMY:
                # 1. Match scientific name
                sci = entry["scientific"]
                if sci in clean_text or clean_text in sci:
                    detected.append(ResolvedAllergen(
                        raw_ingredient=ing,
                        scientific_or_inci_name=sci.title(),
                        allergen_category=entry["category"],
                        common_name=entry["common"],
                        confidence=0.98
                    ))
                    continue

                # 2. Match aliases
                for alias in entry["aliases"]:
                    pattern = r'\b' + re.escape(alias) + r'\b'
                    if re.search(pattern, clean_text):
                        detected.append(ResolvedAllergen(
                            raw_ingredient=ing,
                            scientific_or_inci_name=alias.title(),
                            allergen_category=entry["category"],
                            common_name=entry["common"],
                            confidence=0.92
                        ))
                        break

        # De-duplicate by raw ingredient and category
        seen = set()
        unique = []
        for d in detected:
            key = (d.raw_ingredient.lower(), d.allergen_category.lower())
            if key not in seen:
                seen.add(key)
                unique.append(d)

        return unique

botanical_alias_resolver = BotanicalAliasResolver()
