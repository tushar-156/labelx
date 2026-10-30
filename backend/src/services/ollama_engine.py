"""
100% Offline / Private Local LLM Inference Engine for LabelX
Inspired by ai-nutri-lens:
  - Eliminates cloud API costs and keeps sensitive user health data strictly on-premise
  - Direct integration with local Ollama daemon (Llama 3, Mistral, Qwen, or Phi-3)
  - Configurable timeout and robust fallback error handling
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class OfflineInferenceResult(BaseModel):
    is_offline: bool = True
    model_used: str
    product_type: str
    safety_rating: int  # 1 to 10
    verdict: str
    composition_analysis: str
    raw_response: str
    status: str  # 'success', 'daemon_unavailable', 'error'

class OllamaOfflineEngine:
    """Local LLM inference client for Ollama."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")

    def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def analyze_ingredients_locally(
        self, 
        ingredients: List[str], 
        context_region: str = "Global / FSSAI / CIS",
        custom_instructions: Optional[str] = None
    ) -> OfflineInferenceResult:
        """
        Runs complete local analysis on Ollama with privacy preservation.
        """
        if not ingredients:
            return OfflineInferenceResult(
                model_used=self.model,
                product_type="Unknown",
                safety_rating=5,
                verdict="No ingredients provided.",
                composition_analysis="Empty input list.",
                raw_response="",
                status="error"
            )

        ingredients_str = ", ".join(ingredients)
        prompt = f"""
You are an expert chemical, cosmetic, and nutritional safety analyst.
CONTEXT & MARKET REGULATIONS: {context_region}
INGREDIENTS TO ANALYZE:
{ingredients_str}

Please perform an objective breakdown:
1. Product Category & Type: (Food, Beverage, Skincare, Haircare, etc.)
2. Additive & Safety Analysis: (Check for high-risk preservatives, synthetic dyes, endocrine disruptors, allergens)
3. Processing & Composition Purity: (Evaluate clean-label status and ultra-processing level)
4. Health & Safety Verdict: (Provide clear guidance for everyday consumers)
5. Safety Score: (An integer rating from 1 to 10, where 10 is completely harmless/natural and 1 is hazardous)

Respond in a structured format:
PRODUCT_TYPE: <type>
SAFETY_SCORE: <integer 1-10>
VERDICT: <concise summary verdict>
ANALYSIS: <bullet points explaining key findings>
"""
        if custom_instructions:
            prompt += f"\nADDITIONAL INSTRUCTION: {custom_instructions}"

        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            }

            resp = requests.post(url, json=payload, timeout=45)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")

            raw_text = resp.json().get("response", "").strip()

            # Parse key-values from formatted text
            p_type = "Consumer Product"
            score = 7
            verdict = "Analyzed offline via local Ollama."
            analysis = raw_text

            for line in raw_text.splitlines():
                if line.startswith("PRODUCT_TYPE:"):
                    p_type = line.replace("PRODUCT_TYPE:", "").strip()
                elif line.startswith("SAFETY_SCORE:"):
                    score_str = line.replace("SAFETY_SCORE:", "").strip()
                    try:
                        import re
                        m = re.search(r'\d+', score_str)
                        if m: score = int(m.group(0))
                    except Exception:
                        pass
                elif line.startswith("VERDICT:"):
                    verdict = line.replace("VERDICT:", "").strip()

            return OfflineInferenceResult(
                is_offline=True,
                model_used=self.model,
                product_type=p_type,
                safety_rating=min(10, max(1, score)),
                verdict=verdict,
                composition_analysis=analysis,
                raw_response=raw_text,
                status="success"
            )

        except requests.exceptions.RequestException as e:
            return OfflineInferenceResult(
                is_offline=True,
                model_used=self.model,
                product_type="Unknown",
                safety_rating=5,
                verdict="Local Ollama daemon is offline or unreachable at http://localhost:11434.",
                composition_analysis=f"Ensure Ollama is started (`ollama run {self.model}`). Error: {e}",
                raw_response="",
                status="daemon_unavailable"
            )
        except Exception as e:
            return OfflineInferenceResult(
                is_offline=True,
                model_used=self.model,
                product_type="Unknown",
                safety_rating=5,
                verdict=f"Error executing offline inference: {e}",
                composition_analysis=str(e),
                raw_response="",
                status="error"
            )

ollama_engine = OllamaOfflineEngine()
