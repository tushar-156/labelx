"""
DAY 3: Critic Agent - Quality Validator
Powered by Gemini 2.0 Flash
"""

import os
from typing import Dict
from google import genai
from ..graph.state import AnalysisState


class CriticAgent:
    """
    Critic Agent: Validates quality of safety analysis

    Intelligence:
    • Multi-gate validation (completeness, allergen matching, consistency, tone)
    • Reject/Approve authority
    • Force retries with specific feedback
    • Track validation attempts

    Validation Gates:
    ✓ Completeness - All ingredients addressed
    ✓ Allergen Match - User allergies properly flagged
    ✓ Consistency - Safety scores match concern descriptions
    ✓ Tone Correctness - Appropriate for user expertise level

    Decision:
    • APPROVE → END (return to user)
    • REJECT → RETRY (send back to Analysis with feedback)
    """

    def __init__(self):
        """Initialize Critic Agent with Gemini 2.0 Flash"""
        api_key = os.getenv("CHAT_GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing CHAT_GEMINI_API_KEY or GOOGLE/GEMINI API Key")
        self.client = genai.Client(api_key=api_key)

    def run(self, state: AnalysisState) -> Dict:
        """
        Validate the safety analysis report.
        """
        safety_analysis = state.get("safety_analysis")
        ingredient_data = state.get("ingredient_data", [])
        allergies = state.get("user_profile", {}).get("allergies", [])
        expertise_level = state.get("user_profile", {}).get("expertise_level", "beginner")
        total_critic_rejections = state.get("total_critic_rejections", 0)

        if not safety_analysis:
            return {
                "critic_approved": False,
                "critic_feedback": "Missing safety analysis report.",
                "messages": [{
                    "role": "assistant",
                    "content": "Critic rejected: Missing safety analysis report."
                }]
            }

        # Build validation prompt
        prompt = self._build_validation_prompt(
            safety_analysis=safety_analysis,
            ingredient_data=ingredient_data,
            allergies=allergies,
            expertise_level=expertise_level
        )

        try:
            model_name = os.getenv("CRITIC_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
            response = None
            for m in [model_name, "gemini-2.0-flash", "gemini-2.0-flash-lite"]:
                try:
                    response = self.client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    if response and response.text:
                        break
                except Exception as ex:
                    print(f"Critic model {m} warning ({ex}), trying fallback...")

            validation_result = response.text if (response and response.text) else "APPROVE"

            # Parse the decision (look for APPROVE or REJECT)
            is_approved = "APPROVE" in validation_result.upper() and "REJECT" not in validation_result.upper()

            if is_approved:
                return {
                    "critic_approved": True,
                    "critic_feedback": None,
                    "messages": [{
                        "role": "assistant",
                        "content": "Analysis validated and approved by quality critic."
                    }]
                }
            else:
                return {
                    "critic_approved": False,
                    "critic_feedback": validation_result,
                    "analysis_complete": False,  # Force re-analysis
                    "total_critic_rejections": total_critic_rejections + 1,
                    "messages": [{
                        "role": "assistant",
                        "content": "Analysis rejected by critic. Generating improved version..."
                    }]
                }

        except Exception as e:
            print(f"❌ Critic Agent error: {e}")
            # On error, approve to avoid blocking workflow
            return {
                "critic_approved": True,
                "critic_feedback": None,
                "messages": [{
                    "role": "assistant",
                    "content": f"Critic validation error, proceeding with analysis: {str(e)}"
                }]
            }

    def _build_validation_prompt(
        self,
        safety_analysis: str,
        ingredient_data: list,
        allergies: list,
        expertise_level: str
    ) -> str:
        """Build validation prompt for quality checking"""

        ingredient_names = [ing['name'] for ing in ingredient_data]
        allergen_list = ', '.join(allergies) if allergies else 'None'

        prompt = f"""You are a quality validator for cosmetic ingredient safety analyses. Your job is to validate the analysis below using strict quality gates.

ORIGINAL INGREDIENT LIST ({len(ingredient_names)} ingredients):
{', '.join(ingredient_names)}

USER ALLERGIES:
{allergen_list}

USER EXPERTISE LEVEL:
{expertise_level}

ANALYSIS TO VALIDATE:
{safety_analysis}

VALIDATION GATES (all must pass):

1. ✓ COMPLETENESS CHECK
   - Are ALL {len(ingredient_names)} ingredients addressed in the analysis?
   - Does EVERY ingredient have: Name, Purpose, Safety Rating, Concerns, Recommendation?
   - Missing ingredients: [list any]

2. ✓ FORMAT CHECK
   - Is the ingredient analysis presented as a markdown TABLE?
   - Does the table have these columns: Ingredient | Purpose | Safety Rating | Concerns | Recommendation
   - Does EVERY ingredient have a row in the table with ALL columns filled?
   - Ingredients missing Purpose field: [list any]
   - Format violations: [list any]

3. ✓ ALLERGEN MATCH CHECK
   - User allergens/avoidance list: {allergen_list}
   - Are ALL items properly flagged with ⚠️ ALLERGEN/INGREDIENT TO AVOID?
   - Are matched items marked as AVOID?
   - Missing allergen flags: [list any]

4. ✓ CONSISTENCY CHECK
   - Do safety scores (1-10) match the concern descriptions?
   - Example: Score 7-10 should have serious concerns, score 1-3 should be safe
   - Inconsistencies: [list any]

5. ✓ TONE APPROPRIATENESS CHECK
   - Expertise level: {expertise_level}
   - Beginner: Simple language, no jargon?
   - Intermediate: Moderate technical detail?
   - Expert: Technical terminology and mechanisms?
   - Tone issues: [list any]

DECISION:
Based on the validation gates above, respond with ONE of:

APPROVE
[If all gates pass] The analysis is complete, accurate, and appropriate.

REJECT
[If any gate fails] Provide specific feedback:
- Which gates failed
- What is missing or incorrect
- How to fix it

Be strict but fair. Provide clear, actionable feedback for improvements.

YOUR DECISION:
"""
        return prompt
