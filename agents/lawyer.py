"""
NyayaSim Adversarial Lawyer Agents
Simulates adversarial legal debate between Claimant Counsel and Respondent Counsel.
Enforces strict rules:
1. May cite verified statutory citations only.
2. Must address specific opposing points in round 2.
3. Code-based concession check prevents improper concession of claims.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from agents.base_agent import BaseAgent
from schemas.case import CaseFile
from schemas.citation import Citation
from schemas.debate import Argument
from pipeline.rules import evaluate_concession
from tools.gateway import ModelGateway


class LawyerArgumentSchema(BaseModel):
    headline: str = Field(..., description="Concise statement of the argument")
    reasoning: str = Field(..., description="Detailed legal and factual argument")
    answers_argument_id: Optional[str] = Field(None, description="Opposing argument ID this point directly answers")
    cited_references: List[str] = Field(default_factory=list, description="Claimed statutory references cited")
    concession_flag: bool = Field(default=False, description="True if conceding any opposing claim or defense")
    concession_evidence: Optional[str] = Field(None, description="Documentary justification if conceding")


class LawyerAgent(BaseAgent):
    def __init__(self, side: str, gateway: Optional[ModelGateway] = None):
        if side not in ["claimant", "respondent"]:
            raise ValueError("Lawyer side must be either 'claimant' or 'respondent'")
        self.side = side
        role = "Aggressive advocate for the consumer (Claimant)" if side == "claimant" else "Defensive counsel for the merchant/manufacturer (Respondent)"
        super().__init__(name=f"{side.capitalize()} Counsel", role=role, gateway=gateway)

    def draft_argument(
        self,
        case_file: CaseFile,
        round_num: int,
        verified_citations: List[Citation],
        opposing_arguments: Optional[List[Argument]] = None
    ) -> Argument:
        """
        Drafts an argument for round_num, responding to opposing_arguments if present.
        """
        opposing_arguments = opposing_arguments or []

        # Verified citations available to cite
        cit_text = "\n".join([
            f"- [{c.citation_id}] {c.claimed_reference}: {c.proposition} (Excerpt: {c.source_text})"
            for c in verified_citations
        ]) if verified_citations else "No verified legal provisions provided."

        # Opposing points to answer
        opp_text = "\n".join([
            f"- [{arg.argument_id}] ({arg.side.upper()} R{arg.round_num}): {arg.headline}\n  Details: {arg.reasoning}"
            for arg in opposing_arguments
        ]) if opposing_arguments else "None (Opening Round)."

        prompt = (
            f"You are representing the {self.side.upper()} in Round {round_num} of adversarial proceedings.\n\n"
            f"CASE SUMMARY:\n{case_file.narrative_summary}\n\n"
            f"CLAIMS:\n" + "\n".join([f"- {c}" for c in case_file.claims]) + "\n\n"
            f"RELIEF SOUGHT:\n" + "\n".join([f"- {r}" for r in case_file.relief_sought]) + "\n\n"
            f"VERIFIED LEGAL AUTHORITIES AVAILABLE:\n{cit_text}\n\n"
            f"OPPOSING ARGUMENTS TO ANSWER:\n{opp_text}\n\n"
            f"RULES:\n"
            f"1. Advocate vigorously for your client ({self.side}).\n"
            f"2. You may cite ONLY provisions from the verified legal authorities listed above.\n"
            f"3. In Round 2, you MUST specify answers_argument_id and directly refute the opposing counsel's point.\n"
            f"4. Do NOT concede any claim without concrete documentary evidence."
        )

        response = self.execute(prompt=prompt, response_model=LawyerArgumentSchema, temperature=0.1)

        # Code concession gatekeeping check
        is_invalid, warning = evaluate_concession(response.concession_flag, response.concession_evidence)
        concession_flag = False if is_invalid else response.concession_flag

        # Link matching verified citations
        matching_citations = [
            c for c in verified_citations
            if any(ref.lower() in c.claimed_reference.lower() for ref in response.cited_references)
        ]

        arg_id = f"ARG-{self.side[0].upper()}-R{round_num}-01"
        return Argument(
            argument_id=arg_id,
            side=self.side,
            round_num=round_num,
            headline=response.headline,
            reasoning=response.reasoning,
            answers_argument_id=response.answers_argument_id,
            supporting_citations=matching_citations,
            concession_flag=concession_flag,
            concession_evidence=response.concession_evidence
        )
