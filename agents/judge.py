"""
NyayaSim Multi-Judge Panel
Implements independent sealed deliberation followed by a comparison stage.
Prevents sycophancy and judge anchoring through distinct judicial philosophies.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from agents.base_agent import BaseAgent
from schemas.case import CaseFile
from schemas.checklist import ChecklistResult
from schemas.issue import Issue
from schemas.citation import Citation
from schemas.debate import Argument
from schemas.judge import JudgeOpinion
from tools.gateway import ModelGateway


JUDGE_PERSONAS = [
    {
        "judge_id": "judge_textualist",
        "name": "Judge A (Statutory Textualist)",
        "philosophy": (
            "You are a strict statutory textualist. You base all determinations strictly on the express wording "
            "of the Consumer Protection Act, 2019. If a claim does not fall precisely within statutory definitions "
            "of 'defect' (Sec 2(10)) or 'deficiency' (Sec 2(11)), or if formal prerequisites are missing, you rule strictly."
        )
    },
    {
        "judge_id": "judge_welfare",
        "name": "Judge B (Consumer Welfare & Equity)",
        "philosophy": (
            "You view consumer protection as remedial social welfare legislation designed to protect buyers from "
            "asymmetric commercial bargaining power. You interpret statutory terms broadly in favor of consumer remedy "
            "where an obvious hardship or product failure is apparent in the record."
        )
    },
    {
        "judge_id": "judge_proceduralist",
        "name": "Judge C (Evidentiary Proceduralist)",
        "philosophy": (
            "You focus strictly on burden of proof, standard of evidence, and procedural regularity. Under Section 38(2)(c), "
            "technical manufacturing defects often require expert laboratory testing. If a claim rests only on assertion without "
            "independent technical proof or conclusive merchant admission, you mandate a human hearing or dismiss."
        )
    }
]


class JudgeDraftSchema(BaseModel):
    reasoning: str = Field(..., description="Detailed legal and evidentiary reasoning")
    verdict: str = Field(
        ...,
        description="Verdict: 'in_favor_of_claimant', 'in_favor_of_respondent', 'remand_or_dismiss', or 'human_hearing'"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    revised_from_stage1: bool = Field(default=False, description="True if verdict changed after viewing peer opinions")
    revision_explanation: Optional[str] = Field(None, description="Detailed explanation if verdict or reasoning was altered")


class JudgeAgent(BaseAgent):
    def __init__(self, judge_id: str, name: str, philosophy: str, gateway: Optional[ModelGateway] = None):
        super().__init__(name=name, role=f"Presiding Judicial Member: {name}", gateway=gateway)
        self.judge_id = judge_id
        self.philosophy = philosophy

    def deliberate_stage1(
        self,
        case_file: CaseFile,
        checklist_results: List[ChecklistResult],
        issues: List[Issue],
        verified_citations: List[Citation],
        arguments: List[Argument]
    ) -> JudgeOpinion:
        """
        Stage 1: Independent sealed opinion committed without seeing other judges.
        """
        args_text = "\n".join([
            f"- [{a.side.upper()} R{a.round_num}] {a.headline}\n  Argument: {a.reasoning}"
            for a in arguments
        ]) if arguments else "No oral/written arguments recorded."

        citations_text = "\n".join([
            f"- {c.claimed_reference}: {c.proposition} ({c.status})"
            for c in verified_citations
        ]) if verified_citations else "None."

        prompt = (
            f"JUDICIAL PHILOSOPHY:\n{self.philosophy}\n\n"
            f"CASE SUMMARY:\n{case_file.narrative_summary}\n\n"
            f"VERIFIED CITATIONS:\n{citations_text}\n\n"
            f"ADVERSARIAL ARGUMENTS:\n{args_text}\n\n"
            f"TASK (STAGE 1 - INDEPENDENT OPINION):\n"
            f"Write your independent sealed opinion and reach a verdict.\n"
            f"Verdict choices: 'in_favor_of_claimant', 'in_favor_of_respondent', 'remand_or_dismiss', 'human_hearing'.\n"
            f"Be objective, apply your philosophy, and output strictly according to the schema."
        )

        response = self.execute(prompt=prompt, response_model=JudgeDraftSchema, temperature=0.1)

        return JudgeOpinion(
            opinion_id=f"JOP-{self.judge_id}-S1",
            judge_id=self.judge_id,
            judge_name=self.name,
            stage="independent",
            reasoning=response.reasoning,
            verdict=response.verdict,
            confidence=response.confidence,
            revised_from_stage1=False
        )

    def deliberate_stage2(
        self,
        stage1_opinion: JudgeOpinion,
        peer_opinions: List[JudgeOpinion]
    ) -> JudgeOpinion:
        """
        Stage 2: Comparison stage where judges review peers and may reaffirm or revise their verdict.
        """
        peers_text = "\n".join([
            f"- {p.judge_name} Verdict: {p.verdict} (Confidence: {p.confidence})\n  Reasoning Excerpt: {p.reasoning[:300]}..."
            for p in peer_opinions
        ])

        prompt = (
            f"JUDICIAL PHILOSOPHY:\n{self.philosophy}\n\n"
            f"YOUR INITIAL INDEPENDENT OPINION (STAGE 1):\n"
            f"Verdict: {stage1_opinion.verdict}\n"
            f"Reasoning: {stage1_opinion.reasoning}\n\n"
            f"PEER JUDGE OPINIONS ON THE BENCH:\n"
            f"{peers_text}\n\n"
            f"TASK (STAGE 2 - BENCH DELIBERATION & FINAL VOTE):\n"
            f"Review your colleagues' reasoning. You may either:\n"
            f"a) Reaffirm your Stage 1 verdict and reasoning, OR\n"
            f"b) Revise your verdict based on persuasive points raised by peers.\n"
            f"CRITICAL: If you change your verdict, set revised_from_stage1 to True and provide a thorough revision_explanation."
        )

        response = self.execute(prompt=prompt, response_model=JudgeDraftSchema, temperature=0.1)

        return JudgeOpinion(
            opinion_id=f"JOP-{self.judge_id}-S2",
            judge_id=self.judge_id,
            judge_name=self.name,
            stage="comparison",
            reasoning=response.reasoning,
            verdict=response.verdict,
            confidence=response.confidence,
            revised_from_stage1=response.revised_from_stage1,
            revision_explanation=response.revision_explanation
        )


def create_judge_bench(gateway: Optional[ModelGateway] = None) -> List[JudgeAgent]:
    """
    Factory function creating the standard 3-judge bench.
    """
    return [
        JudgeAgent(
            judge_id=p["judge_id"],
            name=p["name"],
            philosophy=p["philosophy"],
            gateway=gateway
        )
        for p in JUDGE_PERSONAS
    ]
