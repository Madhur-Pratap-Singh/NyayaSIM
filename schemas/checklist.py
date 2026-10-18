"""
NyayaSim Data Contracts - Checklist Schemas
Used by Procedural Checker and Early-Stop Orchestrator.
"""

from typing import Optional
from pydantic import BaseModel, Field
from schemas.common import ItemStatus


class ChecklistItem(BaseModel):
    item_code: str = Field(..., description="Unique rule code, e.g. CHK-DOC-INVOICE")
    category: str = Field(..., description="Category: 'document', 'jurisdiction', 'limitation', 'parties'")
    title: str = Field(..., description="Short name of requirement")
    description: str = Field(..., description="Detailed description of what must be verified")
    is_critical: bool = Field(default=False, description="If True, missing status triggers early stop")


class ChecklistResult(BaseModel):
    item_code: str = Field(..., description="Matching ChecklistItem code")
    title: str = Field(..., description="Title of checklist requirement")
    is_critical: bool = Field(..., description="Whether this item is mandatory for hearing")
    status: ItemStatus = Field(..., description="Status: 'present', 'missing', or 'unclear'")
    reason: str = Field(..., description="Justification for the assigned status")
    evidence_span: Optional[str] = Field(None, description="Direct quote or document pointer from case file")
