---
name: council-this
description: "Multi-persona decision council: spawns 5 parallel expert agents, runs anonymous peer review and delivers a chairman synthesis as an interactive HTML report. Use when the user says \"council this\" followed by a strategy, hiring or high-stakes decision."
---

# Council This: multi-persona decision maker

Trigger: when the user types "council this" followed by a question or decision.

---

## Process

### Step 1: validate input

If the user provides less than 20 words of context, ask for more before spawning agents. Good decisions need good inputs.

### Step 2: spawn the council (parallel)

Spawn all 5 agents simultaneously using the Agent tool. Pass each agent the full question/context the user provided. Every agent must return a structured response with: verdict (one sentence), reasoning (3 bullet points max), risk flag (if any), and recommended action.

**1. The Researcher**
Prompt prefix: "You are a rigorous analyst on a 5-person decision council. Your job is to examine this question with evidence-first thinking. What do we actually know? What assumptions are being made? What data is missing? Be specific. No speculation without flagging it. If the user has a CLAUDE.md describing who they are and their constraints, include that context."

**2. The Sceptic**
Prompt prefix: "You are a constructive sceptic on a 5-person decision council. Your job is to stress-test this decision. What could go wrong? What's being overlooked? What's the strongest case AGAINST the leading option? Push hard, but be specific, not vaguely negative."

**3. The Strategist**
Prompt prefix: "You are a long-term strategist on a 5-person decision council. Your job is to zoom out. How does this decision look in 12 months? 3 years? What are the compounding effects, positive and negative? What's the highest-leverage move? Think about where the user is trying to get to, from what they have told you."

**4. The Operator**
Prompt prefix: "You are a practical operator on a 5-person decision council. Your job is to focus on execution. What does implementation actually look like? What are the real blockers? What would this cost in time, money, and focus? What's the fastest path to a result?"

**5. The Creative**
Prompt prefix: "You are a lateral thinker on a 5-person decision council. Your job is to find the option nobody's considered. Is there a third path? A reframe? An unconventional approach that sidesteps the original tension entirely? Be bold but grounded."

Each agent prompt must end with: "Return your response in this exact format: VERDICT: [one sentence]. REASONING: [3 bullet points]. RISK FLAG: [one sentence, or 'None']. RECOMMENDED ACTION: [one sentence]."

### Step 3: peer review round

After all 5 agents complete, run a second round. Label the 5 responses anonymously as Member A through E (randomise which role maps to which letter). Spawn one agent that receives all 5 anonymised responses and performs the peer review:

Prompt: "You are reviewing 5 anonymous council member responses to this decision: [question]. Here are their positions: [A through E]. For each member, write one sentence on what you agree with and one sentence on what you'd challenge. Be direct. Then identify the strongest tension or disagreement across the group."

### Step 4: chairman synthesis

After peer review completes, write the chairman synthesis yourself (do not spawn another agent). The synthesis must:

1. Name the core tensions between the five perspectives
2. Identify the strongest 2-3 options with clear reasoning for each
3. Make a concrete recommended next step (even if that step is "gather more information on X before deciding")
4. Flag any deal-breakers raised by the Sceptic or Operator
5. Give a confidence rating: HIGH / MEDIUM / LOW with one-line justification

### Step 5: build the HTML report

Generate a single interactive HTML file saved to: `council-reports/[slug]-[YYYY-MM-DD].html`

Then open it in the browser.

---

## HTML report specification

### Design system

| Token | Value |
|---|---|
| Background | #1C1A1D (INK) |
| Accent | #E2F075 (LIME) |
| Text primary | #FFFFFF |
| Text secondary | #A0A0A0 |
| Card background | #2A2830 |
| Card border | 1px solid #3A3840 |
| Border radius | 12px |
| Font stack | 'Inter', system-ui, sans-serif (load from Google Fonts) |

### Layout

Single-page, responsive, no external dependencies beyond Google Fonts. CSS grid or flexbox. Mobile-first.

### Sections (top to bottom)

1. **Header**: the question in large type, date, "Council Report" subtitle
2. **Council verdict strip**: 5 small cards in a row, each showing the member SVG icon, role name, and one-sentence verdict. Colour-code borders: green (#4ADE80) if recommending action, amber (#FBBF24) if cautious, red (#F87171) if against
3. **Council member cards**: 5 expandable cards (collapsed by default, click to expand). Each card shows: role name, SVG icon, verdict, 3 reasoning bullets, risk flag, recommended action. Subtle expand/collapse animation (max-height transition)
4. **Peer review section**: the anonymised cross-review, styled as a conversation thread with alternating slight background tints
5. **Chairman synthesis box**: bordered with LIME accent (2px left border). Contains: core tensions, top options, recommendation (in a callout box with LIME background at 10% opacity), deal-breakers, confidence rating badge
6. **Next steps**: bulleted action list extracted from the recommendation, each with a checkbox (cosmetic, not functional)

### Interactivity

- Expand/collapse council cards (JS toggle with aria-expanded)
- Smooth scroll navigation (anchor links in a sticky mini-nav bar at top)
- Print-friendly: `@media print` stylesheet that removes dark backgrounds, uses black text on white
- Timestamp in footer
- "Copy summary" button that copies the chairman synthesis to clipboard

### SVG icons (inline, no external library)

- Researcher: magnifying glass
- Sceptic: shield
- Strategist: chess knight
- Operator: gear/cog
- Creative: lightbulb

---

## Rules

- All 5 council agents must run in parallel (not sequential)
- Each agent gets the same question and context, nothing more
- Peer review uses anonymous labels (A-E), never role names
- The chairman synthesis is written by you (main context), not delegated
- Report file path format: `council-reports/[slug]-[YYYY-MM-DD].html` where slug is the first 6 words of the question, lowercased, hyphenated, no special characters
- Open the report in the default browser after saving
- Time estimate: ~3-4 minutes for the full council process
