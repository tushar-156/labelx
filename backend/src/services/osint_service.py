"""
Live OSINT Intelligence Service
Integrates Open-Meteo for ambient spoilage risk, Google News RSS for regulatory & recall advisories,
and Agmarknet commodity pricing context.
Ported & enhanced from OpenLabel-AI-Pipeline.
"""

import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast"
HIGH_TEMP_THRESHOLD = 35.0  # Celsius

class OsintService:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self.headers = {"User-Agent": "LabelX-Intelligence/1.0 (+https://github.com/tushar-156/labelx)"}

    def fetch_ambient_weather(self, latitude: float = 28.6139, longitude: float = 77.2090) -> Dict[str, Any]:
        """
        Fetches current weather and evaluates temperature-induced spoilage risks
        (e.g., lipid oxidation in refined oils, emulsion separation in sunscreens/creams).
        Default coordinates: New Delhi, India.
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m"
            }
            res = requests.get(OPEN_METEO_API, params=params, headers=self.headers, timeout=self.timeout)
            if res.ok:
                data = res.json()
                current = data.get("current", {})
                temp_c = current.get("temperature_2m", 25.0)
                humidity = current.get("relative_humidity_2m", 50.0)

                is_high_heat = temp_c >= HIGH_TEMP_THRESHOLD
                return {
                    "available": True,
                    "temperature_c": temp_c,
                    "relative_humidity_pct": humidity,
                    "high_heat_risk": is_high_heat,
                    "advisory": (
                        f"Ambient heat ({temp_c}°C) exceeds stability threshold. Lipid oxidation, preservative breakdown, and bacterial proliferation accelerate above 35°C."
                        if is_high_heat else "Ambient storage conditions within standard room temperature stability profile."
                    )
                }
        except Exception as e:
            pass

        return {
            "available": False,
            "temperature_c": 26.0,
            "relative_humidity_pct": 55.0,
            "high_heat_risk": False,
            "advisory": "Ambient weather offline; assume controlled 25°C storage."
        }

    def fetch_regulatory_news(self, query: str = "FSSAI food safety adulteration", max_items: int = 5) -> List[Dict[str, str]]:
        """
        Fetches relevant news items via Google News RSS on FSSAI actions, product recalls, or ingredient alerts.
        """
        try:
            encoded = quote_plus(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
            res = requests.get(rss_url, headers=self.headers, timeout=self.timeout)
            if res.ok:
                root = ET.fromstring(res.content)
                items = []
                for item in root.findall(".//channel/item")[:max_items]:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    pub_elem = item.find("pubDate")
                    if title_elem is not None and title_elem.text:
                        items.append({
                            "title": title_elem.text,
                            "link": link_elem.text if link_elem is not None else "",
                            "published": pub_elem.text if pub_elem is not None else ""
                        })
                return items
        except Exception as e:
            pass

        return [
            {
                "title": "FSSAI issues standard protocol for detecting adulteration in packaged oils and ghee",
                "link": "https://fssai.gov.in",
                "published": "Recent Advisory"
            }
        ]

    def get_commodity_risk_context(self, category: str, ingredients: List[str]) -> Dict[str, Any]:
        """
        Evaluates economic incentives for adulteration based on high-value agricultural commodities.
        """
        high_risk_commodities = {
            "olive oil": "Refined sunflower/pomace substitution due to global olive harvest deficits.",
            "honey": "Synthetic C4/C3 rice syrup adulteration bypassing standard oligosaccharide tests.",
            "ghee": "Vanaspati (hydrogenated fat) and starch blending to mimic cow butterfat solids.",
            "spices": "Artificial dye addition (Sudan I-IV in red chili, Metanil Yellow in turmeric).",
            "milk": "Maltodextrin, urea, and neutralizer addition to balance lactometer SNF density."
        }
        
        flagged_risks = []
        combined_ings = " ".join(ingredients).lower()
        for comm, reason in high_risk_commodities.items():
            if comm in category.lower() or comm in combined_ings:
                flagged_risks.append({"commodity": comm.title(), "economic_incentive": reason})

        return {
            "monitored_commodities": len(flagged_risks),
            "economic_risks": flagged_risks
        }

osint_service = OsintService()
