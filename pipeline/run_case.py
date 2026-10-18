"""
NyayaSim CLI Runner
Executes a case through the pipeline orchestrator and renders the results.
Usage:
    py -3.11 pipeline/run_case.py --case <path_to_case.txt>
    py -3.11 pipeline/run_case.py --sample
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
from pipeline.orchestrator import PipelineOrchestrator
from tools.gateway import get_default_gateway

SAMPLE_CASE_DEFECTIVE = """
IN THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION AT NEW DELHI

COMPLAINT NO: CC/2024/889

IN THE MATTER OF:
Mr. Vikram Malhotra, Resident of Vasant Kunj, New Delhi ... COMPLAINANT
VERSUS
AcroTech Electronics Pvt. Ltd., Connaught Place, New Delhi ... OPPOSITE PARTY

STATEMENT OF COMPLAINT:
1. The Complainant states that on 15th October 2023, he purchased an AcroTech 4K Smart Television (Model: AT-55UHD) from an authorized dealer for a consideration of Rs. 48,000/-.
2. The television started experiencing severe display discoloration and frequent flickering within 10 days of installation.
3. The Complainant contacted customer service multiple times, and a technician visited on 2nd November 2023, acknowledging in a service slip that the panel was defective.
4. However, the Opposite Party refused to replace the defective unit or refund the amount, stating that physical panel faults are not covered.
5. The Complainant served a formal legal notice dated 20th November 2023 demanding refund or replacement within 15 days. The Opposite Party received the notice on 24th November 2023 but failed to provide any remedy.
6. PRAYER:
   a) Refund the purchase amount of Rs. 48,000/- with interest @ 12% p.a.
   b) Compensation of Rs. 25,000/- for mental harassment and deficiency of service.
   c) Litigation expenses of Rs. 10,000/-.

LIST OF DOCUMENTS ATTACHED:
1. Document No. 1: Retail Tax Invoice No. AT/DEL/9021 dated 15.10.2023.
2. Document No. 2: Manufacturer 1-Year Comprehensive Warranty Card.
3. Document No. 3: Service Technician Inspection Report dated 02.11.2023.
4. Document No. 4: Office copy of Legal Notice dated 20.11.2023 along with Postal Speed Post Delivery Tracking Receipt.
"""

SAMPLE_CASE_MISSING_INVOICE = """
IN THE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION AT BANGALORE

COMPLAINT UNDER CONSUMER PROTECTION ACT, 2019

Complainant: Sneha Rao, Indiranagar, Bangalore
Opposite Party: HyperMart Retail Pvt Ltd, Koramangala, Bangalore

GRIEVANCE:
I purchased a kitchen blender from HyperMart on 5th February 2024 for Rs. 3,500.
The motor burned out during normal operation on 12th February 2024.
I went back to the store to ask for an exchange, but the store manager refused to attend to me.
I sent them an email demanding a replacement, which they ignored.
I want my money back and compensation for the harassment caused to me.

Note: I seem to have misplaced the paper receipt given at the cash counter, but the store has CCTV footage of my purchase.
"""


def format_report_output(state, report):
    sep = "=" * 70
    print("\n" + sep)
    print(f"  NYAYASIM READINESS REPORT | RUN STATE: {state.value.upper()}")
    print(sep)
    print(f"Report ID:    {report.report_id}")
    print(f"Case ID:      {report.case_id}")
    print(f"Early Stop:   {'YES (Halting before judicial debate)' if report.is_early_stop else 'NO'}")
    print(f"Escalation:   {report.escalation.decision.value.upper()}")
    print("-" * 70)
    print("EXECUTIVE SUMMARY:")
    print(f"  {report.executive_summary}\n")

    print("ESCALATION REASONS:")
    for reason in report.escalation.reasons:
        print(f"  * {reason}")
    print()

    print("PROCEDURAL CHECKLIST AUDIT:")
    for res in report.checklist_results:
        status_marker = "[PASS]" if res.status.value == "present" else f"[{res.status.value.upper()}]"
        crit = " (CRITICAL)" if res.is_critical else ""
        print(f"  {status_marker:<14} {res.title}{crit}")
        print(f"                 Reason: {res.reason}")
    print()

    if report.issues:
        print("IDENTIFIED DEFECTS & ISSUES:")
        for iss in report.issues:
            print(f"  [{iss.severity.value.upper():<8}] {iss.title}")
            print(f"             {iss.description}")
        print()

    if report.verified_citations:
        print("VERIFIED STATUTORY PROVISIONS:")
        for c in report.verified_citations:
            print(f"  * {c.claimed_reference}")
            print(f"    Proposition: {c.proposition}")
        print()

    if report.arguments:
        print("ADVERSARIAL LAWYER DEBATE (2 ROUNDS):")
        for arg in report.arguments:
            side_badge = f"[{arg.side.upper()} - ROUND {arg.round_num}]"
            rebut = f" (Rebutting: {arg.answers_argument_id})" if arg.answers_argument_id else ""
            print(f"  {side_badge:<22} {arg.headline}{rebut}")
            print(f"    Reasoning: {arg.reasoning}")
            if arg.supporting_citations:
                cits = ", ".join([c.claimed_reference for c in arg.supporting_citations])
                print(f"    Citations: {cits}")
            print()

    if report.judge_opinions:
        print("3-MEMBER JUDICIAL BENCH DELIBERATION:")
        for op in report.judge_opinions:
            stage_tag = f"[{op.stage.upper()}]"
            rev_note = f" (REVISED FROM STAGE 1: {op.revision_explanation})" if op.revised_from_stage1 else ""
            print(f"  {op.judge_name} {stage_tag}:")
            print(f"    Verdict:    {op.verdict.upper()} (Confidence: {op.confidence*100:.0f}%)")
            print(f"    Reasoning:  {op.reasoning}{rev_note}")
            print()

    if report.unverified_or_unchecked_items:
        print("DISCLOSURE (UNCHECKED / OUT OF SCOPE):")
        for item in report.unverified_or_unchecked_items:
            print(f"  - {item}")
        print()

    print(sep)
    print(f"  {report.prototype_disclaimer}")
    print(sep + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run NyayaSim pipeline on a case file.")
    parser.add_argument("--case", type=str, help="Path to text case file")
    parser.add_argument("--sample", action="store_true", help="Run with built-in complete sample case")
    parser.add_argument("--missing", action="store_true", help="Run with sample case missing invoice (early-stop test)")

    parser.add_argument("--single-judge", action="store_true", help="Ablation: run with single judge instead of 3-judge bench")
    parser.add_argument("--no-verifier", action="store_true", help="Ablation: disable verifier filtering")

    args = parser.parse_args()

    if args.missing:
        case_text = SAMPLE_CASE_MISSING_INVOICE
        case_id = "CASE-MISSING-DOC-001"
    elif args.case:
        if not os.path.exists(args.case):
            print(f"Error: File '{args.case}' not found.")
            sys.exit(1)
        with open(args.case, "r", encoding="utf-8") as f:
            case_text = f.read()
        case_id = os.path.basename(args.case).replace(".txt", "")
    else:
        case_text = SAMPLE_CASE_DEFECTIVE
        case_id = "CASE-SAMPLE-TV-001"

    print(f"Starting NyayaSim Orchestrator for {case_id}...")
    if args.single_judge:
        print("  [ABLATION ACTIVE: Single-Judge Mode]")
    if args.no_verifier:
        print("  [ABLATION ACTIVE: Unverified Citation Injection Mode]")

    gateway = get_default_gateway()
    orchestrator = PipelineOrchestrator(gateway=gateway)

    state, report = orchestrator.run_case(
        raw_case_text=case_text,
        case_id=case_id,
        single_judge=args.single_judge,
        disable_verifier=args.no_verifier
    )
    format_report_output(state, report)


if __name__ == "__main__":
    main()
