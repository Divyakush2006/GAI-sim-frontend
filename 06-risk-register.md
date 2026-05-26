# GovernAI Studio — Risk Register & Mitigations
## v2.0 · May 2026

---

## Risk Matrix

| # | Risk | Category | Probability | Impact | Severity | Mitigation |
|---|---|---|---|---|---|---|
| R1 | **Gemini free tier rate limits hit during concurrent usage** | Technical | High | Medium | 🟡 High | Queue with backoff. Show "thinking..." animation (2-8s extra wait). Stagger pilot cohort usage times. At 15 RPM, max ~2 concurrent officers without queuing. |
| R2 | **Render free tier cold starts frustrate officers** | Technical | High | Low | 🟢 Medium | Cron ping every 14 min during business hours (free cron-job.org). Pre-warm on login. Loading animation. |
| R3 | **Gemini free tier discontinued or terms change** | Technical | Low | Critical | 🟡 High | LLM Gateway is abstracted. Can swap to: Groq free tier (Llama 3), Cerebras free, or local Ollama in <1 day. Architecture is provider-agnostic. |
| R4 | **Neon free tier compute hours exhausted (190 hrs/month)** | Technical | Low | High | 🟡 High | Neon scales to zero when idle (good). Monitor usage. If approaching limit, optimize queries with connection pooling. Upgrade to $19/month Launch tier if needed. |
| R5 | **NPC responses break character or hallucinate** | AI Quality | Medium | Medium | 🟡 High | Strong system prompts with explicit constraints. Temperature 0.7 (not higher). Guardrail prompts: "Never break character. Never reference that you are an AI." Test all NPC prompts before launch. |
| R6 | **Reference Whisperer returns irrelevant or incorrect legal clauses** | AI Quality | Medium | High | 🔴 Critical | Scenario-specific keyword filtering. Gemini rerank step. Human review of top-3 results per scenario during QA. Disclaimer: "Contextual suggestions, not legal advice." |
| R7 | **Reflection Coach sounds evaluative despite "no scoring" principle** | AI Quality | Medium | High | 🔴 Critical | Extensive prompt engineering with explicit constraints: "Never score. Never rank. Never compare to other officers. Use only reflective questions and observations." Tone review with civil-servant advisors during Phase 3. |
| R8 | **Officers don't trust that their data is private** | Adoption | Medium | Critical | 🔴 Critical | Clear privacy notice at login. "Your responses are never shared, never used for evaluation, never used to train AI models." Technical enforcement via RLS. No admin dashboard that shows individual data. |
| R9 | **Officers find scenarios unrealistic or patronising** | Content | Medium | High | 🔴 Critical | Scenarios authored with retired civil servants and GovernAI Academy faculty. Government idiom validated by IAS/IPS advisors. Internal pilot feedback (Phase 3) catches tone issues before launch. |
| R10 | **Low pilot adoption (officers don't complete scenarios)** | Adoption | Medium | Medium | 🟡 High | Keep scenarios to 35-45 minutes. Mobile-friendly design for on-the-go use. Personal outreach from GovernAI Academy alumni network. No mandatory completion — purely voluntary. |
| R11 | **Scenario content becomes outdated as frameworks evolve** | Content | Low | Medium | 🟢 Medium | Scenarios stored as versioned JSON. Content author can update without code changes. Reference corpus can be re-chunked and re-embedded. Version field tracks currency. |
| R12 | **Platform used for officer evaluation despite design intent** | Privacy | Low | Critical | 🔴 Critical | No admin endpoint for cross-officer data. No transcript export. No aggregate per-officer reporting. Audit logs track only access events, not decision content. Terms of use prohibit institutional evaluation use. |
| R13 | **Single point of failure — one developer leaves** | Team | Medium | High | 🔴 Critical | Monorepo with clear folder structure. Comprehensive README. All decisions documented in architecture docs. Standard Python + Next.js stack — easy to onboard replacements. |
| R14 | **ChromaDB data lost on Render disk reset** | Technical | Low | Medium | 🟢 Medium | Corpus ingestion is a repeatable script (takes ~10 min). Run automatically on deploy. Source chunks stored in repo. Officer data is in Neon (persistent). |
| R15 | **Resend free tier (100 emails/day) insufficient** | Technical | Low | Low | 🟢 Low | 100 magic links/day is plenty for 50-200 pilot users (most login once). If needed, switch to Brevo free (300/day) or implement password-based auth as fallback. |

---

## Risk Severity Legend

| Severity | Definition | Action |
|---|---|---|
| 🔴 **Critical** | Could derail the project or violate core principles | Mitigate before Phase 3. Escalate to Product Lead. |
| 🟡 **High** | Will degrade user experience or delay timeline | Mitigate before pilot launch. Monitor actively. |
| 🟢 **Medium** | Manageable with known workarounds | Accept risk with documented workaround. |

---

## Top 3 Risks Requiring Immediate Attention

1. **R8 (Privacy Trust):** Officers must believe the platform is safe. This is existential. Implement privacy notice, RLS, no-admin-view policy in Phase 1. Review with civil-servant advisors in Phase 3.

2. **R6 (Whisperer Accuracy):** Surfacing wrong legal clauses would destroy credibility. Invest in corpus quality, scenario-specific filtering, and human QA of retrieval results before launch.

3. **R7 (Reflection Coach Tone):** If the coach sounds like an examiner, officers will disengage or perform. Prompt engineering must be validated with actual IAS officers during internal pilot.

---

## Assumptions

| # | Assumption | If Wrong... |
|---|---|---|
| A1 | Gemini 2.0 Flash free tier remains available through pilot period | Swap to Groq/Cerebras free tier (1-day migration) |
| A2 | Neon free tier is sufficient for 200 officers | Upgrade to $19/month or switch to Supabase free |
| A3 | Render free tier cold starts are acceptable for pilot | Upgrade to $7/month Starter for always-on |
| A4 | 50-200 officers will use the platform sequentially, not concurrently | If concurrent >3, add request queuing |
| A5 | English-only is acceptable for MVP pilot | Correct — vernacular is Phase 3 by design |
| A6 | Government networks can access Vercel + Render domains | If blocked, self-host on Oracle Cloud free tier (2 VMs always-free) |
| A7 | Team members have their own development machines | No cloud dev environments needed |

---

*End of Risk Register v2.0*
