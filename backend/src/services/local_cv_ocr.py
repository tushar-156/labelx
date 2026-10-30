"""
Local Computer Vision Text Extraction & Noise Cleaning Pipeline for LabelX
Inspired by ai-nutri-lens:
  - Local EasyOCR / Tesseract / OpenCV Computer Vision extraction
  - Regex-based packaging noise cleaner (IngredientProcessor)
  - Keyword boundary detection (ingredients, состав, etc.)
  - Packaging artifact stripper (phones, addresses, GOST/FSSAI metadata)
  - Graceful fallback for low-confidence or blurry images
"""

import os
import re
import io
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

class IngredientProcessor:
    """Processor for cleaning and tokenizing raw OCR text."""

    STOP_WORDS = [
        'тел', 'адрес', 'республика', 'email', 'год', 'гост', 'ту рб', 'онын', 
        'курамы', 'изготовитель', 'batch no', 'mfg date', 'exp date', 'mrp rs',
        'customer care', 'toll free', 'lic no', 'fssai', 'net wt', 'net content',
        'packed by', 'marketed by', 'store in a cool', 'keep dry', 'protect from heat'
    ]

    START_KEYWORDS = [
        'состав:', 'курамы:', 'ингредиенты:', 'сосiаb', 'соспав', 
        'ingredients:', 'ingredients :', 'contains:', 'active ingredients:', 
        'inactive ingredients:', 'composition:', 'ingredienser:'
    ]

    def filter_ingredients(self, tokens: List[str]) -> List[str]:
        clean_ingredients = []
        for token in tokens:
            token = token.strip()
            # Remove leading bullets, numbers or symbols
            token = re.sub(r'^[•\-\*\d\.\s\:]+', '', token).strip()
            if len(token) < 2:
                continue
            # Filter if token matches any stop words
            if not any(word in token.lower() for word in self.STOP_WORDS):
                clean_ingredients.append(token)
        return clean_ingredients

    def clean_and_split(self, raw_text: str) -> List[str]:
        text = raw_text.lower()
        start_index = -1
        
        # 1. Isolate text after start keyword if found
        for key in self.START_KEYWORDS:
            if key in text:
                start_index = text.find(key) + len(key)
                break
                
        content = text[start_index:] if start_index != -1 else text

        # 2. Stop at mandatory warnings or manufacturer sections
        stop_section_words = [
            "allergen advice", "contains:", "manufactured by", "marketed by", 
            "stored in", "directions:", "caution:", "warning:", "for external use only"
        ]
        end_index = len(content)
        for sw in stop_section_words:
            pos = content.find(sw)
            if 0 < pos < end_index and start_index != -1:
                end_index = pos
        content = content[:end_index]

        # 3. Clean OCR noise (preserve alphanumeric, commas, parens, hyphens, percent)
        cleaned = re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\(\)\%\-\,\.\s]', ' ', content)
        # Split on commas or semicolons
        raw_tokens = [t.strip() for t in re.split(r'[,;•\n]', cleaned) if t.strip()]
        return self.filter_ingredients(raw_tokens)

class LocalCVEngine:
    """Local Computer Vision Text Extractor with PyTorch EasyOCR & Tesseract."""

    def __init__(self):
        self.processor = IngredientProcessor()
        self._easyocr_reader = None

    def _get_easyocr(self):
        if self._easyocr_reader is None:
            try:
                import easyocr
                # Initialize English and Russian reader
                self._easyocr_reader = easyocr.Reader(['en', 'ru'], gpu=False)
            except Exception as e:
                print(f"Notice: EasyOCR not available ({e}), using PIL/Tesseract pipeline")
                self._easyocr_reader = False
        return self._easyocr_reader

    def preprocess_image(self, image_bytes: bytes) -> Image.Image:
        image = Image.open(io.BytesIO(image_bytes))
        try:
            image = ImageOps.exif_transpose(image)
        except Exception:
            pass

        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")

        # Resize for optimal OCR processing
        max_dim = 1600
        if max(image.size) > max_dim:
            image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        # Contrast enhancement and unsharp mask for curvature
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
        image = image.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))

        # Attenuate glare & specular reflections on shiny foil packets or glossy bottles
        image = self.attenuate_glare_and_reflections(image)
        return image

    def attenuate_glare_and_reflections(self, image: Image.Image) -> Image.Image:
        """
        Specular reflection & glare attenuation inspired by FCI-IMAGE-ANALYZER (artifact_removal.py).
        Detects blown-out glare patches on shiny foil chip packets or glossy plastic bottles
        and restores local contrast via CLAHE and luminance equalization.
        """
        try:
            import cv2
            import numpy as np
            
            img_np = np.array(image)
            lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            
            glare_mask = cv2.threshold(l_channel, 235, 255, cv2.THRESH_BINARY)[1]
            glare_pixels = cv2.countNonZero(glare_mask)
            total_pixels = img_np.shape[0] * img_np.shape[1]
            
            if glare_pixels / total_pixels > 0.005:
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                l_equalized = clahe.apply(l_channel)
                lab_restored = cv2.merge([l_equalized, a_channel, b_channel])
                restored_rgb = cv2.cvtColor(lab_restored, cv2.COLOR_LAB2RGB)
                return Image.fromarray(restored_rgb)
        except Exception:
            pass
        return image

    def extract_text(self, image_bytes: bytes) -> Tuple[str, List[str], float]:
        """
        Extracts raw text and parsed ingredients locally.
        Returns: (raw_text, ingredients_list, confidence_score)
        """
        image = self.preprocess_image(image_bytes)
        raw_text = ""
        confidence = 0.85

        reader = self._get_easyocr()
        if reader and reader is not False:
            try:
                import numpy as np
                img_np = np.array(image)
                results = reader.readtext(img_np)
                # results: list of (bbox, text, prob)
                text_pieces = []
                probs = []
                for bbox, text, prob in results:
                    text_pieces.append(text)
                    probs.append(prob)
                raw_text = " ".join(text_pieces)
                if probs:
                    confidence = sum(probs) / len(probs)
            except Exception as e:
                print(f"EasyOCR run error: {e}")
                raw_text = ""

        # Fallback to pytesseract if EasyOCR was unavailable or returned empty
        if not raw_text.strip():
            try:
                import pytesseract
                raw_text = pytesseract.image_to_string(image)
                confidence = 0.70
            except Exception as e:
                print(f"Pytesseract fallback error: {e}")

        # Low-Confidence / Blurry Image Fallback
        if len(raw_text.strip()) < 15 or confidence < 0.35:
            confidence = 0.30
            # Return graceful low-confidence alert flag
            print("Notice: Low OCR confidence detected on label image. Triggering graceful fallback.")

        # Process and clean tokens
        ingredients = self.processor.clean_and_split(raw_text)

        return raw_text, ingredients, round(confidence, 2)

local_cv_engine = LocalCVEngine()
