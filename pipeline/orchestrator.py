"""
NyayaSim Pipeline Orchestrator
Coordinates agent execution, manages pipeline state transitions,
enforces the early-stop gate, and applies deterministic escalation.
"""

import uuid
from typing import Optional, Tuple
from schemas.common import RunState, EscalationDecision
from schemas.case import CaseFile
from schemas.report import FinalReport, EscalationResult
from pipeline.rules import evaluate_early_stop, evaluate_escalation
from agents.intake import IntakeAgent
from agents.procedural_checker import ProceduralChecker
from agents.reviewer import ReviewerAgent
from tools.gateway import ModelGateway, get_default_gateway


class PipelineOrchestrator:
    def __init__(self, gateway: Optional[ModelGateway] = None):
        self.gateway = gateway or get_default_gateway()
        self.intake_agent = IntakeAgent(gateway=self.gateway)
        self.checker_agent = ProceduralChecker(gateway=self.gateway)
        self.reviewer_agent = ReviewerAgent(gateway=self.gateway)

    def run_case(
        self,
        raw_case_text: str,
        case_id: Optional[str] = None,
        case_type: str = "consumer_dispute",
        single_judge: bool = False,
        disable_verifier: bool = False
    ) -> Tuple[RunState, FinalReport]:
        """
        Executes the pre-hearing readiness review on raw case text.
        Supports ablation flags:
          - single_judge: runs with a single judge (Judge A) instead of a 3-member panel.
          - disable_verifier: injects unverified citations to test lawyer hallucination rate.
        """
        run_id = str(uuid.uuid4())
        case_id = case_id or f"CASE-{run_id[:6].upper()}"
        state = RunState.QUEUED

        # 1. Pre-checks (Code)
        if not raw_case_text or len(raw_case_text.strip()) < 20:
            raise ValueError("Case text is too short or empty.")

        state = RunState.RUNNING

        # 2. Intake Agent (Model + Schema)
        case_file = self.intake_agent.process(
            raw_case_text=raw_case_text,
            case_id=case_id,
            case_type=case_type
        )

        # 3. Procedural Checker (Model vs Statutory Checklist)
        checklist_results, issues = self.checker_agent.check(case_file)

        # 4. Early-Stop Gate (Code Decision)
        should_stop, critical_defects = evaluate_early_stop(checklist_results)

        if should_stop:
            state = RunState.STOPPED_EARLY
            defect_titles = ", ".join([d.title for d in critical_defects])
            escalation = EscalationResult(
                decision=EscalationDecision.HUMAN_HEARING_NEEDED,
                reasons=[f"Critical procedural defects present: {defect_titles}. File must be regularized prior to judicial listing."],
                facts_undisputed=False,
                documents_complete=False,
                law_verified=False,
                judges_unanimous=False
            )

            report = self.reviewer_agent.generate_report(
                case_file=case_file,
                run_id=run_id,
                checklist_results=checklist_results,
                issues=issues,
                escalation=escalation,
                is_early_stop=True
            )
            return state, report

        # 5. Full Simulation (Sprint 3: Adversarial Debate & Multi-Judge Deliberation)
        # Standard verified statutory provisions under CPA 2019
        from schemas.citation import Citation
        from schemas.common import CitationStatus
        default_verified_citations = [
            Citation(
                citation_id="CIT-CPA-2-10",
                claimed_reference="Section 2(10), Consumer Protection Act, 2019",
                matched_unit_id="CPA-2019-SEC-2-10",
                proposition="Defines 'defect' as any fault, imperfection or shortcoming in the quality, quantity, potency, purity or standard of goods.",
                status=CitationStatus.VERIFIED,
                source_text="defect means any fault, imperfection or shortcoming in the quality, quantity, potency, purity or standard which is required to be maintained by or under any law for the time being in force.",
                origin="statutory_corpus"
            ),
            Citation(
                citation_id="CIT-CPA-2-11",
                claimed_reference="Section 2(11), Consumer Protection Act, 2019",
                matched_unit_id="CPA-2019-SEC-2-11",
                proposition="Defines 'deficiency' as any fault, imperfection, shortcoming or inadequacy in the quality, nature and manner of performance.",
                status=CitationStatus.VERIFIED,
                source_text="deficiency means any fault, imperfection, shortcoming or inadequacy in the quality, nature and manner of performance which is required to be maintained by or under any law.",
                origin="statutory_corpus"
            )
        ]

        # Ablation mode: inject unverified citation if disable_verifier is True
        if disable_verifier:
            unverified_citation = Citation(
                citation_id="CIT-ABLATION-UNVERIFIED",
                claimed_reference="Section 999(Z), Consumer Protection Act, 2019",
                proposition="Requires unconditional 4x punitive damages for all consumer product complaints without defect proof.",
                status=CitationStatus.NOT_FOUND,
                source_text="[FABRICATED PROVISION FOR SYSTEM EVALUATION]",
                origin="ablation_study"
            )
            citations_for_debate = default_verified_citations + [unverified_citation]
        else:
            citations_for_debate = default_verified_citations

        # 6. Adversarial Lawyer Debate (2 Rounds)
        from agents.lawyer import LawyerAgent
        claimant_lawyer = LawyerAgent(side="claimant", gateway=self.gateway)
        respondent_lawyer = LawyerAgent(side="respondent", gateway=self.gateway)

        # Round 1: Opening arguments
        arg_c1 = claimant_lawyer.draft_argument(
            case_file=case_file,
            round_num=1,
            verified_citations=citations_for_debate
        )
        arg_r1 = respondent_lawyer.draft_argument(
            case_file=case_file,
            round_num=1,
            verified_citations=citations_for_debate,
            opposing_arguments=[arg_c1]
        )

        # Round 2: Rebuttal & Sur-rebuttal
        arg_c2 = claimant_lawyer.draft_argument(
            case_file=case_file,
            round_num=2,
            verified_citations=citations_for_debate,
            opposing_arguments=[arg_r1]
        )
        arg_r2 = respondent_lawyer.draft_argument(
            case_file=case_file,
            round_num=2,
            verified_citations=citations_for_debate,
            opposing_arguments=[arg_c2]
        )
        arguments = [arg_c1, arg_r1, arg_c2, arg_r2]

        # 7. Judicial Deliberation (Independent -> Comparison)
        from agents.judge import create_judge_bench
        judge_bench = create_judge_bench(gateway=self.gateway)

        if single_judge:
            # Ablation Mode: Single Judge only (Judge A Textualist)
            single_j = judge_bench[0]
            op_single = single_j.deliberate_stage1(
                case_file=case_file,
                checklist_results=checklist_results,
                issues=issues,
                verified_citations=citations_for_debate,
                arguments=arguments
            )
            final_opinions = [op_single]
        else:
            # Standard 3-Judge Bench Mode: Independent sealed opinions -> Comparison stage
            stage1_opinions = []
            for judge in judge_bench:
                op = judge.deliberate_stage1(
                    case_file=case_file,
                    checklist_results=checklist_results,
                    issues=issues,
                    verified_citations=citations_for_debate,
                    arguments=arguments
                )
                stage1_opinions.append(op)

            # Stage 2: Comparison stage & voting
            final_opinions = []
            for i, judge in enumerate(judge_bench):
                peers = [op for j, op in enumerate(stage1_opinions) if j != i]
                op2 = judge.deliberate_stage2(
                    stage1_opinion=stage1_opinions[i],
                    peer_opinions=peers
                )
                final_opinions.append(op2)

        # 8. Deterministic Escalation Engine
        facts_undisputed = "dispute" not in arg_r1.reasoning.lower() and "disputed" not in arg_r2.reasoning.lower()
        escalation = evaluate_escalation(
            facts_undisputed=facts_undisputed,
            checklist_results=checklist_results,
            issues=issues,
            citations=citations_for_debate,
            judge_opinions=final_opinions
        )

        # 9. Reviewer synthesizes Final Report
        report = self.reviewer_agent.generate_report(
            case_file=case_file,
            run_id=run_id,
            checklist_results=checklist_results,
            issues=issues,
            escalation=escalation,
            citations=default_verified_citations,
            arguments=arguments,
            judge_opinions=final_opinions,
            is_early_stop=False
        )

        state = RunState.COMPLETED
        return state, report
