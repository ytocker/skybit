VERDICT: ITERATE

# Draugr — Round 2 critique (Batch 2 / Skeletons) — FINAL critique, brief for the GD's round-3 pass

Round 2 fixed the headline problem. The "grey knight" read is GONE: the frost-bone
skull is now the dominant light mass, the ice-cyan is disciplined to the jaw glow +
one restrained crown rime cluster, and the figure reads unmistakably as a COLD,
frosted barrow-undead — not an armored man. Horns are now stubby angled nubs that
survive downscale. The axe-pillar remains the sheet's best element. This is one
small color tweak away from ship; it does NOT clear the bar yet because the new
brow-cap drifted too pale and there's a stray cyan dot fighting the focal, so I'm
spending the last designer pass on a surgical cleanup rather than blessing as-is.

## Strongest / weakest
- **Strongest:** the cold identity now lands. Frost-bone skull is the lightest mass,
  the ice-cyan jaw plate + tiny cyan socket-pupils are a clean focal cold-tell, and
  the rust mail / brown shield give exactly the warm counterweight the palette wants.
  The 32px day AND night tiers both still read as "frosted helmed warrior with a
  shield" — the identity survives to gameplay scale. The prop->pillar mirror is
  unchanged and perfect.
- **Weakest:** the helm brow-cap is now too PALE — a near-white/light-slate dome that
  reads as more frost-bone, not "rust-iron brow-cap." The brief pinned the helm as a
  LOW rust-iron + bronze-trim accent; right now the only rust-iron is the thin bronze
  brow-band, and the cap above it is the same value as the skull, so the head reads as
  one big pale blob split by a gold band rather than iron-cap-over-bone.

## Per-aspect KEEP / FIX

**Color / helm cap — FIX (primary, the only real blocker).** The brow-cap dome is
near-white with a faint cyan wash. It should be the rust-iron `(150,96,62)` family
(matching the mail) or a cool dark slate, so the value structure is: dark iron cap →
bright frost-bone skull → cyan jaw focal. As-is, cap and skull share a value and the
helm disappears as a distinct element. Darken/warm the cap to rust-iron with the
bronze band as its trim. This also re-separates Draugr from any pale-bone sibling and
kills the last whiff of "is that frost or metal?"

**Ice-cyan discipline — KEEP** the jaw plate + socket pupils + ONE crown rime
cluster. That's the right restraint. **FIX:** there's a stray cyan diamond/dot sitting
on the nose-guard between the eyes that competes with the jaw for the focal cold-tell
— remove it (or fold it into the crown cluster). One cyan focal zone, not two.

**Skull face — KEEP** the wide hollow sockets + tiny cyan pupils; genuinely
cute-creepy and the brow now has a slight angry arch. Good menace without losing
chibi charm.

**Rust mail / studs — KEEP.** The white mail studs are toned down and no longer a
second noise field — fixed cleanly. Mail value separates well from bone.

**Moss — KEEP** the moss is now up on the shoulder + a few ground tufts, so the
"moss-crusted barrow-mound" thesis reads. Good. Minor: one or two flecks on the helm
crown would seal it, but this is optional polish, not a blocker.

**Shield — KEEP.** Settles into a supporting warm anchor now that the face pops;
reads at every scale. No change.

**32px / scale ramp — KEEP.** Face survives to 24px (jaw + sockets still read); 16px
collapses to a blob but that's below gameplay floor and acceptable. Horns now survive.
Once the cap darkens, the 16/24px tier will gain even more head/cap contrast — verify
the cap still reads distinct from the skull at 24px after recolor.

**Identity / feasibility / accessibility — OK.** Distinct from warm-bone siblings; no
green/violet conflict; all flat triad fills (procedural-safe). The high frost-bone
value + crystalline rime geometry give a non-hue cold tell. The cap recolor actually
strengthens accessibility (adds a value step independent of cyan).

## Iteration directives (round-3 punch list — prioritized)
1. **Recolor the helm brow-cap to rust-iron `(150,96,62)`** (or a cool dark slate if
   iron ties the mail too closely) so the value reads dark-cap -> bright-bone-skull ->
   cyan-jaw. This is the one blocker. The bronze band stays as its trim.
2. **Remove the stray cyan dot on the nose-guard** between the eyes — keep cyan to the
   jaw plate + socket pupils + the single crown rime cluster only.
3. **Verify 24px** after the recolor: the cap must still read as a distinct darker mass
   over the lighter skull (it should improve, not regress).
4. **(Optional polish)** one or two moss flecks on the helm crown to seal the
   "barrow-mound, ancient" thesis.
5. Leave the axe-pillar, mail, studs, shield, horns, and moss base exactly as they are
   — all resolved.

If round 3 lands directives 1–2, this ships.
