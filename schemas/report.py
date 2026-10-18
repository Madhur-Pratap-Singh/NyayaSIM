"""
NyayaSim Data Contracts - Escalation Result and Final Report Schemas
Output from Escalation Engine and Reviewer Agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.common import EscalationDecision
from schemas.checklist import ChecklistResult
from schemas.issue import Issue
from schemas.citation import Citation
from schemas.debate import Argument
from schemas.judge import JudgeOpinion


class EscalationResult(BaseModel):
    decision: EscalationDecision = Field(..., description="Final decision: proposed_resolution or human_hearing_needed")
    reasons: List[str] = Field(default_factory=list, description="Explicit criteria triggering the decision")
    facts_undisputed: bool = Field(..., description="Whether all key factual claims are undisputed")
    documents_complete: bool = Field(..., description="Whether all critical checklist documents are present")
    law_verified: bool = Field(..., description="Whether all essential legal citations were verified")
    judges_unanimous: bool = Field(..., description="Whether all judge agents agreed on the same verdict")


class FinalReport(BaseModel):
    report_id: str = Field(..., description="Unique report ID, e.g. REP-RUN-001")
    case_id: str = Field(..., description="Associated case file ID")
    run_id: str = Field(..., description="Pipeline execution run ID")
    generated_at: str = Field(..., description="ISO 8601 timestamp")
    is_early_stop: bool = Field(default=False, description="True if halted early due to missing critical checklist item")
    executive_summary: str = Field(..., description="High-level synthesis of file readiness and findings")
    checklist_results: List[ChecklistResult] = Field(default_factory=list, description="Procedural checklist audit")
    issues: List[Issue] = Field(default_factory=list, description="All identified defects, missing docs, and discrepancies")
    verified_citations: List[Citation] = Field(default_factory=list, description="Citations that passed existence and support checks")
    rejected_citations: List[Citation] = Field(default_factory=list, description="Citations rejected (not found or unsupported)")
    arguments: List[Argument] = Field(default_factory=list, description="Adversarial debate records (if not early stopped)")
    judge_opinions: List[JudgeOpinion] = Field(default_factory=list, description="Stage 1 & 2 judge opinions (if not early stopped)")
    escalation: EscalationResult = Field(..., description="Deterministic code escalation verdict")
    unverified_or_unchecked_items: List[str] = Field(default_factory=list, description="Disclosures of what could NOT be checked")
    prototype_disclaimer: str = Field(
        default="NOTICE: NyayaSim is an experimental prototype operating exclusively on fictional data. "
                "This readiness report is for procedural assistance only and does NOT constitute legal advice or a binding judicial determination.",
        description="Mandatory prototype safety notice"
    )
