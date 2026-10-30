"""
Dual-Tier Caching Layer (Image SHA-256 + Ingredient Text MD5)
Caches raw OCR outputs and multi-agent chemical analyses to achieve <10ms repeat latency
and zero token consumption for previously scanned cosmetic formulations.
"""

import hashlib
import time
from typing import Optional, Dict, Any, List

class DualTierCache:
    def __init__(self, ttl_seconds: int = 172800):  # 48 hours default TTL
        self.ttl = ttl_seconds
        # Tier 1: Image SHA-256 -> { data: dict, created_at: float }
        self._image_cache: Dict[str, Dict[str, Any]] = {}
        # Tier 2: Normalized Ingredients MD5 -> { data: dict, created_at: float }
        self._text_cache: Dict[str, Dict[str, Any]] = {}
        # Metrics
        self.stats = {
            "tier1_hits": 0,
            "tier1_misses": 0,
            "tier2_hits": 0,
            "tier2_misses": 0
        }

    @staticmethod
    def hash_image(image_bytes: bytes) -> str:
        """Computes SHA-256 of raw image bytes."""
        return hashlib.sha256(image_bytes).hexdigest()

    @staticmethod
    def hash_ingredients(ingredients: List[str]) -> str:
        """Normalizes and computes MD5 of ingredient names."""
        clean = sorted([i.strip().lower() for i in ingredients if i.strip()])
        normalized_str = ",".join(clean)
        return hashlib.md5(normalized_str.encode("utf-8")).hexdigest()

    def get_image_result(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """Tier 1 lookup by image SHA-256."""
        entry = self._image_cache.get(image_hash)
        if entry:
            if time.time() - entry["created_at"] < self.ttl:
                self.stats["tier1_hits"] += 1
                result = dict(entry["data"])
                result["_cache_hit"] = "tier1_image_sha256"
                return result
            else:
                del self._image_cache[image_hash]
        self.stats["tier1_misses"] += 1
        return None

    def set_image_result(self, image_hash: str, data: Dict[str, Any]):
        """Tier 1 store by image SHA-256."""
        self._image_cache[image_hash] = {
            "data": data,
            "created_at": time.time()
        }

    def get_text_result(self, text_hash: str) -> Optional[Dict[str, Any]]:
        """Tier 2 lookup by ingredient MD5."""
        entry = self._text_cache.get(text_hash)
        if entry:
            if time.time() - entry["created_at"] < self.ttl:
                self.stats["tier2_hits"] += 1
                result = dict(entry["data"])
                result["_cache_hit"] = "tier2_text_md5"
                return result
            else:
                del self._text_cache[text_hash]
        self.stats["tier2_misses"] += 1
        return None

    def set_text_result(self, text_hash: str, data: Dict[str, Any]):
        """Tier 2 store by ingredient MD5."""
        self._text_cache[text_hash] = {
            "data": data,
            "created_at": time.time()
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "tier1_entries": len(self._image_cache),
            "tier2_entries": len(self._text_cache)
        }

# Global singleton cache instance
cache = DualTierCache()
