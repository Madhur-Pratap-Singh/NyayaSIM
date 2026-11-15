"""
Unit Tests for Verifier Agent, Corpus Lookup (BM25), and SQLite Audit DB
Covers Person 3 deliverables in the 8-Week MVP Roadmap.
"""

import os
import sys
import pytest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.lookup import get_lookup_engine
from agents.verifier import VerifierAgent
from schemas.citation import Citation
from schemas.common import CitationStatus
from tools.db import init_db, log_run, log_step, log_event, get_run_steps


def test_corpus_lookup_exact():
    lookup = get_lookup_engine()
    unit = lookup.lookup_exact("Section 2(10)")
    assert unit is not None
    assert unit["unit_id"] == "CPA-2019-SEC-2-10"
    assert "defect" in unit["text"].lower()


def test_corpus_lookup_nonexistent():
    lookup = get_lookup_engine()
    unit = lookup.lookup_exact("Section 999(Z)")
    assert unit is None


def test_corpus_bm25_search():
    lookup = get_lookup_engine()
    results = lookup.search_bm25("thermal throttling motherboard hardware defect", top_k=3)
    assert len(results) > 0
    # Should rank Section 2(10) (defect) highly
    sections = [r["section"] for r in results]
    assert any("2(10)" in s or "2(11)" in s or "84" in s for s in sections)


def test_two_tier_verifier_hallucination_detection():
    lookup = get_lookup_engine()
    verifier = VerifierAgent(lookup=lookup)

    fake_citation = Citation(
        citation_id="CIT-FAKE-01",
        claimed_reference="Section 999(Z), Consumer Protection Act, 2019",
        proposition="Allows automatic 10x refund without proof"
    )

    verified = verifier.verify_citation(fake_citation)
    assert verified.status == CitationStatus.NOT_FOUND
    assert verified.source_text is None


def test_two_tier_verifier_valid_section():
    lookup = get_lookup_engine()
    verifier = VerifierAgent(lookup=lookup)

    valid_citation = Citation(
        citation_id="CIT-VALID-01",
        claimed_reference="Section 2(10)",
        proposition="Defines defect as any fault or imperfection in quality of goods"
    )

    verified = verifier.verify_citation(valid_citation)
    assert verified.status == CitationStatus.VERIFIED
    assert verified.matched_unit_id == "CPA-2019-SEC-2-10"


def test_sqlite_audit_logging():
    init_db()
    test_run_id = "TEST-RUN-DB-99"
    log_run(run_id=test_run_id, case_id="CASE-TEST", state="COMPLETED", is_early_stop=False)
    log_step(run_id=test_run_id, agent_name="TestAgent", prompt_text="Sample Prompt", response_data={"outcome": "pass"})
    log_event(run_id=test_run_id, event_type="TEST_EVENT", payload={"metric": 100})

    steps = get_run_steps(test_run_id)
    assert len(steps) > 0
    assert steps[0]["agent_name"] == "TestAgent"
