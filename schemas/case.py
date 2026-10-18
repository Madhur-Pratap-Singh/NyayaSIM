"""
NyayaSim Data Contracts - Case File Schema
Output from Intake Agent and input to Procedural Checker.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.common import Party, DocumentItem, KeyDate


class CaseFile(BaseModel):
    case_id: str = Field(..., description="Unique case identifier, e.g. CASE-2026-001")
    case_type: str = Field(default="consumer_dispute", description="Dispute category, e.g. consumer_dispute")
    is_fictional: bool = Field(default=True, description="Safety flag confirming synthetic/fictional data")
    forum: Optional[str] = Field(default="District Consumer Disputes Redressal Commission", description="Forum of filing")
    parties: List[Party] = Field(default_factory=list, description="Parties to the case")
    claims: List[str] = Field(default_factory=list, description="Core grievances or causes of action asserted")
    relief_sought: List[str] = Field(default_factory=list, description="Prayers or monetary compensation sought")
    documents_listed: List[DocumentItem] = Field(default_factory=list, description="Documents attached or referenced")
    key_dates: List[KeyDate] = Field(default_factory=list, description="Chronological timeline of events")
    narrative_summary: str = Field(..., description="Neutral chronological summary of the facts as claimed")
    raw_text: Optional[str] = Field(None, description="Original unprocessed submission text")
