"""
NyayaSim Model Gateway
Unified, pluggable interface for all model calls.
Handles structured outputs, local disk caching, retries, and rate-limiting.
"""

import os
import json
import hashlib
import time
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache", "llm_responses")
os.makedirs(CACHE_DIR, exist_ok=True)


class ModelGateway:
    """
    Abstract/base wrapper for LLM calls with disk caching and retry logic.
    """
    def __init__(self, provider: str = "mock", cache_enabled: bool = True):
        self.provider = provider
        self.cache_enabled = cache_enabled
        self.total_tokens_used = 0
        self.call_history = []

    def _get_cache_key(self, prompt: str, system_instruction: str, model_name: str, schema_name: str) -> str:
        raw = f"{self.provider}:{model_name}:{schema_name}:{system_instruction}:{prompt}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _read_cache(self, cache_key: str) -> Optional[str]:
        if not self.cache_enabled:
            return None
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("response")
        return None

    def _write_cache(self, cache_key: str, response_text: str):
        if not self.cache_enabled:
            return
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"response": response_text, "timestamp": time.time()}, f, indent=2)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: str = "You are a neutral judicial assistant. Output valid JSON only.",
        model_name: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 2
    ) -> T:
        """
        Generates structured data adhering to response_model.
        """
        model_name = model_name or os.getenv("NYAYASIM_MODEL", "gemini-2.0-flash")
        cache_key = self._get_cache_key(prompt, system_instruction, model_name, response_model.__name__)

        cached_text = self._read_cache(cache_key)
        if cached_text:
            try:
                return response_model.model_validate_json(cached_text)
            except Exception:
                pass  # Cache corrupt or schema changed, re-fetch

        # Call provider implementation
        raw_output = None
        for attempt in range(max_retries + 1):
            try:
                raw_output = self._call_provider(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    response_model=response_model,
                    model_name=model_name,
                    temperature=temperature
                )
                parsed = response_model.model_validate_json(raw_output)
                self._write_cache(cache_key, raw_output)
                return parsed
            except Exception as e:
                if attempt == max_retries:
                    raise RuntimeError(f"ModelGateway failed to produce valid {response_model.__name__} after {max_retries+1} attempts: {e}. Raw was: {raw_output}")
                # Retry prompt with error feedback
                prompt = f"{prompt}\n\nPREVIOUS OUTPUT FAILED VALIDATION:\nError: {e}\nEnsure response strictly matches the required JSON schema."
                time.sleep(1.0)

    def _call_provider(
        self,
        prompt: str,
        system_instruction: str,
        response_model: Type[T],
        model_name: str,
        temperature: float
    ) -> str:
        raise NotImplementedError("Subclasses must implement _call_provider")


class MockModelGateway(ModelGateway):
    """
    Deterministic mock gateway for rapid testing without API keys.
    """
    def __init__(self, mock_handlers: Optional[Dict[str, Any]] = None):
        super().__init__(provider="mock", cache_enabled=False)
        self.mock_handlers = mock_handlers or {}

    def register_mock(self, schema_name: str, handler):
        self.mock_handlers[schema_name] = handler

    def _call_provider(
        self,
        prompt: str,
        system_instruction: str,
        response_model: Type[T],
        model_name: str,
        temperature: float
    ) -> str:
        schema_name = response_model.__name__
        if schema_name in self.mock_handlers:
            data = self.mock_handlers[schema_name](prompt)
            if isinstance(data, BaseModel):
                return data.model_dump_json()
            elif isinstance(data, (dict, list)):
                return json.dumps(data)
            return str(data)

        # Smart mock fallbacks for common NyayaSim schemas
        if schema_name == "CaseFile":
            from schemas.case import CaseFile
            from schemas.common import Party, DocumentItem
            # Extract case_id from prompt if present
            import re
            m = re.search(r"Case Identifier:\s*([A-Za-z0-9\-_]+)", prompt)
            cid = m.group(1) if m else "CASE-001"
            
            # Detect missing invoice from prompt
            lower_prompt = prompt.lower()
            is_missing = "misplaced" in lower_prompt or "missing" in lower_prompt or "no invoice" in lower_prompt
            has_invoice = ("invoice" in lower_prompt or "receipt" in lower_prompt) and not is_missing
            docs = [
                DocumentItem(doc_id="DOC-01", title="Tax Invoice", doc_type="invoice", is_present=True)
            ] if has_invoice else []

            mock_case = CaseFile(
                case_id=cid,
                case_type="consumer_dispute",
                parties=[
                    Party(name="Complainant (Simulated)", role="claimant"),
                    Party(name="Opposite Party (Simulated)", role="respondent")
                ],
                claims=["Defective product delivered and remedy refused."],
                relief_sought=["Full refund of purchase price plus litigation costs."],
                documents_listed=docs,
                narrative_summary="Consumer dispute regarding alleged product defects."
            )
            return mock_case.model_dump_json()

        elif schema_name == "CheckerOutputSchema":
            from agents.procedural_checker import CheckerOutputSchema
            from schemas.checklist import ChecklistResult
            from schemas.common import ItemStatus
            # Check if invoice is present in listed docs
            has_invoice = "Tax Invoice" in prompt and "DOC-01" in prompt
            invoice_status = ItemStatus.PRESENT if has_invoice else ItemStatus.MISSING
            reason = "Tax Invoice attached and verified" if has_invoice else "No invoice or proof of purchase attached to complaint."
            mock_checker = CheckerOutputSchema(results=[
                ChecklistResult(
                    item_code="CHK-DOC-INVOICE",
                    title="Proof of Purchase / Tax Invoice",
                    is_critical=True,
                    status=invoice_status,
                    reason=reason
                ),
                ChecklistResult(
                    item_code="CHK-DOC-NOTICE",
                    title="Pre-Litigation Notice",
                    is_critical=True,
                    status=ItemStatus.PRESENT,
                    reason="Notice sent to opposite party."
                ),
                ChecklistResult(
                    item_code="CHK-LIM-PERIOD",
                    title="Limitation Compliance",
                    is_critical=True,
                    status=ItemStatus.PRESENT,
                    reason="Filed within 2-year statutory limit."
                )
            ])
            return mock_checker.model_dump_json()

        elif schema_name == "ReviewerSynthesisSchema":
            from agents.reviewer import ReviewerSynthesisSchema
            mock_rev = ReviewerSynthesisSchema(
                executive_summary="Audit completed. Critical procedural requirements evaluated.",
                unverified_or_unchecked_items=[
                    "Physical verification of the hardware defect",
                    "Authenticity of physical merchant signatures"
                ]
            )
            return mock_rev.model_dump_json()

        elif schema_name == "LawyerArgumentSchema":
            from agents.lawyer import LawyerArgumentSchema
            side = "Claimant" if "CLAIMANT" in prompt else "Respondent"
            mock_arg = LawyerArgumentSchema(
                headline=f"Legal submission for {side}",
                reasoning=f"Substantive argument submitted on behalf of {side} regarding the dispute.",
                answers_argument_id="ARG-OPP-01" if "OPPOSING" in prompt else None,
                cited_references=["Section 2(10), Consumer Protection Act, 2019"],
                concession_flag=False,
                concession_evidence=None
            )
            return mock_arg.model_dump_json()

        elif schema_name == "JudgeDraftSchema":
            from agents.judge import JudgeDraftSchema
            mock_judge = JudgeDraftSchema(
                reasoning="Examined statutory definitions and documentary proof on record under CPA 2019.",
                verdict="in_favor_of_claimant",
                confidence=0.92,
                revised_from_stage1=False,
                revision_explanation=None
            )
            return mock_judge.model_dump_json()

        # Fallback default empty model
        default_inst = response_model.model_construct()
        return default_inst.model_dump_json()


class GeminiModelGateway(ModelGateway):
    """
    Official Google Gemini API gateway using the free tier.
    Uses Google AI Studio REST API endpoint directly.
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(provider="gemini", cache_enabled=True)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def _call_provider(
        self,
        prompt: str,
        system_instruction: str,
        response_model: Type[T],
        model_name: str,
        temperature: float
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment or constructor.")

        # Strip any leading 'models/' if present
        cleaned_model = model_name.replace("models/", "")
        candidate_models = [cleaned_model, "gemini-3.5-flash-lite", "gemini-3.7-flash", "gemini-3.8-flash", "gemini-flash-lite-latest"]
        # Deduplicate while preserving order
        unique_models = []
        for m in candidate_models:
            if m not in unique_models:
                unique_models.append(m)

        for active_model in unique_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={self.api_key}"
            schema_json = response_model.model_json_schema()
            schema_prompt = (
                f"{system_instruction}\n\n"
                f"CRITICAL: You must output a JSON object adhering strictly to this JSON Schema:\n"
                f"{json.dumps(schema_json, indent=2)}\n"
                f"Do not include any commentary or explanations outside the JSON."
            )

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "systemInstruction": {
                    "parts": [{"text": schema_prompt}]
                },
                "generationConfig": {
                    "temperature": temperature,
                    "responseMimeType": "application/json"
                }
            }

            # Rate-limiting backoff
            max_attempts = 5
            backoff = 4.0
            quota_exhausted_for_this_model = False

            for attempt in range(max_attempts):
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
                if resp.status_code == 200:
                    result = resp.json()
                    candidates = result.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            raw_text = parts[0]["text"].strip()
                            if raw_text.startswith("```json"):
                                raw_text = raw_text[7:]
                            elif raw_text.startswith("```"):
                                raw_text = raw_text[3:]
                            if raw_text.endswith("```"):
                                raw_text = raw_text[:-3]
                            time.sleep(2.0)
                            return raw_text.strip()
                    raise ValueError(f"Empty candidate text returned by Gemini: {result}")
                elif resp.status_code in [429, 503]:
                    err_text = resp.text.lower()
                    if "exceeded your current quota" in err_text or "resource_exhausted" in err_text:
                        print(f"  [Model {active_model} daily quota exhausted. Auto-failing over to next available model...]")
                        quota_exhausted_for_this_model = True
                        break  # Break attempt loop to try next model in unique_models!
                    else:
                        print(f"  [Rate limit (Status {resp.status_code}) - waiting {backoff:.1f}s before retry {attempt+1}/{max_attempts}...]")
                        time.sleep(backoff)
                        backoff = min(backoff * 1.5, 20.0)
                else:
                    raise RuntimeError(f"Gemini API error on {active_model} (Status {resp.status_code}): {resp.text}")

            if not quota_exhausted_for_this_model:
                raise RuntimeError(f"Gemini API exceeded retry attempts for rate limits on {active_model}.")

        raise RuntimeError("All candidate Gemini models have exhausted their free-tier quotas.")


def get_default_gateway() -> ModelGateway:
    """
    Factory function: returns GeminiGateway if key is present, else MockModelGateway.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and not api_key.startswith("your_"):
        return GeminiModelGateway(api_key=api_key)
    return MockModelGateway()
