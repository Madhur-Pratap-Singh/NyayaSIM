"""
NyayaSim Pipeline Orchestrator
Coordinates agent execution, manages pipeline state transitions,
enforces the early-stop gate, verifies legal citations against closed corpus,
logs audit traces to SQLite, and applies deterministic escalation.
"""

import uuid
from typing import Optional, Tuple
from schemas.common import RunState, EscalationDecision, CitationStatus
from schemas.case import CaseFile
from schemas.citation import Citation
from schemas.report import FinalReport, EscalationResult
from pipeline.rules import evaluate_early_stop, evaluate_escalation
from agents.intake import IntakeAgent
from agents.procedural_checker import ProceduralChecker
from agents.reviewer import ReviewerAgent
from agents.verifier import VerifierAgent
from tools.gateway import ModelGateway, get_default_gateway
from tools.lookup import get_lookup_engine
from tools.db import log_run, log_step, log_event


class PipelineOrchestrator:
    def __init__(self, gateway: Optional[ModelGateway] = None):
        self.gateway = gateway or get_default_gateway()
        self.lookup = get_lookup_engine()
        self.intake_agent = IntakeAgent(gateway=self.gateway)
        self.checker_agent = ProceduralChecker(gateway=self.gateway)
        self.reviewer_agent = ReviewerAgent(gateway=self.gateway)
        self.verifier_agent = VerifierAgent(gateway=self.gateway, lookup=self.lookup)

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
        log_run(run_id=run_id, case_id=case_id, state=state.value)

        # 2. Intake Agent (Model + Schema)
        case_file = self.intake_agent.process(
            raw_case_text=raw_case_text,
            case_id=case_id,
            case_type=case_type
        )
        log_step(run_id, "IntakeAgent", raw_case_text[:300], case_file.model_dump())

        # 3. Procedural Checker (Model vs Statutory Checklist)
        checklist_results, issues = self.checker_agent.check(case_file)
        log_step(run_id, "ProceduralChecker", case_file.narrative_summary, [r.model_dump() for r in checklist_results])

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
            log_run(run_id=run_id, case_id=case_id, state=state.value, is_early_stop=True, escalation_decision=escalation.decision.value)
            return state, report

        # 5. Corpus Research & Two-Tier Verification
        # Retrieve candidate sections using BM25 query over complaint narrative
        query = f"{case_file.narrative_summary} {' '.join(case_file.claims)}"
        candidate_units = self.lookup.search_bm25(query, top_k=3)
        if not candidate_units:
            # Fallback to standard core sections
            candidate_units = [self.lookup.lookup_exact("Section 2(10)"), self.lookup.lookup_exact("Section 2(11)")]

        raw_citations = []
        for i, u in enumerate(candidate_units):
            if u:
                raw_citations.append(Citation(
                    citation_id=f"CIT-{u['unit_id']}",
                    claimed_reference=u["section"],
                    matched_unit_id=u["unit_id"],
                    proposition=u["title"],
                    status=CitationStatus.UNCLEAR,
                    source_text=u["text"],
                    origin="statutory_corpus"
                ))

        if disable_verifier:
            unverified_citation = Citation(
                citation_id="CIT-ABLATION-UNVERIFIED",
                claimed_reference="Section 999(Z), Consumer Protection Act, 2019",
                proposition="Requires unconditional 4x punitive damages for all consumer complaints without defect proof.",
                status=CitationStatus.NOT_FOUND,
                source_text="[FABRICATED PROVISION FOR SYSTEM EVALUATION]",
                origin="ablation_study"
            )
            verified_citations = raw_citations + [unverified_citation]
        else:
            verified_citations = self.verifier_agent.verify_all(raw_citations)

        log_step(run_id, "VerifierAgent", query[:200], [c.model_dump() for c in verified_citations])

        # 6. Adversarial Lawyer Debate (2 Rounds)
        from agents.lawyer import LawyerAgent
        claimant_lawyer = LawyerAgent(side="claimant", gateway=self.gateway)
        respondent_lawyer = LawyerAgent(side="respondent", gateway=self.gateway)

        # Round 1: Opening arguments
        arg_c1 = claimant_lawyer.draft_argument(
            case_file=case_file,
            round_num=1,
            verified_citations=verified_citations
        )
        arg_r1 = respondent_lawyer.draft_argument(
            case_file=case_file,
            round_num=1,
            verified_citations=verified_citations,
            opposing_arguments=[arg_c1]
        )

        # Round 2: Rebuttals
        arg_c2 = claimant_lawyer.draft_argument(
            case_file=case_file,
            round_num=2,
            verified_citations=verified_citations,
            opposing_arguments=[arg_r1]
        )
        arg_r2 = respondent_lawyer.draft_argument(
            case_file=case_file,
            round_num=2,
            verified_citations=verified_citations,
            opposing_arguments=[arg_c2]
        )

        debate_arguments = [arg_c1, arg_r1, arg_c2, arg_r2]
        log_step(run_id, "LawyerDebate", "2-Round Adversarial Arguments", [a.model_dump() for a in debate_arguments])

        # 7. Judicial Deliberation Panel
        from agents.judge import create_judge_bench
        judge_bench = create_judge_bench(gateway=self.gateway)

        if single_judge:
            judge_bench = [judge_bench[0]]

        # Stage 1: Independent sealed opinions
        stage1_opinions = []
        for judge in judge_bench:
            op = judge.deliberate_stage1(
                case_file=case_file,
                checklist_results=checklist_results,
                issues=issues,
                verified_citations=verified_citations,
                arguments=debate_arguments
            )
            stage1_opinions.append(op)

        # Stage 2: Peer comparison (only if multi-judge)
        if len(judge_bench) > 1:
            stage2_opinions = []
            for i, judge in enumerate(judge_bench):
                peers = [op for j, op in enumerate(stage1_opinions) if j != i]
                op2 = judge.deliberate_stage2(stage1_opinion=stage1_opinions[i], peer_opinions=peers)
                stage2_opinions.append(op2)
            final_opinions = stage2_opinions
        else:
            final_opinions = stage1_opinions

        log_step(run_id, "JudicialBench", "Deliberation Opinions", [o.model_dump() for o in final_opinions])

        # 8. Deterministic Escalation Evaluation (Code Decision)
        facts_undisputed = "dispute" not in arg_r1.reasoning.lower() and "disputed" not in arg_r2.reasoning.lower()
        escalation = evaluate_escalation(
            facts_undisputed=facts_undisputed,
            checklist_results=checklist_results,
            issues=issues,
            citations=verified_citations,
            judge_opinions=final_opinions
        )

        # 9. Reviewer Agent: Final Readiness Report
        report = self.reviewer_agent.generate_report(
            case_file=case_file,
            run_id=run_id,
            checklist_results=checklist_results,
            issues=issues,
            escalation=escalation,
            citations=verified_citations,
            arguments=debate_arguments,
            judge_opinions=final_opinions,
            is_early_stop=False
        )

        state = RunState.COMPLETED
        log_run(run_id=run_id, case_id=case_id, state=state.value, is_early_stop=False, escalation_decision=escalation.decision.value)
        return state, report
