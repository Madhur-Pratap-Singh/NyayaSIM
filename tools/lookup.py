"""
NyayaSim Corpus Lookup & BM25 Search Engine
Enforces Zero Hallucination: legal candidates are retrieved exclusively
from the local statutory corpus (data/corpus/cpa_2019.json).
"""

import os
import json
import re
import math
from typing import List, Dict, Any, Optional

CORPUS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "corpus",
    "cpa_2019.json"
)


class CorpusLookupEngine:
    def __init__(self, corpus_path: Optional[str] = None):
        self.corpus_path = corpus_path or CORPUS_PATH
        self.units: List[Dict[str, Any]] = []
        self.by_unit_id: Dict[str, Dict[str, Any]] = {}
        self.by_section_norm: Dict[str, Dict[str, Any]] = {}
        self._load_corpus()

        # BM25 Precomputations
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freq: Dict[str, int] = {}
        self.tokenized_corpus: List[List[str]] = []
        self._init_bm25()

    def _normalize_section_key(self, sec_str: str) -> str:
        """Normalizes references like 'Section 2(10)', 'sec 2(10)', '2(10)', 'sec-2-10'."""
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", sec_str).lower()
        cleaned = cleaned.replace("section", "").replace("sec", "")
        return cleaned

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_]{2,}\b", text.lower())
        return words

    def _load_corpus(self):
        if not os.path.exists(self.corpus_path):
            raise FileNotFoundError(f"Corpus file not found at {self.corpus_path}")

        with open(self.corpus_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.units = data.get("units", [])
        for u in self.units:
            uid = u.get("unit_id")
            self.by_unit_id[uid] = u
            sec = u.get("section", "")
            norm_k = self._normalize_section_key(sec)
            self.by_section_norm[norm_k] = u

    def _init_bm25(self):
        N = len(self.units)
        if N == 0:
            return

        total_words = 0
        for u in self.units:
            content = f"{u.get('title', '')} {u.get('text', '')} {' '.join(u.get('keywords', []))}"
            tokens = self._tokenize(content)
            self.tokenized_corpus.append(tokens)
            doc_l = len(tokens)
            self.doc_len.append(doc_l)
            total_words += doc_l

            unique_tokens = set(tokens)
            for t in unique_tokens:
                self.doc_freq[t] = self.doc_freq.get(t, 0) + 1

        self.avg_doc_len = total_words / N if N > 0 else 1.0

    def lookup_exact(self, reference: str) -> Optional[Dict[str, Any]]:
        """
        Tier 1 Exact Match: checks if the section exists in the closed corpus.
        Matches unit_id (e.g. 'CPA-2019-SEC-2-10') or text ('Section 2(10)', '2(10)').
        """
        ref_clean = reference.strip()
        if ref_clean in self.by_unit_id:
            return self.by_unit_id[ref_clean]

        norm = self._normalize_section_key(ref_clean)
        if norm in self.by_section_norm:
            return self.by_section_norm[norm]

        # Fuzzy regex check against section names
        for u in self.units:
            if u.get("section", "").lower() in ref_clean.lower() or ref_clean.lower() in u.get("section", "").lower():
                return u

        return None

    def search_bm25(self, query: str, top_k: int = 5, k1: float = 1.5, b: float = 0.75) -> List[Dict[str, Any]]:
        """
        Retrieves top-k statutory sections matching the query using BM25 scoring.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.units[:top_k]

        N = len(self.units)
        scores = [0.0] * N

        for q in query_tokens:
            df = self.doc_freq.get(q, 0)
            if df == 0:
                continue
            # Standard Robertson-Spärck Jones IDF
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)

            for i, doc_tokens in enumerate(self.tokenized_corpus):
                tf = doc_tokens.count(q)
                if tf == 0:
                    continue
                numerator = tf * (k1 + 1.0)
                denominator = tf + k1 * (1.0 - b + b * (self.doc_len[i] / self.avg_doc_len))
                scores[i] += idf * (numerator / denominator)

        ranked_indices = sorted(range(N), key=lambda i: scores[i], reverse=True)
        results = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] > 0.05:
                res_unit = dict(self.units[idx])
                res_unit["bm25_score"] = round(scores[idx], 4)
                results.append(res_unit)

        return results


# Global singleton instance
_lookup_engine = None

def get_lookup_engine() -> CorpusLookupEngine:
    global _lookup_engine
    if _lookup_engine is None:
        _lookup_engine = CorpusLookupEngine()
    return _lookup_engine
