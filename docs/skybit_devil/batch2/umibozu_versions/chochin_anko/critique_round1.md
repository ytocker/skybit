# Chochin-Anko — abyssal anglerfish lure-fiend — Round 1 critique (Art Director)

VERDICT: ITERATE

This is a strong, confident first round. The character genuinely reads as an
EPIC, memorable creature — the grump-maw + nightlight-on-a-stalk is instantly
legible and it nails the scary-CUTE register. It is NOT a re-roll. But three
real problems keep it off SHIP-READY, and the most important is exactly the one
the GD flagged — though my ruling differs from the implied "leave it."

---

## Ranking of issues (most important first)

### 1. FOCAL INVERSION — the esca lure pip is NOT the sole brightest mass (HARD pin fail)
This is the one that must change. The brief is unambiguous: "Keep the body near-
silhouette DARK so the single lure pip is the only focal," and "hot-white-peach
lure is the sole brightest pip." Right now, at true 32px and especially at the
4x blow-up, the lure-bulb is a peach/cream RING, not a hot WHITE-peach point —
its center is the same value as its rim, so it has no hot core. Meanwhile the
coral belly+gum flush and the white needle-teeth row are reading at competitive
or HIGHER brightness than the esca. On the night chip the teeth + coral mouth
grab the eye before the lure does; on the day chip the lure nearly disappears
against the bright sky because it has no white-hot core to separate it.

The lure must win the value contest outright. It needs a true hot-white core
`(255,~244,228)` blooming up out of the peach `(255,224,168)` body, so it reads
as a single incandescent PIP, not a flat lantern coin. Pull the teeth down ~25%
in brightness (off-white/cool-grey, not pure white) and keep the coral strictly
belly+gum (it currently creeps up the lower lip toward mid-value). Eye should
land on the lure FIRST at 32px on both skies. Right now it lands on the grin.

### 2. The 1px-stalk dropout at 32px — ACCEPTABLE, but only after #1 and #3 are fixed
The GD's read is correct and honest: at true 32px the segmented stalk thins to
~1px and the knuckle-nodes/barbels drop out, so the chip reads "dark blob + hot
lure on a stick + coral grin." My ruling: that compact read is ACCEPTABLE and
even desirable — the stalk detail is rightly a hero/pillar feature, and a clean
"dark blob + lure-stick + grin" is a great gameplay-scale silhouette. We do NOT
need to fatten the stalk to preserve nodes at 32px; chasing node legibility
would only add noise. KEEP the thin elegant stalk in the compact bake.

BUT two caveats, both currently failing:
- The stalk must stay one unbroken value at 32px. On the current night chip the
  cold-steel sheen on the stalk breaks it into dashes — it reads as a dotted
  line, not a stalk. Bake the compact stalk as a single solid dark stroke (no
  segment sheen below ~SS2); let the hero/pillar carry the knuckle/barbel detail.
- It must survive the DAY sky. On the day chip the dark stalk against bright blue
  is fine, but the lure-on-stick gesture only works if the lure has the hot core
  from #1. Without it, day-chip reads as "dark blob with a pale smudge."

### 3. Esca separated from the silhouette + glow bleed over the body (polish)
The GD flagged both correctly. The esca currently floats slightly off the brow —
there's a visible sky-gap between the stalk-arc and the head, so the lure reads
as a detached object rather than THIS creature's lure. Tighten the brow-root →
stalk-arc connection: root the illicium visibly into the brow/forehead with a
1–2px dark anchor nub so the eye traces head → stalk → lure as one continuous
form. And rein in the hero stalk-glow: it's bleeding a soft halo over the oil-
black body, muddying the silhouette's top edge and stealing contrast from the
lure. Keep the glow tight to the esca; the body must stay crisp near-silhouette
so the 1px outline still pops.

---

## House-style fidelity — PASS (with the #1 caveat)
- Chibi proportions: big grump head, stubby implied body — YES.
- Scary-CUTE, elevated not grim: the perpetually-annoyed underbite + needle-maw
  lands the hook perfectly. This is the charm win of the round. KEEP it exactly.
- Flat triad (dark-core -> flat-fill -> cold-steel top-left rim-sheen): present
  and clean on the head.
- 1-2px ink keyline + 1px grown outline: reads at hero scale; just protect it
  from the glow bleed (#3).

## Cross-set PIN compliance — PASS
- Blood-coral is correctly BELLY+GUM ONLY, never full-body — clear of
  Akkorokamui's full-body red. Good discipline; just stop the coral from
  creeping up the lower lip (#1) so it stays unambiguously a belly/gum flush.
- Hot-white-peach lure as the sole brightest pip: this is the INTENT but not yet
  the RESULT — see #1. This is the gating fix.
- Oil-black body, distinct from the smooth teal-black source Umibozu and from the
  rest of the roster: YES, the angler grump-maw silhouette is wholly its own.

## Pillar — PASS, near ship
The illicium-stalk-as-shaft with the esca lure-bulb cap is clean, bottom-rooted,
and mirrors well top<->bottom. The knuckle-node + barbel-feeler cadence is
characterful and exactly the kind of hero detail that earns the "stalk detail is
a pillar feature" ruling. Two small notes: (a) confirm the esca cap is ~shaft+30%
and on-axis — it currently looks slightly larger, verify it's not top-heavy;
(b) give the cap the same hot-white core from #1 so the pillar's gap-cap glow
matches the creature's lure.

---

## Iteration directives (next-round punch list)
1. Give the esca a TRUE hot-white core `(255,244,228)` blooming out of the peach
   `(255,224,168)`, so it reads as a single incandescent PIP — the sole brightest
   mass — at 32px on BOTH day and night. This is the gating fix.
2. Drop the needle-teeth ~25% in brightness (cool off-white, not pure white) and
   keep coral strictly to belly+gum — stop it creeping up the lip. The eye must
   land on the lure first, the grin second.
3. Tighten the brow-root -> stalk-arc connection with a 1-2px dark anchor nub at
   the forehead so the lure reads as attached to THIS creature, not floating.
4. Rein in the hero stalk-glow so it stops bleeding over the oil-black body —
   keep the glow tight to the esca; protect the crisp silhouette + 1px outline.
5. Compact 32px bake: keep the thin elegant stalk, but render it as ONE solid
   dark stroke (no segment sheen / dotted-dash break) below ~SS2 — the "dark blob
   + lure-stick + grin" read is the target and is approved.
6. Verify the pillar esca cap is ~shaft+30% on-axis (not top-heavy) and carries
   the same hot-white core as the creature's lure.

## References
- Source Umibozu (round_3) for lineage value-discipline:
  /home/user/skybit/docs/skybit_devil/batch2/leyak_epic/umibozu/round_3.png
- Locked brief concept #1:
  /home/user/skybit/docs/skybit_devil/batch2/umibozu_versions/brainstorm_locked5.md
