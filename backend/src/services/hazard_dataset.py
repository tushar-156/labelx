"""
Hazard Dataset Service
Loads and indexes the 2400+ curated chemical hazard dataset (Food & Cosmetics).
Provides instant O(1) indexed lookup and fuzzy hazard classification.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

class HazardDataset:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HazardDataset, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, dataset_path: Optional[str] = None):
        if self._initialized:
            return

        if not dataset_path:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dataset_path = os.path.join(backend_dir, "data", "ingredients_dataset.json")

        self.dataset_path = dataset_path
        self.chemicals_by_name: Dict[str, Dict[str, Any]] = {}
        self.chemicals_list: List[Dict[str, Any]] = []
        self._load_dataset()
        self._initialized = True

    def _normalize(self, name: str) -> str:
        clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', name.lower())
        return ' '.join(clean.split())

    def _load_dataset(self):
        if not os.path.exists(self.dataset_path):
            print(f"Notice: Hazard dataset not found at {self.dataset_path}")
            return

        type_priority = {"toxic": 3, "moderate": 2, "safe": 1}

        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                self.chemicals_list = data
                for item in data:
                    raw_name = item.get("name", "")
                    norm_name = self._normalize(raw_name)
                    if norm_name:
                        # If already exists, keep the one with higher severity
                        curr = self.chemicals_by_name.get(norm_name)
                        if not curr or type_priority.get(item.get("type"), 1) > type_priority.get(curr.get("type"), 1):
                            self.chemicals_by_name[norm_name] = item
                        
                        # Index parenthetical contents (e.g. 'Monosodium Glutamate (MSG)' -> index 'msg')
                        parens = re.findall(r'\((.*?)\)', raw_name)
                        for p in parens:
                            norm_p = self._normalize(p)
                            if len(norm_p) >= 2:
                                curr_p = self.chemicals_by_name.get(norm_p)
                                if not curr_p or type_priority.get(item.get("type"), 1) > type_priority.get(curr_p.get("type"), 1):
                                    self.chemicals_by_name[norm_p] = item

                        # Index base without parenthetical
                        base = re.sub(r'\(.*?\)', '', raw_name)
                        norm_base = self._normalize(base)
                        if norm_base:
                            curr_b = self.chemicals_by_name.get(norm_base)
                            if not curr_b or type_priority.get(item.get("type"), 1) > type_priority.get(curr_b.get("type"), 1):
                                self.chemicals_by_name[norm_base] = item

            print(f"Loaded Hazard Dataset with {len(self.chemicals_list)} records ({len(self.chemicals_by_name)} indexed tokens).")
        except Exception as e:
            print(f"Error loading hazard dataset: {e}")

    def lookup(self, ingredient_name: str) -> Optional[Dict[str, Any]]:
        """Exact normalized lookup."""
        norm = self._normalize(ingredient_name)
        if norm in self.chemicals_by_name:
            return self.chemicals_by_name[norm]
            
        # Check sub-phrases
        for indexed_name, entry in self.chemicals_by_name.items():
            if len(indexed_name) >= 4 and (indexed_name in norm or norm in indexed_name):
                return entry
        return None

    def find_hazards_in_list(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """Scans a list of ingredients and returns all flagged hazards."""
        matches = []
        for ing in ingredients:
            found = self.lookup(ing)
            if found:
                matches.append({
                    "scanned_name": ing,
                    "matched_id": found.get("id"),
                    "matched_name": found.get("name"),
                    "type": found.get("type", "moderate"),
                    "category": found.get("category", "General"),
                    "profile": found.get("profile", "")
                })
        return matches

hazard_dataset = HazardDataset()
