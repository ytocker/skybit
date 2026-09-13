# /design — Visual concept exploration

Invoked as `/design [brief]` for any task that designs or restyles a visual in Skybit.
Run all phases straight through with no mid-session checkpoints.

---

## Phase 1 · Brainstorm — graphics-designer (Opus)

Brief the `graphics-designer` agent:
- What is being designed (feature, context, what the current version looks like if it exists)
- Game visual DNA reference points (e.g. game/store_cards.py, game/draw.py)
- The `distinct-design-variants` skill constraints apply: concepts must differ in kind
  (core concept, silhouette, construction, shape language) — not just palette or finish
- Deliver 5 concepts. For each: slug, one-sentence thesis, construction/silhouette note,
  player-delight hook ("why would a player screenshot this?"), feasibility note
- No renders yet. Mark top 2–3 picks.

## Phase 2 · Brainstorm critique — art-director (Opus)

Hand the 5 directions to `art-director`:
- Critique for: visual clarity, Skybit identity fit, layout feasibility, distinctiveness
- First line: VERDICT: PROCEED or VERDICT: REWORK [slugs]
- On REWORK: one-line replacement direction per flagged slug

## Phase 3 · Lock 5 concepts — graphics-designer (Opus)

Feed art-director critique back to `graphics-designer`:
- Revise any flagged directions; keep approved ones unchanged
- Deliver the locked 5 concept slugs + design briefs (one paragraph each)

---

## Phase 4 · Design loop — 5 concepts in parallel

Launch all 5 concept triplets in a single message (up to 15 agents, 5×3).

### Step A — Round 1: graphics-designer (Opus)
For each concept: render; save to `docs/<feature>/<slug>/round_1.png`; commit + push.
Distinctness constraints from the `distinct-design-variants` skill apply.

### Step B — Critique: art-director (Opus)
For each concept: standard per-concept critique. First line: VERDICT: SHIP-READY / ITERATE / RE-ROLL.

### Step C — Round 2 (final): graphics-designer (Sonnet)
For each concept: implement the art director's notes regardless of VERDICT (this is always the
last pass); save to `docs/<feature>/<slug>/round_2.png`; commit + push.

Run all 5 Step A agents → then all 5 Step B → then all 5 Step C.

---

## Phase 5 · Showcase comparison figure — orchestrator

The main session renders `docs/<feature>/showcase.png`:

1. Original panel (if it exists): check for `docs/<feature>/original.png` or render the
   current in-game state headlessly. If found, include as the leftmost panel labeled "BEFORE".
2. Five concept panels: load each `docs/<feature>/<slug>/round_2.png`, crop to the primary
   state, scale to 200 × 355 px.
3. Canvas: (8, 8, 20) background; 200 × 355 panels; 8 px gaps; 20 px margins;
   40 px header; 32 px footer per panel (slug name + SHIP-READY or FINAL).
4. Save to `docs/<feature>/showcase.png`, commit + push.
5. Post the GitHub blob URL in chat.

The orchestrator (main session) runs on **Sonnet**.
