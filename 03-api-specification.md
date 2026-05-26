# GovernAI Studio — API Specification (Zero-Cost Stack)
## v2.0 · May 2026

> Base URL: `https://governai-api.onrender.com/v1` (free Render subdomain)
> All endpoints require `Authorization: Bearer <jwt>` unless marked PUBLIC.

---

## 1. Authentication

### `POST /auth/magic-link` — PUBLIC
```
Request:  { "email": "officer@gov.in" }
Response: { "message": "Magic link sent", "expires_in": 900 }
```
Rate limit: 3/min per email. Only `*.gov.in` and whitelisted domains. Uses Resend free (100 emails/day).

### `POST /auth/verify` — PUBLIC
```
Request:  { "token": "<32_byte_token>" }
Response: { "access_token": "jwt...", "refresh_token": "jwt...", "expires_in": 900,
            "user": { "id": "uuid", "onboarding_complete": false } }
```

### `POST /auth/refresh`
```
Request:  { "refresh_token": "..." }
Response: { "access_token": "...", "expires_in": 900 }
```

---

## 2. Onboarding

### `GET /onboarding/questions`
Returns the 2 mandatory + 1 optional question with options. Static response, cached.

### `POST /onboarding/submit`
```
Request:  { "work_location": "central_hq", "work_shape": "drafting_reviewing", 
            "domains": ["procurement"] }
Response: { "onboarding_complete": true }
```
**Tier logic (server-side, never exposed):**
- **Tier A:** location ∈ {central_hq, state_secretariat} AND shape ∈ {drafting_reviewing, running_programmes}
- **Tier B:** location = district_field OR shape = field_implementation
- **Edge:** psu_regulatory + drafting → A; psu_regulatory + field → B; other → B

---

## 3. Scenarios

### `GET /scenarios`
```
Query:    ?domain=healthcare&page=1&limit=12
Response: { "scenarios": [{ "id": "uuid", "slug": "vendor-free-ai", "title": "...", 
            "domain": "cross_cutting", "estimated_minutes": 35, "is_recommended": true,
            "tags": {...} }], "total": 12 }
```
Backend auto-filters by officer's tier. `is_recommended` based on domain interests.

### `GET /scenarios/{id}` — Scenario metadata (no full content until session starts).

---

## 4. Sessions

### `POST /sessions/start`
```
Request:  { "scenario_id": "uuid" }
Response: { "session_id": "uuid", "state": "SETTING",
            "setting": { "narrative": "It is 9:47 AM on a Tuesday...", 
                         "stage_instructions": "..." } }
```

### `GET /sessions` — List officer's own sessions. `?state=COMPLETED&page=1`

### `GET /sessions/{id}` — Full session state for resume.

### `POST /sessions/{id}/interact` — NPC Dialogue (SSE Streaming)
```
Request:  { "npc_id": "uuid", "message": "What data residency guarantees..." }
Response: Server-Sent Events stream:
  event: token
  data: {"content": "Excellent question...", "done": false}
  
  event: token  
  data: {"content": "", "done": true, "message_id": "uuid"}
```

### `POST /sessions/{id}/decision`
```
Request:  { "decision_moment_id": "uuid", "choice_type": "OPTION", 
            "selected_option": "opt_b" }
Response: { "accepted": true, "next_state": "DECISION_MOMENTS", 
            "current_decision_index": 2 }
```

### `GET /sessions/{id}/reference` — Reference Whisperer
```
Query:    ?decision_moment_id=uuid
Response: { "references": [
              { "clause_text": "Rule 144 of GFR 2017...", "source": "GFR 2017",
                "section": "Rule 144", "relevance_score": 0.94 }
            ], "disclaimer": "Contextual suggestions, not legal advice." }
```
Latency target: < 2s. ChromaDB query + optional Gemini rerank.

### `POST /sessions/{id}/draft`
```
Request:  { "decision_moment_id": "uuid", "draft_text": "Para-wise comments..." }
Response: { "critique": {
              "legal_soundness": "...", "ethical_risk": "...",
              "citizen_impact": "...", "political_optics": "...",
              "drafting_convention": "..." } }
```

### `GET /sessions/{id}/consequences`
```
Response: { "consequences": [
              { "type": "news_headline", "content": "Ministry signs 3-year AI deal..." },
              { "type": "rti_filing", "content": "Under Section 6, I request..." }
            ], "narrative": "Three months later..." }
```

### `GET /sessions/{id}/reflection`
```
Response: { "reflection": {
              "preamble": "You navigated a complex procurement decision...",
              "sutra_observations": [
                { "sutra": "Trust is the Foundation",
                  "observation": "Your decision to request documentation...",
                  "reflective_question": "How might the vendor have responded if..." }
              ],
              "alternative_approaches": ["Some officers have chosen to..."],
              "further_reading": [{ "title": "GFR Rule 173", "source": "GFR 2017" }]
            } }
```

---

## 5. Error Codes & Rate Limits

| Code | Status | Meaning |
|---|---|---|
| `AUTH_REQUIRED` | 401 | Missing/expired token |
| `FORBIDDEN` | 403 | Accessing another officer's data |
| `NOT_FOUND` | 404 | Invalid resource ID |
| `INVALID_TRANSITION` | 409 | State machine violation |
| `RATE_LIMITED` | 429 | Too many requests |
| `LLM_BUSY` | 503 | Gemini rate limit hit — retry after backoff |

| Endpoint Group | Limit |
|---|---|
| Auth | 3 req/min per email |
| NPC interactions | 20 req/min per user |
| Reference Whisperer | 10 req/min per user |
| Draft critique | 5 req/min per user |
| **Gemini global** | **15 RPM shared across all users** |

When Gemini 15 RPM limit is hit, requests queue with exponential backoff. Frontend shows "thinking..." animation. Max wait: ~8 seconds.

---

*End of API Specification v2.0*
