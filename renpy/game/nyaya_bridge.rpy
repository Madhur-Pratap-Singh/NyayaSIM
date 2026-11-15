# nyaya_bridge.rpy - Python Bridge to NyayaSim Backend API
# Runs inside Ren'Py Python 3 runtime

init -1 python:
    import urllib.request
    import urllib.error
    import json
    import time

    def sanitize_for_renpy(text):
        """
        Sanitizes any AI-generated text so Ren'Py NEVER treats it as code.

        Ren'Py processes dialogue through THREE internal layers:
          1. %  formatting  →  what % tag_quoting_dict   →  escape as %%
          2. [] substitution → [variable] evaluated as Python → escape as [[
          3. {} text tags   → {b}, {color=#fff} parsed  → escape as {{ }}

        ORDER MATTERS: % must be replaced FIRST.
        """
        if not text:
            return ""
        text = text.replace("%", "%%")   # 1. Must be first — prevents "12% p.a." crash
        text = text.replace("[", "[[")   # 2. Prevents [Section 2(10)] being evaluated
        text = text.replace("{", "{{")   # 3. Prevents {b} tag parsing
        text = text.replace("}", "}}")   # 4. Close brace pair
        return text

    def chunk_dialogue(text, max_chars=200):
        """
        Splits a long AI dialogue paragraph into short readable chunks.

        Strategy:
          1. Split on sentence boundaries (. ! ?)
          2. Group sentences together until adding the next would exceed max_chars
          3. If a single sentence is itself too long, hard-wrap it at word boundaries
          4. Returns a list of strings — each shown as a separate click-to-advance line

        Example:
          "The Commission notes X. Under Section 2(10), Y is established. Relief granted."
          → ["The Commission notes X.", "Under Section 2(10)], Y is established.", "Relief granted."]
        """
        import re

        if not text or len(text) <= max_chars:
            return [text] if text else []

        # Split into sentences at ". ", "! ", "? ", ".\n", "!\n", "?\n"
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        chunks = []
        current = ""

        for sentence in raw_sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # If a single sentence is itself too long, hard-wrap at word boundaries
            if len(sentence) > max_chars:
                # Flush current buffer first
                if current:
                    chunks.append(current.strip())
                    current = ""
                words = sentence.split()
                line = ""
                for word in words:
                    if len(line) + len(word) + 1 > max_chars and line:
                        chunks.append(line.strip())
                        line = word
                    else:
                        line = (line + " " + word).strip()
                if line:
                    chunks.append(line.strip())
                continue

            # Would adding this sentence exceed the limit?
            candidate = (current + " " + sentence).strip()
            if len(candidate) > max_chars and current:
                chunks.append(current.strip())
                current = sentence
            else:
                current = candidate

        if current.strip():
            chunks.append(current.strip())

        return chunks if chunks else [text]

    CANDIDATE_API_URLS = ["http://127.0.0.1:8000", "http://127.0.0.1:8001"]

    def get_active_backend_url():
        """Auto-detects whether port 8000 or 8001 is responding."""
        for base_url in CANDIDATE_API_URLS:
            try:
                url = f"{base_url}/api/health"
                req = urllib.request.Request(url, headers={"User-Agent": "RenPy-NyayaSim"})
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("status") == "ok":
                        return base_url
            except Exception:
                continue
        return None

    def check_backend_health():
        """Check if the NyayaSim FastAPI backend is running on 8000 or 8001."""
        return get_active_backend_url() is not None

    def simulate_custom_case(case_text, case_id="CUSTOM-CASE-01"):
        """
        Sends custom case pleading to NyayaSim FastAPI backend and retrieves live AI agent dialogue.
        """
        active_url = get_active_backend_url()
        if not active_url:
            return {
                "status": "error",
                "message": "Could not connect to NyayaSim backend on port 8000 or 8001. Please run 'start_renpy_sim.bat' or 'py -3.11 -m uvicorn backend.server:app'.",
                "dialogues": []
            }

        try:
            url = f"{active_url}/api/simulate/batch"
            payload = json.dumps({
                "case_text": case_text,
                "case_id": case_id,
                "single_judge": False,
                "disable_verifier": False
            }).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "RenPy-NyayaSim"}
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection error: {str(e)}",
                "dialogues": []
            }



    def fetch_sample_cases():
        """Fetch sample cases from backend, with local offline fallback."""
        try:
            url = f"{NYAYASIM_API_BASE}/api/samples"
            req = urllib.request.Request(url, headers={"User-Agent": "RenPy-NyayaSim"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            # High-fidelity offline fallback cases
            return {
                "laptop_defect": {
                    "title": "Laptop Thermal Defect (Full Merit Hearing)",
                    "case_id": "CC-2024-LAPTOP-001",
                    "description": "Premium gaming laptop shuts down within 15 mins due to motherboard thermal throttling.",
                    "complainant": "Rajesh Sharma",
                    "respondent": "Apex Electronics Retail Ltd.",
                    "section": "Section 35, Consumer Protection Act, 2019",
                    "claim_amount": "Rs. 85,000/- + 30,000/- Compensation"
                },
                "missing_invoice": {
                    "title": "Missing Invoice (Procedural Dismissal)",
                    "case_id": "CC-2024-DEFECT-002",
                    "description": "Smartphone claim missing tax invoice / proof of purchase. Triggers early stop.",
                    "complainant": "Informal Litigant",
                    "respondent": "City Electronics Market",
                    "section": "Section 35, Consumer Protection Act, 2019",
                    "claim_amount": "Rs. 24,000/-"
                }
            }
