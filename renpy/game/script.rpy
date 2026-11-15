# NyayaSim - AI Courtroom Simulator (Ren'Py Edition)
# Inspired by Phoenix Wright & Summertime Saga VN Mechanics

# ==============================================================================
# CHARACTER DEFINITIONS
# ==============================================================================
define j = Character("Chief Judge (Textualist)", color="#e5c07b", who_outlines=[(2, "#181a1f")])
define j_welfare = Character("Judge Bannerjee (Welfare)", color="#98c379", who_outlines=[(2, "#181a1f")])
define j_proc = Character("Judge Chawla (Proceduralist)", color="#61afef", who_outlines=[(2, "#181a1f")])
define clerk = Character("Peshkar / Court Clerk", color="#c678dd", who_outlines=[(2, "#181a1f")])
define claimant = Character("Adv. Rajesh Sharma (Complainant)", color="#4fa6e8", who_outlines=[(2, "#181a1f")])
define respondent = Character("Adv. Sunita Mehta (Respondent)", color="#e06c75", who_outlines=[(2, "#181a1f")])
define sys_msg = Character("SYSTEM", color="#abb2bf", italic=True)

# ==============================================================================
# IMAGE & SPRITE DECLARATIONS
# ==============================================================================
image bg courtroom = Transform("images/backgrounds/Courtroom.png", size=(1920, 1080))
image bg chamber = Transform("images/backgrounds/Background.jpg", size=(1920, 1080))

# Clerk poses (Left Corner - Never Center Alone)
# pose_0: 677x369 (zoom=2.0 -> 738px height), pose_1: 429x581 (zoom=1.27 -> 738px height)
image clerk normal = Transform("images/sprites/clerk/frames/pose_0.png", zoom=2.0, xpos=0.18, xanchor=0.5, yalign=1.0)
image clerk reading = Transform("images/sprites/clerk/frames/pose_1.png", zoom=1.27, xpos=0.18, xanchor=0.5, yalign=1.0)
image clerk announce = Transform("images/sprites/clerk/frames/pose_2.png", zoom=2.0, xpos=0.18, xanchor=0.5, yalign=1.0)

# Judge poses (When Presiding Alone in Solo Shot)
image judge normal = Transform("images/sprites/judge/frames/pose_0.png", zoom=2.0, xpos=0.5, xanchor=0.5, yalign=1.0)
image judge thinking = Transform("images/sprites/judge/frames/pose_1.png", zoom=2.0, xpos=0.5, xanchor=0.5, yalign=1.0)
image judge gavel = Transform("images/sprites/judge/frames/pose_2.png", zoom=2.0, xpos=0.5, xanchor=0.5, yalign=1.0)
image judge speak = Transform("images/sprites/judge/frames/pose_3.png", zoom=2.0, xpos=0.5, xanchor=0.5, yalign=1.0)

# Judge Center Bench (ONLY when both Claimant and Respondent are on screen: 3-character wide panel)
# Scaled to zoom=1.15 and positioned at center elevated bench (ypos=780) to eliminate overlap with counsel tables
image judge_bench normal = Transform("images/sprites/judge/frames/pose_0.png", zoom=1.15, xpos=0.5, xanchor=0.5, ypos=780, yanchor=1.0)
image judge_bench thinking = Transform("images/sprites/judge/frames/pose_1.png", zoom=1.15, xpos=0.5, xanchor=0.5, ypos=780, yanchor=1.0)
image judge_bench gavel = Transform("images/sprites/judge/frames/pose_2.png", zoom=1.15, xpos=0.5, xanchor=0.5, ypos=780, yanchor=1.0)
image judge_bench speak = Transform("images/sprites/judge/frames/pose_3.png", zoom=1.15, xpos=0.5, xanchor=0.5, ypos=780, yanchor=1.0)

# Claimant Counsel (Player Advocate) - Left Corner (xpos=0.18)
# pose_0: 1289x1220 (zoom=0.605 -> 738px height), pose_1: 1536x1024 (zoom=0.72 -> 737px height)
image claimant normal = Transform("images/sprites/claimant/frames/pose_0.png", zoom=0.605, xpos=0.18, xanchor=0.5, yalign=1.0)
image claimant pointing = Transform("images/sprites/claimant/frames/pose_1.png", zoom=0.72, xpos=0.20, xanchor=0.48, yalign=1.0)
image claimant confident = Transform("images/sprites/claimant/frames/pose_2.png", zoom=0.605, xpos=0.18, xanchor=0.5, yalign=1.0)
image claimant object = Transform("images/sprites/claimant/frames/pose_3.png", zoom=0.72, xpos=0.20, xanchor=0.48, yalign=1.0)

# Respondent Counsel (Opponent / Female Lawyer) - Right Corner (xpos=0.82)
# Anchored at center of character (xanchor=0.5) at xpos=0.82 to keep her on the right counsel bench without overlapping center judge
image respondent normal = Transform("images/sprites/respondent/frames/pose_0.png", zoom=2.0, xpos=0.82, xanchor=0.5, yalign=1.0)
image respondent smirk = Transform("images/sprites/respondent/frames/pose_1.png", zoom=2.0, xpos=0.82, xanchor=0.5, yalign=1.0)
image respondent object = Transform("images/sprites/respondent/frames/pose_2.png", zoom=2.0, xpos=0.82, xanchor=0.5, yalign=1.0)
image respondent sweat = Transform("images/sprites/respondent/frames/pose_3.png", zoom=2.0, xpos=0.82, xanchor=0.5, yalign=1.0)


# Quick flash effect
transform flash_effect:
    Solid("#ffffff")
    alpha 0.8
    linear 0.2 alpha 0.0

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
label start:
    stop music fadeout 1.0
    scene bg courtroom with fade
    
    # Show top-right docket / evidence button
    show screen courtroom_docket_button

    show clerk announce with dissolve
    clerk "All rise! The District Consumer Disputes Redressal Commission, New Delhi is now convening."
    
    hide clerk with dissolve
    show judge normal with dissolve
    with hpunch
    
    j "Silence in the court. The Commission will take up today's simulation docket."
    j "Counsel and members of the bar, select the case file to present before the Bench."

label case_menu:
    menu:
        "Select Case for Simulation Hearing:"

        "Case 1: The Overheating Laptop (Full Merit Hearing - CPA 2019)":
            jump case_laptop_hearing

        "Case 2: The Missing Invoice (Procedural Dismissal / Early Stop)":
            jump case_missing_invoice

        "Case 3: Enter Custom Case Pleading (Live Gemini AI Simulation)":
            jump case_custom_hearing

        "Check NyayaSim FastAPI Backend Connection":
            jump check_server_status


# ==============================================================================
# CASE 1: FULL MERIT HEARING (LAPTOP THERMAL DEFECT)
# ==============================================================================
label case_laptop_hearing:
    scene bg courtroom with fade
    show screen courtroom_docket_button

    show clerk reading with dissolve
    clerk "Calling Matter No. CC-2024-LAPTOP-001!"
    clerk "Complainant Rajesh Sharma versus Apex Electronics Retail Ltd."
    clerk "Petition filed under Section 35 of the Consumer Protection Act, 2019 claiming refund of Rs. 85,000/- with compensation."
    
    hide clerk with dissolve
    show judge normal with dissolve
    j "Registry has received the petition. Before we proceed to arguments, the Commission will verify procedural readiness."

    # Procedural Verification
    show judge thinking
    j "Intake Auditor report: Tax Invoice present. 2-Year Warranty present. Statutory Notice served on 20/02/2024."
    j "Pleadings are in order. We will now hear oral arguments on defect and liability."

    # Adversarial Debate Round 1
    show claimant normal with moveinleft
    claimant "Much obliged, Your Honour."
    show claimant pointing
    claimant "My client purchased an Apex Pro X laptop for Rs. 85,000/-. Within 14 days, the unit suffered continuous thermal shutdowns within 15 minutes of booting."
    claimant "The opposite party has steadfastly refused a replacement or refund, forcing my client into severe professional disruption."

    # Respondent Objection
    show respondent smirk with moveinright
    with vpunch
    respondent "Objection, Your Honour! This entire claim is completely fabricated!"
    show respondent object
    respondent "The complainant downloaded heavy unauthorized software that overloaded the thermal envelope!"
    respondent "The retailer is not liable for consumer misuse under Section 2(10) of the Act!"

    # Player Interactive Decision 1 (Judge in Center Bench between both lawyers)
    show judge_bench normal
    j "Counsel for the Complainant, how do you answer the Respondent's objection?"

    menu:
        "Present Exhibit P-3: Authorised Service Job Sheet SRV-7712":
            $ player_score = 100
            jump counter_jobsheet_success

        "Argue verbal consumer hardship without referencing technical documents":
            $ player_score = 40
            jump counter_jobsheet_weak

label counter_jobsheet_success:
    show claimant confident
    with hpunch
    claimant "I draw the Bench's attention to Exhibit P-3 in the Docket — Service Job Sheet No. SRV-7712!"
    claimant "This inspection was conducted by the Opposite Party's OWN authorised service technician on 2nd February 2024!"
    show claimant pointing
    claimant "The technician's signed finding states verbatim: 'Manufacturing defect in heat pipe thermal mounting causing motherboard thermal shutdown.'!"
    
    # Opponent shocked
    show respondent sweat
    with vpunch
    respondent "W-What?! That technician report was an internal preliminary note, not meant for legal proceedings!"

    show judge_bench speak
    with hpunch
    j "An admission by the manufacturer's own authorized agent is binding, Counsel Mehta. Section 38(2)(c) defect threshold is prima facie satisfied."
    jump debate_round_2

label counter_jobsheet_weak:
    show claimant normal
    claimant "Your Honour, my client is an honest citizen who cannot even turn on his computer to do his office work!"
    show respondent smirk
    respondent "Emotional appeals cannot substitute for strict statutory proof of defect under Section 2(10)!"
    show judge_bench thinking
    j "Counsel Sharma, consumer hardship alone cannot replace technical proof. Please substantiate with evidence from your docket."
    show claimant pointing
    claimant "Understood, Your Honour. We tender Exhibit P-3 — the signed Authorized Job Sheet confirming motherboard thermal pipe failure!"
    show respondent sweat
    respondent "Tsk... very well."
    jump debate_round_2

# Adversarial Debate Round 2: Limitation & Remedy
label debate_round_2:
    show respondent object
    respondent "Even if a defect exists, the Complainant cannot demand an outright cash refund!"
    respondent "Under our retailer terms and conditions, we are only obligated to attempt motherboard repairs!"
    
    show claimant object
    with hpunch
    claimant "Point of Law, Your Honour!"
    claimant "Under Section 39(1)(a) and 39(1)(b) of the Consumer Protection Act 2019, the Commission holds statutory power to order full return of the price paid!"
    claimant "A consumer cannot be forced to accept a defective, refurbished motherboard on a brand-new Rs. 85,000/- device!"

    # Judicial Deliberation Phase
    scene bg chamber with fade
    show screen courtroom_docket_button
    
    j "The Commission has heard both sides. The Bench will now retire for judicial deliberation."

    # 3-Judge Deliberation Panel
    show judge thinking with dissolve
    j "Chief Judge (Textualist): Let us examine the statutory statutory strictures. Section 35 complaint is within the 2-year limitation under Section 69. Proof of purchase is verified."

    show judge normal
    j_welfare "Judge Bannerjee (Welfare): The Complainant is a software engineer whose livelihood was halted. The Opposite Party's refusal to replace the unit after their own technician verified a hardware fault constitutes gross deficiency in service under Section 2(11)."

    j_proc "Judge Chawla (Proceduralist): All notice requirements satisfied. Registered postal acknowledgment on record. No triable issue of fact remains. This matter is ripe for final escalation and disposal."

    # Verdict
    scene bg courtroom with fade
    show screen courtroom_docket_button
    show judge gavel with dissolve
    with hpunch
    
    j "ORDER! Having considered the statutory corpus and pleadings on record, the District Commission delivers its unanimous ruling:"
    
    j "1. The Opposite Party shall issue a full refund of Rs. 85,000/- to the Complainant within 30 days."
    j "2. Compensation of Rs. 25,000/- awarded for mental harassment and loss of professional utility."
    j "3. Litigation expenses of Rs. 10,000/- awarded."

    # Display Verdict Modal
    call screen verdict_report_modal("CASE ESCALATED & MERIT RELIEF GRANTED", "96", "3-0 Unanimous Bench Approval", "Full purchase refund of Rs. 85,000 + Rs. 25,000 compensation decreed. Matter closed with high court-readiness confidence.")
    
    jump case_menu

# ==============================================================================
# CASE 2: PROCEDURAL DISMISSAL (MISSING INVOICE / EARLY STOP)
# ==============================================================================
label case_missing_invoice:
    scene bg courtroom with fade
    show screen courtroom_docket_button

    show clerk reading with dissolve
    clerk "Calling Matter No. CC-2024-DEFECT-002: Informal Smartphone Complaint."
    clerk "Petitioner seeks replacement of smartphone due to swollen battery."

    show clerk normal
    clerk "Reporting from Preliminary Intake Audit: The petitioner has submitted a photo of the phone, but states the original tax invoice has been misplaced."

    hide clerk with dissolve
    show judge thinking with dissolve
    j "Where is the Tax Invoice or proof of purchase establishing privity of contract?"

    show claimant normal with moveinleft
    claimant "Your Honour, the Complainant lost the receipt during house shifting, but has the cardboard packaging box with the serial number..."

    show respondent smirk with moveinright
    with vpunch
    respondent "Objection! Without a tax invoice or registered proof of consideration, the petitioner does not qualify as a 'Consumer' under Section 2(7) of the Consumer Protection Act, 2019!"
    respondent "This matter fails at the threshold and must be dismissed at the intake stage!"

    show judge gavel
    with hpunch
    j "The objection is SUSTAINED."
    j "The NyayaSim Early-Stop Engine mandates dismissal when critical statutory documents are absent."
    j "Without proof of consideration, no statutory consumer dispute lies before this Commission."
    
    call screen verdict_report_modal("EARLY-STOP PROCEDURAL DISMISSAL", "25", "Dismissed at Threshold", "Petition dismissed for failure to establish consumer relationship under Sec 2(7). Early-stop rule triggered before merit debate.")

    jump case_menu

# ==============================================================================
# CASE 3: LIVE CUSTOM CASE PLEADING (GEMINI MULTI-AGENT SIMULATION)
# ==============================================================================
label case_custom_hearing:
    scene bg courtroom with fade
    show screen courtroom_docket_button
    show judge normal with dissolve

    j "Counsel, enter the facts and complaint details of your custom consumer dispute."

    $ custom_input = renpy.input("Enter Case Facts / Consumer Complaint:\n(Press Enter when finished, or leave default)", default="On 10th January 2024, complainant purchased a Refrigerator for Rs. 45,000 with 2-year warranty. The cooling compressor stopped working after 3 weeks. Authorized service technician inspected and noted manufacturing gas leak defect. Retailer refused replacement or refund.")
    
    $ custom_input = custom_input.strip()
    if not custom_input:
        $ custom_input = "Complainant purchased electronics item for Rs 45,000 with warranty. Product broke down within 3 weeks due to manufacturing defect. Opposite party refused refund or replacement."

    show clerk reading with dissolve
    clerk "Submitting custom pleading to NyayaSim Multi-Agent Backend (Gemini)..."
    clerk "AI Intake, Procedural Checker, Opposing Counsels, and 3-Judge Bench are deliberating. Please wait a moment..."

    $ sim_res = simulate_custom_case(custom_input)

    if sim_res.get("status") == "error":
        show judge thinking
        j "Simulation Server Communication Notice:"
        j "[sim_res['message']]"
        jump case_menu

    $ custom_dialogues = sim_res.get("dialogues", [])
    if not custom_dialogues:
        j "The backend processed the case but returned no dialogue lines."
        jump case_menu

    clerk "Hearing commences! Proceeding to examination of pleadings and statutory audit..."

    # Play back dialogues dynamically line-by-line!
    # Long AI paragraphs are split into short readable chunks (max 200 chars each).
    # Each chunk requires a click/Enter to advance — just like normal VN dialogue.
    python:
        for item in custom_dialogues:
            spk = item.get("speaker", "Court Speaker")
            txt = item.get("text", "")
            char = item.get("character", "clerk")

            # Determine which character + sprite to show for this line
            if "Rajesh" in spk or char == "claimant":
                renpy.hide("clerk")
                renpy.show("claimant pointing")
                renpy.show("respondent normal")
                speaker_char = claimant
            elif "Sunita" in spk or "Priya" in spk or "Mehta" in spk or char == "respondent":
                renpy.hide("clerk")
                renpy.show("claimant normal")
                renpy.show("respondent object")
                speaker_char = respondent
            elif "Judge" in spk or "Verma" in spk or "Chief" in spk or "Bannerjee" in spk or "Chawla" in spk or char == "judge":
                renpy.hide("clerk")
                renpy.show("claimant normal")
                renpy.show("respondent normal")
                renpy.show("judge_bench speak")
                speaker_char = j
            else:
                renpy.hide("claimant")
                renpy.hide("respondent")
                renpy.hide("judge_bench")
                renpy.hide("judge")
                renpy.show("clerk reading")
                speaker_char = clerk

            # Split long paragraph into short chunks, then show each one separately.
            # Player clicks/presses Enter to advance each chunk — proper VN pacing.
            chunks = chunk_dialogue(txt, max_chars=200)
            for chunk in chunks:
                safe_chunk = sanitize_for_renpy(chunk)
                renpy.say(speaker_char, safe_chunk)

        # Hearing concludes: Judge alone on Right corner
        renpy.hide("claimant")
        renpy.hide("respondent")
        renpy.hide("judge_bench")
        renpy.show("judge gavel")


    # Show final verdict modal if returned
    $ verdict_info = sim_res.get("verdict", {})
    if verdict_info:
        $ esc_dec = verdict_info.get("escalation", {}).get("decision", "HEARING COMPLETE")
        $ bench_text = verdict_info.get("majority_decision", "Order reserved on merits.")
        call screen verdict_report_modal("CUSTOM CASE FINAL VERDICT", "90", esc_dec, bench_text)

    jump case_menu


# ==============================================================================
# BACKEND SERVER HEALTH CHECK
# ==============================================================================
label check_server_status:
    scene bg chamber with fade
    
    $ is_online = check_backend_health()
    
    if is_online:
        show judge normal with dissolve
        j "NyayaSim FastAPI Server is ONLINE at http://127.0.0.1:8000."
        j "Real-time AI agent debate streaming is available."
    else:
        show judge thinking with dissolve
        j "NyayaSim Backend is currently OFFLINE or running on another port."
        j "You can start the backend anytime by running: python backend/server.py in your terminal."
        j "The visual novel offline simulation mode is fully playable right now."

    jump case_menu
