"""
Cumulative Daily Nutrient & Additive Budget Tracker for LabelX
Inspired by Food-Label-Analyzer (food_logger.py) & BeyondLabel
Maintains a persistent daily log of nutritional intake and tracks against WHO / ICMR limits.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "daily_food_log.json")

# WHO / ICMR Statutory Daily Maximum Allowances for Adults
WHO_DAILY_ALLOWANCES = {
    "added_sugar_g": 25.0,      # Max 25g/day (6 teaspoons)
    "sodium_mg": 2000.0,        # Max 2000mg/day (5g table salt)
    "saturated_fat_g": 20.0,    # Max 20g/day
    "calories_kcal": 2000.0,    # 2000 kcal standard baseline
    "chemical_additives_count": 5 # Prudent daily threshold for synthetic additives
}

class IntakeLogEntry(BaseModel):
    id: str
    timestamp: str
    date: str
    product_name: str
    serving_fraction: float = 1.0
    sugar_g: float = 0.0
    sodium_mg: float = 0.0
    saturated_fat_g: float = 0.0
    calories_kcal: float = 0.0
    additives_count: int = 0
    harmful_additives: List[str] = []

class DailyBudgetReport(BaseModel):
    date: str
    entries_count: int
    total_sugar_g: float
    total_sodium_mg: float
    total_saturated_fat_g: float
    total_calories_kcal: float
    total_additives_consumed: int
    sugar_budget_pct: float
    sodium_budget_pct: float
    saturated_fat_budget_pct: float
    calories_budget_pct: float
    alerts: List[str]
    recent_entries: List[Dict[str, Any]]

def _load_all_logs() -> List[dict]:
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_all_logs(logs: List[dict]):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def log_food_intake(
    product_name: str,
    nutritional_info: Optional[dict] = None,
    additives_list: Optional[List[str]] = None,
    serving_fraction: float = 1.0
) -> DailyBudgetReport:
    """Logs scanned product consumption and returns the updated daily budget report."""
    logs = _load_all_logs()
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    nutri = nutritional_info or {}
    sugar = float(nutri.get("sugar_g") or 0.0) * serving_fraction
    sodium = float(nutri.get("sodium_mg") or 0.0) * serving_fraction
    sat_fat = float(nutri.get("saturated_fat_g") or 0.0) * serving_fraction
    calories = float(nutri.get("energy_kcal") or 0.0) * serving_fraction
    additives = additives_list or []

    entry = {
        "id": f"log_{int(now.timestamp() * 1000)}",
        "timestamp": now.isoformat(),
        "date": today_str,
        "product_name": product_name,
        "serving_fraction": serving_fraction,
        "sugar_g": round(sugar, 1),
        "sodium_mg": round(sodium, 1),
        "saturated_fat_g": round(sat_fat, 1),
        "calories_kcal": round(calories, 1),
        "additives_count": len(additives),
        "harmful_additives": additives
    }
    logs.append(entry)
    _save_all_logs(logs)

    return get_daily_budget_report(today_str)

def get_daily_budget_report(target_date: Optional[str] = None) -> DailyBudgetReport:
    """Computes daily cumulative totals and budget percentage vs WHO thresholds."""
    date_str = target_date or datetime.now().strftime("%Y-%m-%d")
    logs = _load_all_logs()
    day_entries = [e for e in logs if e.get("date") == date_str]

    tot_sugar = sum(e.get("sugar_g", 0.0) for e in day_entries)
    tot_sodium = sum(e.get("sodium_mg", 0.0) for e in day_entries)
    tot_sat_fat = sum(e.get("saturated_fat_g", 0.0) for e in day_entries)
    tot_calories = sum(e.get("calories_kcal", 0.0) for e in day_entries)
    tot_additives = sum(e.get("additives_count", 0) for e in day_entries)

    sugar_pct = round((tot_sugar / WHO_DAILY_ALLOWANCES["added_sugar_g"]) * 100, 1)
    sodium_pct = round((tot_sodium / WHO_DAILY_ALLOWANCES["sodium_mg"]) * 100, 1)
    sat_fat_pct = round((tot_sat_fat / WHO_DAILY_ALLOWANCES["saturated_fat_g"]) * 100, 1)
    cal_pct = round((tot_calories / WHO_DAILY_ALLOWANCES["calories_kcal"]) * 100, 1)

    alerts = []
    if sugar_pct >= 100:
        alerts.append(f"Sugar Limit Exceeded: {tot_sugar:.1f}g consumed ({sugar_pct}% of WHO max 25g daily limit).")
    elif sugar_pct >= 80:
        alerts.append(f"Approaching Sugar Ceiling: {sugar_pct}% of daily sugar budget consumed.")

    if sodium_pct >= 100:
        alerts.append(f"Sodium Warning: {tot_sodium:.0f}mg exceeds the WHO 2000mg maximum daily threshold.")

    if tot_additives > WHO_DAILY_ALLOWANCES["chemical_additives_count"]:
        alerts.append(f"High Chemical Additive Burden: {tot_additives} synthetic additives consumed today.")

    return DailyBudgetReport(
        date=date_str,
        entries_count=len(day_entries),
        total_sugar_g=round(tot_sugar, 1),
        total_sodium_mg=round(tot_sodium, 1),
        total_saturated_fat_g=round(tot_sat_fat, 1),
        total_calories_kcal=round(tot_calories, 1),
        total_additives_consumed=tot_additives,
        sugar_budget_pct=sugar_pct,
        sodium_budget_pct=sodium_pct,
        saturated_fat_budget_pct=sat_fat_pct,
        calories_budget_pct=cal_pct,
        alerts=alerts,
        recent_entries=day_entries[-5:]
    )

def get_all_food_history() -> List[Dict[str, Any]]:
    """Returns all historically logged food items in reverse chronological order."""
    logs = _load_all_logs()
    return list(reversed(logs))

