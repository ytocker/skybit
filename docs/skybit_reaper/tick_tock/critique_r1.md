# TICK-TOCK — Art-Director Critique, Round 1

`VERDICT: ITERATE`

Round 1 has a genuinely strong PROP and a smart prop->pillar mirror — but the
BOSS itself has slid right back into the exact failure the brainstorm was
written to correct: it reads dark, desaturated, and grim at showcase scale, and
near-illegible at 1x. The hourglass is shippable-adjacent; the figure carrying
it is not. This is fixable in one round, but the fixes are not cosmetic — the
robe value/saturation and the silhouette read are load-bearing.

---

## Ranking of this round's elements (strongest -> weakest)

1. **The hourglass-staff prop (b, pillar pair)** — STRONGEST. The pinch-waist
   eye at the gap-edge with a clean brass post and ferrule banding is a bold,
   ownable tiling silhouette. This is the thing that's working. Keep it.
2. **The hourglass head on the boss (a)** — Good. Bright amber/brass, the one
   place the palette actually sings. It's also the only high-chroma mass on the
   whole figure — which is the problem (see below).
3. **The smug face** — Promising construction (half-lids + arched brow + cocked
   mouth) but it's drowning: too small, too low-contrast inside a near-black
   cavity, and at 1x it's gone entirely.
4. **The robe / hood mass** — WEAKEST. Reads as a dull dark-navy slab, not bold
   saturated teal-blue. This single failure sinks HOUSE-STYLE FIDELITY,
   SCARY-CUTE, and 1x LEGIBILITY at once.

---

## Against the rubric

### 1. HOUSE-STYLE FIDELITY — MISS (the headline problem)
The robe is rendering as a muddy dark slate/navy, not the "BOLD saturated
teal-blue" the spec mandates. Two things are conspiring:
- **The base ROBE `(43,86,110)` is already a fairly dark, low-chroma teal.** On
  a 360x640 phone it needs to be a confident mid-value teal that POPS, not a
  twilight navy. It currently sits at roughly the same value as the night sky.
- **The triad is being applied too dark.** `_shade_c(col,-55)` for both the
  dark-core keyline AND a 2-2.4px poly border means the figure is ringed and
  cored in near-ink, so the flat fill barely gets to speak. Combined with the
  full `_add_outline` pass on top, the body is mostly edge-darkness. The result
  reads "semi-realistic desaturated hood" — the prior round's exact sin.

This is the one note that matters most: **the robe must read as a punchy,
saturated teal that a player would call "blue-green," not "dark grey-blue."**

### 2. SCARY-CUTE MENACE — PARTIAL MISS
The smug-clerk INTENT is in the code (half-lids, oh-really brow, cocked smirk),
but none of it survives to the eye. At showcase scale the face is a pale smudge
in a black hole; the charm beat is invisible. Right now the figure reads as a
generic grim hooded wizard/monk, which is precisely the "just a wizard, not
Death-but-cute" trap the guardrail named. The character is in the face — so the
face has to be bigger, brighter, and contrastier.

### 3. PROP->PILLAR — PASS (the win)
The pillar pair (b) is the clear success: pinch-waist eye at the gap, full-height
brass post, ferrule banding that gives a tileable mid-section rhythm. The eye
silhouette is distinct and unmistakably "hourglass." Minor: the two piers' eyes
are slightly different widths than the boss's staff hourglass — unify the
half-width ratio so the "one literal shape" promise holds at a glance.

### 4. 1x LEGIBILITY — MISS (esp. NIGHT)
This is where round 1 fails hardest. In the DAY inset the figure is a dark blob
with an amber dot; the smug face, sash, clasp, and hands are all gone. In the
NIGHT inset the teal robe nearly merges INTO the night sky — the only things
holding the silhouette are the outline and the amber hourglass. A Death boss
that disappears into a night biome is not shippable. The amber hourglass is
currently doing 90% of the legibility work; the BODY needs to carry its own
share via value contrast.

### 5. DISTINCTNESS — PASS
The squat-trapezoid + tall-hourglass-staff silhouette stays clearly distinct
from Grim Sprout (tiny imp), Big Reapy (giant skull), Dr. Quill (beak), and The
Hollow (broad void-hood). No collision. The hourglass prop is uniquely owned.

### On the GD's flagged behind-the-back arm — I OVERRULE the concern, with a fix
The GD worried the behind-back arm reads as "a floating slab rather than a
clasped-behind tell." Looking at the render: the viewer-LEFT shape that's
floating and reading as a slab is the CRADLING-arm sleeve / mitt region near the
staff, not the behind-back nub — the nub itself (`_shade_c(ROBE,-18)` at the far
hip) is actually fine and correctly subtle. The real culprit is a low,
detached-looking dark lobe on the figure's left that doesn't connect to the
shoulder. So: keep the behind-back nub as-is, but re-seat the CRADLING arm so it
visibly springs from the shoulder and clasps the pole as one continuous sleeve.
Don't over-correct the nub into a bigger shape — that would weaken the
"hands-clasped-behind" smug tell.

### 7. ACCESSIBILITY — AT RISK
Per the guardrail, the face read currently depends almost entirely on the amber
hourglass for "where to look." Desaturate the sheet to grayscale and the body is
a flat dark mass with no internal read. The fixes below (lift robe value, brighten
the face crescent, strengthen the sash) all serve grayscale legibility too.

---

## KEEP
- The hourglass-staff prop and its pillar mirror — the pinch-eye + banded post.
- The smug-face CONSTRUCTION logic (half-lid bar, arched brow, cocked-corner
  smirk). Right idea; just buried.
- The scalloped chibi hem and the brass-clasp-on-rose-sash detail (when visible).
- The draining sand on the boss's glass (sand_t=0.34) vs balanced on the pillars
  — nice storytelling touch ("he flipped YOUR glass").

## FIX (the next-round punch list, prioritized)

1. **LIFT THE ROBE OFF THE FLOOR — saturated, mid-value teal.** Raise ROBE to a
   confident blue-green (push toward roughly `(38,120,150)`-ish — brighter and
   more chroma than the current `(43,86,110)`). The robe must read clearly
   BLUE-GREEN, not dark-navy, and must sit a solid value-step ABOVE the night
   sky so it never merges. This is the single highest-priority change.

2. **STOP DOUBLE-DARKENING THE FILLS.** You have `_shade_c(col,-55)` doing both
   the dark-core ring AND a 2-2.4px keyline, THEN a full `_add_outline` pass.
   That's three layers of darkness eating the flat fill. Thin the internal poly
   keyline (1px, or drop it where the silhouette outline already covers it) and
   let the bright flat fill dominate the mass. House style is FLAT-fill-forward
   with a crisp single ink line — not an inked-and-cored slab.

3. **MAKE THE FACE WIN AT 1x.** Enlarge the face crescent ~20-25% and lift the
   inner-hood cavity from near-black `_shade_c(ROBE_DK,-22)` to a clearly
   readable dark teal so the bone-cream face reads as a bright shape against a
   dark-but-colored recess (not a black hole). Confirm the smug half-lid + smirk
   survive at the 1x inset size — if not, simplify to: two half-lid sliver eyes +
   one cocked mouth line, drop the nose-bridge tick (it's noise at 1x).

4. **PUSH THE FOCAL HIERARCHY: face first, hourglass second.** Right now the
   amber hourglass out-shouts the face and steals the read. Either nudge the
   hourglass glow alpha down slightly, or (better) raise the face/sash contrast
   so the head wins the eye first and the glass is the supporting beat. The
   character is the clerk's SMIRK, not the prop.

5. **STRENGTHEN THE SASH AS A VALUE BREAK.** The rose sash `(214,62,90)` is a
   great mid-body horizontal that breaks the tall dark mass — but it's barely
   visible. Make it read clearly at showcase scale; it's your warm accent and a
   key legibility band across the waist. Confirm it survives at 1x.

6. **RE-SEAT THE CRADLING ARM** so it springs from the shoulder as one
   continuous sleeve to the pole (kills the floating-slab read on the figure's
   left). Leave the behind-back nub alone.

7. **UNIFY THE HOURGLASS HALF-WIDTH** between the boss's staff and the two pillar
   piers so the "one literal shape" mirror reads identical at a glance.

8. **RE-CONFIRM IN GRAYSCALE.** After 1-5, desaturate the sheet: the figure
   should still read as Death-clerk-with-hourglass on value alone, face included.

---

## References
- Skybit's own `docs/warren_clown/round_17_final.png` is the fidelity north star:
  note how the warren clown's fills are BRIGHT and saturated, with the ink line
  as a crisp single edge — the body mass reads as confident flat color, not a
  dark inked slab. Match that fill-forward punch.
- For the night-sky-merge problem: the rule is value separation from the biome.
  The robe must sit a clear value step above NIGHT_BOT `(35,55,115)` — right now
  it doesn't.
