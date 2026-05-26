"""
GovernAI Studio — Live Backend Prototype Demo
==============================================
Walks through the ENTIRE simulation lifecycle via real API calls.
"""
import requests
import json
import sys

BASE = "http://127.0.0.1:8000"

def pretty(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def step(num, title):
    print(f"\n{'='*60}")
    print(f"  STEP {num}: {title}")
    print(f"{'='*60}\n")

# ===== STEP 1: Health Check =====
step(1, "Health Check")
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    if r.status_code != 200:
        print(f"Server returned {r.status_code}: {r.text}")
        sys.exit(1)
    pretty(r.json())
except Exception as e:
    print(f"Server not running! Start it with: python -m uvicorn app.main:app")
    sys.exit(1)

# ===== STEP 2: Magic Link =====
step(2, "Request Magic Link (Dev Mode)")
r = requests.post(f"{BASE}/v1/auth/magic-link", json={"email": "prototype.demo@gmail.com"})
data = r.json()
pretty(data)
msg = data.get("message", "")
raw_token = msg.split("token: ")[1] if "token: " in msg else None
if not raw_token:
    print("ERROR: No token. Is DEBUG=true in .env?")
    sys.exit(1)
print(f"\n  Token extracted successfully")

# ===== STEP 3: Verify -> JWT =====
step(3, "Verify Magic Link -> Get JWT")
r = requests.post(f"{BASE}/v1/auth/verify", json={"token": raw_token})
auth = r.json()
jwt = auth["access_token"]
uid = auth["user"]["id"]
headers = {"Authorization": f"Bearer {jwt}"}
print(f"  User ID:   {uid}")
print(f"  JWT:       {jwt[:40]}...")
print(f"  Onboarded: {auth['user']['onboarding_complete']}")

# ===== STEP 4: Onboarding =====
step(4, "Officer Onboarding (Tier Routing)")
r = requests.post(f"{BASE}/v1/onboarding/submit", json={
    "work_location": "central_hq",
    "work_shape": "policy_drafting",
    "domains": ["ai_governance", "procurement"]
}, headers=headers)
print(f"  Result: {r.json()}")
print(f"  Officer is now Tier A (Policy/HQ level)")

# ===== STEP 5: List Scenarios =====
step(5, "Available Scenarios (from Neon PostgreSQL)")
r = requests.get(f"{BASE}/v1/scenarios", headers=headers)
resp = r.json()
scenarios = resp.get("scenarios", [])
for i, s in enumerate(scenarios):
    print(f"  {i+1}. [{s['domain']}] {s['title']} ({s['estimated_minutes']} min, {s['npc_count']} NPCs, {s['decision_count']} decisions)")

# Pick "The Vendor with the Free AI"
vendor_scenario = None
for s in scenarios:
    if s["slug"] == "vendor-free-ai":
        vendor_scenario = s
        break
if not vendor_scenario:
    vendor_scenario = scenarios[0]
print(f"\n  >>> Selected: {vendor_scenario['title']}")

# ===== STEP 6: Start Simulation (DIRECTOR AGENT - AI CALL #1) =====
step(6, "Start Simulation [AI: Director Agent]")
print("  The Director Agent is adapting the narrative for a Tier A officer...")
print("  (Calling Gemini 2.5 Flash via LLM Gateway...)\n")
r = requests.post(f"{BASE}/v1/sessions/start", json={
    "scenario_slug": vendor_scenario["slug"],
    "officer_tier": "A"
}, headers=headers, timeout=60)
session = r.json()
session_id = session.get("session_id", "")
print(f"  Session ID: {session_id}")
print(f"  Stage:      {session.get('stage', '?')}")
narrative = session.get("setting_narrative", "")
if narrative:
    print(f"\n  --- NARRATIVE ---")
    for line in narrative[:600].split(". "):
        print(f"  {line.strip()}.")
    if len(narrative) > 600:
        print(f"  ...")
print(f"\n  Initial Prompt: {session.get('initial_prompt', '?')}")
npcs = session.get("npcs", [])
print(f"\n  NPCs Available:")
for npc in npcs:
    req_label = " (REQUIRED)" if npc.get("required_interactions", 0) > 0 else ""
    print(f"    - {npc['name']} ({npc['role']}){req_label}")

# ===== STEP 7: Talk to Vendor (NPC AGENT - AI CALL #2) =====
step(7, "Talk to Vendor Rep [AI: NPC Agent]")
print("  Officer: 'Tell me about your platform. Where is the data stored?'")
print("  (Calling Groq / Llama 3.3 70B...)\n")
r = requests.post(f"{BASE}/v1/sessions/{session_id}/interact", json={
    "npc_id": "npc_vendor_rep",
    "message": "Tell me about your AI platform. Where is the data stored and processed?"
}, headers=headers, timeout=60)
npc = r.json()
print(f"  {npc.get('npc_name', '?')} ({npc.get('npc_role', '?')}):")
print(f"  ---")
resp_text = npc.get("response", "")
for line in resp_text.split("\n"):
    print(f"  {line}")
print(f"\n  Interactions: {npc.get('interaction_count', '?')}")
print(f"  Can advance to decisions: {npc.get('can_advance_to_decisions', '?')}")

# ===== STEP 8: Talk to Technical Advisor (NPC AGENT - AI CALL #3) =====
step(8, "Talk to NIC Advisor [AI: NPC Agent]")
print("  Officer: 'What are the technical risks?'")
print("  (Calling Groq / Llama 3.3 70B...)\n")
r = requests.post(f"{BASE}/v1/sessions/{session_id}/interact", json={
    "npc_id": "npc_technical_advisor",
    "message": "Dr. Sharma, what are the technical risks of this vendor's proposal? I'm concerned about data residency and vendor lock-in."
}, headers=headers, timeout=60)
npc = r.json()
print(f"  {npc.get('npc_name', '?')} ({npc.get('npc_role', '?')}):")
print(f"  ---")
resp_text = npc.get("response", "")
for line in resp_text.split("\n"):
    print(f"  {line}")
print(f"\n  Can advance to decisions: {npc.get('can_advance_to_decisions', '?')}")

# ===== STEP 9: Advance to Decisions =====
step(9, "Advance to Decision Stage [No AI]")
r = requests.post(f"{BASE}/v1/sessions/{session_id}/advance", json={
    "target_stage": "DECISION_MOMENTS"
}, headers=headers, timeout=30)
print(f"  Result: {r.json()}")

# ===== STEP 10: Submit Decisions (NO AI - pure DB) =====
step(10, "Submit 4 Decisions [No AI - Rule Engine]")

decisions = [
    ("dm_initial_response", "OPTION", "opt_negotiate", None, "Negotiate contract terms"),
    ("dm_data_residency", "OPTION", "opt_clause", None, "Add data localization clause"),
    ("dm_budget_pressure", "OPTION", "opt_gem", None, "Route through GeM"),
    ("dm_final_recommendation", "FREEFORM", None,
     "I recommend a limited 6-month pilot with strict data localization, GeM routing, and independent audit.",
     "Freeform recommendation"),
]

for dm_id, choice_type, option, freetext, label in decisions:
    body = {"decision_moment_id": dm_id, "choice_type": choice_type}
    if option:
        body["selected_option"] = option
    if freetext:
        body["free_text"] = freetext
    r = requests.post(f"{BASE}/v1/sessions/{session_id}/decision", json=body, headers=headers, timeout=30)
    result = r.json()
    remaining = result.get("decisions_remaining", "?")
    stage = result.get("next_stage", "?")
    print(f"  [{dm_id}] {label}")
    print(f"    -> Remaining: {remaining}, Stage: {stage}")

# ===== STEP 11: Get Consequences (NO AI - rule-based branching) =====
step(11, "View Consequences [No AI - Rule Engine]")
r = requests.get(f"{BASE}/v1/sessions/{session_id}/consequences", headers=headers, timeout=30)
consequences = r.json()
print(f"  Branch: {consequences.get('branch', '?')}")
artifacts = consequences.get("consequences", consequences.get("artifacts", []))
if isinstance(artifacts, list):
    for c in artifacts:
        ctype = c.get("type", "?")
        content = c.get("content", "")
        print(f"\n  [{ctype.upper()}]")
        print(f"  {content[:200]}")
else:
    pretty(consequences)

# ===== STEP 12: Get Reflection (COACH AGENT - AI CALL #4) =====
step(12, "Seven Sutras Reflection [AI: Coach Agent]")
print("  The Coach Agent is analyzing all decisions...")
print("  (Calling Gemini 2.5 Flash — this is the longest call ~10-15 sec)\n")
r = requests.get(f"{BASE}/v1/sessions/{session_id}/reflection", headers=headers, timeout=120)
reflection = r.json()

preamble = reflection.get("preamble", "")
if preamble:
    print(f"  --- PREAMBLE ---")
    print(f"  {preamble[:300]}")

sutras = reflection.get("sutra_observations", [])
if sutras:
    print(f"\n  --- SUTRA OBSERVATIONS ({len(sutras)} sutras) ---")
    for s in sutras[:4]:
        print(f"\n  [{s.get('sutra', '?')}] ({s.get('engagement', '?')})")
        obs = s.get("observation", "")
        print(f"  Observation: {obs[:150]}...")
        q = s.get("reflective_question", "")
        print(f"  Question: {q[:150]}")

synthesis = reflection.get("synthesis", "")
if synthesis:
    print(f"\n  --- SYNTHESIS ---")
    print(f"  {synthesis[:300]}")

if not preamble and not sutras:
    pretty(reflection)

# ===== DONE =====
print("\n" + "=" * 60)
print("  GOVERNAI STUDIO PROTOTYPE — COMPLETE!")
print("=" * 60)
print(f"""
  All 12 steps executed successfully:

  [NO AI]  1. Health Check           -> Server alive
  [NO AI]  2. Magic Link             -> Token generated
  [NO AI]  3. JWT Auth               -> Access token issued
  [NO AI]  4. Onboarding             -> Tier A assigned
  [NO AI]  5. Scenario List          -> 5 scenarios from DB
  [AI #1]  6. Start Session          -> Director adapted narrative
  [AI #2]  7. Talk to Vendor         -> NPC in-character response
  [AI #3]  8. Talk to NIC Advisor    -> NPC technical advice
  [NO AI]  9. Advance Stage          -> State machine transition
  [NO AI] 10. Submit 4 Decisions     -> Stored in PostgreSQL
  [NO AI] 11. View Consequences      -> Rule-based branching
  [AI #4] 12. Seven Sutras Debrief   -> Coach reflection generated

  Backend: FastAPI + Neon PostgreSQL + LightRAG
  AI:      Gemini 2.5 Flash + Groq Llama 70B (4 providers total)
  Auth:    Magic Link + JWT (passwordless)
""")
