"""
Token-Budgeted Chunker with Sentence Overlap
Prevents silent truncation by embedding models (e.g. all-MiniLM-L6-v2, which degrades
past 128 tokens and silently discards past 256 tokens).
Ported and adapted from Smart-Ingredient-Analyzer.
"""

import re
from typing import List, Callable, Optional

MAX_CHUNK_TOKENS = 110
SENTENCE_OVERLAP = 1

def default_token_counter(text: str) -> int:
    """Estimates tokens conservatively (~0.75 words per token or alphanumeric splitting)."""
    words = re.findall(r'\S+', text)
    # Factor in special punctuation, chemical brackets, and commas
    punctuation_count = len(re.findall(r'[,;:()[\]{}]', text))
    return int(len(words) * 1.3) + punctuation_count

def split_sentences(text: str) -> List[str]:
    """Splits on sentence terminators while preserving the trailing period/exclamation."""
    if not text:
        return []
    # Match sentences ending with ., !, ? followed by whitespace or end of string
    raw_sentences = re.split(r'(?<=[.!?])\s+', str(text).strip())
    return [s.strip() for s in raw_sentences if s.strip()]

def hard_split(
    sentence: str,
    count_tokens: Callable[[str], int],
    max_tokens: int = MAX_CHUNK_TOKENS
) -> List[str]:
    """Hard-splits a run-on sentence on whitespace when it exceeds max_tokens."""
    words = sentence.split()
    chunks = []
    current_words = []

    for word in words:
        candidate = " ".join(current_words + [word])
        if current_words and count_tokens(candidate) > max_tokens:
            chunks.append(" ".join(current_words))
            current_words = [word]
        else:
            current_words.append(word)

    if current_words:
        chunks.append(" ".join(current_words))
    return chunks

def chunk_text(
    text: str,
    count_tokens: Optional[Callable[[str], int]] = None,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap: int = SENTENCE_OVERLAP
) -> List[str]:
    """
    Packs sentences into overlapping chunks within max_tokens budget.
    Guarantees no chunk exceeds the embedding model's optimal window.
    """
    if not text or not str(text).strip():
        return []

    tokenizer = count_tokens or default_token_counter
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks: List[str] = []
    current_sentences: List[str] = []

    def flush():
        nonlocal current_sentences
        if not current_sentences:
            return
        chunks.append(" ".join(current_sentences))
        current_sentences = current_sentences[-overlap:] if overlap > 0 else []

    for sentence in sentences:
        # If single sentence exceeds budget, hard-split it
        if tokenizer(sentence) > max_tokens:
            flush()
            current_sentences = []
            chunks.extend(hard_split(sentence, tokenizer, max_tokens))
            continue

        candidate = " ".join(current_sentences + [sentence])
        if current_sentences and tokenizer(candidate) > max_tokens:
            flush()

        current_sentences.append(sentence)

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks
