# ART-DIRECTOR CRITIQUE — A5 PYRECROWN — round 1

VERDICT: ITERATE

PYRECROWN has a genuinely strong CORE: the serene closed-eye priest-skull is
charming and eerie-cute exactly as briefed, the grayscale read proves the face +
black tapers carry the silhouette without leaning on the green, and it owns
Group A's only-green / only-serene lane cleanly. It does NOT collide with
Glitchfiend's neon (the flame is a contained flat teardrop + tight outside halo,
not a wash) or Baalgoat's warm torch (it's green and multiplied, not a single
gold brazier). The concept is a keeper. But this round does not ship: the
showcase is broken, the crown reads as a MOHAWK not a candle-crown, the candles
LEAN THE WRONG WAY, and the prop->pillar payoff (skull-knob + green flame
LIGHTING the gap) is missing from the one cell that's supposed to prove it.
Fixable in a pass — iterate.

---

## RANKING — strongest to weakest aspect

1. **STRONGEST — the serene skull face + grayscale read.** Closed-eye lash
   crescents, heart-nose, quiet tooth band, calm bone brow: this is the eerie-CUTE
   priest the brief asked for, and the grayscale cell proves it survives with no
   green at all. The scary-cute beat ("calm face is the menace") lands. Keep this
   almost as-is.
2. **Palette / night pop.** Bone-dominant + wax-black value anchor + green accent
   is harmonious and reads on BOTH skies; the night cell shows the green lifting
   nicely without going neon. Good.
3. **Distinctness.** Lane is clean vs the set and the existing roster. No notes.
4. **The cassock body.** Reads as a clean robe; praying hands are a touch mushy at
   1x (see FIX) but the proportion (small body, dominant skull+crown) is right.
5. **WEAKEST — the candle CROWN read + the prop->pillar cap.** Two real failures
   below. The crown currently reads "mohawk / sci-fi headdress," not "ring of
   altar candles," and the pillar cell fails to show the flame lighting the gap.

---

## KEEP

- The serene closed-eye face, heart-nose, calm brow, quiet tooth band — the whole
  face. This is the win; protect it.
- The flat-teardrop flame + tight outside additive halo. Correct house grammar,
  correct distinctness vs neon/torch. Do not soften into a gradient blob.
- Bone/wax-black/green value structure and the night-lift behaviour.
- Small praying cassock proportion (skull + crown dominate). Right call.

## FIX

1. **(SHOWCASE BROKEN) Cell (a) clips the entire crown off the top of the panel —
   horns and flames bleed into the title row.** The figure is composed too tall
   for its surface: the crown rises into the top `pad` but `build_pyrecrown` only
   pads the TOP by `pad` while the boss is then bottom-aligned in the panel, so at
   scale 1.7 the flames render above the panel. The showcase is the first thing
   the user sees and right now it's unreadable. Re-frame so the whole figure
   (top flame tip -> hem) sits inside the cell with margin.
2. **(CROWN READS AS MOHAWK, not candles) The five tapers are too tightly packed,
   too uniform, and fan from a narrow rim — at 1x they merge into one black
   spiky mass with green dots on top.** It reads "punk crest / Invader Zim
   antennae," not "ring of altar candles." To sell CANDLES: (a) widen the rim
   spread so the outer two splay clearly past the skull's temples and you see SKY
   between the tapers; (b) vary the candle widths/heights more boldly (right now
   the heights step too gently); (c) make the wax-drip + melted-lip read at the
   tops obvious even at 1x — the "melted candle" tell is what separates this from
   horns/spikes. Gap between tapers is the whole game; open it up.
3. **(CANDLES LEAN INWARD / CONVERGE) The outer candles tilt their flames TOWARD
   the centre, so the flames cluster into a single clump instead of fanning into
   a crown.** Look at the day cell: the five green flames bunch into ~one blob at
   1x. Flip the lean so tapers splay OUTWARD (a fan/candelabra opening upward),
   or keep them dead-straight-vertical. A converging cluster also undercuts the
   distinctness guardrail (it starts to read as one big flame, drifting toward the
   torch/neon lane). Splay them.
4. **(PROP->PILLAR PAYOFF MISSING) The 2x gap-zoom in cell (b) shows only the
   dark wax-drip shaft — NO skull-knob cap, NO green flame lighting the gap.** The
   entire thesis of this prop ("the flame caps into the gap; it LIGHTS not snuffs")
   is the one thing the pillar cell must prove, and it's absent from frame. Either
   the zoom is framed on mid-shaft (most likely — re-aim `zoom_src` at the cap
   band, not the banding) or the cap is being drawn off the visible gap. Until a
   green flame is visibly lighting the gap edge on the NIGHT sky, the pillar
   concept is unproven. This is the highest-value fix after the showcase.
5. **(GAP DARK ON NIGHT SKY) Because the cap/flame isn't lighting the gap, the
   pillar gap is a black-on-dark void at night** — the worst-case legibility a
   Skybit obstacle can have. The green flame caps exist precisely to rim-light the
   gap edge against the night sky; make them do that job. Show the pillar pair on
   the NIGHT sky in cell (b), not only day — the brief says green must pop on
   night SPECIFICALLY, and that's exactly where the gap-edge flame earns its keep.
6. **(MINOR) Praying hands mush at 1x** — the two bone rects + seam blur into one
   pale lump on the dark robe. Either commit to a clearer two-hand steeple
   silhouette (a peak with a visible centre seam) or simplify to a single small
   bone diamond. As-is it reads as a random pale patch.
7. **(MINOR) The green under-socket glow is doing very little at 1x and risks
   muddying the serene read** if pushed. The grayscale proves the face works
   without it; keep it subtle (current night value is about right) and do not
   raise it to compensate for the crown — fix the crown instead.

---

## ITERATION DIRECTIVES (prioritized punch list)

1. **Fix the showcase clip.** Re-frame `build_pyrecrown` so the full figure
   (top flame tip to hem) fits inside cell (a) with margin at scale 1.7 — pad the
   TOP enough for the crown and bottom-align to the padded bounds, not the raw body.
2. **Re-aim the gap zoom + show the cap.** Point cell (b)'s 2x zoom at the
   skull-knob + green-flame CAP band so the "flame lights the gap" payoff is
   visibly proven; confirm the cap actually renders at the gap edge of both
   pillars.
3. **Splay the candles OUTWARD** (or dead-vertical) so the five flames fan into a
   crown instead of converging into one clump; flip the `lean` sign in `_crown`.
4. **Open the crown read:** widen rim spread so sky shows between tapers, push
   bolder height/width variation, and make the melted-lip + wax-drip tell legible
   at 1x — sell CANDLES, kill the mohawk.
5. **Put the pillar pair on the NIGHT sky** in cell (b) and confirm the green
   gap-edge flame rim-lights the gap (the brief's headline requirement).
6. **Clarify the praying hands** (clean steeple silhouette or single bone diamond).
7. Hold the green socket-glow subtle; do not lean on it to rescue the crown.

---

## REFERENCES

- Candelabra / advent-candle fans (the splayed-outward, sky-between-tapers read
  this needs): search "candelabra silhouette" — note how legibility comes from the
  GAPS between candles, not the candles themselves.
- Baphomet "torch between the horns" (the source idea): keep the green soul-fire
  multiplied and contained so it stays an altar CROWN, not a single torch (the
  Baalgoat lane) or a glow wash (the Glitchfiend lane).
