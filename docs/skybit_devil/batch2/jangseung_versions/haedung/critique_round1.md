# AD critique — Haedung (fire-eating guardian-lion totem-post) — ROUND 1

**VERDICT: ITERATE**

Strong, characterful first pass that lands the house style and is clearly its own
creature — but the single defining gag (the fire-EATER flame-curl) is failing the
1x read by fusing into the ember maw, and a too-bright gold bell is stealing the
warm focal. Fix the flame separation + tame the bell and this ships.

---

## Ranked notes (most important first)

### 1. THE flame-curl is invisible at 1x — fix it or the concept's soul is lost (FIX, top priority)
The whole hook is "fire-EATER": a carved flame licking from ONE mouth corner. Right now
the curl is the **same ember-orange `(238,128,64)` as the maw interior**, sits directly
against the maw, and has no dark gap — so at true 32px (and even in the day chip) it just
reads as a slightly lumpy mouth corner, not a flame. The GD flagged this correctly; my
ruling: **it does NOT read.** Concrete fix, do all three:
  - Insert a **hard ink-keyline gap** `(28,22,30)` between the maw rim and the flame-curl
    so they are two separate shapes, not one blob.
  - **Chunkier curl** — make it one bold comma-lobe ~30–40% taller than current, with a
    single clear hook, lifted clear of the lip line so its silhouette breaks the mouth
    outline (a flame should bite into the negative space above the corner).
  - Give the flame a **2-value tip**: hot core `(238,128,64)` + a brighter cream-yellow
    tongue-tip so it out-values the maw and becomes the eye's second stop after the eyes.
  - Keep it on ONE corner only (brief-correct now — don't let it become symmetric).

### 2. The gold bell is over-bright and competes with the ember maw for the warm focal (FIX)
The bell/chest plate under the mouth is currently a large, high-key yellow mass with its
own internal glow — at 1x it's actually **brighter and bigger than the ember maw**, so the
focal hierarchy inverts: the eye goes to the chest, not the face. The ember mouth (with its
flame) must be the single warm focal.
  - Drop the bell's value/saturation ~20–25% and shrink its lit area; let it be gold
    `(222,184,86)` hardware, not a second light source.
  - Reserve the brightest warm value for the **ember maw + flame** only.

### 3. Eyes — re-spec compliance is GOOD, hold it (KEEP)
Simple round bug-eyes with a SINGLE carved ring read clean — no concentric goggle stack,
clear of Tlaloc. The thick ink keyline + warm-cream catchlight survives the night chip well.
Keep exactly as is. One micro-note: the cream eye-ring is very high-key and the brightest
white in the piece; if after fix #2 the eyes still out-pull the maw, knock the ring
cream down a hair so the mouth wins the focal.

### 4. Brow-horn reads as a flat plug, not a horn — give it dimension (FIX, minor)
The ONE stubby center brow-horn (correct — single, no pair) currently reads as a flat
trapezoid tab between the eyes. Add the standard triad (dark-core → flat-fill → top-left
rim-sheen) and a slight taper so it reads as a carved nub in the round, not a sticker.
Keep it stubby and centered.

### 5. Mane lobes are slightly too many / too even — push toward "sparse ring of ~6" (FIX, minor)
The curl-lobe ring is reading closer to 8–9 evenly-packed beads and edges toward "noise
ring" at 1x rather than "6 bold carved lobes." Cull to ~6 chunkier lobes with a hair more
gap between them so each lobe is a distinct silhouette bump. This also helps the mask not
feel quite so wide/top-heavy (see #6).

### 6. Pillar mirror + weight — clean, but mask is a touch top-heavy (KEEP w/ small FIX)
Mirror cap is clean, bottom-rooted, and the scaled cedar column reads as a proper tall body —
good. The fish-scale courses survive downscale as repeat texture (nice). However the wide
lion-mask + full mane ring slightly overweights the top third; the column wins but only just.
Trimming the mane to 6 lobes (#5) plus keeping the bell quieter (#2) will rebalance it.
Don't widen the mask further.

### 7. CROSS-SET PIN — jade is compliant (KEEP)
Jade `(72,150,118)` stays a blue-leaning SCALE-BAND course + mane-tip flecks; it is NOT a
body fill and reads as placed accent, not a second mass. Eye glow is warm amber/cream only —
no cool glow borrowed. Distinct from the slate-wood + cinnabar source Jangseung (different
wood tone, different face, different accent placement) and clearly separable from the other
four briefs. Hold this discipline.

### 8. House-style fidelity — MATTE wood is correct (KEEP)
No glaze/crackle/kiln sheen — reads as matte carved cedar, clear of Zhenmushou. Flat triad +
hard ink keyline + 1px outline all present. Elevated/epic, not grim. Good.

---

## Iteration directives (punch list)
1. Separate the flame-curl from the maw with a hard ink gap; make it ONE chunky comma-lobe,
   taller, breaking the mouth's top silhouette, with a cream-yellow hot tip.
2. Drop the gold bell ~20–25% value/sat and shrink its lit area — ember maw + flame is the
   ONLY warm focal.
3. Add triad shading + taper to the single brow-horn so it reads as a carved nub.
4. Cull mane to ~6 bolder, slightly-spaced curl-lobes.
5. Re-shoot the day AND night 32px chips after the above — the flame-curl must be legibly a
   FLAME at 1x on both. That chip is the acceptance test for ship.
6. Hold everything else: eyes, jade scale-band, matte wood, warm-only glow, clean mirror.
