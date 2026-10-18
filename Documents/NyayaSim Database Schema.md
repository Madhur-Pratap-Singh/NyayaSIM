# NyayaSim (AI Court Sim): Database Schema

The full relational schema for NyayaSim, written for PostgreSQL. It also works on SQLite with minor changes (replace UUID and JSONB types with text). The companion documents cover the product requirements, technical requirements, tech stack and workflow.

## 1. Entity overview

| Table | Purpose |
| --- | --- |
| users | People who use the app (optional) |
| case\_types | Supported dispute types |
| checklist\_items | Required items for each case type |
| cases | Case files |
| case\_parties | Parties in a case |
| case\_documents | Documents attached to or listed in a case |
| legal\_sources | Statutes and judgments in the corpus |
| legal\_units | Numbered sections or paragraphs |
| runs | One execution of the pipeline on a case |
| agent\_steps | Every agent call within a run |
| checklist\_results | Result of each checklist item in a run |
| issues | Problems found |
| citations | Every citation and its verification result |
| arguments | Lawyer arguments by round |
| judge\_opinions | Judge outputs by stage |
| reports | Final reports |
| test\_cases | Fictional cases with ground truth |
| planted\_defects | Known defects in test cases |
| eval\_runs | One evaluation execution |
| eval\_results | Score per test case per system |
| bias\_pairs | Original and identity-swapped case pairs |
| audit\_log | Access and change events |

- ## Relationship in words

* A **case type** has many checklist items and many cases.
* A **case** has many parties, documents and runs.
* A **run** has many agent steps, issues, citations, arguments, judge opinions and checklist results, and exactly one report.
* A **citation** may point to a legal unit; if it does not, it is recorded as not found.
* An **issue** points to the step that raised it, which gives the trace back to the exact input and output.
* A **test case** wraps a case with ground truth and has planted defects.
* An **evaluation run** has one result per test case, each linked to the pipeline run that produced it.
* A **bias pair** links two cases that differ only in one identity attribute and records whether the output changed.

- ## Design notes

* Storing raw agent inputs and outputs as JSON in agent\_steps keeps the trail complete even when schemas change.
* Separating citations from arguments lets the verifier work in one place and lets the test harness score citations directly.
* The is\_hidden flag on test cases supports holding back some cases until the final evaluation, so prompts are not tuned to every test.
* Judge opinions keep the independent version and the revised version as separate rows, so anchoring can be measured.
* The is\_fictional flag defaults to true and can be used to reject any case that is not marked fictional.
* The audit log records access and change events, so reviewers can see who opened or modified a case or report.
