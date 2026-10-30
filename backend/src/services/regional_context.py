"""
Regional Formulation & Market Context Awareness Engine for LabelX
Provides jurisdiction-specific regulatory knowledge, compliance thresholds, and product standards:
  - India: FSSAI (Food Safety & Standards Authority of India) & BIS
  - CIS / Eurasia: GOST standards, TR CU 021/2011, condensed milk fat profiles, dairy purity
  - European Union: EFSA (European Food Safety Authority) & EU Cosmetics Reg 1223/2009 (Annex II/III)
  - United States: US FDA (21 CFR Part 101, GRAS list, MoCRA cosmetics)
"""

from typing import Dict, List, Optional
from pydantic import BaseModel

class RegionalStandardProfile(BaseModel):
    region_code: str  # 'IN', 'CIS', 'EU', 'US'
    authority_name: str
    primary_regulations: List[str]
    banned_substances: List[str]
    special_mandatory_requirements: List[str]
    context_notes: str

REGIONAL_REGISTRIES: Dict[str, RegionalStandardProfile] = {
    "IN": RegionalStandardProfile(
        region_code="IN",
        authority_name="FSSAI (Food Safety and Standards Authority of India)",
        primary_regulations=[
            "FSS (Packaging and Labelling) Regulations, 2011",
            "FSS (Food Products Standards and Food Additives) Regulations, 2011 (Schedule I)",
            "FSS (Advertising and Claims) Regulations, 2018",
            "FSS (Labelling and Display) Regulations, 2020",
            "Drugs and Cosmetics Act, 1940 (BIS Standards for Cosmetics)"
        ],
        banned_substances=[
            "Titanium Dioxide (E171) in selected food lines",
            "Potassium Bromate (bread conditioner)",
            "Carbon Black (E153) in food",
            "Cyclamate (E952 artificial sweetener)",
            "Bithionol, Chloroform, Methylene chloride in cosmetics"
        ],
        special_mandatory_requirements=[
            "Green/Brown Vegetarian / Non-Vegetarian circular symbol with green/brown square outline",
            "14-digit FSSAI License Number with FSSAI Logo",
            "Nutritional facts per 100g and per serving with %RDA",
            "Explicit Allergen Declaration ('Contains: ...')"
        ],
        context_notes="India mandates strict vegetarian/non-vegetarian disclosure and a 14-digit verifiable FSSAI license number on all packaged goods."
    ),
    "CIS": RegionalStandardProfile(
        region_code="CIS",
        authority_name="EAEU / GOST & Rospotrebnadzor",
        primary_regulations=[
            "TR CU 021/2011 On Food Safety",
            "TR CU 022/2011 Food Products in Terms of Their Labelling",
            "TR CU 009/2011 On Safety of Perfumery and Cosmetic Products",
            "GOST 31688-2012 for Condensed Milk and Dairy Preserves"
        ],
        banned_substances=[
            "Synthetic trans-fats exceeding 2% in fats/oils",
            "E128 (Red 2G), E121 (Citrus Red 2)",
            "Uncertified synthetic GMO constructs without CU declaration"
        ],
        special_mandatory_requirements=[
            "EAC (Eurasian Conformity) Mark",
            "Strict fraction distinction between whole dairy fat vs vegetable oil substitutes (СЗМЖ vs БЗМЖ)",
            "GOST standard number citation if claimed as traditional formulation"
        ],
        context_notes="CIS markets place stringent emphasis on dairy authenticity (e.g. condensed milk purity, prohibiting vegetable oils under traditional dairy designations)."
    ),
    "EU": RegionalStandardProfile(
        region_code="EU",
        authority_name="EFSA & European Commission",
        primary_regulations=[
            "Regulation (EC) No 1223/2009 on Cosmetic Products (Annex II Banned, Annex III Restricted)",
            "Regulation (EU) No 1169/2011 (FIC - Food Information to Consumers)",
            "Regulation (EC) No 1333/2008 on Food Additives",
            "REACH Regulation (EC) 1907/2006"
        ],
        banned_substances=[
            "Titanium Dioxide (E171) banned in food across EU (2022)",
            "Lilial (Butylphenyl methylpropional) banned in cosmetics",
            "Zinc Pyrithione banned in cosmetics (Annex II)",
            "Over 1,600 chemical substances prohibited in cosmetics"
        ],
        special_mandatory_requirements=[
            "Nutri-Score Front-of-Pack classification (A to E in participating member states)",
            "26 specific cosmetic fragrance allergens must be declared if >0.001% in leave-on",
            "Mandatory Responsible Person (RP) within the EU and CPNP notification"
        ],
        context_notes="The EU maintains the global gold standard for precautionary consumer safety with the largest database of prohibited cosmetic and food ingredients."
    ),
    "US": RegionalStandardProfile(
        region_code="US",
        authority_name="US FDA (Food and Drug Administration)",
        primary_regulations=[
            "21 CFR Part 101 - Food Labeling",
            "Food Allergen Labeling and Consumer Protection Act (FALCPA & FASTER Act 2021 for Sesame)",
            "Modernization of Cosmetics Regulation Act of 2022 (MoCRA)",
            "FDA GRAS (Generally Recognized as Safe) List"
        ],
        banned_substances=[
            "Cyclamate (banned artificial sweetener)",
            "Bithionol, Mercury compounds, Vinyl chloride in cosmetics",
            "Chloroform in cosmetics"
        ],
        special_mandatory_requirements=[
            "Nutrition Facts panel with Added Sugars declared in grams and %DV",
            "Top 9 major food allergens declared (includes Sesame as of Jan 2023)",
            "MoCRA adverse event reporting contact and facility registration for cosmetics"
        ],
        context_notes="The US FDA requires precise Nutrition Facts tables with Added Sugars explicitly segregated from total carbs."
    )
}

class RegionalContextEngine:
    """Provides market-aware context injection for label analysis."""

    @staticmethod
    def get_profile(region_code: str = "IN") -> RegionalStandardProfile:
        code = region_code.upper().strip()
        return REGIONAL_REGISTRIES.get(code, REGIONAL_REGISTRIES["IN"])

    @staticmethod
    def detect_region_from_text(raw_text: str) -> str:
        text_lower = raw_text.lower()
        if any(term in text_lower for term in ["fssai", "mrp rs", "lic no", "veg", "non-veg", "india"]):
            return "IN"
        if any(term in text_lower for term in ["гост", "состав", "ту рб", "еас", "руб", "республика"]):
            return "CIS"
        if any(term in text_lower for term in ["ec no", "1223/2009", "nutri-score", "eur", "made in eu", "fragrance allergens"]):
            return "EU"
        if any(term in text_lower for term in ["fda", "nutrition facts", "added sugars", "% daily value", "distributed by usa"]):
            return "US"
        return "IN"  # default to FSSAI

regional_context_engine = RegionalContextEngine()
