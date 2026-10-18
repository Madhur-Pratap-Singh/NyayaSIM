# NyayaSim (AI Court Sim)

An adversarial, multi-agent AI court readiness simulator designed for Indian civil disputes (starting with the **Consumer Protection Act, 2019**).

NyayaSim reviews a fictional case file **before human judicial review** to detect missing documents, procedural defects, verify legal citations against a strictly closed statutory corpus, simulate adversarial debate and independent multi-judge deliberation, and produce an explainable, evidence-backed **Readiness Report**.

> **NOTICE:** NyayaSim is an experimental academic prototype operating exclusively on synthetic/fictional data. It does not provide legal advice, replace real judges, or process real litigant files.

---

## 🏛 System Architecture & Pipeline

```
  Raw Case Text / PDF
          │
  Pre-checks & Sanitizer (Code)
          │
  Intake Agent (LLM + Pydantic Schema)
          │
  Procedural Checker (Checklist Audit)
          │
  [ Critical Document Missing? ]
    ├── YES ──► Early-Stop Engine ──► Reviewer Agent (Early Readiness Report)
    └── NO
          │
  Corpus Lookup & Verification (Code Existence + LLM Support)
          │
  Adversarial Lawyer Debate (Claimant vs. Respondent - 2 Rounds)
          │
  3-Member Judicial Deliberation Panel (Judge A Textualist, Judge B Welfare, Judge C Proceduralist)
          │
  Deterministic Escalation Rule (Pure-Code Gate: 4 Strict Conditions)
          │
  Reviewer Agent (Final Readiness Report with Evidence Trace)
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Installation
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/Madhur-Pratap-Singh/NyayaSIM.git
cd NyayaSIM

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. API Key Setup
Create a local `.env` file from `.env.example`:
```bash
copy .env.example .env
```
Add your free Google AI Studio API key in `.env`:
```env
GEMINI_API_KEY="your_api_key_here"
NYAYASIM_MODEL="gemini-3.5-flash"
```
*(Note: If no API key is set, NyayaSim automatically runs with a deterministic offline Mock Gateway for zero-cost testing).*

---

## 🧪 Running the Pipeline

### Run Automated Test Suite
Run the 9 automated pytest tests (validating schemas, early stop, concession rules, escalation engine, and prompt-injection safety):
```bash
pytest tests/test_person2_pipeline.py -v
```

### Run a Complete Case Simulation
Runs the full 15-step multi-agent simulation (Intake $\rightarrow$ Procedural Audit $\rightarrow$ 2-Round Lawyer Debate $\rightarrow$ 3-Judge Deliberation Bench $\rightarrow$ Escalation Engine $\rightarrow$ Report):
```bash
python pipeline/run_case.py --sample
```

### Test Early-Stop Gate (Case Missing Invoice)
Demonstrates that a case with a missing purchase receipt is halted early before judicial debate:
```bash
python pipeline/run_case.py --missing
```

### Run Ablation Studies
Run research ablation modes for academic evaluation:
```bash
# Single-Judge Mode (tests opinion anchoring vs 3-member bench):
python pipeline/run_case.py --sample --single-judge

# Unverified Citation Injection Mode (tests verifier protection):
python pipeline/run_case.py --sample --no-verifier
```

---

## 📂 Repository Layout

```
nyayasim/
├── schemas/                 # Shared Pydantic data contracts
│   ├── common.py            # Enums, Party, DocumentItem, KeyDate
│   ├── case.py              # CaseFile schema
│   ├── checklist.py         # ChecklistItem & ChecklistResult
│   ├── issue.py             # Issue schema
│   ├── citation.py          # Citation & verification schema
│   ├── debate.py            # Argument schema
│   ├── judge.py             # JudgeOpinion schema (sealed & comparison)
│   └── report.py            # EscalationResult & FinalReport
├── pipeline/
│   ├── rules.py             # Deterministic pure-code rules (Early-stop, Concession, Escalation)
│   ├── orchestrator.py      # Pipeline state machine coordinator
│   └── run_case.py          # Interactive CLI runner
├── agents/
│   ├── base_agent.py        # BaseAgent with prompt injection defense
│   ├── intake.py            # Extracts unstructured text into CaseFile
│   ├── procedural_checker.py# Checks case against statutory requirements
│   ├── lawyer.py            # 2-round adversarial debate
│   ├── judge.py             # 3-Judge panel (independent + comparison)
│   └── reviewer.py          # Synthesizes evidence-backed Readiness Report
├── tools/
│   └── gateway.py           # Model Gateway (Gemini Flash + disk cache + auto-failover)
├── tests/
│   └── test_person2_pipeline.py # Automated test suite (9 unit tests)
├── NyayaSim_4_Person_Team_Roadmap.pdf # 8-Week roadmap PDF for 4 people
├── requirements.txt         # Project dependencies
└── README.md                # Documentation
```

---

## 👥 4-Person Team Roles

| Role | Teammate | Focus Area |
| :--- | :--- | :--- |
| **Person 1** | **Legal & Domain Architect** | Consumer Protection Act corpus, checklists, 15+ synthetic test cases with ground-truth defect labels, demographic bias pairs. |
| **Person 2** | **Agent & Orchestration Engineer** | Pipeline state machine, agent prompts, deterministic rules (early stop, escalation), 2-round lawyer debate, 3-judge panel. |
| **Person 3** | **Data & Verification Systems Engineer** | Model gateway, response caching, two-tier verifier (code lookup + LLM support), SQLite relational audit logging. |
| **Person 4** | **Evaluation & Frontend Lead** | Streamlit web interface with trace drawer, single-prompt baseline benchmark, automated scoring metrics. |

---

## 📄 License & Academic Disclaimer
Built for academic research and educational demonstration. All simulated disputes are fictional.
