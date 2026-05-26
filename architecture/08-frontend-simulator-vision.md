# GovernAI Studio — Frontend Simulator Vision & Prototype Plan
## v3.0 · May 2026

> **Design Philosophy:** Public-interest infrastructure with the polish of a premium product.
> **NOT:** gamified, flashy, corporate-training, or minimum-viable.

---

## 1. The Simulator Experience — What Makes It Innovative

### 1.1 The "War Room" Metaphor

The simulator doesn't feel like a quiz, a chatbot, or a training module. It feels like walking into a **government war room** at a critical moment. The officer sits at their desk. The files arrive. The stakeholders walk in. The clock is ticking. The references are at hand. The consequences play out. The mentor appears afterward.

### 1.2 Six Design Innovations Beyond v2.0

| Innovation | What It Is | Why It Matters |
|---|---|---|
| **Cinematic Setting Reveal** | Full-viewport immersive scene with parallax depth, ambient sound cues, and typewriter narrative | Creates emotional investment before the first decision |
| **Living NPC Panels** | NPCs appear as character cards with animated expressions, role badges, and contextual body language | Officers engage with *characters*, not chat bubbles |
| **Split-Brain Decision UI** | Decision cards on left, Reference Whisperer on right, with a connecting "tension line" showing which references relate to which options | Makes the framework-to-decision connection visual and visceral |
| **Consequence Theater** | Consequences render as a newspaper front page, RTI filing document, internal government noting — not as plain text cards | Consequences feel *real* because they look like real artifacts |
| **Reflection Observatory** | Post-scenario debrief rendered as a constellation map where each Sutra is a star, connections show trade-offs, and the officer's path is traced | Reflection becomes spatial and contemplative, not a report card |
| **Ambient State Awareness** | Subtle environmental changes (background tint, ambient particles, progress glow) shift as the officer moves through stages | The interface *breathes* with the narrative without distracting |

---

## 2. Page-by-Page Prototype Specifications

### 2.1 Login Page (`/login`)

**Concept:** "Entering the institution." A single floating card on a deep navy void with subtle grid lines suggesting the structure of governance.

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│              ╔══════════════════════╗                │
│              ║                      ║                │
│              ║     ◆ GovernAI       ║                │
│              ║       Studio         ║                │
│              ║                      ║                │
│              ║  "Foresight, made    ║                │
│              ║   practiceable."     ║                │
│              ║                      ║                │
│              ║ ┌──────────────────┐ ║                │
│              ║ │ your@gov.in      │ ║                │
│              ║ └──────────────────┘ ║                │
│              ║ ┌──────────────────┐ ║                │
│              ║ │  Send Magic Link │ ║                │
│              ║ └──────────────────┘ ║                │
│              ║                      ║                │
│              ║  🔒 Private. Always. ║                │
│              ╚══════════════════════╝                │
│                                                      │
│   Built as public-interest infrastructure for India  │
└──────────────────────────────────────────────────────┘
```

**Key Effects:**
- Background: `#020617` with CSS grid pattern at 3% opacity
- Radial gradient: Indigo (`#312E81`) at 8% opacity behind card
- Card entrance: Scale 0.96 → 1.0 + fade-in (400ms ease-out)
- Input focus: Indigo glow ring + subtle shadow expansion
- Button hover: Lift 1px + shadow deepen
- Success state: Card content crossfades to envelope icon with SVG checkmark draw animation

---

### 2.2 Dashboard / Scenario Library (`/dashboard`)

**Concept:** "The briefing table." Scenarios laid out like classified folders on a desk.

```
┌──────────────────────────────────────────────────────┐
│ ◆ GovernAI Studio              ☀️ ⚙️ [DK]           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Your Scenarios                                      │
│  Choose a scenario to begin. Each takes ~35-45 min.  │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │ ▶ Resume: "The Vendor with the Free AI"         │ │
│  │   Stage: Stakeholder Dialogue · Decision 2 of 5 │ │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
│  [All] [Agriculture] [Healthcare] [Education] [Smart │
│   Cities] [Cross-cutting]                            │
│                                                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│  │ CROSS-CUT  │ │ HEALTHCARE │ │ AGRICULTURE│       │
│  │            │ │            │ │            │       │
│  │ The Vendor │ │ The Reading│ │ The Advisory│       │
│  │ with the   │ │ That Wasn't│ │ That Failed │       │
│  │ Free AI    │ │ Consistent │ │ in Marathi  │       │
│  │            │ │            │ │            │       │
│  │ ~35 min    │ │ ~40 min    │ │ ~35 min    │       │
│  │ ★ Recom.   │ │            │ │ In Progress│       │
│  │ Trust +2   │ │ Fairness+1 │ │ People +2  │       │
│  └────────────┘ └────────────┘ └────────────┘       │
│                                                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│  │ CROSS-CUT  │ │ EDUCATION  │ │ CROSS-CUT  │       │
│  │            │ │            │ │            │       │
│  │ 72 Hours   │ │ Classroom  │ │ Aadhaar    │       │
│  │ Before     │ │ That Out-  │ │ Numbers in │       │
│  │ Polling    │ │ paced...   │ │ Chatbot    │       │
│  │            │ │            │ │            │       │
│  │ ~40 min    │ │ ~35 min    │ │ ~35 min    │       │
│  │            │ │ ★ Recom.   │ │ ✓ Complete │       │
│  └────────────┘ └────────────┘ └────────────┘       │
└──────────────────────────────────────────────────────┘
```

**Card Interactions:**
- Hover: Border glow (indigo 15%), translateY(-2px), shadow deepen
- Domain pill: Color-coded (green/agriculture, red/healthcare, blue/education, violet/smart-city, slate/cross-cutting)
- Sutra pills: Tiny neutral badges showing engaged principles
- Click: Card scales to 1.02 briefly, then navigates with a page fade

---

### 2.3 Simulation — The Core Experience (`/simulation/[session_id]`)

This is the heart of the product. Five stages, each with a distinct layout.

#### Stage 1: Setting — "Cinematic Reveal"

```
┌──────────────────────────────────────────────────────┐
│ ← Exit  "The Vendor with the Free AI"  ●○○○○  📖   │
├──────────────────────────────────────────────────────┤
│                                                      │
│                                                      │
│         ┌──────────────────────────────┐             │
│         │                              │             │
│         │  It is 9:47 AM on a Tuesday  │             │
│         │  in March. You are sitting   │             │
│         │  in your office on the       │             │
│         │  fourth floor of Shastri     │             │
│         │  Bhawan. Your PA walks in    │             │
│         │  with a file marked          │             │
│         │  "URGENT — AI Procurement"   │             │
│         │  and a visiting card from    │             │
│         │  a vendor you've never       │             │
│         │  met. The file has been      │             │
│         │  pending for eleven days.█   │             │
│         │                              │             │
│         │                              │             │
│         └──────────────────────────────┘             │
│                                                      │
│                                    [Continue →]      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Effects:**
- Typewriter text reveal: 30ms per character, cursor blink at end
- Background: Subtle vignette effect (darker edges, lighter center)
- Ambient: Faint paper-texture overlay at 2% opacity
- Continue button: Appears with fade after narrative completes
- Transition to Stage 2: 400ms crossfade

#### Stage 2: Stakeholder Dialogue — "The Room"

```
┌──────────────────────────────────────────────────────┐
│ ← Exit  "The Vendor with the Free AI"  ●●○○○  📖   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────┐ ┌──────────────────────┐│
│  │ STAKEHOLDERS           │ │                      ││
│  │                        │ │  Vikram Desai        ││
│  │ ┌──────────────────┐   │ │  Vendor Architect    ││
│  │ │ ◉ Vikram Desai   │   │ │  ─────────────────  ││
│  │ │   Vendor Arch.   │   │ │                      ││
│  │ │   [Speaking...]   │   │ │  "Thank you for     ││
│  │ └──────────────────┘   │ │   making the time,   ││
│  │                        │ │   sir. I know your   ││
│  │ ┌──────────────────┐   │ │   schedule is tight. ││
│  │ │ ○ Meera Sharma   │   │ │   Let me get        ││
│  │ │   Your Dep. Sec. │   │ │   straight to the   ││
│  │ │   [Waiting...]    │   │ │   point..."         ││
│  │ └──────────────────┘   │ │                      ││
│  │                        │ │  ┌──────────────────┐││
│  │ ┌──────────────────┐   │ │  │ Type response... │││
│  │ │ ○ Rajesh Kumar   │   │ │  └──────────────────┘││
│  │ │   IT Director    │   │ │              [Send →]││
│  │ │   [Waiting...]    │   │ │                      ││
│  │ └──────────────────┘   │ │                      ││
│  └────────────────────────┘ └──────────────────────┘│
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Key Interactions:**
- NPC list on left: Click to switch active conversation
- Active NPC: Teal badge glow, "Speaking..." status with typing dots
- Waiting NPCs: Subtle pulse animation on badge when they have something to say
- Chat: SSE streaming with character-by-character reveal
- NPC response: 3-dot typing indicator (150ms staggered)
- Input: Auto-resize textarea, max 500 chars
- Required interactions: Subtle indicator showing min exchanges needed

#### Stage 3: Decision Moments — "The Split Brain"

```
┌──────────────────────────────────────────────────────┐
│ ← Exit  "The Vendor with the Free AI"  ●●●○○  📖   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Decision 2 of 5                                     │
│                                                      │
│  "The vendor has offered a 3-year exclusive          │
│   contract with free first-year licensing.           │
│   Your IT Director is enthusiastic. The Deputy       │
│   Secretary has flagged data residency concerns."    │
│                                                      │
│  ┌─────────────────────┐  ┌──────────────────────┐  │
│  │ YOUR OPTIONS        │  │ 📖 REFERENCES        │  │
│  │                     │  │                      │  │
│  │ ┌─────────────────┐ │  │ GFR Rule 144         │  │
│  │ │ A. Proceed with │ │  │ "All procurement of  │  │
│  │ │ the vendor's    │◄├──┤  goods and services   │  │
│  │ │ proposal        │ │  │  shall be done..."   │  │
│  │ └─────────────────┘ │  │  Relevance: ████░ H  │  │
│  │                     │  │                      │  │
│  │ ┌─────────────────┐ │  │ ─────────────────    │  │
│  │ │ B. Propose open │ │  │                      │  │
│  │ │ tender with     │◄├──┤ DPDP Act Section 17  │  │
│  │ │ safeguards      │ │  │ "Data residency and  │  │
│  │ └─────────────────┘ │  │  localisation..."    │  │
│  │                     │  │  Relevance: ████░ H  │  │
│  │ ┌─────────────────┐ │  │                      │  │
│  │ │ C. Reject and   │ │  │ ─────────────────    │  │
│  │ │ escalate        │ │  │                      │  │
│  │ └─────────────────┘ │  │ India AI Guidelines  │  │
│  │                     │  │ Sutra 3: "Innovation │  │
│  │ ┌─────────────────┐ │  │ over Restraint..."   │  │
│  │ │ ✍ Write your   │ │  │  Relevance: ███░░ M  │  │
│  │ │ own approach    │ │  │                      │  │
│  │ └─────────────────┘ │  │  ⚠️ Contextual       │  │
│  │                     │  │  suggestions, not    │  │
│  │   [Confirm →]       │  │  legal advice.       │  │
│  └─────────────────────┘  └──────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**The "Tension Lines":**
- SVG lines connect reference cards to relevant decision options
- Lines pulse softly when a reference is highly relevant to a hovered option
- Creates a visual representation of "framework meeting decision"

**Decision Card Interactions:**
- Hover: Scale 1.02, border glow, connected references highlight
- Select: Indigo border (2px), checkmark fade-in, other cards dim to 60%
- Freeform: Expands to textarea with 2000-char limit
- Confirm: Requires selection, button pulses gently when ready

#### Stage 4: Consequences — "The Theater"

```
┌──────────────────────────────────────────────────────┐
│ ← Exit  "The Vendor with the Free AI"  ●●●●○  📖   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  "Three months later..."                             │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │ ╔══════════════════════════════════════════╗  │    │
│  │ ║  THE HINDUSTAN TIMES                     ║  │    │
│  │ ║                                          ║  │    │
│  │ ║  Ministry Signs 3-Year AI Deal           ║  │    │
│  │ ║  with Single Vendor; Opposition          ║  │    │
│  │ ║  Questions Procurement Process           ║  │    │
│  │ ║                                          ║  │    │
│  │ ║  "Sources say the contract was awarded   ║  │    │
│  │ ║   without a comparative evaluation..."   ║  │    │
│  │ ╚══════════════════════════════════════════╝  │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │  📋 RTI FILING (CPIO/2026/AI/0847)          │    │
│  │                                              │    │
│  │  "Under Section 6 of the RTI Act, I         │    │
│  │   request copies of all evaluation           │    │
│  │   criteria used for the AI vendor            │    │
│  │   selection in File No. F.12/3/2026-IT..."  │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │  📝 INTERNAL NOTE (Deputy Secretary)         │    │
│  │                                              │    │
│  │  "Sir, the vendor's system is now processing │    │
│  │   citizen data on servers in Singapore.      │    │
│  │   DPDP Act compliance may be at risk..."     │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│                                    [Continue →]      │
└──────────────────────────────────────────────────────┘
```

**Effects:**
- Each consequence card slides in sequentially (300ms stagger)
- Newspaper: Serif font (Georgia/Merriweather), faded paper texture
- RTI filing: Monospace font (JetBrains Mono), government form styling
- Internal note: Handwritten-style font, slightly tilted (1deg), notepad background
- No right/wrong indicators — just consequences, presented as facts

#### Stage 5: Reflection — "The Observatory"

```
┌──────────────────────────────────────────────────────┐
│ ← Exit  "The Vendor with the Free AI"  ●●●●●  📖   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Your Reflection                                     │
│                                                      │
│  "You navigated a complex procurement decision       │
│   under time pressure, balancing innovation with     │
│   institutional safeguards..."                       │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │             THE SEVEN SUTRAS                  │    │
│  │                                               │    │
│  │    ◆ Trust ─────────── ◆ People First         │    │
│  │    │ (strongly          │ (moderately          │    │
│  │    │  engaged)          │  engaged)            │    │
│  │    │                    │                      │    │
│  │    ◆ Innovation ─────── ◆ Fairness            │    │
│  │    │ (tension            (not addressed)       │    │
│  │    │  identified)                              │    │
│  │    │                                           │    │
│  │    ◆ Accountability ── ◆ Understandable        │    │
│  │    │ (strongly           (moderately           │    │
│  │    │  engaged)            engaged)             │    │
│  │    │                                           │    │
│  │    └───────────────── ◆ Safety                 │    │
│  │                        (not addressed)         │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ▼ Trust is the Foundation                           │
│  "Your decision to request documentation before      │
│   proceeding showed an instinct for institutional    │
│   trust-building. How might the vendor have          │
│   responded if you had asked for a public audit      │
│   clause instead?"                                   │
│                                                      │
│  ▼ Innovation over Restraint                         │
│  "You chose caution over speed — which protected     │
│   the institution. What conditions would need to     │
│   exist for you to move faster on an AI deployment   │
│   without sacrificing due diligence?"                │
│                                                      │
│  📚 Further Reading                                  │
│  • GFR Rule 173 — Open Tender Requirements           │
│  • DPDP Act Section 8 — Data Fiduciary Obligations   │
│  • India AI Guidelines — Sutra 3 Commentary          │
│                                                      │
│                        [Return to Library →]         │
└──────────────────────────────────────────────────────┘
```

**Effects:**
- Sutra constellation: SVG with animated path draws connecting engaged sutras
- Engaged sutras: Bright indigo glow, pulsing softly
- Unaddressed sutras: Dim, with a subtle "?" icon
- Expandable sections: Click sutra name to reveal observation + reflective question
- No scores, no percentages, no comparisons — ever

---

## 3. Component Architecture

```
src/
├── app/
│   ├── layout.tsx              # Root layout, dark mode, Inter font
│   ├── page.tsx                # Redirect to /login or /dashboard
│   ├── login/page.tsx          # Login page
│   ├── onboarding/page.tsx     # Onboarding flow
│   ├── dashboard/page.tsx      # Scenario library
│   └── simulation/
│       └── [sessionId]/
│           └── page.tsx        # Main simulation container
├── components/
│   ├── ui/                     # shadcn/ui primitives
│   ├── auth/
│   │   └── LoginCard.tsx
│   ├── onboarding/
│   │   ├── QuestionCard.tsx
│   │   └── ProgressDots.tsx
│   ├── dashboard/
│   │   ├── ScenarioCard.tsx
│   │   ├── DomainFilter.tsx
│   │   └── ResumeBanner.tsx
│   ├── simulation/
│   │   ├── SimulationShell.tsx       # Stage router + top bar
│   │   ├── SettingReveal.tsx         # Typewriter narrative
│   │   ├── StakeholderPanel.tsx      # NPC list
│   │   ├── NPCChat.tsx              # Streaming chat with NPC
│   │   ├── DecisionPanel.tsx         # Decision cards
│   │   ├── ReferenceWhisperer.tsx    # Reference sidebar
│   │   ├── DraftingEditor.tsx        # TipTap rich text
│   │   ├── ConsequenceTheater.tsx    # Consequence cards
│   │   ├── ReflectionObservatory.tsx # Sutra constellation
│   │   └── SutraCard.tsx             # Expandable sutra observation
│   └── shared/
│       ├── StageIndicator.tsx
│       ├── TypingDots.tsx
│       └── LoadingScreen.tsx
├── stores/
│   ├── sessionStore.ts         # Zustand — simulation state
│   └── authStore.ts            # Zustand — auth state
├── lib/
│   ├── api.ts                  # API client
│   ├── sse.ts                  # Server-Sent Events handler
│   └── constants.ts            # Design tokens
└── styles/
    └── globals.css             # Design system CSS variables
```

---

## 4. Responsive Design Strategy

| Breakpoint | Layout | Adaptations |
|---|---|---|
| Desktop (>1280px) | Full two-panel simulation | Side-by-side NPC + chat, decision + references |
| Tablet (768-1279px) | Stacked panels | NPC list collapses to top bar, references become bottom sheet |
| Mobile (< 768px) | Single panel | Tab navigation between panels, bottom sheet for references |

---

## 5. Animation Specification (Production)

| Element | Animation | Duration | Easing |
|---|---|---|---|
| Page transition | Fade + slight scale | 200ms | ease-out |
| Card hover | translateY(-2px) + shadow | 150ms | ease-in-out |
| Typewriter text | Character reveal | 30ms/char | linear |
| NPC typing dots | Sequential pulse | 1.2s loop | ease-in-out, 150ms stagger |
| Decision select | Scale 1.02 + border glow | 200ms | ease-out |
| Consequence card entry | Slide up + fade | 300ms, 200ms stagger | cubic-bezier(0.4, 0, 0.2, 1) |
| Sutra constellation | SVG path draw | 600ms per edge | ease-in-out |
| Reference connection lines | Opacity pulse | 2s loop | ease-in-out |
| Stage transition | Crossfade | 400ms | ease-in-out |
| Button loading | Spinner rotation | 800ms loop | linear |

---

## 6. Key Design Tokens (CSS Variables)

```css
:root {
  /* This is dark mode by default */
  --bg-page: #0F172A;
  --bg-card: #1E293B;
  --bg-input: #0F172A;
  --bg-hover: #334155;
  
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  --text-disabled: #475569;
  
  --brand-500: #6366F1;
  --brand-600: #4F46E5;
  --brand-400: #818CF8;
  --brand-glow: rgba(99, 102, 241, 0.15);
  
  --border-default: #334155;
  --border-hover: #475569;
  --border-active: #6366F1;
  
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  
  --shadow-glow: 0 0 20px var(--brand-glow);
  --transition-fast: 150ms ease-in-out;
  --transition-panel: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

*End of Frontend Simulator Vision v3.0*
