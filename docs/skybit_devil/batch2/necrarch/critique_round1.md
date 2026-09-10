VERDICT: ITERATE

# Necrarch — round 1 critique (art-director)

A strong, on-palette FIRST pass with genuinely lich-y bones: the violet+bronze
read is unmistakable, the orb glow is gorgeous, and the crozier pillar mirror is
the cleanest deliverable on the sheet. But the headline brief promise — a "tall
hooded skull lich cradling a soul-orb" — does not survive contact with the 32px
read. Right now the small read is "a glowing orb wearing a purple poncho." The
skull, crown, and sleeve-cuffs all evaporate, and the orb has effectively eaten
the character. That is the gate issue. ITERATE.

## Ranking of the design's aspects (strongest -> weakest)

1. **Palette / SOLE-VIOLET identity (KEEP, near-perfect).** Royal-violet robe +
   deep-plum shade + arcane orb-glow + bronze crown land exactly on the pinned
   spec. This will not collide with any sibling — it owns violet. Don't touch the
   hues.
2. **Crozier soul-staff -> pillar mirror (KEEP).** Slim symmetric bone shaft with
   knuckle/rune banding, claw-finial caged orb as the gap cap, clean top<->bottom
   mirror. This is ship-quality and matches Big Reapy's grammar. Minor polish only.
3. **Orb rendering (KEEP the craft, FIX the dominance).** The triad on the orb
   (dark-core violet sphere -> light-violet halo -> saffron-white hot sheen) is
   beautiful and reads as "arcane energy" instantly. The problem is scale, not
   quality.
4. **Skull face at large size (MIXED).** The gaunt skull with sunken violet
   socket-glow is charming and correctly scary-cute at 3x. But the socket-glow is
   blown out to near-white and the sockets are drawn as hard square violet tiles —
   reads more "robot visor" than "glowing eye-sockets."
5. **The 32px silhouette (WEAKEST — this is the gate failure).** At gameplay size
   the character is an orb + a blob of purple. No skull. No crown spikes. No
   sleeve-cuffs. No legless-wisp taper that reads as a robe-hem — the bottom reads
   as two stubby legs/lobes. The four pinned silhouette tells (hooded skull /
   spiked crown / robe-wisp / cradled orb) must ALL survive at 32px and only one
   (the orb) currently does.

## KEEP

- Violet+bronze palette and the orb-glow triad — locked, do not drift.
- Crozier pillar: banding rhythm, claw-finial cap, symmetric mirror.
- The large skull's overall proportion and the chibi big-head intent.
- Hard flat fills + ink keyline + top-left rim-sheen triad discipline — house
  style is respected throughout.

## FIX (prioritized punch list for round 2)

1. **REUNITE the character — head and body are reading as two separate objects.**
   On the large render the skull sits ABOVE and the orb+robe sit BELOW with empty
   sky between them. The brief is ONE tall figure: hooded skull on top, robe
   falling from the shoulders below it, sleeve-cuffs cradling the orb at the CHEST
   (below the chin, not floating in a torso void). Stack into a single continuous
   silhouette — skull -> bronze crown -> narrow shoulders -> robe -> orb held at
   chest -> robe-wisp tail. The two-piece layout is the root cause of the 32px
   collapse.

2. **Shrink the orb to ~40% of its current diameter.** It is the single largest
   mass and out-glows the whole creature, so at 32px the lich IS the orb. The orb
   is the phylactery-HEART — a focal accent, not the body. Pull it to roughly one
   sleeve-cuff wide so the skull can dominate. Keep the glow but contain it
   (tighter falloff, less bloom) so it stops bleeding over robe and cuffs.

3. **Make the spiked bone CROWN survive at 32px.** Small, the crown reads as a
   flat bronze band with no spikes — a hat brim, not a horned bone crown. Give it
   3 bold triangular spikes (center + two flanking) tall enough to break the head
   silhouette by ~3-4px at 32px. The crown is one of the four pinned tells; it
   must notch the outline.

4. **Rework the robe bottom into a true legless WISP.** It currently splits into
   two stubby lobes reading as feet/legs — contradicting the "no feet, floats" pin
   and drifting toward a standing figure. Taper the robe to a single asymmetric
   trailing wisp-curl (one soft S-tip), like Yurei's drift-tail but violet. No
   bilateral leg-lobes.

5. **Fix the eye-sockets — hard square "visor" tiles, not glowing sockets.** On
   the large head they are flat violet squares with a light dot, blown to white at
   the rim. Make them rounded/teardrop sockets with a contained violet inner glow
   and a darker plum socket-rim so bone reads first, glow second. Drop the white
   halo ~30% — it is currently the brightest thing on the FACE and steals from the
   orb.

6. **Guard against the batch-1 Hollow drift.** A faceless-feeling hooded violet
   silhouette with a glowing core is exactly Hollow's territory. The separator is
   the VISIBLE SKULL FACE and BONE CROWN — they must dominate, not the orb/hood.
   Fixes 1-3 and 5 all serve this; verify at 32px that you read "skull mage"
   before "glowing hooded thing." Also keep clear of Pyrecrown — the crown must
   read as bone spikes + bronze, never fire.

7. **Sleeve-cuffs must be visible at 32px.** A pinned tell that currently only
   appears at large size. Make them two chunky bronze-trimmed cuff shapes flanking
   the orb (cradling it) so the "hands holding a heart" gesture reads even small —
   this also makes the orb read as HELD, not free-floating, reinforcing fix 1.

8. **Polish (low priority): crozier finial.** The claw-finial cap is good but the
   two prongs are near-symmetric and slightly stiff; a touch of inward curl + a
   1px sheen on the upper-left prong lifts it to AAA-casual finish. Confirm the
   cap orb matches the now-smaller creature orb's glow falloff so prop and creature
   read as the same magic.

## Accessibility / night-biome check

- Violet robe vs. dark-blue NIGHT sky: deep-plum shade (60,34,92) on night sky is
  low-contrast — robe edges may vanish. Lean on the 1px alpha-grown outline and
  keep the high-value bone skull at the TOP as a bright anchor against dark sky.
  Test the whole silhouette against bright day AND dark night next round.
- Don't let violet be the only carrier: SKULL SHAPE + CROWN SPIKES + WISP TAIL
  must carry the read for colorblind players independent of hue — another reason
  the skull/crown can't evaporate at 32px.

## What I want to see in round 2

A single unified tall figure, skull+spiked-crown dominant, orb shrunk to a chest
accent cradled by visible bronze cuffs, robe tapering to one legless wisp — and a
32px read where I can name all four pinned tells. Palette and pillar are already
there; this round is purely about silhouette unification and scale hierarchy.
