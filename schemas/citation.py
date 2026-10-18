"""
NyayaSim Data Contracts - Citation Schema
Tracks statutory provisions, existence checks, and textual support validation.
"""

from typing import Optional
from pydantic import BaseModel, Field
from schemas.common import CitationStatus


class Citation(BaseModel):
    citation_id: str = Field(..., description="Unique identifier, e.g. CIT-001")
    claimed_reference: str = Field(..., description="Exact reference cited, e.g. 'Section 2(7) of CPA 2019'")
    matched_unit_id: Optional[str] = Field(None, description="Matched corpus ID, e.g. 'CPA-2019-SEC-2-7'")
    proposition: str = Field(..., description="The legal proposition or rule the party claims this section establishes")
    status: CitationStatus = Field(default=CitationStatus.UNCLEAR, description="verified, not_found, not_supported, unclear")
    source_text: Optional[str] = Field(None, description="Exact statutory section or judgment text from corpus")
    justification: Optional[str] = Field(None, description="Explanation of why the citation does or does not support the proposition")
    origin: str = Field(default="case_file", description="'case_file', 'researcher', 'claimant_lawyer', 'respondent_lawyer'")
