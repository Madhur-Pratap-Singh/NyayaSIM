"""
NyayaSim Procedural Checker Agent
Audits a structured CaseFile against statutory checklist requirements.
Identifies missing documents, procedural defects, and raises Issue records.
"""

from typing import List, Tuple, Optional
from pydantic import BaseModel, Field
from agents.base_agent import BaseAgent
from schemas.case import CaseFile
from schemas.checklist import ChecklistItem, ChecklistResult
from schemas.issue import Issue
from schemas.common import ItemStatus, Severity
from tools.gateway import ModelGateway


DEFAULT_CONSUMER_CHECKLIST: List[ChecklistItem] = [
    ChecklistItem(
        item_code="CHK-DOC-INVOICE",
        category="document",
        title="Proof of Purchase / Tax Invoice",
        description="Invoice, receipt, or payment confirmation proving purchase of goods/services by the complainant.",
        is_critical=True
    ),
    ChecklistItem(
        item_code="CHK-DOC-NOTICE",
        category="document",
        title="Pre-Litigation Notice to Opposite Party",
        description="Written complaint, email, or formal legal notice sent to merchant/manufacturer demanding rectification.",
        is_critical=True
    ),
    ChecklistItem(
        item_code="CHK-DOC-WARRANTY",
        category="document",
        title="Warranty / Terms of Sale Documentation",
        description="Warranty certificate, guarantee policy, or standard contract terms applicable at the time of purchase.",
        is_critical=False
    ),
    ChecklistItem(
        item_code="CHK-LIM-PERIOD",
        category="limitation",
        title="Limitation Compliance (Section 69 CPA 2019)",
        description="Complaint instituted within 2 years from the date on which the cause of action arose.",
        is_critical=True
    ),
    ChecklistItem(
        item_code="CHK-DOC-REPLY",
        category="document",
        title="Merchant Reply or Proof of Delivery",
        description="Opposite party's response, refusal, or postal tracking receipt showing notice was delivered.",
        is_critical=False
    )
]


class CheckerOutputSchema(BaseModel):
    results: List[ChecklistResult] = Field(..., description="Audit results for each required checklist item")


class ProceduralChecker(BaseAgent):
    def __init__(self, gateway: Optional[ModelGateway] = None, checklist: Optional[List[ChecklistItem]] = None):
        super().__init__(
            name="Procedural Checker",
            role="Court registry procedural auditor verifying document completeness and statutory filing requirements",
            gateway=gateway
        )
        self.checklist = checklist or DEFAULT_CONSUMER_CHECKLIST

    def check(self, case_file: CaseFile) -> Tuple[List[ChecklistResult], List[Issue]]:
        """
        Audits case_file against the checklist.
        Returns:
            (checklist_results: List[ChecklistResult], issues_raised: List[Issue])
        """
        checklist_text = "\n".join([
            f"- [{item.item_code}] {item.title} (Critical: {item.is_critical}): {item.description}"
            for item in self.checklist
        ])

        documents_summary = "\n".join([
            f"- {doc.doc_id}: {doc.title} ({doc.doc_type}) - Attached: {doc.is_present}"
            for doc in case_file.documents_listed
        ]) if case_file.documents_listed else "No documents explicitly listed."

        prompt = (
            f"You are conducting a strict pre-hearing registry audit of the following case file.\n\n"
            f"CASE SUMMARY:\n{case_file.narrative_summary}\n\n"
            f"CLAIMS:\n{json_list(case_file.claims)}\n\n"
            f"DOCUMENTS LISTED IN FILE:\n{documents_summary}\n\n"
            f"STATUTORY CHECKLIST REQUIREMENTS:\n{checklist_text}\n\n"
            f"TASK:\n"
            f"Evaluate EVERY checklist item. For each, determine if it is:\n"
            f"- 'present': Clear evidence in the file.\n"
            f"- 'missing': Required item is absent or not attached.\n"
            f"- 'unclear': Mentioned vaguely but without requisite proof/dates.\n"
            f"Provide a concise reason and quote the exact evidence span if present."
        )

        response = self.execute(prompt=prompt, response_model=CheckerOutputSchema, temperature=0.0)
        results = response.results

        # Raise Issue objects for defects
        issues = []
        issue_counter = 1
        for res in results:
            if res.status in [ItemStatus.MISSING, ItemStatus.UNCLEAR]:
                severity = Severity.CRITICAL if res.is_critical else Severity.MEDIUM
                category = "missing_document" if "DOC" in res.item_code else "procedural"
                issues.append(Issue(
                    issue_id=f"ISS-PROC-{issue_counter:03d}",
                    category=category,
                    title=f"Defect: {res.title}",
                    description=f"{res.title} is marked {res.status}. Reason: {res.reason}",
                    severity=severity,
                    raised_by=self.name,
                    evidence=res.evidence_span
                ))
                issue_counter += 1

        return results, issues


def json_list(items: List[str]) -> str:
    return "\n".join([f"- {item}" for item in items])
