# Japanese-totem family — brainstorm (GD, Phase A)

Seeded from **`moai_ancestor`** (the winner). Every direction below KEEPS the
reusable skeleton verbatim and only re-skins the relief + materials + crown:

- `_draw_tower` stack driver, `_hw_at` half-width profile, `_HEAD_H_FLOOR=92`
  height-adaptive head COUNT (1 big face ~70px → several at 355px), hidden
  full-width core fill guarantee, neck-waist seams, `_draw_plinth`, the harness
  (`_max_empty_run` fill gate, `_gap_rim_clearance`, `_blackout`, vertical-flip
  mirror). **Each "ancestor head" becomes one carved Japanese MASK.**
- Relief `_draw_head` → a Japanese MASK-face builder (paint planes instead of
  carved basalt planes). Body triad `_body_triad`/`_scoria` → Japanese
  lacquer/porcelain/iron/gold materials, all `_mix(palette[key], anchor, t)` +
  lit/shadow so the 5-min day→night retint sweeps straight through.
- Faces reuse the `_buddha_eye` stack (retinted to mask paint) + `_lit_niche`
  eye/mouth sockets, with a **2-dot thumbnail fallback** so the mask still reads
  at 58px. `_gradient_rect` every panel, `_aa_polyline` every silhouette edge.
- Pukao `_draw_pukao` crown → a Japanese TOPPER (horns / tokin cap / fox-ears /
  helmet crest / dish-rim / hair-mass), sized ~1.15–1.25× the crown so the
  blackout keeps the "gaunt post + distinct wide topper" moai tell, overhang
  living in the 64px eave/ornament MARGIN gutter so it never widens the 58px
  collision band.

The MIX: **5 traditional MASK stacks + 2 non-mask directions** for silhouette
spread. The 7 are pushed apart on SILHOUETTE-as-solid-black first
(horns-back / horns-forward+grin / long-nose / fox-ears / beak+dish /
round-beaded / lumpy-irregular). AD culls to 5.

---

## 1. `oni_kanabo` — MASK · KIND-tag: BACKSWEPT-HORNS BRUTE

**Thesis:** A tower of snarling iron-and-vermilion oni demon heads, each pair of
thick bull horns sweeping BACK off the skull like a stack of gargoyles.

- **Silhouette-tell:** two THICK, blunt horns per head raking up-and-BACK (a wide
  shallow "V" opening rearward), a broad brute jaw wider than the temple, brow
  boss bulging forward. Reads as a knuckled column with backswept antler-pairs —
  brute, top-heavy, angry.
- **Mask/face construction:** heavy over-hanging brow boss (reuse the moai shelf
  poly, fattened), huge round bulging eyes via `_buddha_eye` retinted to gold-on-
  black glare, a flat pug snout with two `_lit_niche` nostril pits, a wide snarl
  mouth with two upward FANGS (small `_gold_bright` triangles). Horns are filled
  `_aa_polyline` wedges springing from the temples into the gutter.
- **Materials:** skin `_vermilion` (stone_dark) triad with `_vermilion_lit` raking
  highlight + `_vermilion_shadow` in the socket recesses; horns + fangs + brow
  studs `_iron_brown` (stone_dark) tipped `_gold_bright` (stone_accent); mane
  tufts `_lapis`-deep-`_shade` near-black indigo.
- **Crown/topper:** a knotted **wild-hair / kanabō-club** cap — a spiked
  `_iron_brown` studded drum with a gold band, presenting a solid wide flat edge
  at the gap rim (replaces the pukao drum 1:1).
- **Column-fill + mirror:** brute jaw is full-width → fills the 58px band solidly;
  horns are pure gutter overhang. Near-symmetric about the vertical axis → clean
  ceiling flip (backswept horns just point the other way, still oni-legible).

```
   \__      __/        backswept horns
    (o    o)           bulging gold eyes
     \ vv /            fanged snarl
    [######]           full-width brute jaw (58px band)
```

---

## 2. `hannya_grudge` — MASK · KIND-tag: FORWARD-HORNS + ANGUISHED GRIN

**Thesis:** The jealous-spirit hannya — two SLENDER horns curving FORWARD over an
anguished, metal-toothed grin; sickly bone-flesh, not demon-red. The deliberate
hard-differentiation from Oni.

- **Silhouette-tell:** two thin sharp horns set CLOSE together, curving up-and-
  FORWARD (a narrow forward-tilting "V"), and — the killer tell — a wide down-
  turned GRIN whose bared teeth break the lower silhouette into a serrated band.
  Narrow-topped, jagged-mouthed. Opposite geometry to Oni's wide backswept brute.
- **Mask/face construction:** high arched anguished brows (thin `_aa_polyline`
  peaks), narrow slit-glare eyes via `_lit_niche` under gold rims, a pinched
  ridge nose, and a grinning mouth stretched ear-to-ear with a full row of
  `_gold_bright` teeth + two side fangs (the metallic-teeth signature). Furrow
  lines rake the cheeks.
- **Materials:** skin `_plaster`/`_porcelain_cream` (stone_light) pushed toward a
  sickly ochre with a `_terracotta` blush at the cheekbones — bone-flesh, NOT
  vermilion; horns `_bronze`→`_gold_deep` (stone_accent) two-tone; teeth
  `_gold_bright`; hair `_lapis` deep-indigo mane framing the temples.
- **Crown/topper:** a swept-back **indigo hair-mass knot** (`_lapis` + deep
  `_shade`) with a single small gold pin, tapering to a solid wide rim edge —
  quieter than Oni's studded club so the two horned masks don't twin at the cap.
- **Column-fill + mirror:** grinning jaw full-width fills the band; the toothed
  mouth-break is interior relief, not a silhouette gap. Forward horns are gutter
  overhang, near-symmetric → clean flip.

```
    \\  //            slender FORWARD horns, close-set
    (=  =)            narrow slit eyes, gold rims
   /wwwwww\           ear-to-ear grin, gold teeth (serrated tell)
    [####]            full-width jaw (58px band)
```

---

## 3. `tengu_yamabushi` — MASK · KIND-tag: LONG-NOSE

**Thesis:** The crimson long-nosed mountain-goblin tengu — one enormous phallic
NOSE juts straight out of every face, a stack of yamabushi ascetics' masks.

- **Silhouette-tell:** a single dominant NOSE spearing forward-and-down from the
  center of each head (a long horizontal spur), no horns, no ears — the anti-Oni,
  anti-Hannya read. Column reads as a smooth post skewered by repeated forward
  beaks-of-nose. Unmistakable and unlike anything else in the set.
- **Mask/face construction:** furious scowl brows, round bulging eyes via
  `_buddha_eye` (angry gold), and the hero feature: a long tapering nose wedge
  (extend the moai nose-ridge poly WAY out past the cheek into the gutter, lit
  top plane / shadow underside via `_gradient_rect`), a bristled moustache + a
  down-set frown mouth beneath it.
- **Materials:** face deep `_lacquer_red`/`_vermilion` (stone_dark) — a darker,
  cooler crimson than Oni's bright vermilion so they don't twin on hue; nose lit
  edge `_vermilion_lit`; brows + moustache `_lapis` near-black; a `_gold_deep`
  brow-jewel.
- **Crown/topper:** the little black **tokin** pillbox cap of the yamabushi —
  a small `_lapis` hexagon drum with a `_gold_bright` cord — plus one upright
  crimson-and-white **feather** as the maedate spike (solid wide rim edge from
  the pillbox base).
- **Column-fill + mirror:** face + cheeks full-width fill the band; the long nose
  is horizontal gutter overhang (watch it doesn't pinch the neck seam — keep the
  nose ABOVE the waist). Vertical-symmetric face → clean flip; the nose points
  down on the flipped ceiling copy, still unmistakably tengu.

```
     (o  o)           angry round eyes
      |====>          long forward NOSE spur (the whole tell)
      /~~\            bristled frown
     [####]           full-width face (58px band)
```

---

## 4. `kitsune_inari` — MASK · KIND-tag: FOX-EARS + SNOUT (WHITE)

**Thesis:** The white Inari fox — tall pointed EARS and a tapered snout, porcelain
white with vermilion swirl markings and gold trim; a shrine-fox totem.

- **Silhouette-tell:** two tall, sharp, upright triangular EARS per head (a
  narrow upward "V", pointy not blunt like Oni's horns) plus a gently tapered
  muzzle poking below. Reads as a column of alert triangular ear-pairs — sleek,
  pointed, pale. Distinct from horns (ears are taller/thinner/upright) and
  from the nose spur.
- **Mask/face construction:** smooth planar fox face (less carved than the demons
  — porcelain calm), narrow up-slanted eyes via `_lit_niche` ringed in vermilion
  liner, a small black nose-dot at the muzzle tip, a delicate closed mouth. Ears
  are filled triangles with a `_vermilion` inner-ear membrane.
- **Materials:** face `_porcelain_white` (stone_light, cool) triad; markings
  (eye-liner, cheek swirls, ear insides, forehead flame-crest) `_vermilion`
  (stone_dark); ear-tips + brow crest + whisker studs `_gold_bright`
  (stone_accent). The porcelain-white + vermilion + gold = the Inari palette.
- **Crown/topper:** a **flaming jewel (hōju) between the ears** — a small
  `_gold_bright` teardrop on a `_vermilion` base drum, ears framing it, solid
  wide rim edge. (Ears themselves are gutter overhang, the jewel-drum is the
  gap-rim presenter.)
- **Column-fill + mirror:** cheeks/muzzle full-width fill the band; ears are
  narrow gutter overhang. Perfectly bilateral → clean flip; ears point down on
  the ceiling copy but the white-fox read survives.

```
     /\  /\           tall pointed EARS
    (  ><  )          slant eyes, vermilion liner
      \__/            tapered white muzzle
     [####]           full-width cheeks (58px band)
```

---

## 5. `kappa_suijin` — MASK · KIND-tag: BEAK + HEAD-DISH

**Thesis:** The water-imp kappa — a turtle-beaked green face crowned by the
concave **sara** water-dish; a river-spirit totem, jade-and-porcelain.

- **Silhouette-tell:** a protruding turtle BEAK (a forward diamond, not a long
  spur like tengu's nose — shorter, wedge-lipped) and the unique CONCAVE DISH
  crown — the top of each head DIPS into a shallow bowl instead of bulging. The
  only inward-domed topper in the set; unmistakable.
- **Mask/face construction:** a low domed cranium, big round wet eyes via
  `_buddha_eye` (dark iris), a hard keratin beak (two filled `_gradient_rect`
  wedges meeting at a lit edge, replacing the moai lip shelf), sunken cheeks.
  The sara dish is a shallow `_lit_niche`-style concave ellipse holding a bright
  water glint.
- **Materials:** skin moss-jade — the cool-green `_porcelain_aqua` /
  `_porcelain_panel_teal` family pulled toward `stone_mid` so it reads amphibian-
  green, not tile-blue; beak + shell-scutes `_bronze`→`_gold_deep` (stone_accent);
  dish water `_porcelain_white` glint with a `_lapis` shadow pool.
- **Crown/topper:** the **sara dish** itself — a `_bronze`-rimmed concave bowl
  with a porcelain-white water disc, sitting flat and WIDE at the gap rim (the
  concave face still presents a solid rim silhouette, just dished on top).
- **Column-fill + mirror:** domed head + jaw fill the band; beak is short gutter
  overhang. The concave dish must still present a solid rim at the gap line —
  fill the bowl underside so no >12px empty run opens under it. Bilateral → clean
  flip; on the ceiling copy the dish domes up, reading as the belly-shell — still
  coherent.

```
    (~~~~)            concave sara water-DISH (inward tell)
    (O  O)            round wet eyes
     <##>             turtle BEAK wedge
    [####]            full-width jaw (58px band)
```

---

## 6. `daruma_gankake` — NON-MASK · KIND-tag: ROUND-BEADED (EYELESS RED)

**Thesis:** A stack of round-bottomed **Daruma** wish-dolls — bright red weighted
spheres with gold-outlined blank eyes; the deliberately ROUND, smooth, non-carved
counterpoint to all the angular masks.

- **Silhouette-tell:** a beaded column of near-CIRCLES — each head a squat round
  weighted ovoid with only a shallow neck pinch between (the moai waist read but
  rounder), no horns/ears/nose at all. Smooth, bulbous, symmetric. The round
  blackout is its whole identity (and is intentional Daruma, not the accidental
  bulbous moai the seed warns against — read via the flat gold face + brow, not
  a carved profile).
- **Mask/face construction:** a broad flat painted FACE zone on the round body —
  bushy gold-and-black eyebrows (crane) and a moustache (turtle) as bold
  `_aa_polyline` sweeps, and two big BLANK white eye-discs with NO pupils (the
  gankake un-filled-eye custom) via `_buddha_eye` retinted to plain white rings.
  A gold kanji medallion on the belly.
- **Materials:** body `_lacquer_red`/`_vermilion` (stone_dark) with a strong
  `_vermilion_lit` left-lit sheen (papier-mâché gloss); face patch
  `_porcelain_cream` (stone_light); brows/moustache `_lapis` deep + `_gold_deep`;
  medallion + eye-rims `_gold_bright` (stone_accent).
- **Crown/topper:** almost none — a small gold-lacquer **crown-knot / incense
  swirl** cap, low and rounded, so the topper stays sub-1.2× and the round read
  isn't spiked. Presents a solid rounded rim at the gap.
- **Column-fill + mirror:** rounded body is full-width at its belt → fills the
  band; the round taper top/bottom must not open a >12px empty run at the seam —
  keep the pinch shallow (rounder, shorter waist than moai). Fully symmetric →
  the cleanest flip in the set.

```
     (  )             low crown knot
    (o  o)            BLANK eyeless white discs, gold rims
    ( ww )            gold brow + moustache
   ( ###### )         round weighted body (58px band)
```

---

## 7. `yokai_hyakki_pole` — NON-MASK · KIND-tag: LUMPY-IRREGULAR (MANY-SMALL)

**Thesis:** A **hyakki-yagyō** night-parade pole — MANY small mismatched yōkai
faces swarming up the post (a one-eyed, a long-necked, a horned imp, a lantern-
ghost), so the silhouette is knobbly and asymmetric, not a clean repeated mask.
The construction variant: many small faces instead of few big ones.

- **Silhouette-tell:** a busy, LUMPY, off-axis column — little stray horns,
  tongues, ears and eyestalks poking irregularly out of both gutters at
  different heights, no two faces alike. The anti-symmetry is the tell; reads as
  a writhing goblin-totem, distinct from every clean bilateral mask above and
  from the retired formline pole (which is bold smooth ovoids, not comic imps).
- **Mask/face construction:** halve `_HEAD_H_FLOOR` so the adaptive count packs
  ~2× the faces; per face pick one of a small yōkai kit — a single central
  `_buddha_eye` cyclops, a `_lit_niche` gaping mouth with a lolling `_vermilion`
  tongue, a one-horn imp, a round lantern-ghost — alternating left/right so the
  overhangs stagger. Small scale → lean hard on the 2-dot thumbnail fallback.
- **Materials:** a mixed but harmonized set drawn per-face from the same keys —
  `_vermilion` red imps, `_porcelain_aqua` ghost-pale spirits, `_iron_brown`
  bark-goblins, all trimmed `_gold_deep`; a `_lapis` twilight wash unifies them
  so the parade reads as one indigo-night pole, not confetti.
- **Crown/topper:** a **chōchin paper-lantern** finial — a round `_porcelain_
  cream` glow-lantern with a `_gold_bright` cap and `_vermilion` ribs, lit from
  within by a `_lit_niche` core, presenting a solid rounded rim at the gap
  (doubles as the one guaranteed-symmetric element for a stable flip anchor).
- **Column-fill + mirror:** the core faces stay full-width to hold the 58px band
  solid (stray limbs are gutter-only); the risk is a >12px gap where a small face
  necks in — enforce the hidden full-width core fill under every yōkai. At short
  heights the adaptive count collapses to 1–2 faces + lantern, so the busy read
  is a tall-tower reward, not a 70px liability. Asymmetric faces mean the flip
  won't mirror cleanly — rely on the symmetric lantern finial as the flip anchor
  and accept the body reshuffles (acceptable for a "parade" whose disorder is the
  point). **Feasibility caveat flagged for AD.**

```
    (====)            chōchin lantern finial (symmetric anchor)
   o< (O) \_          cyclops + stray eyestalk
    _/(vv)            gaping mouth, lolling tongue
   /(o o)             one-horn imp, off-axis
    (###)             full-width cores (58px band), lumpy gutter
```

---

## CROSS-SET PINS — distinctness policing

- **Oni vs Hannya (the horned pair — the headline pin).** Both horned; keep BOTH
  only if these hold, else AD culls one:
  - *Geometry:* Oni = TWO THICK BLUNT horns raking BACK, wide brute jaw, top-heavy
    "V-opening-rearward." Hannya = TWO SLENDER SHARP horns close-set curving
    FORWARD, narrow top, jagged toothed grin. Opposite horn direction + jaw width.
  - *Face:* Oni = pug-snout snarl, few big fangs. Hannya = ear-to-ear full-tooth
    grin. Different mouth silhouette entirely.
  - *Material:* Oni = bright `_vermilion` demon-red + `_iron_brown` horns.
    Hannya = sickly `_plaster`/ochre bone-flesh + `_bronze`/`_gold` horns. Red
    vs bone — no hue twin.
  - *Crown:* Oni = studded iron kanabō-club. Hannya = quiet indigo hair-knot.
  - **Recommendation:** distinct enough to keep both; if AD wants only one, drop
    Hannya and promote `menpo_bushi` (iron war-mask, moustache-flare + faceted
    hinged jaw + golden kabuto maedate-crest crown — `_iron_brown`+`_gold_bright`)
    as the spare 5th mask.

- **Kitsune vs Hannya vs Daruma (the pale-face trio).** Kitsune = COOL
  `_porcelain_white` + vermilion markings + EARS. Hannya = WARM ochre/bone-flesh
  `_plaster` + horns + grin. Daruma = `_porcelain_cream` face patch on a RED
  round body, eyeless. Different base hue temperature AND different silhouette
  feature (ears / horns / round-eyeless) — no twin.

- **Tengu nose vs Kappa beak.** Tengu = LONG straight forward SPUR (extends far
  into the gutter). Kappa = SHORT wedge BEAK + the inward concave dish. Length +
  the dish disambiguate; don't let the kappa beak grow long.

- **Vermilion-red bodies (Oni / Tengu / Daruma) must not twin on hue.** Oni =
  BRIGHT `_vermilion` (stone_dark, high-sat). Tengu = DARKER cooler
  `_lacquer_red` crimson. Daruma = glossy `_lacquer_red` but ROUND + eyeless +
  gold face patch. Silhouette (horns / nose / round) already separates them;
  the hue split is the second guard.

- **vs retired totem set** (`totem_formline`, `moai_ancestor`, `jade_serpent`,
  `kota_reliquary`, `tiwanaku_stele`) **and shipped pagodas.** Formline is the
  closest neighbor to `yokai_hyakki_pole` (both stacked faces) — kept apart by
  shape language: formline = bold smooth ovoid/U-form glyphs; yōkai = comic
  irregular imps + lantern. Moai's gaunt smooth-vertical is closest to Daruma's
  smooth column — kept apart by round-beaded-vs-gaunt-angular + red-vs-basalt.
  Jade_serpent = coiled scaled serpent (no faces), kota = brass reliquary bust,
  tiwanaku = incised stone stele — none share a Japanese mask read.

- **Non-mask count.** Delivered 5 masks + 2 non-mask (`daruma_gankake`,
  `yokai_hyakki_pole`) per the user's MIX. If AD finds the yōkai pole's
  asymmetry too risky for the flip/58px fill, swap it for `menpo_bushi` (a 6th
  mask) and keep Daruma as the sole non-mask — noted so AD can steer.

- **Blackout / Swap / Cover-the-label / One-sentence:** each of the 7 passes —
  the solid-black silhouettes alone (backswept-horns / forward-horns+grin /
  long-nose / fox-ears / beak+dish / round-beaded / lumpy-irregular) are
  mutually unmistakable; no head from one drops legibly into another; each earns
  a one-sentence thesis above.
