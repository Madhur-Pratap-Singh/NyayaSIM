"""
NyayaSim Intake Agent
Parses unstructured legal complaint text into a typed Pydantic CaseFile.
"""

from typing import Optional
from agents.base_agent import BaseAgent
from schemas.case import CaseFile
from tools.gateway import ModelGateway


class IntakeAgent(BaseAgent):
    def __init__(self, gateway: Optional[ModelGateway] = None):
        super().__init__(
            name="Intake Agent",
            role="Registry intake officer extracting structured dispute metadata without legal conclusions",
            gateway=gateway
        )

    def process(self, raw_case_text: str, case_id: str = "CASE-2026-001", case_type: str = "consumer_dispute") -> CaseFile:
        prompt = (
            f"Extract the following raw dispute text into a structured CaseFile schema.\n\n"
            f"Case Identifier: {case_id}\n"
            f"Case Category: {case_type}\n\n"
            f"=== BEGIN SUBMITTED CASE TEXT ===\n"
            f"{raw_case_text}\n"
            f"=== END SUBMITTED CASE TEXT ===\n\n"
            f"RULES:\n"
            f"1. Extract Claimant(s) and Respondent(s) into the parties list.\n"
            f"2. Extract specific consumer grievances into claims.\n"
            f"3. Extract specific financial refunds or damages into relief_sought.\n"
            f"4. Extract all mentioned evidence, invoices, warranty cards, or notices into documents_listed.\n"
            f"5. Extract chronological dates into key_dates.\n"
            f"6. Provide a neutral, objective factual narrative summary without legal opinions.\n"
            f"7. Ensure is_fictional is True."
        )

        case_file = self.execute(prompt=prompt, response_model=CaseFile, temperature=0.0)
        case_file.raw_text = raw_case_text
        return case_file
