"""
Interactive Conversational Label Q&A Agent
Provides natural language question answering grounded strictly on the product's
OCR text, ingredient monographs, 4-quadrant breakdown, and allergen flags.
Ported & enhanced from LabelLens.
"""

import os
import re
from typing import Dict, Any, List, Optional
from scripts.stub_llm import DualModeLLM

class LabelQAAgent:
    def __init__(self, prefer_local: bool = True):
        self.llm = DualModeLLM(prefer_local=prefer_local)

    def answer_question(
        self,
        question: str,
        product_name: str,
        category: str,
        physical_state: str,
        ingredients: List[str],
        claims: List[Dict[str, str]],
        allergen_report: Optional[Dict[str, Any]] = None,
        adulteration_alerts: Optional[List[Dict[str, Any]]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Answers a user question grounded strictly on the scanned label evidence.
        """
        # Grounding context block
        context_lines = [
            f"PRODUCT NAME: {product_name or 'Scanned Product'}",
            f"CATEGORY: {category} (Physical Matrix: {physical_state.upper()})",
            f"VERIFIED INGREDIENTS ({len(ingredients)} items): {', '.join(ingredients)}",
        ]

        if claims:
            context_lines.append("MARKETING CLAIMS:")
            for c in claims:
                context_lines.append(f"- Claim: '{c.get('claim')}' -> Verdict: {c.get('verdict')} ({c.get('truth')})")

        if allergen_report and allergen_report.get("allergens_found"):
            context_lines.append(f"FLAGGED ALLERGENS: {', '.join(allergen_report.get('allergens_found'))}")

        if adulteration_alerts:
            context_lines.append("ADULTERATION & HIDDEN ADDITIVES:")
            for a in adulteration_alerts:
                context_lines.append(f"- {a.get('title')}: {a.get('message')}")

        context_str = "\n".join(context_lines)

        prompt = f"""You are LabelX Clinical & Consumer Q&A Assistant.
Answer the user's specific product question truthfully and strictly grounded in the provided label facts.

LABEL CONTEXT:
{context_str}

USER QUESTION:
{question}

RULES:
1. Ground your answer strictly in the ingredients and chemical facts above.
2. If the user asks about diabetes, check for high-GI sugars (maltodextrin, dextrose, syrups) and physical state (liquids spike faster).
3. If the user asks about allergies, skin sensitivity, or dietary restrictions (vegan, gluten, dairy), check the allergen and ingredient flags.
4. If an ingredient or claim is missing or ambiguous, state clearly that the label does not disclose it.
5. Keep the response concise, authoritative, and helpful for the consumer.
"""

        # Generate response
        res = self.llm.generate_analysis(prompt)
        answer_text = res.get("text", "")

        # Format if stub response returned table
        if "###" in answer_text and "|" in answer_text and len(answer_text) > 300:
            # Deterministic conversational summary if stub returned default table
            answer_text = f"Based on the scanned formulation of {product_name or 'this product'}, it contains {len(ingredients)} verified ingredient(s). "
            q_lower = question.lower()
            if "diabet" in q_lower or "sugar" in q_lower:
                sugars = [i for i in ingredients if any(s in i.lower() for s in ["sugar", "maltodextrin", "dextrose", "syrup", "honey"])]
                if sugars:
                    answer_text += f"Caution for blood glucose management: contains {', '.join(sugars)}."
                else:
                    answer_text += "No high-glycemic sugar syrups or added sugars were detected in the visible ingredient panel."
            elif "allerg" in q_lower or "sensitiv" in q_lower:
                if allergen_report and allergen_report.get("allergens_found"):
                    answer_text += f"Flagged potential contact sensitizers: {', '.join(allergen_report['allergens_found'])}."
                else:
                    answer_text += "No major standard allergens or EU Annex III fragrance sensitizers were detected."
            elif "vegan" in q_lower or "animal" in q_lower:
                non_veg = [i for i in ingredients if any(nv in i.lower() for nv in ["gelatin", "carmine", "milk", "whey", "honey", "beeswax", "shellac"])]
                if non_veg:
                    answer_text += f"Potential non-vegan / animal-derived constituents detected: {', '.join(non_veg)}."
                else:
                    answer_text += "No overt animal-derived ingredients (like gelatin or carmine) were detected in the visible list."
            else:
                answer_text += f"The formulation is classified as {category} ({physical_state}). Always review local patch-test guidelines before intensive use."

        return {
            "question": question,
            "answer": answer_text.strip(),
            "product_name": product_name,
            "grounded": True
        }

label_qa_agent = LabelQAAgent()
