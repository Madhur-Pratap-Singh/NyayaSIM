"""
NyayaSim Data Contracts - Judge Opinion Schema
Used by the 3-Judge panel for independent and comparison rounds.
"""

from typing import Optional
from pydantic import BaseModel, Field


class JudgeOpinion(BaseModel):
    opinion_id: str = Field(..., description="Unique opinion ID, e.g. JOP-J1-S1")
    judge_id: str = Field(..., description="Judge identifier, e.g. 'judge_textualist', 'judge_welfare', 'judge_proceduralist'")
    judge_name: str = Field(..., description="Human readable title, e.g. 'Judge A (Strict Statutory)'")
    stage: str = Field(..., description="'independent' (sealed stage 1) or 'comparison' (stage 2)")
    reasoning: str = Field(..., description="Detailed legal reasoning evaluating claims, evidence, and arguments")
    verdict: str = Field(..., description="'in_favor_of_claimant', 'in_favor_of_respondent', 'remand_or_dismiss', 'human_hearing'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    revised_from_stage1: bool = Field(default=False, description="True if verdict/reasoning altered after viewing peers")
    revision_explanation: Optional[str] = Field(None, description="Detailed justification for changing opinion")
