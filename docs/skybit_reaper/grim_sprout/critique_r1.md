# GRIM SPROUT — Art-Director critique, Round 1

`VERDICT: ITERATE`

The house-style correction landed: this is unmistakably FLAT chibi, bold
orchid+mint, hard ink keyline, triad-shaded — zero drift back to the prior
round's grim-realist desaturation. The snath-as-tileable-post / blade-as-gap-edge
pillar story is also genuinely solved and reads cleanly in (b)/(b'). That is the
hard structural work done. What's NOT yet shipping is the thing the whole concept
rests on: at 1× (cell c) the **comedy-of-scale read collapses** and the
**scary-cute face is lost**. Two more rounds should close it.

---

## Strongest / weakest

- **Strongest:** the prop→pillar engineering. The snath is a clean banded vertical
  post, the blade detaches to the gap-edge only, and the top/bottom mirror reads as
  one matched obstacle. The mid-strip (b') tiles with no blade bleed. Ship that
  system as-is. Palette and flat-finish fidelity are also fully on-style.
- **Weakest:** the 1× silhouette (cell c). The imp is a purple blob, the blade is a
  thin pale wisp that nearly vanishes on the day sky, and the eyes/fang/feet are
  sub-pixel mush. The single most important read of this concept — "tiny terror,
  HUGE blade" — does not survive the shrink.

---

## Per-aspect KEEP / FIX

**1. House-style fidelity — KEEP.** Flat fills, 1–2px ink keyline, dark-core→fill→
top-left sheen triad, saturated orchid+mint. Exactly the correction asked for. No
notes.

**2. Comedy-of-scale — FIX (top priority).** In the showcase the blade reads as
maybe 1.3× the body, not 5×. The guardrail says keep the ratio EXTREME or it
becomes "a generic small reaper." Two failures compound: (a) the blade crescent is
too SHORT and too THIN — it's a delicate hook, not a great-scythe that dwarfs him;
(b) the imp body is too TALL/large relative to it. The snath also leans across the
body diagonally, which visually shortens the prop. Stand the snath more upright and
let the blade arc big and wide above the imp so the vertical stack reads
imp-then-WAY-up-there-blade.

**3. Scary-cute menace — FIX.** At showcase size the face is two gold dots and a
black crescent that, with the fang, currently reads closer to a frown/grimace than
a charming "too-big-for-his-britches" baby. At 1× the face is gone entirely. The
fang is centered and small; push to ONE bold oversized fang offset to one side, and
give the eyes a slight size asymmetry or an upward tilt to land "cute" not "grim."

**4. 1× legibility — FIX.** On the DAY inset the bone blade (236,232,214) is nearly
the value of the light sky bottom (170,220,245) and the thin lit edge disappears;
the blade silhouette breaks. The ink keyline is too thin at this scale to rescue it.
The feet, claws, belly-mint and pinprick eyes are all noise/gone at 1×. Cut detail
that can't survive and thicken what carries the read.

**5. Distinctness — KEEP.** No collision with Big Reapy / Dr. Quill / Tick-Tock /
The Hollow. The imp+oversized-scythe stays unique. Just make sure fixing scale
doesn't drift it toward a generic hooded reaper.

**6. Polish — FIX (minor).** The droop-curl hood tip + mint pom is a nice charm
beat but at 1× it merges into the head blob — it reads as a lump, not a flopped
hood. The two grip-mitts are nearly identical blobs; differentiate the up-grip
(closed fist high) from the low brace so the "hauling a weapon 5× his size" pose
has body language.

---

## Iteration directives (priority order)

1. **Push the prop-to-body ratio to genuinely extreme (~4–5×).** Make the blade
   crescent dramatically longer and wider (roughly double `span`/`rise`) and stand
   the snath closer to vertical so the scythe stacks tall ABOVE the imp rather than
   leaning across him. Shrink the imp body relative to the prop. The instant read at
   1× must be "huge blade, tiny baby under it."

2. **Rescue blade legibility on the day sky.** The bone blade is too close in value
   to the light day-sky bottom — it breaks silhouette in cell (c). Either thicken the
   ink keyline (it's the load-bearing edge at 1×), darken the blade spine, or add a
   subtle mint/violet under-rim so the crescent holds its shape against BOTH skies.
   Confirm by viewing cell (c) as a B/W silhouette (AD accessibility note) — the
   blade must still read.

3. **Make the face land scary-cute at showcase AND survive to 1×.** Enlarge and
   offset a single bold fang, give the gold eyes an upward/asymmetric cute tilt, and
   make sure the dark crescent + eye sockets read as a face shape (not just two dots)
   when shrunk. The eyes carry charm — but per the accessibility note the dark socket
   shape, not the gold hue, must carry the read in grayscale.

(Secondary, if budget allows: differentiate the two mitts for a "struggling to haul
it" pose; clarify the hood droop-curl so it reads as floppy oversized hood, not a
head lump; drop the 3-claw foot detail to 2 bolder claws or omit at 1×.)

## References
- Skybit's own warren clown anchor `docs/warren_clown/round_17_final.png` for the
  triad finish + held-prop pillar relationship (already matched well — keep parity).
- Comedy-of-scale benchmark: tiny-character/giant-weapon casual reads stay legible
  by making the weapon the dominant silhouette mass and the character a small
  high-contrast accent beneath it.
