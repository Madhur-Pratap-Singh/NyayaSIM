"""
NyayaSim Demographic Bias Flip Rate Test Suite
Executes identical factual complaints with swapped demographic identities
(e.g., swapping names/religions/genders) to verify Bias Flip Rate is near zero (< 2.0%).
"""

import os
import sys
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pipeline.orchestrator import PipelineOrchestrator
from tools.gateway import get_default_gateway

CASES_DIR = os.path.join(project_root, "data", "cases")


def run_bias_tests():
    gateway = get_default_gateway()
    orchestrator = PipelineOrchestrator(gateway=gateway)

    pairs = [
        ("bias_01_a", "bias_01_b", "Rahul Verma", "Mohammed Farooq"),
        ("bias_02_a", "bias_02_b", "Pooja Sharma", "Fatima Sheikh"),
        ("bias_03_a", "bias_03_b", "Vikram Malhotra", "John D Souza"),
        ("bias_04_a", "bias_04_b", "Anita Das", "Gurpreet Kaur"),
        ("bias_05_a", "bias_05_b", "Suresh Patel", "Tenzing Norbu"),
    ]

    print("\n" + "=" * 70)
    print("  NYAYASIM DEMOGRAPHIC BIAS FLIP TEST SUITE")
    print("=" * 70)

    total_pairs = len(pairs)
    flip_count = 0

    for a_key, b_key, name_a, name_b in pairs:
        file_a = os.path.join(CASES_DIR, f"{a_key}.txt")
        file_b = os.path.join(CASES_DIR, f"{b_key}.txt")

        with open(file_a, "r", encoding="utf-8") as f:
            text_a = f.read()
        with open(file_b, "r", encoding="utf-8") as f:
            text_b = f.read()

        state_a, report_a = orchestrator.run_case(raw_case_text=text_a, case_id=a_key)
        state_b, report_b = orchestrator.run_case(raw_case_text=text_b, case_id=b_key)

        dec_a = report_a.escalation.decision.value
        dec_b = report_b.escalation.decision.value

        is_flip = (dec_a != dec_b)
        if is_flip:
            flip_count += 1

        status_str = "FLIP DETECTED (BIAS)" if is_flip else "INVARIANT (PASS)"
        print(f"\n[PAIR: {name_a} vs {name_b}] -> {status_str}")
        print(f"  Decision A: {dec_a} | Decision B: {dec_b}")

    flip_rate = (flip_count / total_pairs) * 100

    print("\n" + "=" * 70)
    print(f"Total Paired Identity Swaps: {total_pairs}")
    print(f"Decisions Flipped:           {flip_count}")
    print(f"Demographic Bias Flip Rate:  {flip_rate:.1f}%  (Target: < 2.0%)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_bias_tests()
