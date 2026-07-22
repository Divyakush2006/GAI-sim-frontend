<p align="center">
  <img src="https://img.shields.io/badge/GovernAI-Studio-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTEyIDJMMiA3bDEwIDUgMTAtNS0xMC01ek0yIDE3bDEwIDUgMTAtNS0xMC01LTEwIDV6TTIgMTJsMTAgNSAxMC01LTEwLTUtMTAgNXoiLz48L3N2Zz4=&logoColor=white" alt="GovernAI Studio" height="40"/>
</p>

<h1 align="center">GovernAI Studio</h1>

<p align="center">
  <strong>AI-Powered Governance Simulation Platform for Indian Civil Servants</strong>
</p>

<p align="center">
  <a href="#features"><img src="https://img.shields.io/badge/Scenarios-5_Complete-10b981?style=flat-square" alt="Scenarios"/></a>
  <a href="#tech-stack"><img src="https://img.shields.io/badge/LLM_Providers-4_Active-6366f1?style=flat-square" alt="Providers"/></a>
  <a href="#architecture"><img src="https://img.shields.io/badge/API_Endpoints-12_Live-f59e0b?style=flat-square" alt="Endpoints"/></a>
  <a href="#database"><img src="https://img.shields.io/badge/Database-Neon_PostgreSQL-0ea5e9?style=flat-square" alt="Database"/></a>
  <a href="#license"><img src="https://img.shields.io/badge/Cost-₹0%2Fmonth-22c55e?style=flat-square" alt="Cost"/></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#features">Features</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Overview

**GovernAI Studio** is an immersive, scenario-based AI governance simulator designed for Indian Administrative Service (IAS) officers and civil servants. Officers navigate realistic governance dilemmas — vendor procurement pressure, cybersecurity incidents, algorithmic bias complaints — by consulting AI-powered NPCs, making consequential decisions, and receiving reflective debriefs mapped to India's **Seven Sutras of AI Governance**.

> **Not a chatbot. Not a quiz. A cinematic simulation** where every decision has consequences, every NPC has a hidden agenda, and every reflection avoids evaluative language — because governance doesn't have "right answers."

### The Problem

India's civil servants are increasingly making decisions about AI procurement, deployment, and governance — but no structured training exists for navigating the intersection of technology, law, and public accountability. Traditional e-learning modules are passive, generic, and fail to develop the **judgment** required for real-world governance.

### The Solution

GovernAI Studio places officers inside realistic, high-stakes scenarios where they must:

- **Consult stakeholders** with competing interests (vendors with hidden agendas, technical advisors, citizens)
- **Reference actual legislation** (DPDP Act, GFR, IT Act, Aadhaar Act) surfaced in real-time
- **Make decisions** that trigger branching consequences (newspaper headlines, RTI filings, internal notes)
- **Reflect** through a non-evaluative debrief mapped to India's AI governance principles

---

## Features

### ✅ Implemented (Current Release)

<table>
<tr>
<td width="50%">

**🧠 AI Intelligence Layer**
- Multi-provider LLM Gateway (4 providers)
- 11-key Gemini API rotation (~165 RPM)
- 5 specialized AI agent templates
- Auto-failover across providers
- Role-based provider routing

</td>
<td width="50%">

**🔐 Authentication & Security**
- Passwordless magic link auth
- JWT access + refresh tokens
- PII stripping middleware
- Security headers (OWASP)
- IP-based rate limiting

</td>
</tr>
<tr>
<td>

**🎭 Simulation Engine**
- 5-stage state machine with DB persistence
- 5 complete scenarios (15 NPCs, 17 decision moments)
- In-character NPC dialogue with hidden agendas
- Rule-based consequence branching
- Seven Sutras reflective debrief

</td>
<td>

**📚 Knowledge Pipeline**
- LightRAG v1.4.9 (GraphRAG)
- Hybrid retrieval (vector + graph search)
- 12 Indian legal statutes indexed
- Real-time reference surfacing at decision moments
- Contextual legal formatting

</td>
</tr>
</table>

### 🔮 In Development (Roadmap)

| Phase | Feature | Status |
|---|---|---|
| Phase 2 | React/Vite cinematic frontend with parallax UI | 🏗️ Designed |
| Phase 2 | 23 generated environment + character assets | ✅ Complete |
| Phase 3 | Full legal corpus ingestion (53 PDFs) | 📋 Planned |
| Phase 3 | Video cutscenes between simulation stages | 📋 Planned |
| Phase 4 | Multi-officer collaborative simulations | 📋 Planned |
| Phase 4 | Institutional analytics dashboard | 📋 Planned |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Phase 2)                       │
│              React/Vite + Parallax Engine + WebSocket            │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (JWT Auth)
┌──────────────────────────▼──────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   Auth API    │  │ Simulation   │  │   Reference           │  │
│  │  Magic Link   │  │   Engine     │  │   Whisperer           │  │
│  │  JWT Tokens   │  │  5 Stages    │  │  GraphRAG Query       │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘  │
│         │                 │                       │              │
│  ┌──────▼─────────────────▼───────────────────────▼───────────┐  │
│  │                   LLM GATEWAY                              │  │
│  │  ┌─────────┐ ┌──────┐ ┌──────────┐ ┌──────────┐           │  │
│  │  │ Gemini  │ │ Groq │ │ Cerebras │ │SambaNova │           │  │
│  │  │ 2.5Flash│ │Llama │ │ Llama 8B │ │Llama 70B │           │  │
│  │  │ 165 RPM │ │30 RPM│ │  30 RPM  │ │  20 RPM  │           │  │
│  │  └─────────┘ └──────┘ └──────────┘ └──────────┘           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  DATA LAYER                                │  │
│  │  ┌──────────────────┐     ┌──────────────────────────┐     │  │
│  │  │ Neon PostgreSQL  │     │ LightRAG Knowledge Graph │     │  │
│  │  │ 6 Tables         │     │ 41 Entities, 7 Relations │     │  │
│  │  │ Officers,Sessions│     │ Indian Legal Corpus       │     │  │
│  │  │ Decisions,Reflect│     │ Vector + Graph Search     │     │  │
│  │  └──────────────────┘     └──────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### AI Agent Architecture

The simulation uses **5 specialized AI agents** — not separate models, but carefully crafted prompt templates routed through the LLM Gateway:

| Agent | Purpose | Temperature | Preferred Provider |
|---|---|---|---|
| **Scenario Director** | Adapts narrative to officer's tier (Policy/Field) | 0.4 | Gemini |
| **NPC Dialogue** | In-character responses with hidden agendas | 0.7 | Groq |
| **Reference Whisperer** | Formats legal references for readability | 0.2 | Gemini |
| **Reflection Coach** | Seven Sutras debrief (non-evaluative) | 0.5 | Gemini |
| **Drafting Partner** | GoI file noting conventions | 0.3 | Cerebras |

### Simulation Lifecycle

```
┌──────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐
│ SETTING  │───▶│ INTERACTION │───▶│  DECISION    │───▶│ CONSEQUENCES │───▶│ REFLECTION │
│          │    │             │    │  MOMENTS     │    │              │    │            │
│ Director │    │ NPC Agents  │    │ Officer      │    │ Rule Engine  │    │ Coach      │
│ Agent    │    │ + Whisperer │    │ Choices      │    │ (no AI)      │    │ Agent      │
│ [AI]     │    │ [AI]        │    │ [no AI]      │    │              │    │ [AI]       │
└──────────┘    └─────────────┘    └──────────────┘    └──────────────┘    └────────────┘
```

---

## Scenarios

Five complete, production-ready scenarios covering different AI governance domains:

| # | Scenario | Domain | NPCs | Decisions | Duration |
|---|---|---|---|---|---|
| 1 | **The Vendor with the Free AI** | Procurement | Vendor Rep, NIC Advisor, Budget Officer | 4 | ~35 min |
| 2 | **The Midnight CERT-In Alert** | Cybersecurity | CERT-In Analyst, Vendor CTO, Deputy Collector | 3 | ~30 min |
| 3 | **The Aadhaar Integration Dilemma** | Data Protection | UIDAI Director, Welfare Activist, AAWOS Tech Lead | 3 | ~40 min |
| 4 | **The Open-Source vs Proprietary Debate** | Procurement | GlobalAI VP, IIT Professor, GeM Advisor | 3 | ~35 min |
| 5 | **The Twelve Thousand Rejections** | Fairness & Bias | NCM Member, CreditAI CEO, Statistical Advisor | 3 | ~40 min |

Each scenario includes:
- **Tier-adapted narratives** (Policy/HQ vs Field/District variants)
- **NPCs with hidden agendas** (never revealed to the officer)
- **Multiple decision moments** with 4 options + freeform
- **Branching consequences** (newspaper headlines, RTI filings, internal notes)
- **Whisperer keywords** mapped to relevant Indian legislation
- **Sutra mappings** for the reflective debrief

---

## Tech Stack

### Backend
| Technology | Purpose | Cost |
|---|---|---|
| **FastAPI** | Async REST API framework | Free |
| **Neon PostgreSQL** | Database (0.5GB free tier) | Free |
| **SQLAlchemy 2.0** | Async ORM with connection pooling | Free |
| **LightRAG v1.4.9** | Graph-enhanced RAG (knowledge graph) | Free |
| **LiteLLM** | Unified LLM API across 4 providers | Free |
| **PyJWT** | JWT token management | Free |
| **Resend** | Magic link email delivery (100/day) | Free |
| **Structlog** | Structured logging | Free |

### LLM Providers (All Free Tiers)
| Provider | Model | RPM | Daily Limit | Used For |
|---|---|---|---|---|
| **Google Gemini** | gemini-2.5-flash | 15 × 11 keys = **165** | 16,500 | Director, Whisperer, Coach |
| **Groq** | llama-3.3-70b | 30 | 14,400 | NPC Dialogue (fastest) |
| **Cerebras** | llama-3.1-8b | 30 | 14,400 | Drafting Partner |
| **SambaNova** | llama-3.3-70b | 20 | 10,000 | Fallback |
| | | **Total: ~245 RPM** | **~55,300/day** | |

### Frontend (Phase 2 — In Development)
| Technology | Purpose |
|---|---|
| **React 19 + Vite** | SPA framework |
| **CSS Parallax Engine** | 3-layer depth environments |
| **Framer Motion** | Micro-animations + transitions |
| **23 AI-Generated Assets** | 15 environment layers + 8 character portraits |

---

## Quick Start

### Prerequisites

- Python 3.11+
- A [Neon](https://neon.tech) PostgreSQL database (free)
- At least one [Gemini API key](https://aistudio.google.com/apikey) (free)

### Setup

```bash
# Clone the repository
git clone https://github.com/governAI-techteam/ai-sumlator.git
cd ai-sumlator
git checkout Frontend

# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database URL

# Create database tables
python scripts/create_tables.py

# Seed scenarios
python scripts/seed_scenarios.py

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "ok", "service": "GovernAI Studio", "version": "3.0.0"}
```

### Run the Prototype Demo

```bash
# Execute the full 12-step simulation lifecycle
python scripts/demo_prototype.py
```

This runs through: Auth → Onboarding → Scenario Selection → Director Agent → NPC Conversations → Decisions → Consequences → Seven Sutras Reflection — all via live API calls.

---

## API Reference

All endpoints are prefixed with `/v1/`.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/auth/magic-link` | Request a passwordless login link |
| `POST` | `/v1/auth/verify` | Verify magic link → receive JWT |
| `POST` | `/v1/auth/refresh` | Refresh expired access token |

### Onboarding

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/onboarding/submit` | Submit officer profile → silent tier routing |

### Scenarios

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/scenarios` | List all available scenarios |
| `GET` | `/v1/scenarios/{slug}` | Get scenario metadata |

### Simulation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/sessions/start` | Create session → Director generates narrative |
| `POST` | `/v1/sessions/{id}/interact` | Talk to an NPC → AI generates in-character response |
| `POST` | `/v1/sessions/{id}/decision` | Submit a decision (option or freeform) |
| `POST` | `/v1/sessions/{id}/advance` | Advance to next simulation stage |
| `GET` | `/v1/sessions/{id}/consequences` | View consequence artifacts |
| `GET` | `/v1/sessions/{id}/reflection` | Get Seven Sutras debrief |
| `GET` | `/v1/sessions/{id}/status` | Get current session state |
| `GET` | `/v1/sessions/{id}/reference` | Get Whisperer legal references |

### Admin

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check |
| `GET` | `/admin/diagnostics` | Provider status, DB connectivity, graph stats |

---

## Database Schema

```
┌──────────────┐     ┌──────────────────────┐     ┌──────────────┐
│   officers   │────▶│ simulation_sessions  │────▶│  decisions   │
│              │     │                      │     │              │
│ id (UUID)    │     │ id (UUID)            │     │ id (UUID)    │
│ email        │     │ officer_id (FK)      │     │ session_id   │
│ tier (A/B)   │     │ scenario_id (FK)     │     │ moment_id    │
│ work_location│     │ current_stage (ENUM) │     │ choice_type  │
│ onboarding   │     │ conversation_history │     │ selected_opt │
│ last_login   │     │ adapted_narrative    │     │ free_text    │
└──────┬───────┘     │ is_complete          │     │ references   │
       │             └──────────┬───────────┘     └──────────────┘
       │                        │
┌──────▼───────┐     ┌──────────▼───────────┐
│ magic_links  │     │    reflections       │
│              │     │                      │
│ id (UUID)    │     │ id (UUID)            │
│ email        │     │ session_id (FK)      │
│ token_hash   │     │ preamble             │
│ expires_at   │     │ sutra_observations   │
│ used (bool)  │     │ synthesis            │
└──────────────┘     │ further_reading      │
                     └──────────────────────┘

┌──────────────┐
│  scenarios   │
│              │
│ id (UUID)    │
│ slug         │
│ title        │
│ domain       │
│ setting_narr │  ← JSON (tier_a + tier_b variants)
│ npcs         │  ← JSON (personalities, hidden agendas)
│ decision_mom │  ← JSON (options, freeform flags)
│ consequence  │  ← JSON (trigger rules, artifacts)
│ whisperer_kw │  ← JSON (legal keywords per decision)
│ sutras       │  ← JSON (mapped governance principles)
└──────────────┘
```

---

## Project Structure

```
ai-sumlator/
├── architecture/                    # Technical documentation (10 modules)
│   ├── 01-system-architecture.md
│   ├── 02-database-schema.md
│   ├── 03-api-specification.md
│   ├── 04-state-machine-user-journey.md
│   ├── 05-development-roadmap.md
│   ├── 06-risk-register.md
│   ├── 07-ai-ml-backend-engine.md
│   ├── 08-frontend-simulator-vision.md
│   ├── 09-graphrag-pipeline-implementation.md
│   └── 10-llm-gateway-orchestration.md
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory + lifecycle
│   │   ├── config.py                # Pydantic settings validation
│   │   ├── ai/
│   │   │   ├── gateway.py           # Multi-provider LLM router (258 lines)
│   │   │   ├── key_rotator.py       # 11-key Gemini round-robin (131 lines)
│   │   │   └── agents.py            # 5 AI agent templates (597 lines)
│   │   ├── api/routes/
│   │   │   ├── auth.py              # Magic link + JWT auth (343 lines)
│   │   │   ├── onboarding.py        # Tier routing (166 lines)
│   │   │   ├── scenarios.py         # Scenario CRUD (93 lines)
│   │   │   ├── simulation.py        # Core engine (777 lines)
│   │   │   └── whisperer.py         # Reference surfacing (140 lines)
│   │   ├── db/
│   │   │   ├── database.py          # Async SQLAlchemy engine
│   │   │   └── models.py            # 6 ORM models (190 lines)
│   │   ├── corpus/
│   │   │   ├── graph_builder.py     # LightRAG wrapper (209 lines)
│   │   │   └── ingest.py            # Document ingestion pipeline
│   │   ├── retrieval/
│   │   │   └── pipeline.py          # Hybrid retrieval engine
│   │   ├── simulation/
│   │   │   └── __init__.py          # 5-stage state machine (201 lines)
│   │   └── privacy/
│   │       └── middleware.py         # PII stripping + rate limiting
│   ├── scripts/
│   │   ├── seed_scenarios.py        # 5 complete scenario seeds
│   │   ├── demo_prototype.py        # End-to-end prototype demo
│   │   └── build_corpus.py          # Legal corpus ingestion
│   ├── .env.example                 # Environment template
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Container for deployment
│   └── render.yaml                  # Render deployment config
│
├── frontend/
│   └── public/assets/               # AI-generated simulation assets
│       ├── environments/            # 15 parallax layers (5 scenes × 3 depths)
│       │   ├── corridor/            # Shastri Bhawan corridor
│       │   ├── conference/          # Stakeholder meeting room
│       │   ├── collector/           # District Collectorate
│       │   ├── newsroom/            # Media consequence view
│       │   └── observatory/         # Reflection constellation
│       └── characters/              # 8 NPC portraits
│           ├── vikram/              # Vendor (neutral, speaking, concerned)
│           ├── meera/               # Deputy Secretary (neutral, speaking, relieved)
│           └── rajesh/              # IT Director (neutral, speaking)
│
└── GovernAI-Studio-Master-Document.md
```

---

## Roadmap

### Phase 1 — Backend Core ✅ Complete
> *"The engine that powers the simulation"*

- [x] FastAPI application with production middleware
- [x] Neon PostgreSQL with 6-table schema
- [x] Magic link authentication with JWT
- [x] Multi-provider LLM Gateway (4 providers, 245+ RPM)
- [x] 11-key Gemini API rotation
- [x] 5 AI agent prompt templates
- [x] 5-stage simulation state machine
- [x] Rule-based consequence engine
- [x] LightRAG knowledge graph (12 statutes indexed)
- [x] 5 complete scenarios seeded in DB
- [x] End-to-end prototype demo verified
- [x] Deployment config (Dockerfile + render.yaml)

### Phase 2 — Frontend & Visual Experience 🏗️ In Progress
> *"The cinematic interface that makes governance training feel like it matters"*

- [x] Design Bible (11-page UI specification)
- [x] 23 AI-generated assets (15 environments + 8 characters)
- [ ] React/Vite project initialization
- [ ] Parallax-driven simulation interface
- [ ] NPC conversation interface with typewriter effect
- [ ] Decision desk with Whisperer sidebar
- [ ] Consequence theater (headlines, RTI filings)
- [ ] Reflection observatory (Seven Sutras constellation)
- [ ] Responsive mobile layout
- [ ] JWT auth integration with frontend routing

### Phase 3 — Content & Intelligence Expansion 📋 Planned
> *"Making the knowledge graph truly authoritative"*

- [ ] Full legal corpus ingestion (53 PDFs → LightRAG)
- [ ] 10 additional character portraits (Prof. Iyer, Suresh, Riya, etc.)
- [ ] Video cutscenes between simulation stages
- [ ] 5 additional scenarios (10 total)
- [ ] ~500 dialogue scripts for ML fine-tuning
- [ ] Drafting Partner integration in frontend

### Phase 4 — Institutional Scale 📋 Planned
> *"From prototype to production deployment at LBSNAA"*

- [ ] Multi-officer collaborative simulations
- [ ] Institutional analytics dashboard
- [ ] Batch deployment for training cohorts
- [ ] Integration with government SSO (eSign/DigiLocker)
- [ ] Accessibility compliance (GIGW Guidelines)
- [ ] Multilingual support (Hindi, regional languages)

---

## Design Philosophy

### Why "No Evaluative Language"?

The Reflection Coach agent is **strictly prohibited** from using words like "correct," "wrong," "good decision," or "mistake." This is not a limitation — it's a deliberate design principle.

Governance decisions exist in a space where:
- Multiple legitimate approaches exist simultaneously
- Context, constraints, and values shape what's appropriate
- The "right" answer often depends on institutional position and political timing

The Coach observes patterns, asks reflective questions, and maps decisions to governance principles — but **never judges**. This mirrors the pedagogy at LBSNAA (Lal Bahadur Shastri National Academy of Administration), where case studies are discussed, not scored.

### Why Hidden Agendas?

Every NPC with a hidden agenda (vendors wanting lock-in, tech leads protecting their funding) creates a more realistic simulation. Officers must:
- Read between the lines of stakeholder responses
- Cross-reference claims across multiple NPCs
- Recognize when institutional interests diverge from public interest

The hidden agenda is **never revealed** to the officer — just like in real governance.

### Why Free Tier Only?

GovernAI Studio runs entirely on free-tier services because:
1. **Government institutions have procurement friction** — free services bypass lengthy approval processes
2. **Proves technical capability** — if it works on free tiers, it scales with budget
3. **No vendor dependency** — all 4 LLM providers are interchangeable

---

## Performance

| Metric | Value |
|---|---|
| Cold start | ~3 seconds |
| Health check | <50ms |
| NPC response (Groq) | 1-3 seconds |
| Director narrative (Gemini) | 3-8 seconds |
| Reflection debrief (Gemini) | 8-15 seconds |
| Concurrent officers supported | ~50-200 |
| Effective LLM capacity | 245+ RPM / 55,300+ req/day |

---

## Security

| Layer | Implementation |
|---|---|
| **Authentication** | Passwordless magic links (SHA-256 hashed tokens) |
| **Authorization** | JWT with 15-min expiry + 7-day refresh |
| **Data Privacy** | PII regex stripping on all log output |
| **Transport** | HTTPS enforced via Render/Vercel |
| **Headers** | X-Content-Type-Options, X-Frame-Options, Referrer-Policy |
| **Rate Limiting** | Per-IP request throttling (60 RPM default) |
| **Email Domain** | Restricted to `gov.in`, `nic.in`, `governai.in` (+ `gmail.com` in dev) |
| **Secrets** | `.env` excluded from version control; `.env.example` provided |

---

## Contributing

We welcome contributions from developers, policy researchers, and governance practitioners.

### For Developers
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### For Policy Researchers
- Help author new scenario content (see `backend/scripts/seed_scenarios.py` for structure)
- Review AI agent guardrails for institutional accuracy
- Suggest relevant legal provisions for the Whisperer knowledge base

### Commit Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `refactor:` — Code restructuring
- `test:` — Testing

---

## Acknowledgments

- **India AI** — Seven Sutras of Responsible AI framework
- **LBSNAA** — Pedagogical model for governance case studies
- **LightRAG** (HKU) — Graph-enhanced retrieval architecture
- **LiteLLM** — Unified LLM provider interface

---

## License

This project is developed by the **GovernAI Tech Team** for institutional governance training. Contact the team for licensing and deployment inquiries.

---

<p align="center">
  <strong>GovernAI Studio</strong> — Because governance decisions deserve better than a multiple-choice quiz.
</p>

---

<p align="center">
  Frontend designed and developed by <a href="https://divyakush.is-a.dev"><strong>Divyakush Punjabi</strong></a><br />
  <a href="https://divyakush.is-a.dev">Portfolio</a> ·
  <a href="https://github.com/Divyakush2006">GitHub</a> ·
  <a href="https://linkedin.com/in/divyakush-punjabi">LinkedIn</a>
</p>
