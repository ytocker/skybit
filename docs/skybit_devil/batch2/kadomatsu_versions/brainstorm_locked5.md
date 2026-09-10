# Kadomatsu brood — locked 5 (epic bamboo-PLANT bosses inspired by Kadomatsu-Shin)

Spin-off brood off **Kadomatsu-Shin** (the New-Year three-culm gate-god, `bamboo_v2_versions/kadomatsu_shin/`).
North Star (user, verbatim): **"MAKE IT RELIABLE TO BAMBOO. IT IS A BOSS BAMBOO PLANT."** Bamboo-plant
reliability is a HARD GATE every round; mythic/epic is flavor layered on top, never a replacement.
Flavor = **mythic bamboo-beast**; centrality = **both** (4 body-is-bamboo + 1 beast, leaning body-forward
on purpose since the parent is a pure plant).

## Inherited DNA — non-negotiable in ALL 5 (clone from `kadomatsu_shin/render_round_2.py`)
- **Diagonal-cut hollow-ring CREAM mouths = THE signature focal.** `diagonal_cut()`: bright ring-wall
  `CUT_CREAM (224,214,170)` + sheen `CUT_HI (244,238,206)` (the BRIGHTEST value on the form) + small
  lightened cavity `CAVITY (118,128,92)`, steep sogi slant. Must POP at true 32px → collapses to a bright
  cream disc.
- **Bound / fresh-cut culm material dominates the silhouette.** `culm_shaft()` node-segments (madake
  two-ring collars + branch-stub nubs); warm fresh-culm green `CULM (124,188,104)` w/ 4–6 HARD stepped
  bands (`CULM_HI 172,216,130` / `CULM_D 74,138,72` / `CULM_DD 50,102,56`); warm rim-keyline
  `CULM_RIM (158,206,116)` for night-hold; `CULM_BACK (58,116,62)` for stepped depth.
- **Auspicious New-Year kit, base-anchored (never top-heavy):** `straw_collar()` tight bind
  (`STRAW 206,176,104`), `pine_fan()` (`PINE 58,104,62`), `plum_blossom()` vermilion `PLUM (216,80,60)`,
  `bound_face()` + the sole `radial_glow` gold blessing `GLOW (244,224,150)`.
- **Pipeline:** `SS=6` → smoothscale; ZERO gradients (hard steps only); ink keyline `INK (28,22,30)` +
  1px `grow_outline`. Each sheet = hero + assembled top↔bottom-mirrored **pillar** (culm-segment repeat +
  explicit slant `cut_cap` gap-edge + value-anchored lower mirror) + true-32px **day & night** chips +
  **blacked-out** silhouette proof + palette strip.

Each concept keeps the warm fresh-cut-bamboo family and adds ONE held-apart accent (off roster green
lanes: Cernun pine / Kappa yellow-green / Kitsune mint / Haedung jade).

---

## 1. Moso-no-Taisho — the great single-culm monolith (rank 1, the set's spine)
- **Silhouette KIND:** SINGLE FAT MONOLITHIC COLUMN with one colossal top slant-cut — a lone
  standing-stone of bamboo, wider than any single element in the brood. The deliberate anti-parent
  (parent = slim stepped trio; this = one titanic shaft). Purest bamboo read of the set.
- **Epic hook:** awe through scale + restraint (a megalith).
- **Held-apart accent:** **kintsugi gold-vein** as THIN ~2px line-work tracing the node-collars only —
  NOT a glow fill (kept distinct from the pale-gold blessing glow at the foot).
- **Pillar:** it already IS the hero pillar — node-segments tile, the colossal cut = gap-cap,
  straw-cinched plum-cream foot = lower mirror. Cleanest mirror in the brood.
- **MUST-FIX:** the giant cut-disc fills ~the top quarter and stays the brightest value (at 32px → one
  unmissable cream disc); 5–6 BIG node collars (only direction with room for node geometry to read
  large — use it); gold veins ≤2px hairlines so they don't boil at 32px; foot-kit (straw + plum + one
  pine sprig) carries just enough base life so the monolith isn't inert — but never top-heavy.

## 2. Kadomatsu-Torii — the living gate of stacked cut culms (rank 2)
- **Silhouette KIND:** TALL ⛩-FRAME GATE — two vertical culm-bundle uprights + a heavy horizontal
  lintel + a smaller tie-beam; the OPEN doorway between the legs is the read (the ONLY negative-space
  form in the set or the siblings).
- **Epic hook:** monumental architectural scale; the doorway faintly gold-lit.
- **Held-apart accent:** a single **vermilion shrine-cord / shimenawa-red band** across the top beam —
  the only high horizontal red sash (base-balanced by straw + plum below).
- **Pillar:** one upright leg IS the pillar verbatim — bound-culm shaft tiles, the cut lintel-end =
  slant gap-cap, straw + plum = lower mirror.
- **MUST-FIX:** the four corner cut-discs (two upright tops + two lintel ends) are the signature — make
  them the brightest cream and large enough that at 32px the form reads "open rectangle pinned by four
  cream nodes." Keep legs visibly STRIPED bound-culm (vertical stepped bands + straw lashing where
  lintel meets leg) so the frame never reads as plain timber. Push OPENNESS hard — wide doorway, thin
  members — to bank the negative-space read.

## 3. Tatsu-no-Takemura — the coiling grove-serpent (rank 3, the set's one beast)
- **Silhouette KIND:** VERTICAL COILING S/Ω-SERPENT — a thick ribboning culm-body looping up the frame,
  head reared at the top; a continuous winding tube. The only kinetic/coiling form; the most
  bamboo-reliable beast (its body IS a stacked culm, node-collars = belly-scales).
- **Epic hook:** motion + length — the dragon of prosperity climbing the gate.
- **Held-apart accent:** **jade-teal whisker / dorsal-fin glint**, DARKER + COOLER than CULM, as
  thread-thin filament-only accents (kept off the Haedung jade lane — never a body fill).
- **Pillar:** a straight body-segment IS the pillar (node-collars = repeat band), reared-head cut-maw =
  gap-cap, coiled tail-foot + plum = lower mirror.
- **MUST-FIX:** the reared HEAD is the hero cream cut-disc maw (cavity = open mouth), brightest value;
  every coil-segment shows clear node-collar rings so it reads bamboo-as-scales, not a plain green tube;
  keep to 2–3 GENEROUS loops (not tight spaghetti that blurs to a blob) so at 32px the silhouette reads
  as a winding S with one bright cut-disc head; 1–2 small cut-nubs where coils overlap to seed cream rhythm.

## 4. Kazari-no-Yama — the offering-mound pyre of bundled culms (rank 4)
- **Silhouette KIND:** FAT TRIANGULAR MOUND-PYRE — a broad-based PEAKED pile of dozens of DISCRETE bound
  culms, hard culm-tips bristling the upper slopes, triple straw bands cinching the tiers. Buys the set
  its "sheer mass / abundance" register.
- **Epic hook:** the most culms of any direction — a mountain of offerings.
- **Held-apart accent:** **mikan-orange daidai + rice-ear gold** tucked in the lashings — the only
  warm-orange in the brood.
- **Pillar:** one tier-culm IS the pillar; tiered straw bands = repeat collars, an apex cut-disc =
  gap-cap, the broad lashed foot = lower mirror.
- **MUST-FIX (the set's one real watch — separate HARD from the Takenoko sibling cone):** Takenoko is
  ONE smooth tapering husk-SHELL (continuous plates); Kazari must be a PACKED CLUSTER of many DISCRETE
  culms with a bristling, BROKEN upper edge + a constellation of cream cut-discs (one big apex hero + a
  graded scatter down the flanks). Blackout silhouette must read jagged/many-tipped, NEVER a smooth
  solid triangle. The triple horizontal straw bands + the cream-disc constellation are what kill the
  cone twin — make both unmistakable.

## 5. Shishi-Kadomatsu — the bound-culm guardian lion (rank 5, conditional on the mane rebuild)
- **Silhouette KIND:** SQUAT CROUCHED QUADRUPED with a round CUT-DISC mane — low, heavy, broad, four
  planted leg-bundles, a circular crown around a blessing-face. The only horizontal/quadruped form in
  the brood or siblings; the set's creature-centrality entry.
- **Epic hook:** heraldic guardian power, coiled and grounded.
- **Held-apart accent:** **indigo-cobalt brow / mane-cord** — the only cool-blue accent (heraldic,
  never washes into the greens).
- **Pillar:** a foreleg-bundle culm IS the pillar; a mane cut-disc = gap-cap, planted paw + straw anklet
  + plum = lower mirror.
- **MUST-FIX (the keep CONDITION):** the mane must NOT read as fur — build it as a RADIAL SUNBURST OF
  CREAM CUT-DISCS (a halo ring of bright diagonal-cut culm-ends around the face) so the mane IS the
  cut-mouth signature. The four legs are obviously bound stepped-green culm bundles (node rings visible);
  the body a lashed-culm mass — blackout reads "bundle-bodied beast crowned with a ring of cut-tips," NOT
  "lion." If at 32px the mane reads as a furry blob rather than a ring of cream nubs, this direction
  FAILS the gate → re-roll rather than ship a green lion. Lean the cut-disc crown bright and discrete.

---

## Set-level distinctness (locked)
- **Blackout shapes:** lone fat monolith (Moso) / open gate-frame (Torii) / vertical coiling S-tube
  (Tatsu) / fat peaked many-tipped pyre (Kazari) / squat horizontal quadruped + ring-crown (Shishi) —
  five clearly different black shapes. None matches the parent's slim vertical stepped trio.
- **Vs the 4 bamboo v2 siblings:** none is a smooth single husk-cone (Takenoko), a wide-LOW drift-mound
  (Sasa), a winged beaked crow (Kurochiku-Tengu), or a downward radial leg-star (Take-Tsuchigumo).
  Watches handled in-brief: Kazari vs Takenoko cone (DISCRETE many-culm + bristling top + straw bands);
  Shishi's "lion" risk (mane-rebuild).
- **Accents (all held-apart, none on a roster green lane):** kintsugi-gold line-work (Moso) /
  shrine-vermilion sash (Torii) / jade-teal filament (Tatsu) / mikan-orange (Kazari) / indigo-cobalt
  (Shishi).
- **Cut-mouth deployment variety:** one giant hero disc (Moso) / four corner discs (Torii) / reared-head
  maw + overlap nubs (Tatsu) / a constellation (Kazari) / a radial ring-crown (Shishi).
