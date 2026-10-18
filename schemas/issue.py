"""
NyayaSim Data Contracts - Issue Schema
Represents any defect, missing item, or legal conflict flagged during the run.
"""

from typing import Optional
from pydantic import BaseModel, Field
from schemas.common import Severity


class Issue(BaseModel):
    issue_id: str = Field(..., description="Unique issue identifier, e.g. ISS-001")
    category: str = Field(..., description="Category: 'missing_document', 'unverified_citation', 'unsupported_claim', 'jurisdiction', 'procedural'")
    title: str = Field(..., description="Short summary of the issue")
    description: str = Field(..., description="Full explanation of the problem or defect found")
    severity: Severity = Field(default=Severity.MEDIUM, description="Impact level: low, medium, high, critical")
    raised_by: str = Field(..., description="Agent or component that identified the issue")
    evidence: Optional[str] = Field(None, description="Supporting excerpt or trace reference")
