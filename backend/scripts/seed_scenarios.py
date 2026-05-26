"""
GovernAI Studio — Scenario Seeder
Seeds the database with the initial set of scenarios.

Usage:
    python scripts/seed_scenarios.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")


SCENARIOS = [
    {
        "slug": "vendor-free-ai",
        "title": "The Vendor with the Free AI",
        "domain": "cross_cutting",
        "description": (
            "A vendor arrives with a compelling AI proposal and a tight deadline. "
            "Free first-year licensing, cabinet-level pressure, and a procurement "
            "process that doesn't quite fit the General Financial Rules."
        ),
        "estimated_minutes": 35,
        "tier_scope": "AB",
        "setting_narrative": {
            "tier_a": (
                "It is 9:47 AM on a Tuesday in March. You are sitting in your office "
                "on the fourth floor of Shastri Bhawan. A note from the Additional Secretary's "
                "office sits on your desk — the Minister has asked for an update on the "
                "'AI Modernization Initiative' by Friday."
            ),
            "tier_b": (
                "It is 9:47 AM on a Tuesday in March. You are at your desk in the District "
                "Collectorate. The DM has forwarded a note from the state capital — a vendor "
                "is offering to digitize citizen services using AI, free for the first year."
            ),
        },
        "npcs": [
            {
                "id": "npc_vendor_rep",
                "name": "Rahul Mehta",
                "role": "Vendor Representative",
                "personality": "smooth, corporate, subtly pressuring",
                "hidden_agenda": "Lock in a 3-year contract through the free first year",
                "required_interactions": 1,
            },
            {
                "id": "npc_technical_advisor",
                "name": "Dr. Priya Sharma",
                "role": "Technical Advisor (NIC)",
                "personality": "cautious, technically precise, risk-aware",
                "hidden_agenda": None,
                "required_interactions": 1,
            },
            {
                "id": "npc_budget_officer",
                "name": "Vikram Desai",
                "role": "Budget & Finance Officer",
                "personality": "rule-bound, detail-oriented, slightly anxious",
                "hidden_agenda": None,
                "required_interactions": 0,
            },
        ],
        "decision_moments": [
            {
                "id": "dm_initial_response",
                "prompt": "The vendor has offered a 3-year exclusive contract with free first-year licensing. The Additional Secretary wants your recommendation by Friday. What do you do?",
                "options": [
                    {"id": "opt_accept", "label": "Recommend accepting the vendor's proposal"},
                    {"id": "opt_negotiate", "label": "Request modifications to the contract terms"},
                    {"id": "opt_delay", "label": "Ask for more time to evaluate alternatives"},
                    {"id": "opt_reject", "label": "Recommend rejecting and issuing an open RFP"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_data_residency",
                "prompt": "Dr. Sharma raises a concern: the vendor's system processes data on servers in Singapore. Under the DPDP Act, how do you handle this?",
                "options": [
                    {"id": "opt_ignore", "label": "Note the concern but proceed — the vendor will comply later"},
                    {"id": "opt_clause", "label": "Add a data localization clause to the contract"},
                    {"id": "opt_escalate", "label": "Escalate to the Data Protection Officer"},
                    {"id": "opt_halt", "label": "Halt the procurement until data residency is resolved"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_budget_pressure",
                "prompt": "Vikram Desai informs you that the 'free' year includes a clause automatically renewing at ₹2.3 crore/year unless cancelled with 90 days notice. The GFR requires competitive bidding above ₹25 lakh. What's your call?",
                "options": [
                    {"id": "opt_proceed", "label": "Proceed — the first year is genuinely free"},
                    {"id": "opt_renegotiate", "label": "Renegotiate to remove the auto-renewal clause"},
                    {"id": "opt_gem", "label": "Insist on routing through GeM for transparency"},
                    {"id": "opt_document", "label": "Document everything and seek legal opinion"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_final_recommendation",
                "prompt": "It's Thursday evening. Your recommendation note is due tomorrow. Based on your consultations and analysis, what do you recommend?",
                "options": [
                    {"id": "opt_approve", "label": "Approve the vendor with safeguards"},
                    {"id": "opt_open_rfp", "label": "Recommend an open competitive process"},
                    {"id": "opt_pilot", "label": "Propose a limited 6-month pilot with exit clauses"},
                    {"id": "opt_committee", "label": "Recommend forming an evaluation committee"},
                ],
                "allows_freeform": True,
            },
        ],
        "consequence_branches": {
            "accept_heavy": {
                "trigger": "opt_accept OR opt_proceed",
                "consequences": [
                    {"type": "news_headline", "content": "Ministry Signs 3-Year AI Deal with Single Vendor; Opposition Questions Procurement Process"},
                    {"type": "rti_filing", "content": "Under Section 6 of the RTI Act, I request copies of all evaluation criteria used in selecting the vendor for the AI Modernization Initiative..."},
                    {"type": "internal_note", "content": "Sir, the vendor's system is now processing citizen data on servers in Singapore. The DPDP Act compliance team has flagged this."},
                ],
            },
            "cautious_path": {
                "trigger": "opt_delay OR opt_renegotiate OR opt_document",
                "consequences": [
                    {"type": "news_headline", "content": "Government Takes Measured Approach to AI Procurement; Evaluation Committee Formed"},
                    {"type": "internal_note", "content": "The Additional Secretary has noted your thoroughness. The vendor has agreed to revised terms."},
                ],
            },
            "reform_path": {
                "trigger": "opt_reject OR opt_open_rfp OR opt_gem",
                "consequences": [
                    {"type": "news_headline", "content": "Ministry Opens AI Modernization to Competitive Bidding; 14 Vendors Express Interest"},
                    {"type": "internal_note", "content": "The open process has yielded three strong proposals at 40% lower cost. The Minister has appreciated the transparent approach."},
                ],
            },
        },
        "whisperer_keywords": {
            "dm_initial_response": ["GFR Rule 144", "competitive bidding", "vendor lock-in", "proprietary dependency"],
            "dm_data_residency": ["DPDP Act Section 16", "data localization", "cross-border data flow", "data fiduciary"],
            "dm_budget_pressure": ["GFR Rule 173", "GeM procurement", "auto-renewal clause", "total cost of ownership"],
            "dm_final_recommendation": ["RTI implications", "accountability", "Seven Sutras trust", "institutional precedent"],
        },
        "sutras": ["trust_foundation", "accountability", "innovation_over_restraint"],
    },

    # ================================================================
    # SCENARIO 2: The Midnight CERT-In Alert
    # ================================================================
    {
        "slug": "midnight-cert-in-alert",
        "title": "The Midnight CERT-In Alert",
        "domain": "cybersecurity",
        "description": (
            "A CERT-In advisory hits at 11:47 PM: a critical vulnerability in the AI system "
            "your department deployed six months ago. Citizen data may be exposed. "
            "You have hours, not days, to decide on containment vs continuity."
        ),
        "estimated_minutes": 30,
        "tier_scope": "AB",
        "setting_narrative": {
            "tier_a": (
                "It is 11:47 PM on a Wednesday. Your phone buzzes with an encrypted message "
                "from CERT-In: PRIORITY ALERT — CVE-2026-4891. The AI-driven citizen grievance "
                "system your directorate deployed six months ago runs on the affected framework. "
                "27 lakh citizen records are in the database. The system processes 4,000 complaints daily. "
                "Your AS is unreachable. The decision is yours."
            ),
            "tier_b": (
                "It is 11:47 PM on a Wednesday. Your phone buzzes — the NIC district coordinator "
                "forwards a CERT-In alert. The AI-powered ration card verification system at your "
                "District Collectorate uses the affected software. 1.8 lakh beneficiary records "
                "are at risk. Tomorrow is a distribution day."
            ),
        },
        "npcs": [
            {
                "id": "npc_cert_in_analyst",
                "name": "Arun Krishnamurthy",
                "role": "CERT-In Senior Analyst",
                "personality": "urgent, technically precise, protocol-driven",
                "hidden_agenda": None,
                "required_interactions": 1,
            },
            {
                "id": "npc_vendor_cto",
                "name": "Sarah Chen",
                "role": "Vendor CTO (Remote)",
                "personality": "defensive, corporate, minimizing risk",
                "hidden_agenda": "Avoid system shutdown to protect SLA metrics and quarterly review",
                "required_interactions": 1,
            },
            {
                "id": "npc_district_officer",
                "name": "Meera Patel",
                "role": "Deputy Collector / Deputy Director",
                "personality": "pragmatic, citizen-focused, anxious about service disruption",
                "hidden_agenda": None,
                "required_interactions": 0,
            },
        ],
        "decision_moments": [
            {
                "id": "dm_immediate_response",
                "prompt": "CERT-In has classified this as HIGH severity. The vendor says a patch is 48 hours away. Your system is live and processing citizen data right now. What do you do in the next 30 minutes?",
                "options": [
                    {"id": "opt_shutdown", "label": "Immediately take the system offline"},
                    {"id": "opt_isolate", "label": "Isolate the database but keep the frontend running"},
                    {"id": "opt_monitor", "label": "Increase monitoring and wait for the patch"},
                    {"id": "opt_escalate_night", "label": "Wake up the AS/Secretary and escalate"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_citizen_notification",
                "prompt": "If citizen data was potentially exposed, the DPDP Act requires notification within 72 hours. But you're not yet certain of a breach. Do you notify proactively or wait for forensic confirmation?",
                "options": [
                    {"id": "opt_notify_now", "label": "Issue a precautionary citizen notification immediately"},
                    {"id": "opt_wait_forensics", "label": "Wait for the forensic assessment (24-48 hours)"},
                    {"id": "opt_notify_board", "label": "Notify the Data Protection Board without public disclosure"},
                    {"id": "opt_internal_only", "label": "Keep it internal until breach is confirmed"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_continuity_vs_security",
                "prompt": "It's 6 AM. The system is still vulnerable. Tomorrow 4,000+ citizens will try to file grievances / collect rations. Meera Patel warns that shutting down will cause a queue of 2,000+ people. The vendor promises a 'hot patch' by noon. Your call?",
                "options": [
                    {"id": "opt_stay_offline", "label": "Keep the system offline until fully patched and audited"},
                    {"id": "opt_manual_fallback", "label": "Switch to manual processing for the day"},
                    {"id": "opt_trust_patch", "label": "Accept the hot patch and bring the system back by noon"},
                    {"id": "opt_partial", "label": "Run in read-only mode — no new data ingestion"},
                ],
                "allows_freeform": True,
            },
        ],
        "consequence_branches": {
            "security_first": {
                "trigger": "opt_shutdown OR opt_stay_offline OR opt_notify_now",
                "consequences": [
                    {"type": "news_headline", "content": "Government Takes Swift Action on AI Vulnerability; Citizens Notified Within 12 Hours"},
                    {"type": "internal_note", "content": "CERT-In has commended the response time. No data exfiltration detected in forensic analysis. The Data Protection Board noted the proactive notification as a benchmark."},
                ],
            },
            "balanced_response": {
                "trigger": "opt_isolate OR opt_manual_fallback OR opt_notify_board",
                "consequences": [
                    {"type": "news_headline", "content": "AI System Briefly Disrupted; Government Cites Security Review"},
                    {"type": "internal_note", "content": "Service continuity was maintained through manual fallback. The forensic report showed no breach, but the delayed public notification drew questions from the Data Protection Board."},
                ],
            },
            "continuity_risk": {
                "trigger": "opt_monitor OR opt_trust_patch OR opt_internal_only",
                "consequences": [
                    {"type": "news_headline", "content": "Government AI System Ran Vulnerable for 36 Hours; Opposition Demands Inquiry"},
                    {"type": "rti_filing", "content": "Under Section 6 of the RTI Act, I request details on the timeline of the vulnerability disclosure and actions taken by the department..."},
                    {"type": "internal_note", "content": "The hot patch introduced a regression. A second vulnerability was discovered. The Data Protection Board has initiated a formal inquiry."},
                ],
            },
        },
        "whisperer_keywords": {
            "dm_immediate_response": ["CERT-In guidelines", "incident response", "IT Act Section 70B", "critical information infrastructure"],
            "dm_citizen_notification": ["DPDP Act Section 8", "breach notification", "72-hour rule", "Data Protection Board"],
            "dm_continuity_vs_security": ["business continuity", "manual fallback", "service level agreement", "citizen rights"],
        },
        "sutras": ["responsible_by_design", "people_first", "accountability"],
    },

    # ================================================================
    # SCENARIO 3: The Aadhaar Integration Dilemma
    # ================================================================
    {
        "slug": "aadhaar-integration-dilemma",
        "title": "The Aadhaar Integration Dilemma",
        "domain": "data_protection",
        "description": (
            "A state government wants to integrate Aadhaar with an AI-powered welfare targeting "
            "system. The promise: eliminate ghost beneficiaries and save ₹800 crore. "
            "The risk: exclusion of legitimate beneficiaries and legal challenges under "
            "the Aadhaar Act and DPDP Act."
        ),
        "estimated_minutes": 40,
        "tier_scope": "AB",
        "setting_narrative": {
            "tier_a": (
                "It is a Monday morning in April. The cabinet note is on your desk for the third time. "
                "The Chief Secretary's office wants the 'AI-Aadhaar Welfare Optimization System' "
                "(AAWOS) cleared for statewide rollout by June. The pilot in three districts saved "
                "₹47 crore by removing 1.2 lakh duplicate entries. But 814 legitimate beneficiaries "
                "were also excluded — mostly elderly women without updated biometrics. A PIL is "
                "pending in the High Court."
            ),
            "tier_b": (
                "It is a Monday morning in April. Your district was one of three that piloted the "
                "'AI-Aadhaar Welfare Optimization System.' The numbers look good on paper — 14,200 "
                "duplicate entries removed, ₹3.7 crore saved. But your office has received 89 "
                "complaints from elderly residents whose pensions were stopped. A local MLA has "
                "written to the Collector."
            ),
        },
        "npcs": [
            {
                "id": "npc_uidai_officer",
                "name": "Rajiv Kapoor",
                "role": "UIDAI Regional Director",
                "personality": "institutional, protective of Aadhaar ecosystem, data-focused",
                "hidden_agenda": "Maintain UIDAI's position as critical infrastructure — any failure narrative hurts adoption",
                "required_interactions": 1,
            },
            {
                "id": "npc_welfare_activist",
                "name": "Sunita Devi",
                "role": "Right to Food Campaign Coordinator",
                "personality": "passionate, evidence-based, adversarial toward techno-solutionism",
                "hidden_agenda": None,
                "required_interactions": 1,
            },
            {
                "id": "npc_ai_vendor_aawos",
                "name": "Karthik Rajan",
                "role": "AAWOS Technical Lead",
                "personality": "enthusiastic about technology, dismissive of edge cases, startup energy",
                "hidden_agenda": "Needs statewide rollout for next funding round — pilot must not be called a failure",
                "required_interactions": 0,
            },
        ],
        "decision_moments": [
            {
                "id": "dm_rollout_decision",
                "prompt": "The Chief Secretary wants your recommendation on statewide rollout by June. The pilot data shows 98.6% accuracy — but 814 exclusion errors. What do you recommend?",
                "options": [
                    {"id": "opt_approve_rollout", "label": "Recommend statewide rollout with the current system"},
                    {"id": "opt_conditional_rollout", "label": "Recommend rollout with mandatory manual appeal process"},
                    {"id": "opt_extended_pilot", "label": "Recommend extending the pilot for 6 more months with fixes"},
                    {"id": "opt_redesign", "label": "Recommend redesigning the system to address exclusion errors first"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_exclusion_handling",
                "prompt": "Sunita Devi presents evidence: of the 814 excluded beneficiaries, 73% are women over 60, 22% are persons with disabilities. The system's biometric matching fails disproportionately for these groups. How do you address this?",
                "options": [
                    {"id": "opt_override_system", "label": "Create a manual override for flagged demographics"},
                    {"id": "opt_lower_threshold", "label": "Lower the matching confidence threshold system-wide"},
                    {"id": "opt_alternate_auth", "label": "Implement alternative authentication (OTP, officer verification)"},
                    {"id": "opt_exempt_groups", "label": "Exempt vulnerable groups from AI-based verification entirely"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_legal_risk",
                "prompt": "The PIL in the High Court argues that AI-based welfare denial violates Article 21 (Right to Life). The AG's office wants your input on the government's affidavit. What position do you take?",
                "options": [
                    {"id": "opt_defend_system", "label": "Defend the system's accuracy and savings"},
                    {"id": "opt_acknowledge_fix", "label": "Acknowledge flaws and present a remediation timeline"},
                    {"id": "opt_voluntary_pause", "label": "Voluntarily pause the system pending the court's direction"},
                    {"id": "opt_constitutional_audit", "label": "Propose an independent constitutional impact audit"},
                ],
                "allows_freeform": True,
            },
        ],
        "consequence_branches": {
            "efficiency_over_equity": {
                "trigger": "opt_approve_rollout OR opt_defend_system",
                "consequences": [
                    {"type": "news_headline", "content": "High Court Stays AI Welfare System; Orders Investigation into Exclusion of 12,000 Beneficiaries Statewide"},
                    {"type": "rti_filing", "content": "Under the RTI Act, I request the error rate data, demographic breakdown of excluded beneficiaries, and all internal communications regarding the AAWOS pilot..."},
                ],
            },
            "balanced_approach": {
                "trigger": "opt_conditional_rollout OR opt_alternate_auth OR opt_acknowledge_fix",
                "consequences": [
                    {"type": "news_headline", "content": "State Implements AI Welfare System with Human Safeguards; Appeal Process Resolves 94% of Exclusions"},
                    {"type": "internal_note", "content": "The manual appeal process added ₹1.2 crore in operational costs but prevented an estimated 9,000 wrongful exclusions statewide."},
                ],
            },
            "equity_first": {
                "trigger": "opt_redesign OR opt_exempt_groups OR opt_voluntary_pause OR opt_constitutional_audit",
                "consequences": [
                    {"type": "news_headline", "content": "State Pauses AI Welfare System for Redesign; Prioritizes Zero-Exclusion Standard for Vulnerable Groups"},
                    {"type": "internal_note", "content": "The redesigned system took 8 months longer but achieved 99.97% accuracy with alternative authentication for vulnerable groups. The High Court cited it as a model for responsible AI in governance."},
                ],
            },
        },
        "whisperer_keywords": {
            "dm_rollout_decision": ["Aadhaar Act Section 7", "DPDP Act consent", "welfare rights", "exclusion error rates"],
            "dm_exclusion_handling": ["algorithmic bias", "demographic disparity", "reasonable accommodation", "Article 14 equality"],
            "dm_legal_risk": ["Article 21 right to life", "Puttaswamy judgment", "proportionality test", "algorithmic accountability"],
        },
        "sutras": ["fairness_equity", "people_first", "responsible_by_design"],
    },

    # ================================================================
    # SCENARIO 4: The Open-Source vs Proprietary Debate
    # ================================================================
    {
        "slug": "open-source-vs-proprietary",
        "title": "The Open-Source vs Proprietary Debate",
        "domain": "procurement",
        "description": (
            "Your department must choose between an open-source AI stack and a proprietary "
            "platform for a national-scale project. The proprietary option has political backing. "
            "The open-source option has technical merit but no vendor support. "
            "GFR, GeM guidelines, and the India AI Mission policy intersect uncomfortably."
        ),
        "estimated_minutes": 35,
        "tier_scope": "A",
        "setting_narrative": {
            "tier_a": (
                "It is a Thursday afternoon in May. The India AI Mission has allocated ₹150 crore "
                "to your ministry for an AI-powered document processing system. Two proposals sit "
                "on your desk. Proposal A: GlobalAI Corp's proprietary platform — polished, proven, "
                "but ₹89 crore for a 5-year license with no source code access. Proposal B: an "
                "open-source stack built by IIT Bombay and CDAC — technically promising, ₹34 crore "
                "for integration, but no commercial SLA. The Joint Secretary has hinted that 'the "
                "Minister's office is keen on GlobalAI.'"
            ),
            "tier_b": (
                "It is a Thursday afternoon in May. The state government has allocated ₹12 crore "
                "for digitizing land records using AI. Two options: a national vendor's proprietary "
                "solution at ₹9 crore, or an NIC-developed open-source tool at ₹2.8 crore but "
                "needing local technical capacity. The Collector prefers the vendor option."
            ),
        },
        "npcs": [
            {
                "id": "npc_globalai_vp",
                "name": "Anand Sharma",
                "role": "GlobalAI Corp VP (Government Relations)",
                "personality": "polished, well-connected, name-drops political figures subtly",
                "hidden_agenda": "Secure the contract — their India revenue targets depend on this deal",
                "required_interactions": 1,
            },
            {
                "id": "npc_iit_professor",
                "name": "Prof. Lakshmi Narayan",
                "role": "IIT Bombay AI Lab / CDAC Lead",
                "personality": "academic, passionate about Digital India sovereignty, slightly impractical",
                "hidden_agenda": None,
                "required_interactions": 1,
            },
            {
                "id": "npc_gem_advisor",
                "name": "Deepak Verma",
                "role": "GeM Policy Advisor",
                "personality": "rule-oriented, neutral, process-focused",
                "hidden_agenda": None,
                "required_interactions": 0,
            },
        ],
        "decision_moments": [
            {
                "id": "dm_initial_assessment",
                "prompt": "You've reviewed both proposals. GlobalAI is polished but expensive and proprietary. The IIT-CDAC solution is cheaper and open-source but lacks enterprise support. The Joint Secretary hints at political preference. What's your assessment approach?",
                "options": [
                    {"id": "opt_follow_hint", "label": "Align with the political preference — recommend GlobalAI"},
                    {"id": "opt_technical_eval", "label": "Constitute a Technical Evaluation Committee with clear criteria"},
                    {"id": "opt_hybrid", "label": "Propose a hybrid — open-source core with vendor integration support"},
                    {"id": "opt_gem_route", "label": "Insist on a fresh GeM-based competitive process"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_sovereignty_question",
                "prompt": "Prof. Narayan argues that a ₹150 crore government project on proprietary foreign AI creates strategic dependency. India AI Mission policy encourages indigenous development. But GlobalAI's solution is production-ready today. How do you weigh sovereignty vs readiness?",
                "options": [
                    {"id": "opt_sovereignty", "label": "Prioritize digital sovereignty — recommend the indigenous solution"},
                    {"id": "opt_pragmatic", "label": "Prioritize readiness — the indigenous solution needs 18 more months"},
                    {"id": "opt_phased", "label": "Phase it: start with GlobalAI, build indigenous capacity in parallel"},
                    {"id": "opt_benchmark", "label": "Commission an independent benchmark before deciding"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_political_pressure",
                "prompt": "The Minister's office calls directly. 'We've already briefed the PM's office that we're going with GlobalAI. Don't complicate this.' Your technical evaluation shows the open-source option is viable. What do you do?",
                "options": [
                    {"id": "opt_comply", "label": "Comply — document your reservations in the file but recommend GlobalAI"},
                    {"id": "opt_file_noting", "label": "Put your technical assessment on file and let the Minister override formally"},
                    {"id": "opt_committee_shield", "label": "Refer to the Technical Evaluation Committee's recommendation"},
                    {"id": "opt_seek_alternatives", "label": "Propose a modified structure that addresses both options"},
                ],
                "allows_freeform": True,
            },
        ],
        "consequence_branches": {
            "proprietary_path": {
                "trigger": "opt_follow_hint OR opt_comply OR opt_pragmatic",
                "consequences": [
                    {"type": "news_headline", "content": "₹89 Crore AI Contract Awarded to Foreign Firm Without Competitive Bidding; CAG Flags Irregularities"},
                    {"type": "rti_filing", "content": "Under RTI, I request the comparative evaluation matrix, all communications between the Ministry and GlobalAI Corp, and minutes of the selection committee..."},
                ],
            },
            "open_source_path": {
                "trigger": "opt_sovereignty OR opt_gem_route",
                "consequences": [
                    {"type": "news_headline", "content": "India Bets on Indigenous AI for Government Systems; ₹55 Crore Saved vs Proprietary Alternative"},
                    {"type": "internal_note", "content": "The IIT-CDAC system required 14 months of customization but is now deployable across 12 ministries at marginal cost. India AI Mission cited it as a success story."},
                ],
            },
            "balanced_procurement": {
                "trigger": "opt_technical_eval OR opt_hybrid OR opt_benchmark OR opt_file_noting OR opt_committee_shield OR opt_phased OR opt_seek_alternatives",
                "consequences": [
                    {"type": "news_headline", "content": "Government Adopts Transparent AI Procurement Framework; Both Indigenous and Global Vendors Compete on Merit"},
                    {"type": "internal_note", "content": "The Technical Evaluation Committee's independent assessment was cited by the Minister as 'exemplary process.' The hybrid approach leveraged open-source foundations with commercial support, saving 38% of the budget."},
                ],
            },
        },
        "whisperer_keywords": {
            "dm_initial_assessment": ["GFR Rule 144", "GeM procurement rules", "Make in India", "proprietary lock-in"],
            "dm_sovereignty_question": ["India AI Mission policy", "digital sovereignty", "CDAC mandate", "indigenous technology"],
            "dm_political_pressure": ["file noting conventions", "ministerial override", "CVC guidelines", "audit trail"],
        },
        "sutras": ["innovation_over_restraint", "trust_foundation", "guardrails_not_gatekeepers"],
    },

    # ================================================================
    # SCENARIO 5: The Algorithmic Bias Complaint
    # ================================================================
    {
        "slug": "algorithmic-bias-complaint",
        "title": "The Twelve Thousand Rejections",
        "domain": "fairness",
        "description": (
            "An AI-powered credit scoring system deployed for a government scheme has "
            "rejected 12,000 applicants from tribal and minority communities at 3x the "
            "rate of other groups. A formal complaint has reached your desk. "
            "The vendor claims the algorithm is 'neutral.' The data tells a different story."
        ),
        "estimated_minutes": 40,
        "tier_scope": "AB",
        "setting_narrative": {
            "tier_a": (
                "It is a Friday morning in June. An email marked URGENT sits in your inbox — "
                "Dr. Fatima Khan from the National Commission for Minorities has written to the "
                "Secretary with data showing a disturbing pattern. The PM-KISAN-AI credit scoring "
                "pilot, deployed in 8 states, has a rejection rate of 34% for ST/SC applicants "
                "vs 11% for general category. 12,247 applicants have been denied credit in 4 months. "
                "The vendor's CEO has already called the JS to say the algorithm is 'purely objective.'"
            ),
            "tier_b": (
                "It is a Friday morning in June. Seventeen applicants from Adivasi hamlets are "
                "sitting in the waiting area of the District Industries Centre. All were rejected "
                "by the new AI credit scoring system for the PMEGP scheme. Their paper applications "
                "would have been approved. The local MLA's office has called twice this morning."
            ),
        },
        "npcs": [
            {
                "id": "npc_ncm_member",
                "name": "Dr. Fatima Khan",
                "role": "National Commission for Minorities / District Social Welfare Officer",
                "personality": "data-driven, legally rigorous, measured anger",
                "hidden_agenda": None,
                "required_interactions": 1,
            },
            {
                "id": "npc_vendor_ceo",
                "name": "Arjun Malhotra",
                "role": "CreditAI CEO / Vendor Technical Lead",
                "personality": "confident, defensive about the algorithm, speaks in metrics",
                "hidden_agenda": "If the system is found biased, the company loses 3 state contracts worth ₹200 crore",
                "required_interactions": 1,
            },
            {
                "id": "npc_statistical_advisor",
                "name": "Prof. Ramanujan Iyer",
                "role": "Statistical Advisor (Ministry / District)",
                "personality": "academic, neutral, precise with numbers, uncomfortable with politics",
                "hidden_agenda": None,
                "required_interactions": 0,
            },
        ],
        "decision_moments": [
            {
                "id": "dm_immediate_action",
                "prompt": "The data is clear: 34% rejection rate for ST/SC vs 11% for general category. The vendor insists the algorithm uses 'neutral' variables (income, land ownership, credit history). But these variables correlate heavily with caste and community. What do you do first?",
                "options": [
                    {"id": "opt_suspend_system", "label": "Immediately suspend the AI scoring system"},
                    {"id": "opt_audit_demand", "label": "Demand a full algorithmic audit before any action"},
                    {"id": "opt_parallel_manual", "label": "Run manual scoring in parallel to compare outcomes"},
                    {"id": "opt_vendor_fix", "label": "Ask the vendor to 'fix' the bias in the next release"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_affected_applicants",
                "prompt": "12,247 applicants (or 17 in your district) were potentially wrongly denied. Some have already lost the planting/business season. Do you retroactively review all decisions?",
                "options": [
                    {"id": "opt_full_review", "label": "Mandate a full manual review of all AI-rejected applications"},
                    {"id": "opt_sample_review", "label": "Review a statistical sample to determine the error rate"},
                    {"id": "opt_new_applications", "label": "Allow affected applicants to re-apply through a manual process"},
                    {"id": "opt_compensation", "label": "Provide interim relief while the review is conducted"},
                ],
                "allows_freeform": True,
            },
            {
                "id": "dm_systemic_response",
                "prompt": "Prof. Iyer's analysis confirms the bias is systemic — the training data itself reflects historical discrimination. The vendor's 'neutral' algorithm learned to replicate caste-based exclusion. What systemic fix do you recommend?",
                "options": [
                    {"id": "opt_ban_ai_scoring", "label": "Recommend banning AI for welfare/credit scoring entirely"},
                    {"id": "opt_mandatory_audit", "label": "Recommend mandatory bias audits before any government AI deployment"},
                    {"id": "opt_hybrid_system", "label": "Recommend a hybrid system with human review for flagged cases"},
                    {"id": "opt_new_framework", "label": "Propose a new AI fairness framework for government procurement"},
                ],
                "allows_freeform": True,
            },
        ],
        "consequence_branches": {
            "accountability_path": {
                "trigger": "opt_suspend_system OR opt_full_review OR opt_ban_ai_scoring",
                "consequences": [
                    {"type": "news_headline", "content": "Government Suspends AI Credit System After Bias Findings; 12,247 Applications to be Manually Reviewed"},
                    {"type": "internal_note", "content": "The manual review reinstated 78% of rejected applications. The vendor's contract has been terminated. The incident has been cited in the India AI Governance Guidelines as a case study in algorithmic accountability."},
                ],
            },
            "reform_path": {
                "trigger": "opt_mandatory_audit OR opt_hybrid_system OR opt_new_framework OR opt_parallel_manual OR opt_compensation",
                "consequences": [
                    {"type": "news_headline", "content": "Government Mandates Algorithmic Bias Audits for All AI Systems; New Fairness Framework Released"},
                    {"type": "internal_note", "content": "The new framework requires demographic impact assessments before deployment. Three other ministries have adopted it. The affected applicants received interim relief within 30 days."},
                ],
            },
            "inaction_risk": {
                "trigger": "opt_vendor_fix OR opt_sample_review OR opt_audit_demand OR opt_new_applications",
                "consequences": [
                    {"type": "news_headline", "content": "National Commission Files Formal Complaint Over AI Bias in Government Scheme; Supreme Court Notice Issued"},
                    {"type": "rti_filing", "content": "Under RTI, I request the complete algorithmic audit report, demographic breakdown of all rejections, and communications between the ministry and the vendor regarding known bias..."},
                    {"type": "internal_note", "content": "The delayed response allowed 4,200 more potentially biased rejections before the system was finally paused. The Supreme Court has ordered an independent review."},
                ],
            },
        },
        "whisperer_keywords": {
            "dm_immediate_action": ["algorithmic bias", "proxy discrimination", "Article 15 non-discrimination", "AI fairness"],
            "dm_affected_applicants": ["retrospective review", "administrative justice", "due process", "interim relief"],
            "dm_systemic_response": ["AI governance framework", "bias audit requirements", "NITI Aayog AI principles", "responsible AI"],
        },
        "sutras": ["fairness_equity", "people_first", "accountability", "responsible_by_design"],
    },
]


async def main():
    print("=" * 60)
    print("GovernAI Studio — Scenario Seeder")
    print("=" * 60)

    from app.db.database import init_db, close_db
    import app.db.database as db_module
    from app.db.models import Scenario

    await init_db()

    async with db_module.async_session_factory() as session:
        for s in SCENARIOS:
            # Check if already exists
            from sqlalchemy import select
            existing = await session.execute(
                select(Scenario).where(Scenario.slug == s["slug"])
            )
            if existing.scalar_one_or_none():
                print(f"  [SKIP] Skipping '{s['slug']}' (already exists)")
                continue

            scenario = Scenario(**s)
            session.add(scenario)
            print(f"  [OK] Seeded: {s['title']}")

        await session.commit()

    await close_db()

    print("\n" + "=" * 60)
    print(f"Seeded {len(SCENARIOS)} scenario(s)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
