# NyayaSim (AI Court Sim): Product Requirements Document (PRD)

This document defines what NyayaSim should do, for whom, and how success is measured. The companion documents cover the technical requirements, tech stack, database schema and workflow.

## 1. Overview

NyayaSim is a multi-agent AI system that reviews a fictional Indian civil case file before human judicial review. Agents act as lawyers for both sides, legal researchers, procedural checkers and judges. They challenge each other, identify missing documents, and verify every legal reference against a controlled legal source set. A review agent then produces a report explaining the problems found and the possible next steps.

The product supports case preparation and reduces avoidable delays. It does not replace human judges and does not give legal advice to real people.

## 2. Problem statement

- Court-side AI tools in India focus on transcription and translation. None test whether a case file is complete and arguable before a hearing.
- Commercial legal research assistants answer questions but do not run adversarial review, and independent evaluations show they still produce wrong or unsupported citations.
- Research court simulators exist but target other legal systems and do not produce a readiness report.
- Multi-agent debate can converge on the first opinion or collapse into agreement, so a naive panel of AI judges is unreliable.

## 3. Goals

1. Detect missing documents and procedural defects in a case file.
2. Verify every legal citation against source text, and reject unsupported ones.
3. Surface the strongest arguments and weaknesses of both sides.
4. Produce an explainable, traceable readiness report.
5. Decide conservatively: recommend a human hearing unless strict conditions are met.
6. Provide measured evidence (against a baseline) that each component helps.

## 4. Non-goals

- Replacing or imitating a real judge's authority.
- Advising real litigants or processing real case files.
- Covering all branches of law. The prototype covers one dispute type.
- Predicting outcomes for the purpose of betting or negotiation.
- Multilingual support in the first version (see Open questions).

## 5. Users and personas

| Persona | Description | Main need |
| --- | --- | --- |
| Court clerk or registry reviewer (simulated) | Checks a file before listing it for hearing | Quick list of missing documents and defects |
| Junior lawyer or law student | Prepares a case | Strongest arguments for both sides and verified citations |
| Judge or judicial researcher (simulated) | Receives the file | Neutral summary, issues, and a recommendation on whether a hearing is needed |
| Project examiner or evaluator | Assesses the prototype | Transparent logs, test results and honest limitations |

## 6. User stories

1. As a clerk, I upload a case file and see which required documents are present, missing or unclear.
2. As a lawyer, I see every legal reference in the file marked verified, not found or not supported, with the source passage.
3. As a lawyer, I read both sides' arguments and rebuttals built only from verified material.
4. As a judge, I read independent opinions from several judge agents and see where they disagree.
5. As a judge, I see a clear escalation decision with reasons.
6. As an evaluator, I open the full trail for any statement in the report and see which agent produced it and from what evidence.
7. As an evaluator, I run the test suite and see scores for the baseline and the full system.

## 7. Functional requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-1 | Accept a case file (text or PDF) and a case type | Must |
| FR-2 | Extract parties, claims, relief, documents and key dates into a structured form | Must |
| FR-3 | Compare the file against the case-type checklist and mark each item present, missing or unclear | Must |
| FR-4 | Retrieve relevant legal provisions from the controlled corpus only | Must |
| FR-5 | Verify every citation: existence check by code, support check by model, with source passage shown | Must |
| FR-6 | Generate arguments for both sides using verified material only, with a fixed number of rebuttal rounds | Should |
| FR-7 | Generate independent opinions from multiple judge agents, then a comparison round and a vote | Should |
| FR-8 | Apply the escalation rule and output a decision with reasons | Must |
| FR-9 | Generate a final report listing issues, verified and rejected citations, both sides' positions, judge views, and what could not be checked | Must |
| FR-10 | Log every agent input and output for every run | Must |
| FR-11 | Provide a trace view for any issue in the report | Should |
| FR-12 | Provide a test harness that runs all test cases and reports scores | Must |
| FR-13 | Provide bias tests that swap identity attributes and report changes in output | Should |
| FR-14 | Display a visible prototype and fictional-data notice | Must |
| FR-15 | Support export of the report as PDF or Markdown | Could |

## 8. Non-functional requirements

- **Accuracy and honesty:** the system must say what it could not check instead of guessing.
- **Explainability:** every report statement links to an agent output and evidence.
- **Reproducibility:** a run can be repeated with the same inputs and settings, and differences are recorded.
- **Safety and privacy:** only fictional data; secrets never stored in the repository.
- **Cost control:** model spending is capped and cached where possible.
- **Usability:** a new user can run a case and read the report without assistance.
- **Maintainability:** each agent is a separate module with a typed input and output.

## 9. Success metrics

| Metric | Definition | Target direction |
| --- | --- | --- |
| Missing-document recall | Share of planted missing documents found | Higher than baseline |
| False alarm rate | Items flagged missing that were present | Lower than baseline |
| Citation accuracy | Share of citations correctly classified (verified, not found, not supported) | Higher than baseline, near complete for existence checks |
| Escalation accuracy | Share of cases where escalation matches ground truth | Higher than baseline |
| Wrongful resolution rate | Contested cases wrongly given a proposed resolution | As close to zero as possible |
| Judge anchoring rate | Share of cases where the final result only mirrors the first judge | Low |
| Bias flip rate | Share of identity-swap pairs where the output changes | Near zero |
| Traceability | Share of report statements that link to evidence | Complete |

## 10. MVP scope and later scope

**MVP:** intake agent, procedural checker, verifier, review agent, logging, baseline and test harness, simple interface.

**Later:** researcher with retrieval, lawyer agents, judge panel and meta-judge, bias test suite, PDF export, more dispute types, regional language support.

## 11. Assumptions and constraints

- One dispute type and a small, curated legal corpus.
- A hosted language model API is available within a spending limit.
- Cases are written by the team and are fictional.
- A human reviews all outputs; the system never issues binding decisions.

## 12. Risks

| Risk | Mitigation |
| --- | --- |
| Fabricated or misapplied citations | Mandatory verifier; unverified citations never reach lawyer agents |
| Sycophantic debate and judge anchoring | Fixed opposing roles, independent first opinions, concession checks, anchoring test |
| Biased outputs | Hide identity attributes unless legally relevant; identity-swap tests |
| Overclaiming accuracy | Report limitations plainly; evaluate against a baseline |
| Scope creep | Written scope and quality gates |

## 13. Open questions

- Which dispute type is chosen (consumer, tenancy, money recovery)?
- Which language models are used for which agents?
- Is regional language input needed, or only English?
- Are PDF uploads required in the first version or only pasted text?
