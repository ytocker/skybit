# AD critique — Haedung (fire-eating guardian-lion totem-post) — ROUND 2

**VERDICT: ITERATE**

One fix from ship. Every round-1 note landed cleanly and the flame-curl now
reads as a genuine flame — but the GD's own self-flag is correct: at HERO
scale the ember maw interior runs hot/high-key and FUSES with the bright gold
bell directly below it into one connected bright-yellow lower-face mass. Tone
the maw interior down a notch and break it from the bell, and this ships. This
is the single most important remaining fix; everything else holds.

---

## Round-1 fix verification (all addressed)

- **Flame-curl (top priority last round) — FIXED.** Now a distinct chunky
  comma-lobe with a hard dark ink-gap collar separating it from the maw rim,
  and a cream-yellow hooked tip that bites up above the mouth corner and breaks
  the mouth's top silhouette. At hero scale it is unmistakably a separate flame,
  not a lumpy lip. The fire-EATER gag is recovered. GOOD.
- **Brow-horn — FIXED.** Rounded carved nub with dimension (no longer a flat
  trapezoid plug), single and centered. GOOD.
- **Mane — FIXED.** Reads as ~6 bold, spaced curl-lobes; no longer a packed
  bead/noise ring. Each lobe is its own silhouette bump. GOOD.
- **Pillar / weight — GOOD.** Mirror cap clean and bottom-rooted; scaled cedar
  column reads visibly tall; mask no longer top-heavy after the mane cull. The
  fish-scale courses survive downscale as repeat texture.
- **Eyes — HELD.** Simple round bug-eyes, single carved ring, warm-cream
  catchlight, thick ink keyline. Anti-Tlaloc compliant. GOOD.
- **Matte wood — HELD.** No glaze/crackle; flat triad + ink keyline + outline.
  Honey-cedar tone correct, clear of Zhenmushou. GOOD.
- **Jade — HELD.** Stays a blue-leaning SCALE-BAND / mane-tip accent, placed not
  massed; eye glow warm-only. Cross-set pin compliant. GOOD.

---

## THE remaining fix — tone the hero maw interior, de-couple it from the bell (FIX, ship-gate)

Ruling on the GD self-flag: **confirmed.** At HERO scale the ember maw interior
is pushed to nearly the same top value as the flame's cream tip AND the gold
bell plate sitting immediately below the chin. Those three zones now read as one
continuous blown-out yellow field across the entire lower face. Consequences:

- The flame-curl's cream tip no longer out-values its surroundings, so it stops
  being the clean SECOND focal stop after the eyes — it's swimming in a bright
  field instead of popping against a contained ember.
- The bell, which round 1 correctly muted in hue, is now bleeding back in via
  GLOW: it's lit to the same key as the maw, so the warm focal smears downward
  off the face onto the chest.

Concrete fixes (do all three; they're small):
1. **Drop the maw INTERIOR a value notch** — pull the maw fill back from the
   ~240-lum near-white toward the spec ember `(238,128,64)` mid, reserving the
   brightest cream value ONLY for the flame-curl tip and a thin maw rim-lick.
   The maw should glow, not blow out.
2. **Insert separation between maw and bell.** Re-establish a clear dark
   chin/jaw band (ink keyline + cedar shade) between the lit maw and the bell so
   they are two shapes, not one light source. The bell should sit a value below
   the maw — gold hardware catching warm light, not emitting it.
3. **Knock the bell's own glow down** the last ~10–15% so it never matches maw
   key at hero scale. (Hue is already correct from round 1; this is purely the
   lit-area value.)

Acceptance: at HERO scale the read order must be EYES > flame-curl + maw ember
> everything else, with a clear dark gap under the chin so the bright lower face
no longer reads as a single mass. The true-32px chips already pass (see below),
so this is a hero-scale-only tuning — do not let it cost the 32px flame read.

---

## Confirmations against the round-2 questions

1. **Fire-curl reads as the soul at true 32px (day + night)? YES.** Day chip:
   the ink-gapped comma-lobe with cream tip reads as a warm flame hooking off
   the left mouth corner — distinct from the maw, legibly a flame, not a lump.
   Night chip: actually the STRONGEST read of the set — the dark sky contains
   the glow, the ember maw stays the warm focal, and the flame tip pops. Both
   pass the 1x acceptance test. (This is exactly why the hero blow-out is the
   only blocker: shrink hides it, hero scale exposes it.)
2. **EPIC scary-cute, matte carved wood (no glaze), single-ring bug-eyes
   (anti-Tlaloc), one brow-horn, jade as scale-band only? YES on all.** Reads
   epic and characterful, not grim; matte cedar with no kiln sheen; one carved
   eye-ring per eye; one centered brow-nub; jade confined to scale-band + mane
   flecks.
3. **Pillar mirrors clean + bottom-rooted, wide mask not top-heavy, distinct
   from source + roster? YES.** Clean mirror, tall column, balanced weight after
   the mane cull. Distinct from the slate-wood/cinnabar source Jangseung and
   separable from the other four briefs.

---

## Iteration directives (final round — punch list)
1. Drop the ember maw INTERIOR a value notch toward the spec mid; reserve the
   top cream value for the flame-curl tip + a thin maw rim only.
2. Re-establish a dark chin/jaw separation band so the lit maw and the gold bell
   are two distinct shapes, not one bright lower-face mass.
3. Knock the bell's lit-area value down the last ~10–15% (hue is fine) so it
   never matches maw key at hero scale.
4. Re-shoot the HERO render to confirm read order EYES > flame+maw > rest, with
   a clear dark gap under the chin.
5. Do NOT touch the 32px chips' flame read or anything else — flame-curl,
   brow-horn, mane, eyes, jade, matte wood, mirror all HOLD as-is.
