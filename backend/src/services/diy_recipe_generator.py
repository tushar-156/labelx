"""
Healthy Home-Cooked DIY Recipe & Kitchen Swap Generator for LabelX
Adapted from Food-Label-Analyzer (ai_client.py)

Generates simple whole-food homemade recipes using kitchen staples to replace
ultra-processed commercial packaged foods.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class DIYRecipe(BaseModel):
    title: str
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: str  # 'Easy', 'Medium'
    target_craving: str
    ingredients: List[str]
    instructions: List[str]
    why_healthier: str
    eliminated_industrial_additives: List[str]

# Curated high-assurance whole-food kitchen recipes for common food categories
RECIPE_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "snack": [
        {
            "title": "Air-Fried Crispy Spiced Sweet Potato Wedges",
            "prep_time_minutes": 10,
            "cook_time_minutes": 15,
            "servings": 2,
            "difficulty": "Easy",
            "target_craving": "Crispy salty potato chips",
            "ingredients": [
                "2 medium sweet potatoes, sliced into thin wedges",
                "1 tbsp cold-pressed olive oil or avocado oil",
                "1/2 tsp smoked paprika & 1/4 tsp garlic powder",
                "Pink Himalayan rock salt & fresh cracked black pepper"
            ],
            "instructions": [
                "Wash, dry, and slice sweet potatoes into uniform wedges.",
                "Toss with olive oil, paprika, garlic powder, and rock salt in a bowl.",
                "Air-fry at 195°C (385°F) for 14-16 minutes, shaking halfway until crisp and golden.",
                "Cool for 2 minutes and serve warm."
            ],
            "why_healthier": "Provides rich beta-carotene, complex dietary fiber, and natural potassium. Zero palmolein, zero TBHQ antioxidant, and 80% less sodium.",
            "eliminated_industrial_additives": ["TBHQ (E319)", "Palmolein", "Monosodium Glutamate (E621)", "Maltodextrin"]
        },
        {
            "title": "Crunchy Lemon Herb Roasted Chickpeas",
            "prep_time_minutes": 5,
            "cook_time_minutes": 20,
            "servings": 3,
            "difficulty": "Easy",
            "target_craving": "Savory extruded puffs / namkeen",
            "ingredients": [
                "1.5 cups cooked or canned chickpeas (rinsed and thoroughly dried)",
                "1 tbsp extra virgin olive oil",
                "1/2 tsp ground cumin, 1/4 tsp turmeric, pinch of cayenne",
                "Fresh lemon zest and sea salt"
            ],
            "instructions": [
                "Pat chickpeas completely dry using a kitchen towel (essential for crunch).",
                "Toss with olive oil, cumin, turmeric, and sea salt.",
                "Bake at 200°C (400°F) for 20-25 minutes until deeply crunchy.",
                "Toss with fresh lemon zest and let cool to room temperature."
            ],
            "why_healthier": "High-protein plant snack with 7g fiber per serving. Stabilizes blood glucose without refined starch spikes.",
            "eliminated_industrial_additives": ["Artificial Flavors", "Synthetic Colorants (Tartrazine)", "Preservatives"]
        }
    ],
    "beverage": [
        {
            "title": "Sparkling Hibiscus Berry Cooler",
            "prep_time_minutes": 5,
            "cook_time_minutes": 5,
            "servings": 2,
            "difficulty": "Easy",
            "target_craving": "High-sugar soda / fizzy soft drinks",
            "ingredients": [
                "2 dried hibiscus flower tea bags (or 1 tbsp loose dried hibiscus)",
                "1 cup boiling water",
                "1 cup chilled sparkling mineral water / club soda",
                "1 tsp raw honey or pure monk fruit drops (optional)",
                "Fresh mint leaves and lime wedges"
            ],
            "instructions": [
                "Steep hibiscus in boiling water for 5 minutes, then cool completely in the fridge.",
                "Fill glasses with ice cubes, fresh mint, and lime wedges.",
                "Pour equal parts hibiscus concentrate and sparkling water.",
                "Stir and enjoy an effervescent antioxidant refresher."
            ],
            "why_healthier": "Naturally packed with anthocyanins that support cardiovascular health. Zero High Fructose Corn Syrup, phosphoric acid, or synthetic dyes.",
            "eliminated_industrial_additives": ["High Fructose Corn Syrup (HFCS)", "Phosphoric Acid (E338)", "Caramel Color (E150d)", "Sodium Benzoate (E211)"]
        }
    ],
    "biscuit": [
        {
            "title": "3-Ingredient Banana Oat Chia Breakfast Cookies",
            "prep_time_minutes": 8,
            "cook_time_minutes": 12,
            "servings": 4,
            "difficulty": "Easy",
            "target_craving": "Packaged cream biscuits / cookies",
            "ingredients": [
                "2 ripe bananas, mashed smooth",
                "1 cup rolled oats",
                "1 tbsp chia seeds & 1/2 tsp ground cinnamon",
                "2 tbsp dark chocolate chips (70%+ cacao, optional)"
            ],
            "instructions": [
                "Preheat oven to 180°C (350°F) and line a baking sheet with parchment.",
                "Mix mashed bananas, rolled oats, chia seeds, and cinnamon until a thick batter forms.",
                "Scoop tablespoons of dough onto baking sheet and flatten slightly into rounds.",
                "Bake for 12-14 minutes until golden at the edges."
            ],
            "why_healthier": "100% naturally sweetened by fruit fructose and resistant starch. Contains zero hydrogenated vegetable shortening or artificial emulsifiers.",
            "eliminated_industrial_additives": ["Hydrogenated Palm Fat (Trans Fats)", "Invert Syrup", "Soy Lecithin (E322)", "Artificial Vanillin"]
        }
    ]
}

def generate_diy_recipes(category: str, product_name: Optional[str] = None) -> List[DIYRecipe]:
    """
    Returns 2 tailored healthy kitchen recipes to replace the analyzed processed food.
    """
    cat_lower = category.lower() if category else "snack"

    matched_key = "snack"
    if any(k in cat_lower for k in ["beverage", "drink", "soda", "juice", "tea", "coffee"]):
        matched_key = "beverage"
    elif any(k in cat_lower for k in ["biscuit", "cookie", "confectionery", "chocolate", "sweet", "cake"]):
        matched_key = "biscuit"

    raw_recipes = RECIPE_CATALOG.get(matched_key, RECIPE_CATALOG["snack"])
    results = [DIYRecipe(**r) for r in raw_recipes]
    return results
