"""
DAY 3: Analysis Agent - Personalized Safety Analyst
Powered by Gemini 2.0 Flash
"""

import os
from typing import Dict
from google import genai
from ..graph.state import AnalysisState

def check_ingredient_conflict(ingredient1: str, ingredient2: str) -> str:
    """Checks if two cosmetic ingredients have known conflicts when used together."""
    conflicts = {
        ("retinol", "vitamin c"): "High risk of irritation. Use at different times.",
        ("retinol", "aha"): "High risk of irritation. Do not layer.",
        ("retinol", "bha"): "High risk of irritation. Do not layer.",
        ("vitamin c", "aha"): "Can destabilize vitamin C. Proceed with caution.",
        ("niacinamide", "vitamin c"): "Safe in modern formulations, but traditionally thought to conflict."
    }
    
    i1 = ingredient1.lower()
    i2 = ingredient2.lower()
    
    for (c1, c2), msg in conflicts.items():
        if (c1 in i1 and c2 in i2) or (c1 in i2 and c2 in i1):
            return msg
            
    return "No known conflicts between these ingredients."

class AnalysisAgent:
    """
    Analysis Agent: Generates personalized safety reports.
    
    Core Intelligence:
    - Cross-references gathered ingredient data with user profile
    - Determines overall safety status based on identified risks
    - Highlights critical warnings (allergens, severe conflicts)
    - Suggests alternative products or safer usage methods
    - Adapts language tone based on user expertise level
    
    Adaptive Behavior:
    • Beginner → Simple, clear language
    • Expert → Technical details and chemical explanations
    • High-risk ingredients → Bold warnings
    • Allergies → AVOID tags prominently displayed
    """

    def __init__(self):
        """Initialize Analysis Agent with Google GenAI Client"""
        api_key = os.getenv("CHAT_GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing CHAT_GEMINI_API_KEY or GOOGLE/GEMINI API Key")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("ANALYSIS_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"

    def run(self, state: AnalysisState) -> Dict:
        """
        Generate personalized safety analysis report

        Process:
        1. Get user profile and ingredient data from state
        2. Adapt analysis tone based on expertise level
        3. Cross-reference ingredients with user allergies
        4. Generate warnings for high-risk ingredients
        5. Format as structured report
        6. Self-validate completeness

        Args:
            state: Current workflow state

        Returns:
            Updated state with safety_analysis and analysis_complete flag
        """

        ingredient_data = state.get("ingredient_data", [])
        user_name = state.get("user_name", "User")
        skin_type = state.get("skin_type", "normal")
        allergies = state.get("allergies", [])
        routine = state.get("routine", [])
        expertise_level = state.get("expertise_level", "beginner")
        season = state.get("season", None)
        analysis_attempts = state.get("analysis_attempts", 0)
        critic_feedback = state.get("critic_feedback")

        if not ingredient_data:
            return {
                "analysis_complete": False,
                "analysis_attempts": analysis_attempts + 1,
                "messages": [{
                    "role": "assistant",
                    "content": "No ingredient data available for analysis."
                }]
            }

        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            ingredient_data=ingredient_data,
            user_name=user_name,
            skin_type=skin_type,
            allergies=allergies,
            routine=routine,
            expertise_level=expertise_level,
            season=season,
            critic_feedback=critic_feedback
        )

        try:
            # Google GenAI Best Practice with automatic model fallback for 503 high demand
            response = None
            for m in [self.model_name, "gemini-2.0-flash", "gemini-2.0-flash-lite"]:
                try:
                    chat = self.client.chats.create(
                        model=m,
                        config={
                            "temperature": 0.1,
                            "tools": [check_ingredient_conflict]
                        }
                    )
                    response = chat.send_message(prompt)
                    if response and response.text:
                        break
                except Exception as ex:
                    print(f"Analysis model {m} warning ({ex}), trying fallback...")

            if not response or not response.text:
                raise RuntimeError("All candidate models failed to generate safety analysis.")

            safety_analysis = response.text

            return {
                "analysis_complete": True,
                "safety_analysis": safety_analysis,
                "analysis_attempts": analysis_attempts + 1,
                "critic_feedback": None,  # Reset feedback after incorporating it
                "messages": [{
                    "role": "assistant",
                    "content": f"Generated personalized safety analysis for {len(ingredient_data)} ingredients."
                }]
            }

        except Exception as e:
            print(f"❌ Analysis Agent error: {e}")
            return {
                "analysis_complete": False,
                "analysis_attempts": analysis_attempts + 1,
                "messages": [{
                    "role": "assistant",
                    "content": f"Error generating analysis: {str(e)}"
                }]
            }

    def _build_analysis_prompt(
        self,
        ingredient_data: list,
        user_name: str,
        skin_type: str,
        allergies: list,
        routine: list,
        expertise_level: str,
        season: str = None,
        critic_feedback: str = None
    ) -> str:
        """Build analysis prompt adapted to user profile"""

        # Build ingredient summary
        ingredient_summary = "\n".join([
            f"- {ing['name']}: {ing.get('purpose', 'Unknown purpose')} "
            f"(Safety: {ing.get('safety_score', 'N/A')}, Concerns: {', '.join(ing.get('concerns', ['none']))})"
            for ing in ingredient_data
        ])

        # Adapt tone based on expertise
        tone_instruction = {
            "beginner": "Use simple, clear language. Avoid jargon. Focus on practical implications.",
            "intermediate": "Use moderate technical detail. Explain key concepts briefly.",
            "expert": "Use technical terminology. Include chemical mechanisms and research references."
        }.get(expertise_level, "Use clear, accessible language.")

        # Build base prompt
        prompt = f"""You are a cosmetic ingredient safety analyst. Generate a personalized safety analysis report.

USER PROFILE:
- Name: {user_name}
- Skin Type: {skin_type}
- Expertise Level: {expertise_level}
- Allergens/Ingredients to Avoid: {', '.join(allergies) if allergies else 'None'}
- Current Routine: {', '.join(routine) if routine else 'None'}
- Personal Color Season: {season if season else 'Unknown'}

INGREDIENTS TO ANALYZE:
{ingredient_summary}

INSTRUCTIONS:
1. {tone_instruction}
2. For EVERY SINGLE ingredient, you MUST provide ALL of the following in a TABLE format:
   - **Ingredient:** [Ingredient Name]
   - **Purpose:** [What this ingredient does - moisturizer, preservative, etc.]
   - **Safety Rating:** [1-10 scale, where 1=safest, 10=most concerning]
   - **Concerns:** [Specific safety concerns or "None known" if safe]
   - **Recommendation:** [SAFE / USE WITH CAUTION / AVOID]
3. Cross-reference ALL ingredients with user's allergen/avoidance list: {', '.join(allergies) if allergies else 'none'}
4. If any ingredient matches the user's list, mark it with "⚠️ ALLERGEN/INGREDIENT TO AVOID" in the Ingredient column and recommend AVOID
   - IMPORTANT: Use the term "Allergen/Ingredient to Avoid" - this covers both true allergies and preference-based avoidance
   - Reason: Some users have true allergies, others just prefer to avoid certain ingredients (e.g., alcohol-free or fragrance-free preference)
5. Adapt recommendations based on skin type ({skin_type})
6. Provide an overall verdict (SAFE TO USE / USE WITH CAUTION / AVOID)
7. Check for conflicts between the analyzed ingredients and the user's current routine ({', '.join(routine) if routine else 'none'}).
   - IMPORTANT: For example, Retinol conflicts with Vitamin C or AHA/BHA in the same application.
8. Color Analysis Alert: If the user's Personal Color Season is provided, add a short note in the recommendations on how these ingredients relate to creating a healthy canvas for their {season if season else 'unknown'} color palette, if applicable.
9. Keep the analysis concise and actionable

FORMAT EXAMPLE (FOLLOW THIS EXACTLY):
## Ingredient Analysis

| Ingredient | Purpose | Safety Rating | Concerns | Recommendation |
|------------|---------|---------------|----------|----------------|
| Aqua (Water) | Solvent and base ingredient | 1 | None known | SAFE |
| Glycolic Acid | Chemical exfoliant (AHA) | 4 | Can cause irritation, sun sensitivity | USE WITH CAUTION |
| Fragrance ⚠️ ALLERGEN/INGREDIENT TO AVOID | Adds scent to product | 7 | Potential allergen, irritation | AVOID |

## Allergen/Ingredient Check
[List any ingredients that match user's allergen/avoidance list]

## Routine Conflict Check
[List any potential conflicts between the new ingredients and the user's current routine, e.g., "Warning: Product contains Glycolic Acid which conflicts with Retinol in your current routine."]

## Overall Verdict
[Safe to use / Use with caution / Avoid - with brief reasoning]

## Recommendations for {skin_type.title()} Skin
[Specific guidance]
"""

        # Add critic feedback if this is a retry
        if critic_feedback:
            prompt += f"\n\nCRITIC FEEDBACK (incorporate these improvements):\n{critic_feedback}\n"

        return prompt
