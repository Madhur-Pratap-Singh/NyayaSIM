# courtroom_screens.rpy - Courtroom HUD, Evidence Docket & Verdict Card

screen courtroom_docket_button():
    # Quick evidence bag button on the top right (Summertime Saga / Ace Attorney style)
    frame:
        xalign 0.98
        yalign 0.03
        background Solid("#1a1e24cc")
        padding (12, 8)
        textbutton "📜 Case File Docket":
            text_size 20
            text_color "#f1fa8c"
            text_hover_color "#50fa7b"
            action Show("courtroom_docket_modal")

screen courtroom_docket_modal():
    modal True
    zorder 100
    
    # Dark dimmed backdrop
    add Solid("#000000aa")
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1100
        ysize 720
        background Solid("#181b20f0")
        padding (30, 25)
        
        vbox:
            spacing 15
            
            hbox:
                text "🏛 Case File & Statutory Exhibits" size 30 color "#e5c07b" bold True
                null width 450
                textbutton "✕ Close" action Hide("courtroom_docket_modal"):
                    text_size 24
                    text_color "#ff5555"
                    text_hover_color "#ff6e6e"
            
            null height 5
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                draggable True
                ysize 560
                
                vbox:
                    spacing 16
                    
                    frame:
                        xfill True
                        background Solid("#23272e")
                        padding (15, 12)
                        vbox:
                            text "EXHIBIT P-1: Tax Invoice No. APX/2024/0912" size 20 color "#61afef" bold True
                            text "Dated 15/01/2024. Purchase price Rs. 85,000/- with registered GSTIN. Proves consumer relationship under Sec 2(7) CPA 2019." size 17 color "#abb2bf"
                    
                    frame:
                        xfill True
                        background Solid("#23272e")
                        padding (15, 12)
                        vbox:
                            text "EXHIBIT P-2: Manufacturer 2-Year Warranty Card" size 20 color "#61afef" bold True
                            text "Official warranty certificate valid until 15/01/2026. Explicitly covers motherboard, thermal pipe, and display." size 17 color "#abb2bf"

                    frame:
                        xfill True
                        background Solid("#23272e")
                        padding (15, 12)
                        vbox:
                            text "EXHIBIT P-3: Service Job Sheet SRV-7712 (Crucial Evidence)" size 20 color "#50fa7b" bold True
                            text "Authorised technician finding: 'Manufacturing defect in heat pipe thermal mounting causing motherboard thermal shutdown within 15 mins.' Conclusive proof under Sec 38(2)(c)." size 17 color "#abb2bf"

                    frame:
                        xfill True
                        background Solid("#23272e")
                        padding (15, 12)
                        vbox:
                            text "EXHIBIT P-4: Statutory Legal Notice & Proof of Delivery" size 20 color "#61afef" bold True
                            text "Served 20/02/2024 via Registered Speed Post. Delivery acknowledged 23/02/2024. 15-day notice period elapsed with no remedy." size 17 color "#abb2bf"

                    frame:
                        xfill True
                        background Solid("#23272e")
                        padding (15, 12)
                        vbox:
                            text "STATUTORY BASIS: Consumer Protection Act, 2019" size 20 color "#e5c07b" bold True
                            text "• Sec 2(10): Defect in goods.\n• Sec 2(11): Deficiency in service.\n• Sec 35: Manner in which complaint shall be made.\n• Sec 39: Findings of the District Commission (Refund, replacement, compensation)." size 17 color "#abb2bf"

screen verdict_report_modal(verdict_title, confidence_score, status_text, recommendation):
    modal True
    zorder 100
    
    add Solid("#000000bb")
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 1050
        ysize 680
        background Solid("#1b1f27fa")
        padding (35, 30)
        
        vbox:
            spacing 20
            
            text "📋 NYAYASIM COURT READINESS REPORT" size 32 color "#e5c07b" bold True xalign 0.5
            
            null height 5
            
            frame:
                xfill True
                background Solid("#242a35")
                padding (20, 16)
                vbox:
                    spacing 8
                    text "VERDICT / DISPOSITION: [verdict_title]" size 24 color "#50fa7b" bold True
                    text "Bench Consensus: [status_text]" size 19 color "#f8f8f2"
                    text "Readiness Score / Judicial Confidence: [confidence_score]%" size 20 color "#61afef" bold True
            
            frame:
                xfill True
                background Solid("#242a35")
                padding (20, 16)
                vbox:
                    spacing 8
                    text "3-JUDGE BENCH DELIBERATION BREAKDOWN" size 20 color "#d19a66" bold True
                    text "• Judge A (Textualist): Section 35(1) procedural conditions satisfied. Statutory standing verified." size 17 color "#abb2bf"
                    text "• Judge B (Welfare): Consumer experienced grave professional harassment. Full refund + compensation recommended." size 17 color "#abb2bf"
                    text "• Judge C (Proceduralist): Chain of custody from purchase invoice to technician defect job sheet is unbroken." size 17 color "#abb2bf"

            frame:
                xfill True
                background Solid("#242a35")
                padding (20, 16)
                vbox:
                    spacing 6
                    text "FINAL COMMISSION DIRECTIVE:" size 19 color "#e5c07b" bold True
                    text "[recommendation]" size 17 color "#f1fa8c"

            null height 10
            textbutton "Return to Main Docket":
                xalign 0.5
                text_size 24
                text_color "#ffffff"
                text_hover_color "#50fa7b"
                action [Hide("verdict_report_modal"), Return()]
