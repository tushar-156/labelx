"""
Parenthetical Matcher & Robust String Similarity
Decomposes nested chemical parentheticals (e.g. 'Tocopherol (Vitamin E)', 'INS 500(ii)'),
normalizes IUPAC names, and enforces minimum token lengths to prevent false acronym matches (e.g. SLS vs SLES).
Ported & enhanced from LabelSpy-AI.
"""

import re
import difflib
from typing import List, Set, Tuple, Optional

STOP_WORDS: Set[str] = {"and", "of", "in", "for", "with", "to", "or", "a", "an", "the", "contains", "extract"}

def clean_chemical_name(name: str) -> str:
    """Removes special punctuation, numbers, and extra spaces for linguistic comparison."""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(name))
    return ' '.join(cleaned.split()).lower()

def calculate_match_score_raw(scanned_clean: str, target_clean: str) -> float:
    """
    Computes lexical similarity score between two cleaned chemical strings.
    Guards strictly against short acronym false positives.
    """
    # 1. Direct whitespace-stripped match
    scanned_nospace = scanned_clean.replace(" ", "")
    target_nospace = target_clean.replace(" ", "")
    
    if target_nospace and (target_nospace == scanned_nospace):
        return 1.0

    if target_nospace and len(target_nospace) >= 4 and target_nospace in scanned_nospace:
        return 0.95

    s_words = scanned_clean.split()
    t_words = target_clean.split()

    if not s_words or not t_words:
        return 0.0

    word_scores = []
    for w_t in t_words:
        best_word_score = 0.0
        for w_s in s_words:
            if w_t == w_s:
                best_word_score = 1.0
                break

            # Short tokens / acronyms (<= 4 chars) require exact match to prevent false matches (SLS != SLES, BHA != BHT)
            if len(w_t) <= 4 or len(w_s) <= 4:
                continue

            # Substring check with min length 5 for chemical roots (e.g. 'paraben' in 'methylparaben')
            is_sub = (w_s in w_t and len(w_s) >= 5) or (w_t in w_s and len(w_t) >= 5)
            ratio = difflib.SequenceMatcher(None, w_t, w_s).ratio()

            if is_sub:
                word_score = max(ratio, 0.85)
            else:
                word_score = ratio

            if word_score > best_word_score:
                best_word_score = word_score

        # If a non-stop-word key term is completely missing, penalize heavily
        if w_t not in STOP_WORDS and best_word_score < 0.70:
            return 0.0

        word_scores.append(best_word_score)

    if not word_scores:
        return 0.0

    return sum(word_scores) / len(word_scores)

def calculate_parenthetical_match_score(scanned: str, target: str) -> float:
    """
    Extracts and tests contents inside parentheses:
    e.g. Scanned 'Vitamin E' matches Target 'Tocopherol (Vitamin E)' with 1.0 score.
    Also handles reversed targets.
    """
    scanned_clean = clean_chemical_name(scanned)
    max_score = calculate_match_score_raw(scanned_clean, clean_chemical_name(target))

    # Check contents inside target parentheses
    target_parens = re.findall(r'\((.*?)\)', str(target))
    for content in target_parens:
        c_clean = clean_chemical_name(content)
        if c_clean:
            score = calculate_match_score_raw(scanned_clean, c_clean)
            if score > max_score:
                max_score = score

    # Check target base without parentheses
    target_no_parens = re.sub(r'\(.*?\)', '', str(target))
    score = calculate_match_score_raw(scanned_clean, clean_chemical_name(target_no_parens))
    if score > max_score:
        max_score = score

    # Also check contents inside scanned parentheses if any
    scanned_parens = re.findall(r'\((.*?)\)', str(scanned))
    for s_content in scanned_parens:
        sc_clean = clean_chemical_name(s_content)
        if sc_clean:
            score = calculate_match_score_raw(sc_clean, clean_chemical_name(target))
            if score > max_score:
                max_score = score

    return round(max_score, 3)

def is_chemical_match(scanned: str, target: str, threshold: float = 0.80) -> bool:
    """Returns True if similarity meets or exceeds the threshold."""
    return calculate_parenthetical_match_score(scanned, target) >= threshold
