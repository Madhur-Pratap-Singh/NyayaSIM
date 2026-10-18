"""
NyayaSim Deterministic Pipeline Rules
Pure-code judicial gatekeeping logic.
No model judgments are permitted to override these criteria.
"""

from typing import List, Tuple, Optional
from schemas.common import ItemStatus, Severity, CitationStatus, EscalationDecision
from schemas.checklist import ChecklistResult
from schemas.issue import Issue
from schemas.citation import Citation
from schemas.judge import JudgeOpinion
from schemas.report import EscalationResult


def evaluate_early_stop(checklist_results: List[ChecklistResult]) -> Tuple[bool, List[ChecklistResult]]:
    """
    Early-Stop Rule:
    If any checklist item designated as CRITICAL is marked 'missing' or 'unclear',
    the pipeline immediately halts further adversarial and judicial simulation.
    
    Returns:
        (should_stop: bool, critical_defects: List[ChecklistResult])
    """
    critical_defects = []
    for item in checklist_results:
        if item.is_critical and item.status in [ItemStatus.MISSING, ItemStatus.UNCLEAR]:
            critical_defects.append(item)

    should_stop = len(critical_defects) > 0
    return should_stop, critical_defects


def evaluate_concession(
    concession_flag: bool,
    concession_evidence: Optional[str]
) -> Tuple[bool, Optional[str]]:
    """
    Concession Check Rule:
    Flags any concession made during adversarial lawyer debate that lacks
    documentary evidence or factual substantiation.
    
    Returns:
        (is_invalid_concession: bool, warning_message: Optional[str])
    """
    if concession_flag:
        if not concession_evidence or len(concession_evidence.strip()) < 10:
            return True, "Lawyer conceded an adversarial point without documentary evidence or legal justification."
    return False, None


def evaluate_escalation(
    facts_undisputed: bool,
    checklist_results: List[ChecklistResult],
    issues: List[Issue],
    citations: List[Citation],
    judge_opinions: List[JudgeOpinion]
) -> EscalationResult:
    """
    Deterministic Escalation Engine (TRD Section 3.8):
    A proposed resolution is permitted ONLY if all 4 conditions hold:
      1. Facts are undisputed.
      2. Required checklist documents are complete (no critical or high-severity missing items).
      3. Applicable legal provisions are verified and clear (no unverified citations).
      4. All judge agents agree unanimously on the verdict.
      
    If ANY condition fails, the outcome is strictly HUMAN_HEARING_NEEDED.
    """
    reasons = []

    # 1. Documents complete check
    missing_critical = [c for c in checklist_results if c.is_critical and c.status != ItemStatus.PRESENT]
    high_doc_issues = [i for i in issues if i.category == "missing_document" and i.severity in [Severity.HIGH, Severity.CRITICAL]]
    documents_complete = (len(missing_critical) == 0) and (len(high_doc_issues) == 0)
    if not documents_complete:
        reasons.append("Mandatory statutory documentation is incomplete or missing.")

    # 2. Facts undisputed check
    if not facts_undisputed:
        reasons.append("Material facts regarding defect, payment, or notice remain disputed between parties.")

    # 3. Applicable law verified check
    unverified_citations = [c for c in citations if c.status != CitationStatus.VERIFIED]
    law_verified = (len(citations) > 0) and (len(unverified_citations) == 0)
    if not law_verified:
        if len(citations) == 0:
            reasons.append("No verified statutory provisions were cited or established.")
        else:
            reasons.append(f"{len(unverified_citations)} cited legal provision(s) failed existence or textual support verification.")

    # 4. Judicial unanimity check
    stage2_opinions = [j for j in judge_opinions if j.stage == "comparison"]
    eval_opinions = stage2_opinions if len(stage2_opinions) > 0 else judge_opinions

    if len(eval_opinions) == 0:
        judges_unanimous = False
        reasons.append("Judicial panel did not convene or reach a verdict.")
    else:
        verdicts = set(j.verdict for j in eval_opinions)
        judges_unanimous = (len(verdicts) == 1) and ("human_hearing" not in verdicts)
        if not judges_unanimous:
            reasons.append("Judicial panel was divided or recommended a full evidentiary hearing.")

    # Final Decision Gate
    if documents_complete and facts_undisputed and law_verified and judges_unanimous:
        decision = EscalationDecision.PROPOSED_RESOLUTION
        reasons = ["All statutory documents present, facts undisputed, law verified, and judicial panel unanimous."]
    else:
        decision = EscalationDecision.HUMAN_HEARING_NEEDED

    return EscalationResult(
        decision=decision,
        reasons=reasons,
        facts_undisputed=facts_undisputed,
        documents_complete=documents_complete,
        law_verified=law_verified,
        judges_unanimous=judges_unanimous
    )
