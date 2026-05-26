# GovernAI Studio — Frontend Development Prompt
## Part 1: Design System, Pages & Layouts

---

## YOUR TASK

Build a complete, production-ready frontend for **GovernAI Studio** — a scenario-based AI governance simulator for Indian civil servants. This is NOT a learning management system. It is an immersive simulation platform where officers are dropped into realistic government situations, interact with AI-powered characters, make governance decisions, and receive private reflective debriefs.

The platform must feel like **public-interest infrastructure** — think the gravitas of a government portal crossed with the polish of a premium SaaS product. It should feel serious, trustworthy, and elegant — never gamified, never flashy, never corporate-training.

**Tech Stack:** Next.js 14 (App Router) · React 18 · Tailwind CSS · shadcn/ui components · Zustand for client state · TipTap for rich text editor · Self-hosted Inter font from Google Fonts.

---

## DESIGN SYSTEM

### Color Palette

```
PRIMARY PALETTE (Government Indigo)
--primary-50:    #EEF2FF    (lightest tint, backgrounds)
--primary-100:   #E0E7FF    (hover states, subtle fills)
--primary-200:   #C7D2FE    (borders, dividers)
--primary-300:   #A5B4FC    (inactive elements)
--primary-400:   #818CF8    (secondary buttons)
--primary-500:   #6366F1    (primary brand color — buttons, links, active states)
--primary-600:   #4F46E5    (primary button hover)
--primary-700:   #4338CA    (pressed states)
--primary-800:   #3730A3    (dark accents)
--primary-900:   #312E81    (darkest — header bar)

NEUTRAL PALETTE (Slate)
--neutral-50:    #F8FAFC    (page backgrounds)
--neutral-100:   #F1F5F9    (card backgrounds, alternate rows)
--neutral-200:   #E2E8F0    (borders, dividers)
--neutral-300:   #CBD5E1    (disabled text)
--neutral-400:   #94A3B8    (placeholder text)
--neutral-500:   #64748B    (secondary text)
--neutral-600:   #475569    (body text)
--neutral-700:   #334155    (headings)
--neutral-800:   #1E293B    (dark mode card bg)
--neutral-900:   #0F172A    (dark mode page bg)
--neutral-950:   #020617    (darkest background)

SEMANTIC COLORS
--success:       #10B981    (completed scenarios, positive consequences)
--success-light: #D1FAE5    (success background)
--warning:       #F59E0B    (in-progress, caution consequences)
--warning-light: #FEF3C7    (warning background)
--error:         #EF4444    (errors only — never for "wrong" decisions)
--error-light:   #FEE2E2    (error background)
--info:          #3B82F6    (Reference Whisperer highlights)
--info-light:    #DBEAFE    (info background)

ACCENT COLORS (for NPC role badges and domain tags)
--accent-teal:     #14B8A6    (Stakeholder Roleplayer badge)
--accent-amber:    #F59E0B    (Scenario Director cues)
--accent-violet:   #8B5CF6    (Reference Whisperer)
--accent-rose:     #F43F5E    (Drafting Partner critique)
--accent-emerald:  #10B981    (Reflection Coach)
--accent-sky:      #0EA5E9    (system messages)

DOMAIN TAG COLORS
--domain-agriculture:  #16A34A / #DCFCE7
--domain-healthcare:   #DC2626 / #FEE2E2
--domain-education:    #2563EB / #DBEAFE
--domain-smartcity:    #7C3AED / #EDE9FE
--domain-crosscutting: #64748B / #F1F5F9
```

### Mode
**Dark mode by default.** Light mode as toggle in settings. The dark mode should feel like a late-night government office — deep navy/slate backgrounds, soft glowing text, subtle borders. NOT pure black — use `--neutral-900` (#0F172A) as page bg and `--neutral-800` (#1E293B) as card bg.

### Typography

```
FONT FAMILY
Primary: 'Inter', system-ui, -apple-system, sans-serif
Monospace: 'JetBrains Mono', 'Fira Code', monospace (for legal clause citations)

SCALE (rem based, 1rem = 16px)
--text-xs:    0.75rem / 1rem     (12px — timestamps, badges)
--text-sm:    0.875rem / 1.25rem (14px — secondary text, captions)
--text-base:  1rem / 1.5rem      (16px — body text, NPC dialogue)
--text-lg:    1.125rem / 1.75rem (18px — card titles, decision options)
--text-xl:    1.25rem / 1.75rem  (20px — section headers)
--text-2xl:   1.5rem / 2rem      (24px — page titles)
--text-3xl:   1.875rem / 2.25rem (30px — hero text on landing)
--text-4xl:   2.25rem / 2.5rem   (36px — scenario title in simulation)

WEIGHTS
--font-normal:   400  (body text)
--font-medium:   500  (labels, badges)
--font-semibold: 600  (headings, buttons)
--font-bold:     700  (hero text, scenario titles)

LETTER SPACING
Headings: -0.025em (slightly tight)
Body: 0em (default)
Caps/badges: 0.05em (slightly wide)
```

### Spacing & Layout

```
SPACING SCALE (Tailwind default)
4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px

BORDER RADIUS
--radius-sm: 6px   (badges, small buttons)
--radius-md: 8px   (cards, inputs)
--radius-lg: 12px  (modals, panels)
--radius-xl: 16px  (large cards, hero sections)
--radius-full: 9999px (avatars, pills)

SHADOWS (subtle, no harsh drop shadows)
--shadow-sm:  0 1px 2px rgba(0,0,0,0.05)
--shadow-md:  0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05)
--shadow-lg:  0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)
--shadow-glow: 0 0 20px rgba(99,102,241,0.15) (primary glow on focus/active)

MAX WIDTHS
Page container: 1280px (centered)
Content area: 768px (reading width for narratives)
Simulation panel: 100% viewport width (immersive, no container)
Chat messages: 640px max per message bubble
```

### Animations & Transitions

```
TRANSITIONS
Default: 150ms ease-in-out (buttons, hovers)
Panel slide: 300ms cubic-bezier(0.4, 0, 0.2, 1)
Modal appear: 200ms ease-out (scale 0.95→1, opacity 0→1)
Page transition: 200ms fade

MICRO-ANIMATIONS
Button hover: translateY(-1px) + shadow increase
Card hover: subtle border glow (primary-500 at 15% opacity)
NPC typing: 3-dot pulse animation (dot1: 0ms, dot2: 150ms, dot3: 300ms delay)
Typewriter: 30ms per character for setting narrative
Decision card select: scale(1.02) + primary border + checkmark fade-in
Reference Whisperer notification: gentle pulse on the sidebar icon (2s loop)
Stage transition: 400ms crossfade between simulation stages
Success checkmark: SVG path draw animation (600ms)
```

---

## PAGE-BY-PAGE SPECIFICATIONS

### Page 1: Login (`/login`)

**Layout:** Centered card on full-viewport dark background.

**Background:** `--neutral-950` with a very subtle grid pattern (1px lines at 5% opacity, 40px spacing). Optional: faint radial gradient (primary-900 at 10% opacity) behind the card.

**Card:** 420px wide, `--neutral-800` bg, `--radius-xl`, `--shadow-lg`. Padding 40px.

**Contents (top to bottom):**
1. **Logo mark** — Stylised "G" monogram or shield icon in `--primary-500`. 32x32px. Centered.
2. **Product name** — "GovernAI Studio" in `--text-2xl`, `--font-bold`, white. Below logo, centered.
3. **Tagline** — "Foresight, made practiceable." in `--text-sm`, `--neutral-400`, italic. 8px below name.
4. **Spacer** — 32px.
5. **Email input** — Full width. `--neutral-900` bg, `--neutral-200` border (1px), white text. Placeholder: "Enter your government email" in `--neutral-400`. Focus: `--primary-500` border + `--shadow-glow`. Height 48px. `--radius-md`.
6. **Submit button** — Full width. `--primary-500` bg, white text, `--font-semibold`, `--text-base`. Height 48px. `--radius-md`. Hover: `--primary-600` + translateY(-1px). Loading state: spinner icon replacing text.
7. **Privacy notice** — Below button, 16px gap. `--text-xs`, `--neutral-500`. Text: "Your data is private. We never share, score, or evaluate. [Privacy Policy]". Link in `--primary-400`.
8. **Footer line** — At bottom of card. `--text-xs`, `--neutral-500`. "Built as public-interest infrastructure for Indian governance."

**States:**
- Default: as described
- Loading: button shows spinner, input disabled
- Success: card content fades to "Check your email for a magic link ✉️" message with a subtle checkmark animation
- Error: red border on input, error text below in `--error`

---

### Page 2: Onboarding (`/onboarding`) — First-time only

**Layout:** Full viewport, centered content. Progress indicator at top.

**Progress bar:** 3 steps shown as dots connected by lines. Active dot: `--primary-500` (filled). Completed: `--primary-500` (filled + checkmark). Upcoming: `--neutral-600` (outline). Line between: `--neutral-700` default, `--primary-500` when connecting completed steps. Position: top center, 48px from top.

**Question cards:** Centered, max-width 560px. Each question animates in (slide-from-right, 300ms).

**Question 1 — "Where do you primarily work?"**
- Heading: `--text-xl`, `--font-semibold`, white. 
- Subtext: `--text-sm`, `--neutral-400`. "This helps us show you relevant scenarios."
- Options as selectable cards (not radio buttons): 4 cards in 2x2 grid. Each card: 
  - Size: equal width (fill grid), height auto (min 80px)
  - Default: `--neutral-800` bg, `--neutral-600` border (1px), `--radius-md`
  - Hover: `--neutral-700` bg, border `--neutral-400`
  - Selected: `--primary-500` border (2px), `--primary-50` bg at 5% opacity, checkmark icon top-right
  - Icon: Each option has a simple line icon (building for Central HQ, landmark for State Secretariat, map-pin for District, briefcase for PSU). Icon in `--neutral-300`, selected: `--primary-400`. 24x24px.
  - Label: `--text-base`, `--font-medium`, white
  - Sublabel: `--text-sm`, `--neutral-400`
- Options:
  1. Icon: building. Label: "Central Headquarters". Sublabel: "Ministry, department, or attached office"
  2. Icon: landmark. Label: "State Secretariat". Sublabel: "State government headquarters"
  3. Icon: map-pin. Label: "District or Field". Sublabel: "District, block, or frontline posting"
  4. Icon: briefcase. Label: "PSU or Regulatory Authority". Sublabel: "Public sector or regulator"

**Question 2 — "What is the main shape of your work?"**
- Same card style, 4 options in 2x2:
  1. Icon: file-text. Label: "Drafting, reviewing, or approving". Sublabel: "Policy, schemes, regulations, files"
  2. Icon: play-circle. Label: "Running programmes or pilots". Sublabel: "Mission-mode, project management"
  3. Icon: users. Label: "Field implementation". Sublabel: "Citizen interface, ground operations"
  4. Icon: help-circle. Label: "Other". Sublabel: "Doesn't fit the above"

**Question 3 (optional) — "Which domains are most relevant?"**
- Heading includes "(optional)" badge in `--neutral-500`.
- Options as pill-shaped toggles (multi-select). Wrap in a flex row.
  - Default pill: `--neutral-800` bg, `--neutral-600` border, `--radius-full`, padding 8px 16px
  - Selected pill: `--primary-500` bg, white text
  - Options: Procurement · Citizen services · Sectoral regulation · Cross-sectoral policy · Data & digital infrastructure · International & diplomatic

**Navigation:** "Continue" button bottom-right (same style as login submit). "Skip" link for Q3 in `--neutral-500`.

**Completion:** After Q3/Skip, brief animation — card fades out, replaced by "You're all set." message with subtle confetti-like particle effect (restrained, 1 second), then auto-redirects to dashboard in 1.5s.

---

### Page 3: Dashboard / Scenario Library (`/dashboard`)

**Layout:** Top nav bar + main content area.

**Top Navigation Bar:**
- Height: 64px. Background: `--neutral-900`. Bottom border: 1px `--neutral-800`.
- Left: Logo "GovernAI Studio" in `--text-lg`, `--font-semibold`, white. Logo mark (small G icon) in `--primary-500` before text.
- Right: 
  - Dark/light mode toggle (sun/moon icon, `--neutral-400`, 20px)
  - Settings gear icon (`--neutral-400`, 20px)
  - User avatar circle (initials from email, `--primary-500` bg, white text, 32px diameter, `--radius-full`)

**Welcome Section:**
- Full width, padding 48px horizontal, 32px vertical.
- Heading: "Your Scenarios" in `--text-2xl`, `--font-bold`, white.
- Subtext: "Choose a scenario to begin. Each takes about 35-45 minutes." in `--text-base`, `--neutral-400`.
- If officer has in-progress sessions, show a "Resume" banner: `--primary-900` bg with `--primary-500` left border (4px). Contains scenario title, progress stage, and "Resume →" button.

**Scenario Grid:**
- 3-column grid on desktop, 2 on tablet, 1 on mobile. Gap: 24px.
- Filter bar above grid: horizontal pills for domain filter. "All" (default selected) · Agriculture · Healthcare · Education · Smart Cities · Cross-cutting. Same pill style as onboarding Q3.

**Scenario Card Design:**
- Width: fill column. Height: auto (content-driven, min ~260px).
- Background: `--neutral-800`. Border: 1px `--neutral-700`. `--radius-lg`.
- Hover: border transitions to `--neutral-600`, `--shadow-md`, translateY(-2px).
- **Top section:** Domain tag pill (top-left corner, inside card, 12px from edges). Uses domain-specific color (e.g., `--domain-agriculture` green pill for agriculture scenarios). `--text-xs`, `--font-medium`, uppercase, letter-spacing 0.05em.
- **Title:** `--text-lg`, `--font-semibold`, white. Below domain tag, 16px gap. Max 2 lines, ellipsis overflow.
- **Description:** `--text-sm`, `--neutral-400`. 2-3 lines max, ellipsis. 8px below title.
- **Bottom section:** Horizontal divider (1px `--neutral-700`), then a row with:
  - Clock icon + "~35 min" in `--text-xs`, `--neutral-500`
  - If recommended: star icon in `--warning` + "Recommended" in `--text-xs`, `--warning`
  - If completed: checkmark icon in `--success` + "Completed" in `--text-xs`, `--success`
  - If in-progress: circle-dot icon in `--warning` + "In Progress" in `--text-xs`, `--warning`
- **Tags row (below divider):** Sutra pills in `--text-xs`. Show max 3 sutras as tiny neutral pills (`--neutral-700` bg, `--neutral-400` text). e.g., "Trust" "Accountability" "+1 more"

**Empty state (if somehow no scenarios):** Centered illustration + "Scenarios are being prepared. Check back soon." in `--neutral-500`.

---

### Page 4: Simulation — THE CORE EXPERIENCE (`/simulation/[session_id]`)

This is the heart of the product. It has 5 sub-stages that transition within the same page. The layout changes per stage.

**Overall simulation layout:**
- Full viewport height. No scroll on the outer container (content scrolls within panels).
- Top bar: Slim (48px height). `--neutral-900` bg. Shows:
  - Left: Back arrow (← with tooltip "Exit Scenario") + Scenario title in `--text-sm`, `--font-medium`, white
  - Center: Stage indicator — 5 dots representing Setting → Stakeholders → Decisions → Consequences → Reflection. Active dot: `--primary-500` filled. Completed: `--primary-500` with checkmark. Upcoming: `--neutral-600` outline. Connected by thin lines.
  - Right: Reference Whisperer toggle button (book icon, `--accent-violet`). Shows a subtle pulse notification dot when references are available.

Detailed specifications for each simulation stage are in Part 2.

---

**IMPORTANT NOTES FOR THE DEVELOPER:**
- NO scores, grades, percentages, leaderboards, or comparison metrics ANYWHERE in the UI
- NO "correct/incorrect" visual indicators on decisions — all choices are valid
- The word "test", "exam", "score", "grade", "pass", "fail" must NEVER appear
- Officer's tier (A/B) must NEVER be shown in the UI
- Every interactive element needs a unique HTML id for testing
- All text must be selectable (officers may want to copy references)
- Implement proper focus management for keyboard navigation
- Reduce motion mode must disable all animations
- Minimum touch target: 44x44px for mobile
