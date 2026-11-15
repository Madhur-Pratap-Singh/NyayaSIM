"""
NyayaSim Courtroom Simulator - FastAPI Backend Server
Streams real-time court events via Server-Sent Events (SSE) to the GBA Courtroom UI.
"""

import sys
import os
import json
import asyncio
import traceback
from typing import AsyncGenerator, Optional
from pydantic import BaseModel

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from schemas.common import RunState, EscalationDecision, ItemStatus
from schemas.report import EscalationResult
from pipeline.rules import evaluate_early_stop, evaluate_escalation
from agents.intake import IntakeAgent
from agents.procedural_checker import ProceduralChecker
from agents.reviewer import ReviewerAgent
from agents.lawyer import LawyerAgent
from agents.judge import create_judge_bench
from agents.verifier import VerifierAgent
from tools.gateway import get_default_gateway
from tools.lookup import get_lookup_engine
from tools.db import log_run, log_step, log_event

app = FastAPI(title="NyayaSim GBA Courtroom API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationRequest(BaseModel):
    case_text: str
    case_id: Optional[str] = None
    single_judge: bool = False
    disable_verifier: bool = False


SAMPLE_CASES = {
    "laptop_defect": {
        "title": "Laptop Thermal Defect (Full Merit Hearing)",
        "case_id": "CC-2024-LAPTOP-001",
        "description": "Purchased premium gaming laptop that shuts down within 15 mins due to mother-board thermal throttling.",
        "text": """
CONSUMER COMPLAINT UNDER SECTION 35 OF CONSUMER PROTECTION ACT, 2019
BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION, NEW DELHI

Complainant: Rajesh Sharma, R/o B-42, Preet Vihar, Delhi - 110092
Opposite Party: Apex Electronics Retail Ltd., Connaught Place, New Delhi

FACTS OF THE CASE:
1. On 15th January 2024, the Complainant purchased a high-performance Apex Pro X Laptop for Rs. 85,000/- vide Tax Invoice No. APX/2024/0912 from the Opposite Party with a 2-year warranty card attached.
2. Within 2 weeks of purchase, the laptop began shutting down abruptly within 15 minutes of booting due to severe motherboard overheating.
3. The Complainant deposited the device at the Opposite Party authorized service centre on 2nd February 2024 vide Service Job Sheet No. SRV-7712.
4. An authorized inspection technician confirmed in writing: 'Manufacturing defect in heat pipe thermal mounting causing motherboard thermal shutdown.'
5. The Opposite Party refused replacement or refund, alleging without evidence that the issue arose from user software installation.
6. The Complainant served a formal legal notice dated 20th February 2024 via registered post demanding a full refund or defect-free replacement unit.
7. The Opposite Party acknowledged receipt on 23rd February 2024 but failed to resolve the grievance.

RELIEFS SOUGHT:
1. Full refund of purchase price of Rs. 85,000/- with interest @ 12% p.a.
2. Compensation of Rs. 30,000/- for harassment and disruption of professional work.
3. Litigation expenses of Rs. 15,000/-.

LIST OF ATTACHED DOCUMENTS:
1. Tax Invoice No. APX/2024/0912 dated 15/01/2024 (Proof of Purchase).
2. Manufacturer 2-Year Warranty Certificate.
3. Authorised Service Job Sheet No. SRV-7712 confirming thermal hardware defect.
4. Legal Notice dated 20/02/2024 with postal delivery tracking receipt.
"""
    },
    "missing_invoice": {
        "title": "Missing Invoice (Procedural Dismissal)",
        "case_id": "CC-2024-DEFECT-002",
        "description": "Smartphone claim missing tax invoice / proof of purchase. Triggers early stop.",
        "text": """
INFORMAL COMPLAINT LETTER
To: Consumer Court Forum

I bought a smartphone 6 months ago from an electronics store in the city market for roughly Rs. 24,000.
The phone battery swollen up and cracked the glass screen.
I visited the seller but they said without the original bill they cannot honor any service.
I misplaced the paper receipt and tax invoice during house shifting, but I have the phone box with IMEI number.
I want the court to order the shopkeeper to give me a replacement phone and Rs. 50,000 compensation.

Documents available:
1. Photo of swollen phone.
2. Original cardboard packaging box.
(Note: Tax invoice / receipt is misplaced and unavailable).
"""
    }
}


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "NyayaSim GBA Courtroom Backend"}


@app.get("/api/samples")
def get_samples():
    return SAMPLE_CASES


async def run_simulation_stream(req: SimulationRequest) -> AsyncGenerator[str, None]:
    """Generates SSE events matching the courtroom animation phases."""
    gateway = get_default_gateway()

    def make_event(event_type: str, payload: dict) -> str:
        return json.dumps({"type": event_type, "data": payload})

    import uuid
    run_id = str(uuid.uuid4())
    case_id = req.case_id or f"CASE-{run_id[:6].upper()}"

    # INITIAL STATE
    yield make_event("system", {
        "message": "Courtroom session convened.",
        "case_id": case_id,
        "run_id": run_id
    })
    await asyncio.sleep(0.4)

    # =========================================================================
    # PHASE 1: CASE INTAKE / CLERK READING
    # =========================================================================
    yield make_event("phase_change", {
        "phase": 1,
        "phase_name": "PHASE 1: CASE REGISTRATION & INTAKE",
        "banner": "phase_banner.png",
        "active_character": "clerk",
        "pose": "idle"
    })
    await asyncio.sleep(0.6)

    yield make_event("dialogue", {
        "speaker": "Court Clerk",
        "role": "Peshkar / Registry Officer",
        "character": "clerk",
        "pose": "reading",
        "text": f"Calling Matter No. {case_id}! The Registry has received the consumer petition and is verifying formal pleadings."
    })
    await asyncio.sleep(1.0)

    # Process Intake Agent
    intake_agent = IntakeAgent(gateway=gateway)
    case_file = intake_agent.process(
        raw_case_text=req.case_text,
        case_id=case_id,
        case_type="consumer_dispute"
    )

    claimant_party = next((p.name for p in case_file.parties if p.role.lower() == 'claimant'), "Rajesh Sharma")
    respondent_party = next((p.name for p in case_file.parties if p.role.lower() == 'respondent'), "Apex Electronics")
    relief_text = "; ".join(case_file.relief_sought) if case_file.relief_sought else "Refund & Compensation under CPA 2019"

    yield make_event("case_file_ready", {
        "case_file": case_file.model_dump(),
        "summary": case_file.narrative_summary,
        "parties": [p.name for p in case_file.parties],
        "claimed_relief": relief_text
    })

    yield make_event("dialogue", {
        "speaker": "Court Clerk",
        "role": "Registry Officer",
        "character": "clerk",
        "pose": "presenting",
        "text": f"Pleadings verified for Complainant {claimant_party}. "
                f"Grievance asserted against {respondent_party}. "
                f"Relief sought: {relief_text}."
    })
    await asyncio.sleep(1.2)

    # =========================================================================
    # PHASE 2: PROCEDURAL AUDIT / REGISTRY AUDIT
    # =========================================================================
    yield make_event("phase_change", {
        "phase": 2,
        "phase_name": "PHASE 2: PROCEDURAL REGISTRY AUDIT",
        "banner": "phase_banner.png",
        "active_character": "judge",
        "pose": "listening"
    })
    await asyncio.sleep(0.6)

    yield make_event("dialogue", {
        "speaker": "Presiding Judge",
        "role": "Bench President",
        "character": "judge",
        "pose": "thinking",
        "text": "Before proceeding to arguments on merits, let the bench audit statutory compliance under the Consumer Protection Act, 2019."
    })
    await asyncio.sleep(1.0)

    checker_agent = ProceduralChecker(gateway=gateway)
    checklist_results, issues = checker_agent.check(case_file)

    for item in checklist_results:
        is_pass = item.status == ItemStatus.PRESENT
        yield make_event("checklist_item", {
            "item_id": item.item_code,
            "title": item.title,
            "status": "PASS" if is_pass else "FAIL",
            "is_critical": item.is_critical,
            "notes": item.reason or "",
            "defect": item.reason if not is_pass else ""
        })
        await asyncio.sleep(0.5)

    should_stop, critical_defects = evaluate_early_stop(checklist_results)

    if should_stop:
        # Dramatic Dismissal
        yield make_event("banner_splash", {
            "type": "HOLD_IT",
            "banner_file": "hold_it.png",
            "character": "judge",
            "pose": "gavel"
        })
        await asyncio.sleep(1.0)

        defect_msg = ", ".join([d.title for d in critical_defects])
        yield make_event("dialogue", {
            "speaker": "Presiding Judge",
            "role": "Bench President",
            "character": "judge",
            "pose": "gavel",
            "text": f"HOLD IT! Critical statutory documents are absent from the record: [{defect_msg}]. "
                    f"Under Section 35 of the Act, this commission cannot list a matter on merits without essential purchase evidence. "
                    f"PROCEEDINGS ARRESTED AT THRESHOLD."
        })
        await asyncio.sleep(1.5)

        escalation = EscalationResult(
            decision=EscalationDecision.HUMAN_HEARING_NEEDED,
            reasons=[f"Critical defects: {defect_msg}. Regularization required."],
            facts_undisputed=False,
            documents_complete=False,
            law_verified=False,
            judges_unanimous=False
        )

        reviewer = ReviewerAgent(gateway=gateway)
        report = reviewer.generate_report(
            case_file=case_file,
            run_id=run_id,
            checklist_results=checklist_results,
            issues=issues,
            escalation=escalation,
            is_early_stop=True
        )

        yield make_event("complete", {
            "state": RunState.STOPPED_EARLY.value,
            "final_report": report.model_dump(),
            "decision": "THRESHOLD_STOP",
            "reason": f"Critical checklist item missing: {defect_msg}"
        })
        return

    # Passed checklist
    yield make_event("dialogue", {
        "speaker": "Presiding Judge",
        "role": "Bench President",
        "character": "judge",
        "pose": "listening",
        "text": "All statutory documents are present and prima facie compliant. Counsel may now open arguments."
    })
    await asyncio.sleep(1.0)

    # =========================================================================
    # PHASE 3: ADVERSARIAL DEBATE (ROUNDS 1 & 2)
    # =========================================================================
    yield make_event("phase_change", {
        "phase": 3,
        "phase_name": "PHASE 3: ADVERSARIAL LAWYER DEBATE",
        "banner": "phase_banner.png",
        "active_character": "claimant",
        "pose": "talking"
    })
    await asyncio.sleep(0.6)

    from schemas.citation import Citation
    from schemas.common import CitationStatus
    lookup_engine = get_lookup_engine()
    verifier = VerifierAgent(gateway=gateway, lookup=lookup_engine)

    # Search corpus candidates based on narrative
    query = f"{case_file.narrative_summary} {' '.join(case_file.claims)}"
    candidate_units = lookup_engine.search_bm25(query, top_k=3)
    if not candidate_units:
        candidate_units = [lookup_engine.lookup_exact("Section 2(10)"), lookup_engine.lookup_exact("Section 2(11)")]

    raw_cits = []
    for u in candidate_units:
        if u:
            raw_cits.append(Citation(
                citation_id=f"CIT-{u['unit_id']}",
                claimed_reference=u["section"],
                matched_unit_id=u["unit_id"],
                proposition=u["title"],
                status=CitationStatus.UNCLEAR,
                source_text=u["text"],
                origin="statutory_corpus"
            ))

    citations = verifier.verify_all(raw_cits)
    log_step(run_id, "VerifierAgent", query[:200], [c.model_dump() for c in citations])

    claimant_lawyer = LawyerAgent(side="claimant", gateway=gateway)
    respondent_lawyer = LawyerAgent(side="respondent", gateway=gateway)

    # --- ROUND 1: Claimant Opens ---
    arg_c1 = claimant_lawyer.draft_argument(case_file=case_file, round_num=1, verified_citations=citations)

    yield make_event("banner_splash", {
        "type": "TAKE_THAT",
        "banner_file": "take_that.png",
        "character": "claimant",
        "pose": "pointing"
    })
    await asyncio.sleep(0.8)

    yield make_event("dialogue", {
        "speaker": "Advocate for Complainant",
        "role": "Claimant Counsel",
        "character": "claimant",
        "pose": "pointing",
        "text": f"{arg_c1.headline}: {arg_c1.reasoning}",
        "legal_basis": [c.claimed_reference for c in arg_c1.supporting_citations]
    })
    await asyncio.sleep(2.0)

    # --- ROUND 1: Respondent Rebuts ---
    arg_r1 = respondent_lawyer.draft_argument(
        case_file=case_file,
        round_num=1,
        verified_citations=citations,
        opposing_arguments=[arg_c1]
    )

    yield make_event("banner_splash", {
        "type": "OBJECTION",
        "banner_file": "objection.png",
        "character": "respondent",
        "pose": "objection"
    })
    await asyncio.sleep(0.8)

    yield make_event("dialogue", {
        "speaker": "Advocate for Respondent",
        "role": "Defense Counsel",
        "character": "respondent",
        "pose": "talking",
        "text": f"{arg_r1.headline}: {arg_r1.reasoning}",
        "concession": arg_r1.concession_flag
    })
    await asyncio.sleep(2.0)

    # --- ROUND 2: Claimant Counter ---
    arg_c2 = claimant_lawyer.draft_argument(
        case_file=case_file,
        round_num=2,
        verified_citations=citations,
        opposing_arguments=[arg_r1]
    )

    yield make_event("dialogue", {
        "speaker": "Advocate for Complainant",
        "role": "Claimant Counsel",
        "character": "claimant",
        "pose": "objection",
        "text": f"Sur-rebuttal: {arg_c2.headline}: {arg_c2.reasoning}"
    })
    await asyncio.sleep(2.0)

    # --- ROUND 2: Respondent Conclusion ---
    arg_r2 = respondent_lawyer.draft_argument(
        case_file=case_file,
        round_num=2,
        verified_citations=citations,
        opposing_arguments=[arg_c2]
    )

    yield make_event("dialogue", {
        "speaker": "Advocate for Respondent",
        "role": "Defense Counsel",
        "character": "respondent",
        "pose": "thinking",
        "text": f"Closing defense: {arg_r2.headline}: {arg_r2.reasoning}"
    })
    await asyncio.sleep(2.0)

    arguments = [arg_c1, arg_r1, arg_c2, arg_r2]

    # =========================================================================
    # PHASE 4: JUDICIAL DELIBERATION (3-JUDGE BENCH)
    # =========================================================================
    yield make_event("phase_change", {
        "phase": 4,
        "phase_name": "PHASE 4: 3-JUDGE BENCH DELIBERATION",
        "banner": "phase_banner.png",
        "active_character": "judge",
        "pose": "thinking"
    })
    await asyncio.sleep(0.6)

    yield make_event("banner_splash", {
        "type": "HOLD_IT",
        "banner_file": "hold_it.png",
        "character": "judge",
        "pose": "gavel"
    })
    await asyncio.sleep(0.8)

    yield make_event("dialogue", {
        "speaker": "Presiding Judge",
        "role": "Bench President",
        "character": "judge",
        "pose": "gavel",
        "text": "Silence in the Commission! Arguments have concluded. The members of the Bench will now enter sealed judicial deliberation."
    })
    await asyncio.sleep(1.5)

    judge_bench = create_judge_bench(gateway=gateway)
    stage1_opinions = []

    for judge in judge_bench:
        op = judge.deliberate_stage1(
            case_file=case_file,
            checklist_results=checklist_results,
            issues=issues,
            verified_citations=citations,
            arguments=arguments
        )
        stage1_opinions.append(op)
        yield make_event("judge_stage1", {
            "judge_id": op.judge_id,
            "persona": judge.name,
            "verdict": op.verdict,
            "confidence": op.confidence,
            "reasoning": op.reasoning[:200] + "..." if len(op.reasoning) > 200 else op.reasoning
        })
        await asyncio.sleep(0.8)

    # Stage 2 Comparison
    final_opinions = []
    for i, judge in enumerate(judge_bench):
        peers = [op for j, op in enumerate(stage1_opinions) if j != i]
        op2 = judge.deliberate_stage2(stage1_opinion=stage1_opinions[i], peer_opinions=peers)
        final_opinions.append(op2)

    # Escalation Rule
    facts_undisputed = "dispute" not in arg_r1.reasoning.lower() and "disputed" not in arg_r2.reasoning.lower()
    escalation = evaluate_escalation(
        facts_undisputed=facts_undisputed,
        checklist_results=checklist_results,
        issues=issues,
        citations=citations,
        judge_opinions=final_opinions
    )

    # =========================================================================
    # PHASE 5: FINAL REPORT & DISPOSITION
    # =========================================================================
    yield make_event("phase_change", {
        "phase": 5,
        "phase_name": "PHASE 5: COMMISSION PRONOUNCEMENT",
        "banner": "phase_banner.png",
        "active_character": "judge",
        "pose": "verdict"
    })
    await asyncio.sleep(0.6)

    reviewer = ReviewerAgent(gateway=gateway)
    report = reviewer.generate_report(
        case_file=case_file,
        run_id=run_id,
        checklist_results=checklist_results,
        issues=issues,
        escalation=escalation,
        citations=citations,
        arguments=arguments,
        judge_opinions=final_opinions,
        is_early_stop=False
    )

    majority_verdict = final_opinions[0].verdict
    avg_conf = sum(op.confidence for op in final_opinions) / len(final_opinions)

    yield make_event("banner_splash", {
        "type": "OBJECTION",
        "banner_file": "objection.png",
        "character": "judge",
        "pose": "verdict"
    })
    await asyncio.sleep(0.8)

    yield make_event("dialogue", {
        "speaker": "Presiding Judge",
        "role": "Bench Pronouncement",
        "character": "judge",
        "pose": "verdict",
        "text": f"FINAL ORDER: The Commission has deliberated. By consensus/majority, the finding is: {majority_verdict.replace('_', ' ')}. "
                f"Escalation recommendation: {escalation.decision.value}. Average judicial confidence: {avg_conf * 100:.1f}%."
    })
    await asyncio.sleep(1.5)

    yield make_event("complete", {
        "state": RunState.COMPLETED.value,
        "final_report": report.model_dump(),
        "decision": escalation.decision.value,
        "confidence": avg_conf,
        "opinions": [
            {
                "judge_id": op.judge_id,
                "persona": op.judge_name,
                "verdict": op.verdict,
                "confidence": op.confidence
            }
            for op in final_opinions
        ]
    })


@app.post("/api/simulate")
async def simulate(req: SimulationRequest):
    """Streams SSE courtroom events for the provided case text."""
    async def sse_wrapper():
        try:
            async for raw_data in run_simulation_stream(req):
                yield {"event": "courtroom_event", "data": raw_data}
        except Exception as e:
            traceback.print_exc()
            err_data = json.dumps({
                "type": "dialogue",
                "data": {
                    "speaker": "System Error",
                    "role": "Server Exception",
                    "character": "judge",
                    "pose": "gavel",
                    "text": f"Server encountered error: {str(e)}"
                }
            })
            yield {"event": "courtroom_event", "data": err_data}

    return EventSourceResponse(sse_wrapper())


@app.post("/api/simulate/batch")
async def simulate_batch(req: SimulationRequest):
    """
    Executes the simulation and returns all courtroom dialogue events in an array.
    Tailored for Visual Novel engines like Ren'Py and Godot that consume JSON events sequentially.
    """
    dialogues = []
    checklist = []
    verdict = None

    async for raw_data in run_simulation_stream(req):
        try:
            parsed = json.loads(raw_data)
            ev_type = parsed.get("type")
            ev_data = parsed.get("data", {})
            if ev_type == "dialogue":
                dialogues.append(ev_data)
            elif ev_type == "checklist_item":
                checklist.append(ev_data)
            elif ev_type == "complete":
                verdict = ev_data
        except Exception:
            continue

    return {
        "status": "success",
        "case_id": req.case_id,
        "dialogues": dialogues,
        "checklist": checklist,
        "verdict": verdict,
    }



if __name__ == "__main__":
    import uvicorn
    print("Starting NyayaSim GBA Courtroom Backend on port 8000...")
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)
