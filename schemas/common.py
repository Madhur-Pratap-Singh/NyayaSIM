"""
NyayaSim Data Contracts - Common Enums and Base Types
Defines system-wide enums and primitive models shared across all agents.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RunState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    STOPPED_EARLY = "stopped_early"
    COMPLETED = "completed"
    FAILED = "failed"


class ItemStatus(str, Enum):
    PRESENT = "present"
    MISSING = "missing"
    UNCLEAR = "unclear"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CitationStatus(str, Enum):
    VERIFIED = "verified"
    NOT_FOUND = "not_found"
    NOT_SUPPORTED = "not_supported"
    UNCLEAR = "unclear"


class EscalationDecision(str, Enum):
    PROPOSED_RESOLUTION = "proposed_resolution"
    HUMAN_HEARING_NEEDED = "human_hearing_needed"


class Party(BaseModel):
    name: str = Field(..., description="Name of the party (person or entity)")
    role: str = Field(..., description="Role: 'claimant', 'respondent', or 'other'")
    representation: Optional[str] = Field(None, description="Counsel or self-represented")
    address: Optional[str] = Field(None, description="Jurisdictional address or city")


class DocumentItem(BaseModel):
    doc_id: str = Field(..., description="Identifier, e.g. DOC-01")
    title: str = Field(..., description="Name of the document (e.g. 'Purchase Invoice')")
    doc_type: str = Field(..., description="Type: 'invoice', 'warranty', 'notice', 'reply', 'affidavit', etc.")
    is_present: bool = Field(True, description="Whether the document is physically attached or textually proven")
    details: Optional[str] = Field(None, description="Dates, amounts, or brief description from document")


class KeyDate(BaseModel):
    date_str: str = Field(..., description="Date or timeframe mentioned in the file")
    event_description: str = Field(..., description="What occurred on this date")
