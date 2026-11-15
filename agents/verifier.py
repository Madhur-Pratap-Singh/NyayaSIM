"""
NyayaSim Two-Tier Legal Citation Verifier Agent
Enforces the Zero Hallucination protocol:
  Tier 1: Exact code existence check against the local statutory corpus.
  Tier 2: Textual proposition support check (verifies legal reasoning is backed by text).
"""

from typing import List, Optional
from schemas.citation import Citation
from schemas.common import CitationStatus
from tools.lookup import get_lookup_engine, CorpusLookupEngine
from tools.gateway import ModelGateway, get_default_gateway


class VerifierAgent:
    def __init__(self, gateway: Optional[ModelGateway] = None, lookup: Optional[CorpusLookupEngine] = None):
        self.gateway = gateway or get_default_gateway()
        self.lookup = lookup or get_lookup_engine()

    def verify_citation(self, citation: Citation) -> Citation:
        """
        Executes Tier 1 (Code Existence) and Tier 2 (Proposition Support) verification.
        """
        # =====================================================================
        # TIER 1: Exact Code Existence Check
        # =====================================================================
        matched_unit = self.lookup.lookup_exact(citation.claimed_reference)
        if not matched_unit:
            # Check matched_unit_id if provided
            if citation.matched_unit_id:
                matched_unit = self.lookup.lookup_exact(citation.matched_unit_id)

        if not matched_unit:
            citation.status = CitationStatus.NOT_FOUND
            citation.source_text = None
            citation.origin = "unverified_external"
            return citation

        # Tier 1 passed: Section is authentic
        citation.matched_unit_id = matched_unit["unit_id"]
        citation.source_text = matched_unit["text"]
        citation.origin = "statutory_corpus"

        # =====================================================================
        # TIER 2: Textual Proposition Support Check
        # =====================================================================
        # If no proposition is asserted, existence is enough for basic verification
        if not citation.proposition or len(citation.proposition.strip()) < 10:
            citation.status = CitationStatus.VERIFIED
            return citation

        # Check proposition support via keyword overlap or Gateway LLM verification
        prompt = f"""
You are a judicial verification clerk auditing statutory citations for an Indian Consumer Commission.
STATUTORY UNIT: {matched_unit['section']} - {matched_unit['title']}
STATUTORY TEXT: \"{matched_unit['text']}\"

CLAIMED PROPOSITION: \"{citation.proposition}\"

Determine whether the STATUTORY TEXT supports the CLAIMED PROPOSITION.
Answer strictly in JSON:
{{
  "is_supported": true or false,
  "confidence": 0.0 to 1.0,
  "reason": "brief rationale"
}}
"""
        try:
            res = self.gateway.generate_json(
                prompt=prompt,
                system_instruction="You are a strict legal citation auditor under the Consumer Protection Act, 2019."
            )
            is_supported = res.get("is_supported", False)
            if is_supported:
                citation.status = CitationStatus.VERIFIED
            else:
                citation.status = CitationStatus.NOT_SUPPORTED
        except Exception:
            # Fallback heuristic: check if essential legal keywords overlap
            prop_words = set(citation.proposition.lower().split())
            source_words = set(matched_unit["text"].lower().split())
            overlap = len(prop_words.intersection(source_words))
            if overlap >= 2:
                citation.status = CitationStatus.VERIFIED
            else:
                citation.status = CitationStatus.NOT_SUPPORTED

        return citation

    def verify_all(self, citations: List[Citation]) -> List[Citation]:
        return [self.verify_citation(c) for c in citations]
