# NyayaSim (AI Court Sim): Technical Requirements Document (TRD)

This document defines how NyayaSim is built: the architecture, each component's inputs, outputs and rules, the interfaces, and the engineering requirements for safety, testing and deployment. The companion documents cover the product requirements, tech stack, database schema and workflow.

## 1. Architecture overview

The system is a pipeline of specialised agents coordinated by an orchestrator. Each agent is a function with a typed input and a typed output (validated JSON). Agents that produce legal claims are separate from the agent that verifies them. A logging layer records everything.

Main components:

1. **Interface layer:** web app for upload, run and report viewing.
2. **API layer:** receives requests, starts runs, serves results.
3. **Orchestrator:** runs agents in order, applies branching rules, handles retries and errors.
4. **Agents:** intake, procedural checker, researcher, verifier, two lawyers, judge panel, meta-judge, reviewer.
5. **Knowledge layer:** legal corpus, section lookup tool, optional search index.
6. **Model gateway:** one wrapper through which all model calls pass, with retries, caching and spending tracking.
7. **Storage:** relational database for cases, runs, steps, issues, citations, reports and evaluations.
8. **Observability:** structured logs and trace view.
9. **Evaluation system:** baseline, test harness and bias tests.

## 2. Design principles

- **Separate writing from checking.** The component that produces a legal claim is never the one that verifies it.
- **Typed boundaries.** Every agent reads and writes validated JSON, so a bad output is caught at the boundary.
- **Code where code can decide.** Existence checks, escalation rules and checklist logic are code, not model judgments.
- **Default to a human hearing.** The system proposes a resolution only under strict conditions.
- **Everything is logged.** Any statement in a report can be traced to an agent step and its evidence.

## 3. Component specifications

### 3.1 Intake agent

- **Input:** raw case text or extracted PDF text, case type.
- **Output:** structured case file (parties, claims, relief, documents listed, dates, narrative).
- **Rules:** return only what the text supports; mark unknown fields as null; no legal conclusions.

### 3.2 Procedural checker

- **Input:** structured case file, checklist for the case type.
- **Output:** one result per checklist item (present, missing, unclear) with a reason and a pointer to the text that supports it.
- **Rules:** use the checklist only; raise an issue for each missing or unclear item; flag critical items so the orchestrator can stop early.

### 3.3 Researcher

- **Input:** structured claims.
- **Output:** list of candidate unit IDs from the corpus with a short reason.
- **Rules:** may only return IDs that exist in the lookup tool.

### 3.4 Verifier

- **Input:** a citation (unit ID or case reference) and the proposition it supports.
- **Output:** status (verified, not\_found, not\_supported, unclear), the retrieved text, and a short justification.
- **Rules:** step 1 is a code lookup for existence. Step 2 is a model judgment on support, run only if step 1 passes. The verifier never drafts arguments.

### 3.5 Lawyer agents (claimant side and respondent side)

- **Input:** structured case, verified citations, opposing arguments from the previous round.
- **Output:** list of arguments, each with supporting verified citations and the opposing point it answers.
- **Rules:** cite only verified material; answer specific opposing points; fixed number of rounds; a concession check flags any agreement without new evidence.

### 3.6 Judge agents (three, plus optional meta-judge)

- **Input:** structured case, verified material, final arguments, procedural issues.
- **Output:** opinion with reasoning, conclusion, and confidence.
- **Rules:** each judge writes and commits an opinion before seeing the others; then one comparison round where changes must be explained; then a vote. Judges use different prompt framings or different models. The meta-judge audits whether reasoning supports each vote.

### 3.7 Reviewer

- **Input:** all structured outputs and the escalation decision.
- **Output:** final report in the report schema.
- **Rules:** must list what could not be checked; must not introduce claims that are not in earlier outputs.

### 3.8 Escalation rule

A proposed resolution is allowed only if all of these hold: facts are undisputed, required documents are complete, applicable law is verified and clear, and all judges agree. Otherwise the decision is human hearing needed. This rule is implemented in code, not left to a model.

## 4. Data contracts

Every agent boundary uses a defined JSON format, kept in a schemas folder with an example for each.

| Format | Main fields |
| --- | --- |
| Case file | parties, claims, relief sought, documents listed, key dates, narrative |
| Checklist result | item code, status (present, missing, unclear), reason, evidence span |
| Issue | issue ID, category, description, severity, raised by, evidence |
| Citation | claimed reference, matched unit ID, proposition, status, shown text, justification, origin |
| Argument | side, round, point, answers (ID of the point it rebuts), citations, concession flag |
| Judge opinion | judge label, stage, reasoning, conclusion, confidence, change reason |
| Final report | issues, checklist results, verified and rejected citations, both sides' positions, judge views, escalation decision and reasons, what could not be checked |

Example of an issue record:

```json
{
  "issue_id": "I-003",
  "category": "missing_document",
  "description": "No proof of purchase is attached to the complaint.",
  "severity": "high",
  "raised_by": "procedural_checker"
}
```

## 5. Model gateway requirements

- Single module for all model calls, with model name, temperature and other settings recorded per call.
- Structured output enforced by schema validation, with a bounded number of retries on invalid output.
- Response caching keyed by prompt and settings, to reduce cost and make tests repeatable.
- Token and cost accounting per run and per agent.
- A configurable timeout and graceful failure that marks the step as failed instead of crashing the run.
- Ability to swap providers without changing agent code.

## 6. Knowledge layer requirements

- Corpus stored as structured units: ID, source name, heading, text, type (statute section or judgment paragraph).
- Lookup by exact ID returns exact text or an explicit not-found result.
- Search over units by keyword, optionally by embedding, used only by the researcher.
- Source provenance recorded for every document.

## 7. API design (suggested endpoints)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | /cases | Create a case from text or an uploaded file |
| GET | /cases/{id} | Fetch a case and its structured form |
| POST | /cases/{id}/runs | Start a pipeline run with chosen configuration |
| GET | /runs/{id} | Run status and step summaries |
| GET | /runs/{id}/report | Final report |
| GET | /runs/{id}/steps | All agent steps with inputs and outputs |
| GET | /issues/{id}/trace | Evidence trail for one issue |
| POST | /eval/runs | Start an evaluation over the test set |
| GET | /eval/runs/{id} | Evaluation scores |
| GET | /sources/{unit\_id} | Retrieve a legal unit by ID |

## 8. Error handling

- Invalid model output: retry with the validation error, then mark the step failed.
- Missing critical documents: orchestrator stops and sends a short report directly.
- Citation not found: mark the citation rejected, record the issue, continue.
- Provider outage: the run is marked failed with a clear reason and can be resumed from the last completed step.

## 9. Security and privacy

- Fictional data only; uploads are checked for obvious personal identifiers and rejected or masked.
- API keys stored in environment variables or a secrets manager, never in the repository.
- Role-based access if the app has accounts (admin, reviewer, evaluator).
- Prompt injection awareness: case text is treated as data, not instructions. Agent prompts state this explicitly and outputs are schema-validated.
- Logs may contain case text, so access to logs is restricted.

## 10. Observability and traceability

- Every step stores input, output, model, settings, token counts and status.
- Every issue links to the step that raised it and the evidence it used.
- A trace tool prints the chain for any report statement.

## 11. Testing strategy

| Level | What is tested |
| --- | --- |
| Unit tests | Lookup tool, schema validation, escalation rule, checklist logic |
| Agent tests | Each agent on a small set of cases with known answers |
| Pipeline tests | Whole run from case file to report on all test cases |
| Evaluation | Baseline versus full system on the scoring metrics |
| Robustness | Repeated runs of the same case; consistency of results |
| Bias tests | Identity-swap pairs; flip rate |
| Anchoring test | Frequency with which the final result mirrors judge one |
| Adversarial inputs | Case text containing instructions or fake citations |

## 12. Deployment

- Containerised app with environment-based configuration.
- Separate configuration for local development and the demo environment.
- Continuous integration runs unit tests and a small evaluation subset on every change.
- Demo build uses cached responses for the sample cases as a fallback if the provider is unreachable.

## 13. Suggested repository structure

```
nyayasim/
  README.md
  decisions.md
  data/
    corpus/            legal texts, split into numbered sections
    cases/             fictional case files
    ground_truth/      expected answers for each case
  schemas/             JSON formats shared by all agents
  agents/
    intake.py
    procedural_checker.py
    researcher.py
    verifier.py
    lawyer.py
    judge.py
    reviewer.py
  pipeline/
    run_case.py        runs all agents in order
  tools/
    lookup.py          returns section text by ID
    logger.py
  eval/
    baseline.py        single-prompt comparison system
    run_tests.py
    bias_tests.py
  app/
    interface.py
  docs/
```
