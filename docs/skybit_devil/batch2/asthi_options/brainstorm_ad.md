VERDICT: ITERATE

# ASTHI-DAKINI — brainstorm critique (5 VERSION directions)

Brainstorm-critique mode: judging the SET, not finish. The shared base
(necklace HERO gem brightest → third-eye → skull cyan → crown dimmest) is
sound and locked — I'm only judging whether the five skull-content/cyan
LANGUAGES are a genuine spread of "so whats," whether each truly individuates
its 12 skulls, and whether each survives 32px without breaking the ladder.

Bottom line: this is a strong, near-lockable set with ONE real distinctness
problem and ONE feasibility/scale flag. Four of five are confirmed as-is;
#1 serene-relic must be sharpened to stop bleeding into #5, or swapped. I'm
calling ITERATE (not SHIP-READY) for one reason: as proposed, the gentle pole
is double-covered and the set under-uses its most ownable lever. Apply the
fixes below and the five go straight into per-version loops.

---

## 1. Distinctness — ranking + the weak pair

Ranked by strength of an ownable, non-overlapping "so what":

1. **gem-eyed-oracle** — the only one that changes the SOCKET CONTRACT
   (pits become jewelled stares). That is a structural read, instantly legible,
   and unlike anything else in the set. Strongest direction; lead with it.
2. **wrathful-grin** — the clean opposite pole (snarl/fang/glare-out), and the
   only one whose differentiator is carried by SILHOUETTE (agape jaws, jagged
   sutures, brow cant). Survives 32px best of all five.
3. **verdigris-reliquary** — the only true MATERIAL-WORLD shift (bronze/patina
   vs icy jewel). Owns a hue territory (green-gold) no other version touches.
   Distinct, but its differentiator lives mostly in fine marks — see §4.
4. **dawn-lotus-court** — owns rose-gold + lotus-pink, a palette nobody else
   has, and the "auspicious/celebratory" register is a real third emotional
   pole between serene and wrathful. Confirmed.
5. **serene-relic** — the WEAKEST-differentiated. Its "so what" (calm,
   gentle, devotional consoler) substantially overlaps #5 dawn-lotus-court,
   whose register is ALSO calm/content/gentle. Both = soft jaws, no cracks,
   even teeth, low cyan socket glints, downcast-or-mild gaze. At 32px the two
   will read as the same brood with a palette swap.

**The weak pair: serene-relic (1) × dawn-lotus-court (5).** They collapse on
the EXPRESSION axis — both are "the gentle court." #5 only escapes because it
also re-tunes palette/ornament; strip that and it IS #1. That means #1 is
carrying its weight on a single, soft lever (lidded sockets + downcast glint),
which is exactly the cue most at risk of vanishing at gameplay scale (§4).

**Two ways to fix — pick one per the loop, I recommend A:**

A. **Push #1 to a genuinely different idea than "calm."** Keep ONE gentle
   pole (let #5 own it, since #5 also has the palette to make calm read). Re-cast
   #1 as **`ancestor-choir` / sleeping-then-singing**: not just lidded, but a
   COURT IN SONG — jaws softly OPEN in a sustained "aah" (rounded agape, no
   fangs, no cracks), eyes lidded/closed, heads tilted up-and-back. That gives
   #1 its own silhouette move (open soft jaws read at 32px, unlike lidded
   sockets which do not) and a distinct "so what" (devotional chant, not sleep)
   that no longer mirrors #5's content register. Cyan stays internal/pooled as
   proposed. This is my recommendation — it keeps a soft-pole direction while
   making it SILHOUETTE-distinct from both wrathful (open-but-fanged) and
   dawn-lotus (closed/content).

B. **If you'd rather not re-cast, swap #1 out entirely** for
   **`hollow-ascetic` / weathered-empty**: sockets deliberately, theatrically
   EMPTY and over-large (no cyan inside several of them at all), a few jaws
   fully cracked/missing — a stark, ascetic, near-skull-king severity. Its "so
   what" is *absence* (the renunciate), the opposite of #3's jewel-full stares,
   which sharpens BOTH directions by contrast. Cyan retreats to just the 2-3
   accent skulls, making the ladder trivially safe.

Either way: do NOT ship #1 as "calm/lidded/downcast" alongside #5. That is the
one duplication in the set.

---

## 2. Skull-content focus — real per-skull spread vs one-face-×12

The base already individuates the 12 via the `PROFILE` (palm) and
`CROWN_PROFILE` (crown) tables — cranium w/h, lean, jaw mode, tooth count,
suture, gem/pip, chip. So "12 distinct skulls" is achievable for every version
PROVIDED each version's language varies the RIGHT axis. Per direction:

- **gem-eyed-oracle (3):** strongest content spread — eye-set, gem size,
  one-eyed-vs-paired, gem-high-vs-low give 12 readable personalities. KEEP. Risk
  is the opposite: with jaws all kept mild "so eyes carry the read," the LOWER
  half of all 12 skulls goes uniform. FIX: let 2-3 jaws still vary (one cracked
  seer, one wide knowing grin) so the bottom half isn't a stamp.
- **wrathful-grin (2):** strong spread (roar width, which side cracked, snarl
  lean). KEEP. Risk: "every socket canted out + every jaw agape + every suture
  zig" is itself a stamp of MAXIMUM. FIX: vary INTENSITY — 2-3 full roars,
  several half-snarls, one clench-jawed silent fury — so it's a chorus, not 12
  identical screamers.
- **verdigris-reliquary (4):** spread = WHERE patina crept (one socket, a
  temple streak, a cranium crust). Good in principle, but this is the version
  most at risk of same-y skulls, because under neutral expressions the ONLY
  differentiator is small green marks that mush at scale (§4). FIX: make the
  patina vary the SHAPE read too — heavy bloom that visibly thickens/eats a
  socket rim or chips a jaw on the oldest 2-3, so erosion changes silhouette,
  not just colour.
- **dawn-lotus-court (5):** spread = which ornament-mark each carries (forehead
  lotus, tilaka dot, petal-tick) + tilt. Adequate at hero scale, weak at 32px
  (§4). FIX: anchor the spread to jaw/tilt variety (which already reads small)
  and treat the lotus/tilaka marks as hero-only flavour.
- **serene-relic (1) / its replacement:** if kept as calm, real per-skull
  spread is the hardest here because "uniform calm register" deliberately
  removes the loudest individuating cues (cracks, agape, fangs). This is more
  evidence for the §1 re-cast — the song/ascetic versions restore a varying,
  readable axis.

---

## 3. Value-ladder safety — guardrails per direction

The locked ladder is: **necklace HERO gem (faceted, white-hot core, largest)
→ third-eye (same gem, smaller, NO hot core) → skull cyan (dim, capped) →
crown cyan (dimmest, CYAN_D only).** The base enforces this in code: hero gem
`focal=True` hot-core ON; third-eye `focal=True, hot=False`; `palm_cabochon`
caps at CYAN_BR rim with NO white core; crown inlays are CYAN_D. Every version
must honor that ceiling. Specific risks:

- **gem-eyed-oracle (3) — HIGHEST risk, by design.** Up to ~24 cyan stones in
  the skulls. The danger is not any single stone out-bright the hero, but
  AGGREGATE cyan MASS pulling the eye away from the necklace and flattening the
  focal hierarchy. Guardrails: (a) every gem-eye capped at CYAN_BR rim, NO
  white-hot core — only the hero gem and (a step down) the third-eye get the
  white core; (b) most gem-eyes use CYAN_D bodies; only the 2-3 accent skulls
  go to full CYAN; (c) keep gem-eyes SMALL — none may approach the hero's
  faceted size; quantity, not brightness. (d) Hold total cyan COVERAGE down by
  making several skulls one-eyed/dark-socket so the field isn't wall-to-wall
  cyan. If the necklace gem doesn't still win instantly at 32px, pull gem-eye
  count or value, not the hero.
- **wrathful-grin (2) — moderate.** "Burning embers" tempts a hot core. Hard
  rule: ember tops out at CYAN_BR upper-rim glint, NO white core. The flare
  read comes from SOCKET SHAPE (wide canted oval) + the dim CYAN_D ember, not
  from brightness. Accent only the ~3 lead snarls.
- **verdigris-reliquary (4) — lowest risk, but check the opposite.** Green-
  shifted matte cyan is dim by construction; safe. WATCH that the bronze-
  verdigris pips don't drop so dark they kill the hue-separation the GOLD pips
  currently provide on ivory (the base relies on gold-on-ivory for colourblind-
  safe separation). Verdigris on warm ivory must keep a clear VALUE step too,
  not lean only on the green hue.
- **dawn-lotus-court (5) — low, with one trap.** Rose-gold bezels are warm/dim;
  fine. The trap is the LOTUS-PINK secondary: keep it strictly low-sat, small,
  and below the cyan in value, or a bright pink petal becomes a second focal
  competing with the cyan blessing-drop. Pink is an accent tick, never a fill,
  never near the third-eye in value.
- **serene-relic / replacement (1) — safe.** Internal socket pools capped at
  CYAN_BR rim. If recast to `hollow-ascetic`, even safer (less cyan).

Universal guardrail for all five: the WHITE-HOT CORE is reserved for the hero
gem (and is dropped one step for the third-eye). No skull — palm or crown,
oracle or wrath — ever gets a white core. That single rule keeps the ladder.

---

## 4. Two-scale — what survives 32px vs hero-only flavour

This is where the set is uneven. Cues that read at 32px are SILHOUETTE
(open/closed/agape jaw, socket size, cranium lean, missing teeth) and VALUE
(is there a bright cyan dot or not, light vs dark mass). Cues that DON'T survive
are fine incised lines, suture style, thin rim-blooms, small petal/tilaka marks.

- **wrathful-grin (2):** differentiator is silhouette+value (agape, glare-out,
  cracks). SURVIVES best. No worry.
- **gem-eyed-oracle (3):** differentiator is VALUE (cyan dots where pits were).
  Survives — the eye reads "stones, not holes" even tiny. Gem-set vs dark-socket
  reads as a value pattern at 32px. Good. Just don't rely on gem-SIZE alone to
  distinguish skulls (size deltas vanish small); back it with one-eyed-vs-paired
  (a value/asymmetry cue that survives).
- **serene-relic (1) as proposed:** WORST at scale. "Narrow lidded crescent
  sockets" + "downcast inward glint" are exactly the sub-pixel cues that mush —
  at 32px a lidded socket and a normal dark socket look identical, and downcast
  vs centred glint is invisible. The serene read would simply not exist in
  gameplay; it would look like the base with dimmer eyes. This is the
  feasibility case for the §1 re-cast (open soft jaws / over-large empty
  sockets BOTH read as silhouette).
- **verdigris-reliquary (4):** the patina (green crust, temple streaks, rim-
  bloom) is HERO-ONLY flavour — beautiful in the showcase, gone at 32px. For
  this version to survive small it must push the green into a VALUE/silhouette
  read: noticeably darker, blotchier sockets and a visibly green-shifted overall
  cast (the whole figure reads cooler/older as a mass), plus erosion that
  changes a couple of silhouettes (§2). The fine crust is bonus, not the read.
- **dawn-lotus-court (5):** incised lotus marks, tilaka dots, petal-ticks,
  daintier bead lattice = ALL hero-only flavour. At 32px this version must read
  via (a) the overall WARM rose-gold cast vs everyone else's cool ivory, and
  (b) the single cool cyan blessing-drop punching against that warmth. The
  warm-vs-cool palette contrast is the only thing that survives — design it to
  carry the version, treat the petal marks as close-up delight.

Net: two versions (4, 5) and the as-proposed #1 lean on hero-only cues. #4 and
#5 are salvageable because each ALSO owns a palette/value cast that survives;
#1 has no such fallback, which is the third reason to re-cast or swap it.

---

## 5. Final recommendation — the 5 to pursue + sharpened per-version briefs

Confirm the set of 5, with #1 RE-CAST (recommendation A) — no merges, no other
swaps. The two gentle poles are de-duplicated by giving #1 a song/ascetic
identity and letting #5 own "calm + auspicious." Sharpened one-line briefs for
each per-version loop:

1. **`ancestor-choir`** (recast of serene-relic) — a devotional court mid-CHANT:
   soft ROUNDED-AGAPE jaws (open, no fangs, no cracks), lidded/closed eyes,
   heads tipped up-and-back; cyan pooled INTERNALLY in sockets (capped CYAN_BR
   rim), brighter at the heart of the fan. Differentiator must be the
   open-soft-jaw silhouette (reads at 32px), not lidded sockets.
   *(If you reject the recast, swap to `hollow-ascetic`: over-large EMPTY
   sockets, several cracked/missing jaws, cyan only on 2-3 accent skulls.)*

2. **`wrathful-grin`** — fierce charnel chorus: wide canted-out oval sockets,
   agape fanged roars, jagged `zig` sutures, temple cracks; vary INTENSITY
   (full roar / half-snarl / clenched fury) so it's a chorus not a stamp. Cyan =
   wrath-fire ember, CYAN_BR rim glint MAX, NO white core, ~3 lead snarls hotter.

3. **`gem-eyed-oracle`** — the seer court: sockets become gold-bezel cyan
   cabochon STARES; individuate via eye-set, one-eyed-vs-paired, high/low, size;
   let 2-3 jaws still vary so the lower half isn't uniform. Hardest ladder job:
   many SMALL stones, all capped CYAN_BR rim (no white core), aggregate cyan
   mass held under the necklace hero — pull count/value if the hero stops
   winning at 32px. Strongest direction; lead the showcase with it.

4. **`verdigris-reliquary`** — the dug-up ancient: bronze-verdigris pips/bezels
   (keep a VALUE step + hue separation, don't rely on green hue alone), matte
   green-shifted cyan as mineral bloom, the only LIVING jewels are the icy hero +
   third-eye. Make erosion change SILHOUETTE on the oldest 2-3 (eaten socket
   rim, chipped jaw); push an overall cooler/older cast so the version reads at
   32px, not just via fine crust.

5. **`dawn-lotus-court`** — the auspicious sunrise: rose-gold bezels + sparing
   low-sat lotus-pink accent (tick, never fill, below cyan in value); incised
   lotus/tilaka as hero-only flavour. The version must read small via the WARM
   cast vs everyone's cool ivory + the single cool cyan blessing-drop punching
   against it. Anchor per-skull spread to jaw/tilt (survives), not the marks.

Run all five per-version loops on the locked base. The non-negotiable shared
guardrail across every loop: white-hot core = hero gem only (one step down for
the third-eye); no skull ever gets it.

## References
- For "jewel-eyed skull reads small without going wall-to-wall bright,"
  benchmark Día-de-Muertos calavera UI (e.g. Grim Fandango / Guacamelee menu
  skulls) where socket-jewels stay contained and the hero accent still wins.
- For wrath-vs-serene as a silhouette (jaw/socket) read at icon scale, the
  Tibetan citipati/mahakala mask vocabulary is the right grammar source — keep
  it bone-grammar, not cartoon-face, exactly as the base already does.
