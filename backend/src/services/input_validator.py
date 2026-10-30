"""
Defensive Input Sanitizer & The "Ladder of Refusals"
Enforces strict security boundaries before bytes touch memory, OCR, or LLM services.
Inspired by production security practices in Smart-Ingredient-Analyzer.
"""

import io
from typing import Tuple, Dict, Any, Optional
from PIL import Image

# Magic bytes signature table
MAGIC_BYTES: Dict[str, bytes] = {
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "webp": b"RIFF",
    "gif": b"GIF8"
}

# Refusal codes
class RefusalCode:
    IMAGE_TOO_SMALL = "IMAGE_TOO_SMALL"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    UNSUPPORTED_IMAGE_TYPE = "UNSUPPORTED_IMAGE_TYPE"
    IMAGE_TOO_MANY_PIXELS = "IMAGE_TOO_MANY_PIXELS"
    CORRUPTED_IMAGE = "CORRUPTED_IMAGE"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    INSUFFICIENT_INGREDIENTS = "INSUFFICIENT_INGREDIENTS"


class RefusalError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def sniff_image_type(data: bytes) -> Optional[str]:
    """Inspects the leading bytes to verify actual image format without trusting MIME header."""
    if len(data) < 12:
        return None
    
    if data.startswith(MAGIC_BYTES["jpeg"]):
        return "jpeg"
    if data.startswith(MAGIC_BYTES["png"]):
        return "png"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "gif"
    return None


def validate_image_bytes(
    data: bytes,
    min_size: int = 1024,             # 1 KB
    max_size: int = 12 * 1024 * 1024,  # 12 MB
    max_pixels: int = 80_000_000      # 80 MP decompression bomb limit
) -> Tuple[str, Tuple[int, int]]:
    """
    Validates incoming image bytes against the Ladder of Refusals.
    Returns (format, (width, height)).
    """
    byte_len = len(data)
    if byte_len < min_size:
        raise RefusalError(
            RefusalCode.IMAGE_TOO_SMALL,
            f"Image payload too small ({byte_len} bytes). Minimum size is {min_size} bytes.",
            status_code=413
        )
    if byte_len > max_size:
        raise RefusalError(
            RefusalCode.IMAGE_TOO_LARGE,
            f"Image payload exceeds maximum limit of {max_size // (1024*1024)}MB.",
            status_code=413
        )

    # Magic byte verification
    fmt = sniff_image_type(data)
    if not fmt:
        raise RefusalError(
            RefusalCode.UNSUPPORTED_IMAGE_TYPE,
            "Unsupported file format. Only JPEG, PNG, and WebP images are allowed.",
            status_code=415
        )

    # Decompression bomb and dimension validation
    try:
        with Image.open(io.BytesIO(data)) as img:
            w, h = img.size
            total_pixels = w * h
            if total_pixels > max_pixels:
                raise RefusalError(
                    RefusalCode.IMAGE_TOO_MANY_PIXELS,
                    f"Image resolution too large ({w}x{h} = {total_pixels:,} pixels). Limit is {max_pixels:,} pixels.",
                    status_code=413
                )
            return fmt, (w, h)
    except RefusalError:
        raise
    except Exception as e:
        raise RefusalError(
            RefusalCode.CORRUPTED_IMAGE,
            f"Failed to decode image data: {str(e)}",
            status_code=400
        )


def sanitize_text(text: str, max_chars: int = 20_000) -> str:
    """
    Protects against ReDoS and buffer bloating by capping text at 20k characters
    and stripping control/null characters.
    """
    if not text:
        return ""
    if len(text) > max_chars:
        text = text[:max_chars]
    # Remove null bytes and dangerous control chars
    return "".join(ch for ch in text if ch == "\n" or ch == "\t" or (ord(ch) >= 32 and ord(ch) != 127)).strip()
