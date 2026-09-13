---
name: distinct-design-variants
description: >-
  Non-negotiable rules for producing multiple design variants / a candidate
  "options" sheet (e.g. "give me 5 designs", "explore N concepts"). Enforces that
  each variant is a UNIQUE, bottom-up design — never the same base with a changed
  pose, colour, accessory, or proportion. Use whenever a brief asks for N distinct
  visual concepts/options for a character, prop, icon, logo, sky, pillar, ground,
  power-up, or any visual. Applies to graphics-designer candidate sheets and any
  design-loop round.
---

# Distinct Design Variants — the doctrine

When a brief asks for **N options / concepts / variants**, the deliverable is
**N genuinely different designs**, each conceived and built from the ground up.
Five variants = five separate design efforts, **not one design shown five ways.**

## The hard rule
Each variant MUST differ in **KIND, not in finish.** Every variant differs from
every other in **all** of these at once:
- **Core concept / thesis** — a different idea of what this thing *is*.
- **Silhouette** — recognisably different as a solid black shape.
- **Construction / anatomy** — its own proportions and structure (ideally its own
  builder + primitives), not a shared base body re-dressed.
- **Shape language** — e.g. round vs. angular vs. jagged vs. tall-gaunt vs. squat.

## Banned as "a different design" — these are the SAME design
A variant is INVALID if the only thing separating it from another is:
- recolour / palette swap
- a changed **pose**, gesture, camera, flip, or mirror
- adding / removing an **accessory** or prop
- **scaling** up/down or stretching proportions
- a single swapped **feature** (hat, collar, mouth) on an otherwise shared body
- reusing **one base build function** with different parameters

> If you could turn variant A into variant B by recolour + repose + swapping an
> accessory, they are ONE design. Kill one and invent a real alternative.

## Required process (bottom-up, in order)
1. **Concepts first.** Before drawing, write N one-line theses that differ in kind.
   If two theses are paraphrases of each other, delete one and invent a new one.
2. **Build each independently.** Author each variant from its own construction.
   Do NOT parameterise a single base body into the set. Shared *low-level* helpers
   (a line, a gradient, a bevel) are fine; a shared *figure/body/silhouette*
   builder is not.
3. **Self-audit** against the tests below.
4. **If you run dry, widen the search** (fresh references, new shape language) —
   never pad the set with near-duplicates to hit the count.

## How this runs in the design loop (orchestrator)
Distinctness is won at the **brainstorm**, before anything is rendered, then
protected while each concept matures on its own — never by rushing N finals into
one sheet. Per CLAUDE.md's Design loop "Multiple concepts" flow:

1. **Brainstorm the directions (GD↔AD).** `graphics-designer` proposes the N
   theses + their silhouette / construction / shape language (the bottom-up step
   above, no full render); `art-director` runs the distinctness gate on the SET
   (the tests below) and culls any look-alikes before a single full render happens.
2. **Mature each concept in its own loop.** Each locked concept gets its own full
   designer↔critic loop and its own `docs/<feature>/<concept-slug>/round_N.png`.
   The tests still apply across the maturing set — a concept that drifts into
   another's territory gets corrected, not shipped as a near-twin.
3. **Showcase all N at the end** for the user to choose.

So the tests below run on the **set of concept directions** (and are re-checked on
the finals) — not on a single combined options sheet.

## Distinctiveness tests — run ALL before delivering
- **Blackout test:** fill each variant solid black. All N must read as clearly
  different shapes. Any two that match are duplicates — replace one.
- **Swap test:** can variant A become variant B via recolour + repose + accessory
  swap? If yes, they are the same design.
- **Cover-the-label test:** with captions hidden, a stranger can tell the variants
  apart and describe each differently.
- **One-sentence test:** each variant has its own thesis sentence; no two are
  rephrasings.

A round that fails any test is **not deliverable** — fix it before handing back.

## What MUST stay the same
Only the **subject's identity** the brief fixes: same character/IP lineage, same
project art rules (e.g. procedural-only, no asset reuse, the stated palette
family). Sameness of *subject* is required; sameness of *design* is the exact
failure this skill exists to prevent.
