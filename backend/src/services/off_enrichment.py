"""
Open Food Facts (OFF) Real-Time Database Enrichment Service
Queries the Open Food Facts API to retrieve:
1. NOVA Group (1: Unprocessed to 4: Ultra-Processed Food UPF)
2. Nutri-Score (A through E)
3. Eco-Score
4. Nutrient Levels (fat, saturated-fat, sugars, salt: low/moderate/high)
"""

import requests
from typing import Dict, Any, Optional

OFF_PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

class OpenFoodFactsClient:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self.headers = {"User-Agent": "LabelX-Platform/1.0 (+https://github.com/tushar-156/labelx)"}

    def fetch_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Direct barcode lookup against Open Food Facts API."""
        clean_code = str(barcode).strip()
        if not clean_code.isdigit() or len(clean_code) < 8:
            return None

        url = OFF_PRODUCT_URL.format(barcode=clean_code)
        try:
            res = requests.get(url, headers=self.headers, timeout=self.timeout)
            if res.ok:
                data = res.json()
                if data.get("status") == 1:
                    return self._format_product(data.get("product", {}))
        except Exception:
            pass
        return None

    def search_by_title(self, product_name: str) -> Optional[Dict[str, Any]]:
        """Fuzzy search by product name against Open Food Facts."""
        if not product_name or len(product_name.strip()) < 3:
            return None

        params = {
            "search_terms": product_name.strip(),
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 1
        }
        try:
            res = requests.get(OFF_SEARCH_URL, params=params, headers=self.headers, timeout=self.timeout)
            if res.ok:
                data = res.json()
                products = data.get("products", [])
                if products:
                    return self._format_product(products[0])
        except Exception:
            pass
        return None

    def _format_product(self, prod: Dict[str, Any]) -> Dict[str, Any]:
        nova_group = prod.get("nova_group")
        nova_labels = {
            1: "Unprocessed or Minimally Processed Food",
            2: "Processed Culinary Ingredient",
            3: "Processed Food",
            4: "Ultra-Processed Food (UPF) - High Industrial Processing"
        }

        nutri_score = (prod.get("nutriscore_grade") or "").upper()
        eco_score = (prod.get("ecoscore_grade") or "").upper()
        nutrient_levels = prod.get("nutrient_levels", {})

        return {
            "found": True,
            "product_name": prod.get("product_name") or prod.get("product_name_en") or "Identified OFF Product",
            "brands": prod.get("brands") or "Verified Manufacturer",
            "nova_group": nova_group,
            "nova_desc": nova_labels.get(nova_group, "NOVA Classification Not Available"),
            "nutri_score": nutri_score or "Not Rated",
            "eco_score": eco_score or "Not Rated",
            "nutrient_levels": {
                "sugars": nutrient_levels.get("sugars", "moderate"),
                "fat": nutrient_levels.get("fat", "moderate"),
                "saturated_fat": nutrient_levels.get("saturated-fat", "moderate"),
                "salt": nutrient_levels.get("salt", "moderate")
            },
            "additives_tags": prod.get("additives_tags", []),
            "allergens_tags": prod.get("allergens_tags", [])
        }

off_client = OpenFoodFactsClient()
