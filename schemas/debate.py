"""
NyayaSim Data Contracts - Adversarial Debate Schema
Used by Lawyer agents during structured adversarial rounds.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.citation import Citation


class Argument(BaseModel):
    argument_id: str = Field(..., description="Unique argument ID, e.g. ARG-C-R1-01")
    side: str = Field(..., description="'claimant' or 'respondent'")
    round_num: int = Field(..., description="Debate round number (1 or 2)")
    headline: str = Field(..., description="Concise statement of the argument")
    reasoning: str = Field(..., description="Detailed legal and factual argument")
    answers_argument_id: Optional[str] = Field(None, description="Opposing argument ID this point directly rebuts")
    supporting_citations: List[Citation] = Field(default_factory=list, description="Verified citations only")
    concession_flag: bool = Field(default=False, description="Whether the argument concedes an opposing claim")
    concession_evidence: Optional[str] = Field(None, description="Documentary reason for conceding")
