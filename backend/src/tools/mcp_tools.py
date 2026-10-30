"""
DAY 3: FastMCP Custom Tools
Built with FastMCP for agent tool calling
"""

import os
import json
from pathlib import Path
import warnings
from typing import Dict, List, Optional
import pandas as pd
from rapidfuzz import process, fuzz
from tavily import TavilyClient

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import FAISS
from src.tools.bm25_retriever import HybridIngredientRetriever
class IngredientTools:
    """
    Custom tools for ingredient analysis
    Designed to be exposed via FastMCP server
    """

    def __init__(self):
        """Initialize tools with FAISS, embedding model, and Tavily"""
        self.index_path = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
        self.embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        if os.path.exists(self.index_path):
            self.vectorstore = FAISS.load_local(self.index_path, self.embedding_model, allow_dangerous_deserialization=True)
        else:
            self.vectorstore = None
            print(f"Warning: FAISS index not found at {self.index_path}")

        # Initialize Tavily for web search fallback
        tavily_key = (os.getenv("TAVILY_API_KEY") or "").strip()
        if "tavilyApiKey=" in tavily_key:
            tavily_key = tavily_key.split("tavilyApiKey=")[-1].split("&")[0]
        self.tavily_client = TavilyClient(api_key=tavily_key) if tavily_key else None

        # Load local databases for fuzzy matching and brand ethics
        self.db_df = None
        self.search_terms = []
        self.terms_only = []
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "ingredients_database.csv")
        if os.path.exists(db_path):
            self.db_df = pd.read_csv(db_path, encoding='latin-1')
            for idx, row in self.db_df.iterrows():
                self.search_terms.append((str(row['ingredient_name']).lower().strip(), idx))
                if pd.notna(row['common_aliases']):
                    for alias in str(row['common_aliases']).split(','):
                        alias = alias.lower().strip()
                        if alias:
                            self.search_terms.append((alias, idx))
            self.terms_only = [term for term, idx in self.search_terms]
        else:
            print(f"Warning: Local ingredients DB not found at {db_path}")

        self.brands_data = []
        brands_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "brands.json")
        if os.path.exists(brands_path):
            try:
                with open(brands_path, "r", encoding="utf-8") as f:
                    self.brands_data = json.load(f)
            except:
                print(f"Warning: Failed to load brands DB at {brands_path}")

        # Initialize Hybrid BM25 + Dense RRF Retriever with Double-Refusal Abstention
        self.hybrid_retriever = HybridIngredientRetriever(self.db_df, self.vectorstore)

    def ingredient_lookup(self, ingredient_name: str) -> Dict:
        """
        Tool 1: Query Hybrid BM25 + Dense RRF Retriever for ingredient information.
        Enforces double-refusal abstention when out-of-corpus.
        """
        try:
            # 1. Run Hybrid BM25 + Dense RRF retrieval
            hybrid_res = self.hybrid_retriever.retrieve(ingredient_name)

            # If out-of-corpus, trigger strict double-refusal abstention
            if hybrid_res.get("is_uncovered"):
                return {
                    "name": ingredient_name,
                    "purpose": "Uncovered / No Authoritative Entry",
                    "safety_score": None,
                    "concerns": ["Unverified in official regulatory corpus"],
                    "description": hybrid_res.get("reason", "Out of corpus"),
                    "confidence": 0.0,
                    "source": "uncovered_abstention",
                    "is_uncovered": True,
                    "citations": []
                }

            s_level = hybrid_res.get("concern_level", "Safe")
            num_score = 10 if s_level == 'Avoid' else (6 if s_level == 'Caution' else 2)

            return {
                "name": hybrid_res.get("name", ingredient_name),
                "purpose": hybrid_res.get("benefits") or "Conditioning / Active Agent",
                "safety_score": num_score,
                "concerns": [s_level],
                "description": hybrid_res.get("description", ""),
                "confidence": hybrid_res.get("confidence", 0.85),
                "source": "hybrid_bm25_dense_rrf",
                "is_uncovered": False,
                "citations": hybrid_res.get("citations", []),
                "passages": hybrid_res.get("passages", [])
            }

        except Exception as e:
            print(f"Notice: Hybrid lookup fallback ({e})")
            return {
                "name": ingredient_name,
                "purpose": "Unknown",
                "safety_score": None,
                "concerns": ["Lookup unavailable"],
                "description": "",
                "confidence": 0.0,
                "source": "error",
                "is_uncovered": True,
                "citations": []
            }


    def safety_scorer(
        self,
        ingredient_data: Dict,
        user_skin_type: str = "normal",
        user_allergies: List[str] = None
    ) -> Dict:
        """
        Tool 2: Calculate personalized safety score

        Factors:
        - Base safety score from ingredient data
        - User skin type compatibility
        - Allergen matching

        Args:
            ingredient_data: Dict from ingredient_lookup
            user_skin_type: normal, sensitive, oily, dry, combination
            user_allergies: List of user's allergens

        Returns:
            {
                "personalized_score": float (1-10),
                "base_score": int (1-10),
                "adjustments": List[str],
                "recommendation": str (SAFE/CAUTION/AVOID),
                "reasoning": str
            }
        """
        user_allergies = user_allergies or []

        ingredient_name = ingredient_data.get("name", "Unknown")
        concerns = str(ingredient_data.get("concerns", [])).lower()

        # Start with max score (SkinWise 100-point logic)
        personalized_score = 100
        adjustments = []
        reasoning_parts = []

        # Find base severity from data
        is_avoid = "avoid" in concerns
        is_caution = "caution" in concerns

        # Adjustment 1: Allergen check (Immediate -100 or huge penalty)
        if self.is_allergen_match(ingredient_name, user_allergies):
            personalized_score -= 100
            adjustments.append("Allergen match: -100 points")
            reasoning_parts.append(f"ALLERGEN MATCH: {ingredient_name} matches your allergy list")

        # Adjustment 2: Skin type compatibility
        if user_skin_type == "sensitive":
            if any(concern in concerns for concern in ["irritation", "allergic", "sensitizing"]):
                personalized_score -= 10
                is_avoid = True
                adjustments.append("Sensitive skin: -10 points for irritation concerns")
                reasoning_parts.append("Higher concern for sensitive skin due to irritation risk")

        if user_skin_type == "oily":
            if "comedogenic" in concerns or "clog" in concerns:
                personalized_score -= 10
                is_avoid = True
                adjustments.append("Oily skin: -10 points for comedogenic risk")
                reasoning_parts.append("May clog pores on oily skin")
                
        if user_skin_type == "dry":
            if "drying" in concerns or "alcohol" in concerns or "astringent" in concerns:
                personalized_score -= 10
                is_avoid = True
                adjustments.append("Dry skin: -10 points for drying effect")
                reasoning_parts.append("May further strip moisture from dry skin")

        # Standard penalties if flagged but not dynamically caught
        if is_avoid and not adjustments:
            personalized_score -= 10
            adjustments.append("Avoid flagged ingredient: -10 points")
            reasoning_parts.append("Ingredient flagged to avoid generally")
        elif is_caution and not adjustments:
            personalized_score -= 3
            adjustments.append("Caution flagged ingredient: -3 points")
            reasoning_parts.append("Ingredient requires caution")

        # Floor score
        personalized_score = max(0, personalized_score)

        # Determine recommendation
        if personalized_score < 80:
            recommendation = "AVOID"
        elif personalized_score < 100:
            recommendation = "USE WITH CAUTION"
        else:
            recommendation = "SAFE"

        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Generally safe for your profile"

        return {
            "personalized_score": personalized_score,
            "base_score": 100 if not (is_avoid or is_caution) else (90 if is_avoid else 97),
            "adjustments": adjustments,
            "recommendation": recommendation,
            "reasoning": reasoning
        }

    def predict_cheminformatics(self, ingredient_name: str) -> Dict:
        """
        Tool: Compute in silico molecular descriptors, Potts-Guy dermal permeability (Kp),
        and toxicological proxy endpoints for an ingredient.
        """
        from .cheminformatics import get_cheminformatics_dossier
        return get_cheminformatics_dossier(ingredient_name)
        
    def brand_ethics_lookup(self, brand_name: str) -> Dict:
        """
        Tool: Check brand against the EthiScan database (cruelty-free / vegan)
        """
        if not self.brands_data:
            return {"brand": brand_name, "found": False, "status": "Database unavailable"}
            
        brand_lower = brand_name.lower().strip()
        
        # Exact match
        for brand in self.brands_data:
            if brand.get("name", "").lower() == brand_lower:
                return {"brand": brand.get("name"), "found": True, "cruelty_free": brand.get("is_cruelty_free"), "vegan": brand.get("is_vegan")}
                
        # Fuzzy match
        brand_names = [b.get("name", "") for b in self.brands_data]
        result = process.extractOne(brand_lower, brand_names, scorer=fuzz.token_sort_ratio)
        if result:
            matched_term, fuzzy_score, term_index = result
            if fuzzy_score >= 85:
                brand = self.brands_data[term_index]
                return {"brand": brand.get("name"), "found": True, "cruelty_free": brand.get("is_cruelty_free"), "vegan": brand.get("is_vegan")}
                
        return {"brand": brand_name, "found": False, "status": "Not found in ethics database"}

    def allergen_matcher(self, ingredient_name: str, user_allergies: List[str]) -> Dict:
        """
        Tool 3: Check if ingredient matches user allergies

        Handles:
        - Exact name matching
        - Synonym matching
        - Chemical name variations

        Args:
            ingredient_name: Ingredient to check
            user_allergies: List of user's allergens

        Returns:
            {
                "is_match": bool,
                "matched_allergen": str or None,
                "match_type": str (exact/synonym/chemical)
            }
        """
        is_match, matched_allergen = self.is_allergen_match(ingredient_name, user_allergies)

        if is_match:
            # Determine match type
            if matched_allergen.lower() == ingredient_name.lower():
                match_type = "exact"
            elif matched_allergen.lower() in ingredient_name.lower() or ingredient_name.lower() in matched_allergen.lower():
                match_type = "partial"
            else:
                match_type = "synonym"
        else:
            match_type = None

        return {
            "is_match": is_match,
            "matched_allergen": matched_allergen,
            "match_type": match_type
        }

    def is_allergen_match(self, ingredient_name: str, user_allergies: List[str]) -> tuple:
        """
        Helper: Check if ingredient matches any user allergen

        Returns:
            (is_match: bool, matched_allergen: str or None)
        """
        ingredient_lower = ingredient_name.lower()

        # Common synonym mappings
        synonym_map = {
            "fragrance": ["parfum", "perfume", "fragrance"],
            "parfum": ["fragrance", "perfume", "parfum"],
            "vitamin e": ["tocopherol", "tocopheryl acetate"],
            "alcohol": ["alcohol denat", "ethanol", "ethyl alcohol"],
            "retinol": ["retinyl palmitate", "retinoic acid", "tretinoin"]
        }

        for allergen in user_allergies:
            allergen_lower = allergen.lower()

            # Exact match
            if allergen_lower == ingredient_lower:
                return (True, allergen)

            # Partial match (ingredient contains allergen or vice versa)
            if allergen_lower in ingredient_lower or ingredient_lower in allergen_lower:
                return (True, allergen)

            # Synonym match
            for key, synonyms in synonym_map.items():
                if allergen_lower == key or allergen_lower in synonyms:
                    if any(syn in ingredient_lower for syn in synonyms):
                        return (True, allergen)

        return (False, None)

    def tavily_search(self, ingredient_name: str) -> Dict:
        """
        Tool 4: Web search for ingredients not in database (Fallback)

        Uses Tavily API to search the web for ingredient safety information
        when Qdrant confidence is low (<0.7) or ingredient not found.

        Args:
            ingredient_name: Ingredient to research

        Returns:
            {
                "name": str,
                "purpose": str,
                "safety_score": int (estimated 1-10),
                "concerns": List[str],
                "description": str,
                "confidence": float (0-1),
                "source": str
            }
        """
        if not self.tavily_client:
            print("[WARNING] Tavily API key not configured. Returning placeholder.")
            return {
                "name": ingredient_name,
                "purpose": "Web search unavailable",
                "safety_score": 5,
                "concerns": ["No web search available"],
                "description": "Tavily API key not configured",
                "confidence": 0.3,
                "source": "tavily_unavailable"
            }

        try:
            # Search for ingredient safety information
            search_query = f"{ingredient_name} cosmetic skincare ingredient safety concerns benefits"

            response = self.tavily_client.search(
                query=search_query,
                max_results=3,
                search_depth="advanced"
            )

            if not response or "results" not in response or not response["results"]:
                return {
                    "name": ingredient_name,
                    "purpose": "Unknown",
                    "safety_score": 5,
                    "concerns": ["No web results found"],
                    "description": "",
                    "confidence": 0.2,
                    "source": "tavily_no_results"
                }

            # Extract information from top results
            results = response["results"]
            combined_content = " ".join([r.get("content", "") for r in results[:3]])

            # Simple keyword-based analysis (in production, use LLM to parse)
            purpose = "Unknown purpose"
            concerns = []
            safety_score = 5  # Neutral default

            # Extract purpose clues
            if any(word in combined_content.lower() for word in ["moisturizer", "hydrat"]):
                purpose = "Moisturizing agent"
            elif any(word in combined_content.lower() for word in ["preservative", "antimicrobial"]):
                purpose = "Preservative"
            elif any(word in combined_content.lower() for word in ["antioxidant", "vitamin"]):
                purpose = "Antioxidant"
            elif any(word in combined_content.lower() for word in ["surfactant", "cleanser"]):
                purpose = "Cleansing agent"
            elif any(word in combined_content.lower() for word in ["emulsifier", "stabilizer"]):
                purpose = "Emulsifier"
            elif any(word in combined_content.lower() for word in ["fragrance", "scent", "perfume"]):
                purpose = "Fragrance"

            # Detect concerns
            if any(word in combined_content.lower() for word in ["irritat", "sensitiz", "allergic"]):
                concerns.append("potential irritation")
                safety_score = max(6, safety_score)
            if any(word in combined_content.lower() for word in ["toxic", "harmful", "danger"]):
                concerns.append("toxicity concerns")
                safety_score = max(7, safety_score)
            if any(word in combined_content.lower() for word in ["comedogenic", "acne", "clog"]):
                concerns.append("may clog pores")
                safety_score = max(6, safety_score)
            if any(word in combined_content.lower() for word in ["safe", "gentle", "mild"]):
                safety_score = min(3, safety_score)
                if not concerns:
                    concerns.append("generally safe")

            if not concerns:
                concerns = ["insufficient data"]

            # Confidence based on result quality
            confidence = 0.6 if len(results) >= 2 else 0.4

            return {
                "name": ingredient_name,
                "purpose": purpose,
                "safety_score": safety_score,
                "concerns": concerns,
                "description": combined_content[:300] + "..." if len(combined_content) > 300 else combined_content,
                "confidence": confidence,
                "source": "tavily_web_search"
            }

        except Exception as e:
            print(f"[ERROR] Tavily search error: {e}")
            return {
                "name": ingredient_name,
                "purpose": "Search error",
                "safety_score": 5,
                "concerns": [f"Web search error: {str(e)}"],
                "description": "",
                "confidence": 0.1,
                "source": "tavily_error"
            }


# Singleton instance
_tools_instance = None

def get_tools() -> IngredientTools:
    """Get singleton instance of tools"""
    global _tools_instance
    if _tools_instance is None:
        _tools_instance = IngredientTools()
    return _tools_instance
