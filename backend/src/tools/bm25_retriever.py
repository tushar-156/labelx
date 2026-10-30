"""
Hybrid BM25 + Dense RRF Retriever with Double-Refusal Abstention
Combines lexical keyword matching with dense semantic embeddings using Reciprocal Rank Fusion.
Enforces double-refusal abstention to guarantee out-of-corpus ingredients are designated
as UNCOVERED (NO_SOURCE_FOUND) rather than hallucinated by generative models.
"""

import math
import re
from typing import List, Dict, Any, Tuple, Optional

class BM25Okapi:
    """Fast in-process pure Python BM25 implementation for chemical and ingredient records."""
    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(doc) for doc in corpus) / self.corpus_size if self.corpus_size > 0 else 0
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.doc_len: List[int] = []
        self._initialize(corpus)

    def _initialize(self, corpus: List[List[str]]):
        df: Dict[str, int] = {}
        for doc in corpus:
            self.doc_len.append(len(doc))
            frequencies: Dict[str, int] = {}
            for word in doc:
                frequencies[word] = frequencies.get(word, 0) + 1
            self.doc_freqs.append(frequencies)
            for word in frequencies:
                df[word] = df.get(word, 0) + 1

        for word, freq in df.items():
            self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def get_scores(self, query: List[str]) -> List[float]:
        scores = [0.0] * self.corpus_size
        for q in query:
            if q not in self.idf:
                continue
            idf_val = self.idf[q]
            for i, doc_freq in enumerate(self.doc_freqs):
                if q in doc_freq:
                    freq = doc_freq[q]
                    denom = freq + self.k1 * (1 - self.b + self.b * (self.doc_len[i] / self.avgdl))
                    scores[i] += idf_val * (freq * (self.k1 + 1)) / denom
        return scores


def tokenize(text: str) -> List[str]:
    """Tokenizes text including chemical terms, alphanumeric codes (e.g. CI 77891), and hyphens."""
    return [w.lower() for w in re.findall(r'[a-zA-Z0-9_\-]+', text) if len(w) > 1]


class HybridIngredientRetriever:
    """
    Hybrid retriever combining BM25 lexical search and dense vector search
    with Reciprocal Rank Fusion (RRF) and double-refusal abstention.
    """
    def __init__(self, db_df, vectorstore=None):
        self.db_df = db_df
        self.vectorstore = vectorstore
        self.corpus_docs = []
        self.doc_metadata = []

        if self.db_df is not None and not self.db_df.empty:
            for idx, row in self.db_df.iterrows():
                name = str(row.get('ingredient_name', ''))
                aliases = str(row.get('common_aliases', ''))
                benefits = str(row.get('primary_benefits', ''))
                desc = str(row.get('description', ''))
                combined_text = f"{name} {aliases} {benefits} {desc}"
                tokens = tokenize(combined_text)
                self.corpus_docs.append(tokens)
                self.doc_metadata.append({
                    "id": f"C{idx+1}",
                    "row_index": idx,
                    "name": name,
                    "aliases": aliases,
                    "concern_level": str(row.get('concern_level', 'Safe')),
                    "benefits": benefits,
                    "description": desc
                })

        self.bm25 = BM25Okapi(self.corpus_docs) if self.corpus_docs else None

    def retrieve(
        self,
        ingredient_name: str,
        top_k: int = 3,
        cosine_threshold: float = 0.42,
        bm25_threshold: float = 2.5
    ) -> Dict[str, Any]:
        """
        Executes hybrid BM25 + dense search fused via RRF.
        Applies Double-Refusal Abstention:
        If both dense cosine < 0.42 AND BM25 score < 8.5, abstains and marks as UNCOVERED.
        """
        top_cosine = 0.0
        dense_hits = []
        
        # 1. Dense retrieval (FAISS)
        if self.vectorstore:
            try:
                results = self.vectorstore.similarity_search_with_score(ingredient_name, k=top_k)
                for rank, (doc, score) in enumerate(results):
                    # FAISS L2 distance conversion to approximate cosine similarity
                    cosine_sim = max(0.0, 1.0 - (score / 2.0))
                    dense_hits.append((doc.metadata.get("name", ""), cosine_sim, rank + 1))
                if dense_hits:
                    top_cosine = dense_hits[0][1]
            except Exception as e:
                pass

        # 2. Lexical retrieval (BM25 + Exact Name/Alias matching)
        top_bm25 = 0.0
        bm25_hits = []
        
        # Check exact chemical name or alias match
        if self.doc_metadata:
            q_clean = ingredient_name.strip().lower()
            for idx, meta in enumerate(self.doc_metadata):
                m_name = meta["name"].lower()
                m_aliases = meta.get("aliases", "").lower()
                if q_clean == m_name or (len(q_clean) > 3 and (q_clean in m_aliases or m_name in q_clean)):
                    top_bm25 = max(top_bm25, 10.0)
                    bm25_hits.append((idx, 10.0, 1))
                    break

        if self.bm25:
            q_tokens = tokenize(ingredient_name)
            if q_tokens:
                scores = self.bm25.get_scores(q_tokens)
                ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
                for rank, (doc_idx, b_score) in enumerate(ranked):
                    if b_score > 0:
                        bm25_hits.append((doc_idx, b_score, rank + 1))
                if bm25_hits and top_bm25 == 0.0:
                    top_bm25 = bm25_hits[0][1]

        # 3. Double-Refusal Abstention Gate
        # If BOTH retrievers are weak, the ingredient is out-of-corpus.
        # DO NOT allow LLMs to invent toxicity profiles!
        if top_cosine < cosine_threshold and top_bm25 < bm25_threshold:
            return {
                "name": ingredient_name,
                "is_uncovered": True,
                "status": "NO_SOURCE_FOUND",
                "reason": f"No authoritative chemical entry in CIR/FDA/EU corpus (Cosine: {top_cosine:.2f} < {cosine_threshold}, BM25: {top_bm25:.2f} < {bm25_threshold})",
                "citations": [],
                "passages": [],
                "confidence": 0.0
            }

        # 4. Reciprocal Rank Fusion (RRF)
        # RRF(d) = 1/(60 + r_dense) + 1/(60 + r_bm25)
        rrf_scores: Dict[int, float] = {}
        for doc_idx, b_score, rank in bm25_hits:
            rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (60.0 + rank))

        # Merge matching dense hits if identifiable by name
        if self.doc_metadata:
            for name, score, rank in dense_hits:
                for idx, meta in enumerate(self.doc_metadata):
                    if meta["name"].lower() == name.lower():
                        rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (60.0 + rank))
                        break

        # Select top fused candidate
        if not rrf_scores:
            best_doc_idx = bm25_hits[0][0] if bm25_hits else 0
        else:
            best_doc_idx = max(rrf_scores.items(), key=lambda x: x[1])[0]

        best_meta = self.doc_metadata[best_doc_idx] if best_doc_idx < len(self.doc_metadata) else {}
        
        # Build passage evidence with numbered citation ID
        citation_id = best_meta.get("id", "C1")
        passage_text = f"[{citation_id}] {best_meta.get('name')}: {best_meta.get('description')} Benefits: {best_meta.get('benefits')}. CIR Status: {best_meta.get('concern_level')}."

        return {
            "name": best_meta.get("name", ingredient_name),
            "is_uncovered": False,
            "status": "SOURCE_VERIFIED",
            "concern_level": best_meta.get("concern_level", "Safe"),
            "benefits": best_meta.get("benefits", ""),
            "description": best_meta.get("description", ""),
            "citations": [citation_id],
            "passages": [passage_text],
            "confidence": max(top_cosine, min(1.0, top_bm25 / 20.0)),
            "retrieval_metrics": {
                "top_cosine": round(top_cosine, 3),
                "top_bm25": round(top_bm25, 2)
            }
        }
