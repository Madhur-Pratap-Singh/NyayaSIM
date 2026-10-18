import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Don't draw top header on first page
        if self._pageNumber > 1:
            self.drawString(54, 11 * inch - 36, "NyayaSim (AI Court Sim) — 4-Person Engineering Roadmap")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer on all pages
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 54, 30, page_str)
        self.drawString(54, 30, "NyayaSim Project • Fictional Data Only • Free-Tier Architecture")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 42, 8.5 * inch - 54, 42)
        self.restoreState()

def create_roadmap_pdf(output_filename="NyayaSim_4_Person_Team_Roadmap.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#1A365D")    # Navy
    c_secondary = colors.HexColor("#2B6CB0")  # Blue
    c_accent = colors.HexColor("#C05621")     # Warm Amber/Rust
    c_dark = colors.HexColor("#2D3748")       # Charcoal
    c_light_bg = colors.HexColor("#F7FAFC")   # Off-white / light slate
    c_card_border = colors.HexColor("#E2E8F0")

    # Typography
    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=14
    ))

    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'SubSectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_dark
    ))

    styles.add(ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2C5282")
    ))

    styles.add(ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    ))

    styles.add(ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_dark
    ))

    styles.add(ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    ))

    story = []

    # TITLE & METADATA BLOCK
    story.append(Paragraph("NyayaSim: AI Court Readiness Simulator", styles['DocTitle']))
    story.append(Paragraph("Comprehensive 4-Person Engineering Roadmap & Implementation Plan (8-Week MVP)", styles['DocSubtitle']))
    
    notice_text = (
        "<b>Project Focus:</b> Pre-hearing readiness review for Indian civil disputes (Consumer Protection Act, 2019). "
        "Built strictly with free-tier tools (Python 3.11+, Gemini Flash/Groq, SQLite, Streamlit, pytest). "
        "<b>Core Rule:</b> Code decides wherever code can; conservative escalation to human judicial review."
    )
    notice_table = Table(
        [[Paragraph(notice_text, styles['CalloutText'])]],
        colWidths=[504]
    )
    notice_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BEE3F8")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(notice_table)
    story.append(Spacer(1, 10))

    # SECTION 1: SYSTEM OVERVIEW & ARCHITECTURE
    story.append(Paragraph("1. System Architecture & Operational Workflow", styles['SectionHeader']))
    arch_desc = (
        "NyayaSim acts as a pre-judicial automated audit panel. It ingests case files, verifies procedural completeness, "
        "validates statutory references against a closed corpus, simulates adversarial debate, runs multi-judge independent "
        "deliberation, and enforces a deterministic code-based escalation rule."
    )
    story.append(Paragraph(arch_desc, styles['BodyDark']))

    # Pipeline Steps Table
    pipeline_data = [
        [
            Paragraph("Stage", styles['TableHead']),
            Paragraph("Component / Agent", styles['TableHead']),
            Paragraph("Decided By", styles['TableHead']),
            Paragraph("Core Responsibility", styles['TableHead'])
        ],
        [
            Paragraph("1. Pre-checks", styles['TableCellBold']),
            Paragraph("Upload Handler", styles['TableCell']),
            Paragraph("Code", styles['TableCellBold']),
            Paragraph("Sanitizes input, masks PII, rejects non-fictional submissions.", styles['TableCell'])
        ],
        [
            Paragraph("2. Intake", styles['TableCellBold']),
            Paragraph("Intake Agent", styles['TableCell']),
            Paragraph("LLM + Schema", styles['TableCellBold']),
            Paragraph("Extracts parties, claims, prayers, listed documents, and key dates.", styles['TableCell'])
        ],
        [
            Paragraph("3. Procedural Check", styles['TableCellBold']),
            Paragraph("Procedural Checker", styles['TableCell']),
            Paragraph("LLM vs Checklist", styles['TableCellBold']),
            Paragraph("Checks Consumer Protection Act checklist; marks items Present/Missing/Unclear.", styles['TableCell'])
        ],
        [
            Paragraph("4. Early Stop Gate", styles['TableCellBold']),
            Paragraph("Orchestrator", styles['TableCell']),
            Paragraph("Code", styles['TableCellBold']),
            Paragraph("Halts pipeline immediately if critical checklist items are missing (e.g. proof of purchase).", styles['TableCell'])
        ],
        [
            Paragraph("5. Corpus Research", styles['TableCellBold']),
            Paragraph("Researcher", styles['TableCell']),
            Paragraph("BM25 / Exact", styles['TableCellBold']),
            Paragraph("Retrieves candidate legal units exclusively from the local JSON corpus.", styles['TableCell'])
        ],
        [
            Paragraph("6. Verification", styles['TableCellBold']),
            Paragraph("Two-Tier Verifier", styles['TableCell']),
            Paragraph("Code + LLM", styles['TableCellBold']),
            Paragraph("Tier 1: Exact code existence check. Tier 2: LLM textual support validation.", styles['TableCell'])
        ],
        [
            Paragraph("7. Adversarial Debate", styles['TableCellBold']),
            Paragraph("Lawyer Agents (2)", styles['TableCell']),
            Paragraph("LLM + Code Guard", styles['TableCellBold']),
            Paragraph("Claimant vs Respondent multi-round debate; restricted to verified citations only.", styles['TableCell'])
        ],
        [
            Paragraph("8. Judicial Panel", styles['TableCellBold']),
            Paragraph("Judge Agents (3)", styles['TableCell']),
            Paragraph("LLM (Diverse)", styles['TableCellBold']),
            Paragraph("Independent sealed opinions followed by a comparison/vote round.", styles['TableCell'])
        ],
        [
            Paragraph("9. Escalation Rule", styles['TableCellBold']),
            Paragraph("Escalation Engine", styles['TableCell']),
            Paragraph("Code", styles['TableCellBold']),
            Paragraph("Proposes resolution ONLY if facts undisputed, docs complete, law verified, and judges unanimous.", styles['TableCell'])
        ],
        [
            Paragraph("10. Readiness Report", styles['TableCellBold']),
            Paragraph("Reviewer Agent", styles['TableCell']),
            Paragraph("LLM from JSON", styles['TableCellBold']),
            Paragraph("Compiles final report, highlighting unresolved issues and evidence traces.", styles['TableCell'])
        ]
    ]

    pipeline_table = Table(pipeline_data, colWidths=[80, 105, 80, 239])
    pipeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, c_card_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(pipeline_table)
    story.append(Spacer(1, 14))

    # SECTION 2: 4-PERSON TEAM ROLE BREAKDOWN
    story.append(Paragraph("2. Four-Person Team Responsibilities & Ownership Matrix", styles['SectionHeader']))
    team_data = [
        [
            Paragraph("Role & Teammate", styles['TableHead']),
            Paragraph("Primary Domain", styles['TableHead']),
            Paragraph("Key Modules & Code Artifacts", styles['TableHead']),
            Paragraph("Acceptance Criteria / Deliverables", styles['TableHead'])
        ],
        [
            Paragraph("<b>Person 1</b><br/>Legal & Domain Architect", styles['TableCell']),
            Paragraph("Legal corpus, checklists, synthetic case design, ground-truth datasets, bias pairs", styles['TableCell']),
            Paragraph("<code>data/corpus/cpa_2019.json</code><br/><code>data/cases/*.txt</code><br/><code>data/ground_truth/*.json</code><br/>Checklist definitions", styles['TableCell']),
            Paragraph("Curated Consumer Protection Act JSON (25+ units); 15+ rich fictional cases with planted defects; 5 identity-swap bias pairs.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Person 2</b><br/>Agent & Orchestration Engineer", styles['TableCell']),
            Paragraph("Agent prompt engineering, orchestration pipeline, debate logic, judge panel", styles['TableCell']),
            Paragraph("<code>agents/intake.py</code><br/><code>agents/procedural_checker.py</code><br/><code>agents/lawyer.py</code><br/><code>agents/judge.py</code><br/><code>pipeline/run_case.py</code>", styles['TableCell']),
            Paragraph("Deterministic orchestrator state machine; strict concession checks; multi-judge comparison protocol; pure-code escalation logic.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Person 3</b><br/>Data & Verification Systems Engineer", styles['TableCell']),
            Paragraph("Model gateway, caching, rate limiting, Pydantic schemas, two-tier verifier, SQLite DB", styles['TableCell']),
            Paragraph("<code>tools/gateway.py</code><br/><code>schemas/*.py</code><br/><code>tools/lookup.py</code><br/><code>agents/verifier.py</code><br/><code>tools/db.py</code> (SQLite)", styles['TableCell']),
            Paragraph("Unified Gemini/Groq gateway with exponential backoff & file cache; two-tier verifier; relational SQLite audit log for every step.", styles['TableCell'])
        ],
        [
            Paragraph("<b>Person 4</b><br/>Evaluation, Frontend & Observability Lead", styles['TableCell']),
            Paragraph("Evaluation harness, baseline comparison, metrics calculation, Streamlit UI, demo", styles['TableCell']),
            Paragraph("<code>app/interface.py</code><br/><code>eval/baseline.py</code><br/><code>eval/run_tests.py</code><br/><code>eval/bias_tests.py</code><br/><code>tests/</code>", styles['TableCell']),
            Paragraph("Interactive Streamlit app with evidence trace drawer; single-prompt baseline runner; scoring dashboard (recall, citation accuracy, bias flip).", styles['TableCell'])
        ]
    ]

    team_table = Table(team_data, colWidths=[95, 110, 140, 159])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, c_card_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(team_table)
    story.append(Spacer(1, 14))

    # PAGE BREAK FOR DETAILED ROADMAP
    story.append(PageBreak())

    # SECTION 3: 8-WEEK SPRINT-BY-SPRINT PLAN
    story.append(Paragraph("3. Detailed 8-Week Implementation Plan (4 Sprints)", styles['SectionHeader']))
    story.append(Paragraph(
        "Structured in two-week agile sprints. Every week ends with a synchronous integration test to prevent drift.",
        styles['BodyDark']
    ))

    def make_sprint_block(sprint_num, sprint_title, weeks, objective, tasks_by_person, sync_milestone):
        elements = []
        elements.append(Paragraph(f"Sprint {sprint_num} ({weeks}): {sprint_title}", styles['SubSectionHeader']))
        elements.append(Paragraph(f"<b>Sprint Objective:</b> {objective}", styles['BodyDark']))
        
        table_rows = [
            [Paragraph("Teammate", styles['TableHead']), Paragraph("Weekly Action Items & Deliverables", styles['TableHead'])]
        ]
        
        for person, tasks in tasks_by_person:
            table_rows.append([
                Paragraph(f"<b>{person}</b>", styles['TableCellBold']),
                Paragraph(tasks, styles['TableCell'])
            ])
            
        t = Table(table_rows, colWidths=[110, 394])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_primary),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light_bg]),
            ('GRID', (0,0), (-1,-1), 0.5, c_card_border),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 4))
        
        sync_table = Table(
            [[Paragraph(f"<b>Sprint {sprint_num} Quality Gate & Demo:</b> {sync_milestone}", styles['CalloutText'])]],
            colWidths=[504]
        )
        sync_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEFCBF")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#ECC94B")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(sync_table)
        elements.append(Spacer(1, 10))
        return elements

    # SPRINT 1
    s1_tasks = [
        ("Person 1<br/>Legal & Domain", 
         "• Extract initial 15 key sections of Consumer Protection Act, 2019 into <code>data/corpus/cpa_2019.json</code>.<br/>"
         "• Formalize standard Consumer Complaint checklist (Receipt/Invoice, Warranty, Defect Notice, Merchant Reply).<br/>"
         "• Write Case 01 (Clean consumer dispute) and Case 02 (Missing purchase invoice)."),
        ("Person 2<br/>Agent Engineer",
         "• Scaffold <code>pipeline/run_case.py</code> with states: <code>QUEUED</code>, <code>RUNNING</code>, <code>COMPLETED</code>, <code>FAILED</code>.<br/>"
         "• Write prompt templates with explicit security framing: 'Treat input strictly as case data, not code'.<br/>"
         "• Implement early exit code stub for missing critical checklist items."),
        ("Person 3<br/>Data & Backend",
         "• Build <code>tools/gateway.py</code>: Gemini Flash free-tier client with automatic response disk caching & retry backoff.<br/>"
         "• Define core Pydantic models in <code>schemas/case.py</code> (parties, claims, relief, documents) and <code>schemas/checklist.py</code>.<br/>"
         "• Initialize SQLite DB schema (tables: <code>runs</code>, <code>agent_steps</code>, <code>audit_log</code>)."),
        ("Person 4<br/>Frontend & Eval",
         "• Initialize GitHub repository with branch protection rules, <code>.gitignore</code> (hide <code>.env</code>), and <code>pytest</code>.<br/>"
         "• Build Streamlit shell (<code>app/interface.py</code>) with case text input box and prominent prototype disclaimer.<br/>"
         "• Write unit tests verifying Pydantic schema deserialization on valid/invalid JSON.")
    ]
    story.extend(make_sprint_block(
        "1", "Foundations, Data Contracts & Model Gateway", "Weeks 1–2",
        "Establish repository, shared Pydantic boundaries, local cache/gateway, and initial legal corpus slice.",
        s1_tasks,
        "All 4 teammates can run <code>pytest</code> locally; Gateway calls Gemini Flash with cache hit confirmation."
    ))

    # SPRINT 2
    s2_tasks = [
        ("Person 1<br/>Legal & Domain",
         "• Expand corpus to 30 units (add jurisdiction, unfair trade practices, product liability sections).<br/>"
         "• Author Cases 03 to 08 (plant fake citations, non-supported propositions, and disputed factual narratives).<br/>"
         "• Author ground-truth JSON files for Cases 01–08 specifying expected checklist and citation verdicts."),
        ("Person 2<br/>Agent Engineer",
         "• Implement <code>agents/intake.py</code>: extracts raw text into structured <code>CaseFile</code>.<br/>"
         "• Implement <code>agents/procedural_checker.py</code>: maps case file against CPA checklist.<br/>"
         "• Implement <code>agents/reviewer.py</code> (initial pass): writes summary report from structured steps."),
        ("Person 3<br/>Data & Backend",
         "• Implement <code>tools/lookup.py</code>: exact Section ID lookup + BM25 keyword search over corpus.<br/>"
         "• Implement <code>agents/verifier.py</code>: Step 1 = exact code lookup (existence); Step 2 = LLM check (proposition support).<br/>"
         "• Connect pipeline steps to SQLite so every prompt, response, and error is stored in <code>agent_steps</code>."),
        ("Person 4<br/>Frontend & Eval",
         "• Build Streamlit Checklist & Verification UI: display items as color-coded badges (Present/Missing/Unclear).<br/>"
         "• Build single-prompt baseline system (<code>eval/baseline.py</code>): passes raw text to Gemini in one prompt.<br/>"
         "• Write test runner comparing Baseline vs NyayaSim on planted missing documents.")
    ]
    story.extend(make_sprint_block(
        "2", "Core Intake, Checker, Verifier & Early Stop", "Weeks 3–4",
        "Deliver the working linear MVP: Intake -> Procedural Check -> Early Stop -> Verification -> Report.",
        s2_tasks,
        "An uploaded case with missing invoice stops early with an explainable report; valid case verifies real citations and rejects fake ones."
    ))

    # PAGE BREAK FOR SPRINT 3 & 4
    story.append(PageBreak())

    # SPRINT 3
    s3_tasks = [
        ("Person 1<br/>Legal & Domain",
         "• Design structured prompt arguments and defenses for Claimant vs Respondent lawyers.<br/>"
         "• Create 3 distinct Judicial philosophies/prompts: Judge A (Strict Textualist), Judge B (Consumer Welfare), Judge C (Proceduralist).<br/>"
         "• Author 5 demographic/identity-swap case pairs for bias testing (e.g. swap names/religions, keep facts identical)."),
        ("Person 2<br/>Agent Engineer",
         "• Implement <code>agents/lawyer.py</code>: 2-round Claimant/Respondent adversarial debate (must cite verified laws only).<br/>"
         "• Implement code concession check (flags if a lawyer concedes without new documentary evidence).<br/>"
         "• Implement <code>agents/judge.py</code>: Stage 1 (sealed independent opinions) -> Stage 2 (comparison round) -> Final vote.<br/>"
         "• Implement pure-code <code>pipeline/escalation.py</code>: strict conditions for resolution vs Human Hearing."),
        ("Person 3<br/>Data & Backend",
         "• Implement <code>agents/researcher.py</code>: uses BM25 to propose corpus sections for asserted claims.<br/>"
         "• Build Issue Trace API/Helper (<code>get_issue_trace(issue_id)</code>): fetches prompt, response, and source evidence.<br/>"
         "• Optimize gateway caching to prevent token burn during multi-round lawyer debate and 3-judge execution."),
        ("Person 4<br/>Frontend & Eval",
         "• Streamlit UI: add tabs for Lawyer Debate rounds, Judge opinions, and final Escalation verdict.<br/>"
         "• Build Interactive Traceability Drawer: clicking any report statement reveals its exact evidence chain.<br/>"
         "• Integrate PDF upload and text extraction (using PyMuPDF or pdfplumber).")
    ]
    story.extend(make_sprint_block(
        "3", "Adversarial Debate, Judicial Panel & Streamlit UI", "Weeks 5–6",
        "Full simulation functionality: 2-round lawyer debate, 3-judge deliberation, code escalation, and rich UI.",
        s3_tasks,
        "End-to-end simulation runs on Streamlit in < 3 mins (cached); judges debate without sycophancy; escalation logic triggers accurately."
    ))

    # SPRINT 4
    s4_tasks = [
        ("Person 1<br/>Legal & Domain",
         "• Curate 5 unseen 'hidden' test cases for final impartial evaluation.<br/>"
         "• Audit final output reports for legal coherence and factual accuracy.<br/>"
         "• Author final project documentation, ethical safeguards statement, and presentation slides."),
        ("Person 2<br/>Agent Engineer",
         "• Build ablation toggles (<code>--no-verifier</code>, <code>--single-judge</code>) to generate empirical ablation proof.<br/>"
         "• Implement run recovery: resume interrupted runs from the last successful step stored in SQLite.<br/>"
         "• Harden prompts against prompt-injection attacks embedded in case text."),
        ("Person 3<br/>Data & Backend",
         "• Package an offline demo bundle: pre-recorded SQLite database and cached API calls for bulletproof live presentation.<br/>"
         "• Run database performance checks, add export commands (export run report to Markdown and JSON).<br/>"
         "• Code cleanup, type checking with Pydantic, and repository documentation."),
        ("Person 4<br/>Frontend & Eval",
         "• Run complete test suite (<code>eval/run_tests.py</code>): compute Missing-doc Recall, Citation Accuracy, Escalation Accuracy.<br/>"
         "• Run bias test suite (<code>eval/bias_tests.py</code>): verify Bias Flip Rate is near zero on identity-swap pairs.<br/>"
         "• Build Evaluation Dashboard in Streamlit displaying comparative charts: NyayaSim vs Baseline.")
    ]
    story.extend(make_sprint_block(
        "4", "Evaluation, Bias Tests, Demo Hardening & Polish", "Weeks 7–8",
        "Benchmarking against baseline, bias testing, anchoring metrics, ablation study, and presentation readiness.",
        s4_tasks,
        "Evaluation suite outputs verifiable scores showing NyayaSim beats baseline; offline demo ready; clean code freeze."
    ))

    # SECTION 4: SUCCESS METRICS & EVALUATION TARGETS
    story.append(Paragraph("4. Target Evaluation Metrics & Success Criteria", styles['SectionHeader']))
    metrics_data = [
        [
            Paragraph("Metric", styles['TableHead']),
            Paragraph("Formula / Definition", styles['TableHead']),
            Paragraph("Baseline", styles['TableHead']),
            Paragraph("NyayaSim Target", styles['TableHead']),
            Paragraph("Evaluation Method", styles['TableHead'])
        ],
        [
            Paragraph("<b>Missing-Doc Recall</b>", styles['TableCell']),
            Paragraph("Planted missing items identified / Total planted missing items", styles['TableCell']),
            Paragraph("~55 - 65%", styles['TableCell']),
            Paragraph("<b>> 90%</b>", styles['TableCellBold']),
            Paragraph("Checked against ground-truth defect list", styles['TableCell'])
        ],
        [
            Paragraph("<b>Citation Accuracy</b>", styles['TableCell']),
            Paragraph("Citations correctly verified or flagged invalid / Total citations", styles['TableCell']),
            Paragraph("~40 - 55%", styles['TableCell']),
            Paragraph("<b>> 95%</b>", styles['TableCellBold']),
            Paragraph("Code lookup for existence + LLM check for support", styles['TableCell'])
        ],
        [
            Paragraph("<b>Escalation Accuracy</b>", styles['TableCell']),
            Paragraph("Correct 'Human Hearing' vs 'Proposed Resolution' decisions", styles['TableCell']),
            Paragraph("~60%", styles['TableCell']),
            Paragraph("<b>> 95%</b>", styles['TableCellBold']),
            Paragraph("Deterministic code rule checking 4 strict gates", styles['TableCell'])
        ],
        [
            Paragraph("<b>Wrongful Resolution Rate</b>", styles['TableCell']),
            Paragraph("Contested/defective cases wrongly proposed for resolution", styles['TableCell']),
            Paragraph("15 - 25%", styles['TableCell']),
            Paragraph("<b>0.0%</b>", styles['TableCellBold']),
            Paragraph("Critical safety metric: default to human hearing", styles['TableCell'])
        ],
        [
            Paragraph("<b>Judge Anchoring Rate</b>", styles['TableCell']),
            Paragraph("% of final verdicts identical only to Judge 1's initial opinion", styles['TableCell']),
            Paragraph("High (>70%)", styles['TableCell']),
            Paragraph("<b>< 30%</b>", styles['TableCellBold']),
            Paragraph("Independent sealed round before comparison round", styles['TableCell'])
        ],
        [
            Paragraph("<b>Demographic Bias Flip</b>", styles['TableCell']),
            Paragraph("% of cases where swapping names/demographics changes outcome", styles['TableCell']),
            Paragraph("10 - 20%", styles['TableCell']),
            Paragraph("<b>< 2.0%</b>", styles['TableCellBold']),
            Paragraph("5 identity-swap paired test cases", styles['TableCell'])
        ]
    ]

    metrics_table = Table(metrics_data, colWidths=[105, 135, 55, 65, 144])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, c_card_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 14))

    # SECTION 5: RISK MANAGEMENT & BEST PRACTICES
    story.append(Paragraph("5. Free-Tier Guardrails & Collaboration Protocol", styles['SectionHeader']))
    tips_data = [
        [
            Paragraph("<b>1. Free API Quota Safety:</b>", styles['TableCellBold']),
            Paragraph("Each member creates their own Google AI Studio key. All calls go through <code>tools/gateway.py</code> with disk caching enabled. Never rerun an identical prompt against the live API.", styles['TableCell'])
        ],
        [
            Paragraph("<b>2. GitHub Hygiene:</b>", styles['TableCellBold']),
            Paragraph("Never commit <code>.env</code>. Never push broken code to <code>main</code>. Use Pull Requests for every feature, reviewed by at least one other teammate.", styles['TableCell'])
        ],
        [
            Paragraph("<b>3. Zero Hallucination:</b>", styles['TableCellBold']),
            Paragraph("No open-web searches for legal statutes. All statutory citations are restricted to <code>data/corpus/cpa_2019.json</code>. Unverified citations are rejected immediately.", styles['TableCell'])
        ],
        [
            Paragraph("<b>4. Examiner Presentation:</b>", styles['TableCellBold']),
            Paragraph("Prepare a fallback offline mode using pre-recorded SQLite test runs so live network latency or API rate limits cannot derail the final academic evaluation.", styles['TableCell'])
        ]
    ]
    tips_table = Table(tips_data, colWidths=[130, 374])
    tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, c_card_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(tips_table)

    # Build the document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Roadmap PDF generated successfully: {output_filename}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "NyayaSim_4_Person_Team_Roadmap.pdf"
    create_roadmap_pdf(out_file)
