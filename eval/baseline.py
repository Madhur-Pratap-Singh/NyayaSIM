"""
NyayaSim Single-Prompt Baseline Evaluator
Represents the standard naive LLM approach: passes the raw case text
directly to an LLM in a single ungrounded prompt without procedural checklists,
closed corpus lookup, two-tier verification, or adversarial deliberation.
"""

from typing import Dict, Any
from tools.gateway import ModelGateway, get_default_gateway


class BaselineSystem:
    def __init__(self, gateway: ModelGateway = None):
        self.gateway = gateway or get_default_gateway()

    def evaluate(self, raw_case_text: str) -> Dict[str, Any]:
        """
        Single-prompt pass to Gemini without multi-agent checks or verified corpus.
        """
        prompt = f"""
You are a legal assistant reviewing an Indian Consumer Complaint.
CASE TEXT:
{raw_case_text}

Provide your judgment. Answer in JSON:
{{
  "should_admit": true or false,
  "missing_documents": ["list of missing items if any"],
  "citations_cited": ["statutory sections cited"],
  "recommended_outcome": "PROPOSED_RESOLUTION" or "HUMAN_HEARING_NEEDED",
  "reasoning": "brief summary"
}}
"""
        try:
            return self.gateway.generate_json(
                prompt=prompt,
                system_instruction="You are a consumer dispute legal assistant in India."
            )
        except Exception as e:
            return {
                "should_admit": True,
                "missing_documents": [],
                "citations_cited": [],
                "recommended_outcome": "PROPOSED_RESOLUTION",
                "reasoning": f"Fallback baseline execution: {e}"
            }
