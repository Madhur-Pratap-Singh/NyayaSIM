"""
NyayaSim Reviewer Agent
Synthesizes all structured agent outputs into an explainable, evidence-backed FinalReport.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from agents.base_agent import BaseAgent
from schemas.case import CaseFile
from schemas.checklist import ChecklistResult
from schemas.issue import Issue
from schemas.citation import Citation
from schemas.debate import Argument
from schemas.judge import JudgeOpinion
from schemas.report import EscalationResult, FinalReport
from tools.gateway import ModelGateway


class ReviewerSynthesisSchema(BaseModel):
    executive_summary: str = Field(..., description="High-level synthesis of case file readiness")
    unverified_or_unchecked_items: List[str] = Field(default_factory=list, description="Items that could not be verified")


class ReviewerAgent(BaseAgent):
    def __init__(self, gateway: Optional[ModelGateway] = None):
        super().__init__(
            name="Reviewer Agent",
            role="Neutral judicial clerk synthesizing audit results, debate points, and escalation findings",
            gateway=gateway
        )

    def generate_report(
        self,
        case_file: CaseFile,
        run_id: str,
        checklist_results: List[ChecklistResult],
        issues: List[Issue],
        escalation: EscalationResult,
        citations: Optional[List[Citation]] = None,
        arguments: Optional[List[Argument]] = None,
        judge_opinions: Optional[List[JudgeOpinion]] = None,
        is_early_stop: bool = False
    ) -> FinalReport:
        citations = citations or []
        arguments = arguments or []
        judge_opinions = judge_opinions or []

        verified_citations = [c for c in citations if c.status == "verified"]
        rejected_citations = [c for c in citations if c.status != "verified"]

        issues_summary = "\n".join([
            f"- [{i.severity.upper()}] {i.title}: {i.description}" for i in issues
        ]) if issues else "No procedural issues identified."

        checklist_summary = "\n".join([
            f"- {c.title}: {c.status} ({c.reason})" for c in checklist_results
        ])

        prompt = (
            f"Generate the executive summary and disclosure list for the final readiness report.\n\n"
            f"CASE ID: {case_file.case_id}\n"
            f"IS EARLY STOPPED: {is_early_stop}\n"
            f"ESCALATION DECISION: {escalation.decision.value}\n"
            f"ESCALATION REASONS:\n" + "\n".join([f"- {r}" for r in escalation.reasons]) + "\n\n"
            f"PROCEDURAL AUDIT:\n{checklist_summary}\n\n"
            f"ISSUES IDENTIFIED:\n{issues_summary}\n\n"
            f"RULES:\n"
            f"1. Summarize file readiness objectively without introducing new facts.\n"
            f"2. Explicitly disclose what could NOT be checked (e.g. physical authenticity of original invoices, offline expert laboratory defect reports).\n"
            f"3. If early stopped, explicitly state which critical documents must be filed before a hearing can be listed."
        )

        synthesis = self.execute(prompt=prompt, response_model=ReviewerSynthesisSchema, temperature=0.0)

        report = FinalReport(
            report_id=f"REP-{case_file.case_id}-{run_id[:8]}",
            case_id=case_file.case_id,
            run_id=run_id,
            generated_at=datetime.utcnow().isoformat() + "Z",
            is_early_stop=is_early_stop,
            executive_summary=synthesis.executive_summary,
            checklist_results=checklist_results,
            issues=issues,
            verified_citations=verified_citations,
            rejected_citations=rejected_citations,
            arguments=arguments,
            judge_opinions=judge_opinions,
            escalation=escalation,
            unverified_or_unchecked_items=synthesis.unverified_or_unchecked_items
        )

        return report
