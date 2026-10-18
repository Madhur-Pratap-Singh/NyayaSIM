# NyayaSim (AI Court Sim): Workflow

How a case moves through NyayaSim from submission to report, where the system decides to stop or escalate, and how the system itself is evaluated. The companion documents cover the product requirements, technical requirements, tech stack and database schema.

## 1. End-to-end pipeline

1. **Submit case.** The user selects a case type and pastes text or uploads a file. The system stores the case and records that it is fictional.
2. **Pre-checks.** Uploaded files are converted to text. The system checks for obvious personal identifiers and rejects or masks them. Case text is treated strictly as data.
3. **Intake.** The intake agent produces the structured case file. The output is validated against the schema. Invalid output triggers a bounded retry.
4. **Procedural check.** The checker compares the structured file to the checklist for the case type. Each item becomes present, missing or unclear, and issues are raised.
5. **Early stop decision.** If any critical checklist item is missing, the orchestrator stops and sends the results straight to the reviewer, who writes a short report recommending that the file be completed before a hearing. Otherwise the run continues.
6. **Research.** The researcher proposes legal units for each claim, restricted to the corpus.
7. **Citation collection.** Citations from the case file and from the researcher are gathered into one list.
8. **Verification.** The verifier checks every citation. Code confirms existence; the model judges support. Each citation gets a status and the source text. Rejected citations are recorded as issues and removed from the material passed on.
9. **Lawyer rounds.** The two lawyer agents argue using only verified material. Each round, an agent must answer specific points from the other side. A concession check flags agreement without new evidence. The number of rounds is fixed.
10. **Judge panel, independent stage.** Each judge writes an opinion and commits it before seeing the others.
11. **Judge panel, comparison stage.** Opinions are shared. A judge may revise but must explain any change. A vote is recorded.
12. **Meta-audit (optional).** The meta-judge checks whether the reasoning supports each vote and flags weak or copied reasoning.
13. **Escalation decision.** Code applies the rule: resolution proposed only if facts are undisputed, documents complete, law verified and clear, and judges unanimous. Otherwise human hearing needed.
14. **Report.** The reviewer builds the report from structured outputs: issues, checklist results, verified and rejected citations, both sides' positions, judge views, the decision and its reasons, and everything that could not be checked.
15. **Trace and review.** The user opens the report. Each statement links to its trace. A human reviews the output.

&#91;embedded content: pipeline flow · 10 steps, 1 early-stop decision\]

The diagram shows the main path. A missing critical item ends the run early with a short report; otherwise every citation is verified before the lawyers argue, and the escalation rule is applied by code at the end.

## 2. Decision points

| Decision | Condition | Result |
| --- | --- | --- |
| Output invalid | Fails schema after the allowed retries | Step marked failed; run can resume from that step |
| Critical item missing | A checklist item marked critical is missing | Stop early; short report |
| Citation not found | Existence check fails | Reject citation; raise issue; continue |
| Citation unsupported | Support check fails | Reject for that proposition; raise issue; continue |
| Concession without new evidence | Concession flag with no new evidence | Mark in log; lawyer retries the round |
| Judges disagree | Not unanimous after the comparison stage | Escalate to human hearing |
| Facts disputed | Procedural or lawyer stage shows a conflict in facts | Escalate to human hearing |
| Law unclear or unverified | A key proposition lacks a verified citation | Escalate to human hearing |

## 3. Run states

A run moves through these states: queued, running, then either stopped\_early, completed or failed. A failed run keeps all completed steps so it can resume from the last successful one.

## 4. Who does what in the pipeline

| Step | Component | Decided by |
| --- | --- | --- |
| Pre-checks | Upload handler | Code |
| Intake | Intake agent | Model, validated by schema |
| Procedural check | Procedural checker | Model against an explicit checklist |
| Early stop | Orchestrator | Code |
| Research | Researcher | Model, limited to corpus IDs |
| Verification | Verifier | Code for existence, model for support |
| Lawyer rounds | Lawyer agents | Model, with a concession check in code |
| Judge panel | Judge agents | Model, independent first opinions |
| Escalation | Escalation rule | Code |
| Report | Reviewer | Model, from structured outputs only |

## 5. Evaluation workflow

1. Load all test cases and their ground truth.
2. Run the baseline system on every case and store the scores.
3. Run the full system on every case and store the scores.
4. Run component ablations (for example, the full system without the verifier) to show what each component adds.
5. Run bias pairs and record how often outputs change.
6. Run the anchoring test on the judge panel.
7. Compare scores, list failures with an owner and likely cause, fix, and rerun.
8. Run the hidden cases once at the end and report the results as they are.

## 6. Team roles in the workflow

| Stage | Primary owner |
| --- | --- |
| Scope, checklist, escalation rules, ground truth | Legal and product lead |
| Agents and orchestration | Agent engineer |
| Corpus, lookup, verifier, schemas, logging | Data and verification engineer |
| Baseline, test harness, bias tests, interface, report | Evaluation and documentation lead |
