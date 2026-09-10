# Skybit Death/Reaper Boss — Brainstorm (chibi house-style re-grounding)

**Context.** The user picked the **Death/Reaper** direction from a prior round,
but it shipped in an off-style finish: desaturated void-violet, semi-realistic
soft shading, feathered smoke, thin/no keyline, grim-dark tone. That clashes
with Skybit's chibi house style (the warren clown anchor: chunky big-head body,
weight-shifted presenting pose, FLAT saturated fills, hard ~`(28,22,30)` ink
keylines, the dark-core → fill → top-left sheen triad, and a tall vertical
held prop that mirrors into a scrolling pillar — `docs/warren_clown/round_17_final.png`).

This brainstorm seeds **8 genuinely distinct chibi-Skybit takes on Death** for
the art-director to cull to 5. Each is a *different KIND of Death* — not one
hooded robe in eight colors. Every take obeys the non-negotiable house spec:

- **Chibi build** — head ≈ 40% of total height, short wide torso, asymmetric
  weight-shifted stance (one hip cocked, one shoulder dropped, head tilt),
  built from primitive circles/polys/lines like `build_jester`.
- **FLAT fills + 1–2px hard ink keylines** `(28,22,30)`. No within-shape
  gradients, no soft/feathered edges, no bevels, no realistic multi-light.
- **Form via the triad** (`_marotte_ruff`, `pillar_staff.py:240`): `_shade_c(col,-55)`
  dark-core ring → `col` fill → `_shade_c(col,55)` ~⅓-radius top-left sheen.
- **Silhouette POP** via grown 1px outline (`parrot._add_outline`) or inset ink
  keylines (jester). Must read black-shape-Death on ANY sky.
- **BOLD saturated palette per take** (6–8 colors), distinct between takes, NONE
  reusing the seed's void-violet/spectral-green.
- **Playful MENACE, not grim** — one charming "scary-cute" beat each. This is
  the single most important correction vs the prior round.
- Reuse `_shade_c`, `lerp_color`, `blit_glow`/`make_glow_surface` (BLEND_ADD);
  study `_mini_clown_face`, `build_jester`, `_marotte_ruff`, `_add_outline`.

A note on **FACELESS vs FACE**: the seed leaned faceless-void. In chibi house
style a totally empty hood reads as a hole, not a character — so most takes here
carry a *tiny expressive face read* (glowing pinprick eyes, a single fang, a
skull-grin, a smug glower). Faceless-void is preserved as ONE deliberate take
(#8) so the cull can weigh it against the cuter reads.

---

## Take 1 — "GRIM SPROUT" (the tiny reaper-imp)

1. **Thesis.** Death is a knee-high *baby reaper* — a roly-poly hooded imp who
   is far too small for the giant scythe he insists on dragging. Menace through
   comedy of scale: tiny terror, huge blade.
2. **Silhouette.** A fat low teardrop (oversized droopy hood lobe) with two
   stubby clawed feet poking out the bottom and a scythe-staff TALLER than the
   whole body angled across him. The disproportionate prop-to-body ratio is the
   instant "Death-but-cute" read — unmistakable even at 1×.
3. **Construction.** One big circle hood (40% of height) drooping to a long
   curl-tip, a small round belly nub overlapping under it, two pebble feet with
   3 ink claw-lines each, two stubby mitt arms (one up gripping the snath, one
   bracing it low). The hood mouth-shadow is a flat dark crescent, two pinprick
   eyes inside.
4. **Held prop — the GREAT-SCYTHE.** The straight **snath** is the pillar body:
   a chunky tapered pole with a banded grip wrap. It mirrors top↔bottom into a
   clean vertical post; the curved blade rides only the GAP-EDGE as a hooked
   flourish (per the seed's snath→pillar decision), bone-flat with a 1px lit
   inner edge. Tiles cleanly because the blade is a detachable gap-flourish.
5. **Palette (bold, distinct — "candy-poison").** Hood `#7B4FD8` orchid-violet,
   shade `#4E2E96`, sheen `#A98CF2`; belly/trim `#39E0C4` mint; claws/teeth
   `#FFF3C2` cream-bone; eyes `#FFE14A` glow-gold; snath `#B07A3A` warm wood;
   ink `#1C1620`. (Saturated orchid+mint candy pair — NOT the seed's dull violet.)
6. **Scary-cute hook.** Two glowing gold pinprick eyes + a single oversized
   fang poking up over the hood-shadow lip, and the wobble of a kid hauling a
   weapon five times his size.

```
  rough:   ▲           ← scythe tip
          (●)  /        hood + tiny scythe
          ▟▙ /          fat body, stub feet
          ʌʌ
```

---

## Take 2 — "TICK-TOCK" (the hourglass timekeeper)

1. **Thesis.** Death is a fussy little *bureaucrat of time* — a stout hooded
   clerk who doesn't reap, he just turns your hourglass over with a smug
   "time's up." Menace = patience, not violence.
2. **Silhouette.** A wide squat trapezoid robe (very low center of gravity) with
   a small flat-topped hood, and a tall slender **hourglass-on-a-staff** held
   vertically at his side — the pinched-waist hourglass profile is a silhouette
   no other take owns.
3. **Construction.** Trapezoid robe body (wide hem, narrow shoulders), small
   half-circle hood pulled low, two sleeve-stub arms (one cradling the staff,
   one tucked smugly behind his back). Flat sash belt across the waist with a
   ink keyline. Within the hood: a flat skull-pale crescent + two narrow eyes.
4. **Held prop — the HOURGLASS-STAFF.** A vertical pole capped by an hourglass:
   two stacked triangles meeting at a pinch, ink-keyed frame, sand-fill inside.
   Mirrors beautifully — the pinch-waist hourglass sits at the gap-edge as the
   "eye" of the pillar, the pole runs the full post. As a pillar the falling
   sand can even animate. Bold tiling silhouette (the hourglass bulge).
5. **Palette ("ink & amber").** Robe `#2B566E` deep teal-blue, shade `#173A4E`,
   sheen `#4E8AA6`; hood face `#F2E9D0` bone-cream; hourglass frame `#C8902E`
   brass, sand `#FFC23D` amber, sheen `#FFE49A`; sash `#D63E5A` rose; ink
   `#1C1620`. (Teal+brass+amber — owns the warm-metal family.)
6. **Scary-cute hook.** A smug sidelong half-lidded glower and one eyebrow-arch
   ridge, tapping the hourglass with a stubby finger like he's waiting for you
   to be late. The "I have all the time in the world; you don't" smirk.

---

## Take 3 — "CAPTAIN DAVY" (the jolly pirate-of-souls)

1. **Thesis.** Death is a swaggering *ghost-pirate ferryman* — he doesn't fear
   you, he's here to collect your fare and welcome you aboard with a grin. The
   most extroverted, jolliest Death in the set.
2. **Silhouette.** A barrel-chested chibi with a big **bicorne/tricorne hat**
   (the widest top-mass in the set — instantly not-a-hood), a peg-leg stance
   that hard-breaks symmetry, and a tall **oar/gaff-pole topped with a hanging
   ship's-lantern** held upright beside him.
3. **Construction.** Round head with a flat skull-grin face, big tri-point hat
   block on top, barrel torso with a coat-tail flare, one normal pebble boot +
   one peg-leg (a tapered wood spike — the asymmetry engine), two mitt hands
   (one on the gaff, one cocked on the hip). Coat lapels + a wide belt buckle
   as flat ink-keyed shapes.
4. **Held prop — the SOUL-GAFF + LANTERN.** A tall ship's gaff/oar pole (the
   pillar body, with rope-whipping bands) topped by a square iron **soul-lantern**
   with a wisp curling inside. Mirrors into a vertical post; the lantern rides
   the gap-edge as a glowing flourish (BLEND_ADD glow inside the glass via
   `blit_glow`). Rope bands read as pillar banding.
5. **Palette ("rum & brine").** Coat `#1F8A5B` viridian, shade `#10573A`, sheen
   `#46C98A`; hat/boots `#3A2A1E` dark-leather brown; skull/cuffs `#F4ECD6`
   bone-cream; lantern glow `#FF9E2C` ember-orange, sheen `#FFD27A`; sash/wisp
   `#43D6E0` cyan-soul; gold buckle `#FFC83D`; ink `#1C1620`. (Viridian+ember+
   cyan — owns the green-but-not-lime, warm-lantern family.)
6. **Scary-cute hook.** A wide gold-toothed skull GRIN with one gold fang, an
   eyepatch over one socket while the other socket glows cyan, and a hearty
   "welcome aboard!" tilt. Jolly to the point of unsettling.

---

## Take 4 — "WARDEN WISP" (the lantern-jailer herding souls)

1. **Thesis.** Death is a stern *soul-jailer* — a tall narrow hooded warden who
   herds little ghost-wisps with a caged lantern-pole, keeping the dead in line.
   Menace via authority + the captured wisps, not a blade.
2. **Silhouette.** The TALLEST, most vertical figure (a narrow column robe vs
   everyone else's squat builds — distinct on stance alone), with a long
   **caged-lantern pole** held dead-upright and 2–3 tiny round wisps orbiting
   his hem. Lantern cage + orbiting dots = unmistakable read.
3. **Construction.** A narrow tall robe column (still chibi — big head, but a
   long straight body), a pointed monk-cowl hood, two long sleeve arms (both on
   the pole, a two-handed warden grip). Three small wisp circles (each a glow
   dot + ink keyline) tethered around the feet. The hem flares to a flat base.
4. **Held prop — the CAGE-LANTERN POLE.** A tall pole (pillar body) topped by a
   barred iron **birdcage-lantern** with a trapped soul-wisp glowing inside.
   Mirrors into a vertical post; the cage rides the gap-edge, bars drawn as
   evenly spaced ink lines (great pillar texture), wisp glow via `blit_glow`.
   The bars give the pillar a unique grilled silhouette no other prop offers.
5. **Palette ("dusk indigo & ghost-green-gold").** Robe `#3C3A8C` indigo, shade
   `#262560`, sheen `#6A68C4`; hood face `#E8E2F4` pale; cage iron `#5A5566`
   slate, sheen `#8E8898`; wisp/lantern glow `#9BFF7A` ghost-lime-green (this is
   the ONE take that may flirt with green — but it's a SATURATED electric lime,
   the opposite of the seed's dull desaturated green); cuffs `#F4ECD6`; ink
   `#1C1620`. (Indigo+slate+electric-lime — owns cool-jailer family.)
6. **Scary-cute hook.** A single stern glowing eye-slit under the cowl + a
   disapproving brow-furrow, while a captured wisp inside the cage makes a tiny
   pleading :( face. The warden is grumpy, the prisoner is adorable.

---

## Take 5 — "DR. QUILL" (the plague-bird reaper)

1. **Thesis.** Death is a *plague-doctor BIRD* — a long-beaked physician
   reaper who has come to take your "appointment." Ties slyly to Skybit's macaw
   DNA: Death as a sinister cousin of the player-parrot.
2. **Silhouette.** The only BEAKED profile — a round head with a long downward
   plague-mask **beak** jutting forward (a silhouette spike no other take has),
   a wide flat-brim doctor's hat, a caped robe, holding a tall **cane/bone-
   syringe staff** upright.
3. **Construction.** Round head + huge curved beak cone (the read), flat wide-
   brim hat disc on top, two round goggle-lenses on the face, a short caped
   robe body with a high collar, two glove hands (one on the cane, one holding a
   tiny vial). Beady glow dots behind the goggle glass. Bird-foot talons peek at
   the hem to seal the bird read.
4. **Held prop — the BONE-CANE / APOTHECARY STAFF.** A tall doctor's cane (pillar
   body) with a coiled snake/ivy or a vial cluster at the top, OR a giant
   syringe-staff. Mirrors into a vertical post; the vial/ampoule rides the
   gap-edge glowing with a sickly tincture (`blit_glow`). Banded cane grip =
   pillar banding.
5. **Palette ("bile & wax").** Robe `#3E7D2E` apothecary-green, shade `#255017`,
   sheen `#6FBE54`; beak/hat `#E8C24A` waxen-gold, shade `#B0892A`, sheen
   `#FFE49A`; goggle glass `#E84D8A` magenta-tincture (the eyes glow); cape lining
   `#7A2BC8` violet; vial glow `#B6FF4A` toxic-chartreuse; ink `#1C1620`.
   (Apothecary-green+waxen-gold+magenta — owns the sickly-medical family.)
6. **Scary-cute hook.** Two big round goggle-lenses with glowing pink pinprick
   eyes that read like a curious, head-tilted bird saying "say aaah," plus the
   beak gives an unintentionally inquisitive cock. Creepy-cute clinical bird.

---

## Take 6 — "RATTLE-JACK" (the bone-jester / death harlequin)

1. **Thesis.** Death is a *court-jester of the crypt* — a skeleton harlequin who
   reaps by performance, capering with a bone-rattle scepter. Directly answers
   the warren clown as its dark twin: same costume grammar, skull where the face
   was.
2. **Silhouette.** A jester's lean contrapposto (cocked hip, dropped shoulder,
   reused `build_jester` pose) topped by a **two-point belled cap** and a flat
   **skull face**, holding a tall **skull-topped marotte/rattle** upright — but
   where the warren marotte has a mini-clown, this has a mini-SKULL bauble.
3. **Construction.** Direct `build_jester` lineage: harlequin two-tone legs,
   panelled costume torso, scalloped/belled collar (`_marotte_ruff`), pointed
   cap with bell-tips, presenting pose. Swap the cream clown face for a flat
   skull-pale face with hollow sockets + a stitched grin. The mini-marotte head
   becomes a tiny skull with bell-cap.
4. **Held prop — the SKULL-MAROTTE / RATTLE-STAFF.** Literally the warren
   marotte grammar (barber-twist shaft → `_marotte_ruff` collar → bauble), but
   the bauble is a grinning mini-skull in a belled cap. Mirrors into a vertical
   post EXACTLY like the existing jester-staff pillar (`pillar_staff.py` is the
   proven path) — lowest integration risk of the set; the skull-bauble rides the
   gap-edge.
5. **Palette ("crypt harlequin — bruise & bone").** Costume dark `#5A2A7A`
   royal-purple, light `#E54A8C` hot-magenta (the two-tone harlequin split),
   sheen on each via `_shade_c(+55)`; bone/skull `#F4ECD6` cream, shade
   `#C8B89A`; cap-bells + ferrules `#FFC83D` gold, sheen `#FFE49A`; socket-glow
   `#36E0FF` cold-cyan; ink `#1C1620`. (Purple+magenta+gold+cyan — owns the
   carnival-bruise family, loud and circus-y.)
6. **Scary-cute hook.** A skull with a stitched-on grin, ONE gold tooth, and
   cold-cyan pinprick eyes in the sockets glancing sidelong — plus the goofy
   belled cap flopping. It's the warren clown's mischievous energy wearing a
   skull mask: pure scary-cute.

---

## Take 7 — "BIG REAPY" (the towering boss-skull in a cloak)

1. **Thesis.** Death is a *giant grinning SKULL* wearing the cloak like a tiny
   poncho — the head IS most of the body. The pure boss-scale "oh no it's huge"
   read; menace via sheer head-mass and a toothy grin.
2. **Silhouette.** A colossal round skull dominating ~55% of the figure (the
   biggest head-ratio in the set), perched on a tiny cloaked body with stubby
   feet, flanked by a tall **bone-trident / bident scythe-fork** held upright.
   The giant-circle-on-tiny-body read is unique.
3. **Construction.** One huge skull circle (jaw, two big round sockets, a flat
   tooth-row band across the lower face), a small triangular cloak draped under
   it with two stub arms, tiny feet. The skull gets the full triad: dark-core
   ring, bone fill, top-left sheen — so the giant head reads sculpted-but-flat.
4. **Held prop — the BONE-BIDENT / FORK-SCYTHE.** A tall bone shaft (pillar body)
   splitting at the top into a two-prong fork (a soul-catcher), each prong a
   hooked bone. Mirrors into a vertical post; the fork rides the gap-edge as a
   menacing pronged flourish. Vertebra-bumps along the shaft = pillar banding.
5. **Palette ("ember-bone & ash-blue").** Skull/bone `#F0E6CE` warm bone, shade
   `#C2AE84`, sheen `#FFF7E0`; cloak `#37485E` ash-blue-slate, shade `#21303F`,
   sheen `#5E7892`; socket-fire `#FF6A2C` ember-orange glow, inner `#FFC23D`;
   tooth-line ink + jaw shadow `#1C1620`; collar trim `#C8902E` brass. (Warm-bone
   dominant + ash-blue + ember-orange — owns the classic-skull warm family.)
6. **Scary-cute hook.** A massive jack-o-grin with two big square teeth and
   glowing ember eyes in deep round sockets that, because they're so big and
   round on a chibi head, read more "excited puppy" than terror — a giant skull
   that seems delighted to see you.

---

## Take 8 — "THE HOLLOW" (the faceless cosmic void-shroud)

1. **Thesis.** Death is *the void wearing a shape* — a faceless hooded shroud
   whose interior is pure starlit emptiness. The one deliberately FACELESS take,
   preserving the seed's core idea but re-cut to chibi-flat with bold color so
   it's cosmic-cute, not grim-realistic. Menace via the unknown.
3. **Thesis-distinct beat.** Where the seed dissolved into smoke (off-style soft
   blur), THIS hollow ends in a hard chibi **scalloped hem** (flat lobes, ink-
   keyed) — no feathering. The void inside the hood is a FLAT black field with a
   few hard-pixel star dots, not a soft gradient.
2. **Silhouette.** A classic broad teardrop hood-and-shoulders (the archetypal
   Death cloak) but SHORT and round-shouldered (chibi), with a hard scalloped
   wavy hem, holding a tall **candle-snuffer pole / soul-staff** upright. Clean
   hooded-cloak read — the canonical Death silhouette done cute.
3. **Construction.** Big hood arch (a circle with a deep flat-black face cavity),
   round shoulders sloping into a bell-shaped robe, a scalloped lobe hem (reuse
   the `_marotte_ruff` lobe grammar inverted as a hem), two sleeve-stub arms on
   the pole. Inside the black void: 3–4 hard white/cyan star-pixels + two faint
   pinprick "almost-eyes" (so it's eerie, not a literal hole).
4. **Held prop — the SNUFFER-POLE / SOUL-CANDLE STAFF.** A tall pole (pillar
   body) topped by a bell-shaped candle-snuffer cone with a tiny soul-flame
   peeking under its rim, OR a guttering soul-candle. Mirrors into a vertical
   post; the snuffer-bell rides the gap-edge, the flame glow via `blit_glow`.
   Pole rings = pillar banding.
5. **Palette ("midnight & starfire" — bold, NOT the seed's dull violet).** Shroud
   `#2A2348` deep-midnight (saturated indigo-black, but with real chroma), shade
   `#15112A`, sheen `#473C72` (a clearly violet rim, not grey); hem trim + pole
   `#F0E6CE` bone; void stars `#7FE8FF` electric-cyan + `#FFFFFF`; snuffer-flame
   `#FF4FA8` soul-pink glow; collar `#C8902E` brass. (Midnight-indigo + electric-
   cyan + soul-pink — saturated cosmic, deliberately NOT desaturated.)
6. **Scary-cute hook.** Two faint cyan pinprick "eyes" deep in the star-field
   void that blink, and the absurd tininess of the chibi shoulders under the
   big spooky hood — a pocket-sized cosmic horror. Empty but endearing.

---

## Distinctness self-check

No two takes collide on silhouette, archetype, prop, AND palette-family
simultaneously — each row is unique on multiple axes.

| # | Take | Silhouette read | Archetype (KIND of Death) | Signature prop | Palette family |
|---|------|-----------------|---------------------------|----------------|----------------|
| 1 | Grim Sprout | tiny fat hood, giant blade across it | baby reaper-imp (comedy of scale) | great-scythe (snath pillar, blade gap-flourish) | orchid-violet + mint candy |
| 2 | Tick-Tock | wide squat trapezoid + pinch-waist glass | bureaucrat of time | hourglass-staff (pinch sits at gap-eye) | teal-blue + brass + amber |
| 3 | Captain Davy | barrel body + wide tricorne + peg-leg | jolly pirate-ferryman | soul-gaff + iron lantern | viridian + ember-orange + cyan |
| 4 | Warden Wisp | tall narrow column + caged pole + orbit dots | soul-jailer warden | cage-lantern pole (barred pillar) | indigo + slate + electric-lime |
| 5 | Dr. Quill | round head + long plague BEAK + brim hat | plague-doctor bird (macaw cousin) | bone-cane / vial-staff | apothecary-green + waxen-gold + magenta |
| 6 | Rattle-Jack | jester contrapposto + belled cap + skull | crypt-jester / death harlequin | skull-marotte rattle (proven pillar path) | royal-purple + hot-magenta + gold + cyan |
| 7 | Big Reapy | GIANT skull (~55%) on tiny cloak | towering boss-skull | bone-bident / fork-scythe | warm-bone + ash-blue + ember-orange |
| 8 | The Hollow | broad hooded teardrop, hard scallop hem | faceless cosmic void-shroud | snuffer-pole / soul-candle | midnight-indigo + electric-cyan + soul-pink |

**Cross-checks for the trap of "one base, eight dresses":**
- *Build/stance differ:* squat-trapezoid (#2), barrel+peg (#3), tall column (#4),
  jester-contrapposto (#6), giant-head (#7), classic-hood-bell (#1, #8), beaked
  caped (#5). No two share a body block.
- *Head read differs:* drooping hood (#1), flat hood-skull (#2), tricorne skull
  (#3), monk-cowl slit (#4), beaked goggle (#5), belled-cap skull (#6), giant
  jack-skull (#7), star-void hood (#8).
- *Prop differs:* scythe / hourglass / gaff-lantern / cage-lantern / cane-vial /
  skull-rattle / bone-bident / snuffer-candle — eight different pillar
  silhouettes (smooth post, pinch-eye, lantern-box, barred grille, vial-cluster,
  twist-marotte, pronged fork, snuffer-bell).
- *Palette families are disjoint:* candy-orchid / teal-amber / viridian-ember /
  indigo-lime / apothecary-magenta / carnival-bruise / bone-ash-ember /
  midnight-cyan-pink. Only #4 and the seed touch green at all, and #4's is a
  SATURATED electric-lime (explicitly the inverse of the seed's dull green);
  #8 owns the violet/indigo space but as a SATURATED midnight-cosmic, not the
  seed's desaturated void.
- *Face strategy spread:* glowing-pinprick (#1, #6), smug-glower (#2),
  skull-grin (#3, #7), stern eye-slit (#4), goggle-bird (#5), faceless-void (#8)
  — the cull gets a real range from cute-eyed to fully hollow.

**Render note.** Rough thumbnail silhouettes were NOT committed this turn
(brainstorm priority is the text theses, and the orchestrator handles all
commits). The 8 ASCII-rough reads above stand in for thumbnails; a later
maturing loop renders each take with the real helpers
(`_shade_c`, `_marotte_ruff` triad, `_add_outline`, `blit_glow`).

---

## ART-DIRECTOR CULL

**Verdict on the set:** Strong brainstorm. These are genuinely 8 different KINDS
of Death, not one robe in eight colors — build, head-read, prop, and palette all
move together across the table, which is the trap this exercise usually falls
into. The faceless-vs-face question was handled correctly (one deliberate hollow,
the rest carry a tiny expressive read; an empty hood at 1× on a night sky reads
as a dropout hole, not a character). The set clears the bar to cull to 5.

`VERDICT: SHIP-READY` (brainstorm locked — proceed to mature the 5 below)

### Final 5 to pursue, in order

1. **#1 GRIM SPROUT** — the comedy-of-scale read (tiny imp + oversized scythe) is
   the single most instantly legible "Death-but-cute" silhouette in the set, and
   the scythe is the canonical Death prop. Snath-as-pillar + blade-as-gap-flourish
   is the cleanest tiling story here. Anchor pick.
2. **#7 BIG REAPY** — the deliberate SCALE OPPOSITE of #1 (giant 55% skull on a
   tiny body vs tiny body + giant prop). Owns the towering boss-scale beat the
   roster wants, and the warm-bone palette is the only place a classic skull lives.
3. **#5 DR. QUILL** — the only BEAKED profile and the only take that ties to
   Skybit's macaw DNA (Death as the parrot's sinister cousin). That thematic hook
   plus a silhouette spike no other take owns makes it the most ORIGINAL pick.
4. **#2 TICK-TOCK** — the non-blade archetype (menace via patience, not violence)
   and the pinch-waist hourglass is a pillar silhouette nobody else owns — with a
   built-in animation hook (falling sand). The smug-glower face anchors the
   "scary-cute, not grim" mandate better than any other.
5. **#8 THE HOLLOW** — the canonical hooded-cloak Death done chibi, and the one
   deliberate FACELESS take. Keep it for spread: the set needs a pure-hood read to
   contrast the imp / giant-skull / beak / clerk. The hard-scallop-hem + flat-void-
   with-star-pixels rewrite is exactly the right correction to the seed's soft blur.

### The 3 cuts

- **#6 RATTLE-JACK — CUT.** This is the hardest call and the most important. By its
  own thesis it is "the warren clown's dark twin: same costume grammar, skull where
  the face was," reusing `build_jester` + `_marotte_ruff` + the literal marotte→pillar
  path. Looking at `round_17_final.png`, that is too close: same contrapposto, same
  belled cap, same scalloped ruff, same barber-twist marotte staff with a bauble-head
  on top. At 1× scrolling, a skull-bauble marotte and a clown-bauble marotte read as
  the SAME pillar with a recolor — a direct silhouette + prop collision with shipping
  art. The "proven path = low integration risk" argument is real but it's an
  ARGUMENT FOR A RESKIN, not for a distinct boss. A Death boss that players read as
  "the clown again" is the one failure mode this roster can't afford. Cut on
  identity-collision with the anchor.
- **#3 CAPTAIN DAVY — CUT.** Strongest of the cut three, but it collides on two
  axes with picks already in: it's a skull-grin face (overlaps #7 BIG REAPY's
  jack-o-grin) AND a lantern-prop (overlaps #4 WARDEN WISP, see swap note). Beyond
  the overlap, the pirate read pushes "jolly costume character" harder than "Death"
  — at 1× the tricorne + peg-leg says swashbuckler, and the Death thesis is the
  weakest-carried of the eight. Cut as the redundant skull-grin and the weakest
  Death-read.
- **#4 WARDEN WISP — CUT.** Genuinely distinct on stance (the only tall column) and
  I considered swapping it IN. But two real risks sink it for a first batch: (a) the
  orbiting wisp-dots + caged prisoner are FINE DETAIL that turns to noise at gameplay
  scale — three tiny tethered glow dots around the hem will read as render dirt at
  1×, fighting the "legibility beats detail" rule; (b) it's the take most at risk of
  sliding back to grim (stern jailer, caged prisoner, indigo) — the exact tonal
  failure we're correcting. Its electric-lime is also the one palette flirting with
  the seed's green. Cut as the highest noise + grim risk.

### Swap I made to preserve distinctness

My instinct was to keep #4 over #2 for the tall-column stance. I swapped **#2
TICK-TOCK in over #4 WARDEN WISP** because:
- Both are non-blade authority archetypes, but #2's hourglass is a far stronger,
  cleaner tiling silhouette than #4's barred cage (the cage bars + orbiting dots are
  noise at 1×; the hourglass pinch is a bold single read).
- #2's smug-clerk face is the safest "scary-cute not grim" beat in the set; #4 is
  the grim-risk take.
- Distinctness on stance is preserved another way: #4's tall column is gone, but the
  final 5 still span squat-imp (#1), giant-head (#7), beaked-caped (#5), squat-
  trapezoid (#2), and broad-hood-bell (#8) — no two share a body block.

### Distinctness audit — the chosen 5 on all four axes

| Pick | Silhouette | Archetype | Signature prop | Palette family |
|------|-----------|-----------|----------------|----------------|
| #1 Grim Sprout | tiny fat hood, giant blade across body | baby reaper-imp (comedy of scale) | great-scythe (smooth snath post + gap-edge blade) | orchid-violet + mint candy |
| #7 Big Reapy | GIANT skull (~55%) on tiny cloak | towering boss-skull | bone-bident / fork-scythe (pronged) | warm-bone + ash-blue + ember |
| #5 Dr. Quill | round head + long plague BEAK + brim | plague-doctor BIRD (macaw cousin) | bone-cane / vial-staff (vial cluster) | apothecary-green + waxen-gold + magenta |
| #2 Tick-Tock | wide squat trapezoid + pinch-waist glass | bureaucrat of time (no blade) | hourglass-staff (pinch = gap-eye) | teal-blue + brass + amber |
| #8 The Hollow | broad hooded teardrop, scallop hem | faceless cosmic void-shroud | snuffer-pole / soul-candle (bell cone) | midnight-indigo + electric-cyan + soul-pink |

- **Silhouette:** tiny-imp / giant-head / beaked / squat-trapezoid / broad-hood —
  five distinct body blocks, no collision.
- **Archetype:** imp / boss-skull / bird-doctor / time-clerk / void-shroud — five
  different KINDS of Death.
- **Prop:** scythe / bone-fork / vial-cane / hourglass / snuffer-candle — five
  distinct pillar silhouettes (smooth post, pronged fork, vial cluster, pinch-eye,
  snuffer-bell). All tile vertically; none reuse the clown's twist-marotte.
- **Palette:** candy-orchid / bone-ash-ember / apothecary-magenta / teal-amber /
  midnight-cyan-pink — five disjoint families. No two collide. None reuse the seed's
  desaturated void-violet/spectral-green; #8 owns the indigo space but as SATURATED
  cosmic, and the cut of #4 removes the only electric-lime that flirted with the seed.

No pair collides on all four axes — no collision required a further swap beyond
#2-for-#4. Spread check passes: face strategy ranges cute-pinprick (#1) → smug-glower
(#2) → giant jack-grin (#7) → curious goggle-bird (#5) → faceless-void (#8); scale
ranges knee-high imp (#1) → towering boss (#7).

### Per-pick guardrails (the one risk the maturing loop must watch on each)

1. **#1 GRIM SPROUT** — keep the prop-to-body ratio EXTREME. The whole read is
   "blade dwarfs imp"; if the scythe shrinks toward realistic proportion it becomes
   a generic small reaper and loses its identity. Confirm the snath reads as a clean
   tileable vertical post with the blade detachable to the gap-edge ONLY (don't let
   the curved blade bleed into the tiling body).
2. **#7 BIG REAPY** — police the grin so the giant skull reads "delighted puppy,"
   not horror-movie. Big round sockets + ember eyes on a chibi head is the scary-cute
   lever; a wide menacing rictus tips it grim. Also watch night-sky legibility — a
   warm-bone skull can flatten against a dark sky, so the ash-blue cloak and ink
   keyline must hold the silhouette.
3. **#5 DR. QUILL** — do NOT let it collide with the player macaw. It must read as
   the parrot's SINISTER COUSIN (plague-doctor uncanny), not a recolored hero bird.
   Lean on the long straight plague-beak (not the macaw's hooked beak), the brim hat,
   and the goggle lenses to separate them. Keep the sickly palette clearly off the
   hero's bright primaries.
4. **#2 TICK-TOCK** — make the hourglass unmistakable as a tileable vertical: the
   pinch-waist must sit at the gap-eye and the pole run the full post. Watch that the
   amber sand and brass frame keep enough value contrast against a day sky (warm-on-
   warm risk) — the ink keyline and teal robe carry the silhouette. Keep the smug-
   glower charming, not a sneer.
5. **#8 THE HOLLOW** — the void must NOT read as a transparency dropout / dead hole
   at 1×. The faint cyan pinprick "almost-eyes" + a few hard star-pixels are
   load-bearing; without them it's an empty silhouette. And hold the line on the hard
   scalloped hem + flat-black-with-pixels void — zero feathering, zero soft gradient.
   This is the take that most wants to slide back into the seed's grim-realist finish;
   it must stay saturated-cosmic-cute.

### Accessibility note for all 5

Several picks lean on a glow color to carry the "eyes/soul" read (gold #1, ember #7,
magenta #5, amber #2, cyan #8). Never let that hue be the ONLY thing distinguishing
the face — the dark socket/keyline shape must read in grayscale too, so colorblind
players and low-contrast night skies still get the character. Confirm each at 1× as a
black-and-white silhouette during the maturing loop.
